"""
Unit tests for Authentic IndoBERT SHAP Explainer Service.
Verifies real SHAP library integration, token-level attribution, and caching.
"""

import pytest
from backend.services.indobert_explainer import (
    explain_text_with_shap,
    get_highlight_color,
    determine_impact,
)


def test_determine_impact_and_color():
    assert determine_impact(0.05) == "High_Trust"
    assert determine_impact(-0.05) == "Low_Trust"
    assert determine_impact(0.01) == "Neutral"

    assert get_highlight_color(0.05, "High_Trust") == "#28a745"
    assert get_highlight_color(-0.05, "Low_Trust") == "#dc3545"
    assert get_highlight_color(0.01, "Neutral") == "#ffc107"


def test_explain_text_with_shap_authentic():
    sample_text = "Produk Wardah ini sangat bagus terbukti aman dan berlogo halal MUI resmi BPOM."
    result = explain_text_with_shap(sample_text)

    assert result["raw_text"] == sample_text
    assert "cleaned_text" in result
    assert result["predicted_trust"] in ["High_Trust", "Low_Trust", "Neutral"]
    assert result["predicted_aspect"] is not None
    assert 0.0 <= result["trust_confidence"] <= 1.0

    assert len(result["tokens"]) > 0
    assert len(result["attributions"]) == len(result["tokens"])
    assert "base_value" in result
    assert "explanation_summary" in result
    assert result["execution_time_ms"] > 0

    # Verify attribution item schema
    for item in result["attributions"]:
        assert "token" in item
        assert isinstance(item["score"], float)
        assert item["impact"] in ["High_Trust", "Low_Trust", "Neutral"]
        assert item["highlight_color"].startswith("#")

    # Verify in-memory cache functionality
    cached_result = explain_text_with_shap(sample_text)
    assert cached_result["from_cache"] is True
    assert cached_result["execution_time_ms"] < 200
