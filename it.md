# Python for Data Science in FinSight

This project uses Python as the main data-science engine behind its financial analytics. The analysis pipeline is implemented in the backend and is focused on cleaning, validating, understanding, and predicting transaction behavior.

## 1. Data ingestion and validation

The first step is to load CSV or app-generated transaction data into a Pandas DataFrame.

- `src/data/validator.py` checks whether required columns are present.
- `src/data/cleaner.py` normalizes dates, amount values, and category strings.
- Currency strings such as `$100`, `₹1,250.50`, and `€42` are converted into numeric values.
- Invalid rows are removed; missing optional metadata is filled with defaults.

This is a classic Python data-science workflow: cleaning raw input before any analytics or modeling.

## 2. Data transformation and exploration

Once the data is cleaned, Python is used to reshape the data for analysis.

Examples from the app include:

- grouping by date to build monthly summaries
- aggregating by category to calculate spending totals
- sorting transactions by recency for recent-activity views
- computing savings rate, expense totals, and income totals

The backend uses `pandas` heavily for DataFrame filtering, grouping, resampling, and conversion to JSON-friendly summaries for the frontend.

## 3. Machine learning and predictive analytics

The project includes a small ML stack built with `scikit-learn`:

### Expense categorization

`src/ml/categorization.py`

- Uses `TfidfVectorizer` to convert item descriptions into numeric features.
- Trains a `LogisticRegression` classifier with balanced class weights.
- Uses merchant-aware grouping during validation to avoid data leakage.
- Returns predictions such as `Food`, `Transport`, or `Needs review`.

This is a practical text-classification workflow commonly used in Python data science.

### Anomaly detection

`src/ml/anomaly_detection.py`

- Uses `IsolationForest` on expense features.
- Computes log-transformed amounts and category-relative robust z-scores.
- Identifies unusual spending patterns compared to a user's own category behavior.

This helps flag suspicious or outlier transactions without pretending to be a fraud detector.

### Expense forecasting

`src/ml/forecasting.py`

- Aggregates expenses by month.
- Builds a simple time index for monthly forecasting.
- Fits a `LinearRegression` model to historical expense behavior.
- Produces future predictions and descriptive error metrics.

This is a standard time-series forecasting baseline used in data-science projects.

## 4. Insight generation and financial scoring

Python is also used to turn cleaned data into business-friendly conclusions.

- `src/analytics/health_score.py` calculates a savings and expense-based health score.
- `src/analytics/insights.py` derives clear finance insights, such as biggest category spend and savings-rate trends.

These modules use structured rules and summary metrics rather than opaque black-box outputs, which makes the analysis explainable and easier to trust.

## 5. Data persistence and backend integration

The data-science work is not isolated from the application; it feeds the API and UI:

- `SQLAlchemy` connects the app to SQLite or PostgreSQL.
- DataFrames are transformed into API responses and charts.
- The Python backend uses the same cleaned data to power dashboards, imports, and exports.

In short, the app treats Python as both a data-cleaning and decision-support layer.

## Why Python is the right fit here

FinSight is a personal finance application with real analytical value, and Python is useful because it provides:

- fast data manipulation with `pandas`
- numerical computing with `numpy` and `scipy`
- mature ML tooling with `scikit-learn`
- easy integration with FastAPI for web services
- robust support for CSV and tabular workflows

This combination makes Python ideal for finance-oriented analytics in a small but realistic application.
