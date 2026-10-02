import pandas as pd
from sklearn.ensemble import IsolationForest
import numpy as np

class AnomalyDetector:
    def __init__(self, contamination=0.01):
        self.model = IsolationForest(contamination=contamination, random_state=42)

    def detect_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect anomalies in expense amounts."""
        df_exp = df[df['type'] == 'Expense'].copy()
        
        if len(df_exp) < 50:
            df_exp['is_anomaly'] = False
            df_exp['anomaly_reason'] = ""
            return df_exp

        # Feature: Amount and frequency within category
        # Here we just use amount for simplicity, but scaled per category
        df_exp['amount_log'] = np.log1p(df_exp['amount'])
        
        cat_means = df_exp.groupby('category')['amount'].transform('mean')
        cat_stds = df_exp.groupby('category')['amount'].transform('std').fillna(1)
        
        df_exp['z_score'] = (df_exp['amount'] - cat_means) / cat_stds
        
        # Fit model on Z-scores
        features = df_exp[['z_score']].fillna(0)
        
        preds = self.model.fit_predict(features)
        
        df_exp['is_anomaly'] = preds == -1
        
        def get_reason(row):
            if row['is_anomaly']:
                if row['amount'] > row['amount'] - (row['z_score'] * 1): # simple check
                     return f"This transaction is substantially higher than your historical {row['category']} transactions."
                return "Unusual transaction pattern."
            return ""

        df_exp['anomaly_reason'] = df_exp.apply(get_reason, axis=1)
        return df_exp
