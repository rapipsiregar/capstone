"""
Unit tests for Review Cards with Inline SHAP XAI Highlighting.
Review cards are rendered by catalog Level 3 (Phase 6, Task 6.1). SHAP highlight
spans are produced by the backend (`highlighted_text`), not by a hardcoded JS list.
"""

import os
import unittest

class TestFDReviewCardsUI(unittest.TestCase):

    def setUp(self):
        self.html_path = os.path.join("frontend", "index.html")
        self.js_path = os.path.join("frontend", "js", "catalog.js")
        self.api_path = os.path.join("backend", "api", "v1", "catalog.py")

    def test_review_feed_container_exists_in_html(self):
        """Catalog Level 3 review container exists; legacy feed container is gone."""
        with open(self.html_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn('id="catalog-level-reviews"', content)
        self.assertNotIn('id="reviewFeedContainer"', content)

    def test_review_feed_card_rendering_logic_exists_in_js(self):
        """catalog.js renders review cards using backend SHAP highlight + XAI fields."""
        with open(self.js_path, "r", encoding="utf-8") as f:
            js = f.read()
        with open(self.api_path, "r", encoding="utf-8") as f:
            api = f.read()

        self.assertIn("catalog-review-card", js)
        self.assertIn("highlighted_text", js)
        self.assertIn("xai-highlight-green", api)
        self.assertIn("xai-highlight-red", api)

if __name__ == "__main__":
    unittest.main()
