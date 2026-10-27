"""
Integration Tests for Export Summary REST API Endpoint.
"""

import unittest
from fastapi.testclient import TestClient
from backend.main import app

class TestExportSummaryAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_get_export_summary_json(self):
        """Test GET /api/v1/export/summary?format=json endpoint."""
        response = self.client.get("/api/v1/export/summary?format=json")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data.get("status"), "success")
        self.assertIn("report_title", data)
        self.assertIn("top_high_trust_brands", data)
        self.assertIn("model_performance", data)

    def test_get_export_summary_csv(self):
        """Test GET /api/v1/export/summary?format=csv endpoint."""
        response = self.client.get("/api/v1/export/summary?format=csv")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response.headers.get("content-type", ""))
        self.assertIn("attachment", response.headers.get("content-disposition", ""))

if __name__ == "__main__":
    unittest.main()
