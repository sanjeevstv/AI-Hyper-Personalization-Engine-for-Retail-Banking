"""Data ingestion service: load CSV data into the database."""

import csv
import io
import os
from datetime import datetime

import pandas as pd
from extensions import db
from models.models import Customer, Transaction, DigitalBehavior, Product

SEED_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "seed_data")

REQUIRED_COLUMNS = {
    "customers": ["customer_id", "age", "occupation", "city", "annual_income", "marital_status"],
    "transactions": ["transaction_id", "customer_id", "transaction_type", "merchant_category", "amount", "transaction_date"],
    "digital_behavior": ["customer_id", "mobile_app_logins", "credit_card_clicks", "investment_page_visits", "chatbot_interactions"],
    "products": ["product_id", "product_name", "product_type", "eligibility_income", "benefits"],
}


def validate_csv(df, dataset_type):
    required = REQUIRED_COLUMNS.get(dataset_type, [])
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for {dataset_type}: {missing}")
    return True


def load_customers(df):
    validate_csv(df, "customers")
    count = 0
    for _, row in df.iterrows():
        existing = Customer.query.get(str(row["customer_id"]))
        if existing:
            existing.age = int(row["age"])
            existing.occupation = str(row["occupation"])
            existing.city = str(row["city"])
            existing.annual_income = float(row["annual_income"])
            existing.marital_status = str(row["marital_status"])
        else:
            db.session.add(Customer(
                customer_id=str(row["customer_id"]),
                age=int(row["age"]),
                occupation=str(row["occupation"]),
                city=str(row["city"]),
                annual_income=float(row["annual_income"]),
                marital_status=str(row["marital_status"]),
            ))
        count += 1
    db.session.commit()
    return count


def load_transactions(df):
    validate_csv(df, "transactions")
    count = 0
    for _, row in df.iterrows():
        existing = Transaction.query.get(str(row["transaction_id"]))
        if not existing:
            db.session.add(Transaction(
                transaction_id=str(row["transaction_id"]),
                customer_id=str(row["customer_id"]),
                transaction_type=str(row["transaction_type"]),
                merchant_category=str(row["merchant_category"]),
                amount=float(row["amount"]),
                transaction_date=datetime.strptime(str(row["transaction_date"]), "%Y-%m-%d").date(),
            ))
            count += 1
    db.session.commit()
    return count


def load_digital_behavior(df):
    validate_csv(df, "digital_behavior")
    count = 0
    for _, row in df.iterrows():
        cid = str(row["customer_id"])
        existing = DigitalBehavior.query.get(cid)
        if existing:
            existing.mobile_app_logins = int(row["mobile_app_logins"])
            existing.credit_card_clicks = int(row["credit_card_clicks"])
            existing.investment_page_visits = int(row["investment_page_visits"])
            existing.chatbot_interactions = int(row["chatbot_interactions"])
        else:
            db.session.add(DigitalBehavior(
                customer_id=cid,
                mobile_app_logins=int(row["mobile_app_logins"]),
                credit_card_clicks=int(row["credit_card_clicks"]),
                investment_page_visits=int(row["investment_page_visits"]),
                chatbot_interactions=int(row["chatbot_interactions"]),
            ))
        count += 1
    db.session.commit()
    return count


def load_products(df):
    validate_csv(df, "products")
    count = 0
    for _, row in df.iterrows():
        existing = Product.query.get(str(row["product_id"]))
        if existing:
            existing.product_name = str(row["product_name"])
            existing.product_type = str(row["product_type"])
            existing.eligibility_income = float(row["eligibility_income"])
            existing.benefits = str(row["benefits"])
        else:
            db.session.add(Product(
                product_id=str(row["product_id"]),
                product_name=str(row["product_name"]),
                product_type=str(row["product_type"]),
                eligibility_income=float(row["eligibility_income"]),
                benefits=str(row["benefits"]),
            ))
        count += 1
    db.session.commit()
    return count


LOADERS = {
    "customers": load_customers,
    "transactions": load_transactions,
    "digital_behavior": load_digital_behavior,
    "products": load_products,
}


def seed_all():
    """Load all CSV files from the seed_data directory. Clears existing data first for a clean seed."""
    from models.models import (
        CustomerProfile, LifeEvent, SegmentAssignment,
        Transaction, DigitalBehavior, Product, Customer,
    )
    for model in [CustomerProfile, LifeEvent, SegmentAssignment, Transaction, DigitalBehavior, Product, Customer]:
        model.query.delete()
    db.session.commit()

    results = {}
    file_map = {
        "customers": "customers.csv",
        "transactions": "transactions.csv",
        "digital_behavior": "digital_behavior.csv",
        "products": "products.csv",
    }
    for dataset_type, filename in file_map.items():
        path = os.path.join(SEED_DIR, filename)
        if os.path.exists(path):
            df = pd.read_csv(path)
            loader = LOADERS[dataset_type]
            count = loader(df)
            results[dataset_type] = count
        else:
            results[dataset_type] = f"File not found: {filename}"
    return results


def upload_csv(file_content, dataset_type):
    """Load a single uploaded CSV into the database."""
    if dataset_type not in LOADERS:
        raise ValueError(f"Unknown dataset type: {dataset_type}. Must be one of {list(LOADERS.keys())}")
    df = pd.read_csv(io.StringIO(file_content))
    loader = LOADERS[dataset_type]
    count = loader(df)
    return count
