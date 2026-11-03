"""
Unit tests for Phase 6 Homepage-First Layout.
Task 6.1: Homepage only contains the 3-level catalog; analytics move to Guidebook "Insight Reputasi".
Task 6.2: Catalog Level 2 & 3 render data-driven badges and real XAI fields (no static fallback text).
"""

import os
import re
import unittest


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class TestHomepageLayout(unittest.TestCase):

    def setUp(self):
        self.html = _read(os.path.join("frontend", "index.html"))
        self.catalog_js = _read(os.path.join("frontend", "js", "catalog.js"))
        self.app_js = _read(os.path.join("frontend", "js", "app.js"))

    def _panel(self, panel_id: str) -> str:
        """Returns HTML between the opening of panel_id and the next tab panel."""
        start = self.html.index(f'id="{panel_id}"')
        nxt = self.html.find('<div id="tab-content-', start + 1)
        return self.html[start:nxt if nxt != -1 else len(self.html)]

    # ---------- Task 6.1 ----------
    def test_old_review_feed_removed(self):
        self.assertNotIn('id="reviewFeedContainer"', self.html)
        self.assertNotIn('id="searchReviewInput"', self.html)
        self.assertNotIn("filterAndRenderReviews", self.app_js)

    def test_homepage_contains_only_catalog(self):
        home = self._panel("tab-content-reputation")
        self.assertIn('id="catalog-drilldown-container"', home)
        self.assertNotIn('id="stat-total-reviews"', home)
        self.assertNotIn('id="aspectChart"', home)
        self.assertNotIn('id="rightSidebarAnalytics"', home)

    def test_insight_guidebook_button_and_panel(self):
        self.assertIn('id="btn-guidebook-insight"', self.html)
        self.assertIn('data-tab-target="tab-content-insight"', self.html)
        insight = self._panel("tab-content-insight")
        for el in ["stat-total-reviews", "stat-high-trust", "aspectChart",
                   "trustChart", "rightSidebarAnalytics", "brandFilter"]:
            self.assertIn(f'id="{el}"', insight)

    # ---------- Task 6.2 ----------
    def test_catalog_uses_real_xai_fields(self):
        self.assertIn("umkm_recommendation", self.catalog_js)
        self.assertNotIn("strategic_recommendation", self.catalog_js)

    def test_catalog_badges_are_data_driven(self):
        self.assertIn("halal_claim", self.catalog_js)
        self.assertIn("bpom_claim", self.catalog_js)
        self.assertIn("Neutral", self.catalog_js)
        self.assertNotIn("Terdaftar Resmi BPOM & Halal", self.catalog_js)
        self.assertIsNone(re.search(r"Memuat \d+ Kategori", self.catalog_js))


    # ---------- Section 9B (Task 9.4, 9.5, 9.6) ----------
    def test_hero_stats_not_hardcoded_in_html(self):
        """Task 9.4 (F2): Verify hero stats row does not contain hardcoded literal numbers."""
        home = self._panel("tab-content-reputation")
        stats_match = re.search(r'<div class="hero-stats-row"[^>]*>(.*?)</div>', home, re.DOTALL)
        self.assertIsNotNone(stats_match)
        stats_html = stats_match.group(1)
        self.assertNotIn(">801<", stats_html)
        self.assertNotIn(">216<", stats_html)
        self.assertNotIn(">8.365<", stats_html)
        self.assertIn('id="heroCountProducts"', stats_html)
        self.assertIn('id="heroCountBrands"', stats_html)
        self.assertIn('id="heroCountReviews"', stats_html)
        self.assertIn('id="heroCountCompliance"', stats_html)

    def test_compliance_pill_not_100_percent(self):
        """Task 9.5 (F1): Verify pill does not falsely claim 100% Halal & BPOM."""
        self.assertNotIn("100% Teranotasi", self.html)
        self.assertNotIn("100% Teranotasi Halal & BPOM", self.html)
        home = self._panel("tab-content-reputation")
        self.assertIn("Klaim Halal & BPOM", home)

    def test_one_fact_one_value_metrics_and_catalog(self):
        """Task 9.6 (F3): Verify single source of truth (no hardcoded mismatch 215/797, uses dynamic DOM hooks)."""
        self.assertNotIn("215 brand dan 797 produk", self.html)
        metrics_panel = self._panel("tab-content-metrics")
        self.assertIn("metricsDatasetBrandCount", metrics_panel)
        self.assertIn("metricsDatasetProductCount", metrics_panel)
        self.assertIn("metricsDatasetReviewCount", metrics_panel)


if __name__ == "__main__":
    unittest.main()

