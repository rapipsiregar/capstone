import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_predict_endpoint_indobert():
    payload = {
        "text": "Sertifikat halal produk Wardah ini jelas dan sudah terdaftar BPOM resmi.",
        "model_choice": "indobert"
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "raw_text" in data
    assert "cleaned_text" in data
    assert "predicted_aspect" in data
    assert "aspect_confidence" in data
    assert "predicted_trust" in data
    assert "trust_confidence" in data
    assert "model_type" in data
    assert "execution_time_ms" in data
    assert data["execution_time_ms"] < 1500  # Benchmark < 1.5s


def test_predict_endpoint_default_model():
    payload = {
        "text": "Teksturnya ringan dan terasa aman tanpa paraben."
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["predicted_aspect"] is not None
    assert data["predicted_trust"] is not None
    assert "IndoBERT" in data["model_type"]


def test_predict_endpoint_invalid_input():
    payload = {"text": "a"}  # Too short
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 422  # Validation Error
