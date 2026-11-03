"""
TDD tests for Solusi 2 & Solusi 4:
- Solusi 2: Brand cards, product cards, product dossier, and sidebar filters highlight
  consumer trust sources (High Trust % and dominant communication aspect) instead of
  "Halal/BPOM disebut N ulasan".
- Solusi 4: Insight Reputasi right sidebar replaces "Klaim halal dan BPOM di ulasan (6.2%)"
  with "Peta faktor pembentuk kepercayaan" (#trustFactorMapPanel / #trustFactorMapList).
"""

from pathlib import Path
from fastapi.testclient import TestClient
from backend.main import app

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
client = TestClient(app)


def test_api_brands_and_products_expose_top_aspect_and_high_trust_facets():
    res = client.get("/api/v1/catalog/brands", params={"limit": 5})
    assert res.status_code == 200
    data = res.json()
    first = data["brands"][0]
    assert "high_trust_pct" in first
    assert "top_aspect" in first and first["top_aspect"]
    assert "aspects" in data["facets"] and len(data["facets"]["aspects"]) >= 1
    assert "high_trust_brands" in data["facets"]

    # Filter by high_trust=true
    ht = client.get("/api/v1/catalog/brands", params={"high_trust": "true", "limit": 50}).json()
    assert ht["total_brands"] == data["facets"]["high_trust_brands"]
    assert all(b["high_trust_pct"] >= 50.0 for b in ht["brands"])

    # Filter by aspect
    aspect_key = data["facets"]["aspects"][0]["aspect_key"]
    asp = client.get("/api/v1/catalog/brands", params={"aspect": aspect_key, "limit": 50}).json()
    assert asp["total_brands"] > 0
    assert all(b["top_aspect"] == aspect_key for b in asp["brands"])

    # Products endpoint includes high_trust_pct and top_aspect and supports aspect/high_trust filters
    prods = client.get("/api/v1/catalog/products", params={"brand": "Wardah", "high_trust": "true"}).json()
    assert all(p["high_trust_pct"] >= 50.0 for p in prods["products"])
    assert all("top_aspect" in p and p["top_aspect"] for p in prods["products"])


def test_solusi_2_catalog_ui_highlights_trust_sources_not_claim_mentions():
    directory_js = (FRONTEND / "js" / "directory.js").read_text(encoding="utf-8")
    brand_js = (FRONTEND / "js" / "brand-products.js").read_text(encoding="utf-8")
    detail_js = (FRONTEND / "js" / "product-detail.js").read_text(encoding="utf-8")
    ui_kit_js = (FRONTEND / "js" / "ui-kit.js").read_text(encoding="utf-8")

    assert "trustSourcePills" in ui_kit_js
    assert "Kepercayaan Tinggi" in ui_kit_js
    assert "Unggul di:" in ui_kit_js

    # Directory & Brand pages use Aspek pembentuk kepercayaan & Tingkat kepercayaan facets
    assert "Aspek pembentuk kepercayaan" in directory_js
    assert "Kepercayaan Tinggi" in directory_js
    assert "Halal disebut" not in directory_js
    assert "BPOM disebut" not in directory_js

    assert "Aspek pembentuk kepercayaan" in brand_js
    assert "Kepercayaan Tinggi" in brand_js
    assert "Halal disebut" not in brand_js
    assert "BPOM disebut" not in brand_js

    # Product detail dossier uses trustSourcePills instead of claim mention pills
    assert "trustSourcePills" in detail_js
    assert "Klaim halal disebut di ulasan" not in detail_js


def test_solusi_4_insight_sidebar_shows_trust_factor_map():
    html = (FRONTEND / "index.html").read_text(encoding="utf-8")
    app_js = (FRONTEND / "js" / "app.js").read_text(encoding="utf-8")

    assert 'id="trustFactorMapPanel"' in html
    assert 'id="trustFactorMapList"' in html
    assert 'id="factorMapReviewCount"' in html
    assert "Peta faktor pembentuk kepercayaan" in html
    assert 'id="halalComplianceProgressBar"' not in html
    assert "Klaim halal dan BPOM di ulasan" not in html

    assert "renderTrustFactorMap" in app_js
    assert "trustFactorMapList" in app_js

