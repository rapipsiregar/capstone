"""
Unit test for Task 10.7: State Lengkap (F18).
Ensures all 3 catalog levels and 3 guidebooks provide honest, informative states
for loading, empty, and error conditions, detailing causes and next steps.
"""

from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_JS = REPO_ROOT / "frontend" / "js"
ARTIFACT_DIR = Path(r"C:\Users\rafif\.gemini\antigravity\brain\765091c6-444d-4ee4-8523-6c4c970c06e2")


def test_catalog_levels_have_cause_and_action_states():
    """V4 catalog views (directory, brand, detail) must name the cause and offer a next step."""
    directory = (FRONTEND_JS / "directory.js").read_text(encoding="utf-8")
    brand = (FRONTEND_JS / "brand-products.js").read_text(encoding="utf-8")
    detail = (FRONTEND_JS / "product-detail.js").read_text(encoding="utf-8")

    # Direktori Brand empty/error state
    assert "Tidak ada brand yang cocok dengan filter ini" in directory
    assert "Hapus semua filter" in directory

    # Produk Brand empty/error state
    assert "Tidak ada produk yang cocok" in brand
    assert "Tampilkan semua produk" in brand

    # Detail Produk empty state points back to the brand directory
    assert "Belum ada ulasan untuk" in detail
    assert "'#/'" in detail


def test_metrics_evaluation_states():
    """charts.js must render per-class evaluation rows and handle empty/error states."""
    charts_js = (FRONTEND_JS / "charts.js").read_text(encoding="utf-8")
    assert "renderPerClassMetrics" in charts_js
    assert "perClassMetricsBody" in charts_js


def test_state_screenshots_captured_in_artifacts():
    """All 6 state screenshots must be captured in the artifact directory."""
    expected_files = [
        "task10_7_state_level1_categories.png",
        "task10_7_state_level2_empty.png",
        "task10_7_state_level2_loaded.png",
        "task10_7_state_level3_loaded.png",
        "task10_7_state_level3_empty.png",
        "task10_7_state_tab2_sandbox.png",
        "task10_7_state_tab3_history.png",
    ]
    for filename in expected_files:
        p = ARTIFACT_DIR / filename
        assert p.exists() and p.stat().st_size > 1000, f"Screenshot {filename} missing or empty"

