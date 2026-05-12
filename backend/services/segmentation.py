"""K-Means customer segmentation based on financial profiles."""

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from extensions import db
from models.models import Customer, CustomerProfile, SegmentAssignment

SEGMENT_LABELS = {
    0: "Premium Customers",
    1: "Travelers",
    2: "Savers",
    3: "Investors",
    4: "Credit Seekers",
}

FEATURE_COLUMNS = [
    "monthly_income",
    "monthly_spending",
    "savings_ratio",
    "travel_frequency",
    "investment_interest",
]


def run_segmentation(n_clusters=5):
    """Run K-Means clustering on all customer profiles."""
    profiles = CustomerProfile.query.all()
    if len(profiles) < n_clusters:
        return {"error": f"Need at least {n_clusters} profiles, found {len(profiles)}"}

    customer_ids = [p.customer_id for p in profiles]
    features = np.array([
        [p.monthly_income, p.monthly_spending, p.savings_ratio,
         p.travel_frequency, p.investment_interest]
        for p in profiles
    ])

    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(features_scaled)
    labels = kmeans.labels_

    centers = scaler.inverse_transform(kmeans.cluster_centers_)
    label_map = _assign_segment_names(centers)

    distances = kmeans.transform(features_scaled)
    max_dist = distances.max() if distances.max() > 0 else 1

    SegmentAssignment.query.delete()

    results = []
    for i, cid in enumerate(customer_ids):
        cluster_id = int(labels[i])
        dist_to_center = distances[i][cluster_id]
        confidence = round(1 - (dist_to_center / max_dist), 2)

        seg = SegmentAssignment(
            customer_id=cid,
            segment_name=label_map.get(cluster_id, f"Segment {cluster_id}"),
            cluster_id=cluster_id,
            confidence=confidence,
        )
        db.session.add(seg)
        results.append(seg.to_dict())

    db.session.commit()
    return results


def _assign_segment_names(centers):
    """Map cluster centers to meaningful segment names based on dominant features."""
    label_map = {}
    n_clusters = len(centers)
    used_labels = set()

    feature_label_mapping = [
        (0, "Premium Customers"),      # highest income
        (3, "Travelers"),              # highest travel frequency
        (2, "Savers"),                 # highest savings ratio
        (4, "Investors"),              # highest investment interest
        (1, "Credit Seekers"),         # highest spending
    ]

    for feat_idx, label_name in feature_label_mapping:
        if len(used_labels) >= n_clusters:
            break
        ranked = np.argsort(centers[:, feat_idx])[::-1]
        for cluster_id in ranked:
            if cluster_id not in label_map and label_name not in used_labels:
                label_map[cluster_id] = label_name
                used_labels.add(label_name)
                break

    for i in range(n_clusters):
        if i not in label_map:
            label_map[i] = f"Segment {i}"

    return label_map


def get_segment_overview():
    """Return a summary of each segment with customer counts."""
    segments = db.session.query(
        SegmentAssignment.segment_name,
        db.func.count(SegmentAssignment.customer_id),
    ).group_by(SegmentAssignment.segment_name).all()

    return [
        {"segment_name": name, "customer_count": count}
        for name, count in segments
    ]
