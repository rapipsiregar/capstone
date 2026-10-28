"""
Task 8.15: dataset numbers written in docs/feature-list.md must equal file counts.
"""

import os

import pandas as pd

FEATURE_LIST = os.path.join("docs", "feature-list.md")
DATASET = os.path.join("data", "annotated", "female_daily_skincare_annotated.csv")


def _fmt(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def test_feature_list_dataset_numbers_match_files():
    with open(FEATURE_LIST, "r", encoding="utf-8") as f:
        doc = f.read()
    df = pd.read_csv(DATASET)
    assert f"{_fmt(len(df))} ulasan" in doc
    assert f"{df['nama_produk'].nunique()} produk" in doc
    assert f"{df['kategori_produk'].nunique()} kategori" in doc
    assert f"{df['merek_umkm'].nunique()} brand" in doc


def test_feature_list_has_no_unverified_numbers():
    with open(FEATURE_LIST, "r", encoding="utf-8") as f:
        doc = f.read()
    for stale in ("10.826", "80+ brand", "861 produk skincare"):
        assert stale not in doc, f"angka tanpa sumber berkas masih ada: {stale}"
