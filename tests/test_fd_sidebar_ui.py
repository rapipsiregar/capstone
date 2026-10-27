"""
Unit tests for Right Sidebar Brand Trust & Compliance Analytics Component.
"""

import os
import unittest

class TestFDSidebarUI(unittest.TestCase):

    def setUp(self):
        self.html_path = os.path.join("frontend", "index.html")
        self.js_path = os.path.join("frontend", "js", "app.js")

    def test_sidebar_elements_exist_in_html(self):
        """Test that right sidebar container and compliance bars exist in index.html."""
        self.assertTrue(os.path.exists(self.html_path))
        with open(self.html_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn('class="dashboard-layout-container"', content)
        self.assertIn('id="rightSidebarAnalytics"', content)
        self.assertIn('id="halalComplianceProgressBar"', content)

    def test_sidebar_logic_exists_in_js(self):
        """Test that JavaScript app.js contains renderRightSidebarAnalytics logic."""
        self.assertTrue(os.path.exists(self.js_path))
        with open(self.js_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("renderRightSidebarAnalytics", content)
        self.assertIn("halalComplianceProgressBar", content)

if __name__ == "__main__":
    unittest.main()
