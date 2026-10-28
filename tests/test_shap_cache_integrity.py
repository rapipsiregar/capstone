"""
Integrity tests for the persistent SHAP cache file (data/cache/review_shap_cache.json).
Reads the real cache file read-only and checks every entry belongs to the dataset.
"""

import json
import os

import pandas as pd
import pytest

from backend.services.catalog_shap_cacher import hash_review_text

CACHE_PATH = os.path.join("data", "cache", "review_shap_cache.json")
DATASET_PATH = os.path.join("data", "annotated", "female_daily_skincare_annotated.csv")


@pytest.fixture(scope="module")
def real_cache():
    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def dataset_texts():
    df = pd.read_csv(DATASET_PATH)
    return set(df["teks_ulasan_mentah"].astype(str).str.strip())


def test_every_cache_entry_comes_from_dataset(real_cache, dataset_texts):
    """No test fixtures or foreign texts may live in the real cache."""
    foreign = [
        v.get("raw_text", "")[:60]
        for v in real_cache.values()
        if v.get("raw_text", "").strip() not in dataset_texts
    ]
    assert foreign == [], f"Entri cache di luar dataset: {foreign}"


def test_cache_keys_match_text_hash(real_cache):
    mismatched = [k for k, v in real_cache.items() if hash_review_text(v.get("raw_text", "")) != k]
    assert mismatched == []


def test_cache_coverage_full_dataset(real_cache, dataset_texts):
    """Task 8.10: Cache must cover all 8,365 active dataset reviews with word-level method."""
    assert len(dataset_texts) == 8365
    assert len(real_cache) == 8365
    missing = [text for text in dataset_texts if hash_review_text(text) not in real_cache]
    assert missing == [], f"Ada {len(missing)} ulasan belum ada di cache"
    wrong_method = [
        k for k, v in real_cache.items()
        if v.get("attribution_method") != "word_shap_high_minus_low_v1"
    ]
    assert wrong_method == [], f"Ada {len(wrong_method)} entri cache dengan metode lama/salah"

