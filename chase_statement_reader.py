from pdf_statement_reader import PDFStatementReader
import pandas as pd
from datetime import datetime
import re
import pdfplumber

class ChaseStatementReader(PDFStatementReader):
    """Chase bank statement reader"""
    
    def identify_bank(self) -> bool:
        """Check if this is a Chase statement"""
        with pdfplumber.open(self.pdf_path) as pdf:
            first_page = pdf.pages[0]
            text = first_page.extract_text().lower()
            return 'chase' in text
            
    def extract_transactions(self) -> pd.DataFrame:
        """Extract transactions from Chase PDF statement"""
        transactions = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                
                # Look for lines that start with a date (MM/DD) followed by text and amount
                for line in text.split('\n'):
                    try:
                        # Skip empty lines or headers
                        if not line.strip() or 'ACCOUNT ACTIVITY' in line or 'Date of' in line:
                            continue
                            
                        # Try to match the date pattern at the start of the line
                        if re.match(r'^\d{2}/\d{2}', line.strip()):
                            # Split the line into parts
                            parts = line.strip().split()
                            if len(parts) >= 3:  # Need at least date, description, and amount
                                date = parts[0]
                                
                                # The amount is usually the last part
                                amount = parts[-1].replace('$', '').replace(',', '')
                                
                                # Everything in between is the description
                                description = ' '.join(parts[1:-1])
                                
                                # Validate amount format
                                if re.match(r'^-?\d+\.\d{2}$', amount):
                                    # Add current year to the date
                                    date = f"{date}/{datetime.now().year}"
                                    
                                    transactions.append({
                                        'date': self._standardize_date(date),
                                        'description': description,
                                        'amount': float(amount),
                                        'bank': 'Chase'
                                    })
                    except Exception as e:
                        print(f"Error processing line: {line}, Error: {e}")
                        continue
        
        df = pd.DataFrame(transactions)
        if not df.empty:
            # Sort by date
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        
        return df 