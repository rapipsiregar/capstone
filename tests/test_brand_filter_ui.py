"""
Unit Tests for Brand & Product Sentiment Filtering UI Component.
"""

import os
import unittest

class TestBrandFilterUI(unittest.TestCase):

    def setUp(self):
        self.html_path = os.path.join("frontend", "index.html")
        self.js_path = os.path.join("frontend", "js", "app.js")

    def test_brand_filter_elements_exist_in_html(self):
        """Test that brand and category select elements exist in index.html."""
        self.assertTrue(os.path.exists(self.html_path))
        with open(self.html_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        self.assertIn('id="brandFilter"', content)
        self.assertIn('id="categoryFilter"', content)
        self.assertIn('id="btnExportSummary"', content)

    def test_brand_filter_logic_exists_in_js(self):
        """Test that JavaScript app.js contains brand filtering functions."""
        self.assertTrue(os.path.exists(self.js_path))
        with open(self.js_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        self.assertIn("brandFilter", content)
        # categoryFilter previously only drove the removed homepage feed;
        # its dynamic wiring to Insight Reputasi is scoped in Task 6.3.
        self.assertIn("fetchBrandAnalytics", content)

if __name__ == "__main__":
    unittest.main()
