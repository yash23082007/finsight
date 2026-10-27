# Python analytics in FinSight

FinSight uses Python and Pandas for transparent, rule-based financial summaries. It does not train or run machine-learning models.

## Data ingestion

- `src/data/validator.py` checks that CSV files include the required transaction columns.
- `src/data/cleaner.py` normalizes dates, currency amounts, text fields, and transaction IDs.
- Invalid rows are discarded during import, and optional metadata receives safe defaults.

## Summaries and insights

The backend groups transactions by month, category, and type to calculate income, expenses, savings, and recent activity. `src/analytics/health_score.py` calculates an educational score from savings rate, expense control, and consistency. `src/analytics/insights.py` generates descriptive summaries from recorded transactions.

SQLAlchemy persists transactions in SQLite or PostgreSQL. Pandas converts the stored data into API responses used by the React dashboard.
