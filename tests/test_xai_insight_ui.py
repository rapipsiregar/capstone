"""
Unit Tests for XAI Keyword Highlighting & Brand Trust Insight Card Component.
"""

import os
import unittest

class TestXAIInsightUI(unittest.TestCase):

    def setUp(self):
        self.html_path = os.path.join("frontend", "index.html")
        self.js_path = os.path.join("frontend", "js", "app.js")

    def test_insight_card_elements_exist_in_html(self):
        """Test that highTrustDriversList and lowTrustDriversList exist in index.html."""
        self.assertTrue(os.path.exists(self.html_path))
        with open(self.html_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        self.assertIn('id="highTrustDriversList"', content)
        self.assertIn('id="lowTrustDriversList"', content)
        self.assertIn('id="insightCardBrandTitle"', content)

    def test_insight_card_logic_exists_in_js(self):
        """Test that JavaScript app.js contains renderBrandTrustInsightCard function."""
        self.assertTrue(os.path.exists(self.js_path))
        with open(self.js_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        self.assertIn("renderBrandTrustInsightCard", content)
        self.assertIn("highTrustDriversList", content)
        self.assertIn("lowTrustDriversList", content)

if __name__ == "__main__":
    unittest.main()
