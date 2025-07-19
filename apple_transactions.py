from add_transactions import AddTransactions
import pandas as pd
from typing import List, Dict
from ai_helper import AIHelper

class AppleTransactions(AddTransactions):
    """
    Implementation of AddTransactions for Apple Card transactions.
    Handles the specific format and requirements of Apple Card CSV files.
    """

    def __init__(self, db_config: dict, person: str):
        """
        Initialize the Apple Card transaction processor.
        
        Args:
            db_config (dict): Database configuration dictionary
            person (str): Name of the person whose transactions are being processed
        """
        super().__init__(db_config, person)
        self.account_type = 'Apple Card'
        self.ai_helper = AIHelper()

    def read_files(self, file_paths: List[str]) -> pd.DataFrame:
        """
        Read Apple Card transaction files and combine them into a single DataFrame.
        
        Args:
            file_paths (List[str]): List of paths to Apple Card transaction CSV files
            
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
                # Remove failed file from processed_files list
                self.processed_files.remove(file_path)
        
        if not dataframes:
            raise ValueError("No valid files were read")
        
        self.df = pd.concat(dataframes, ignore_index=True)
        return self.df

    def clean_data(self) -> pd.DataFrame:
        """
        Clean and standardize the Apple Card transaction data.
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
            'Merchant': 'merchant_name',
            'Amount (USD)': 'amount',
            'Purchased By': 'person',
            'Category': 'category'
        })

        # Convert date string to datetime
        self.df['transaction_date'] = pd.to_datetime(self.df['transaction_date'])

        # Ensure amount is numeric and handle credits/debits
        # First check if amount is already numeric
        if not pd.api.types.is_numeric_dtype(self.df['amount']):
            # Remove $ and , only if amount is string type
            if pd.api.types.is_string_dtype(self.df['amount']):
                self.df['amount'] = self.df['amount'].str.replace('$', '').str.replace(',', '')
            self.df['amount'] = pd.to_numeric(self.df['amount'])
        
        # Add categories using AI helper
        self.df = self.ai_helper.add_category(self.df, self._category_cache)

        # Use AI to categorize transactions with categories not in database
        invalid_category_mask = ~self.df['category'].isin(self._category_cache.keys())
        if invalid_category_mask.any():
            invalid_transactions = self.df[invalid_category_mask]
            for idx, row in invalid_transactions.iterrows():
                ai_category = self.ai_helper.guess_category_openai(
                    row['merchant_name'], 
                    list(self._category_cache.keys())
                )
                if ai_category != 'Other':
                    self.df.loc[idx, 'category'] = ai_category

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
                'person': self.person
            }
            transactions.append(transaction)

        return transactions
