import pandas as pd
import uuid
import numpy as np
from typing import Tuple
from src.utils.logging_config import logger

class DataCleaner:
    """Cleans and standardizes transaction data."""
    
    @staticmethod
    def clean_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
        """
        Cleans the dataframe.
        Returns: Tuple of cleaned dataframe and a report dictionary.
        """
        report = {
            "initial_rows": len(df),
            "duplicates_removed": 0,
            "missing_values_handled": 0,
            "invalid_rows_removed": 0
        }
        
        # Copy to avoid SettingWithCopyWarning
        df_clean = df.copy()
        
        # Normalize column names
        df_clean.columns = df_clean.columns.str.lower().str.strip()
        
        # Remove duplicates
        initial_count = len(df_clean)
        df_clean = df_clean.drop_duplicates()
        report["duplicates_removed"] = initial_count - len(df_clean)
        
        # Handle date parsing
        if 'date' in df_clean.columns:
            df_clean['date'] = pd.to_datetime(df_clean['date'], errors='coerce')
            invalid_dates = df_clean['date'].isna().sum()
            if invalid_dates > 0:
                report["invalid_rows_removed"] += invalid_dates
                df_clean = df_clean.dropna(subset=['date'])
                
        # Handle amount parsing
        if 'amount' in df_clean.columns:
            # Remove any currency symbols and commas
            if df_clean['amount'].dtype == object:
                df_clean['amount'] = df_clean['amount'].astype(str).str.replace(r'[₹$,]', '', regex=True)
            df_clean['amount'] = pd.to_numeric(df_clean['amount'], errors='coerce')
            
            invalid_amounts = df_clean['amount'].isna().sum()
            if invalid_amounts > 0:
                report["invalid_rows_removed"] += invalid_amounts
                df_clean = df_clean.dropna(subset=['amount'])
                
            # Ensure positive amounts
            df_clean['amount'] = df_clean['amount'].abs()
            
        # Standardize strings
        string_cols = ['description', 'category', 'merchant', 'payment_method', 'type']
        for col in string_cols:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).str.strip().str.title()
                df_clean[col] = df_clean[col].replace(['Nan', 'None', ''], 'Unknown')
                
        # Ensure type is strictly Income or Expense
        if 'type' in df_clean.columns:
            df_clean['type'] = df_clean['type'].apply(lambda x: x if x in ['Income', 'Expense'] else 'Expense')
            
        # Generate IDs if missing
        if 'transaction_id' not in df_clean.columns:
            df_clean['transaction_id'] = [str(uuid.uuid4()) for _ in range(len(df_clean))]
            
        # Ensure notes column exists
        if 'notes' not in df_clean.columns:
            df_clean['notes'] = ''
            
        report["final_rows"] = len(df_clean)
        return df_clean, report
