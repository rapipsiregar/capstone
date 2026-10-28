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


TEXT_A = "Sertifikat halal jelas dari BPOM resmi dan formulanya bagus."
TEXT_B = "Produk ini bikin breakout dan iritasi parah di wajah."
TEXT_OTHER = "Ulasan brand lain yang tidak boleh ikut dihitung."


@pytest.fixture
def isolated_cache(tmp_path, monkeypatch):
    """Temp SHAP cache with entries for TEXT_A, TEXT_B, and another brand's text."""
    import backend.services.catalog_shap_cacher as cacher
    monkeypatch.setattr(cacher, "CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(cacher, "CACHE_FILE", str(tmp_path / "cache.json"))
    monkeypatch.setattr(cacher, "_SHAP_DISK_CACHE", None)
    monkeypatch.setattr(ed_module, "_EMPIRICAL_DRIVERS_CACHE", {})

    def entry(text, attrs):
        key = cacher.hash_review_text(text)
        return key, {"text_hash": key, "raw_text": text, "attributions": attrs}

    cache = dict([
        entry(TEXT_A, [
            {"token": "halal", "score": 0.20, "impact": "High_Trust"},
            {"token": "resmi", "score": 0.10, "impact": "High_Trust"},
        ]),
        entry(TEXT_B, [
            {"token": "breakout", "score": -0.30, "impact": "Low_Trust"},
            # positive score but labelled Low_Trust must never become a High Trust driver
            {"token": "iritasi", "score": 0.05, "impact": "Low_Trust"},
        ]),
        entry(TEXT_OTHER, [{"token": "mahal", "score": 0.90, "impact": "High_Trust"}]),
    ])
    cacher.save_shap_cache(cache)
    yield cacher


def test_drivers_equal_aggregation_of_own_cache_entries(isolated_cache):
    df = pd.DataFrame({"teks_ulasan_mentah": [TEXT_A, TEXT_B], "merek_umkm": ["Wardah", "Wardah"]})
    drivers = compute_empirical_trust_drivers(df, top_k=5)
    assert [d["word"] for d in drivers["high"]] == ["halal", "resmi"]
    assert [d["word"] for d in drivers["low"]] == ["breakout", "iritasi"]
    assert drivers["high"][0]["raw_score"] == 0.2
    assert all("SHAP" in d["source"] for d in drivers["high"] + drivers["low"])


def test_brand_without_cached_reviews_gets_empty_drivers(isolated_cache):
    """No fallback: words from other brands must never be attributed to this brand."""
    df = pd.DataFrame({"teks_ulasan_mentah": ["Teks yang belum ada di cache."], "merek_umkm": ["X"]})
    assert compute_empirical_trust_drivers(df, top_k=5) == {"high": [], "low": []}


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
    assert len(data["trust_drivers"]["high"]) > 0

    # Non-existent brand must return empty drivers, no false attribution from other brands
    res_unknown = client.get("/api/v1/analytics/brands?brand=MerekFiktifYangTidakAda")
    assert res_unknown.status_code == 200
    data_unknown = res_unknown.json()
    assert data_unknown["trust_drivers"] == {"high": [], "low": []}
