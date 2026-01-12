# Money Review - Personal Finance Transaction Processor

This project is a personal finance tool for reviewing, cleaning, and loading credit card transactions from multiple sources (Apple Card, Chase, Amex, Citi) into a PostgreSQL database. It helps you organize, categorize, and analyze your spending data with AI-powered categorization.

## Features

- **Multi-source transaction processing**: Apple Card (CSV), Chase (PDF), Amex (CSV), and Citi (CSV)
- **AI-powered categorization**: Uses OpenAI GPT-5-nano to automatically categorize transactions
- **Data normalization**: Cleans and standardizes transaction data for each card type
- **Duplicate prevention**: Prevents duplicate transactions via database constraints
- **Automated file management**: Deletes processed files after successful database insertion
- **Secure credential management**: Uses `.env` file for database and API credentials
- **Category management tools**: Scripts to fix and update transaction categories

## Quick Start

### 1. Environment Setup

Create a `.env` file with your credentials:
```env
DB_USER=your_db_user
DB_PASSWORD=your_db_password
OPENAI_API_KEY=your_openai_api_key
```

### 2. Database Setup

Initialize the database schema:
```bash
psql -d money_stuff -f data_base_code/database.sql
```

### 3. Process Transactions

Place transaction files in their respective folders:
- `apple_files/` - Apple Card CSV files
- `chase_files/` - Chase PDF statements
- `Amex_files/` - Amex CSV files  
- `Citi_files/` - Citi CSV files

Run the main processor:
```bash
python main.py
```

## Architecture

### Core Components

1. **AddTransactions (add_transactions.py)**: Abstract base class defining the transaction processing interface
2. **Card-Specific Processors**:
   - `AppleTransactions`: Processes Apple Card CSV files
   - `ChaseTransactions`: Processes Chase PDF statements using AI categorization
   - `AmexTransactions`: Processes Amex CSV files with AI category guessing
   - `CitiTransactions`: Processes Citi CSV files
3. **AIHelper (ai_helper.py)**: Uses OpenAI's GPT-5-nano model for transaction categorization
4. **PDF Processing**: Chase transactions are processed from PDF files using specialized readers

### Database Schema

The PostgreSQL database (`money_stuff`) uses the `budget_app` schema:

- `persons`: User identities
- `spending_categories`: Transaction categories (read-only)
- `account_type`: Card types
- `transactions`: Main transaction table with foreign key relationships
- `transactions_view`: Denormalized view for reporting

### Processing Flow

1. Each processor reads files from its designated folder
2. Data is cleaned and standardized using card-specific logic
3. AI categorization is applied for unknown/missing categories
4. Transactions are inserted into the database with duplicate prevention
5. Successfully processed files are deleted

## Category Management

### Available Categories

The system includes these spending categories:
- Groceries, Dining, Entertainment, Transportation
- Utilities, Shopping, Education, Subscriptions
- Travel, Personal Care, Gifts & Donations
- Insurance, Home Maintenance, Healthcare
- AI Models, Payments, Refunds & Returns
- Interest Charge, Installment, Other

### Update Categories

Use the category update script to update transactions with missing or incorrect categories:

```bash
# Fix transactions with null category IDs
python update_categories.py

# Update all transactions currently categorized as "Other"
python update_categories.py "Other"

# Update any specific category
python update_categories.py "Installment"
```

The script will:
- Find transactions matching your criteria
- Use AI to determine appropriate categories
- Ask for confirmation before bulk updates
- Update the database with new category assignments

## Requirements

- **Python**: 3.11+
- **Database**: PostgreSQL
- **API**: OpenAI API key for AI categorization
- **Dependencies**: See `requirements.txt`

## File Structure

```
Money_review/
├── main.py                     # Main processor
├── add_transactions.py         # Base transaction class
├── apple_transactions.py       # Apple Card processor
├── chase_transactions.py       # Chase Card processor
├── amex_transactions.py        # Amex processor
├── citi_transactions.py        # Citi processor
├── ai_helper.py               # AI categorization helper
├── update_categories.py        # Category management script
├── chase_statement_reader.py   # Chase PDF reader
├── pdf_statement_reader.py     # Generic PDF reader
├── data_base_code/
│   └── database.sql           # Database schema
├── apple_files/               # Apple CSV files
├── chase_files/               # Chase PDF files
├── Amex_files/               # Amex CSV files
├── Citi_files/               # Citi CSV files
└── .env                      # Environment variables (not in git)
```

## Security Considerations

- **Never commit the `.env` file** containing API keys and database credentials
- The system uses environment variables for all sensitive credentials
- Database connections use proper connection pooling and error handling
- All SQL queries use parameterized statements to prevent injection

## Customization

### Adding New Card Types

1. Create a new class inheriting from `AddTransactions`
2. Implement the required abstract methods:
   - `read_files()`: Parse your card's file format
   - `clean_data()`: Standardize the data format
   - `prepare_data_for_db()`: Format for database insertion

### Extending AI Categorization

The `AIHelper` class can be extended to:
- Use different AI models
- Implement custom categorization logic
- Add category confidence scoring
- Support multiple languages

## Troubleshooting

### Common Issues

1. **Database connection errors**: Check your `.env` file and database credentials
2. **OpenAI API errors**: Verify your API key and account has sufficient credits
3. **PDF processing errors**: Ensure Chase PDF files are not password-protected
4. **Category errors**: Use the fix script to update missing or incorrect categories

### Debugging

Enable debug output by uncommenting debug print statements in `ai_helper.py`:
```python
print(f"DEBUG - AI Prompt: {prompt}")
print(f"DEBUG - AI Response: {category}")
```

## Contributing

This is a personal finance tool, but contributions are welcome:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with sample data
5. Submit a pull request

## License

This project is for personal use. Please ensure compliance with your financial institutions' terms of service when processing transaction data.