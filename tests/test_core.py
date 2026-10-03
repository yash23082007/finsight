import pytest
import pandas as pd
import numpy as np
from src.data.cleaner import DataCleaner
from src.data.validator import DataValidator
from src.analytics.health_score import HealthScoreCalculator
from src.ml.forecasting import ExpenseForecaster

def test_data_validator():
    df_valid = pd.DataFrame({
        'date': ['2023-01-01'],
        'description': ['Test'],
        'amount': [100],
        'type': ['Expense']
    })
    is_valid, _ = DataValidator.validate_csv(df_valid)
    assert is_valid == True

    df_invalid = pd.DataFrame({
        'description': ['Test'],
        'amount': [100]
    })
    is_valid, report = DataValidator.validate_csv(df_invalid)
    assert is_valid == False
    assert 'date' in report['missing_columns']

def test_data_cleaner():
    df_raw = pd.DataFrame({
        'date': ['2023-01-01', 'invalid', '2023-01-01'],
        'description': ['Test', 'Test 2', 'Test'],
        'amount': ['$100', '200', '$100'],
        'type': ['Expense', 'Income', 'Expense']
    })
    
    df_clean, report = DataCleaner.clean_data(df_raw)
    
    # Invalid rows are removed, while identical-looking transactions survive
    # because two real purchases can share date, description, and amount.
    assert len(df_clean) == 2
    assert df_clean.iloc[0]['amount'] == 100.0
    assert 'transaction_id' in df_clean.columns

def test_health_score():
    # Perfect score scenario
    df = pd.DataFrame({
        'date': pd.date_range(start='1/1/2023', periods=90, freq='D'),
        'amount': [30] * 90, # 90 days * 30 = 2700 expense
        'type': ['Expense'] * 90
    })
    # Add income
    df.loc[90] = ['2023-02-01', 5000, 'Income']
    df.loc[91] = ['2023-03-01', 5000, 'Income']
    df.loc[92] = ['2023-01-01', 5000, 'Income'] # total 15000 income
    
    # Savings: 15000 - 2700 = 12300 (82% savings rate)
    
    res = HealthScoreCalculator.calculate_score(df)
    assert res['score'] > 80 # Should be a very high score


def test_forecaster_keeps_completed_historical_month():
    dates = pd.date_range("2023-01-01", periods=6, freq="MS")
    frame = pd.DataFrame({
        "date": dates + pd.Timedelta(days=10),
        "type": ["Expense"] * 6,
        "amount": [100, 110, 120, 130, 140, 150],
    })

    result, message = ExpenseForecaster().forecast_next_months(frame)

    assert message == "Forecast generated successfully."
    historical, forecast, metrics = result
    assert len(historical) == 6
    assert len(forecast) == 3
    assert "three_month_average_mae" in metrics
