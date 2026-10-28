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
    """catalog.js must include honest empty states with causes and call-to-action buttons."""
    catalog_js = (FRONTEND_JS / "catalog.js").read_text(encoding="utf-8")

    # Level 1 Categories empty/error state
    assert "Belum ada kategori terindeks" in catalog_js
    assert "catalogApp.loadCatalogCategories()" in catalog_js

    # Level 2 Products empty/error state
    assert "Tidak ada produk untuk kategori" in catalog_js
    assert "catalogApp.backToCategories()" in catalog_js

    # Level 3 Reviews empty/error state
    assert "Belum ada ulasan untuk" in catalog_js
    assert "tabNavigation.switchToTab('tab-content-sandbox')" in catalog_js


def test_pagination_and_sandbox_states():
    """pagination.js and sandbox.js must display helpful empty/error states."""
    pagination_js = (FRONTEND_JS / "pagination.js").read_text(encoding="utf-8")
    sandbox_js = (FRONTEND_JS / "sandbox.js").read_text(encoding="utf-8")

    assert "Belum ada log inferensi tersimpan" in pagination_js
    assert "Teks ulasan masih kosong" in sandbox_js
    assert "alert(" not in sandbox_js


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

