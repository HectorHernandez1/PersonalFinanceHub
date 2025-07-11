# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal finance transaction processing system that reads, cleans, and loads credit card transactions from multiple sources (Apple Card, Chase, Amex, Citi) into a PostgreSQL database. The system uses OpenAI's GPT API to categorize transactions and provides a normalized database schema for financial analysis.

## Key Commands

### Running the Application
```bash
python main.py
```
This processes all transaction files from the various card providers and loads them into the database.

### Database Setup
Execute the database schema and initial data:
```bash
psql -d money_stuff -f data_base_code/database.sql
```

### Environment Setup
Create a `.env` file with:
```
DB_USER=your_db_user
DB_PASSWORD=your_db_password
OPENAI_API_KEY=your_openai_api_key
```

## Architecture

### Core Components

1. **AddTransactions (add_transactions.py)**: Abstract base class defining the transaction processing interface. All card-specific processors inherit from this class.

2. **Card-Specific Processors**:
   - `AppleTransactions`: Processes Apple Card CSV files
   - `ChaseTransactions`: Processes Chase PDF statements (not CSV)
   - `AmexTransactions`: Processes Amex CSV files with AI category guessing
   - `CitiTransactions`: Processes Citi CSV files

3. **AIHelper (ai_helper.py)**: Uses OpenAI's GPT-4.1-nano model with langchain_openai to categorize transactions based on merchant names.

4. **PDF Processing**: Chase transactions are processed from PDF files using `pdf_statement_reader.py` and `chase_statement_reader.py`.

### Database Schema

The PostgreSQL database (`money_stuff`) uses the `budget_app` schema with these key tables:
- `persons`: User identities
- `spending_categories`: Transaction categories
- `account_type`: Card types
- `transactions`: Main transaction table with foreign key relationships
- `transactions_view`: Denormalized view for reporting

### File Structure

- Transaction files are organized in folders: `apple_files/`, `chase_files/`, `Amex_files/`, `Citi_files/`
- Chase processes PDF files, all others process CSV files
- Files are automatically deleted after successful processing

### Processing Flow

1. Each processor reads files from its designated folder
2. Data is cleaned and standardized using card-specific logic
3. For Amex transactions, AI categorization is applied to unknown merchants
4. Transactions are inserted into the database with duplicate prevention
5. Successfully processed files are deleted

## Important Notes

- The system uses duplicate prevention via the `unique_transaction` constraint
- OpenAI API is only used for Amex transaction categorization
- Chase transactions require PDF processing, not CSV
- All processors use the same database connection pattern with caching for reference data
- The system handles missing categories, persons, and account types by auto-creating them

## Security Considerations

- Never commit the `.env` file containing API keys and database credentials
- The codebase contains an exposed OpenAI API key in `next_steps_notes.txt` that should be secured
- Database connections use environment variables for credentials