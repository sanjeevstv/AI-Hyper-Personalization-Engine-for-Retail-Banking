"""Rule-based and AI-powered life event detection from transaction patterns."""

import json
from datetime import datetime

import pandas as pd
from flask import current_app
from openai import OpenAI

from extensions import db
from models.models import Customer, Transaction, LifeEvent


RULES = []


def rule(event_type):
    """Decorator to register a life-event detection rule."""
    def decorator(fn):
        RULES.append((event_type, fn))
        return fn
    return decorator


@rule("Promotion")
def detect_promotion(df):
    salary = df[df["transaction_type"] == "Salary Credit"].copy()
    if salary.empty:
        return None
    salary = salary.sort_values("transaction_date")
    salary["month"] = pd.to_datetime(salary["transaction_date"]).dt.to_period("M")
    monthly = salary.groupby("month")["amount"].mean().reset_index()
    monthly.columns = ["month", "avg_salary"]
    if len(monthly) < 2:
        return None
    first_half = monthly.head(len(monthly) // 2)["avg_salary"].mean()
    second_half = monthly.tail(len(monthly) // 2)["avg_salary"].mean()
    if first_half > 0 and (second_half - first_half) / first_half > 0.20:
        pct = round(((second_half - first_half) / first_half) * 100, 1)
        return f"Salary increased by {pct}% — likely promotion or raise"
    return None


@rule("Frequent Traveler")
def detect_frequent_traveler(df):
    travel = df[df["transaction_type"] == "Travel"]
    if len(travel) >= 5:
        intl = travel[travel["merchant_category"].isin(["International Travel", "Airlines", "Hotels"])]
        return f"Detected {len(travel)} travel transactions ({len(intl)} international)"
    return None


@rule("New Parent")
def detect_new_parent(df):
    baby = df[df["merchant_category"].str.contains("Baby", case=False, na=False)]
    if len(baby) >= 2:
        total = round(baby["amount"].sum(), 2)
        return f"Detected {len(baby)} baby-related purchases totaling ${total}"
    return None


@rule("Potential Home Buyer")
def detect_home_buyer(df):
    rent = df[df["transaction_type"] == "Rent"]
    if not rent.empty:
        avg_rent = rent["amount"].mean()
        if avg_rent > 2000:
            return f"High average rent of ${round(avg_rent, 2)} — potential home buyer"
    return None


@rule("Investment Oriented")
def detect_investor(df):
    inv = df[df["transaction_type"] == "Investment"]
    sip = df[df["merchant_category"].str.contains("SIP|Mutual Fund", case=False, na=False)]
    if len(inv) >= 4 or len(sip) >= 3:
        return f"Regular investment activity: {len(inv)} investment transactions, {len(sip)} SIP payments"
    return None


@rule("High Spender")
def detect_high_spender(df):
    shopping = df[df["transaction_type"] == "Shopping"]
    if not shopping.empty and shopping["amount"].sum() > 10000:
        total = round(shopping["amount"].sum(), 2)
        return f"High shopping spend totaling ${total}"
    return None


@rule("Credit Disciplined")
def detect_credit_discipline(df):
    emi = df[df["transaction_type"] == "EMI"]
    if len(emi) >= 8:
        return f"Highly disciplined EMI repayment: {len(emi)} regular payments detected"
    return None


def detect_life_events(customer_id):
    """Run all rules against a customer's transaction history."""
    transactions = Transaction.query.filter_by(customer_id=customer_id).all()
    if not transactions:
        return []

    df = pd.DataFrame([t.to_dict() for t in transactions])

    LifeEvent.query.filter_by(customer_id=customer_id).delete()

    detected = []
    for event_type, rule_fn in RULES:
        result = rule_fn(df)
        if result:
            event = LifeEvent(
                customer_id=customer_id,
                event_type=event_type,
                description=result,
                detected_at=datetime.utcnow(),
            )
            db.session.add(event)
            detected.append({"event_type": event_type, "description": result})

    db.session.commit()
    return detected


def detect_all_life_events():
    """Run life event detection for all customers."""
    customers = Customer.query.all()
    results = {}
    for c in customers:
        events = detect_life_events(c.customer_id)
        if events:
            results[c.customer_id] = events
    return results


def detect_life_events_ai(customer_id):
    """Use OpenAI to detect life events from transaction patterns."""
    api_key = current_app.config.get("OPENAI_API_KEY")
    base_url = current_app.config.get("OPENAI_BASE_URL")
    model = current_app.config.get("OPENAI_MODEL", "gpt-3.5-turbo")

    if not api_key:
        return None, "No OPENAI_API_KEY configured"

    customer = Customer.query.get(customer_id)
    if not customer:
        return None, "Customer not found"

    transactions = Transaction.query.filter_by(customer_id=customer_id).all()
    if not transactions:
        return None, "No transactions found"

    df = pd.DataFrame([t.to_dict() for t in transactions])

    txn_summary = f"""Customer: {customer.customer_id}
Age: {customer.age}, Occupation: {customer.occupation}, City: {customer.city}
Annual Income: ${customer.annual_income:,.2f}, Marital Status: {customer.marital_status}

Transaction Summary ({len(df)} transactions):
"""
    for txn_type, group in df.groupby("transaction_type"):
        total = group["amount"].sum()
        count = len(group)
        categories = ", ".join(group["merchant_category"].unique()[:5])
        txn_summary += f"- {txn_type}: {count} transactions, total ${total:,.2f} ({categories})\n"

    date_range = f"{df['transaction_date'].min()} to {df['transaction_date'].max()}"
    txn_summary += f"\nDate range: {date_range}\n"

    prompt = f"""{txn_summary}

Analyze this customer's transaction patterns and identify significant life events or lifestyle changes.

Look for patterns like: career changes, salary growth, new family members, relocation, lifestyle shifts, health changes, retirement planning, education spending, debt patterns, investment behavior changes, travel lifestyle, etc.

You MUST respond ONLY with a JSON array (no markdown, no extra text) in this exact format:
[
  {{"event_type": "Short Event Name", "description": "Detailed explanation of what was detected and why it matters"}},
  ...
]

Return between 2-6 events. Be specific and reference actual transaction patterns from the data."""

    try:
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        client = OpenAI(**client_kwargs)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a banking analytics AI that detects customer life events from transaction data. Respond only with valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=600,
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        events = json.loads(raw)
        results = [
            {"event_type": e.get("event_type", "Unknown"), "description": e.get("description", "")}
            for e in events if isinstance(e, dict)
        ]
        return {"events": results, "detection_type": "ai"}, None

    except Exception as e:
        return None, str(e)
