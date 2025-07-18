#!/usr/bin/env python3
"""
Script to fix transactions with missing category IDs by using AI to categorize them.
This script finds all transactions where category_id is null, uses AI to determine 
the appropriate category, and updates the database.
"""

import psycopg2
import os
from dotenv import load_dotenv
from ai_helper import AIHelper

def get_db_config():
    """Load database configuration from environment variables."""
    load_dotenv()
    return {
        'host': 'localhost',
        'database': 'money_stuff',
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }

def get_categories_from_db(conn):
    """Fetch all available categories from the database."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, category_name FROM budget_app.spending_categories")
    categories = cursor.fetchall()
    category_names = [name for id, name in categories]
    category_map = {name: id for id, name in categories}
    return category_names, category_map

def get_transactions_without_category(conn):
    """Get all transactions that have null category_id."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.merchant_name 
        FROM budget_app.transactions t 
        WHERE t.category_id IS NULL
    """)
    return cursor.fetchall()

def update_transaction_category(conn, transaction_id, category_id):
    """Update a transaction's category_id."""
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE budget_app.transactions 
        SET category_id = %s 
        WHERE id = %s
    """, (category_id, transaction_id))

def main():
    """Main function to fix missing category IDs."""
    print("Starting to fix missing category IDs...")
    
    # Initialize AI helper
    ai_helper = AIHelper()
    if not ai_helper.llm:
        print("Error: AI helper not available. Check OPENAI_API_KEY environment variable.")
        return
    
    # Connect to database
    db_config = get_db_config()
    try:
        conn = psycopg2.connect(**db_config)
        print("Connected to database successfully.")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return
    
    try:
        # Get available categories
        category_names, category_map = get_categories_from_db(conn)
        print(f"Found {len(category_names)} categories: {', '.join(category_names)}")
        
        # Get transactions without category
        transactions = get_transactions_without_category(conn)
        print(f"Found {len(transactions)} transactions without category IDs")
        
        if not transactions:
            print("No transactions need category updates.")
            return
        
        # Process each transaction
        updated_count = 0
        for transaction_id, merchant_name in transactions:
            print(f"Processing transaction {transaction_id}: {merchant_name}")
            
            # Use AI to guess category
            ai_category = ai_helper.guess_category_openai(merchant_name, category_names)
            
            # Get category ID
            if ai_category in category_map:
                category_id = category_map[ai_category]
                
                # Update the transaction
                update_transaction_category(conn, transaction_id, category_id)
                updated_count += 1
                print(f"  -> Updated to category: {ai_category} (ID: {category_id})")
            else:
                print(f"  -> Warning: AI returned unknown category '{ai_category}', skipping")
        
        # Commit all changes
        conn.commit()
        print(f"\nSuccessfully updated {updated_count} transactions with category IDs")
        
    except Exception as e:
        conn.rollback()
        print(f"Error occurred: {e}")
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()