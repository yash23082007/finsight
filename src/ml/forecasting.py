import pandas as pd
import numpy as np
from datetime import date
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

class ExpenseForecaster:
    def __init__(self):
        self.model = LinearRegression()
        self.metrics = {}

    def forecast_next_months(self, df: pd.DataFrame, months_ahead: int = 3) -> tuple:
        """Forecast future expenses using linear regression."""
        df_exp = df[df['type'] == 'Expense'].copy()
        if df_exp.empty:
            return None, "No expense data available."

        df_exp['date'] = pd.to_datetime(df_exp['date'])
        
        # Aggregate by month and exclude only the current calendar month,
        # which may be incomplete. Historical months remain valid even when
        # their final transaction is before month-end.
        monthly = df_exp.resample('ME', on='date')['amount'].sum().reset_index()
        current_month = pd.Timestamp(date.today()).to_period("M")
        if not monthly.empty and monthly["date"].max().to_period("M") == current_month:
            monthly = monthly.iloc[:-1]
        
        if len(monthly) < 6:
            return None, "Insufficient historical data. Need at least 6 months."

        # Create time index for regression
        monthly['time_idx'] = np.arange(len(monthly))
        
        X = monthly[['time_idx']]
        y = monthly['amount']

        self.model.fit(X, y)
        
        # In-sample metrics are descriptive only; rolling metrics compare against
        # baselines so a straight line is not presented as validated performance.
        y_pred = self.model.predict(X)
        residual_std = float(np.std(y - y_pred, ddof=1)) if len(y) > 1 else 0.0
        naive_errors = []
        average_errors = []
        for index in range(3, len(monthly)):
            history = monthly["amount"].iloc[:index]
            actual = monthly["amount"].iloc[index]
            naive_errors.append(abs(actual - history.iloc[-1]))
            average_errors.append(abs(actual - history.iloc[-3:].mean()))
        self.metrics = {
            'MAE': mean_absolute_error(y, y_pred),
            'RMSE': np.sqrt(mean_squared_error(y, y_pred)),
            'R2': r2_score(y, y_pred),
            'naive_mae': float(np.mean(naive_errors)) if naive_errors else None,
            'three_month_average_mae': float(np.mean(average_errors)) if average_errors else None,
        }

        # Forecast
        last_idx = monthly['time_idx'].max()
        future_idx = np.arange(last_idx + 1, last_idx + 1 + months_ahead).reshape(-1, 1)
        
        # Generate future dates correctly
        last_date = monthly['date'].max()
        future_dates = pd.date_range(start=last_date, periods=months_ahead + 1, freq='ME')[1:]
        
        preds = self.model.predict(future_idx)
        lower = np.maximum(0, preds - 1.96 * residual_std)
        upper = np.maximum(0, preds + 1.96 * residual_std)
        
        forecast_df = pd.DataFrame({
            'date': future_dates,
            'predicted_amount': np.maximum(0, preds),
            'lower_bound': lower,
            'upper_bound': upper,
        })
        forecast_df['date'] = forecast_df['date'].dt.strftime('%b %Y')
        
        # Return monthly historical as well for plotting
        monthly['date'] = monthly['date'].dt.strftime('%b %Y')
        
        return (monthly, forecast_df, self.metrics), "Forecast generated successfully."
