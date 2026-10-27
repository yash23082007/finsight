# FinSight

FinSight is a personal finance analyzer with a React frontend and a Python analytics backend. It turns transaction data into dashboards, spending insights, and money-health scoring using clear, rule-based analysis.

The project is designed for educational analysis and lightweight personal finance tracking.

## What the project does

- Tracks income and expense transactions.
- Calculates dashboard totals, monthly trends, and category breakdowns.
- Cleans CSV imports and validates required transaction columns.
- Analyzes recorded categories and monthly spending without predictive models.
- Produces deterministic financial-health insights and scores.
- Supports SQLite for local development and optional PostgreSQL/MongoDB when configured.

## Tech stack

- Frontend: React 18, Vite, React Router, Axios, Recharts
- API: FastAPI, Pydantic, SQLAlchemy, Uvicorn
- Analytics: Pandas with rule-based summaries
- Database: SQLite locally; PostgreSQL/Neon or MongoDB when configured

## Project structure

```text
finsight/
├── README.md               # Project overview and setup
├── it.md                  # Python data-science usage overview
├── main.py                # Vercel serverless FastAPI entry point
├── api/index.py           # Compatibility entry for serverless routes
├── backend/main.py        # Main FastAPI application
├── frontend/              # React + Vite dashboard app
├── src/
│   ├── analytics/         # Health score and insight generation
│   ├── data/              # CSV validation and cleaning
│   ├── database/          # SQLAlchemy models, repository, database setup
│   └── utils/             # Logging and formatting helpers
├── data/
│   ├── raw/               # Demo data source files
│   └── processed/         # SQLite output cache and generated DBs
├── scripts/               # Utility scripts
├── tests/                 # Pytest verification suite
├── requirements.txt      # Runtime dependencies
├── requirements-dev.txt   # Dev and test dependencies
├── pytest.ini            # Pytest configuration
├── vercel.json           # Vercel deployment config
└── .env.example          # Environment variable template
```

## Quick start

### 1) Create a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

macOS/Linux:

```bash
python3 -m venv venv
. venv/bin/activate
pip install -r requirements-dev.txt
```

### 2) Start the API

```powershell
.\venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000
```

The API runs at `http://localhost:8000` and the documentation is available at `http://localhost:8000/docs`.

### 3) Start the frontend

```powershell
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173`.

### 4) Run tests

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

## Environment variables

Create a local `.env` file from the included template if needed:

- `DATABASE_URL` for a PostgreSQL or SQLite override
- `AUTH_SECRET` for signed auth tokens (minimum 32 characters)
- `MONGODB_URI` and `MONGODB_DATABASE` for optional MongoDB mode

Never commit real secrets or production connection strings.

## CSV import rules

Imported files should include:

```text
date,description,amount,type
```

Optional columns include `transaction_id`, `category`, `payment_method`, `merchant`, and `notes`.

The cleaning pipeline:

- normalizes dates and currency strings
- removes invalid rows
- fills missing optional fields with defaults
- preserves repeated transactions while generating fresh IDs for blanks or duplicates

## Data processing and analytics

The backend uses Python to clean transaction data and produce financial summaries:

- `pandas` cleans and aggregates transaction data
- `SQLAlchemy` stores cleaned results in SQLite/PostgreSQL for app queries

The main data and analytics modules are:

- `src/data/cleaner.py` for import normalization and cleanup
- `src/data/validator.py` for schema validation
- `src/analytics/health_score.py` for heuristic scoring
- `src/analytics/insights.py` for deterministic summaries

## Deployment notes

The project supports a Vercel deployment with a FastAPI app and a separate frontend static build:

- `app` handles `/api/*` routes
- `frontend` serves the UI on other routes
- same-origin `/api` calls are preferred for local and hosted deployments

### Render API with the Vercel frontend

To host the API on Render while keeping the React frontend on Vercel, create a Render Web Service from the repository root:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- Root directory: leave blank
- Health check path: `/healthz`

Set these Render environment variables:

- `AUTH_SECRET`: generate a random secret with at least 32 characters.
- `MONGODB_URI`: the MongoDB Atlas connection string, with a URL-encoded database password.
- `MONGODB_DATABASE`: `finsight`
- `CORS_ORIGINS`: the exact Vercel origin, for example `https://finsight-kohl-kappa.vercel.app`
- `COOKIE_SAMESITE`: `none`
- `COOKIE_SECURE`: `true`

When using MongoDB, leave `DATABASE_URL` unset. The Vercel rewrite in `vercel.json` proxies `/api/*` requests to the Render service, keeping browser requests on the Vercel origin. Leave `VITE_API_URL` unset (or set it to `/api`) and redeploy the frontend. The Render API serves only the backend; Vercel continues to serve the React app.

For a SQL deployment instead, set `DATABASE_URL` to a persistent PostgreSQL connection string. Local SQLite storage is suitable for development, not persistent hosting.

## Disclaimer

FinSight is an educational financial tool. It does not replace professional financial advice, tax advice, or credit scoring. Scores and insights are informational summaries, not financial recommendations.
