import streamlit as st
import pandas as pd
import plotly.express as px
from src.database.connection import SessionLocal
from src.database.repository import Repository
from src.ml.anomaly_detection import AnomalyDetector
from src.utils.formatting import format_currency

st.set_page_config(page_title="Anomaly Detection | FinSight", page_icon="🚨", layout="wide")
st.title("Anomaly Detection")

db = SessionLocal()
repo = Repository(db)
df = repo.get_all_transactions_df()

if df.empty:
    st.info("No data available.")
else:
    st.write("Using **Isolation Forest** Machine Learning model to detect unusual spending patterns based on historical data.")
    
    with st.spinner("Running anomaly detection model..."):
        detector = AnomalyDetector(contamination=0.02)
        df_anomalies = detector.detect_anomalies(df)
        
    if df_anomalies.empty or 'is_anomaly' not in df_anomalies.columns:
        st.info("Insufficient data for anomaly detection (need at least 50 expense records).")
    else:
        anomalies = df_anomalies[df_anomalies['is_anomaly'] == True]
        
        st.metric("Total Anomalies Detected", len(anomalies))
        
        if len(anomalies) > 0:
            st.subheader("Unusual Transactions")
            display_df = anomalies[['date', 'description', 'category', 'amount', 'anomaly_reason']].copy()
            display_df['amount'] = display_df['amount'].apply(format_currency)
            st.dataframe(display_df, use_container_width=True)
            
            st.subheader("Anomaly Visualization")
            fig = px.scatter(df_anomalies, x='date', y='amount', color='is_anomaly',
                             color_discrete_map={True: 'red', False: 'lightgrey'},
                             hover_data=['description', 'category'])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("No anomalies detected in your spending patterns!")
            
    st.markdown("---")
    st.caption("*Note: Anomaly detection identifies outliers based on mathematical deviation from your usual patterns. It does not prove fraudulent activity.*")
