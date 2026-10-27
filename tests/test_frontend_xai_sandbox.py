import os
import pytest


def test_xai_sandbox_elements_exist_in_html():
    index_path = os.path.join(os.getcwd(), "frontend", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    assert 'id="xai-sandbox-section"' in html_content
    assert 'id="input-review-text"' in html_content
    assert 'class="model-badge-info"' in html_content
    assert 'id="btn-analyze-review"' in html_content
    assert 'id="xai-result-card"' in html_content
    assert 'id="xai-highlighted-text"' in html_content
    assert 'id="xai-summary-text"' in html_content
