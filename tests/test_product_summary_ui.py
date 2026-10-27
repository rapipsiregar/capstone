"""
TDD tests for Task 6.5 frontend: per-product KPI + 2 pie charts on Level 3.
"""

import os
import unittest

HTML = os.path.join("frontend", "index.html")
JS = os.path.join("frontend", "js", "catalog-summary.js")
CSS = os.path.join("frontend", "css", "catalog-summary.css")
CATALOG_JS = os.path.join("frontend", "js", "catalog.js")


def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class TestProductSummaryUI(unittest.TestCase):

    def test_files_exist_and_are_linked(self):
        self.assertTrue(os.path.exists(JS))
        self.assertTrue(os.path.exists(CSS))
        html = _read(HTML)
        self.assertIn("./js/catalog-summary.js", html)
        self.assertIn("./css/catalog-summary.css", html)
        self.assertLess(html.index("catalog-summary.js"), html.index("./js/catalog.js"))

    def test_summary_container_sits_between_hero_and_feed(self):
        html = _read(HTML)
        hero = html.index('id="productHeroContainer"')
        summary = html.index('id="productSummaryContainer"')
        feed = html.index('id="catalogReviewsFeed"')
        self.assertTrue(hero < summary < feed)

    def test_charts_use_unique_ids_and_are_destroyed(self):
        js = _read(JS)
        self.assertIn("productAspectChart", js)
        self.assertIn("productTrustChart", js)
        self.assertIn(".destroy()", js)
        self.assertIn("ulasan", js)

    def test_values_come_from_api_not_hardcoded(self):
        js = _read(JS)
        for field in ("aspect_distribution", "trust_distribution", "high_trust_pct", "dominant_aspects"):
            self.assertIn(field, js)
        for literal in ("Klaim_Efikasi_Manfaat", "Sertifikasi_Halal_BPOM", "Transparansi_Layanan_Harga"):
            self.assertNotIn(literal, js)

    def test_catalog_js_triggers_summary_render(self):
        self.assertIn("catalogSummary", _read(CATALOG_JS))

    def test_files_within_loc_limit(self):
        for path in (JS, CSS):
            self.assertLessEqual(len(_read(path).splitlines()), 256)


if __name__ == "__main__":
    unittest.main()
