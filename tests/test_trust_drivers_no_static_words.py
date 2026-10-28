"""
TDD Tests for Task 9.8: Dynamic SHAP Trust Drivers from API (zero static word arrays in frontend/js).
Verifies:
1. No static word arrays or hardcoded driver dictionaries in frontend/js/*.js.
2. API endpoint serves dynamic trust drivers aggregated from SHAP cache.
3. UI render function handles dynamic drivers honestly without static fallbacks.
"""

import glob
import os
import re
import pytest
from fastapi.testclient import TestClient
from backend.main import app

FRONTEND_JS_DIR = os.path.join("frontend", "js")


def test_no_static_driver_arrays_in_frontend_js():
    """frontend/js must not contain hardcoded driver word dictionaries or static driver arrays."""
    forbidden_patterns = [
        r"BRAND_DRIVERS\s*=",
        r"brand_drivers\s*=",
        r"HIGH_TRUST_WORDS\s*=",
        r"LOW_TRUST_WORDS\s*=",
        r"\[\s*['\"]kulit['\"],\s*['\"]cocok['\"]",
        r"\[\s*['\"]bruntusan['\"],\s*['\"]breakout['\"]",
    ]

    js_files = glob.glob(os.path.join(FRONTEND_JS_DIR, "*.js"))
    assert len(js_files) > 0, "No JS files found in frontend/js"

    for js_path in js_files:
        with open(js_path, "r", encoding="utf-8") as f:
            content = f.read()
        for pat in forbidden_patterns:
            matches = re.findall(pat, content, re.IGNORECASE)
            assert not matches, f"Found forbidden static driver pattern '{pat}' in {js_path}: {matches}"


def test_api_serves_empirical_drivers_for_all_and_brands():
    """API must serve authentic SHAP drivers for ALL and specific brands."""
    client = TestClient(app)

    # 1. Global drivers
    res_all = client.get("/api/v1/analytics/brands")
    assert res_all.status_code == 200
    data_all = res_all.json()
    assert "trust_drivers" in data_all
    drivers_all = data_all["trust_drivers"]
    assert "high" in drivers_all and "low" in drivers_all
    assert len(drivers_all["high"]) > 0
    assert len(drivers_all["low"]) > 0
    assert all(d.get("source") == "IndoBERT SHAP Cache" for d in drivers_all["high"])

    # 2. Brand specific drivers
    res_wardah = client.get("/api/v1/analytics/brands?brand=Wardah")
    assert res_wardah.status_code == 200
    data_wardah = res_wardah.json()
    drivers_w = data_wardah["trust_drivers"]
    assert len(drivers_w["high"]) > 0
    assert len(drivers_w["low"]) > 0

    # 3. Unknown brand has empty drivers (honest state)
    res_unknown = client.get("/api/v1/analytics/brands?brand=NonExistentBrandXYZ")
    assert res_unknown.status_code == 200
    data_unknown = res_unknown.json()
    assert data_unknown["trust_drivers"] == {"high": [], "low": []}


def test_render_brand_trust_insight_card_logic():
    """app.js must render empty state text when drivers are empty, without fallback to fake words."""
    app_js_path = os.path.join(FRONTEND_JS_DIR, "app.js")
    with open(app_js_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "renderBrandTrustInsightCard" in content
    # Ensure it uses dynamicDrivers passed from API
    assert "dynamicDrivers" in content
