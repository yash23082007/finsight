# FinSight

FinSight is an intelligent personal finance analyzer that turns transaction data into
interactive dashboards, machine-learning insights, and practical spending analysis.
It is intended for educational and analytical use.

## Highlights

- Interactive Streamlit dashboard for income, expenses, savings, budgets, and financial health.
- Transaction validation, cleaning, CSV import, and demo data loading.
- Expense categorization with TF-IDF and logistic regression.
- Anomaly detection with Isolation Forest.
- Expense forecasting with linear regression.
- Deterministic, data-driven financial insights.
- SQLite persistence through SQLAlchemy.
- Optional React and FastAPI architecture for a modern API-first experience.

## Technology

### Backend and analytics

- Python 3.12+
- Pandas, NumPy, SciPy, and scikit-learn
- Streamlit and Plotly
- FastAPI, Uvicorn, Pydantic, and SQLAlchemy
- SQLite

### Frontend

- React 18
- Vite
- React Router
- Axios
- Recharts and Lucide React

## Project structure

```text
finsight/
├── app.py                 # Streamlit entry point
├── backend/main.py        # FastAPI application
├── pages/                 # Streamlit pages
├── src/
│   ├── analytics/         # Health score and insight generation
│   ├── data/              # Validation and cleaning
│   ├── database/          # SQLAlchemy models, connection, and repository
│   └── ml/                # Categorization, anomaly detection, and forecasting
├── frontend/              # React/Vite client
├── data/raw/              # Demo input data
├── scripts/               # Utility scripts
├── tests/                 # Pytest tests
├── requirements.txt
└── Dockerfile
```

## Quick start: Streamlit

From the project root:

```powershell
# Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt

# Optional: generate a fresh demo dataset
python scripts/generate_dataset.py

# Start the dashboard
streamlit run app.py
```

Open the URL printed by Streamlit, usually `http://localhost:8501`.

On Windows, if PowerShell script execution is restricted, activate the environment
with `.\venv\Scripts\activate.bat` from Command Prompt instead.

## Run the FastAPI and React application

The API initializes the SQLite database and seeds it from
`data/raw/synthetic_data.csv` when the database is empty.

### Start the API

```powershell
.\venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000
```

The API is available at `http://localhost:8000`. Interactive OpenAPI
documentation is available at `http://localhost:8000/docs`.

### Start the frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

The React client is available at `http://localhost:5173`.

The API provides dashboard data, transaction CRUD, analytics, budgets, insights,
CSV import, and CSV export. The Streamlit application remains available
independently.

## Docker

To run the Streamlit application in Docker:

```powershell
docker compose up --build
```

Then open `http://localhost:8501`. The Compose configuration mounts `data/` so
the SQLite database and imported data can persist between container runs.

## Configuration

Copy `.env.example` to `.env` when environment-specific settings are needed:

```text
DATABASE_URL=sqlite:///data/processed/finsight.db
LOG_LEVEL=INFO
```

The default database is SQLite at `data/processed/finsight.db`. That generated
database is ignored by Git; the demo CSV in `data/raw/` is the source data used
for initialization.

## CSV data

Uploaded transaction files must include these required columns:

```text
date, description, amount, type
```

Supported optional columns include `transaction_id`, `category`, `payment_method`,
`merchant`, and `notes`. The cleaner normalizes dates and currency-formatted
amounts, removes invalid rows and duplicates, and supplies defaults for optional
fields.

## Tests

Run the Python test suite from the project root:

```powershell
.\venv\Scripts\python.exe -m pytest
```

## Disclaimer

FinSight is an educational and analytical tool, not a source of professional
financial advice. Forecasts depend on historical data, and anomaly detection
identifies unusual patterns but does not prove fraud.
