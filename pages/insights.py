import streamlit as st
from src.database.connection import SessionLocal
from src.database.repository import Repository
from src.analytics.insights import InsightEngine

st.set_page_config(page_title="Insights | FinSight", page_icon="💡", layout="wide")
st.title("Data Insights")

db = SessionLocal()
repo = Repository(db)
df = repo.get_all_transactions_df()

if df.empty:
    st.info("No data available to generate insights.")
else:
    with st.spinner("Analyzing your data..."):
        engine = InsightEngine()
        insights = engine.generate_insights(df)
        
    for insight in insights:
        if insight.get('type') == 'success':
            st.success(f"**{insight['title']}**: {insight['description']} (Metric: {insight['metric']})")
        elif insight.get('type') == 'warning':
            st.warning(f"**{insight['title']}**: {insight['description']} (Metric: {insight['metric']})")
        else:
            st.info(f"**{insight['title']}**: {insight['description']} (Metric: {insight['metric']})")

    st.markdown("---")
    st.subheader("Natural Language Query (Simulated deterministic analytics)")
    query = st.selectbox(
        "Ask a question about your finances",
        ["Select a question...", "How much did I spend on food overall?", "What was my highest expense?", "How much did I save in total?"]
    )
    
    if query == "How much did I spend on food overall?":
        food_exp = df[(df['type']=='Expense') & (df['category']=='Food')]['amount'].sum()
        st.write(f"You spent a total of **₹{food_exp:,.2f}** on Food.")
    elif query == "What was my highest expense?":
        exp_df = df[df['type']=='Expense']
        if not exp_df.empty:
            max_row = exp_df.loc[exp_df['amount'].idxmax()]
            st.write(f"Your highest expense was **₹{max_row['amount']:,.2f}** at **{max_row['merchant']}** on **{max_row['date']}**.")
    elif query == "How much did I save in total?":
        inc = df[df['type']=='Income']['amount'].sum()
        exp = df[df['type']=='Expense']['amount'].sum()
        st.write(f"Your total net savings are **₹{(inc - exp):,.2f}**.")
