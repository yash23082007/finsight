from __future__ import annotations

import io
import os
import base64
import hashlib
import hmac
import json
import secrets
import time
import uuid
from datetime import date
from typing import Any, Generator, Optional

import pandas as pd
from fastapi import Depends, FastAPI, File, Header, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from src.analytics.insights import InsightEngine
from src.database.connection import SessionLocal, init_db
from src.database.models import Budget, Transaction, User
from src.database.repository import Repository
from src.database.store import Store
from src.data.cleaner import DataCleaner
from src.data.validator import DataValidator

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="FinSight API", version="1.0.0", description="REST API for personal financial analysis")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
store = Store()


class TransactionBase(BaseModel):
    date: date
    description: str = Field(min_length=1, max_length=200)
    amount: float = Field(ge=0)
    type: str = Field(pattern="^(Income|Expense)$")
    category: str = Field(default="Other", max_length=80)
    payment_method: str = Field(default="Other", max_length=80)
    merchant: str = Field(default="", max_length=120)
    notes: str = Field(default="", max_length=500)


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    date: Optional[date] = None
    description: Optional[str] = Field(default=None, min_length=1, max_length=200)
    amount: Optional[float] = Field(default=None, ge=0)
    type: Optional[str] = Field(default=None, pattern="^(Income|Expense)$")
    category: Optional[str] = Field(default=None, max_length=80)
    payment_method: Optional[str] = Field(default=None, max_length=80)
    merchant: Optional[str] = Field(default=None, max_length=120)
    notes: Optional[str] = Field(default=None, max_length=500)


