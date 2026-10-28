"""
TDD Tests for Task 9.9: Dynamic Halal & BPOM Compliance Ratios from Dataset.
Verifies:
1. No static fake compliance ratios ({ 'Wardah': '98.2%', ... }) in frontend/js/app.js.
2. GET /api/v1/analytics/brands computes authentic compliance counts and ratios from dataset.
3. Specific brand query (e.g. Wardah) returns authentic compliance values matching dataset.
"""

import os
import re
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from backend.main import app

DATASET_PATH = os.path.join("data", "annotated", "female_daily_skincare_annotated.csv")
APP_JS_PATH = os.path.join("frontend", "js", "app.js")


@pytest.fixture(scope="module")
def dataset_df():
    return pd.read_csv(DATASET_PATH)


def test_no_hardcoded_compliance_ratios_in_app_js():
    """frontend/js/app.js must not contain hardcoded fake compliance ratio object."""
    with open(APP_JS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    fake_patterns = [
        r"98\.2%",
        r"95\.6%",
        r"97\.4%",
        r"96\.4%",
        r"complianceRatios\s*=",
    ]
    for pat in fake_patterns:
        matches = re.findall(pat, content)
        assert not matches, f"Found fake hardcoded compliance ratio pattern '{pat}' in app.js: {matches}"


def test_brand_analytics_api_compliance_scope_all(dataset_df):
    """GET /api/v1/analytics/brands must return dataset compliance for ALL reviews."""
    client = TestClient(app)
    res = client.get("/api/v1/analytics/brands")
    assert res.status_code == 200
    data = res.json()

    assert "compliance" in data
    comp = data["compliance"]
    assert "either_count" in comp
    assert "compliance_ratio" in comp
    assert "compliance_percentage" in comp

    expected_halal = int((dataset_df["klaim_halal"] == 1).sum())
    expected_bpom = int((dataset_df["klaim_bpom"] == 1).sum())
    expected_either = int(((dataset_df["klaim_halal"] == 1) | (dataset_df["klaim_bpom"] == 1)).sum())
    expected_ratio = round(expected_either / len(dataset_df), 4)

    assert comp["halal_count"] == expected_halal
    assert comp["bpom_count"] == expected_bpom
    assert comp["either_count"] == expected_either
    assert comp["compliance_ratio"] == expected_ratio


def test_brand_analytics_api_compliance_wardah(dataset_df):
    """GET /api/v1/analytics/brands?brand=Wardah returns exact dataset compliance for Wardah."""
    client = TestClient(app)
    res = client.get("/api/v1/analytics/brands?brand=Wardah")
    assert res.status_code == 200
    data = res.json()

    assert "compliance" in data
    comp = data["compliance"]

    wardah_df = dataset_df[dataset_df["merek_umkm"].str.lower() == "wardah"]
    expected_either = int(((wardah_df["klaim_halal"] == 1) | (wardah_df["klaim_bpom"] == 1)).sum())
    expected_ratio = round(expected_either / len(wardah_df), 4)

    assert comp["total_reviews"] == len(wardah_df)
    assert comp["either_count"] == expected_either
    assert comp["compliance_ratio"] == expected_ratio
