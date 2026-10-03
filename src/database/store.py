from __future__ import annotations

import os
import uuid
from datetime import date
from typing import Any

import pandas as pd

from .connection import SessionLocal, init_db
from .models import Budget, Transaction, User


class MongoStore:
    def __init__(self, uri: str, database_name: str):
        from pymongo import MongoClient

        self.client = MongoClient(uri, appname="finsight", connect=False)
        self.database = self.client[database_name]
        self.users = self.database.users
        self.transactions = self.database.transactions
        self.budgets = self.database.budgets
        self._indexes_ready = False

    def ping(self) -> None:
        self.client.admin.command("ping")
        if not self._indexes_ready:
            self.users.create_index("email", unique=True)
            self.transactions.create_index([("user_id", 1), ("date", -1)])
            self.budgets.create_index([("user_id", 1), ("month_year", -1), ("category", 1)], unique=True)
            self._indexes_ready = True

    def _next_id(self, name: str) -> int:
        from pymongo import ReturnDocument

        result = self.database.counters.find_one_and_update(
            {"_id": name},
            {"$inc": {"value": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return int(result["value"])

    def find_user_by_email(self, email: str) -> dict[str, Any] | None:
        return self.users.find_one({"email": email})

    def find_user_by_id(self, user_id: int) -> dict[str, Any] | None:
        return self.users.find_one({"id": user_id})

    def create_user(self, email: str, name: str, password_hash: str) -> dict[str, Any]:
        document = {"id": self._next_id("users"), "email": email, "name": name, "password_hash": password_hash}
        self.users.insert_one(document)
        return document

    def list_transactions(self, user_id: int, search: str | None = None, transaction_type: str | None = None, category: str | None = None) -> list[dict[str, Any]]:
        query: dict[str, Any] = {"user_id": user_id}
        if transaction_type:
            query["type"] = transaction_type
        if category:
            query["category"] = category
        if search:
            query["$or"] = [
                {"description": {"$regex": search, "$options": "i"}},
                {"merchant": {"$regex": search, "$options": "i"}},
            ]
        return list(self.transactions.find(query, {"_id": 0}).sort("date", -1))

    def get_transaction(self, transaction_id: str, user_id: int) -> dict[str, Any] | None:
        return self.transactions.find_one({"id": transaction_id, "user_id": user_id}, {"_id": 0})

    def save_transaction(self, document: dict[str, Any]) -> dict[str, Any]:
        self.transactions.replace_one({"id": document["id"], "user_id": document["user_id"]}, document, upsert=True)
        return document

    def delete_transaction(self, transaction_id: str, user_id: int) -> bool:
        return self.transactions.delete_one({"id": transaction_id, "user_id": user_id}).deleted_count == 1

    def dataframe(self, user_id: int) -> pd.DataFrame:
        rows = list(self.transactions.find({"user_id": user_id}, {"_id": 0, "user_id": 0}))
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows)

    def replace_transactions(self, user_id: int, documents: list[dict[str, Any]]) -> None:
        self.transactions.delete_many({"user_id": user_id})
        if documents:
            self.transactions.insert_many(documents)

    def list_budgets(self, user_id: int, month_year: str | None = None) -> list[dict[str, Any]]:
        query: dict[str, Any] = {"user_id": user_id}
        if month_year:
            query["month_year"] = month_year
        return list(self.budgets.find(query, {"_id": 0}).sort([("month_year", -1), ("category", 1)]))

    def save_budget(self, user_id: int, category: str, amount: float, month_year: str) -> dict[str, Any]:
        existing = self.budgets.find_one({"user_id": user_id, "category": category, "month_year": month_year})
        document = existing or {"id": self._next_id("budgets"), "user_id": user_id, "category": category, "month_year": month_year}
        document["amount"] = amount
        self.budgets.replace_one({"id": document["id"]}, document, upsert=True)
        return {key: value for key, value in document.items() if key != "_id"}

    def update_budget(self, budget_id: int, user_id: int, values: dict[str, Any]) -> dict[str, Any] | None:
        budget = self.budgets.find_one({"id": budget_id, "user_id": user_id})
        if not budget:
            return None
        budget.update(values)
        self.budgets.replace_one({"id": budget_id, "user_id": user_id}, budget)
        return {key: value for key, value in budget.items() if key != "_id"}


class Store:
    def __init__(self) -> None:
        uri = os.getenv("MONGODB_URI")
        database_name = os.getenv("MONGODB_DATABASE", "finsight")
        self.mongo = MongoStore(uri, database_name) if uri else None
        if not self.mongo:
            init_db()

    def ping(self) -> None:
        if self.mongo:
            self.mongo.ping()

    def using_mongo(self) -> bool:
        return self.mongo is not None

    def session(self):
        return SessionLocal()
