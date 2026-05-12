"""End-to-end integration test for the banking personalization engine."""

import json
import sys


def run_tests():
    from app import create_app
    from extensions import db

    app = create_app()
    client = app.test_client()

    passed = 0
    failed = 0

    def check(name, condition, detail=""):
        nonlocal passed, failed
        if condition:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name} — {detail}")
            failed += 1

    with app.app_context():
        db.drop_all()
        db.create_all()

    print("\n=== 1. Data Ingestion ===")
    resp = client.post("/api/ingest/seed")
    data = resp.get_json()
    check("Seed endpoint returns 200", resp.status_code == 200, f"got {resp.status_code}")
    check("Customers loaded", data.get("results", {}).get("customers", 0) == 100,
          f"got {data.get('results', {}).get('customers')}")
    check("Transactions loaded", data.get("results", {}).get("transactions", 0) > 2000,
          f"got {data.get('results', {}).get('transactions')}")
    check("Products loaded", data.get("results", {}).get("products", 0) == 10,
          f"got {data.get('results', {}).get('products')}")
    check("Digital behavior loaded", data.get("results", {}).get("digital_behavior", 0) == 100,
          f"got {data.get('results', {}).get('digital_behavior')}")

    print("\n=== 2. Customer Search ===")
    resp = client.get("/api/customers/?q=CUST_0001")
    data = resp.get_json()
    check("Search returns 200", resp.status_code == 200)
    check("Found customer CUST_0001",
          any(c["customer_id"] == "CUST_0001" for c in data.get("customers", [])),
          f"customers: {[c['customer_id'] for c in data.get('customers', [])]}")

    resp = client.get("/api/customers/?q=New+York")
    data = resp.get_json()
    check("City search returns results", data.get("total", 0) > 0, f"total={data.get('total')}")

    print("\n=== 3. Profile Computation ===")
    resp = client.post("/api/customers/compute-profiles")
    data = resp.get_json()
    check("Compute profiles returns 200", resp.status_code == 200)
    check("100 profiles computed", data.get("count") == 100, f"got {data.get('count')}")

    resp = client.get("/api/customers/CUST_0001/profile")
    data = resp.get_json()
    check("Profile endpoint returns 200", resp.status_code == 200)
    check("Profile has monthly_income", "monthly_income" in data and data["monthly_income"] > 0,
          f"monthly_income={data.get('monthly_income')}")
    check("Profile has savings_ratio", "savings_ratio" in data, f"keys={list(data.keys())}")
    check("Profile has travel_frequency", "travel_frequency" in data)
    check("Profile has preferred_spending_category", "preferred_spending_category" in data)

    print("\n=== 4. Life Event Detection ===")
    resp = client.post("/api/customers/detect-life-events")
    data = resp.get_json()
    check("Life events returns 200", resp.status_code == 200)
    check("Events detected for some customers", data.get("customers_with_events", 0) > 0,
          f"got {data.get('customers_with_events')}")
    check("Total events > 0", data.get("total_events", 0) > 0,
          f"got {data.get('total_events')}")

    resp = client.get("/api/customers/CUST_0001/life-events")
    check("Life events per-customer returns 200", resp.status_code == 200)

    print("\n=== 5. Segmentation ===")
    resp = client.post("/api/customers/run-segmentation")
    data = resp.get_json()
    check("Segmentation returns 200", resp.status_code == 200)
    check("100 customers segmented", data.get("count") == 100, f"got {data.get('count')}")

    resp = client.get("/api/customers/CUST_0001/segment")
    data = resp.get_json()
    check("Segment per-customer returns 200", resp.status_code == 200)
    check("Segment has name", "segment_name" in data and data["segment_name"],
          f"got {data}")

    resp = client.get("/api/customers/segments/overview")
    data = resp.get_json()
    check("Segment overview returns 200", resp.status_code == 200)
    check("5 segments in overview", len(data) == 5, f"got {len(data)} segments")
    total_customers = sum(s["customer_count"] for s in data)
    check("All 100 customers accounted for", total_customers == 100,
          f"total={total_customers}")

    print("\n=== 6. Recommendations ===")
    resp = client.get("/api/customers/CUST_0001/recommendations")
    data = resp.get_json()
    check("Recommendations returns 200", resp.status_code == 200)
    check("Has reasoning_type", "reasoning_type" in data, f"keys={list(data.keys())}")
    check("reasoning_type is rule-based (no API key)", data.get("reasoning_type") == "rule-based",
          f"got {data.get('reasoning_type')}")
    recs = data.get("recommendations", [])
    check("Returns list of recommendations", isinstance(recs, list) and len(recs) > 0,
          f"count={len(recs)}")
    if recs:
        rec = recs[0]
        check("Recommendation has product info", "product" in rec)
        check("Recommendation has reasons", "reasons" in rec and len(rec["reasons"]) > 0,
              f"reasons={rec.get('reasons')}")
        check("Recommendation has score", "score" in rec and rec["score"] > 0)

    print("\n=== 7. GenAI Messaging (Fallback) ===")
    resp = client.post("/api/customers/CUST_0001/generate-message",
                       json={"message_type": "email"})
    data = resp.get_json()
    check("Email generation returns 200", resp.status_code == 200)
    check("Message generated", "generated_message" in data and len(data["generated_message"]) > 10,
          f"msg length={len(data.get('generated_message', ''))}")

    resp = client.post("/api/customers/CUST_0001/generate-message",
                       json={"message_type": "push_notification"})
    data = resp.get_json()
    check("Push notification generated", "generated_message" in data)

    resp = client.post("/api/customers/CUST_0001/generate-message",
                       json={"message_type": "rm_talking_points"})
    data = resp.get_json()
    check("RM talking points generated", "generated_message" in data)

    resp = client.post("/api/customers/CUST_0001/generate-message",
                       json={"message_type": "chatbot"})
    data = resp.get_json()
    check("Chatbot message generated", "generated_message" in data)

    print("\n=== 8. Full Customer View ===")
    resp = client.get("/api/customers/CUST_0010")
    data = resp.get_json()
    check("Full customer view returns 200", resp.status_code == 200)
    check("Has customer data", data.get("customer") is not None)
    check("Has profile data", data.get("profile") is not None)
    check("Has segment data", data.get("segment") is not None)

    print("\n=== 9. Segment by City/Occupation ===")
    resp = client.get("/api/customers/segments/by-city")
    data = resp.get_json()
    check("By-city returns 200", resp.status_code == 200)
    check("Multiple cities returned", len(data) > 3, f"got {len(data)}")
    city_total = sum(s["customer_count"] for s in data)
    check("City totals = 100", city_total == 100, f"total={city_total}")

    resp = client.get("/api/customers/segments/by-occupation")
    data = resp.get_json()
    check("By-occupation returns 200", resp.status_code == 200)
    check("Multiple occupations returned", len(data) > 3, f"got {len(data)}")

    print("\n=== 10. Filter & Export ===")
    resp = client.get("/api/customers/filter-options")
    data = resp.get_json()
    check("Filter options returns 200", resp.status_code == 200)
    check("Has cities", len(data.get("cities", [])) > 0)
    check("Has occupations", len(data.get("occupations", [])) > 0)
    check("Has segments", len(data.get("segments", [])) > 0)

    resp = client.get("/api/customers/filter?city=New+York")
    data = resp.get_json()
    check("Filter by city returns 200", resp.status_code == 200)
    check("Filter returns customers", data.get("total", 0) > 0, f"total={data.get('total')}")
    if data.get("customers"):
        check("All filtered in New York",
              all(c["city"] == "New York" for c in data["customers"]))

    resp = client.get("/api/customers/export?city=New+York")
    check("CSV export returns 200", resp.status_code == 200)
    check("CSV content type", "text/csv" in resp.content_type, f"got {resp.content_type}")
    csv_text = resp.data.decode("utf-8")
    check("CSV has header row", "customer_id" in csv_text.split("\n")[0])

    print(f"\n{'='*50}")
    print(f"RESULTS: {passed} passed, {failed} failed, {passed + failed} total")
    print(f"{'='*50}\n")

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
