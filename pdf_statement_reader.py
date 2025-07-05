import pdfplumber
import pandas as pd
import re
from typing import Dict, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime

class PDFStatementReader(ABC):
    """Abstract base class for reading bank statements"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        
    @abstractmethod
    def identify_bank(self) -> bool:
        """Check if the PDF matches this bank's format"""
        pass
    
    @abstractmethod
    def extract_transactions(self) -> pd.DataFrame:
        """Extract transactions from the PDF into a standardized DataFrame"""
        pass
    
    def _standardize_date(self, date_str: str) -> str:
        """Convert various date formats to YYYY-MM-DD"""
        try:
            if not isinstance(date_str, str) or date_str.lower() == 'nan':
                return None
            # Try different date formats
            for fmt in ['%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y']:
                try:
                    return datetime.strptime(date_str.strip(), fmt).strftime('%Y-%m-%d')
                except ValueError:
                    continue
            raise ValueError(f"Unrecognized date format: {date_str}")
        except Exception as e:
            print(f"Error standardizing date {date_str}: {e}")
            return None

    def _standardize_amount(self, amount_str: str) -> float:
        """Convert amount string to float, handling different formats"""
        try:
            if not isinstance(amount_str, str) or amount_str.lower() == 'nan':
                return None
            # Remove currency symbols and commas
            amount_str = re.sub(r'[$,]', '', amount_str.strip())
            # Handle parentheses for negative numbers
            if amount_str.startswith('(') and amount_str.endswith(')'):
                amount_str = '-' + amount_str[1:-1]
            return float(amount_str)
        except Exception as e:
            print(f"Error standardizing amount {amount_str}: {e}")
            return None

def read_statement(pdf_path: str, reader_class) -> pd.DataFrame:
    """
    Read a bank statement using the specified reader class
    
    Args:
        pdf_path: Path to the PDF statement
        reader_class: Class to use for reading the statement
        
    Returns:
        DataFrame with standardized transaction data
    """
    try:
        reader = reader_class(pdf_path)
        if reader.identify_bank():
            return reader.extract_transactions()
        else:
            raise ValueError(f"PDF not recognized as valid format for {reader_class.__name__}")
    except Exception as e:
        print(f"Error reading statement: {e}")
        return pd.DataFrame() 