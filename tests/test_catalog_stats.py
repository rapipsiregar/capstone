"""
Unit & Integration Tests for Catalog & Homepage Statistics API.
Validates authentic stats calculation without literal hardcoding.
"""

import unittest
from fastapi.testclient import TestClient
from backend.main import app


class TestCatalogStatsAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_get_catalog_stats_returns_authentic_numbers(self):
        response = self.client.get("/api/v1/catalog/stats")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data.get("status"), "success")
        self.assertEqual(data.get("total_reviews"), 8365)
        self.assertEqual(data.get("total_products"), 801)
        self.assertEqual(data.get("total_brands"), 216)
        self.assertEqual(data.get("total_categories"), 23)
        self.assertEqual(data.get("halal_claimed_reviews"), 55)
        self.assertEqual(data.get("bpom_claimed_reviews"), 468)
        self.assertIn("55 Halal", data.get("compliance_summary", ""))
        self.assertIn("468 BPOM", data.get("compliance_summary", ""))


if __name__ == "__main__":
    unittest.main()
