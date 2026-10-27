"""
Integration Tests for Brand & Category Analytics REST API Endpoint.
"""

import unittest
from fastapi.testclient import TestClient
from backend.main import app

class TestBrandAnalyticsAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_get_brand_analytics_endpoint(self):
        """Test GET /api/v1/analytics/brands endpoint."""
        response = self.client.get("/api/v1/analytics/brands")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data.get("status"), "success")
        self.assertIn("total_reviews", data)
        self.assertIn("total_brands", data)
        self.assertIn("brands_summary", data)
        
        brands = data.get("brands_summary", [])
        self.assertGreater(len(brands), 0)
        
        first_brand = brands[0]
        self.assertIn("brand_name", first_brand)
        self.assertIn("high_trust_ratio", first_brand)
        self.assertIn("top_aspect", first_brand)
        self.assertIn("aspect_distribution", first_brand)
        self.assertIn("products", first_brand)

    def test_get_brand_analytics_specific_brand(self):
        """Test GET /api/v1/analytics/brands with specific brand parameter."""
        response = self.client.get("/api/v1/analytics/brands?brand=Wardah")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("trust_drivers", data)
        drivers = data.get("trust_drivers", {})
        self.assertIn("high", drivers)
        self.assertIn("low", drivers)
        self.assertGreater(len(drivers["high"]), 0)
        self.assertGreater(len(drivers["low"]), 0)

        brands = data.get("brands_summary", [])
        self.assertEqual(len(brands), 1)
        self.assertEqual(brands[0]["brand_name"], "Wardah")
        self.assertIn("aspect_distribution", brands[0])
        self.assertIn("products", brands[0])


if __name__ == "__main__":
    unittest.main()

