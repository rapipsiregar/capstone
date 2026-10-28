"""
Task 9.4: homepage & metrics-tab statistics come from the API, never from literals.
Numbers to look for are derived from the dataset files, not typed into this test.
"""

import os
import re

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from backend.main import app

ANNOTATED = os.path.join("data", "annotated")
FRONTEND = "frontend"


def _variants(n: int) -> set:
    return {str(n), f"{n:,}", f"{n:,}".replace(",", ".")}


@pytest.fixture(scope="module")
def dataset_numbers():
    df = pd.read_csv(os.path.join(ANNOTATED, "female_daily_skincare_annotated.csv"))
    splits = {s: len(pd.read_csv(os.path.join(ANNOTATED, f"{s}.csv"))) for s in ("train", "val", "test")}
    return {
        "total_reviews": len(df),
        "total_products": int(df["nama_produk"].nunique()),
        "total_brands": int(df["merek_umkm"].nunique()),
        "splits": splits,
    }


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _literal_hits(text: str, numbers: list) -> list:
    hits = []
    for n in numbers:
        for v in _variants(n):
            if re.search(rf"(?<![\w.,#-]){re.escape(v)}(?![\w%]|[.,]\d)", text):
                hits.append(v)
    return hits


def test_index_html_has_no_dataset_stat_literals(dataset_numbers):
    html = _read(os.path.join(FRONTEND, "index.html"))
    numbers = [dataset_numbers["total_reviews"], dataset_numbers["total_products"],
               dataset_numbers["total_brands"], *dataset_numbers["splits"].values(), 10826]
    assert _literal_hits(html, numbers) == []


def test_index_html_text_nodes_have_no_percentages():
    html = _read(os.path.join(FRONTEND, "index.html"))
    body = re.sub(r"<style.*?</style>|<script.*?</script>", "", html, flags=re.S)
    in_text = re.findall(r">[^<]*?\d+(?:[.,]\d+)?\s*%[^<]*<", body)
    in_style_width = re.findall(r"width:\s*\d+(?:\.\d+)?%", body)
    assert in_text == [] and in_style_width == []


def test_js_has_no_dataset_stat_fallbacks(dataset_numbers):
    numbers = [dataset_numbers["total_reviews"], dataset_numbers["total_brands"],
               dataset_numbers["total_products"], *dataset_numbers["splits"].values()]
    for name in ("api.js", "charts.js", "app.js"):
        js = _read(os.path.join(FRONTEND, "js", name))
        assert _literal_hits(js, numbers) == [], name


def test_catalog_stats_serves_split_counts_equal_to_files(dataset_numbers):
    data = TestClient(app).get("/api/v1/catalog/stats").json()
    assert data["split_counts"] == dataset_numbers["splits"]
    assert data["total_reviews"] == dataset_numbers["total_reviews"]
