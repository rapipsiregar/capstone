"""
Empirical Trust Drivers Service for Halal Cosmetics NLP.
Aggregates authentic SHAP Shapley value attributions from persistent catalog review cache
to identify top empirical drivers for High Trust and triggers for Low Trust per brand/category.
100% data-driven, zero linear coefficients or mock weights.
"""

import os
import re
from typing import Dict, Any, List, Optional
import pandas as pd
from backend.services.catalog_shap_cacher import get_cached_review_shap, load_shap_cache

# Filter stopwords and generic conversational fillers to preserve meaningful semantic attributes
SEMANTIC_STOPWORDS = {
    "dan", "di", "ke", "dari", "ini", "itu", "buat", "yang", "untuk", "ada",
    "aku", "saya", "kamu", "dia", "mereka", "kita", "nya", "banget", "juga",
    "bisa", "karena", "kalau", "kalo", "udah", "sudah", "tapi", "lagi", "jadi",
    "sama", "agak", "terus", "sih", "dong", "kok", "ya", "kan", "deh", "aja", "saja",
    "pada", "dengan", "atau", "lebih", "paling", "kurang", "selalu", "pernah",
    "haha", "hahaha", "bgttt", "bangettt", "lumayan", "tidak", "cuma", "masih",
    "bgt", "tp", "gitu", "gak", "ngga", "ga", "kali", "baru", "pas"
}

_EMPIRICAL_DRIVERS_CACHE: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}


def clean_feature_token(token: str) -> str:
    """Normalizes token string for aggregation, stripping punctuation and casing."""
    t = re.sub(r"[^a-zA-Z]", "", token.lower().strip())
    return t


def aggregate_shap_drivers_from_cache(
    texts: List[str],
    top_k: int = 5
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Aggregates token-level SHAP attributions from precomputed catalog cache.
    Calculates cumulative importance and average scores for positive (High Trust)
    and negative (Low Trust) words.
    """
    pos_scores: Dict[str, float] = {}
    pos_counts: Dict[str, int] = {}
    neg_scores: Dict[str, float] = {}
    neg_counts: Dict[str, int] = {}

    all_cache = load_shap_cache()

    for text in texts:
        if not text or not isinstance(text, str):
            continue
        cached = get_cached_review_shap(text)
        if not cached:
            continue

        attributions = cached.get("attributions", [])
        for item in attributions:
            raw_tok = item.get("token", "")
            tok = clean_feature_token(raw_tok)
            if len(tok) < 3 or tok in SEMANTIC_STOPWORDS:
                continue

            score = float(item.get("score", 0.0))
            impact = item.get("impact", "")

            if impact == "High_Trust" or score > 0.02:
                pos_scores[tok] = pos_scores.get(tok, 0.0) + abs(score)
                pos_counts[tok] = pos_counts.get(tok, 0) + 1
            elif impact == "Low_Trust" or score < -0.02:
                neg_scores[tok] = neg_scores.get(tok, 0.0) + abs(score)
                neg_counts[tok] = neg_counts.get(tok, 0) + 1

    # Fallback if specific brand/filter reviews have no cached entries yet:
    # Use global cache aggregated patterns rather than empty or fake data
    if not pos_scores and all_cache:
        for record in all_cache.values():
            for item in record.get("attributions", []):
                tok = clean_feature_token(item.get("token", ""))
                if len(tok) < 3 or tok in SEMANTIC_STOPWORDS:
                    continue
                score = float(item.get("score", 0.0))
                impact = item.get("impact", "")
                if impact == "High_Trust":
                    pos_scores[tok] = pos_scores.get(tok, 0.0) + abs(score)
                    pos_counts[tok] = pos_counts.get(tok, 0) + 1
                elif impact == "Low_Trust":
                    neg_scores[tok] = neg_scores.get(tok, 0.0) + abs(score)
                    neg_counts[tok] = neg_counts.get(tok, 0) + 1

    # Sort descending by cumulative attribution score
    sorted_pos = sorted(pos_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    sorted_neg = sorted(neg_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    high_list = [
        {
            "word": word,
            "score": f"+{round(total_score / max(1, pos_counts[word]), 2):.2f}",
            "raw_score": round(total_score / max(1, pos_counts[word]), 4),
            "frequency": pos_counts[word],
            "total_shap_weight": round(total_score, 4),
            "source": "IndoBERT SHAP Cache"
        }
        for word, total_score in sorted_pos
    ]

    low_list = [
        {
            "word": word,
            "score": f"-{round(total_score / max(1, neg_counts[word]), 2):.2f}",
            "raw_score": round(total_score / max(1, neg_counts[word]), 4),
            "frequency": neg_counts[word],
            "total_shap_weight": round(total_score, 4),
            "source": "IndoBERT SHAP Cache"
        }
        for word, total_score in sorted_neg
    ]

    return {"high": high_list, "low": low_list}


def compute_empirical_trust_drivers(
    df_subset: pd.DataFrame,
    top_k: int = 5,
    cache_key: Optional[str] = None
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Computes top positive and negative trust drivers for a given DataFrame subset of reviews
    by aggregating authentic SHAP values from cache.
    """
    if cache_key and cache_key in _EMPIRICAL_DRIVERS_CACHE:
        return _EMPIRICAL_DRIVERS_CACHE[cache_key]

    if df_subset is None or len(df_subset) == 0:
        return {"high": [], "low": []}

    text_col = "teks_ulasan_mentah" if "teks_ulasan_mentah" in df_subset.columns else "teks_ulasan_bersih"
    if text_col not in df_subset.columns:
        return {"high": [], "low": []}

    texts = df_subset[text_col].dropna().astype(str).tolist()
    result = aggregate_shap_drivers_from_cache(texts, top_k=top_k)

    if cache_key:
        _EMPIRICAL_DRIVERS_CACHE[cache_key] = result
    return result
