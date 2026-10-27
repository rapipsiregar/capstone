"""
Catalog Review SHAP Caching Service for Halal Cosmetics NLP.
Provides offline and persistent caching of SHAP token attributions for catalog reviews,
eliminating repetitive transformer computation during browsing.
"""

import os
import json
import hashlib
from typing import Dict, Any, Optional, List
from backend.services.indobert_explainer import explain_text_with_shap

CACHE_DIR = os.path.join("data", "cache")
CACHE_FILE = os.path.join(CACHE_DIR, "review_shap_cache.json")

_SHAP_DISK_CACHE: Optional[Dict[str, Any]] = None


def hash_review_text(text: str) -> str:
    """Computes a consistent MD5 hex digest for review text."""
    return hashlib.md5(text.strip().encode("utf-8")).hexdigest()


def load_shap_cache() -> Dict[str, Any]:
    """Loads the persistent SHAP cache from disk, initializing if missing."""
    global _SHAP_DISK_CACHE
    if _SHAP_DISK_CACHE is not None:
        return _SHAP_DISK_CACHE

    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                _SHAP_DISK_CACHE = json.load(f)
                return _SHAP_DISK_CACHE
        except Exception:
            _SHAP_DISK_CACHE = {}
            return _SHAP_DISK_CACHE
    else:
        _SHAP_DISK_CACHE = {}
        return _SHAP_DISK_CACHE


def save_shap_cache(cache_data: Dict[str, Any]) -> None:
    """Persists memory cache dictionary to disk atomically."""
    global _SHAP_DISK_CACHE
    _SHAP_DISK_CACHE = cache_data
    os.makedirs(CACHE_DIR, exist_ok=True)
    temp_file = CACHE_FILE + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)
    os.replace(temp_file, CACHE_FILE)


def get_cached_review_shap(text: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves precomputed SHAP attribution record for a review text.
    Returns None if text is not in cache.
    """
    if not isinstance(text, str) or not text.strip():
        return None
    cache = load_shap_cache()
    key = hash_review_text(text)
    return cache.get(key)


def compute_and_cache_review_shap(text: str) -> Dict[str, Any]:
    """
    Computes SHAP attribution via authentic IndoBERT explainer and stores it in disk cache.
    """
    cache = load_shap_cache()
    key = hash_review_text(text)
    if key in cache:
        return cache[key]

    shap_res = explain_text_with_shap(text)
    pos_words = [a["token"] for a in shap_res.get("attributions", []) if a.get("impact") == "High_Trust"]
    neg_words = [a["token"] for a in shap_res.get("attributions", []) if a.get("impact") == "Low_Trust"]

    record = {
        "text_hash": key,
        "raw_text": text,
        "predicted_trust": shap_res.get("predicted_trust"),
        "predicted_aspect": shap_res.get("predicted_aspect"),
        "trust_confidence": shap_res.get("trust_confidence"),
        "tokens": shap_res.get("tokens", []),
        "attributions": shap_res.get("attributions", []),
        "base_value": shap_res.get("base_value", 0.0),
        "top_positive_words": pos_words[:5],
        "top_negative_words": neg_words[:5],
        "explanation_summary": shap_res.get("explanation_summary", "")
    }

    cache[key] = record
    save_shap_cache(cache)
    return record


def precompute_sample_catalog_cache(reviews: List[str], max_count: int = 50) -> int:
    """
    Batch computes and saves SHAP cache for sample catalog reviews.
    Returns count of newly cached items.
    """
    added = 0
    for rev in reviews[:max_count]:
        if not rev or not rev.strip():
            continue
        key = hash_review_text(rev)
        cache = load_shap_cache()
        if key not in cache:
            compute_and_cache_review_shap(rev)
            added += 1
    return added
