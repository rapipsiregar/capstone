"""
Unit test for Task 10.6: Angka & Transisi (F16, F17).
Taste-skill compliance:
- Zero 'transition: all' in stylesheets (explicitly named properties like transform, opacity).
- Numeric alignment: Right-aligned numbers, amounts, and percentages with tabular-nums.
"""

from pathlib import Path
import re

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
    tokens_css = (FRONTEND_CSS / "tokens.css").read_text(encoding="utf-8")
    assert "tabular-nums" in tokens_css, "font-variant-numeric: tabular-nums missing in tokens.css"
    assert ".num-cell, .num-col" in tokens_css, "num-col / num-cell alignment rule missing"
    assert "text-align: right" in tokens_css, "text-align: right for numeric cells missing"


def test_table_headers_and_cells_have_numeric_classes():
    """Verify index.html table headers and charts.js cells use num-col/num-cell."""
    index_html = (REPO_ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
    charts_js = (REPO_ROOT / "frontend" / "js" / "charts.js").read_text(encoding="utf-8")

    assert '<th class="num-col">Precision</th>' in index_html
    assert '<th class="num-col">Recall</th>' in index_html
    assert '<th class="num-col">F1-Score</th>' in index_html
    assert 'class="num-cell"' in charts_js
