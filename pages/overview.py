import streamlit as st
import pandas as pd
import plotly.express as px
from src.database.connection import SessionLocal
from src.database.repository import Repository
from src.utils.formatting import format_currency, format_percentage

st.set_page_config(page_title="Overview | FinSight", page_icon="📈", layout="wide")

st.title("Dashboard Overview")

db = SessionLocal()
repo = Repository(db)
df = repo.get_all_transactions_df()

if df.empty:
    st.warning("No transactions found. Please head to Data Management to load data.")
else:
    df['date'] = pd.to_datetime(df['date'])
    
    # Filters
    st.sidebar.header("Filters")
    date_range = st.sidebar.date_input("Date Range", [df['date'].min(), df['date'].max()])
    
    if len(date_range) == 2:
        mask = (df['date'].dt.date >= date_range[0]) & (df['date'].dt.date <= date_range[1])
        df_filtered = df.loc[mask]
    else:
        df_filtered = df.copy()
        
    categories = st.sidebar.multiselect("Categories", df_filtered['category'].unique())
    if categories:
        df_filtered = df_filtered[df_filtered['category'].isin(categories)]

    # KPIs
    inc_df = df_filtered[df_filtered['type'] == 'Income']
    exp_df = df_filtered[df_filtered['type'] == 'Expense']
    
    total_income = inc_df['amount'].sum()
    total_expense = exp_df['amount'].sum()
    net_savings = total_income - total_expense
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Income", format_currency(total_income))
    with col2:
        st.metric("Total Expenses", format_currency(total_expense))
    with col3:
        st.metric("Net Savings", format_currency(net_savings))
    with col4:
        st.metric("Savings Rate", format_percentage(savings_rate))
        
    st.markdown("---")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Income vs Expense Trend")
        monthly = df_filtered.groupby([df_filtered['date'].dt.to_period('M'), 'type'])['amount'].sum().reset_index()
        monthly['date'] = monthly['date'].astype(str)
        if not monthly.empty:
            fig = px.bar(monthly, x='date', y='amount', color='type', barmode='group',
                         color_discrete_map={'Income': '#2ecc71', 'Expense': '#e74c3c'})
            st.plotly_chart(fig, use_container_width=True)
            
    with col_chart2:
        st.subheader("Expense Distribution")
        if not exp_df.empty:
            cat_dist = exp_df.groupby('category')['amount'].sum().reset_index()
            fig2 = px.pie(cat_dist, values='amount', names='category', hole=0.4)
            st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Recent Transactions")
    st.dataframe(df_filtered.sort_values('date', ascending=False).head(10)[
        ['date', 'description', 'category', 'amount', 'type']
    ], use_container_width=True)
