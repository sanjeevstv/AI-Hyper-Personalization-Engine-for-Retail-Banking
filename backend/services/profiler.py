"""Customer profile builder: compute financial profiles from transaction data."""

from collections import Counter

import pandas as pd
from extensions import db
from models.models import Customer, Transaction, DigitalBehavior, CustomerProfile


def compute_profile(customer_id):
    """Build a unified financial profile for a single customer."""
    customer = Customer.query.get(customer_id)
    if not customer:
        return None

    transactions = Transaction.query.filter_by(customer_id=customer_id).all()
    if not transactions:
        return _empty_profile(customer_id)

    df = pd.DataFrame([t.to_dict() for t in transactions])
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])

    salary_txns = df[df["transaction_type"] == "Salary Credit"]
    monthly_income = salary_txns["amount"].mean() if not salary_txns.empty else 0

    spending_txns = df[df["transaction_type"] != "Salary Credit"]
    months_span = max(
        (df["transaction_date"].max() - df["transaction_date"].min()).days / 30, 1
    )
    monthly_spending = spending_txns["amount"].sum() / months_span if not spending_txns.empty else 0

    savings_ratio = 0
    if monthly_income > 0:
        savings_ratio = max((monthly_income - monthly_spending) / monthly_income, 0)

    travel_txns = df[df["transaction_type"] == "Travel"]
    travel_frequency = len(travel_txns)

    if not spending_txns.empty:
        cat_counts = Counter(spending_txns["merchant_category"])
        preferred_category = cat_counts.most_common(1)[0][0]
    else:
        preferred_category = "N/A"

    emi_txns = df[df["transaction_type"] == "EMI"]
    if len(emi_txns) >= 6:
        credit_behavior = "Excellent"
    elif len(emi_txns) >= 3:
        credit_behavior = "Good"
    elif len(emi_txns) >= 1:
        credit_behavior = "Fair"
    else:
        credit_behavior = "No EMI History"

    investment_txns = df[df["transaction_type"] == "Investment"]
    investment_interest = len(investment_txns) / months_span

    if monthly_income > 10000:
        risk_appetite = "High"
    elif monthly_income > 5000:
        risk_appetite = "Moderate"
    else:
        risk_appetite = "Low"

    digital = DigitalBehavior.query.get(customer_id)
    if digital and digital.mobile_app_logins > 20:
        preferred_channel = "Mobile App"
    elif digital and digital.chatbot_interactions > 5:
        preferred_channel = "Chatbot"
    else:
        preferred_channel = "Branch"

    profile_data = {
        "customer_id": customer_id,
        "monthly_income": round(monthly_income, 2),
        "monthly_spending": round(monthly_spending, 2),
        "savings_ratio": round(savings_ratio, 4),
        "travel_frequency": travel_frequency,
        "preferred_spending_category": preferred_category,
        "credit_behavior": credit_behavior,
        "investment_interest": round(investment_interest, 2),
        "risk_appetite": risk_appetite,
        "preferred_channel": preferred_channel,
    }

    existing = CustomerProfile.query.get(customer_id)
    if existing:
        for key, val in profile_data.items():
            setattr(existing, key, val)
    else:
        db.session.add(CustomerProfile(**profile_data))
    db.session.commit()

    return profile_data


def compute_all_profiles():
    """Build profiles for every customer in the database."""
    customers = Customer.query.all()
    results = []
    for c in customers:
        profile = compute_profile(c.customer_id)
        if profile:
            results.append(profile)
    return results


def _empty_profile(customer_id):
    data = {
        "customer_id": customer_id,
        "monthly_income": 0,
        "monthly_spending": 0,
        "savings_ratio": 0,
        "travel_frequency": 0,
        "preferred_spending_category": "N/A",
        "credit_behavior": "No EMI History",
        "investment_interest": 0,
        "risk_appetite": "Low",
        "preferred_channel": "Branch",
    }
    existing = CustomerProfile.query.get(customer_id)
    if existing:
        for key, val in data.items():
            setattr(existing, key, val)
    else:
        db.session.add(CustomerProfile(**data))
    db.session.commit()
    return data
