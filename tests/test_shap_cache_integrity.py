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
