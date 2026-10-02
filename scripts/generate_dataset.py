import os
import random
import uuid
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict

# Set random seed for reproducibility
random.seed(42)

def generate_transactions(num_transactions: int = 5000, months: int = 24) -> pd.DataFrame:
    """Generates a synthetic financial dataset."""
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)
    
    categories_expense = {
        "Food": {"min": 100, "max": 2000, "freq": 0.3},
        "Travel": {"min": 50, "max": 1000, "freq": 0.15},
        "Shopping": {"min": 500, "max": 10000, "freq": 0.1},
        "Bills": {"min": 500, "max": 5000, "freq": 0.1},
        "Entertainment": {"min": 200, "max": 3000, "freq": 0.1},
        "Healthcare": {"min": 200, "max": 5000, "freq": 0.05},
        "Other": {"min": 50, "max": 1000, "freq": 0.2}
    }
    
    merchants = {
        "Food": ["Swiggy", "Zomato", "Local Cafe", "Domino's", "Starbucks"],
        "Travel": ["Uber", "Ola", "IRCTC", "Metro", "Flight"],
        "Shopping": ["Amazon", "Flipkart", "Myntra", "Local Store", "Reliance Mart"],
        "Bills": ["Electricity", "Jio", "Airtel", "Water", "Gas"],
        "Entertainment": ["Netflix", "PVR", "Spotify", "Gaming", "Event"],
        "Healthcare": ["Apollo", "PharmEasy", "Local Clinic", "Dentist"],
        "Other": ["Misc", "Donation", "Gift"]
    }
    
    payment_methods = ["UPI", "Credit Card", "Debit Card", "Cash"]
    
    data = []
    
    # Add regular income (salary) - monthly
    current_date = start_date
    while current_date <= end_date:
        data.append({
            "transaction_id": str(uuid.uuid4()),
            "date": current_date.replace(day=1).strftime("%Y-%m-%d"),
            "description": "Monthly Salary",
            "amount": round(random.uniform(50000, 70000), 2),
            "type": "Income",
            "category": "Salary",
            "payment_method": "Bank Transfer",
            "merchant": "Employer",
            "notes": "Regular Income"
        })
        current_date += timedelta(days=32)
        current_date = current_date.replace(day=1)
        
    # Generate random expenses
    expense_cats = list(categories_expense.keys())
    expense_weights = [categories_expense[c]["freq"] for c in expense_cats]
    
    for _ in range(num_transactions - len(data)):
        cat = random.choices(expense_cats, weights=expense_weights)[0]
        amt = round(random.uniform(categories_expense[cat]["min"], categories_expense[cat]["max"]), 2)
        
        # Introduce occasional anomalies (1% chance)
        if random.random() < 0.01:
            amt = amt * random.uniform(3, 8)
            
        t_date = start_date + timedelta(days=random.randint(0, months * 30))
        
        data.append({
            "transaction_id": str(uuid.uuid4()),
            "date": t_date.strftime("%Y-%m-%d"),
            "description": f"{random.choice(merchants[cat])} Payment",
            "amount": round(amt, 2),
            "type": "Expense",
            "category": cat,
            "payment_method": random.choice(payment_methods),
            "merchant": random.choice(merchants[cat]),
            "notes": ""
        })
        
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date').reset_index(drop=True)
    df['date'] = df['date'].dt.strftime("%Y-%m-%d")
    
    return df

if __name__ == "__main__":
    os.makedirs("data/raw", exist_ok=True)
    print("Generating synthetic dataset...")
    df = generate_transactions(5000, 24)
    df.to_csv("data/raw/synthetic_data.csv", index=False)
    print(f"Dataset generated at data/raw/synthetic_data.csv with {len(df)} rows.")
