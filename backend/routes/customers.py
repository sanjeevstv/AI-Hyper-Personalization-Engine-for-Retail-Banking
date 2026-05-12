"""Customer API routes: search, profile, life events, segment."""

import io
import csv

from datetime import datetime

from flask import Blueprint, jsonify, request, Response
from extensions import db
from models.models import Customer, CustomerProfile, LifeEvent, SegmentAssignment, Transaction
from services.profiler import compute_profile, compute_all_profiles
from services.life_events import detect_life_events, detect_all_life_events, detect_life_events_ai
from services.segmentation import run_segmentation, get_segment_overview

customers_bp = Blueprint("customers", __name__)


@customers_bp.route("/", methods=["GET"])
def list_customers():
    query = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    q = Customer.query
    if query:
        q = q.filter(
            Customer.customer_id.ilike(f"%{query}%")
            | Customer.occupation.ilike(f"%{query}%")
            | Customer.city.ilike(f"%{query}%")
        )

    total = q.count()
    customers = q.offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        "customers": [c.to_dict() for c in customers],
        "total": total,
        "page": page,
        "per_page": per_page,
    })


@customers_bp.route("/<customer_id>", methods=["GET"])
def get_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    profile = CustomerProfile.query.get(customer_id)
    segment = SegmentAssignment.query.get(customer_id)
    life_events = LifeEvent.query.filter_by(customer_id=customer_id).all()

    return jsonify({
        "customer": customer.to_dict(),
        "profile": profile.to_dict() if profile else None,
        "segment": segment.to_dict() if segment else None,
        "life_events": [e.to_dict() for e in life_events],
    })


@customers_bp.route("/<customer_id>/profile", methods=["GET"])
def get_profile(customer_id):
    profile = CustomerProfile.query.get(customer_id)
    if profile:
        return jsonify(profile.to_dict())
    return jsonify({"error": "Profile not found. Run POST /api/customers/compute-profiles first."}), 404


@customers_bp.route("/compute-profiles", methods=["POST"])
def compute_profiles():
    results = compute_all_profiles()
    return jsonify({"message": f"Computed {len(results)} profiles", "count": len(results)})


@customers_bp.route("/<customer_id>/life-events", methods=["GET"])
def get_life_events(customer_id):
    mode = request.args.get("mode", "").strip().lower()

    if mode == "ai":
        ai_result, error = detect_life_events_ai(customer_id)
        if ai_result:
            return jsonify(ai_result)
        events = LifeEvent.query.filter_by(customer_id=customer_id).all()
        return jsonify({
            "events": [e.to_dict() for e in events],
            "detection_type": "rule-based",
            "note": f"AI unavailable ({error}), showing rule-based fallback",
        })

    events = LifeEvent.query.filter_by(customer_id=customer_id).all()
    return jsonify({
        "events": [e.to_dict() for e in events],
        "detection_type": "rule-based",
    })


@customers_bp.route("/detect-life-events", methods=["POST"])
def run_life_event_detection():
    results = detect_all_life_events()
    total_events = sum(len(v) for v in results.values())
    return jsonify({
        "message": f"Detected {total_events} life events across {len(results)} customers",
        "customers_with_events": len(results),
        "total_events": total_events,
    })


@customers_bp.route("/<customer_id>/segment", methods=["GET"])
def get_segment(customer_id):
    seg = SegmentAssignment.query.get(customer_id)
    if seg:
        return jsonify(seg.to_dict())
    return jsonify({"error": "Segment not assigned. Run POST /api/customers/run-segmentation first."}), 404


@customers_bp.route("/run-segmentation", methods=["POST"])
def run_seg():
    results = run_segmentation()
    if isinstance(results, dict) and "error" in results:
        return jsonify(results), 400
    return jsonify({"message": f"Segmented {len(results)} customers", "count": len(results)})


@customers_bp.route("/segments/overview", methods=["GET"])
def segments_overview():
    overview = get_segment_overview()
    return jsonify(overview)


