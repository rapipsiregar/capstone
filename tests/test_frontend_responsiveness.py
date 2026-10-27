import os
import pytest


def test_responsive_viewport_meta():
    index_path = os.path.join(os.getcwd(), "frontend", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    assert '<meta name="viewport" content="width=device-width, initial-scale=1.0">' in html
    assert 'aria-label=' in html or 'role=' in html


def test_responsive_css_media_queries():
    css_path = os.path.join(os.getcwd(), "frontend", "css", "styles.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    assert "@media" in css
    assert "max-width: 768px" in css
    assert "max-width: 480px" in css
    assert "overflow-x: auto" in css
