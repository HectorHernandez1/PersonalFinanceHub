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

### Maintenance Scripts (`database_fixes/`)
Utility scripts for data integrity, run from inside `database_fixes/`:
```bash
# Re-categorize transactions with null category_id (vendor mapping → OpenAI fallback)
python update_categories.py

# Re-categorize all transactions currently in a given category
python update_categories.py "Other"

# Fix transactions whose dates were parsed into the wrong year
python fix_future_dates.py
```
Both scripts preview changes and require confirmation before writing.

### Requirements
- Python 3.11+
- PostgreSQL
- OpenAI API key

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

3. **AIHelper (ai_helper.py)**: Categorizes transactions using a two-step approach:
   - First checks vendor mapping for known merchants (no API calls)
   - Falls back to OpenAI's GPT-5-nano model via langchain_openai for unknown merchants

4. **Vendor Mapping (vendor_mapping.py)**: Maps known vendor names to spending categories without requiring API calls. Contains patterns for common merchants (Amazon, Netflix, Uber, etc.) that map to database categories.

5. **PDF Processing**: Chase transactions are processed from PDF files using `pdf_statement_reader.py` and `chase_statement_reader.py`.

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
3. For all transactions, AI categorization is applied:
   - First, checks vendor mapping for known merchants (instant, no API cost)
   - Then, uses OpenAI for unknown merchants that don't match any vendor pattern
4. Transactions are inserted into the database with duplicate prevention
5. Successfully processed files are deleted

## Important Notes

- The system uses duplicate prevention via the `unique_transaction` constraint
- **Vendor Mapping**: Known merchants are categorized instantly from `vendor_mapping.py` without API calls
- **OpenAI API**: Only used for unknown merchants that don't match any vendor pattern (reduces API costs)
- All category names in vendor mapping must match exactly with `spending_categories` table in database
- Chase transactions require PDF processing, not CSV
- All processors use the same database connection pattern with caching for reference data
- The system handles missing categories, persons, and account types by auto-creating them

## Security Considerations

- Never commit the `.env` file containing API keys and database credentials
- Database connections use environment variables for credentials
- All transaction files (CSV, PDF) should be kept in their respective folders which are gitignored