"""
Unit test for Task 10.6: Angka & Transisi (F16, F17).
Taste-skill compliance:
- Zero 'transition: all' in stylesheets (explicitly named properties like transform, opacity).
- Numeric alignment: Right-aligned numbers, amounts, and percentages with tabular-nums.
"""

from pathlib import Path
import re
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_CSS = REPO_ROOT / "frontend" / "css"

TRANSITION_ALL_PATTERN = re.compile(r"transition\s*:\s*all\b", re.IGNORECASE)


def test_zero_transition_all_in_css():
    """All frontend CSS files must contain zero 'transition: all' statements."""
    offending = []
    for css_file in FRONTEND_CSS.glob("*.css"):
        content = css_file.read_text(encoding="utf-8")
        matches = TRANSITION_ALL_PATTERN.findall(content)
        if matches:
            offending.append((css_file.name, len(matches)))

    assert not offending, f"Found transition: all in CSS: {offending}"


def test_tabular_nums_and_numeric_alignment_in_styles():
    """Verify font-variant-numeric: tabular-nums and num-col/num-cell right-alignment."""
    styles_css = (FRONTEND_CSS / "styles.css").read_text(encoding="utf-8")
    assert "tabular-nums" in styles_css, "font-variant-numeric: tabular-nums missing in styles.css"
    assert ".data-table th.num-col" in styles_css, "num-col header alignment rule missing"
    assert "text-align: right" in styles_css, "text-align: right for numeric cells missing"


def test_table_headers_and_cells_have_numeric_classes():
    """Verify index.html table headers and pagination.js cells use num-col/num-cell."""
    index_html = (REPO_ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
    pagination_js = (REPO_ROOT / "frontend" / "js" / "pagination.js").read_text(encoding="utf-8")

    assert '<th class="num-col">Confidence</th>' in index_html
    assert '<th class="num-col">Latensi</th>' in index_html
    assert 'class="num-cell"' in pagination_js