class TransactionResponse(TransactionBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: Optional[int] = None


class BudgetCreate(BaseModel):
    category: str = Field(min_length=1, max_length=80)
    amount: float = Field(ge=0)
    month_year: str = Field(pattern=r"^\d{4}-\d{2}$")


class BudgetResponse(BudgetCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class AuthPayload(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=128)
    name: Optional[str] = Field(default=None, min_length=2, max_length=80)


class UserResponse(BaseModel):
    id: int
    email: str
    name: str


class AuthResponse(BaseModel):
    token: str
    user: UserResponse


def get_db() -> Generator[Session | None, None, None]:
    if store.using_mongo():
        yield None
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def password_hash(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 210_000)
    return f"{base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def password_matches(password: str, stored: str) -> bool:
    try:
        salt_text, digest_text = stored.split("$", 1)
        expected = password_hash(password, base64.urlsafe_b64decode(salt_text))
        return hmac.compare_digest(expected, stored)
    except (ValueError, TypeError):
        return False


def make_token(user: User | dict[str, Any]) -> str:
    user_id = user["id"] if isinstance(user, dict) else user.id
    payload = base64.urlsafe_b64encode(json.dumps({"id": user_id, "exp": int(time.time()) + 30 * 24 * 3600}).encode()).decode().rstrip("=")
    secret = os.getenv("AUTH_SECRET", "finsight-development-secret").encode()
    signature = hmac.new(secret, payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def current_user(authorization: Optional[str] = Header(default=None), db: Session | None = Depends(get_db)) -> User | dict[str, Any]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Sign in to continue")
    try:
        payload, signature = authorization.split(" ", 1)[1].split(".", 1)
        secret = os.getenv("AUTH_SECRET", "finsight-development-secret").encode()
        expected = hmac.new(secret, payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError
        claims = json.loads(base64.urlsafe_b64decode(payload + "==="))
        if int(claims["exp"]) <= int(time.time()):
            raise ValueError
        user_id = claims["id"]
        user = store.mongo.find_user_by_id(int(user_id)) if store.mongo else db.get(User, int(user_id))
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        user = None
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")
    return user


def transaction_dict(transaction: Transaction) -> dict[str, Any]:
    return {
        "id": transaction.id,
        "date": transaction.date.isoformat(),
        "description": transaction.description,
        "amount": transaction.amount,
        "type": transaction.type,
        "category": transaction.category,
        "payment_method": transaction.payment_method,
        "merchant": transaction.merchant,
        "notes": transaction.notes or "",
    }


def dataframe_for(db: Session | None, user: User | dict[str, Any]) -> pd.DataFrame:
    if store.mongo:
        return store.mongo.dataframe(user["id"])
    query = db.query(Transaction).filter(Transaction.user_id == user.id)
    return pd.read_sql(query.statement, db.bind)


def load_dataframe(db: Session | None, frame: pd.DataFrame, user: User | dict[str, Any]) -> dict[str, Any]:
    cleaned, report = DataCleaner.clean_data(frame)
    used_ids: set[str] = set()
    transactions = []
    for _, row in cleaned.iterrows():
        transaction_id = str(row.get("transaction_id", "")).strip()
        if not transaction_id or transaction_id in used_ids or transaction_id.lower() in {"nan", "none"}:
            transaction_id = str(uuid.uuid4())
        used_ids.add(transaction_id)
        document = dict(
            id=transaction_id,
            date=pd.to_datetime(row["date"]).date(),
            description=str(row.get("description", "Unknown")),
            amount=float(row["amount"]),
            type=str(row.get("type", "Expense")),
            category=str(row.get("category", "Other")),
            payment_method=str(row.get("payment_method", "Other")),
            merchant=str(row.get("merchant", "")),
            notes=str(row.get("notes", "")),
            user_id=user["id"] if isinstance(user, dict) else user.id,
        )
        transactions.append(document if store.mongo else Transaction(**document))
    if store.mongo:
        store.mongo.replace_transactions(user["id"], transactions)
        return {"imported": len(transactions), "report": report}
    repo = Repository(db)
    db.query(Transaction).filter(Transaction.user_id == user.id).delete()
    repo.bulk_add_transactions(transactions)
    return {"imported": len(transactions), "report": report}


def initialize_database() -> None:
    if not store.using_mongo():
        init_db()


@app.on_event("startup")
def startup() -> None:
    initialize_database()


@app.get("/api/health")
def health() -> dict[str, str]:
    try:
        store.ping()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {exc}") from exc
    return {"status": "ok", "service": "finsight-api"}


@app.post("/api/auth/signup", response_model=AuthResponse, status_code=201)
def signup(payload: AuthPayload, db: Session = Depends(get_db)) -> AuthResponse:
    email = payload.email.lower()
    if store.mongo:
        if store.mongo.find_user_by_email(email):
            raise HTTPException(status_code=409, detail="An account with this email already exists")
        user = store.mongo.create_user(email, payload.name or email.split("@")[0].title(), password_hash(payload.password))
        return AuthResponse(token=make_token(user), user=UserResponse(**{key: user[key] for key in ("id", "email", "name")}))
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    user = User(email=email, name=payload.name or email.split("@")[0].title(), password_hash=password_hash(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return AuthResponse(token=make_token(user), user=UserResponse.model_validate(user, from_attributes=True))


@app.post("/api/auth/login", response_model=AuthResponse)
def login(payload: AuthPayload, db: Session = Depends(get_db)) -> AuthResponse:
    if store.mongo:
        user = store.mongo.find_user_by_email(payload.email.lower())
        if not user or not password_matches(payload.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        return AuthResponse(token=make_token(user), user=UserResponse(**{key: user[key] for key in ("id", "email", "name")}))
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not password_matches(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return AuthResponse(token=make_token(user), user=UserResponse.model_validate(user, from_attributes=True))


@app.get("/api/auth/me", response_model=UserResponse)
def me(user: User = Depends(current_user)) -> UserResponse:
    if isinstance(user, dict):
        return UserResponse(**{key: user[key] for key in ("id", "email", "name")})
    return UserResponse.model_validate(user, from_attributes=True)


@app.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict[str, Any]:
    frame = dataframe_for(db, user)
    if frame.empty:
        return {"income": 0, "expenses": 0, "savings": 0, "savings_rate": 0, "monthly": [], "categories": [], "recent_transactions": []}
    frame["date"] = pd.to_datetime(frame["date"])
    income = float(frame.loc[frame["type"] == "Income", "amount"].sum())
    expenses = float(frame.loc[frame["type"] == "Expense", "amount"].sum())
    monthly = frame.assign(month=frame["date"].dt.to_period("M").astype(str)).groupby(["month", "type"])["amount"].sum().unstack(fill_value=0).reset_index()
    monthly_rows = [{"month": row["month"], "income": float(row.get("Income", 0)), "expenses": float(row.get("Expense", 0)), "savings": float(row.get("Income", 0) - row.get("Expense", 0))} for _, row in monthly.iterrows()]
    categories = frame[frame["type"] == "Expense"].groupby("category")["amount"].sum().sort_values(ascending=False).reset_index()
    recent = frame.sort_values("date", ascending=False).head(8).to_dict("records")
    for row in recent:
        row["date"] = pd.Timestamp(row["date"]).date().isoformat()
    return {"income": income, "expenses": expenses, "savings": income - expenses, "savings_rate": (income - expenses) / income * 100 if income else 0, "monthly": monthly_rows, "categories": [{"name": row["category"], "value": float(row["amount"])} for _, row in categories.iterrows()], "recent_transactions": recent}


@app.get("/api/transactions", response_model=list[TransactionResponse])
def transactions(db: Session = Depends(get_db), user: User = Depends(current_user), search: Optional[str] = Query(default=None), transaction_type: Optional[str] = Query(default=None, alias="type"), category: Optional[str] = None) -> list[Transaction]:
    if store.mongo:
        return store.mongo.list_transactions(user["id"], search, transaction_type, category)
    query = db.query(Transaction).filter(Transaction.user_id == user.id).order_by(Transaction.date.desc())
    if transaction_type:
        query = query.filter(Transaction.type == transaction_type)
    if category:
        query = query.filter(Transaction.category == category)
    if search:
        needle = f"%{search}%"
        query = query.filter((Transaction.description.ilike(needle)) | (Transaction.merchant.ilike(needle)))
    return query.all()


@app.post("/api/transactions", response_model=TransactionResponse, status_code=201)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> Transaction:
    if store.mongo:
        return store.mongo.save_transaction({"id": str(uuid.uuid4()), "user_id": user["id"], **payload.model_dump(), "date": payload.date.isoformat()})
    transaction = Transaction(id=str(uuid.uuid4()), user_id=user.id, **payload.model_dump())
    return Repository(db).add_transaction(transaction)


@app.put("/api/transactions/{transaction_id}", response_model=TransactionResponse)
def update_transaction(transaction_id: str, payload: TransactionUpdate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> Transaction:
    if store.mongo:
        transaction = store.mongo.get_transaction(transaction_id, user["id"])
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        transaction.update(payload.model_dump(exclude_unset=True))
        if isinstance(transaction.get("date"), date):
            transaction["date"] = transaction["date"].isoformat()
        return store.mongo.save_transaction(transaction)
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == user.id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(transaction, field, value)
    db.commit()
    db.refresh(transaction)
    return transaction


@app.delete("/api/transactions/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)) -> None:
    if store.mongo:
        if not store.mongo.delete_transaction(transaction_id, user["id"]):
            raise HTTPException(status_code=404, detail="Transaction not found")
        return
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == user.id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(transaction)
    db.commit()


@app.get("/api/analytics/expenses")
def expense_analytics(db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict[str, Any]:
    frame = dataframe_for(db, user)
    expenses = frame[frame["type"] == "Expense"] if not frame.empty else frame
    return {"total": float(expenses["amount"].sum()) if not expenses.empty else 0, "by_category": [{"category": category, "amount": float(amount)} for category, amount in expenses.groupby("category")["amount"].sum().sort_values(ascending=False).items()]}


@app.get("/api/analytics/income")
def income_analytics(db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict[str, Any]:
    frame = dataframe_for(db, user)
    income = frame[frame["type"] == "Income"] if not frame.empty else frame
    return {"total": float(income["amount"].sum()) if not income.empty else 0, "by_category": [{"category": category, "amount": float(amount)} for category, amount in income.groupby("category")["amount"].sum().items()]}


@app.get("/api/analytics/savings")
def savings_analytics(db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict[str, Any]:
    summary = dashboard(db, user)
    return {"savings": summary["savings"], "savings_rate": summary["savings_rate"], "monthly": summary["monthly"]}


@app.get("/api/analytics/monthly")
def monthly_analytics(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[dict[str, Any]]:
    return dashboard(db, user)["monthly"]


@app.get("/api/analytics/statistics")
def statistics(db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict[str, Any]:
    frame = dataframe_for(db, user)
    expenses = frame.loc[frame["type"] == "Expense", "amount"] if not frame.empty else pd.Series(dtype=float)
    return {"average_expense": float(expenses.mean()) if not expenses.empty else 0, "median_expense": float(expenses.median()) if not expenses.empty else 0, "largest_expense": float(expenses.max()) if not expenses.empty else 0, "transaction_count": int(len(frame))}


@app.get("/api/budgets", response_model=list[BudgetResponse])
def budgets(db: Session = Depends(get_db), user: User = Depends(current_user), month_year: Optional[str] = None) -> list[Budget]:
    if store.mongo:
        return store.mongo.list_budgets(user["id"], month_year)
    query = db.query(Budget).filter(Budget.user_id == user.id).order_by(Budget.month_year.desc(), Budget.category.asc())
    return query.filter(Budget.month_year == month_year).all() if month_year else query.all()


@app.post("/api/budgets", response_model=BudgetResponse, status_code=201)
def create_or_update_budget(payload: BudgetCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> Budget:
    if store.mongo:
        return store.mongo.save_budget(user["id"], payload.category, payload.amount, payload.month_year)
    budget = db.query(Budget).filter_by(category=payload.category, month_year=payload.month_year, user_id=user.id).first()
    if budget:
        budget.amount = payload.amount
    else:
        budget = Budget(user_id=user.id, **payload.model_dump())
        db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


@app.put("/api/budgets/{budget_id}", response_model=BudgetResponse)
def update_budget(budget_id: int, payload: BudgetCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> Budget:
    if store.mongo:
        budget = store.mongo.update_budget(budget_id, user["id"], payload.model_dump())
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")
        return budget
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user.id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    for field, value in payload.model_dump().items():
        setattr(budget, field, value)
    db.commit()
    db.refresh(budget)
    return budget


@app.get("/api/insights")
def insights(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[dict[str, Any]]:
    return InsightEngine.generate_insights(dataframe_for(db, user))


@app.post("/api/import/csv")
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict[str, Any]:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file")
    try:
        frame = pd.read_csv(io.BytesIO(await file.read()))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read CSV: {exc}") from exc
    valid, report = DataValidator.validate_csv(frame)
    if not valid:
        raise HTTPException(status_code=422, detail=report)
    return load_dataframe(db, frame, user)


@app.get("/api/export/csv")
def export_csv(db: Session = Depends(get_db), user: User = Depends(current_user)) -> StreamingResponse:
    frame = dataframe_for(db, user)
    stream = io.StringIO()
    frame.to_csv(stream, index=False)
    stream.seek(0)
    return StreamingResponse(iter([stream.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=finsight-transactions.csv"})
