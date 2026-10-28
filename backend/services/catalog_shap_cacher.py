"""
Catalog Review SHAP Caching Service for Halal Cosmetics NLP.
Provides offline and persistent caching of SHAP token attributions for catalog reviews,
eliminating repetitive transformer computation during browsing.
"""

import os
import json
import hashlib
from typing import Callable, Dict, Any, Optional, List
from backend.services.shap_word_attribution import ATTRIBUTION_METHOD, compute_word_shap_record

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
        json.dump(cache_data, f, ensure_ascii=False, separators=(",", ":"))
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


def compute_and_cache_review_shap(text: str, persist: bool = True) -> Dict[str, Any]:
    """
    Computes word-level SHAP attribution (score = SHAP High_Trust - SHAP Low_Trust)
    via the fine-tuned IndoBERT model and stores it in the cache.
    With persist=False the record is kept in memory only (batch jobs save periodically).
    """
    cache = load_shap_cache()
    key = hash_review_text(text)
    cached = cache.get(key)
    if cached and cached.get("attribution_method") == ATTRIBUTION_METHOD:
        return cached

    record = compute_word_shap_record(text, key)
    cache[key] = record
    if persist:
        save_shap_cache(cache)
    return record


def is_current_record(record: Optional[Dict[str, Any]]) -> bool:
    """True if the cached record was built with the current attribution method."""
    return bool(record) and record.get("attribution_method") == ATTRIBUTION_METHOD


def precompute_review_cache(
    reviews: List[str],
    save_every: int = 200,
    progress: Optional[Callable[[int, int], None]] = None,
) -> int:
    """
    Computes SHAP for every review not yet cached with the current method.
    Saves to disk every `save_every` new records and at the end (resumable).
    Returns count of newly computed records.
    """
    cache = load_shap_cache()
    todo = []
    seen = set()
    for rev in reviews:
        if not isinstance(rev, str) or not rev.strip():
            continue
        key = hash_review_text(rev)
        if key in seen or is_current_record(cache.get(key)):
            continue
        seen.add(key)
        todo.append(rev)

    for i, rev in enumerate(todo, start=1):
        compute_and_cache_review_shap(rev, persist=False)
        if i % save_every == 0:
            save_shap_cache(cache)
        if progress:
            progress(i, len(todo))
    if todo:
        save_shap_cache(cache)
    return len(todo)
