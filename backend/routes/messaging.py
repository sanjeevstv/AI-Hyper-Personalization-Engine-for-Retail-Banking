"""GenAI messaging API routes."""

from flask import Blueprint, jsonify, request
from services.genai_messaging import generate_message

messaging_bp = Blueprint("messaging", __name__)


@messaging_bp.route("/customers/<customer_id>/generate-message", methods=["POST"])
def gen_message(customer_id):
    data = request.get_json(silent=True) or {}
    message_type = data.get("message_type", "email")
    valid_types = ["email", "push_notification", "rm_talking_points", "chatbot"]
    if message_type not in valid_types:
        return jsonify({"error": f"Invalid message_type. Must be one of {valid_types}"}), 400

    result = generate_message(customer_id, message_type)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)
