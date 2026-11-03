"""
TDD Tests for Catalog Global Multi-Field Search Engine.
Tests search queries: 'mask', 'garnier', 'wardah', 'toner', 'oil', 'hada labo', etc.
Verifies matched_categories, matched_brands, pagination, and dropdown integrity.
"""

import os
import unittest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

HERO_CSS = os.path.join("frontend", "css", "catalog-hero.css")
HERO_JS = os.path.join("frontend", "js", "catalog-hero.js")
CATALOG_PY = os.path.join("backend", "api", "v1", "catalog.py")


class TestCatalogSearch(unittest.TestCase):

    def test_file_limits(self):
        for path in [HERO_CSS, HERO_JS, CATALOG_PY]:
            with open(path, "r", encoding="utf-8") as f:
                lines = len(f.read().splitlines())
                self.assertLessEqual(lines, 256, f"{path} has {lines} lines (must be <= 256)")

    def test_search_mask_returns_matched_categories_and_all_111_products(self):
        res = client.get("/api/v1/catalog/products?search=mask&limit=6")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["total_products"], 111)

        cat_names = [c["category_name"] for c in data.get("matched_categories", [])]
        self.assertIn("Mask Sheet", cat_names)
        self.assertIn("Sleeping Mask", cat_names)

        # Check product counts for the matched categories
        mask_sheet = next(c for c in data["matched_categories"] if c["category_name"] == "Mask Sheet")
        self.assertEqual(mask_sheet["product_count"], 26)

    def test_search_garnier_returns_all_27_products_and_brand_match(self):
        res = client.get("/api/v1/catalog/products?search=garnier&limit=6")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["total_products"], 27)

        brand_names = [b["brand_name"] for b in data.get("matched_brands", [])]
        self.assertIn("Garnier", brand_names)

        garnier = next(b for b in data["matched_brands"] if b["brand_name"] == "Garnier")
        self.assertEqual(garnier["product_count"], 27)
        self.assertEqual(garnier["review_count"], 271)

    def test_brand_filter_parameter(self):
        res = client.get("/api/v1/catalog/products?brand=Garnier&limit=50")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total_products"], 27)
        self.assertEqual(len(data["products"]), 27)
        for p in data["products"]:
            self.assertEqual(p["brand_name"], "Garnier")

    def test_search_wardah_and_toner(self):
        res_w = client.get("/api/v1/catalog/products?search=wardah&limit=6")
        self.assertEqual(res_w.status_code, 200)
        self.assertEqual(res_w.json()["total_products"], 46)

        res_t = client.get("/api/v1/catalog/products?search=toner&limit=6")
        self.assertEqual(res_t.status_code, 200)
        self.assertEqual(res_t.json()["total_products"], 39)
        cats = [c["category_name"] for c in res_t.json().get("matched_categories", [])]
        self.assertIn("Toner", cats)

    def test_css_dropdown_not_clipped(self):
        with open(HERO_CSS, "r", encoding="utf-8") as f:
            css = f.read()
        self.assertIn("overflow: visible", css)
        self.assertIn("z-index: 1000", css)
        self.assertIn("max-height: 420px", css)
        self.assertIn(".hero-search-chip-item", css)


if __name__ == "__main__":
    unittest.main()
