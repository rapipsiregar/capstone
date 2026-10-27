"""
Unit tests for Empirical Trust Drivers Service.
Verifies aggregation of authentic SHAP cache, zero linear coef_ or .joblib dependencies,
and structured output delivery for brand analytics.
"""

import pytest
import pandas as pd
from backend.services.empirical_drivers import (
    compute_empirical_trust_drivers,
    aggregate_shap_drivers_from_cache,
    clean_feature_token,
)
import backend.services.empirical_drivers as ed_module


def test_clean_feature_token():
    assert clean_feature_token("Halal!") == "halal"
    assert clean_feature_token("123bpom") == "bpom"
    assert clean_feature_token("  cocok  ") == "cocok"


def test_no_coef_or_joblib_in_empirical_drivers():
    """Verifies empirical_drivers has completely eliminated joblib and coef_."""
    import inspect
    source = inspect.getsource(ed_module)
    assert "joblib" not in source, "empirical_drivers must not import or use joblib"
    assert "coef_" not in source, "empirical_drivers must not reference linear coef_"


def test_aggregate_shap_drivers_from_cache():
    # Construct mock cached reviews dataframe
    df = pd.DataFrame({
        "teks_ulasan_mentah": [
            "Sertifikat halal jelas dari BPOM resmi dan formulanya bagus.",
            "Produk ini bikin breakout dan iritasi parah di wajah."
        ],
        "merek_umkm": ["Wardah", "Wardah"]
    })

    drivers = compute_empirical_trust_drivers(df, top_k=5)
    assert "high" in drivers
    assert "low" in drivers
    assert isinstance(drivers["high"], list)
    assert isinstance(drivers["low"], list)

    if drivers["high"]:
        top_high = drivers["high"][0]
        assert "word" in top_high
        assert "score" in top_high
        assert "source" in top_high
        assert "SHAP" in top_high["source"]


def test_brand_analytics_integration_with_shap_drivers():
    from fastapi.testclient import TestClient
    from backend.main import app

    client = TestClient(app)
    response = client.get("/api/v1/analytics/brands?brand=Wardah")
    assert response.status_code == 200
    data = response.json()
    assert "trust_drivers" in data
    assert "high" in data["trust_drivers"]
    assert "low" in data["trust_drivers"]
