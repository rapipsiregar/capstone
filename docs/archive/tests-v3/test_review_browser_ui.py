"""
Unit Tests for Review Browsing.
The legacy homepage feed/search widget was replaced (Phase 6, Task 6.1) by the
3-level catalog: reviews are now browsed via Category -> Product -> Reviews.
"""

import os
import unittest

class TestReviewBrowserUI(unittest.TestCase):

    def setUp(self):
        self.html_path = os.path.join("frontend", "index.html")
        self.js_path = os.path.join("frontend", "js", "catalog.js")

    def test_review_browser_elements_exist_in_html(self):
        """Reviews are browsed through the catalog Level 3 container, not the legacy feed."""
        with open(self.html_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn('id="catalogReviewsFeed"', content)
        self.assertIn('id="catalogReviewsPagination"', content)
        self.assertNotIn('id="reviewBrowserContainer"', content)

    def test_review_browser_logic_exists_in_js(self):
        """catalog.js fetches product reviews dynamically with pagination."""
        with open(self.js_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("openProductReviews", content)
        self.assertIn("/catalog/reviews", content)
        self.assertIn("renderPagination", content)

if __name__ == "__main__":
    unittest.main()
