from add_transactions import AddTransactions
import pandas as pd
from typing import List, Dict
from ai_helper import AIHelper

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
        self.ai_helper = AIHelper()

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
            'Debit': 'amount'
        })

        #merge credit and debit into amount
        if 'Credit' in self.df.columns:
            self.df['amount'] = self.df['amount'].fillna(0) + self.df['Credit'].fillna(0)
            self.df.drop(columns=['Credit'], inplace=True)


        # Convert date string to datetime
        self.df['transaction_date'] = pd.to_datetime(self.df['transaction_date'], format='%m/%d/%Y')

        # Ensure amount is numeric and handle credits/debits
        self.df['amount'] = pd.to_numeric(self.df['amount'])

        #need to add a category column if it doesn't exist
        if 'category' not in self.df.columns:
            self.df['category'] = 'Other'
        
        #check if mechant_name contains "return" or "refund"
        self.df['category'] = self.df.apply(
            lambda row: "Refunds & Returns" if 'return' in row['merchant_name'].lower() or 'refund' in row['merchant_name'].lower() else row['category'],
            axis=1
        )

        #check merchant_name for payments
        self.df['category'] = self.df.apply(
            lambda row: "Payments" if 'payment' in row['merchant_name'].lower() else row['category'],
            axis=1
        )
        
        # Use AI to categorize transactions with 'Other' category
        other_mask = self.df['category'] == 'Other'
        if other_mask.any():
            other_transactions = self.df[other_mask]
            for idx, row in other_transactions.iterrows():
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
                'transaction_date': row['transaction_date'].strftime('%Y-%m-%d %H:%M:%S'),
                'amount': float(row['amount']),
                'merchant_name': row['merchant_name'],
                'category': row['category'],
                'account_type': self.account_type,
                'person': row['person']
            }
            transactions.append(transaction)

        return transactions 