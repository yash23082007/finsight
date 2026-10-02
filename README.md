# Finsight: Intelligent Personal Financial Analyzer

Finsight is a professional, Python-based financial data analysis application designed for educational and analytical purposes. It transforms raw financial transactions into actionable insights through Data Science, Machine Learning, and an interactive dashboard.

## Features

*   **Interactive Dashboard**: Visualize income, expenses, and savings dynamically.
*   **Data Validation & Cleaning**: Built-in pipeline to process messy transaction CSVs.
*   **Machine Learning Models**:
    *   *Expense Categorization* using TF-IDF and Logistic Regression.
    *   *Anomaly Detection* using Isolation Forest.
    *   *Expense Forecasting* using Linear Regression on time-series data.
*   **Budgeting**: Set and track categorical budgets.
*   **Financial Health Score**: Multi-metric educational scoring system.
*   **Insights Engine**: Deterministic text insights generated from real data.

## Technology Stack

*   Python 3.12+
*   Pandas & NumPy for Data Processing
*   Scikit-Learn for Machine Learning
*   Streamlit for UI/Dashboard
*   Plotly for Data Visualization
*   SQLite + SQLAlchemy for Storage

## Installation

```bash
# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows

# 2. Install requirements
pip install -r requirements.txt

# 3. Generate demo dataset
python scripts/generate_dataset.py

# 4. Run the application
streamlit run app.py
```

## Disclaimer
This project is designed for educational and analytical purposes and does not constitute professional financial advice. Forecasts depend on historical data. Anomaly detection does not prove fraud.

## React + FastAPI stack

The project also includes the API-first application architecture:

* `backend/main.py` - FastAPI REST API backed by SQLite, SQLAlchemy, Pandas, and the existing cleaning and insight modules.
* `frontend/` - Vite React client with React Router, Axios, Tailwind CSS, Recharts, and Lucide icons.

Run the API from the project root:

```bash
venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000
```

Run the React client in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The React client is available at `http://localhost:5173` and the API documentation at `http://localhost:8000/docs`. The API seeds the SQLite database from `data/raw/synthetic_data.csv` when it starts with an empty database.

The REST surface includes `/api/dashboard`, transaction CRUD, analytics, budgets, insights, CSV import, and CSV export. The existing Streamlit application remains available with `streamlit run app.py`.
