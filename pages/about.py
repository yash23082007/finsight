import streamlit as st

st.set_page_config(page_title="About | FinSight", page_icon="ℹ️", layout="wide")

st.title("About FinSight")

st.markdown("""
### Project
**FinSight: Intelligent Personal Financial Analyzer**

### Purpose
Financial data analysis and educational insights to help users understand their spending patterns and make informed decisions.

### Training
**Python for Data Science**

### Training Platform
**Infosys Springboard**

### Developer
**Yash Vijay**

### Program
B.Tech CSE-AI

### Institute
JECRC Foundation, Jaipur

---

### Technologies Used
* **Python 3.12+**
* **Pandas & NumPy** for data manipulation
* **Scikit-learn** for Machine Learning (TF-IDF, Logistic Regression, Isolation Forest, Linear Regression)
* **Streamlit** for the interactive frontend
* **Plotly** for dynamic visualizations
* **SQLite & SQLAlchemy** for database management

---

### Limitations & Disclaimer
* This project is designed for educational and analytical purposes and does not constitute professional financial advice.
* Forecasts depend heavily on historical data patterns and are not guaranteed predictions.
* The demo dataset used for illustration is purely synthetic and does not represent real financial activity.
* Anomaly detection algorithms identify statistical outliers but do not prove or confirm fraudulent activity.
* The financial health score is an educational metric derived from standard budgeting principles.
""")
