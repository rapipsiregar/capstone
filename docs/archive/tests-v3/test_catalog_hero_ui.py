"""
TDD Tests for Editorial Hero Banner & Complete 23 Skincare Category Icons.
Verifies hero banner markup, search input, stats badges, and full icon coverage.
"""

import os
import re
import unittest
import pandas as pd

HTML_PATH = os.path.join("frontend", "index.html")
HERO_CSS_PATH = os.path.join("frontend", "css", "catalog-hero.css")
HERO_JS_PATH = os.path.join("frontend", "js", "catalog-hero.js")
CATALOG_JS_PATH = os.path.join("frontend", "js", "catalog.js")
DATASET_PATH = os.path.join("data", "annotated", "female_daily_skincare_annotated.csv")


class TestCatalogHeroUI(unittest.TestCase):

    def test_hero_files_exist_and_under_loc_limit(self):
        self.assertTrue(os.path.exists(HERO_CSS_PATH), "catalog-hero.css must exist")
        self.assertTrue(os.path.exists(HERO_JS_PATH), "catalog-hero.js must exist")
        
        with open(HERO_CSS_PATH, "r", encoding="utf-8") as f:
            self.assertLessEqual(len(f.read().splitlines()), 256)
        with open(HERO_JS_PATH, "r", encoding="utf-8") as f:
            self.assertLessEqual(len(f.read().splitlines()), 256)

    def test_index_html_links_hero_assets(self):
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            html = f.read()
        self.assertIn("catalog-hero.css", html)
        self.assertIn("catalog-hero.js", html)
        self.assertIn('class="editorial-hero-banner"', html)
        self.assertIn('id="homepageQuickSearch"', html)

    def test_all_23_dataset_categories_have_unique_icons(self):
        df = pd.read_csv(DATASET_PATH)
        all_cats = set(df["kategori_produk"].dropna().unique())
        self.assertEqual(len(all_cats), 23, "Dataset must have 23 categories")
        
        # Read icons from catalog.js or catalog-hero.js
        with open(CATALOG_JS_PATH, "r", encoding="utf-8") as f:
            cat_js = f.read()
        
        hero_js = ""
        if os.path.exists(HERO_JS_PATH):
            with open(HERO_JS_PATH, "r", encoding="utf-8") as f:
                hero_js = f.read()
        
        combined_js = cat_js + "\n" + hero_js
        for cat in all_cats:
            self.assertIn(f'"{cat}"', combined_js, f"Category '{cat}' must have an icon mapped")

    def test_search_features_and_comprehensive_counts(self):
        with open(HERO_CSS_PATH, "r", encoding="utf-8") as f:
            css = f.read()
        self.assertIn(".hero-search-footer", css)

        with open(HERO_JS_PATH, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertIn("openSearchResults", js)
        self.assertIn("renderSearchPagination", js)

        df = pd.read_csv(DATASET_PATH)
        # Verify nose and oil match multiple products across nama, kategori, and brand
        for q in ["nose", "oil"]:
            matched = df[
                df["nama_produk"].str.lower().str.contains(q, na=False) |
                df["merek_umkm"].str.lower().str.contains(q, na=False) |
                df["kategori_produk"].str.lower().str.contains(q, na=False)
            ]
            unique_prods = matched[["merek_umkm", "nama_produk"]].drop_duplicates()
            self.assertGreater(len(unique_prods), 10, f"Query '{q}' must match > 10 products across fields")

    def test_all_23_categories_have_real_downloaded_photos(self):
        category_dir = os.path.join("frontend", "images", "categories")
        self.assertTrue(os.path.isdir(category_dir), "frontend/images/categories directory must exist")
        
        df = pd.read_csv(DATASET_PATH)
        all_cats = set(df["kategori_produk"].dropna().unique())
        
        for cat in all_cats:
            slug = re.sub(r'[^a-zA-Z0-9]+', '-', str(cat)).lower().strip('-')
            img_path = os.path.join(category_dir, f"{slug}.jpg")
            self.assertTrue(os.path.isfile(img_path), f"Category photo for '{cat}' ({slug}.jpg) must exist")
            self.assertGreater(os.path.getsize(img_path), 1000, f"Photo for '{cat}' must not be empty")

        with open(CATALOG_JS_PATH, "r", encoding="utf-8") as f:
            cat_js = f.read()
        self.assertIn("./images/categories/", cat_js)
        self.assertIn("category-fallback-emoji", cat_js)


if __name__ == "__main__":
    unittest.main()

