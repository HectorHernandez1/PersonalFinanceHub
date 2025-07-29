# Database Fix Scripts

This folder contains utility scripts for fixing and maintaining data integrity in the money_stuff database.

## Scripts

### `fix_future_dates.py`
**Purpose**: Fixes transactions with future dates by converting years from 2025 to 2024.

**Usage**:
```bash
python fix_future_dates.py
```

**What it does**:
- Finds all transactions with dates greater than today
- Converts transactions with year 2025 to year 2024
- Shows preview before updating
- Requires user confirmation before making changes
- Updates database with corrected dates

**When to use**: When transaction date parsing incorrectly assigns future years to historical transactions.

### `update_categories.py`
**Purpose**: Fixes transactions with missing category IDs by using AI to categorize them.

**Usage**:
```bash
python update_categories.py
```

**What it does**:
- Finds all transactions where category_id is null
- Uses OpenAI API to determine appropriate categories based on merchant names
- Updates transactions with the AI-suggested categories
- Only assigns categories that exist in the database

**When to use**: When transactions are missing category assignments after import.

## Requirements

Both scripts require:
- `.env` file with `DB_USER` and `DB_PASSWORD` 
- `python-dotenv` package
- `psycopg2` package
- `pandas` package
- For `update_categories.py`: `OPENAI_API_KEY` in `.env`

## Safety Features

- All scripts show previews before making changes
- User confirmation required before database updates
- Transaction rollback on errors
- Detailed logging of what changes are made