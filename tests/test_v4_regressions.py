"""
V4 ports of the invariants from the archived V3 UI suites (docs/archive/tests-v3/).
Each test names the V3 suite whose guarantee it keeps.
"""

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONT = ROOT / "frontend"
HTML = (FRONT / "index.html").read_text(encoding="utf-8")


def _js(name):
    return (FRONT / "js" / name).read_text(encoding="utf-8")


def _css(name):
    return (FRONT / "css" / name).read_text(encoding="utf-8")


def _view(name):
    start = HTML.index(f'data-view="{name}"')
    end = HTML.find('<section class="view"', start)
    return HTML[start:end if end > 0 else len(HTML)]


def test_focus_visible_on_every_control():  # test_category_focus
    assert re.search(r":focus-visible\s*\{[^}]*outline:\s*2px solid", _css("tokens.css"))
    directory = _js("directory.js")
    assert 'type="checkbox"' in directory and "<label class=\"facet-option\"" in directory


def test_mobile_header_stacks_and_search_spans_width():  # test_mobile_header_layout
    shell = _css("shell.css")
    mobile = shell[shell.index("@media (max-width: 480px)"):]
    assert ".masthead" in mobile and ".search-pill" in mobile and "width: 100%" in mobile
    assert "@media (max-width: 768px)" in shell


def test_product_photos_are_real_files_or_honest_text():  # test_product_photos
    photos = [f for f in os.listdir(FRONT / "images" / "products") if f.endswith(".jpg")]
    assert len(photos) >= 10
    kit = _js("ui-kit.js")
    assert "photo-frame" in kit and "Foto belum tersedia" in kit
    assert re.search(r"\.photo-frame img\s*\{[^}]*object-fit:\s*contain", _css("catalog-views.css"))


def test_sticky_header_with_search_dropdown():  # test_fd_header_ui, test_catalog_search
    shell = _css("shell.css")
    assert re.search(r"\.masthead\s*\{[^}]*position:\s*sticky", shell, re.S)
    assert re.search(r"\.search-results\s*\{[^}]*position:\s*absolute[^}]*z-index:\s*200", shell, re.S)
    assert re.search(r"\.frame\s*\{[^}]*overflow:\s*visible", shell, re.S)
    search = _js("header-search.js")
    assert "setTimeout" in search and "Escape" in search and "ArrowDown" in search


def test_review_cards_show_shap_text_trust_and_advice():  # test_fd_review_cards_ui, test_review_browser_ui
    detail = _js("product-detail.js")
    for token in ["review-card", "highlighted_text", "trustPill", "umkm_recommendation", "trust_reason", "pagerHtml"]:
        assert token in detail
    assert "strategic_recommendation" not in detail
    assert 'id="reviewFeed"' in HTML and 'id="reviewPager"' in HTML


def test_product_summary_uses_all_reviews_of_the_product():  # test_product_summary_ui
    detail = _js("product-detail.js")
    for token in ["aspect_distribution", "trust_distribution", "high_trust_pct", "total_reviews"]:
        assert token in detail
    assert _view("detail").index('id="productDossier"') < _view("detail").index('id="reviewFeed"')


def test_homepage_is_the_catalog_and_analytics_live_in_insight():  # test_homepage_layout
    home = _view("directory")
    for absent in ['id="stat-total-reviews"', 'id="aspectChart"', 'id="rightSidebarAnalytics"']:
        assert absent not in home
    insight = _view("insight")
    for el in ["stat-total-reviews", "stat-high-trust", "stat-top-aspect", "aspectChart", "trustChart",
               "highTrustDriversList", "lowTrustDriversList", "halalComplianceProgressBar"]:
        assert f'id="{el}"' in insight
    assert 'id="reviewFeedContainer"' not in HTML and "100% Teranotasi" not in HTML
    metrics = _view("metrics")
    for el in ["metricsDatasetBrandCount", "metricsDatasetProductCount", "metricsDatasetReviewCount"]:
        assert el in metrics


def test_claim_badges_are_data_driven():  # test_homepage_layout, test_fd_design_system
    brand = _js("brand-products.js")
    assert "halal_claim" in brand and "bpom_claim" in brand
    kit = _js("ui-kit.js")
    assert "halalMentions > 0" in kit and "bpomMentions > 0" in kit
    tokens = _css("tokens.css")
    assert ".xai-highlight-green" in tokens and ".xai-highlight-red" in tokens

