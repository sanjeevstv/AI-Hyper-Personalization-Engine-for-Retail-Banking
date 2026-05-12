"""Generate synthetic banking datasets for the personalization engine."""

import csv
import os
import random
from datetime import datetime, timedelta

from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "seed_data")
NUM_CUSTOMERS = 100

OCCUPATIONS = [
    "Software Engineer", "Doctor", "Teacher", "Business Analyst",
    "Accountant", "Designer", "Marketing Manager", "Sales Executive",
    "Data Scientist", "Consultant", "Lawyer", "Entrepreneur",
]

CITIES = [
    "New York", "San Francisco", "Chicago", "Austin", "Boston",
    "Seattle", "Los Angeles", "Denver", "Miami", "Atlanta",
]

TRANSACTION_TYPES = [
    "Salary Credit", "Travel", "Grocery", "EMI", "Investment",
    "Shopping", "Utility Bill", "Dining", "Entertainment", "Rent",
]

MERCHANT_CATEGORIES = {
    "Salary Credit": ["Employer Direct Deposit"],
    "Travel": ["Airlines", "Hotels", "Travel Agency", "Car Rental", "International Travel"],
    "Grocery": ["Supermarket", "Organic Store", "Wholesale Club"],
    "EMI": ["Home Loan EMI", "Car Loan EMI", "Personal Loan EMI"],
    "Investment": ["Mutual Fund SIP", "Stock Brokerage", "Fixed Deposit", "SIP Investment"],
    "Shopping": ["Electronics", "Fashion", "Baby Store", "Home Decor", "Online Marketplace"],
    "Utility Bill": ["Electricity", "Water", "Internet", "Phone"],
    "Dining": ["Restaurant", "Cafe", "Food Delivery"],
    "Entertainment": ["Streaming Service", "Movie Theater", "Gaming"],
    "Rent": ["Apartment Rent", "Office Rent"],
}

PRODUCTS = [
    ("PROD_001", "Platinum Travel Credit Card", "Credit Card", 60000, "Airport lounge access, zero forex markup, 3x travel reward points, complimentary travel insurance"),
    ("PROD_002", "Cashback Rewards Card", "Credit Card", 30000, "5% cashback on online shopping, 2% on dining, no annual fee first year"),
    ("PROD_003", "Premium Savings Account", "Savings", 80000, "Higher interest rate, free unlimited transactions, dedicated relationship manager"),
    ("PROD_004", "Smart Investment Plan", "Investment", 50000, "Curated mutual fund portfolio, auto-rebalancing, tax-saving options"),
    ("PROD_005", "Pre-Approved Personal Loan", "Loan", 40000, "Low interest rate, instant approval, flexible tenure up to 5 years"),
    ("PROD_006", "Home Loan Advantage", "Loan", 70000, "Competitive rates, zero processing fee, balance transfer facility"),
    ("PROD_007", "Wealth Management Suite", "Wealth", 100000, "Dedicated wealth advisor, portfolio management, estate planning"),
    ("PROD_008", "Family Protection Plan", "Insurance", 35000, "Term life coverage, critical illness rider, family floater health insurance"),
    ("PROD_009", "Student Education Loan", "Loan", 25000, "Low interest, moratorium period, covers tuition and living expenses"),
    ("PROD_010", "Business Growth Account", "Business", 60000, "Higher transaction limits, free POS terminal, GST-ready invoicing"),
]


def generate_customers():
    rows = []
    for i in range(1, NUM_CUSTOMERS + 1):
        cid = f"CUST_{i:04d}"
        age = random.randint(22, 65)
        occupation = random.choice(OCCUPATIONS)
        city = random.choice(CITIES)
        income = round(random.uniform(25000, 200000), 2)
        marital = random.choice(["Single", "Married", "Divorced"])
        rows.append([cid, age, occupation, city, income, marital])

    path = os.path.join(OUTPUT_DIR, "customers.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["customer_id", "age", "occupation", "city", "annual_income", "marital_status"])
        w.writerows(rows)
    print(f"Generated {len(rows)} customers -> {path}")
    return [r[0] for r in rows]


def generate_transactions(customer_ids):
    rows = []
    tx_id = 1
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)

    for cid in customer_ids:
        num_txns = random.randint(15, 40)
        has_salary_growth = random.random() < 0.3
        base_salary = round(random.uniform(3000, 15000), 2)

        for month in range(1, 13):
            salary = base_salary
            if has_salary_growth and month >= 7:
                salary = round(base_salary * random.uniform(1.2, 1.5), 2)

            txn_date = start_date + timedelta(days=(month - 1) * 30 + random.randint(0, 5))
            rows.append([
                f"TXN_{tx_id:06d}", cid, "Salary Credit",
                "Employer Direct Deposit", salary, txn_date.strftime("%Y-%m-%d"),
            ])
            tx_id += 1

        for _ in range(num_txns):
            txn_type = random.choice(TRANSACTION_TYPES[1:])  # exclude Salary Credit
            merchant = random.choice(MERCHANT_CATEGORIES[txn_type])
            amount = round(random.uniform(10, 5000), 2)

            if txn_type == "Travel":
                amount = round(random.uniform(200, 8000), 2)
            elif txn_type == "Rent":
                amount = round(random.uniform(1000, 4000), 2)
            elif txn_type == "EMI":
                amount = round(random.uniform(500, 3000), 2)
            elif txn_type == "Investment":
                amount = round(random.uniform(500, 10000), 2)

            days_offset = random.randint(0, 364)
            txn_date = start_date + timedelta(days=days_offset)
            rows.append([
                f"TXN_{tx_id:06d}", cid, txn_type, merchant,
                amount, txn_date.strftime("%Y-%m-%d"),
            ])
            tx_id += 1

    path = os.path.join(OUTPUT_DIR, "transactions.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["transaction_id", "customer_id", "transaction_type", "merchant_category", "amount", "transaction_date"])
        w.writerows(rows)
    print(f"Generated {len(rows)} transactions -> {path}")


def generate_digital_behavior(customer_ids):
    rows = []
    for cid in customer_ids:
        rows.append([
            cid,
            random.randint(0, 60),
            random.randint(0, 30),
            random.randint(0, 20),
            random.randint(0, 15),
        ])

    path = os.path.join(OUTPUT_DIR, "digital_behavior.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["customer_id", "mobile_app_logins", "credit_card_clicks", "investment_page_visits", "chatbot_interactions"])
        w.writerows(rows)
    print(f"Generated {len(rows)} digital behavior records -> {path}")


def generate_products():
    path = os.path.join(OUTPUT_DIR, "products.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["product_id", "product_name", "product_type", "eligibility_income", "benefits"])
        w.writerows(PRODUCTS)
    print(f"Generated {len(PRODUCTS)} products -> {path}")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    cids = generate_customers()
    generate_transactions(cids)
    generate_digital_behavior(cids)
    generate_products()
    print("\nAll seed data generated successfully!")
