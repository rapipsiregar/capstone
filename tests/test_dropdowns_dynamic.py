"""
TDD Tests for Task 9.7: Dynamic Brand and Category Dropdowns from API.
Verifies:
1. index.html does not contain hardcoded <option> elements for brands or categories (only 'ALL').
2. Backend APIs return exactly 216 brands and 23 categories matching the dataset.
3. Dropdown population logic in frontend fetches from API and populates exact dataset counts.
"""

import os
import re
from html.parser import HTMLParser
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from backend.main import app

DATASET_PATH = os.path.join("data", "annotated", "female_daily_skincare_annotated.csv")
INDEX_PATH = os.path.join("frontend", "index.html")
APP_JS_PATH = os.path.join("frontend", "js", "app.js")


class SelectOptionParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current_select = None
        self.select_options = {}

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "select":
            self.current_select = attrs_dict.get("id")
            if self.current_select:
                self.select_options[self.current_select] = []
        elif tag == "option" and self.current_select:
            self.select_options[self.current_select].append(attrs_dict.get("value"))

    def handle_endtag(self, tag):
        if tag == "select":
            self.current_select = None


@pytest.fixture(scope="module")
def dataset_df():
    return pd.read_csv(DATASET_PATH)


@pytest.fixture(scope="module")
def parsed_options():
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    parser = SelectOptionParser()
    parser.feed(content)
    return parser.select_options


def test_index_html_dropdowns_have_no_hardcoded_options(parsed_options):
    """HTML must only contain the initial ALL option for brand and category dropdowns."""
    brand_opts = parsed_options.get("brandFilter", [])
    assert len(brand_opts) == 1, (
        f"brandFilter harus hanya memiliki 1 opsi awal ('ALL'), ditemukan {len(brand_opts)}: {brand_opts}"
    )
    assert brand_opts[0] == "ALL"

    category_opts = parsed_options.get("categoryFilter", [])
    assert len(category_opts) == 1, (
        f"categoryFilter harus hanya memiliki 1 opsi awal ('ALL'), ditemukan {len(category_opts)}: {category_opts}"
    )
    assert category_opts[0] == "ALL"


def test_backend_apis_match_dataset_counts(dataset_df):
    """API endpoints must return 216 brands and 23 categories."""
    client = TestClient(app)

    # 1. Categories endpoint
    cat_res = client.get("/api/v1/catalog/categories")
    assert cat_res.status_code == 200
    cat_data = cat_res.json()
    assert cat_data.get("total_categories") == 23
    assert len(cat_data.get("categories", [])) == 23
    assert dataset_df["kategori_produk"].nunique() == 23

    # 2. Brands endpoint
    brand_res = client.get("/api/v1/analytics/brands")
    assert brand_res.status_code == 200
    brand_data = brand_res.json()
    assert brand_data.get("total_brands") == 216
    assert len(brand_data.get("all_brands", [])) == 216
    assert dataset_df["merek_umkm"].nunique() == 216


def test_app_js_has_populate_categories_and_brands():
    """app.js must define functions to fetch and populate both brand and category dropdowns."""
    with open(APP_JS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    assert "populateAllBrandsDropdown" in content
    assert "populateAllCategoriesDropdown" in content
    assert "/catalog/categories" in content
    assert "/analytics/brands" in content
