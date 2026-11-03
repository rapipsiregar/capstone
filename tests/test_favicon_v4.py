"""
Task 9.3: favicon V4 "3D Glossy Rose Serum" (Konsep D, Blossom Gloss master icon).
User decision 2026-11-03: glossy gradients allowed for the favicon only; no dashed lines, no dark colours.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAVICON = ROOT / "frontend" / "favicon.svg"
INDEX = ROOT / "frontend" / "index.html"
PALETTE = {"#FCF8F8", "#FBEFEF", "#F9DFDF", "#F5AFAF"}


def _svg():
    return FAVICON.read_text(encoding="utf-8")


def test_favicon_is_valid_square_svg():
    svg = _svg()
    assert svg.lstrip().startswith("<svg")
    assert 'viewBox="0 0 100 100"' in svg
    assert "<title>CHARM</title>" in svg


def test_favicon_uses_the_four_palette_colours_in_glossy_gradients():
    svg = _svg().upper()
    for colour in PALETTE:
        assert colour in svg, f"{colour} missing from favicon"
    assert svg.count("<LINEARGRADIENT") >= 2 and "<RADIALGRADIENT" in svg
    assert 'ID="SPECULAR"' in svg, "specular highlight gradient expected for the glossy look"


def test_favicon_has_no_dashed_lines_and_no_dark_colours():
    svg = _svg()
    assert "stroke-dasharray" not in svg
    for hex_code in re.findall(r"#[0-9A-Fa-f]{6}", svg):
        r, g, b = (int(hex_code[i:i + 2], 16) for i in (1, 3, 5))
        lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
        assert lum >= 150, f"dark colour {hex_code} not allowed in the V4 favicon"


def test_index_uses_v4_favicon_in_tab_and_header():
    html = INDEX.read_text(encoding="utf-8")
    assert re.search(r'<link rel="icon" type="image/svg\+xml" href="\./favicon\.svg\?v=4">', html)
    assert '<img src="./favicon.svg?v=4"' in html

