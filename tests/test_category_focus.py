"""
TDD Tests for Task 9.10: Visible Focus Indicators for 23 Category Buttons.
Verifies:
1. CSS defines visible focus-visible outline for .category-circle-item.
2. Rendered category items in catalog.js are accessible button elements.
"""

import os
import re
import pytest

CATALOG_CSS_PATH = os.path.join("frontend", "css", "catalog.css")
CATALOG_JS_PATH = os.path.join("frontend", "js", "catalog.js")


def test_category_items_have_focus_visible_styling():
    """catalog.css must define :focus-visible with clear outline for .category-circle-item."""
    with open(CATALOG_CSS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    assert ".category-circle-item:focus-visible" in content, (
        "catalog.css must define .category-circle-item:focus-visible"
    )
    assert "outline:" in content or "outline" in content


def test_rendered_categories_are_accessible_buttons():
    """catalog.js must render category items as <button type="button"> elements."""
    with open(CATALOG_JS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    assert '<button type="button" class="category-circle-item"' in content
