Money Review - Personal Finance Transaction Processor
====================================================

This project is a personal finance tool for reviewing, cleaning, and loading credit card transactions from multiple sources (Apple Card, Chase, Amex, Citi) into a PostgreSQL database. It is designed to help you organize, categorize, and analyze your spending data.

Features:
---------
- Reads transaction files from Apple Card (CSV), Chase (PDF), Amex (CSV), and Citi (CSV).
- Cleans and standardizes transaction data for each card type.
- Uses AI (OpenAI GPT-4.1-nano) to guess missing spending categories for Amex transactions based on merchant name.
- Loads transactions into a PostgreSQL database with a normalized schema.
- Prevents duplicate transactions and supports custom category mapping.
- Credentials and API keys are managed securely via a `.env` file (never committed to git).
- Automatically deletes processed files after successful database insertion.

How it works:
-------------
1. Place your files in the appropriate folders: `apple_files/` (CSV), `chase_files/` (PDF), `Amex_files/` (CSV), `Citi_files/` (CSV).
2. Configure your database and OpenAI credentials in the `.env` file.
3. Run `python main.py` to process and load all transactions.
4. The program will print a summary of what was processed and loaded.

Requirements:
-------------
- Python 3.11+
- PostgreSQL database
- OpenAI API key (for AI category guessing)
- See `requirements.txt` for Python dependencies

Security:
---------
- Never commit your `.env` file or credentials to git.
- If you ever committed secrets, follow the instructions to clean your git history.

Customization:
--------------
- You can add new card types by creating new transaction classes.
- The AI helper is modular and can be extended to use other AI models.

For more details, see the code comments and docstrings in each file.
