"""
Unit test for Task 10.3: Shadow & Blur Elimination.
Taste-skill compliance: Elements at rest carry no shadows (grounded via quiet borders
or neutral fills); zero backdrop blur. Only real overlays may carry shadows.
"""

from pathlib import Path
import re
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_CSS = REPO_ROOT / "frontend" / "css"

BACKDROP_PATTERN = re.compile(r"backdrop-filter\s*:\s*blur", re.IGNORECASE)


def test_zero_backdrop_blur_in_css():
    """All frontend CSS files must contain zero backdrop blur filters."""
    offending = []
    for css_file in FRONTEND_CSS.glob("*.css"):
        content = css_file.read_text(encoding="utf-8")
        matches = BACKDROP_PATTERN.findall(content)
        if matches:
            offending.append((css_file.name, len(matches)))

    assert not offending, f"Found backdrop-filter blur in CSS: {offending}"


def test_panels_at_rest_carry_no_heavy_shadows():
    """Panels and cards rest flat; only the real search overlay may carry a marked shadow."""
    for css_file in FRONTEND_CSS.glob("*.css"):
        for line in css_file.read_text(encoding="utf-8").splitlines():
            if "box-shadow" in line and "none" not in line:
                assert "taste-skill-ignore: real overlay" in line, f"resting shadow in {css_file.name}: {line.strip()}"