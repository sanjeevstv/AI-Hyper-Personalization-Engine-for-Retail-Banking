"""GenAI personalized messaging using OpenAI API."""

from openai import OpenAI
from flask import current_app
from models.models import (
    Customer, CustomerProfile, LifeEvent, SegmentAssignment,
)
from services.recommendation import get_recommendations


def _build_customer_context(customer_id):
    """Gather all customer data into a context string for the prompt."""
    customer = Customer.query.get(customer_id)
    if not customer:
        return None, "Customer not found"

    profile = CustomerProfile.query.get(customer_id)
    segment = SegmentAssignment.query.get(customer_id)
    life_events = LifeEvent.query.filter_by(customer_id=customer_id).all()
    recommendations = get_recommendations(customer_id, top_n=3)

    context = f"""Customer Information:
- Name: Customer {customer.customer_id}
- Age: {customer.age}
- Occupation: {customer.occupation}
- City: {customer.city}
- Annual Income: ${customer.annual_income:,.2f}
- Marital Status: {customer.marital_status}
"""

    if profile:
        context += f"""
Financial Profile:
- Monthly Income: ${profile.monthly_income:,.2f}
- Monthly Spending: ${profile.monthly_spending:,.2f}
- Savings Ratio: {profile.savings_ratio:.0%}
- Travel Frequency: {profile.travel_frequency} transactions
- Preferred Spending: {profile.preferred_spending_category}
- Credit Behavior: {profile.credit_behavior}
- Investment Interest: {profile.investment_interest}
- Risk Appetite: {profile.risk_appetite}
- Preferred Channel: {profile.preferred_channel}
"""

    if segment:
        context += f"\nCustomer Segment: {segment.segment_name}\n"

    if life_events:
        context += "\nDetected Life Events:\n"
        for e in life_events:
            context += f"- {e.event_type}: {e.description}\n"

    if isinstance(recommendations, list) and recommendations:
        context += "\nRecommended Products:\n"
        for r in recommendations:
            p = r["product"]
            context += f"- {p['product_name']}: {p['benefits']}\n"

    return context, None


def generate_message(customer_id, message_type="email"):
    """Generate a personalized message for a customer using OpenAI."""
    api_key = current_app.config.get("OPENAI_API_KEY")
    base_url = current_app.config.get("OPENAI_BASE_URL")
    model = current_app.config.get("OPENAI_MODEL", "gpt-3.5-turbo")

    if not api_key:
        return _fallback_message(customer_id, message_type)

    context, error = _build_customer_context(customer_id)
    if error:
        return {"error": error}

    type_instructions = {
        "email": "Write a professional, personalized marketing email (subject line + body) from the bank to this customer, recommending the most relevant products. Keep it warm, concise, and action-oriented.",
        "push_notification": "Write a short, compelling push notification (max 2 sentences) for the customer's mobile banking app highlighting a personalized offer.",
        "rm_talking_points": "Generate 5 bullet-point talking points for a Relationship Manager meeting with this customer. Include conversation starters, product recommendations, and how to address their financial needs.",
        "chatbot": "Generate a friendly chatbot response that proactively suggests relevant banking products to this customer based on their profile. Keep it conversational and helpful.",
    }

    instruction = type_instructions.get(message_type, type_instructions["email"])

    prompt = f"""{context}

Task: {instruction}

Important: Personalize the message based on the customer's financial behavior, life events, and recommended products. Make it feel genuine and relevant, not generic."""

    try:
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        client = OpenAI(**client_kwargs)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a retail banking personalization assistant that creates highly personalized customer communications."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=500,
        )
        content = response.choices[0].message.content
        return {
            "customer_id": customer_id,
            "message_type": message_type,
            "generated_message": content,
            "model_used": model,
        }
    except Exception as e:
        return _fallback_message(customer_id, message_type, str(e))


def _fallback_message(customer_id, message_type, error_detail=None):
    """Generate a template-based fallback when OpenAI is unavailable."""
    context, err = _build_customer_context(customer_id)
    if err:
        return {"error": err}

    customer = Customer.query.get(customer_id)
    profile = CustomerProfile.query.get(customer_id)
    recommendations = get_recommendations(customer_id, top_n=3)

    product_name = "our banking products"
    if isinstance(recommendations, list) and recommendations:
        product_name = recommendations[0]["product"]["product_name"]

    if message_type == "push_notification":
        msg = f"Hi! Based on your recent activity, check out {product_name} — tailored just for you. Tap to learn more!"
    elif message_type == "rm_talking_points":
        points = [
            f"Customer is a {customer.occupation} based in {customer.city}",
            f"Annual income: ${customer.annual_income:,.0f}",
        ]
        if profile:
            points.append(f"Savings ratio: {profile.savings_ratio:.0%}")
            points.append(f"Risk appetite: {profile.risk_appetite}")
        points.append(f"Top recommendation: {product_name}")
        msg = "\n".join(f"• {p}" for p in points)
    elif message_type == "chatbot":
        msg = f"Hello! I noticed you might be interested in {product_name}. Would you like me to share more details about how it fits your financial goals?"
    else:
        msg = (
            f"Dear Customer {customer_id},\n\n"
            f"Based on your financial activity, we'd like to introduce {product_name}. "
            f"This product has been selected specifically for customers like you.\n\n"
            f"Visit your nearest branch or contact your relationship manager to learn more.\n\n"
            f"Best regards,\nYour Banking Team"
        )

    result = {
        "customer_id": customer_id,
        "message_type": message_type,
        "generated_message": msg,
        "model_used": "fallback-template",
    }
    if error_detail:
        result["note"] = f"OpenAI unavailable ({error_detail}), using template fallback"
    else:
        result["note"] = "No OPENAI_API_KEY configured, using template fallback"
    return result
