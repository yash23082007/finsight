import pandas as pd

class HealthScoreCalculator:
    @staticmethod
    def calculate_score(df: pd.DataFrame) -> dict:
        """Calculate educational financial health score."""
        if df.empty:
            return {"score": 0, "components": {}, "message": "No data"}
            
        df['date'] = pd.to_datetime(df['date'])
        
        # Get last 3 months
        recent_date = df['date'].max()
        start_date = recent_date - pd.DateOffset(months=3)
        recent_df = df[df['date'] > start_date]
        limited_data = (recent_df['date'].max() - recent_df['date'].min()).days < 42
        
        income = recent_df[recent_df['type'] == 'Income']['amount'].sum()
        expense = recent_df[recent_df['type'] == 'Expense']['amount'].sum()
        
        if income == 0:
            message = "No income recorded"
            if limited_data:
                message += "; limited data"
            return {"score": 0, "components": {"savings_rate": 0, "expense_control": 0}, "message": message}
            
        savings_rate = ((income - expense) / income) * 100
        
        # Component 1: Savings Rate (Max 40 points)
        # Optimal: >= 20%
        sr_score = min(40, max(0, (savings_rate / 20) * 40))
        
        # Component 2: Expense to Income Ratio (Max 40 points)
        # Optimal: <= 80%
        e_ratio = (expense / income) * 100
        er_score = min(40, max(0, ((100 - e_ratio) / 20) * 40)) if e_ratio <= 100 else 0
        
        # Component 3: Consistency (Max 20 points)
        # Low variance in monthly expenses
        monthly_exp = recent_df[recent_df['type']=='Expense'].resample('ME', on='date')['amount'].sum()
        cv = monthly_exp.std() / monthly_exp.mean() if monthly_exp.mean() > 0 and not pd.isna(monthly_exp.std()) else 1
        consistency_score = min(20, max(0, 20 - (cv * 20)))
        
        total_score = sr_score + er_score + consistency_score
        
        return {
            "score": round(total_score),
            "components": {
                "Savings Rate": round(sr_score / 40 * 100),
                "Expense Control": round(er_score / 40 * 100),
                "Consistency": round(consistency_score / 20 * 100)
            },
            "message": "Calculated based on the last 3 months." + (" Limited data: use cautiously." if limited_data else "")
        }
