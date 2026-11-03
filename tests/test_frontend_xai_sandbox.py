"""Verify that the 'Simulasi XAI' (#/sandbox) tab, route, DOM view, and JS module are completely removed."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"


def test_simulasi_xai_tab_and_view_completely_removed_from_html():
    html = (FRONTEND / "index.html").read_text(encoding="utf-8")
    assert "Simulasi XAI" not in html
    assert 'href="#/sandbox"' not in html
    assert 'data-nav="sandbox"' not in html
    assert 'data-view="sandbox"' not in html
    assert 'id="xai-sandbox-section"' not in html
    assert "sandbox.js" not in html


def test_sandbox_js_file_and_route_completely_removed():
    assert not (FRONTEND / "js" / "sandbox.js").exists(), "frontend/js/sandbox.js must be deleted"
    router = (FRONTEND / "js" / "router.js").read_text(encoding="utf-8")
    assert "/sandbox" not in router
    assert "Simulasi XAI" not in router
    app = (FRONTEND / "js" / "app.js").read_text(encoding="utf-8")
    assert "bindSandboxEvents" not in app
    assert "charmViews.sandbox" not in app
