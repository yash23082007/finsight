import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.database.connection import SessionLocal
from src.database.repository import Repository
from src.ml.forecasting import ExpenseForecaster
from src.utils.formatting import format_currency

st.set_page_config(page_title="Forecasting | FinSight", page_icon="🔮", layout="wide")
st.title("Expense Forecasting")

db = SessionLocal()
repo = Repository(db)
df = repo.get_all_transactions_df()

if df.empty:
    st.info("No data available.")
else:
    st.write("Using **Linear Regression** on historical time-series data to estimate future expenses.")
    
    months_ahead = st.slider("Months to forecast", 1, 6, 3)
    
    with st.spinner("Generating forecast..."):
        forecaster = ExpenseForecaster()
        result, msg = forecaster.forecast_next_months(df, months_ahead)
        
    if result is None:
        st.warning(msg)
    else:
        historical, forecast_df, metrics = result
        
        st.subheader("Forecast Results")
        
        # Plotly chart combining historical and forecast
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=historical['date'], 
            y=historical['amount'],
            mode='lines+markers',
            name='Historical Actuals',
            line=dict(color='blue')
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast_df['date'], 
            y=forecast_df['predicted_amount'],
            mode='lines+markers',
            name='Forecast (Estimates)',
            line=dict(color='orange', dash='dash')
        ))
        
        fig.update_layout(title="Monthly Expenses: Historical vs Forecast",
                          xaxis_title="Month",
                          yaxis_title="Amount (₹)")
        
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Future Estimated Expenditure**")
            display_f = forecast_df.copy()
            display_f['predicted_amount'] = display_f['predicted_amount'].apply(format_currency)
            st.dataframe(display_f, hide_index=True)
            
        with col2:
            st.write("**Model Evaluation Metrics**")
            st.metric("Mean Absolute Error (MAE)", round(metrics['MAE'], 2))
            st.metric("Root Mean Squared Error (RMSE)", round(metrics['RMSE'], 2))
            st.metric("R² Score", round(metrics['R2'], 4))
            
    st.markdown("---")
    st.caption("*Forecasts are estimates generated from historical transaction patterns. They are not guaranteed predictions.*")
