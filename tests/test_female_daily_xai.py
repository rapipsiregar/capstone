"""
Unit & Integration Tests for Female Daily SHAP XAI Feature Attribution Service.
"""

import os
import unittest
from backend.services.female_daily_xai import (
    explain_review_shap,
    generate_explanation_narrative
)

class TestFemaleDailyXAIService(unittest.TestCase):

    def test_explain_review_shap_high_trust(self):
        """Test SHAP attribution for high trust review text."""
        sample_text = "produk wardah ini melembabkan banget terdaftar bpom dan halal mui resmi"
        res = explain_review_shap(sample_text)
        
        self.assertIn("tokens", res)
        self.assertIn("shap_values", res)
        self.assertIn("narrative_explanation", res)
        
        # Check green highlights for halal/bpom
        tokens = res["tokens"]
        self.assertTrue(any(t["word"] in ["bpom", "halal", "melembabkan"] and t["color"] == "#28a745" for t in tokens))

    def test_explain_review_shap_low_trust(self):
        """Test SHAP attribution for low trust review text with breakout."""
        sample_text = "bikin kulit iritasi breakout parah beruntusan meragukan gatal gatal"
        res = explain_review_shap(sample_text)
        
        tokens = res["tokens"]
        # Check red highlights for breakout/iritasi
        self.assertTrue(any(t["word"] in ["breakout", "iritasi", "beruntusan"] and t["color"] == "#dc3545" for t in tokens))

    def test_generate_explanation_narrative(self):
        """Test narrative explanation generator."""
        narrative = generate_explanation_narrative("Wardah", "High_Trust", ["halal", "bpom", "melembabkan"], ["iritasi"])
        self.assertIn("Wardah", narrative)
        self.assertIn("High Trust", narrative)

if __name__ == "__main__":
    unittest.main()
