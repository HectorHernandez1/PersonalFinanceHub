#!/usr/bin/env python3
"""
Script to fix transactions with future dates by converting year from 2025 to 2024.
This handles cases where date parsing incorrectly assigned future years to transactions.
"""

import psycopg2
import pandas as pd
from datetime import date
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "money_stuff"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "options": "-c search_path=budget_app"
}

def get_future_transactions():
    """
    Query the database for transactions with dates greater than today.
    
    Returns:
        pd.DataFrame: DataFrame containing future transactions
    """
    conn = psycopg2.connect(**DB_CONFIG)
    
    try:
        query = """
        SELECT id, transaction_date, merchant_name, amount, person_id, category_id, account_type_id
        FROM transactions 
        WHERE transaction_date > CURRENT_DATE
        ORDER BY transaction_date DESC
        """
        
        df = pd.read_sql(query, conn)
        return df
    
    finally:
        conn.close()

def fix_transaction_dates(transactions_df):
    """
    Convert transaction years from 2025 to 2024.
    
    Args:
        transactions_df (pd.DataFrame): DataFrame with future transactions
        
    Returns:
        pd.DataFrame: DataFrame with corrected dates
    """
    corrected_transactions = transactions_df.copy()
    
    # Convert transaction_date to datetime if it's not already
    corrected_transactions['transaction_date'] = pd.to_datetime(corrected_transactions['transaction_date'])
    
    # Filter for 2025 transactions and convert to 2024
    mask_2025 = corrected_transactions['transaction_date'].dt.year == 2025
    
    if mask_2025.any():
        print(f"Found {mask_2025.sum()} transactions with year 2025 to correct")
        
        # Create new dates with year 2024
        corrected_transactions.loc[mask_2025, 'transaction_date'] = (
            corrected_transactions.loc[mask_2025, 'transaction_date'].apply(
                lambda x: x.replace(year=2024)
            )
        )
        
        # Show what we're about to change
        print("\nTransactions to be corrected:")
        print(corrected_transactions[mask_2025][['id', 'transaction_date', 'merchant_name', 'amount']])
        
    else:
        print("No transactions with year 2025 found")
    
    return corrected_transactions[mask_2025]  # Return only the corrected ones

def update_transactions_in_db(corrected_transactions):
    """
    Update the corrected transactions back to the database.
    
    Args:
        corrected_transactions (pd.DataFrame): DataFrame with corrected transaction dates
    """
    if corrected_transactions.empty:
        print("No transactions to update")
        return
    
    conn = psycopg2.connect(**DB_CONFIG)
    
    try:
        cursor = conn.cursor()
        
        update_query = """
        UPDATE transactions 
        SET transaction_date = %s 
        WHERE id = %s
        """
        
        # Prepare update data
        update_data = [
            (row['transaction_date'].strftime('%Y-%m-%d %H:%M:%S'), row['id'])
            for _, row in corrected_transactions.iterrows()
        ]
        
        # Execute batch update
        cursor.executemany(update_query, update_data)
        
        print(f"\nUpdated {cursor.rowcount} transactions in the database")
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        print(f"Error updating transactions: {e}")
        raise
    
    finally:
        conn.close()

def main():
    """
    Main function to orchestrate the date correction process.
    """
    print("=== Future Date Transaction Fixer ===")
    print(f"Today's date: {date.today()}")
    print()
    
    # Step 1: Get transactions with future dates
    print("1. Searching for transactions with future dates...")
    future_transactions = get_future_transactions()
    
    if future_transactions.empty:
        print("No transactions with future dates found!")
        return
    
    print(f"Found {len(future_transactions)} transactions with future dates")
    print("\nFuture transactions found:")
    print(future_transactions[['id', 'transaction_date', 'merchant_name', 'amount']])
    print()
    
    # Step 2: Fix the dates (convert 2025 to 2024)
    print("2. Converting years from 2025 to 2024...")
    corrected_transactions = fix_transaction_dates(future_transactions)
    
    if corrected_transactions.empty:
        print("No transactions needed correction")
        return
    
    # Step 3: Confirm before updating
    response = input(f"\nDo you want to update {len(corrected_transactions)} transactions? (y/n): ")
    
    if response.lower() in ['y', 'yes']:
        print("3. Updating transactions in database...")
        update_transactions_in_db(corrected_transactions)
        print("✅ Date correction completed successfully!")
    else:
        print("❌ Update cancelled by user")

if __name__ == "__main__":
    main()