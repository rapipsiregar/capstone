"""Verify that 'Simulasi XAI' (#/sandbox), inference history UI/DB, and Solusi C per-class evaluation table are properly applied."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"


def test_simulasi_xai_and_inference_history_completely_removed():
    html = (FRONTEND / "index.html").read_text(encoding="utf-8")
    assert "Simulasi XAI" not in html
    assert 'href="#/sandbox"' not in html
    assert 'data-nav="sandbox"' not in html
    assert 'data-view="sandbox"' not in html
    assert 'id="xai-sandbox-section"' not in html
    assert "sandbox.js" not in html
    assert "pagination.js" not in html
    assert "Riwayat inferensi" not in html
    assert 'id="historyTableBody"' not in html

    # Solusi C: Per-class evaluation table and confusion matrix exist in Metrik Skripsi
    assert 'id="perClassEvaluationPanel"' in html
    assert 'id="perClassMetricsBody"' in html
    assert 'id="confusionMatrixGrid"' in html


def test_sandbox_and_history_files_completely_deleted():
    assert not (FRONTEND / "js" / "sandbox.js").exists(), "frontend/js/sandbox.js must be deleted"
    assert not (FRONTEND / "js" / "pagination.js").exists(), "frontend/js/pagination.js must be deleted"
    assert not (ROOT / "backend" / "api" / "v1" / "history.py").exists(), "backend/api/v1/history.py must be deleted"
    assert not (ROOT / "backend" / "services" / "database.py").exists(), "backend/services/database.py must be deleted"
    assert not (ROOT / "data" / "history.db").exists(), "data/history.db must be deleted"

    router = (FRONTEND / "js" / "router.js").read_text(encoding="utf-8")
    assert "/sandbox" not in router
    assert "Simulasi XAI" not in router

    app = (FRONTEND / "js" / "app.js").read_text(encoding="utf-8")
    assert "bindSandboxEvents" not in app
    assert "charmViews.sandbox" not in app
    assert "renderHistoryWithPagination" not in app
    assert "bindPaginationEvents" not in app

    api = (FRONTEND / "js" / "api.js").read_text(encoding="utf-8")
    assert "fetchReviewHistory" not in api
    assert "requestPrediction" not in api
    assert "requestExplanation" not in api

