import streamlit as st
import pandas as pd
import plotly.express as px
from src.database.connection import SessionLocal
from src.database.repository import Repository
from src.utils.formatting import format_currency

st.set_page_config(page_title="Spending Analysis | FinSight", page_icon="📉", layout="wide")
st.title("Spending Analysis")

db = SessionLocal()
repo = Repository(db)
df = repo.get_all_transactions_df()

if df.empty:
    st.info("No data available.")
else:
    df['date'] = pd.to_datetime(df['date'])
    df_exp = df[df['type'] == 'Expense'].copy()
    
    st.sidebar.header("Filters")
    selected_year = st.sidebar.selectbox("Year", df_exp['date'].dt.year.unique())
    df_filtered = df_exp[df_exp['date'].dt.year == selected_year]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Category Distribution")
        cat_dist = df_filtered.groupby('category')['amount'].sum().reset_index()
        fig1 = px.pie(cat_dist, values='amount', names='category', hole=0.3)
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        st.subheader("Monthly Spending Trend")
        monthly = df_filtered.resample('ME', on='date')['amount'].sum().reset_index()
        fig2 = px.line(monthly, x='date', y='amount', markers=True)
        st.plotly_chart(fig2, use_container_width=True)
        
    st.subheader("Top 10 Merchants")
    top_merchants = df_filtered.groupby('merchant')['amount'].sum().nlargest(10).reset_index()
    fig3 = px.bar(top_merchants, x='merchant', y='amount', text='amount')
    fig3.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    st.plotly_chart(fig3, use_container_width=True)
    
    st.subheader("Statistics")
    stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
    with stats_col1:
        st.metric("Average Transaction", format_currency(df_filtered['amount'].mean()))
    with stats_col2:
        st.metric("Median Transaction", format_currency(df_filtered['amount'].median()))
    with stats_col3:
        st.metric("Max Transaction", format_currency(df_filtered['amount'].max()))
    with stats_col4:
        st.metric("Total Spending", format_currency(df_filtered['amount'].sum()))
