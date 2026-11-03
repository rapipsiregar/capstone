"""
Unit tests for Custom Halal Emerald Design System CSS tokens and styling rules.
"""

import os
import unittest

class TestFDDesignSystem(unittest.TestCase):

    def setUp(self):
        self.css_path = os.path.join("frontend", "css", "styles.css")

    def test_css_file_exists(self):
        """Test that styles.css file exists in frontend/css/."""
        self.assertTrue(os.path.exists(self.css_path))

    def test_halal_emerald_tokens_exist(self):
        """Test that Halal Emerald and Rose Gold design system CSS variables exist."""
        with open(self.css_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("--halal-teal", content)
        self.assertIn("--rose-gold", content)
        self.assertIn("--bg-slate", content)
        self.assertIn("--card-bg", content)
        self.assertIn("--text-dark", content)

    def test_inline_shap_highlight_classes_exist(self):
        """Test that inline SHAP highlight classes exist for review text integration."""
        with open(self.css_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn(".xai-highlight-green", content)
        self.assertIn(".xai-highlight-red", content)
        self.assertIn(".review-feed-card", content)

if __name__ == "__main__":
    unittest.main()
