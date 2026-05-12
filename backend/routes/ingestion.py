"""Data ingestion API routes: seed data and CSV upload."""

from flask import Blueprint, jsonify, request
from services.ingestion import seed_all, upload_csv

ingestion_bp = Blueprint("ingestion", __name__)


@ingestion_bp.route("/seed", methods=["POST"])
def seed_data():
    try:
        results = seed_all()
        return jsonify({"message": "Seed data loaded", "results": results})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


@ingestion_bp.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    dataset_type = request.form.get("dataset_type")

    if not dataset_type:
        return jsonify({"error": "dataset_type is required (customers, transactions, digital_behavior, products)"}), 400

    try:
        content = file.read().decode("utf-8")
        count = upload_csv(content, dataset_type)
        return jsonify({"message": f"Loaded {count} records into {dataset_type}", "count": count})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
