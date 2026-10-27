"""
Unit and Integration Tests for Dynamic Catalog & 3-Level Drill-Down REST API.
Verifies dynamic categories, product listings, and product-specific reviews.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_get_catalog_categories_endpoint():
    """Test GET /api/v1/catalog/categories returns authentic dynamic categories."""
    response = client.get("/api/v1/catalog/categories")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "categories" in data
    assert len(data["categories"]) >= 20  # Dataset has 23 categories
    
    # Check category structure
    first_cat = data["categories"][0]
    assert "category_name" in first_cat
    assert "product_count" in first_cat
    assert "review_count" in first_cat
    assert "avg_rating" in first_cat
    assert first_cat["review_count"] > 0
    assert first_cat["product_count"] > 0


def test_get_catalog_products_for_category():
    """Test GET /api/v1/catalog/products?category=Night Cream returns products."""
    response = client.get("/api/v1/catalog/products?category=Night Cream")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["category"] == "Night Cream"
    assert "products" in data
    assert len(data["products"]) > 0
    
    # Check product structure
    first_prod = data["products"][0]
    assert "product_name" in first_prod
    assert "brand_name" in first_prod
    assert "category_name" in first_prod
    assert "review_count" in first_prod
    assert "avg_rating" in first_prod


def test_get_catalog_reviews_for_product():
    """Test GET /api/v1/catalog/reviews?product_name=Perfect 3D Gel returns product reviews + XAI."""
    response = client.get("/api/v1/catalog/reviews?product_name=Perfect 3D Gel")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "reviews" in data
    assert len(data["reviews"]) > 0
    assert "product_info" in data
    
    # Check XAI explanation in review
    first_rev = data["reviews"][0]
    assert "xai_explanation" in first_rev
    assert "trust_reason" in first_rev["xai_explanation"]
    assert "suitable_skin_types" in first_rev["xai_explanation"]


def test_get_catalog_products_global_search():
    """Test GET /api/v1/catalog/products?search=Wardah searches across all categories."""
    response = client.get("/api/v1/catalog/products?search=Wardah&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "products" in data
    assert len(data["products"]) > 0
    # Every returned product must belong to Wardah
    for prod in data["products"]:
        assert "wardah" in prod["brand_name"].lower() or "wardah" in prod["product_name"].lower()

