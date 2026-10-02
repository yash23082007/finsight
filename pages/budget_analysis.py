import streamlit as st
import pandas as pd
from src.database.connection import SessionLocal
from src.database.repository import Repository
from src.database.models import Budget
from src.utils.formatting import format_currency, format_percentage

st.set_page_config(page_title="Budget Analysis | FinSight", page_icon="💰", layout="wide")
st.title("Budget Analysis")

db = SessionLocal()
repo = Repository(db)
df = repo.get_all_transactions_df()
budgets_df = repo.get_budgets_df()

if df.empty:
    st.info("No data available.")
else:
    df['date'] = pd.to_datetime(df['date'])
    df['month_year'] = df['date'].dt.strftime('%Y-%m')
    
    months = sorted(df['month_year'].unique(), reverse=True)
    selected_month = st.selectbox("Select Month", months)
    
    # Filter data for selected month
    month_df = df[(df['month_year'] == selected_month) & (df['type'] == 'Expense')]
    
    st.subheader("Set Budgets")
    categories = df[df['type'] == 'Expense']['category'].unique()
    
    with st.expander("Update Category Budgets"):
        for cat in categories:
            # Get existing budget if any
            existing_budget = budgets_df[(budgets_df['category'] == cat) & (budgets_df['month_year'] == selected_month)]
            default_val = float(existing_budget['amount'].iloc[0]) if not existing_budget.empty else 0.0
            
            new_val = st.number_input(f"{cat} Budget", min_value=0.0, value=default_val, step=500.0, key=f"budget_{cat}")
            
            if new_val != default_val:
                b = Budget(category=cat, amount=new_val, month_year=selected_month)
                repo.save_budget(b)
                st.success(f"Saved {cat} budget.")

    st.markdown("---")
    st.subheader("Budget Utilization")
    
    actual_spending = month_df.groupby('category')['amount'].sum().to_dict()
    
    budgets = repo.get_budgets_df()
    month_budgets = budgets[budgets['month_year'] == selected_month]
    
    if month_budgets.empty:
        st.warning("No budgets set for this month.")
    else:
        for _, row in month_budgets.iterrows():
            cat = row['category']
            budget_amt = row['amount']
            actual_amt = actual_spending.get(cat, 0)
            
            remaining = budget_amt - actual_amt
            pct = (actual_amt / budget_amt * 100) if budget_amt > 0 else 0
            
            st.markdown(f"**{cat}**")
            cols = st.columns([3, 1, 1, 1])
            with cols[0]:
                prog_val = min(pct / 100, 1.0)
                st.progress(prog_val)
            with cols[1]:
                st.write(f"Budget: {format_currency(budget_amt)}")
            with cols[2]:
                st.write(f"Actual: {format_currency(actual_amt)}")
            with cols[3]:
                if remaining < 0:
                    st.error(f"Exceeded by {format_currency(abs(remaining))}")
                else:
                    st.success(f"Left: {format_currency(remaining)}")
