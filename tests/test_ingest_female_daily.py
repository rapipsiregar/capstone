"""
Unit & Integration Tests for Female Daily Dataset Ingestion & Validation Pipeline.
"""

import os
import unittest
import pandas as pd
from backend.services.ingest_female_daily import (
    validate_female_daily_schema,
    clean_female_daily_reviews,
    ingest_female_daily_pipeline
)

class TestFemaleDailyIngestionPipeline(unittest.TestCase):

    def setUp(self):
        self.raw_data_path = os.path.join("data", "raw", "female_daily_skincare_reviews_raw.csv")
        self.cleaned_output_path = os.path.join("data", "cleaned", "female_daily_skincare_cleaned.csv")
        
        # Sample raw dataframe for testing schema validation
        self.sample_raw_df = pd.DataFrame([
            {
                "Merk": "Wardah",
                "Category": "Night Cream",
                "Product": "Wardah Lightening Night Cream",
                "Rating": 5,
                "Recommend": "Recommends this product",
                "Review": "Produk ini beneran bagus bgt, melembabkan & terdaftar BPOM halal!",
                "UserName": "TestUser1",
                "SkinCond_Age": "Oily, 20-24 years old",
                "PostDate": "12 May 2020",
                "Price": "Rp 45.000",
                "OverallRating": 4.2,
                "Reviewer": 800
            },
            {
                "Merk": "Emina",
                "Category": "Sun Protection",
                "Product": "Emina Sun Battle SPF 30",
                "Rating": 1,
                "Recommend": "Does not recommend",
                "Review": "Bikin kulit breakout parah n bruntusan ga cocok bgt!",
                "UserName": "TestUser2",
                "SkinCond_Age": "Sensitive, 15-18 years old",
                "PostDate": "15 Jun 2021",
                "Price": "Rp 30.000",
                "OverallRating": 3.8,
                "Reviewer": 500
            }
        ])

    def test_validate_female_daily_schema(self):
        """Test schema validation function."""
        is_valid, report = validate_female_daily_schema(self.sample_raw_df)
        self.assertTrue(is_valid)
        self.assertEqual(report["total_rows"], 2)
        self.assertIn("Merk", report["columns"])
        self.assertIn("Review", report["columns"])

    def test_clean_female_daily_reviews(self):
        """Test text cleaning and sentiment label mapping."""
        cleaned_df = clean_female_daily_reviews(self.sample_raw_df)
        self.assertIn("teks_ulasan_bersih", cleaned_df.columns)
        self.assertIn("label_sentimen", cleaned_df.columns)
        self.assertEqual(cleaned_df.iloc[0]["label_sentimen"], "Positif")
        self.assertEqual(cleaned_df.iloc[1]["label_sentimen"], "Negatif")
        self.assertNotIn("bgt", cleaned_df.iloc[0]["teks_ulasan_bersih"]) # slang 'bgt' converted to 'banget'

    def test_ingest_female_daily_pipeline_execution(self):
        """Test full pipeline execution on raw file."""
        if os.path.exists(self.raw_data_path):
            cleaned_path, record_count = ingest_female_daily_pipeline(
                raw_csv_path=self.raw_data_path,
                output_csv_path=self.cleaned_output_path
            )
            self.assertTrue(os.path.exists(cleaned_path))
            self.assertGreater(record_count, 1000)

if __name__ == "__main__":
    unittest.main()
