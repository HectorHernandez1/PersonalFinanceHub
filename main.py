from apple_transactions import AppleTransactions
from chase_transactions import ChaseTransactions
from amex_transactions import AmexTransactions
from citi_transactions import CitiTransactions
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
    processors = [
        {
            "class": AppleTransactions,
            "files_glob": "apple_files/*.csv",
            "name": "Apple Card"
        },
        {
             "class": ChaseTransactions,
             "files_glob": "chase_files/*.pdf",
             "name": "Chase Card"
         },
        {
            "class": AmexTransactions,
            "files_glob": "Amex_files/*.csv",
            "name": "Amex Card"
        },
        {
            "class": CitiTransactions,
            "files_glob": "Citi_files/*.CSV",
            "name": "Citi Card"
        }
    ]

    for processor_info in processors:
        try:
            processor = processor_info["class"](db_config=DB_CONFIG, person="Hector Hernandez")
            files = glob.glob(processor_info["files_glob"])
            
            if files:
                processor.process_transactions(files)
                print(f"Successfully processed {processor_info['name']} transactions")
            else:
                print(f"No {processor_info['name']} transaction files found")
        
        except Exception as e:
            print(f"An error occurred while processing {processor_info['name']} transactions: {str(e)}")

if __name__ == "__main__":
    main()
