from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import pandas as pd
from .models import Transaction, Budget

class Repository:
    def __init__(self, db: Session):
        self.db = db

    def add_transaction(self, transaction: Transaction) -> Transaction:
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def bulk_add_transactions(self, transactions: List[Transaction]):
        self.db.bulk_save_objects(transactions)
        self.db.commit()

    def get_all_transactions_df(self) -> pd.DataFrame:
        query = self.db.query(Transaction)
        return pd.read_sql(query.statement, self.db.bind)
    
    def clear_all_transactions(self):
        self.db.query(Transaction).delete()
        self.db.commit()

    def get_budgets_df(self) -> pd.DataFrame:
        query = self.db.query(Budget)
        return pd.read_sql(query.statement, self.db.bind)
    
    def save_budget(self, budget: Budget):
        existing = self.db.query(Budget).filter_by(
            category=budget.category, month_year=budget.month_year
        ).first()
        if existing:
            existing.amount = budget.amount
        else:
            self.db.add(budget)
        self.db.commit()
