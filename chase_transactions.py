from add_transactions import AddTransactions
import pandas as pd
from typing import List, Dict
from chase_statement_reader import ChaseStatementReader
from pdf_statement_reader import read_statement
from ai_helper import AIHelper
import os

class ChaseTransactions(AddTransactions):
    """
    Implementation of AddTransactions for Chase Card transactions.
    Handles the specific format and requirements of Chase PDF files.
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
        self.ai_helper = AIHelper()

    def read_files(self, file_paths: List[str]) -> pd.DataFrame:
        """
        Read Chase Card transaction PDF files and combine them into a single DataFrame.
        Args:
            file_paths (List[str]): List of paths to Chase Card transaction PDF files
        Returns:
            pd.DataFrame: Combined DataFrame of all transactions
        """
        all_transactions = []
        for file_path in file_paths:
            try:
                print(f"Processing {os.path.basename(file_path)}...")
                df = read_statement(file_path, ChaseStatementReader)
                if not df.empty:
                    all_transactions.append(df)
                    print(f"Successfully extracted {len(df)} transactions from {os.path.basename(file_path)}")
                else:
                    print(f"No transactions found in {os.path.basename(file_path)}")
            except Exception as e:
                print(f"Error processing {os.path.basename(file_path)}: {e}")
                if file_path in self.processed_files:
                    self.processed_files.remove(file_path)
        
        if not all_transactions:
            raise ValueError("No valid files were read")
        
        combined_df = pd.concat(all_transactions, ignore_index=True)
        
        # Standardize column names to match the expected format for clean_data
        combined_df = combined_df.rename(columns={
            'date': 'transaction_date',
            'description': 'merchant_name',
            'amount': 'amount'
        })
        
        
        # Remove any duplicates based on date, description, and amount
        combined_df = combined_df.drop_duplicates(subset=['transaction_date', 'merchant_name', 'amount'])
        
        # Reset index after concatenation and deduplication
        combined_df.reset_index(drop=True, inplace=True)
        
        self.df = combined_df
        return self.df

    def clean_data(self) -> pd.DataFrame:
        """
        Clean and standardize the Chase Card transaction data.
        - Handles date formatting
        - Standardizes amount values
        - Maps categories to standard categories
        Returns:
            pd.DataFrame: Cleaned and standardized DataFrame
        """
        if self.df is None:
            raise ValueError("No data to clean. Call read_files first.")
        
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
                'transaction_date': row['transaction_date'],
                'amount': row['amount'],
                'merchant_name': row['merchant_name'],
                'category': row['category'],
                'person': row['person'],
                'account_type': self.account_type
            }
            transactions.append(transaction)
        return transactions
