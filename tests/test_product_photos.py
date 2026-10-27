"""
TDD Tests for Product Visual Cards & Local Photo Serving Engine.
Verifies product card markup, thumbnail containers, fallback handling, and local photo files.
"""

import os
import unittest

PRODUCTS_DIR = os.path.join("frontend", "images", "products")
CATALOG_JS = os.path.join("frontend", "js", "catalog.js")
CATALOG_HERO_JS = os.path.join("frontend", "js", "catalog-hero.js")
CATALOG_CSS = os.path.join("frontend", "css", "catalog.css")


class TestProductPhotos(unittest.TestCase):
    def test_product_images_exist(self):
        self.assertTrue(os.path.isdir(PRODUCTS_DIR), "frontend/images/products directory must exist")
        files = [f for f in os.listdir(PRODUCTS_DIR) if f.endswith(".jpg")]
        self.assertGreaterEqual(len(files), 10, f"Must have authentic product photos, found {len(files)}")

    def test_catalog_js_renders_product_thumbnails(self):
        with open(CATALOG_JS, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertIn("product-card-thumb-wrap", js)
        self.assertIn("product-card-thumb-img", js)
        self.assertIn("./images/products/", js)
        self.assertIn("no-photo", js)
        self.assertIn("onerror=", js)
        self.assertLessEqual(len(js.splitlines()), 256, "catalog.js must be <= 256 LOC")

    def test_catalog_hero_js_renders_product_thumbnails(self):
        with open(CATALOG_HERO_JS, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertIn("product-card-thumb-wrap", js)
        self.assertIn("product-card-thumb-img", js)
        self.assertIn("./images/products/", js)
        self.assertLessEqual(len(js.splitlines()), 256, "catalog-hero.js must be <= 256 LOC")

    def test_catalog_css_has_thumbnail_rules(self):
        with open(CATALOG_CSS, "r", encoding="utf-8") as f:
            css = f.read()
        self.assertIn(".product-card-thumb-wrap", css)
        self.assertIn(".product-card-thumb-img", css)
        self.assertIn("object-fit: contain", css)


if __name__ == "__main__":
    unittest.main()
