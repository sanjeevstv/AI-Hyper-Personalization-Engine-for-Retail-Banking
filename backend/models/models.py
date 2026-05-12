from extensions import db
from datetime import datetime


class Customer(db.Model):
    __tablename__ = "customers"

    customer_id = db.Column(db.String(50), primary_key=True)
    age = db.Column(db.Integer)
    occupation = db.Column(db.String(100))
    city = db.Column(db.String(100))
    annual_income = db.Column(db.Float)
    marital_status = db.Column(db.String(20))

    transactions = db.relationship("Transaction", backref="customer", lazy=True)
    digital_behavior = db.relationship("DigitalBehavior", backref="customer", uselist=False, lazy=True)
    profile = db.relationship("CustomerProfile", backref="customer", uselist=False, lazy=True)
    life_events = db.relationship("LifeEvent", backref="customer", lazy=True)
    segment = db.relationship("SegmentAssignment", backref="customer", uselist=False, lazy=True)

    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "age": self.age,
            "occupation": self.occupation,
            "city": self.city,
            "annual_income": self.annual_income,
            "marital_status": self.marital_status,
        }


class Transaction(db.Model):
    __tablename__ = "transactions"

    transaction_id = db.Column(db.String(50), primary_key=True)
    customer_id = db.Column(db.String(50), db.ForeignKey("customers.customer_id"), nullable=False)
    transaction_type = db.Column(db.String(50))
    merchant_category = db.Column(db.String(100))
    amount = db.Column(db.Float)
    transaction_date = db.Column(db.Date)

    def to_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "customer_id": self.customer_id,
            "transaction_type": self.transaction_type,
            "merchant_category": self.merchant_category,
            "amount": self.amount,
            "transaction_date": self.transaction_date.isoformat() if self.transaction_date else None,
        }


class DigitalBehavior(db.Model):
    __tablename__ = "digital_behavior"

    customer_id = db.Column(db.String(50), db.ForeignKey("customers.customer_id"), primary_key=True)
    mobile_app_logins = db.Column(db.Integer, default=0)
    credit_card_clicks = db.Column(db.Integer, default=0)
    investment_page_visits = db.Column(db.Integer, default=0)
    chatbot_interactions = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "mobile_app_logins": self.mobile_app_logins,
            "credit_card_clicks": self.credit_card_clicks,
            "investment_page_visits": self.investment_page_visits,
            "chatbot_interactions": self.chatbot_interactions,
        }


class Product(db.Model):
    __tablename__ = "products"

    product_id = db.Column(db.String(50), primary_key=True)
    product_name = db.Column(db.String(200))
    product_type = db.Column(db.String(100))
    eligibility_income = db.Column(db.Float)
    benefits = db.Column(db.Text)

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "product_type": self.product_type,
            "eligibility_income": self.eligibility_income,
            "benefits": self.benefits,
        }


class CustomerProfile(db.Model):
    __tablename__ = "customer_profiles"

    customer_id = db.Column(db.String(50), db.ForeignKey("customers.customer_id"), primary_key=True)
    monthly_income = db.Column(db.Float, default=0)
    monthly_spending = db.Column(db.Float, default=0)
    savings_ratio = db.Column(db.Float, default=0)
    travel_frequency = db.Column(db.Integer, default=0)
    preferred_spending_category = db.Column(db.String(100))
    credit_behavior = db.Column(db.String(50))
    investment_interest = db.Column(db.Float, default=0)
    risk_appetite = db.Column(db.String(50))
    preferred_channel = db.Column(db.String(50))

    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "monthly_income": round(self.monthly_income, 2),
            "monthly_spending": round(self.monthly_spending, 2),
            "savings_ratio": round(self.savings_ratio, 2),
            "travel_frequency": self.travel_frequency,
            "preferred_spending_category": self.preferred_spending_category,
            "credit_behavior": self.credit_behavior,
            "investment_interest": round(self.investment_interest, 2),
            "risk_appetite": self.risk_appetite,
            "preferred_channel": self.preferred_channel,
        }


class LifeEvent(db.Model):
    __tablename__ = "life_events"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.String(50), db.ForeignKey("customers.customer_id"), nullable=False)
    event_type = db.Column(db.String(100))
    description = db.Column(db.Text)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "event_type": self.event_type,
            "description": self.description,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
        }


class SegmentAssignment(db.Model):
    __tablename__ = "segment_assignments"

    customer_id = db.Column(db.String(50), db.ForeignKey("customers.customer_id"), primary_key=True)
    segment_name = db.Column(db.String(100))
    cluster_id = db.Column(db.Integer)
    confidence = db.Column(db.Float, default=0)

    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "segment_name": self.segment_name,
            "cluster_id": self.cluster_id,
            "confidence": round(self.confidence, 2) if self.confidence else 0,
        }
