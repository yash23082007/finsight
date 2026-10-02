from sqlalchemy import Column, Integer, String, Float, Date, Text
from .connection import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True)
    date = Column(Date, index=True)
    description = Column(String, index=True)
    amount = Column(Float)
    type = Column(String, index=True)
    category = Column(String, index=True)
    payment_method = Column(String)
    merchant = Column(String)
    notes = Column(Text, nullable=True)

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    amount = Column(Float)
    month_year = Column(String, index=True) # Format: YYYY-MM
