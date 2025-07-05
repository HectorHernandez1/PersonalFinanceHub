from apple_transactions import AppleTransactions
from chase_transactions import ChaseTransactions
from amex_transactions import AmexTransactions
import glob
import os

# Database configuration
DB_CONFIG = {
    "dbname": "money_stuff",
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
    "host": "localhost",
    "port": "5432",
    "options": "-c search_path=budget_app"  
}

def main():
    """
    Main entry point for the Money Review application.
    This function handles the orchestration of loading, processing,
    and reviewing financial transactions from different sources.
    """
    try:
        # Initialize the Apple Card transaction processor
        apple_processor = AppleTransactions(db_config=DB_CONFIG, person="Hector Hernandez")
        # Initialize the Chase Card transaction processor
        chase_processor = ChaseTransactions(db_config=DB_CONFIG, person="Hector Hernandez")
        # Initialize the Amex Card transaction processor
        amex_processor = AmexTransactions(db_config=DB_CONFIG, person="Hector Hernandez")

        # Get all Apple Card transaction files
        apple_files = glob.glob('apple_files/*.csv')
        # Get all Chase Card transaction files
        chase_files = glob.glob('chase_files/*.csv')
        # Get all Amex Card transaction files
        amex_files = glob.glob('Amex_files/*.csv')
        
        if apple_files:
            # Process all Apple Card transactions
            apple_processor.process_transactions(apple_files)
            print("Successfully processed Apple Card transactions")
        else:
            print("No Apple Card transaction files found")

        if chase_files:
            # Process all Chase Card transactions
            chase_processor.process_transactions(chase_files)
            print("Successfully processed Chase Card transactions")
        else:
            print("No Chase Card transaction files found")

        if amex_files:
            # Process all Amex Card transactions
            amex_processor.process_transactions(amex_files)
            print("Successfully processed Amex Card transactions")
        else:
            print("No Amex Card transaction files found")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
