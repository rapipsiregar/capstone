"""
Unit test for Task 10.2: Eyebrow & Gradient elimination.
Taste-skill compliance: No gradient fills in UI backgrounds, and no micro-labels
(uppercase + wide letter-spacing badges).
"""

from pathlib import Path
import re
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_CSS = REPO_ROOT / "frontend" / "css"

GRADIENT_PATTERN = re.compile(r"(linear-gradient|radial-gradient|conic-gradient)\s*\(", re.IGNORECASE)


def test_zero_gradients_in_css():
    """All CSS files in frontend/css must contain zero gradient declarations."""
    offending = []
    for css_file in FRONTEND_CSS.glob("*.css"):
        content = css_file.read_text(encoding="utf-8")
        matches = GRADIENT_PATTERN.findall(content)
        if matches:
            offending.append((css_file.name, len(matches)))

    assert not offending, f"Found gradients in CSS files: {offending}"


def test_hero_editorial_badge_no_microlabel():
    """V4 labels use sentence case: no uppercase letter-spaced micro-labels in any stylesheet."""
    for css_file in FRONTEND_CSS.glob("*.css"):
        content = css_file.read_text(encoding="utf-8")
        assert "text-transform: uppercase" not in content, f"micro-label uppercase in {css_file.name}"
        assert "letter-spacing: 0.06em" not in content, f"micro-label letter-spacing in {css_file.name}"