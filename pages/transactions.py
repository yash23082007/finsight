import streamlit as st
import pandas as pd
from src.database.connection import SessionLocal
from src.database.repository import Repository
from src.utils.constants import TRANSACTION_TYPES, CATEGORIES, PAYMENT_METHODS
from src.database.models import Transaction
import uuid

st.set_page_config(page_title="Transactions | FinSight", page_icon="💸", layout="wide")

st.title("Transactions")

db = SessionLocal()
repo = Repository(db)
df = repo.get_all_transactions_df()

with st.expander("Add New Transaction"):
    with st.form("add_tx_form"):
        col1, col2 = st.columns(2)
        with col1:
            t_date = st.date_input("Date")
            t_desc = st.text_input("Description")
            t_amount = st.number_input("Amount", min_value=0.0, step=10.0)
            t_type = st.selectbox("Type", TRANSACTION_TYPES)
        with col2:
            t_cat = st.selectbox("Category", CATEGORIES.get(t_type, ["Other"]))
            t_method = st.selectbox("Payment Method", PAYMENT_METHODS)
            t_merchant = st.text_input("Merchant")
            t_notes = st.text_input("Notes")
            
        submitted = st.form_submit_button("Add Transaction")
        if submitted:
            new_tx = Transaction(
                id=str(uuid.uuid4()),
                date=t_date,
                description=t_desc,
                amount=t_amount,
                type=t_type,
                category=t_cat,
                payment_method=t_method,
                merchant=t_merchant,
                notes=t_notes
            )
            repo.add_transaction(new_tx)
            st.success("Transaction added successfully!")
            st.rerun()

st.markdown("---")

if df.empty:
    st.info("No transactions available.")
else:
    # Filter
    search = st.text_input("Search description or merchant")
    if search:
        df = df[df['description'].str.contains(search, case=False, na=False) | 
                df['merchant'].str.contains(search, case=False, na=False)]
    
    st.dataframe(
        df[['date', 'description', 'amount', 'type', 'category', 'payment_method', 'merchant']], 
        use_container_width=True
    )
