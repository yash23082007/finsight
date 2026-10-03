from sqlalchemy import Column, Integer, String, Numeric, Date, Text, ForeignKey
from .connection import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True)
    date = Column(Date, index=True)
    description = Column(String, index=True)
    amount = Column(Numeric(12, 2))
    type = Column(String, index=True)
    category = Column(String, index=True)
    payment_method = Column(String)
    merchant = Column(String)
    notes = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    amount = Column(Numeric(12, 2))
    month_year = Column(String, index=True) # Format: YYYY-MM
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
