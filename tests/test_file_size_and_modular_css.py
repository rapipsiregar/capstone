"""
Unit test for Task 10.8: File Size Limits (AGENTS.md §3 <= 256 LOC) & Modular CSS Architecture.
Verifies:
1. Every code file (.py, .js, .css) in the repository is strictly <= 256 LOC.
2. The modular catalog CSS files exist and are all <= 256 LOC.
3. catalog.css acts as the modular entrypoint importing all 4 submodules.
"""

from pathlib import Path
import os
import re
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_CSS = REPO_ROOT / "frontend" / "css"

EXCLUDE_DIRS = {".venv", ".git", "node_modules", "__pycache__", ".taste-skill", ".agents"}


def test_all_repo_code_files_under_256_loc():
    """All code files in the repository must be <= 256 LOC per AGENTS.md §3."""
    oversized_files = []

    for root, dirs, files in os.walk(REPO_ROOT):
        # Skip excluded dirs
        if any(exc in root for exc in EXCLUDE_DIRS):
            continue
        for file_name in files:
            if file_name.endswith((".py", ".js", ".css")):
                file_path = Path(root) / file_name
                try:
                    lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
                    loc = len(lines)
                    if loc > 256:
                        oversized_files.append((str(file_path.relative_to(REPO_ROOT)), loc))
                except Exception as e:
                    oversized_files.append((str(file_path.relative_to(REPO_ROOT)), f"Error: {e}"))

    assert not oversized_files, f"Files exceeding 256 LOC: {oversized_files}"


def test_modular_catalog_css_files_exist_and_sized():
    """All split catalog CSS files must exist and be <= 256 LOC."""
    expected_modules = [
        "catalog-nav.css",
        "catalog-categories.css",
        "catalog-products.css",
        "catalog-reviews.css",
        "catalog.css",
    ]

    for mod in expected_modules:
        mod_path = FRONTEND_CSS / mod
        assert mod_path.exists(), f"Expected modular stylesheet {mod} not found"
        loc = len(mod_path.read_text(encoding="utf-8").splitlines())
        assert loc <= 256, f"{mod} exceeds 256 LOC ({loc} lines)"


def test_catalog_css_entrypoint_imports_all_modules():
    """catalog.css must import all sub-modules for backward compatibility."""
    catalog_css = (FRONTEND_CSS / "catalog.css").read_text(encoding="utf-8")
    for mod in ["catalog-nav.css", "catalog-categories.css", "catalog-products.css", "catalog-reviews.css"]:
        assert mod in catalog_css, f"Import for {mod} missing in catalog.css"
