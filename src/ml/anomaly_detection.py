import pandas as pd
from sklearn.ensemble import IsolationForest
import numpy as np

class AnomalyDetector:
    def __init__(self, contamination="auto"):
        self.model = IsolationForest(contamination=contamination, random_state=42)

    def detect_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect anomalies in expense amounts."""
        df_exp = df[df['type'] == 'Expense'].copy()
        
        if len(df_exp) < 10:
            df_exp['is_anomaly'] = False
            df_exp['anomaly_reason'] = ""
            return df_exp

        # Feature: Amount and frequency within category
        # Here we just use amount for simplicity, but scaled per category
        df_exp['amount_log'] = np.log1p(df_exp['amount'])
        
        cat_medians = df_exp.groupby('category')['amount'].transform('median')
        mad = df_exp.groupby('category')['amount'].transform(
            lambda values: (values - values.median()).abs().median()
        ).replace(0, np.nan)
        df_exp['robust_z_score'] = ((df_exp['amount'] - cat_medians) / (1.4826 * mad)).fillna(0)
        
        # Fit model on Z-scores
        features = df_exp[['amount_log', 'robust_z_score']].fillna(0)
        
        preds = self.model.fit_predict(features)
        
        df_exp['is_anomaly'] = preds == -1
        
        def get_reason(row):
            if row['is_anomaly']:
                typical = df_exp.loc[df_exp["category"] == row["category"], "amount"].median()
                multiple = row["amount"] / typical if typical else 0
                return f"{multiple:.1f}× your typical {row['category']} spend."
            return ""

        df_exp['anomaly_reason'] = df_exp.apply(get_reason, axis=1)
        return df_exp
