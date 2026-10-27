"""
Unit tests for CHARM Sticky Navigation Header & Branding Component.
"""

import os
import unittest

class TestFDHeaderUI(unittest.TestCase):

    def setUp(self):
        self.html_path = os.path.join("frontend", "index.html")
        self.js_path = os.path.join("frontend", "js", "app.js")

    def test_sticky_header_elements_exist_in_html(self):
        """Test that CHARM branding, sticky header, and filter controls exist in index.html."""
        self.assertTrue(os.path.exists(self.html_path))
        with open(self.html_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn('sticky-header', content)
        self.assertIn('CHARM', content)
        self.assertIn('Consumer Halal Awareness & Reputation Monitor', content)
        self.assertIn('id="categoryFilter"', content)

    def test_header_search_logic_exists_in_js(self):
        """Header uses centered brand + Guidebook buttons; app.js still binds the brand filter."""
        with open(self.html_path, "r", encoding="utf-8") as f:
            html = f.read()
        with open(self.js_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn('brand-center', html)
        self.assertIn('btn-guidebook-insight', html)
        self.assertIn('btn-guidebook-sandbox', html)
        self.assertIn('btn-guidebook-metrics', html)
        self.assertIn("bindFilterEvents", content)

if __name__ == "__main__":
    unittest.main()
