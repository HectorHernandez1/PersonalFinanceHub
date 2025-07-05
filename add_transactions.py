from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Dict
import psycopg2
import os
from chase_transactions import load_chase_transactions
from amex_transactions import AmexTransactions
from apple_transactions import AppleTransactions

class AddTransactions(ABC):
    """
    Abstract base class for processing and adding transactions to the database.
    This class defines the interface that all specific transaction processors
    (Apple, Chase, Amex, Citi) must implement.
    """

    def __init__(self, db_config: dict, person: str):
        """
        Initialize the transaction processor.
        
        Args:
            db_config (dict): Database configuration dictionary
            person (str): Name of the person whose transactions are being processed
        """
        self.db_config = db_config
        self.person = person
        self.df = None
        self.processed_files = []
        self._category_cache = {}
        self._person_cache = {}
        self._account_type_cache = {}

    def _load_reference_data(self, conn: psycopg2.extensions.connection) -> None:
        """
        Load reference data from the database into cache.
        """
        cursor = conn.cursor()
        
        # Load categories
        cursor.execute("SELECT id, category_name FROM budget_app.spending_categories")
        self._category_cache = {name.lower(): id for id, name in cursor.fetchall()}
        
        # Load persons
        cursor.execute("SELECT id, name FROM budget_app.persons")
        self._person_cache = {name.lower(): id for id, name in cursor.fetchall()}
        
        # Load account types
        cursor.execute("SELECT id, card_type FROM budget_app.account_type")
        self._account_type_cache = {name.lower(): id for id, name in cursor.fetchall()}

    def _get_or_create_category(self, conn: psycopg2.extensions.connection, category: str) -> int:
        """Get category ID, create if not exists."""
        category_lower = category.lower()
        if category_lower not in self._category_cache:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO budget_app.spending_categories (category_name) VALUES (%s) RETURNING id",
                (category,)
            )
            self._category_cache[category_lower] = cursor.fetchone()[0]
        return self._category_cache[category_lower]

    def _get_or_create_person(self, conn: psycopg2.extensions.connection, person: str) -> int:
        """Get person ID, create if not exists."""
        person_lower = person.lower()
        if person_lower not in self._person_cache:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO budget_app.persons (name) VALUES (%s) RETURNING id",
                (person,)
            )
            self._person_cache[person_lower] = cursor.fetchone()[0]
        return self._person_cache[person_lower]

    def _get_or_create_account_type(self, conn: psycopg2.extensions.connection, account_type: str) -> int:
        """Get account type ID, create if not exists."""
        account_type_lower = account_type.lower()
        if account_type_lower not in self._account_type_cache:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO budget_app.account_type (card_type) VALUES (%s) RETURNING id",
                (account_type,)
            )
            self._account_type_cache[account_type_lower] = cursor.fetchone()[0]
        return self._account_type_cache[account_type_lower]

    @abstractmethod
    def read_files(self, file_paths: List[str]) -> pd.DataFrame:
        """Read transaction files and convert them to a pandas DataFrame."""
        pass

    @abstractmethod
    def clean_data(self) -> pd.DataFrame:
        """Clean and standardize the transaction data."""
        pass

    def create_connection(self) -> psycopg2.extensions.connection:
        """Create a connection to the PostgreSQL database."""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except psycopg2.Error as e:
            raise Exception(f"Database connection error: {str(e)}")

    @abstractmethod
    def prepare_data_for_db(self) -> List[Dict]:
        """Convert the cleaned DataFrame into a format suitable for database insertion."""
        pass

    def add_to_database(self, transactions: List[Dict]) -> bool:
        """
        Add processed transactions to the database.
        
        Args:
            transactions (List[Dict]): List of formatted transaction dictionaries
            
        Returns:
            bool: True if transactions were successfully added, False otherwise
        """
        conn = self.create_connection()
        try:
            # Load reference data
            self._load_reference_data(conn)
            
            cursor = conn.cursor()
            
            # Process each transaction
            for transaction in transactions:
                # Get or create reference IDs
                category_id = self._get_or_create_category(conn, transaction['category'])
                person_id = self._get_or_create_person(conn, transaction['person'])
                account_type_id = self._get_or_create_account_type(conn, transaction['account_type'])
                
                # Insert the transaction
                cursor.execute("""
                    INSERT INTO budget_app.transactions (
                        amount,
                        merchant_name,
                        category_id,
                        person_id,
                        transaction_date,
                        account_type_id
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT ON CONSTRAINT unique_transaction DO NOTHING
                """, (
                    transaction['amount'],
                    transaction['merchant_name'],
                    category_id,
                    person_id,
                    transaction['transaction_date'],
                    account_type_id
                ))
            
            conn.commit()
            return True
        except psycopg2.Error as e:
            conn.rollback()
            raise Exception(f"Database insertion error: {str(e)}")
        finally:
            conn.close()

    def delete_processed_files(self) -> None:
        """Delete the successfully processed files."""
        for file_path in self.processed_files:
            try:
                os.remove(file_path)
                print(f"Deleted processed file: {file_path}")
            except OSError as e:
                print(f"Error deleting file {file_path}: {str(e)}")

    def process_transactions(self, file_paths: List[str]) -> None:
        """Main method to orchestrate the entire process."""
        try:
            self.processed_files = file_paths
            self.df = self.read_files(file_paths)
            self.df = self.clean_data()
            transactions = self.prepare_data_for_db()
            
            if self.add_to_database(transactions):
                self.delete_processed_files()
                print(f"Successfully processed {len(transactions)} transactions and deleted source files")
        except Exception as e:
            raise Exception(f"Transaction processing failed: {str(e)}")

    def get_categories_from_db(self) -> List[str]:
        """
        Fetch spending categories from the database.
        Returns:
            List[str]: List of category names
        """
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT category_name FROM budget_app.spending_categories")
            categories = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return categories
        except Exception as e:
            print(f"Failed to fetch categories from DB: {e}")
            return []

