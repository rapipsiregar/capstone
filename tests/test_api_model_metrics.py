"""
Unit tests for Model Evaluation Metrics REST API Endpoint.
Verifies authentic loading of indobert_evaluation_results.json, valid metric values,
and exact sample count matches (837 test samples).
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_get_model_metrics_endpoint():
    response = client.get("/api/v1/model/metrics")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert data["dataset_split"] == "test.csv"
    assert data["total_test_samples"] == 837

    # Verify trust classifier metrics
    assert "trust_classifier" in data
    trust = data["trust_classifier"]
    assert 0.70 <= trust["accuracy"] <= 1.0
    assert 0.70 <= trust["f1_macro"] <= 1.0
    assert trust["num_samples"] == 837

    # Verify aspect classifier metrics
    assert "aspect_classifier" in data
    aspect = data["aspect_classifier"]
    assert 0.85 <= aspect["accuracy"] <= 1.0
    assert 0.80 <= aspect["f1_macro"] <= 1.0
    assert aspect["num_samples"] == 837
