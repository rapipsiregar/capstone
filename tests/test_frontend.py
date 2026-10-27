import os
import pytest


def test_frontend_files_exist():
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    assert os.path.exists(os.path.join(frontend_dir, "index.html"))
    assert os.path.exists(os.path.join(frontend_dir, "css", "styles.css"))
    assert os.path.exists(os.path.join(frontend_dir, "js", "api.js"))
    assert os.path.exists(os.path.join(frontend_dir, "js", "charts.js"))
    assert os.path.exists(os.path.join(frontend_dir, "js", "app.js"))


def test_index_html_contains_essential_ids():
    index_path = os.path.join(os.getcwd(), "frontend", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    assert 'id="stat-total-reviews"' in html_content
    assert 'id="stat-high-trust"' in html_content
    assert 'id="stat-top-aspect"' in html_content
    assert 'id="aspectChart"' in html_content
    assert 'id="trustChart"' in html_content
    assert 'id="comparisonChart"' in html_content
    assert 'id="historyTableBody"' in html_content
