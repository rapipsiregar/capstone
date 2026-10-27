"""
TDD tests for Task 6.5: per-product trust parameters on Level 3 catalog.
Expected values are recomputed straight from the annotated CSV (data apa adanya).
"""

import os
import pandas as pd
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
DATASET = os.path.join("data", "annotated", "female_daily_skincare_annotated.csv")


def _dataset():
    return pd.read_csv(DATASET)


def _subset(df, name_lower):
    return df[df["nama_produk"].str.strip().str.lower() == name_lower]


def _fetch_info(name):
    resp = client.get("/api/v1/catalog/reviews", params={"product_name": name, "limit": 8})
    assert resp.status_code == 200
    return resp.json()["product_info"]


def test_summary_matches_all_reviews_of_product_not_just_page():
    df = _dataset()
    target = df["nama_produk"].str.strip().str.lower().value_counts().index[0]
    sub = _subset(df, target)
    assert len(sub) > 8, "target must span more than one page"

    info = _fetch_info(target)
    td, ad = info["trust_distribution"], info["aspect_distribution"]

    expected_trust = sub["label_kepercayaan"].value_counts().to_dict()
    for label in df["label_kepercayaan"].dropna().unique():
        assert td[label] == int(expected_trust.get(label, 0))
    expected_aspect = sub["aspek_komunikasi"].value_counts().to_dict()
    for aspect in df["aspek_komunikasi"].dropna().unique():
        assert ad[aspect] == int(expected_aspect.get(aspect, 0))

    assert sum(td.values()) == len(sub)
    high = int((sub["label_kepercayaan"] == "High_Trust").sum())
    assert info["high_trust_pct"] == round(high / len(sub) * 100, 1)
    top = max(expected_aspect.values())
    assert sorted(info["dominant_aspects"]) == sorted(k for k, v in expected_aspect.items() if v == top)


def test_zero_count_aspects_are_kept_as_zero():
    df = _dataset()
    all_aspects = set(df["aspek_komunikasi"].dropna().unique())
    names = df["nama_produk"].str.strip().str.lower()
    per_prod = df.groupby(names)["aspek_komunikasi"].nunique()
    target = per_prod[per_prod < len(all_aspects)].index[0]

    ad = _fetch_info(target)["aspect_distribution"]
    assert set(ad.keys()) == all_aspects
    assert 0 in ad.values()