def load_all_transactions() -> pd.DataFrame:
    """
    Load transactions from all sources and combine them into a single DataFrame
    
    Returns:
        DataFrame with all transactions
    """
    all_transactions = []
    
    # Load Chase transactions from PDFs
    try:
        chase_df = load_chase_transactions()
        if not chase_df.empty:
            all_transactions.append(chase_df)
            print("\nChase transactions loaded successfully")
    except Exception as e:
        print(f"Error loading Chase transactions: {e}")
    
    # Load Amex transactions (assuming CSV for now)
    try:
        amex = AmexTransactions()
        amex_transactions = amex.get_transactions()
        if amex_transactions:
            amex_df = pd.DataFrame(amex_transactions)
            all_transactions.append(amex_df)
            print("Amex transactions loaded successfully")
    except Exception as e:
        print(f"Error loading Amex transactions: {e}")
    
    # Load Apple transactions (assuming CSV for now)
    try:
        apple = AppleTransactions()
        apple_transactions = apple.get_transactions()
        if apple_transactions:
            apple_df = pd.DataFrame(apple_transactions)
            all_transactions.append(apple_df)
            print("Apple transactions loaded successfully")
    except Exception as e:
        print(f"Error loading Apple transactions: {e}")
    
    if not all_transactions:
        print("No transactions found from any source")
        return pd.DataFrame()
    
    # Combine all transactions
    combined_df = pd.concat(all_transactions, ignore_index=True)
    
    # Remove any duplicates based on date, description, and amount
    combined_df = combined_df.drop_duplicates(subset=['date', 'description', 'amount'])
    
    # Sort by date
    combined_df['date'] = pd.to_datetime(combined_df['date'])
    combined_df = combined_df.sort_values('date')
    combined_df['date'] = combined_df['date'].dt.strftime('%Y-%m-%d')
    
    print(f"\nTotal transactions loaded: {len(combined_df)}")
    print(f"Date range: {combined_df['date'].min()} to {combined_df['date'].max()}")
    print(f"Total amount: ${combined_df['amount'].sum():,.2f}")
    
    return combined_df

if __name__ == "__main__":
    # Example usage
    try:
        df = load_all_transactions()
        print("\nFirst few transactions:")
        print(df.head())
        
    except Exception as e:
        print(f"Error: {e}")
