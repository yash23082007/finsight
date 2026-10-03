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
- **Database:** SQLite locally, or PostgreSQL/Neon in production. MongoDB is
  supported only when `MONGODB_URI` is explicitly configured.

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
pip install -r requirements-dev.txt
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

On macOS/Linux, use:

```bash
python3 -m venv venv
. venv/bin/activate
pip install -r requirements-dev.txt
python -m uvicorn backend.main:app --reload --port 8000
```

## Deploy to Vercel

This repository deploys as one Vercel project with two services defined in
`vercel.json`:

- `app` is the FastAPI service, using `main.py`, and is public at `/api/*`.
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
`DATABASE_URL` to its connection string. New accounts start with no
transactions; users can add records individually or import their own CSV.
For Neon, use the pooled connection string and add `AUTH_SECRET` as a separate
Vercel environment variable containing a long random value.

The API rejects authentication when `AUTH_SECRET` is absent or shorter than
32 characters. Never commit `.env` files or real connection
strings; `.env.example` contains placeholders only. CSV uploads are limited to
4 MB and 100,000 rows. Exported text fields are escaped against spreadsheet
formula injection. Browser sessions use an HttpOnly cookie; the token is not
stored in localStorage.

## CSV data

Imported files must include:

```text
date, description, amount, type
```

Optional columns are `transaction_id`, `category`, `payment_method`, `merchant`,
and `notes`. The cleaning pipeline normalizes dates and currency-formatted
amounts, removes invalid rows and supplies defaults for optional fields. Import
reports include the number of rows read, invalid rows, and final rows.
Identical repeated transactions are preserved; supplied duplicate transaction
IDs are replaced with generated IDs.

The checked-in `data/raw/synthetic_data.csv` is synthetic demo data, not bank
data. Amounts are stored as fixed-precision decimals in SQL databases.

## Analytics methodology and limitations

- Categorization uses a TF-IDF/logistic-regression pipeline with balanced
  classes. Evaluation uses merchant-grouped holdout data to avoid reporting
  inflated scores from the same merchant appearing in both sets. Predictions
  below the confidence threshold are returned as **Needs review**.
- Anomaly detection uses deterministic Isolation Forest features based on
  `log1p(amount)` and category-relative robust z-scores. It requires at least
  ten expense rows and reports an explainable typical-spend multiple. It is a
  review aid, not a fraud detector.
- Forecasts aggregate completed months only, clamp negative predictions to zero,
  and report descriptive regression metrics alongside naive and three-month
  average baselines. At least six completed months are required.
- The health score is a heuristic weighted across savings rate, expense control,
  and monthly consistency over the latest three months. It is not a validated
  financial or credit score.

## Tests

```powershell
.\venv\Scripts\python.exe -m pytest
```

## Disclaimer

FinSight is an educational financial analysis tool and does not provide
professional financial advice. Forecasts depend on historical data, and anomaly
detection identifies unusual patterns but does not prove fraud.
