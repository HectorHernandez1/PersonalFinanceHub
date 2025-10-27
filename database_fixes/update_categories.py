#!/usr/bin/env python3
"""
Script to fix transactions with missing category IDs by using AI to categorize them.
This script finds all transactions where category_id is null, uses AI to determine
the appropriate category, and updates the database.
"""

import psycopg2
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_helper import AIHelper
from vendor_mapping import get_category_from_vendor

def get_db_config():
    """Load database configuration from environment variables."""
    # Load .env from parent directory
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(parent_dir, '.env')
    load_dotenv(env_path)
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'money_stuff'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'port': os.getenv('DB_PORT', '5432')
    }

def get_categories_from_db(conn):
    """Fetch all available categories from the database."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, category_name FROM budget_app.spending_categories")
    categories = cursor.fetchall()
    category_names = [name for id, name in categories]
    category_map = {name: id for id, name in categories}
    return category_names, category_map

def get_transactions_to_update(conn, target_category=None):
    """
    Get transactions that need category updates.
    
    Args:
        target_category (str, optional): Specific category name to target for updates.
                                       If None, targets transactions with null category_id.
    """
    cursor = conn.cursor()
    
    if target_category:
        # Get category ID for the target category
        cursor.execute("SELECT id FROM budget_app.spending_categories WHERE category_name = %s", (target_category,))
        result = cursor.fetchone()
        if not result:
            print(f"Error: Category '{target_category}' not found in database.")
            return []
        
        target_category_id = result[0]
        cursor.execute("""
            SELECT t.id, t.merchant_name 
            FROM budget_app.transactions t 
            WHERE t.category_id = %s
        """, (target_category_id,))
        print(f"Finding transactions with category '{target_category}'...")
    else:
        cursor.execute("""
            SELECT t.id, t.merchant_name 
            FROM budget_app.transactions t 
            WHERE t.category_id IS NULL
        """)
        print("Finding transactions with null category_id...")
    
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
    import sys
    
    # Check for command line argument
    target_category = None
    if len(sys.argv) > 1:
        target_category = sys.argv[1]
        print(f"Starting to update transactions with category '{target_category}'...")
    else:
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
        
        # Get transactions to update
        transactions = get_transactions_to_update(conn, target_category)
        print(f"Found {len(transactions)} transactions to update")
        
        if not transactions:
            print("No transactions need category updates.")
            return
        
        # Ask for confirmation if updating a specific category
        if target_category:
            response = input(f"Are you sure you want to update all {len(transactions)} transactions currently categorized as '{target_category}'? (y/N): ")
            if response.lower() != 'y':
                print("Operation cancelled.")
                return
        
        # Process each transaction
        updated_count = 0
        vendor_map_count = 0
        ai_count = 0
        for transaction_id, merchant_name in transactions:
            print(f"Processing transaction {transaction_id}: {merchant_name}")

            # First, try vendor mapping for known vendors
            vendor_category = get_category_from_vendor(merchant_name)

            if vendor_category:
                category_name = vendor_category
                source = "vendor mapping"
                vendor_map_count += 1
            else:
                # Fall back to AI for unknown merchants
                category_name = ai_helper.guess_category_openai(merchant_name, category_names)
                source = "OpenAI"
                if category_name != "Other":
                    ai_count += 1

            # Get category ID
            if category_name in category_map:
                category_id = category_map[category_name]

                # Update the transaction
                update_transaction_category(conn, transaction_id, category_id)
                updated_count += 1
                print(f"  -> Updated to category: {category_name} (ID: {category_id}) [{source}]")
            else:
                print(f"  -> Warning: Category '{category_name}' not found in database, skipping")
        
        # Commit all changes
        conn.commit()
        print(f"\nSuccessfully updated {updated_count} transactions with category IDs")
        print(f"  - From vendor mapping: {vendor_map_count}")
        print(f"  - From OpenAI: {ai_count}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error occurred: {e}")
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()