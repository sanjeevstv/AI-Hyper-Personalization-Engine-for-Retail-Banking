"""Recommendation engine API routes."""

from flask import Blueprint, jsonify, request, current_app
from services.recommendation import get_recommendations, get_ai_recommendations

recommendations_bp = Blueprint("recommendations", __name__)


@recommendations_bp.route("/customers/<customer_id>/recommendations", methods=["GET"])
def get_customer_recommendations(customer_id):
    mode = request.args.get("mode", "").strip().lower()
    api_key = current_app.config.get("OPENAI_API_KEY")

    if mode == "rule":
        result = get_recommendations(customer_id)
        if isinstance(result, dict) and "error" in result:
            return jsonify(result), 404
        return jsonify(result)

    if mode == "ai" or (not mode and api_key):
        ai_result, error = get_ai_recommendations(customer_id)
        if ai_result:
            return jsonify(ai_result)
        if mode == "ai":
            fallback = get_recommendations(customer_id)
            if isinstance(fallback, dict) and "error" in fallback:
                return jsonify(fallback), 404
            fallback["note"] = f"AI unavailable ({error}), showing rule-based fallback"
            return jsonify(fallback)

    result = get_recommendations(customer_id)
    if isinstance(result, dict) and "error" in result:
        return jsonify(result), 404
    return jsonify(result)
