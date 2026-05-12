"""Product recommendation engine using profile, segment, and life-event signals."""

import json

from flask import current_app
from openai import OpenAI

from models.models import (
    Customer, CustomerProfile, LifeEvent, SegmentAssignment, Product,
)

PRODUCT_RULES = {
    "PROD_001": {
        "life_events": ["Frequent Traveler"],
        "segments": ["Travelers", "Premium Customers"],
        "min_income": 60000,
        "profile_boost": lambda p: p.travel_frequency > 3,
    },
    "PROD_002": {
        "life_events": ["High Spender"],
        "segments": ["Credit Seekers"],
        "min_income": 30000,
        "profile_boost": lambda p: p.preferred_spending_category in ["Electronics", "Fashion", "Online Marketplace"],
    },
    "PROD_003": {
        "life_events": [],
        "segments": ["Savers", "Premium Customers"],
        "min_income": 80000,
        "profile_boost": lambda p: p.savings_ratio > 0.3,
    },
    "PROD_004": {
        "life_events": ["Investment Oriented"],
        "segments": ["Investors"],
        "min_income": 50000,
        "profile_boost": lambda p: p.investment_interest > 0.3,
    },
    "PROD_005": {
        "life_events": ["Promotion"],
        "segments": ["Premium Customers", "Credit Seekers"],
        "min_income": 40000,
        "profile_boost": lambda p: p.credit_behavior in ["Excellent", "Good"],
    },
    "PROD_006": {
        "life_events": ["Potential Home Buyer"],
        "segments": ["Savers", "Premium Customers"],
        "min_income": 70000,
        "profile_boost": lambda p: p.credit_behavior in ["Excellent", "Good"],
    },
    "PROD_007": {
        "life_events": ["Investment Oriented"],
        "segments": ["Premium Customers", "Investors"],
        "min_income": 100000,
        "profile_boost": lambda p: p.monthly_income > 12000,
    },
    "PROD_008": {
        "life_events": ["New Parent"],
        "segments": ["Savers"],
        "min_income": 35000,
        "profile_boost": lambda _: False,
    },
    "PROD_009": {
        "life_events": [],
        "segments": ["Credit Seekers"],
        "min_income": 25000,
        "profile_boost": lambda _: False,
    },
    "PROD_010": {
        "life_events": [],
        "segments": ["Premium Customers"],
        "min_income": 60000,
        "profile_boost": lambda p: p.monthly_income > 8000,
    },
}


def get_recommendations(customer_id, top_n=3):
    """Return top-N product recommendations with reasoning for a customer."""
    customer = Customer.query.get(customer_id)
    if not customer:
        return {"error": "Customer not found"}

    profile = CustomerProfile.query.get(customer_id)
    if not profile:
        return {"error": "Profile not computed. Run profile builder first."}

    segment = SegmentAssignment.query.get(customer_id)
    life_events = LifeEvent.query.filter_by(customer_id=customer_id).all()
    event_types = {e.event_type for e in life_events}
    segment_name = segment.segment_name if segment else ""

    products = Product.query.all()
    scored = []

    for product in products:
        rules = PRODUCT_RULES.get(product.product_id, {})
        score = 0
        reasons = []

        if customer.annual_income >= product.eligibility_income:
            score += 1
            reasons.append(f"Meets income eligibility (${product.eligibility_income:,.0f})")

        matching_events = event_types & set(rules.get("life_events", []))
        if matching_events:
            score += 2
            reasons.append(f"Life events: {', '.join(matching_events)}")

        if segment_name in rules.get("segments", []):
            score += 1.5
            reasons.append(f"Segment match: {segment_name}")

        boost_fn = rules.get("profile_boost")
        if boost_fn and boost_fn(profile):
            score += 1
            reasons.append("Profile behavior match")

        if score > 0:
            scored.append({
                "product": product.to_dict(),
                "score": round(score, 2),
                "reasons": reasons,
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    results = scored[:top_n]
    return {"recommendations": results, "reasoning_type": "rule-based"}


def get_ai_recommendations(customer_id, top_n=3):
    """Use OpenAI to freely recommend products with AI-generated reasoning."""
    api_key = current_app.config.get("OPENAI_API_KEY")
    base_url = current_app.config.get("OPENAI_BASE_URL")
    model = current_app.config.get("OPENAI_MODEL", "gpt-3.5-turbo")

    customer = Customer.query.get(customer_id)
    if not customer:
        return None, "Customer not found"

    profile = CustomerProfile.query.get(customer_id)
    if not profile:
        return None, "Profile not computed"

    segment = SegmentAssignment.query.get(customer_id)
    life_events = LifeEvent.query.filter_by(customer_id=customer_id).all()
    products = Product.query.all()

    context = f"""Customer: {customer.customer_id}
Age: {customer.age}, Occupation: {customer.occupation}, City: {customer.city}
Annual Income: ${customer.annual_income:,.2f}, Marital Status: {customer.marital_status}

Financial Profile:
- Monthly Income: ${profile.monthly_income:,.2f}, Monthly Spending: ${profile.monthly_spending:,.2f}
- Savings Ratio: {profile.savings_ratio:.0%}, Travel Frequency: {profile.travel_frequency} trips
- Preferred Spending: {profile.preferred_spending_category}, Credit Behavior: {profile.credit_behavior}
- Investment Interest: {profile.investment_interest}, Risk Appetite: {profile.risk_appetite}
- Preferred Channel: {profile.preferred_channel}
"""
    if segment:
        context += f"\nCustomer Segment: {segment.segment_name}\n"
    if life_events:
        context += "\nLife Events:\n"
        for e in life_events:
            context += f"- {e.event_type}: {e.description}\n"

    context += "\nAvailable Banking Products:\n"
    for p in products:
        context += f"- {p.product_id}: {p.product_name} ({p.product_type}) — Min Income: ${p.eligibility_income:,.0f} — {p.benefits}\n"

    prompt = f"""{context}

Based on this customer's complete financial profile, life events, and segment, recommend the top {top_n} most relevant banking products from the list above.

For each product, provide a personalized explanation of WHY this specific product suits this customer.

You MUST respond ONLY with a JSON array (no markdown, no extra text) in this exact format:
[
  {{"product_id": "PROD_XXX", "reasoning": "Your personalized explanation here"}},
  ...
]"""

    try:
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        client = OpenAI(**client_kwargs)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a retail banking product recommendation AI. Respond only with valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=600,
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        ai_picks = json.loads(raw)
        product_map = {p.product_id: p for p in products}
        results = []
        for pick in ai_picks[:top_n]:
            pid = pick.get("product_id", "")
            product = product_map.get(pid)
            if product:
                results.append({
                    "product": product.to_dict(),
                    "score": 0,
                    "reasons": [pick.get("reasoning", "AI recommended")],
                })

        if results:
            return {"recommendations": results, "reasoning_type": "ai"}, None
        return None, "AI returned no valid products"

    except Exception as e:
        return None, str(e)