@customers_bp.route("/segments/by-city", methods=["GET"])
def segments_by_city():
    results = db.session.query(
        Customer.city, db.func.count(Customer.customer_id)
    ).group_by(Customer.city).order_by(db.func.count(Customer.customer_id).desc()).all()
    return jsonify([{"segment_name": city, "customer_count": count} for city, count in results])


@customers_bp.route("/segments/by-occupation", methods=["GET"])
def segments_by_occupation():
    results = db.session.query(
        Customer.occupation, db.func.count(Customer.customer_id)
    ).group_by(Customer.occupation).order_by(db.func.count(Customer.customer_id).desc()).all()
    return jsonify([{"segment_name": occ, "customer_count": count} for occ, count in results])


@customers_bp.route("/filter-options", methods=["GET"])
def filter_options():
    cities = [r[0] for r in db.session.query(Customer.city).distinct().order_by(Customer.city).all()]
    occupations = [r[0] for r in db.session.query(Customer.occupation).distinct().order_by(Customer.occupation).all()]
    segments = [r[0] for r in db.session.query(SegmentAssignment.segment_name).distinct().order_by(SegmentAssignment.segment_name).all()]
    return jsonify({"cities": cities, "occupations": occupations, "segments": segments})


def _build_filter_query(args):
    q = Customer.query
    segment = args.get("segment", "").strip()
    city = args.get("city", "").strip()
    occupation = args.get("occupation", "").strip()
    customer_id = args.get("customer_id", "").strip()
    date_from = args.get("date_from", "").strip()
    date_to = args.get("date_to", "").strip()
    age_min = args.get("age_min", type=int)
    age_max = args.get("age_max", type=int)

    if customer_id:
        q = q.filter(Customer.customer_id.ilike(f"%{customer_id}%"))
    if segment:
        matching_ids = [r[0] for r in
                        SegmentAssignment.query.with_entities(SegmentAssignment.customer_id)
                        .filter(SegmentAssignment.segment_name == segment).all()]
        q = q.filter(Customer.customer_id.in_(matching_ids))
    if city:
        q = q.filter(Customer.city == city)
    if occupation:
        q = q.filter(Customer.occupation == occupation)
    if age_min is not None:
        q = q.filter(Customer.age >= age_min)
    if age_max is not None:
        q = q.filter(Customer.age <= age_max)
    if date_from or date_to:
        txn_q = Transaction.query.with_entities(Transaction.customer_id).distinct()
        if date_from:
            txn_q = txn_q.filter(Transaction.transaction_date >= datetime.strptime(date_from, "%Y-%m-%d").date())
        if date_to:
            txn_q = txn_q.filter(Transaction.transaction_date <= datetime.strptime(date_to, "%Y-%m-%d").date())
        active_ids = [r[0] for r in txn_q.all()]
        q = q.filter(Customer.customer_id.in_(active_ids))

    return q


@customers_bp.route("/filter", methods=["GET"])
def filter_customers():
    q = _build_filter_query(request.args)
    customers = q.order_by(Customer.customer_id).all()

    results = []
    for c in customers:
        seg = SegmentAssignment.query.get(c.customer_id)
        results.append({
            **c.to_dict(),
            "segment_name": seg.segment_name if seg else None,
        })

    return jsonify({"customers": results, "total": len(results)})


@customers_bp.route("/export", methods=["GET"])
def export_customers():
    q = _build_filter_query(request.args)
    customers = q.order_by(Customer.customer_id).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["customer_id", "age", "occupation", "city", "annual_income", "marital_status", "segment"])

    for c in customers:
        seg = SegmentAssignment.query.get(c.customer_id)
        writer.writerow([
            c.customer_id, c.age, c.occupation, c.city,
            c.annual_income, c.marital_status,
            seg.segment_name if seg else "",
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=customers_export.csv"},
    )
