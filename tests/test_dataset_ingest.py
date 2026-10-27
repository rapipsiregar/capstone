"""
Integration Tests for Dataset Ingestion REST API Endpoint.
"""

import unittest
from fastapi.testclient import TestClient
from backend.main import app

class TestDatasetIngestAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_post_dataset_ingest_endpoint(self):
        """Test POST /api/v1/dataset/ingest endpoint."""
        response = self.client.post("/api/v1/dataset/ingest")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data.get("status"), "success")
        self.assertIn("processed_records", data)
        self.assertGreater(data.get("processed_records", 0), 1000)
        self.assertIn("cleaned_csv_path", data)
        self.assertIn("annotated_csv_path", data)

if __name__ == "__main__":
    unittest.main()
