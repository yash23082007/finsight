import streamlit as st
import pandas as pd
from src.database.connection import SessionLocal
from src.database.repository import Repository
from src.analytics.health_score import HealthScoreCalculator

st.set_page_config(page_title="Financial Health | FinSight", page_icon="❤️", layout="wide")
st.title("Financial Health Score")

db = SessionLocal()
repo = Repository(db)
df = repo.get_all_transactions_df()

if df.empty:
    st.info("No data available.")
else:
    result = HealthScoreCalculator.calculate_score(df)
    score = result['score']
    
    st.markdown(f"### Overall Score: {score} / 100")
    st.progress(score / 100)
    st.caption(result['message'])
    
    st.markdown("---")
    st.subheader("Component Breakdown")
    
    col1, col2, col3 = st.columns(3)
    
    components = result['components']
    
    with col1:
        st.metric("Savings Rate Score", f"{components.get('Savings Rate', 0)} / 100")
        st.info("Measures how much of your income you save. (Target: > 20%)")
        
    with col2:
        st.metric("Expense Control Score", f"{components.get('Expense Control', 0)} / 100")
        st.info("Measures expenses relative to income. (Target: < 80%)")
        
    with col3:
        st.metric("Consistency Score", f"{components.get('Consistency', 0)} / 100")
        st.info("Measures stability of your month-to-month spending.")

    st.markdown("---")
    st.warning("**Disclaimer**: This is an educational metric based on general financial principles. It is not professional financial advice.")
