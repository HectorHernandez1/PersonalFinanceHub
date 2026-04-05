# PersonalFinanceHub - AI-Powered Transaction Manager

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)](https://www.postgresql.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5--nano-green.svg)](https://openai.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-lightgrey.svg)](https://ollama.com/)

This project is a personal finance tool for reviewing, cleaning, and loading credit card transactions from multiple sources (Apple Card, Chase, Amex, Citi) into a PostgreSQL database. It helps you organize, categorize, and analyze your spending data with AI-powered categorization.

## Features

- **Multi-source transaction processing**: Apple Card (CSV), Chase (PDF), Amex (CSV), and Citi (CSV)
- **AI-powered categorization**: Pluggable LLM backend — use OpenAI GPT-5-nano in the cloud or run a local model through Ollama (e.g. `gemma4:e4b`) for offline, zero-cost inference
- **Data normalization**: Cleans and standardizes transaction data for each card type
- **Duplicate prevention**: Prevents duplicate transactions via database constraints
- **Automated file management**: Deletes processed files after successful database insertion
- **Secure credential management**: Uses `.env` file for database and API credentials
- **Category management tools**: Scripts to fix and update transaction categories

## Quick Start

### 1. Environment Setup

Copy the template and fill in your values:
```bash
cp .env.example .env
```

`.env` contains database credentials and the AI backend selection. The `AI_PROVIDER` variable controls which LLM is used:

**Option A — Local LLM via Ollama** (no API costs, runs offline):
```env
AI_PROVIDER=ollama
OLLAMA_MODEL=gemma4:e4b
OLLAMA_BASE_URL=http://localhost:11434
```
Requires [Ollama](https://ollama.com/) installed and the model pulled:
```bash
ollama pull gemma4:e4b
```
Any Ollama-compatible model works — swap `OLLAMA_MODEL` to `gemma4:26b`, `qwen3:14b`, etc. Point `OLLAMA_BASE_URL` at another machine on your LAN to offload inference.

**Option B — OpenAI** (cloud):
```env
AI_PROVIDER=openai
OPENAI_MODEL=gpt-5-nano
OPENAI_API_KEY=your_openai_api_key
```

Because `.env` is gitignored, each machine can pick its own backend independently — e.g. Ollama on a Linux box with a GPU, OpenAI on a laptop.

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
3. **AIHelper (ai_helper.py)**: Two-stage categorization — first checks `vendor_mapping.py` for known merchants (no LLM call), then falls back to an LLM for unknowns. The LLM backend is chosen at runtime from the `AI_PROVIDER` env var: `ollama` (local, via `langchain-ollama`) or `openai` (cloud, via `langchain-openai`). Imports are lazy so only the selected backend's package is required.
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
- **AI backend** (pick one):
  - [Ollama](https://ollama.com/) running locally (or reachable over your LAN) with a chat model pulled, *or*
  - OpenAI API key
- **Dependencies**: See `requirements.txt`

## File Structure

```
PersonalFinanceHub/
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
3. **Ollama connection errors**: Confirm `ollama serve` is running and `OLLAMA_BASE_URL` is reachable (`curl $OLLAMA_BASE_URL/api/tags`). Make sure the model in `OLLAMA_MODEL` has been pulled (`ollama list`).
4. **PDF processing errors**: Ensure Chase PDF files are not password-protected
5. **Category errors**: Use the fix script to update missing or incorrect categories

### Debugging

Enable debug output by uncommenting debug print statements in `ai_helper.py`:
```python
print(f"DEBUG - AI Prompt: {prompt}")
print(f"DEBUG - AI Response: {category}")
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:
- Reporting issues
- Suggesting enhancements
- Submitting pull requests
- Code style and standards
- Adding new card types

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Disclaimer**: Please ensure compliance with your financial institutions' terms of service when processing transaction data. This software is provided as-is without warranty.