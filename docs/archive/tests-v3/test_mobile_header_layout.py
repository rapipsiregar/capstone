"""
TDD Tests for Task 9.12: Mobile Header Layout (390px) Without Cutoff or Edge Bleed.
Verifies:
1. tabs.css and styles.css define media queries for mobile viewport (max-width: 480px / 600px).
2. brand-text p has white-space: normal on mobile viewports so long taglines wrap cleanly.
3. app-container has at least 1rem padding so text does not bleed to the device edge.
"""

import os
import re
import pytest

STYLES_CSS = os.path.join("frontend", "css", "styles.css")
TABS_CSS = os.path.join("frontend", "css", "tabs.css")


def test_styles_css_mobile_rules():
    """styles.css must provide mobile responsive rules for app-container and brand."""
    with open(STYLES_CSS, "r", encoding="utf-8") as f:
        content = f.read()

    assert "@media (max-width: 768px)" in content
    assert "@media (max-width: 480px)" in content
    assert ".app-container { padding: 1rem; }" in content or "padding: 1rem" in content


def test_tabs_css_mobile_header_rules():
    """tabs.css must allow brand-text p to wrap on mobile without edge bleed."""
    with open(TABS_CSS, "r", encoding="utf-8") as f:
        content = f.read()

    assert "@media (max-width: 480px)" in content
    assert "white-space: normal" in content
    assert ".btn-guidebook" in content
