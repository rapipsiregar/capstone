"""
Unit tests for Reviews Feed REST API Endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_get_reviews_feed_default():
    response = client.get("/api/v1/reviews/feed?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "total_dataset" in data
    assert "filtered_count" in data
    assert "reviews" in data
    assert len(data["reviews"]) == 5
    assert "brand" in data["reviews"][0]
    assert "product" in data["reviews"][0]
    assert "rating" in data["reviews"][0]
    assert "highlighted_text" in data["reviews"][0]


def test_get_reviews_feed_brand_filter():
    response = client.get("/api/v1/reviews/feed?brand=Wardah&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["filtered_count"] > 0
    for rev in data["reviews"]:
        assert "wardah" in rev["brand"].lower()


def test_get_reviews_feed_pagination():
    res1 = client.get("/api/v1/reviews/feed?limit=3&page=1")
    res2 = client.get("/api/v1/reviews/feed?limit=3&page=2")
    assert res1.status_code == 200
    assert res2.status_code == 200
    data1 = res1.json()
    data2 = res2.json()
    assert data1["reviews"][0]["id"] != data2["reviews"][0]["id"]
