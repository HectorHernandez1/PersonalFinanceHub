from add_transactions import AddTransactions
import pandas as pd
from typing import List, Dict
from ai_helper import AIHelper

class AmexTransactions(AddTransactions):
    """
    Implementation of AddTransactions for Amex Card transactions.
    Handles the specific format and requirements of Amex CSV files.
    """

    def __init__(self, db_config: dict, person: str):
        """
        Initialize the Amex Card transaction processor.
        Args:
            db_config (dict): Database configuration dictionary
            person (str): Name of the person whose transactions are being processed
        """
        super().__init__(db_config, person)
        self.account_type = 'Amex Card'
        self.ai_helper = AIHelper()

    def read_files(self, file_paths: List[str]) -> pd.DataFrame:
        """
        Read Amex Card transaction files and combine them into a single DataFrame.
        Args:
            file_paths (List[str]): List of paths to Amex Card transaction CSV files
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
        Clean and standardize the Amex Card transaction data.
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
            'Card Member,': 'person'
        })


        # Convert date string to datetime
        self.df['transaction_date'] = pd.to_datetime(self.df['transaction_date'])

        # Ensure amount is numeric and handle credits/debits
        self.df['amount'] = pd.to_numeric(self.df['amount'])

        # Add categories using AI helper
        self.df = self.ai_helper.add_category(self.df, self._category_cache)

        # Select and reorder columns
        self.df = self.df[[
            'transaction_date',
            'amount',
            'merchant_name',
            'category'
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
                'transaction_date': row.get('transaction_date'),
                'amount': row.get('amount'),
                'merchant_name': row.get('merchant_name'),
                'category': row.get('category'),
                'person': self.person,
                'account_type': self.account_type
            }
            transactions.append(transaction)
        return transactions
