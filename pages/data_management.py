import streamlit as st
import pandas as pd
import os
from src.database.connection import SessionLocal
from src.database.repository import Repository
from src.data.cleaner import DataCleaner
from src.data.validator import DataValidator
from scripts.generate_dataset import generate_transactions
from src.database.models import Transaction

st.set_page_config(page_title="Data Management | FinSight", page_icon="🗄️", layout="wide")

st.title("Data Management")

db = SessionLocal()
repo = Repository(db)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Load Demo Dataset")
    st.write("Generate and load a synthetic 24-month transaction dataset.")
    if st.button("Generate & Load Demo Data"):
        with st.spinner("Generating 5000 transactions..."):
            df_demo = generate_transactions(5000, 24)
            df_demo, report = DataCleaner.clean_data(df_demo)
            
            repo.clear_all_transactions()
            
            txs = []
            for _, row in df_demo.iterrows():
                tx = Transaction(
                    id=row['transaction_id'],
                    date=pd.to_datetime(row['date']).date(),
                    description=row['description'],
                    amount=row['amount'],
                    type=row['type'],
                    category=row['category'],
                    payment_method=row['payment_method'],
                    merchant=row['merchant'],
                    notes=row['notes']
                )
                txs.append(tx)
                
            repo.bulk_add_transactions(txs)
            st.success(f"Successfully loaded {len(txs)} demo transactions!")
            st.json(report)

with col2:
    st.subheader("Upload CSV")
    uploaded_file = st.file_uploader("Upload your transactions (CSV)", type="csv")
    
    if uploaded_file is not None:
        df_raw = pd.read_csv(uploaded_file)
        
        is_valid, v_report = DataValidator.validate_csv(df_raw)
        
        if not is_valid:
            st.error("Validation Failed")
            st.json(v_report)
        else:
            st.success("Validation Passed!")
            if st.button("Clean & Import"):
                with st.spinner("Cleaning data..."):
                    df_clean, c_report = DataCleaner.clean_data(df_raw)
                    st.json(c_report)
                    
                    # Convert and save
                    repo.clear_all_transactions() # Warning: this clears existing data
                    txs = []
                    for _, row in df_clean.iterrows():
                        tx = Transaction(
                            id=row['transaction_id'],
                            date=pd.to_datetime(row['date']).date(),
                            description=row['description'],
                            amount=row['amount'],
                            type=row['type'],
                            category=row.get('category', 'Other'),
                            payment_method=row.get('payment_method', 'Other'),
                            merchant=row.get('merchant', ''),
                            notes=row.get('notes', '')
                        )
                        txs.append(tx)
                    repo.bulk_add_transactions(txs)
                    st.success(f"Imported {len(txs)} records!")

st.markdown("---")
st.warning("⚠️ Loading new data will clear existing transactions in the database.")
