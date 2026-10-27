"""
Unit tests for Frontend 3-Level Drill-Down Catalog UI Component.
Verifies Level 1 (Categories), Level 2 (Products), Level 3 (Reviews & XAI), and Breadcrumbs.
"""

import os
import unittest


class TestCatalogUI(unittest.TestCase):

    def setUp(self):
        self.html_path = os.path.join("frontend", "index.html")
        self.js_path = os.path.join("frontend", "js", "catalog.js")
        self.css_path = os.path.join("frontend", "css", "catalog.css")

    def test_catalog_files_exist(self):
        """Test that catalog.js and catalog.css files exist."""
        self.assertTrue(os.path.exists(self.js_path), "catalog.js must exist")
        self.assertTrue(os.path.exists(self.css_path), "catalog.css must exist")

    def test_index_html_contains_drilldown_containers(self):
        """Test that index.html contains the 3-level catalog container hooks."""
        self.assertTrue(os.path.exists(self.html_path))
        with open(self.html_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn('catalog-drilldown-container', content)
        self.assertIn('catalog-level-categories', content)
        self.assertIn('catalog-level-products', content)
        self.assertIn('catalog-level-reviews', content)

    def test_catalog_js_contains_drilldown_logic(self):
        """Test that catalog.js contains functions for loading and transitioning levels."""
        with open(self.js_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("loadCatalogCategories", content)
        self.assertIn("openCategoryProducts", content)
        self.assertIn("openProductReviews", content)
        self.assertIn("backToCategories", content)
        self.assertIn("backToProducts", content)


if __name__ == "__main__":
    unittest.main()
