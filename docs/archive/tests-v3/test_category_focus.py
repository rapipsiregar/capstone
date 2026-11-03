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
    """catalog.css or its imported modules must define :focus-visible with clear outline."""
    with open(CATALOG_CSS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    css_dir = os.path.dirname(CATALOG_CSS_PATH)
    for imported in re.findall(r"@import\s+(?:url\(['\"]?([^'\")]+)['\"]?\)|['\"]([^'\"]+)['\"]);", content):
        sub_file = imported[0] or imported[1]
        sub_path = os.path.join(css_dir, sub_file)
        if os.path.exists(sub_path):
            with open(sub_path, "r", encoding="utf-8") as sf:
                content += "\n" + sf.read()

    assert ".category-circle-item:focus-visible" in content, (
        "catalog stylesheets must define .category-circle-item:focus-visible"
    )
    assert "outline:" in content or "outline" in content


def test_rendered_categories_are_accessible_buttons():
    """catalog.js must render category items as <button type="button"> elements."""
    with open(CATALOG_JS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    assert '<button type="button" class="category-circle-item"' in content
