import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_get_history_endpoint():
    # Make a prediction first
    payload = {
        "text": "Produk ini bersertifikat halal resmi dari BPOM dan terjamin aman.",
        "model_choice": "indobert"
    }
    client.post("/api/v1/predict", json=payload)

    response = client.get("/api/v1/history?limit=10")
    assert response.status_code == 200

    data = response.json()
    assert "logs" in data
    assert "count" in data
    assert isinstance(data["logs"], list)


def test_get_analytics_endpoint():
    response = client.get("/api/v1/analytics")
    assert response.status_code == 200

    data = response.json()
    assert "total_reviews" in data
    assert "aspect_counts" in data
    assert "trust_counts" in data
    assert "avg_execution_time_ms" in data
