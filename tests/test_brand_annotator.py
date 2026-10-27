"""
Unit & Integration Tests for Brand-Specific Halal Entity & Aspect Annotator Service.
"""

import os
import unittest
import pandas as pd
from backend.services.brand_annotator import (
    extract_brand_halal_entities,
    annotate_halal_aspect_and_trust,
    annotate_female_daily_dataset
)

class TestBrandAnnotatorService(unittest.TestCase):

    def setUp(self):
        self.cleaned_data_path = os.path.join("data", "cleaned", "female_daily_skincare_cleaned.csv")
        self.annotated_output_path = os.path.join("data", "annotated", "female_daily_skincare_annotated.csv")
        
        self.sample_review_high_trust = {
            "merek_umkm": "Wardah",
            "kategori_produk": "Night Cream",
            "nama_produk": "Wardah Lightening Night Cream",
            "rating_bintang": 5,
            "status_rekomendasi": "Recommends this product",
            "teks_ulasan_bersih": "produk ini beneran bagus banget melembabkan terdaftar bpom halal mui resmi original segel utuh"
        }
        
        self.sample_review_low_trust = {
            "merek_umkm": "Emina",
            "kategori_produk": "Sun Protection",
            "nama_produk": "Emina Sun Battle SPF 30",
            "rating_bintang": 1,
            "status_rekomendasi": "Does not recommend",
            "teks_ulasan_bersih": "bikin kulit iritasi breakout parah beruntusan gatal gatal meragukan kemasan penyok tidak ada logo bpom"
        }

    def test_extract_brand_halal_entities(self):
        """Test extraction of halal, BPOM, and skin sensitivity entities."""
        entities_high = extract_brand_halal_entities(self.sample_review_high_trust["teks_ulasan_bersih"])
        self.assertTrue(entities_high["has_halal_claim"])
        self.assertTrue(entities_high["has_bpom_claim"])
        self.assertFalse(entities_high["has_breakout_issue"])

        entities_low = extract_brand_halal_entities(self.sample_review_low_trust["teks_ulasan_bersih"])
        self.assertTrue(entities_low["has_breakout_issue"])
        self.assertTrue(entities_low["has_packaging_issue"])

    def test_annotate_halal_aspect_and_trust(self):
        """Test dual-taxonomy aspect and trust sentiment annotation."""
        aspect, trust = annotate_halal_aspect_and_trust(self.sample_review_high_trust)
        self.assertEqual(aspect, "Sertifikasi_Halal_BPOM")
        self.assertEqual(trust, "High_Trust")

        aspect_low, trust_low = annotate_halal_aspect_and_trust(self.sample_review_low_trust)
        self.assertEqual(aspect_low, "Kandungan_Bahan_Sensitivitas")
        self.assertEqual(trust_low, "Low_Trust")

    def test_annotate_female_daily_dataset_execution(self):
        """Test batch annotation execution on cleaned dataset."""
        test_out = os.path.join("data", "annotated", "test_brand_annotated.csv")
        if os.path.exists(self.cleaned_data_path):
            output_path, count = annotate_female_daily_dataset(
                cleaned_csv_path=self.cleaned_data_path,
                output_csv_path=test_out
            )
            self.assertTrue(os.path.exists(output_path))
            self.assertGreater(count, 1000)
            if os.path.exists(test_out):
                os.remove(test_out)

if __name__ == "__main__":
    unittest.main()
