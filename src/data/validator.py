import pandas as pd
from typing import Tuple, Dict, Any

class DataValidator:
    """Validates raw transaction data."""
    
    REQUIRED_COLUMNS = ['date', 'description', 'amount', 'type']
    
    @classmethod
    def validate_csv(cls, df: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
        """Validates CSV structure and contents."""
        report = {
            "is_valid": True,
            "missing_columns": [],
            "total_rows": len(df),
            "errors": []
        }
        
        # Normalize headers without mutating the caller's dataframe.
        normalized_columns = df.columns.astype(str).str.lower().str.strip()
        
        # Check required columns
        for col in cls.REQUIRED_COLUMNS:
            if col not in normalized_columns:
                report["missing_columns"].append(col)
                report["is_valid"] = False
                
        if not report["is_valid"]:
            report["errors"].append(f"Missing required columns: {', '.join(report['missing_columns'])}")
            return False, report
            
        return True, report
