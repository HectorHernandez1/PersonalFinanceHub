import pandas as pd
import psycopg2
from datetime import datetime

class CitiTransactions:
    def __init__(self, db_config, person):
        """
        Initialize CitiTransactions processor
        
        Args:
            db_config (dict): Database configuration parameters
            person (str): Name of the person whose transactions are being processed
        """
        self.db_config = db_config
        self.person = person

    def process_transactions(self, file_paths):
        """
        Process Citi card transaction files and store them in the database
        
        Args:
            file_paths (list): List of paths to Citi transaction CSV files
        """
        for file_path in file_paths:
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Connect to the database
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            try:
                # Process each transaction
                for _, row in df.iterrows():
                    # Format the date (assuming Citi's date format)
                    transaction_date = datetime.strptime(row['Date'], '%m/%d/%Y').strftime('%Y-%m-%d')
                    
                    # Insert transaction into database
                    cursor.execute("""
                        INSERT INTO transactions 
                        (date, description, amount, category, account_type, person)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (date, description, amount, person) DO NOTHING
                    """, (
                        transaction_date,
                        row['Description'],
                        float(row['Amount'].replace('$', '').replace(',', '')),
                        row.get('Category', 'Uncategorized'),  # Use 'Uncategorized' if category not present
                        'Citi',
                        self.person
                    ))
                
                # Commit the transactions
                conn.commit()
                
            except Exception as e:
                print(f"Error processing file {file_path}: {str(e)}")
                conn.rollback()
                raise
            
            finally:
                cursor.close()
                conn.close() 