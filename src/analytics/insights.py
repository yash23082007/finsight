import pandas as pd
from typing import List, Dict, Any

class InsightEngine:
    """Generates deterministic insights based on financial data."""

    @staticmethod
    def generate_insights(df: pd.DataFrame) -> List[Dict[str, str]]:
        if df.empty:
            return [{"title": "No Data", "description": "Add transactions to see insights.", "type": "info"}]

        insights = []
        df['date'] = pd.to_datetime(df['date'])
        
        # Add Month-Year column for aggregation
        df_copy = df.copy()
        df_copy['month_year'] = df_copy['date'].dt.to_period('M')

        # 1. Largest Expense Category Overall
        expenses = df_copy[df_copy['type'] == 'Expense']
        if not expenses.empty:
            cat_totals = expenses.groupby('category')['amount'].sum()
            top_cat = cat_totals.idxmax()
            top_amt = cat_totals.max()
            total_exp = expenses['amount'].sum()
            pct = (top_amt / total_exp) * 100
            
            insights.append({
                "title": "Largest Expense Category",
                "description": f"{top_cat} is your largest expense, making up {pct:.1f}% of total expenditure.",
                "metric": f"₹{top_amt:,.2f}",
                "type": "warning"
            })

        # 2. Savings Rate Trend (Current vs Previous Month)
        monthly_summary = df_copy.groupby(['month_year', 'type'])['amount'].sum().unstack(fill_value=0).reset_index()
        
        if len(monthly_summary) >= 2:
            monthly_summary = monthly_summary.sort_values('month_year')
            curr_month = monthly_summary.iloc[-1]
            prev_month = monthly_summary.iloc[-2]
            
            curr_income = curr_month.get('Income', 0)
            curr_exp = curr_month.get('Expense', 0)
            prev_income = prev_month.get('Income', 0)
            prev_exp = prev_month.get('Expense', 0)
            
            curr_savings = curr_income - curr_exp
            prev_savings = prev_income - prev_exp
            
            curr_rate = (curr_savings / curr_income * 100) if curr_income > 0 else 0
            prev_rate = (prev_savings / prev_income * 100) if prev_income > 0 else 0
            
            diff = curr_rate - prev_rate
            if diff > 0:
                insights.append({
                    "title": "Improved Savings Rate",
                    "description": f"Your savings rate increased by {diff:.1f}% compared to the previous month.",
                    "metric": f"{curr_rate:.1f}%",
                    "type": "success"
                })
            elif diff < 0:
                insights.append({
                    "title": "Decreased Savings Rate",
                    "description": f"Your savings rate decreased by {abs(diff):.1f}% compared to the previous month.",
                    "metric": f"{curr_rate:.1f}%",
                    "type": "warning"
                })

        # 3. High-Value Transactions
        if not expenses.empty:
            mean_exp = expenses['amount'].mean()
            std_exp = expenses['amount'].std()
            high_val_thresh = mean_exp + (2 * std_exp)
            high_val_count = (expenses['amount'] > high_val_thresh).sum()
            
            if high_val_count > 0:
                insights.append({
                    "title": "High-Value Transactions",
                    "description": f"You had {high_val_count} transactions substantially above your average expense.",
                    "metric": f"{high_val_count} count",
                    "type": "info"
                })

        return insights
