# FinSight

FinSight is a React and FastAPI personal finance analyzer. It turns transaction
data into interactive dashboards, spending analysis, machine-learning insights,
budgets, and financial health metrics.

The application is designed for educational and analytical use.

## Features

- Financial overview with income, expenses, savings, and recent activity.
- Transaction search and filtering.
- Expense categorization with TF-IDF and logistic regression.
- Anomaly detection with Isolation Forest.
- Expense forecasting with linear regression.
- Budget and monthly analysis.
- Deterministic insights generated from cleaned transaction data.
- CSV import and export.
- FastAPI OpenAPI documentation.

## Stack

- **Frontend:** React 18, Vite, React Router, Axios, Recharts, and Lucide React.
- **API:** FastAPI, Uvicorn, Pydantic, and SQLAlchemy.
- **Analytics:** Pandas, NumPy, SciPy, and scikit-learn.
- **Local database:** SQLite.

## Project structure

```text
finsight/
├── main.py                 # Vercel FastAPI service entry point
├── api/index.py            # Compatibility serverless entry point
├── backend/main.py        # FastAPI application
├── frontend/              # React/Vite client
├── src/
│   ├── analytics/         # Health score and insight generation
│   ├── data/              # Validation and cleaning
│   ├── database/          # SQLAlchemy models and repository
│   └── ml/                # Categorization, anomaly detection, forecasting
├── data/raw/              # Demo input data
├── scripts/               # Utility scripts
├── tests/                 # Pytest tests
├── requirements.txt       # Python dependencies
└── vercel.json            # Vercel build and routing configuration
```

## Local development

### Install Python dependencies

From the project root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Start the API

```powershell
.\venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000
```

The API runs at `http://localhost:8000`; interactive documentation is at
`http://localhost:8000/docs`.

### Start the frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173`. During local development, set
`VITE_API_URL=http://localhost:8000/api` in `frontend/.env.local` if the
frontend is not using the same-origin Vercel rewrite.

## Deploy to Vercel

This repository deploys as one Vercel project with two services defined in
`vercel.json`:

- `app` is the FastAPI service, using `api/index.py`, and is public at `/api/*`.
- `frontend` is the Vite service and is public at all other paths.

There are no service bindings because the browser calls the API through the
public same-origin `/api` rewrite; neither service makes a direct runtime call
to the other. Services that need private communication later should use a
Vercel service binding rather than a hardcoded hostname.

To deploy:

1. Import the GitHub repository into Vercel.
2. Keep the project root set to the repository root.
3. Deploy with the included `vercel.json`.
4. Add `DATABASE_URL` as a Vercel environment variable if persistent storage is
   required. The default SQLite database is suitable only for local development
   and disposable demos because serverless filesystems are not persistent. When
   `DATABASE_URL` is not set on Vercel, the API uses `/tmp/finsight.db`, which is
   writable but ephemeral.

The frontend uses same-origin `/api` requests by default. Client-side navigation
uses hash routes (`/#/transactions`, `/#/budget`, etc.) so every route works on
Vercel static hosting without requiring server-side SPA rewrites. Set
`VITE_API_URL` only when deploying the API separately.

For production persistence, use a hosted SQLAlchemy-compatible database and set
`DATABASE_URL` to its connection string. The demo data is loaded from
`data/raw/synthetic_data.csv` when the database has no transactions.

## CSV data

Imported files must include:

```text
date, description, amount, type
```

Optional columns are `transaction_id`, `category`, `payment_method`, `merchant`,
and `notes`. The cleaning pipeline normalizes dates and currency-formatted
amounts, removes invalid rows and duplicates, and supplies defaults for optional
fields.

## Tests

```powershell
.\venv\Scripts\python.exe -m pytest
```

## Disclaimer

FinSight is an educational financial analysis tool and does not provide
professional financial advice. Forecasts depend on historical data, and anomaly
detection identifies unusual patterns but does not prove fraud.
