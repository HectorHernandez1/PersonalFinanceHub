from add_transactions import AddTransactions
import pandas as pd
from typing import List, Dict

class CitiTransactions(AddTransactions):
    def __init__(self, db_config: dict, person: str):
        """
        Initialize CitiTransactions processor
        
        Args:
            db_config (dict): Database configuration parameters
            person (str): Name of the person whose transactions are being processed
        """
        super().__init__(db_config, person)
        self.account_type = 'Citi Card'

    def read_files(self, file_paths: List[str]) -> pd.DataFrame:
        """
        Read Citi Card transaction files and combine them into a single DataFrame.
        
        Args:
            file_paths (List[str]): List of paths to Citi Card transaction CSV files
            
        Returns:
            pd.DataFrame: Combined DataFrame of all transactions
        """
        dataframes = []
        for file_path in file_paths:
            try:
                df = pd.read_csv(file_path)
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
        Clean and standardize the Citi Card transaction data.
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
            'Date': 'transaction_date',
            'Description': 'merchant_name',
            'Amount': 'amount',
            'Category': 'category'
        })

        # Convert date string to datetime
        self.df['transaction_date'] = pd.to_datetime(self.df['transaction_date'], format='%m/%d/%Y')

        # Ensure amount is numeric and handle credits/debits
        self.df['amount'] = self.df['amount'].astype(str).str.replace(' , '').str.replace(',', '')
        self.df['amount'] = pd.to_numeric(self.df['amount'])
        # Assuming Citi also exports credits as positive, negate amounts
        self.df['amount'] = -1 * self.df['amount']

        # Add person column
        self.df['person'] = self.person

        # Handle missing categories
        if 'category' not in self.df.columns:
            self.df['category'] = 'Uncategorized'
        else:
            self.df['category'] = self.df['category'].fillna('Uncategorized')

        # Select and reorder columns
        self.df = self.df[[
            'transaction_date',
            'amount',
            'merchant_name',
            'category',
            'person'
        ]]

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
                'transaction_date': row['transaction_date'].strftime('%Y-%m-%d %H:%M:%S'),
                'amount': float(row['amount']),
                'merchant_name': row['merchant_name'],
                'category': row['category'],
                'account_type': self.account_type,
                'person': row['person']
            }
            transactions.append(transaction)

        return transactions 