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
**Purpose**: Fixes transactions with missing or incorrect category IDs using vendor mapping and AI categorization.

**Usage**:

Update transactions with null category_id (uses vendor mapping first, then OpenAI for unknowns):
```bash
python update_categories.py
```

Update all transactions with a specific category (example: update all "Other" transactions):
```bash
python update_categories.py "Other"
```

**What it does**:
- Finds transactions with null category_id (or specific category if provided)
- **First attempts**: Checks vendor mapping for known merchants (instant, no API cost)
- **Falls back to**: OpenAI API for unknown merchants that don't match vendor patterns
- Only assigns categories that exist in the database
- Provides detailed output showing which method was used for each transaction
- Shows final summary with breakdown of categorizations

**Examples**:
- `python update_categories.py` - Fix all null category transactions
- `python update_categories.py "Other"` - Recategorize all "Other" transactions
- `python update_categories.py "Education"` - Recategorize all "Education" transactions

**When to use**:
- When transactions are missing category assignments after import
- When you want to recategorize existing transactions using updated vendor mappings
- When you need to improve categorization accuracy without re-processing files

## Requirements

Both scripts require:
- `.env` file with `DB_USER` and `DB_PASSWORD`
- `python-dotenv` package
- `psycopg2` package
- `pandas` package
- For `update_categories.py`:
  - `OPENAI_API_KEY` in `.env` (only used for unknown merchants not in vendor mapping)
  - Access to `vendor_mapping.py` module for known merchant categorization

## Safety Features

- All scripts show previews before making changes
- User confirmation required before database updates
- Transaction rollback on errors
- Detailed logging of what changes are made