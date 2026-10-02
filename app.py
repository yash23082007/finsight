import streamlit as st
import os
from src.database.connection import init_db

# Page config must be first
st.set_page_config(
    page_title="FinSight | Financial Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize DB
init_db()

st.title("📊 FinSight: Intelligent Personal Financial Analyzer")

st.markdown("""
Welcome to **FinSight**! Turn your raw financial transactions into actionable insights.
Please use the sidebar to navigate through the application.

### Features
* **Overview:** High-level dashboard of your finances.
* **Transactions:** View, search, and manage your raw data.
* **Spending Analysis:** In-depth visualizations of your spending habits.
* **Budget Analysis:** Track your monthly category budgets.
* **Financial Health:** Get an educational score on your financial behavior.
* **Anomaly Detection:** Identify unusual spending using Machine Learning.
* **Forecasting:** Estimate future expenses based on historical trends.
* **Insights:** Read deterministic text insights generated from your data.
* **Data Management:** Upload CSV files or load demo data.
""")

st.info("👈 Select a page from the sidebar to get started.")

st.markdown("---")
st.caption("FinSight is a professional Data Science & Machine Learning project designed for educational purposes.")
