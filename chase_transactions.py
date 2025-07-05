from add_transactions import AddTransactions
import pandas as pd
from typing import List, Dict
import os
from datetime import datetime
from test_code.pdf_statement_reader import ChaseStatementReader

class ChaseTransactions(AddTransactions):
    """
    Implementation of AddTransactions for Chase Card transactions.
    Handles the specific format and requirements of Chase CSV files.
    """

    def __init__(self, db_config: dict, person: str):
        """
        Initialize the Chase Card transaction processor.
        Args:
            db_config (dict): Database configuration dictionary
            person (str): Name of the person whose transactions are being processed
        """
        super().__init__(db_config, person)
        self.account_type = 'Chase Card'

    def read_files(self, file_paths: List[str]) -> pd.DataFrame:
        """
        Read Chase Card transaction files and combine them into a single DataFrame.
        Args:
            file_paths (List[str]): List of paths to Chase Card transaction CSV files
        Returns:
            pd.DataFrame: Combined DataFrame of all transactions
        """
        dataframes = []
        for file_path in file_paths:
            try:
                df = pd.read_csv(file_path)
                df["person"] = self.person
                dataframes.append(df)
            except Exception as e:
                print(f"Error reading file {file_path}: {str(e)}")
                if file_path in self.processed_files:
                    self.processed_files.remove(file_path)
        if not dataframes:
            raise ValueError("No valid files were read")
        self.df = pd.concat(dataframes, ignore_index=True)
        return self.df

    def clean_data(self) -> pd.DataFrame:
        """
        Clean and standardize the Chase Card transaction data.
        - Renames columns to standard format
        - Handles date formatting
        - Standardizes amount values
        - Maps categories to standard categories
        Returns:
            pd.DataFrame: Cleaned and standardized DataFrame
        """
        if self.df is None:
            raise ValueError("No data to clean. Call read_files first.")
        # Rename columns to standard format
        self.df = self.df.rename(columns={
            'Transaction Date': 'transaction_date',
            'Description': 'merchant_name',
            'Amount': 'amount',
            'Category': 'category',
        })
        # Select and reorder columns
        self.df = self.df[[
            'transaction_date',
            'amount',
            'merchant_name',
            'category',
            'person'
        ]]
        # Convert date string to datetime
        self.df['transaction_date'] = pd.to_datetime(self.df['transaction_date'])
        # Make all amounts negative (Chase exports credits as positive)
        self.df['amount'] = -1 * pd.to_numeric(self.df['amount'])
        # Replace category values as needed
        self.df['category'] = self.df['category'].replace({"Food & Drink": "Restaurants", "": "Payment"})
        return self.df

    def prepare_data_for_db(self) -> List[Dict]:
        """
        Convert the cleaned DataFrame into a format suitable for database insertion.
        Returns:
            List[Dict]: List of dictionaries containing formatted transaction data
        """
        if self.df is None:
            raise ValueError("No data to prepare. Call clean_data first.")
        transactions = []
        for _, row in self.df.iterrows():
            transaction = {
                'transaction_date': row['transaction_date'],
                'amount': row['amount'],
                'merchant_name': row['merchant_name'],
                'category': row['category'],
                'person': row['person'],
                'account_type': self.account_type
            }
            transactions.append(transaction)
        return transactions

def load_chase_transactions(pdf_directory: str = "chase_files") -> pd.DataFrame:
    """
    Load Chase transactions from PDF statements
    
    Args:
        pdf_directory: Directory containing Chase PDF statements
        
    Returns:
        DataFrame with standardized transaction data
    """
    all_transactions = []
    
    # Create PDF reader
    for filename in os.listdir(pdf_directory):
        if filename.lower().endswith('.pdf'):
            try:
                pdf_path = os.path.join(pdf_directory, filename)
                print(f"Processing {filename}...")
                
                # Use our Chase PDF reader
                reader = ChaseStatementReader(pdf_path)
                df = reader.extract_transactions()
                
                if not df.empty:
                    all_transactions.append(df)
                    print(f"Successfully extracted {len(df)} transactions from {filename}")
                else:
                    print(f"No transactions found in {filename}")
                    
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue
    
    if not all_transactions:
        print("No transactions found in any PDF files")
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
        df = load_chase_transactions()
        print("\nFirst few transactions:")
        print(df.head())
        
    except Exception as e:
        print(f"Error: {e}")
