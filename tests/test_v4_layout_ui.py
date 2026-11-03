"""
V4 Rose Blush layout contract (mockup V4 halaman 2-4, DESIGN.md sections 2-5).
Static checks on the shipped frontend files; the rendered checks live in the inspector runs.
"""

import re
from pathlib import Path

FRONT = Path(__file__).resolve().parent.parent / "frontend"
HTML = (FRONT / "index.html").read_text(encoding="utf-8")


def _js(name):
    return (FRONT / "js" / name).read_text(encoding="utf-8")


def _css(name):
    return (FRONT / "css" / name).read_text(encoding="utf-8")


def test_symmetric_header_breadcrumb_brand_search():
    header = HTML[HTML.index('<header class="masthead"'):HTML.index("</header>")]
    assert header.index('id="crumbs"') < header.index('class="brandmark"') < header.index('id="headerSearch"')
    assert "CHARM" in header


def test_guide_nav_links_to_hash_routes():
    for route in ['href="#/"', 'href="#/insight"', 'href="#/metrics"']:
        assert route in HTML
    assert 'href="#/sandbox"' not in HTML


def test_unified_l_frame_with_facets_and_sheet():
    assert 'class="frame"' in HTML and 'id="frameBody"' in HTML
    assert 'id="facetPanel"' in HTML and 'class="sheet"' in HTML
    for view in ["directory", "brand", "detail", "insight", "metrics"]:
        assert f'data-view="{view}"' in HTML
    assert 'data-view="sandbox"' not in HTML


def test_router_declares_v4_routes():
    router = _js("router.js")
    for path in ["'/'", "'/brand/products'", "'/product/detail'", "'/insight'", "'/metrics'"]:
        assert path in router
    assert "'/sandbox'" not in router
    assert "hashchange" in router


def test_tokens_declare_palette_and_text_roles():
    tokens = _css("tokens.css").upper()
    for hex_code in ["#FCF8F8", "#FBEFEF", "#F9DFDF", "#F5AFAF", "#3D2228", "#75545A", "#A84A58", "#1E6B47"]:
        assert hex_code in tokens


def test_v4_palette_used_by_surfaces():
    shell = _css("shell.css")
    assert re.search(r"\.masthead\s*\{[^}]*background:\s*var\(--blush-400\)", shell, re.S)
    assert re.search(r"\.frame\s*\{[^}]*background:\s*var\(--blush-100\)", shell, re.S)
    assert re.search(r"\.sheet\s*\{[^}]*background:\s*var\(--blush-50\)", shell, re.S)
    assert "var(--blush-200)" in shell


def test_index_has_no_hardcoded_dataset_numbers():
    text = re.sub(r"<[^>]+>", " ", HTML)
    for literal in ["216", "801", "8.365", "8365", "23 kategori"]:
        assert literal not in text, f"hardcoded dataset value {literal} in index.html"


def test_catalog_views_load_everything_from_the_api():
    assert "/catalog/brands?" in _js("directory.js")
    brand = _js("brand-products.js")
    assert "/catalog/brand-profile?brand=" in brand and "/catalog/products?" in brand
    assert "/catalog/reviews?product_name=" in _js("product-detail.js")
    search = _js("header-search.js")
    assert "/catalog/brands?search=" in search and "/catalog/products?search=" in search


def test_product_cards_are_links_without_repeated_buttons():
    brand = _js("brand-products.js")
    card = brand[brand.index("function productCard"):brand.index("async function render")]
    assert '<a class="product-card"' in card
    assert "<button" not in card


def test_honest_photo_placeholder_and_claim_wording():
    kit = _js("ui-kit.js")
    assert "Foto belum tersedia" in kit
    assert "Kepercayaan Tinggi" in kit
    for js in ["directory.js", "brand-products.js", "product-detail.js", "ui-kit.js"]:
        assert "MUI Verified" not in _js(js) and "Terverifikasi Halal" not in _js(js)


def test_states_name_cause_and_next_step():
    for js in ["directory.js", "brand-products.js", "product-detail.js"]:
        src = _js(js)
        assert "stateBox('loading'" in src and "stateBox('error'" in src and "stateBox('empty'" in src


def test_no_invented_fallback_numbers_in_guidebook_scripts():
    app = _js("app.js")
    assert "0.48" not in app and "0.28" not in app and "* 0.5" not in app
    assert "raw_text: \"" not in _js("api.js")
    assert "0.942" not in _js("charts.js")

