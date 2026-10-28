"""
Unit tests for word-level SHAP attribution (Task 8.10 / 8.11, keputusan user Opsi A).
Subword pieces are merged into whole words by summing SHAP values (SHAP is additive);
each word is scored by SHAP(High_Trust) - SHAP(Low_Trust), regardless of predicted class.
"""

import numpy as np

from backend.services.shap_word_attribution import (
    merge_subword_values,
    build_direction_attributions,
    select_top_words,
)

# class order follows models/indobert_trust/config.json: 0 Low, 1 Neutral, 2 High
RAW_TOKENS = ["", "melemb", "abkan ", "kulit ", "dan ", "peri", "h"]
VALUES = np.array([
    [0.00, 0.00, 0.00],
    [0.01, 0.00, 0.05],
    [0.00, 0.02, 0.03],
    [0.10, 0.00, -0.02],
    [0.00, 0.01, 0.005],
    [0.04, 0.00, 0.00],
    [0.03, 0.00, -0.01],
])


def test_merge_subword_values_joins_pieces_and_sums_values():
    words = merge_subword_values(RAW_TOKENS, VALUES)
    assert [w for w, _ in words] == ["melembabkan", "kulit", "dan", "perih"]
    np.testing.assert_allclose(words[0][1], [0.01, 0.02, 0.08])
    # last word has no trailing space and must still be flushed
    np.testing.assert_allclose(words[3][1], [0.07, 0.00, -0.01])


def test_direction_score_is_high_minus_low_for_any_prediction():
    attrs = build_direction_attributions(RAW_TOKENS, VALUES)
    by_word = {a["token"]: a for a in attrs}
    assert by_word["melembabkan"]["score"] == 0.07
    assert by_word["melembabkan"]["impact"] == "High_Trust"
    assert by_word["kulit"]["score"] == -0.12
    assert by_word["kulit"]["impact"] == "Low_Trust"
    assert by_word["perih"]["impact"] == "Low_Trust"
    # |0.005 - 0| below threshold 0.02 -> Neutral
    assert by_word["dan"]["impact"] == "Neutral"


def test_select_top_words_skips_stopwords_and_orders_by_strength():
    attrs = [
        {"token": "banget", "score": 0.30, "impact": "High_Trust"},
        {"token": "halal", "score": 0.10, "impact": "High_Trust"},
        {"token": "lembut", "score": 0.20, "impact": "High_Trust"},
        {"token": "perih", "score": -0.15, "impact": "Low_Trust"},
        {"token": "ok", "score": 0.50, "impact": "High_Trust"},
    ]
    pos, neg = select_top_words(attrs, k=5)
    assert pos == ["lembut", "halal"]
    assert neg == ["perih"]
