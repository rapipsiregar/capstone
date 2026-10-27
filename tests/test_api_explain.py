import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_explain_endpoint_success():
    payload = {
        "text": "Sertifikat halal jelas dari BPOM dan kandungannya aman tanpa alkohol.",
        "model_choice": "indobert"
    }
    response = client.post("/api/v1/explain", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "raw_text" in data
    assert "cleaned_text" in data
    assert "predicted_aspect" in data
    assert "predicted_trust" in data
    assert "trust_confidence" in data
    assert "tokens" in data
    assert "attributions" in data
    assert "explanation_summary" in data
    assert "execution_time_ms" in data

    assert len(data["attributions"]) > 0
    assert "highlight_color" in data["attributions"][0]
    assert data["execution_time_ms"] < 1500  # Benchmark < 1.5s


def test_explain_endpoint_invalid_input():
    payload = {"text": "hi"}  # Too short
    response = client.post("/api/v1/explain", json=payload)
    assert response.status_code == 422
