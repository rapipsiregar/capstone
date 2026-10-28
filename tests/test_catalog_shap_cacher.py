"""
Unit tests for Catalog Review SHAP Caching Service and Integration.
Verifies persistent cache lookup, zero coef_ usage in review_explainer,
and seamless delivery of SHAP explanations to the catalog API.
"""

import os
import pytest
import backend.services.catalog_shap_cacher as cacher_module
from backend.services.catalog_shap_cacher import (
    hash_review_text,
    get_cached_review_shap,
    load_shap_cache,
    save_shap_cache,
)
from backend.services.review_explainer import generate_review_xai_explanation
import backend.services.review_explainer as re_module


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path, monkeypatch):
    """Redirects the SHAP cache to a temp file so tests never touch data/cache."""
    monkeypatch.setattr(cacher_module, "CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(cacher_module, "CACHE_FILE", os.path.join(str(tmp_path), "cache.json"))
    monkeypatch.setattr(cacher_module, "_SHAP_DISK_CACHE", None)
    yield


def test_hash_review_text_deterministic():
    text1 = "Sertifikat halal jelas dari BPOM resmi."
    text2 = "  Sertifikat halal jelas dari BPOM resmi.  "
    assert hash_review_text(text1) == hash_review_text(text2)


def test_review_explainer_does_not_use_coef():
    """Confirms review_explainer module source has zero references to coef_."""
    import inspect
    source = inspect.getsource(re_module)
    assert "coef_" not in source, "review_explainer must not use linear coef_ attribute"


def test_cached_review_shap_lookup():
    cache = load_shap_cache()
    assert cache == {}, "cache sementara harus kosong di awal"
    test_text = "Sample review halal test text"
    key = hash_review_text(test_text)
    cache[key] = {
        "text_hash": key,
        "raw_text": test_text,
        "predicted_trust": "High_Trust",
        "top_positive_words": ["halal", "test"],
        "top_negative_words": [],
        "explanation_summary": "Test summary"
    }
    save_shap_cache(cache)
    assert os.path.exists(cacher_module.CACHE_FILE)

    sample_key = next(iter(cache.keys()))
    sample_text = cache[sample_key]["raw_text"]
    retrieved = get_cached_review_shap(sample_text)
    assert retrieved is not None
    assert retrieved["text_hash"] == sample_key
    assert "top_positive_words" in retrieved


def test_generate_review_xai_explanation_uses_cache():
    sample_text = "Ulasan produk dengan atribusi SHAP tersimpan."
    key = hash_review_text(sample_text)
    cache = load_shap_cache()
    cache[key] = {
        "text_hash": key,
        "raw_text": sample_text,
        "predicted_trust": "High_Trust",
        "top_positive_words": ["unggul", "terbukti"],
        "top_negative_words": [],
        "explanation_summary": "Summary teruji"
    }
    save_shap_cache(cache)

    review_data = {
        "label_kepercayaan": "High_Trust",
        "aspek_komunikasi": "Klaim_Efikasi_Manfaat",
        "merek_umkm": "Wardah",
        "kondisi_kulit_usia": "Kulit Normal"
    }
    res = generate_review_xai_explanation(review_data, sample_text)
    assert "SHAP Transformer" in res["trust_reason"]
    assert "unggul" in res["trust_reason"]
