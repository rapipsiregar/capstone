"""
Unit & Integration Tests for Multi-Brand IndoBERT Fine-Tuning Trainer Service.
"""

import os
import unittest
import pandas as pd
from backend.services.female_daily_indobert_trainer import (
    prepare_indobert_training_config,
    train_female_daily_indobert,
    predict_indobert_sentiment
)

class TestFemaleDailyIndoBERTTrainer(unittest.TestCase):

    def setUp(self):
        self.model_dir = os.path.join("models", "indobert_halal")
        self.train_path = os.path.join("data", "annotated", "train.csv")
        self.val_path = os.path.join("data", "annotated", "val.csv")

    def test_prepare_indobert_training_config(self):
        """Test configuration generation for IndoBERT fine-tuning."""
        config = prepare_indobert_training_config()
        self.assertEqual(config["base_model_name"], "indobenchmark/indobert-base-p1")
        self.assertEqual(config["learning_rate"], 2e-5)
        self.assertIn("High_Trust", config["label_mapping_trust"])

    def test_train_female_daily_indobert_pipeline(self):
        """Test fine-tuning pipeline execution on dataset."""
        if os.path.exists(self.train_path) and os.path.exists(self.val_path):
            result = train_female_daily_indobert(
                train_csv=self.train_path,
                val_csv=self.val_path,
                output_dir=self.model_dir,
                epochs=1,
                mock_if_no_gpu=True
            )
            self.assertTrue(result["success"])
            self.assertTrue(os.path.exists(os.path.join(self.model_dir, "model_metadata.json")))

    def test_predict_indobert_sentiment(self):
        """Test prediction function using trained IndoBERT service."""
        sample_text = "produk wardah ini melembabkan banget terdaftar bpom dan halal mui"
        res = predict_indobert_sentiment(sample_text)
        self.assertIn("predicted_aspect", res)
        self.assertIn("predicted_trust", res)
        self.assertIn("confidence_score", res)
        self.assertGreater(res["confidence_score"], 0.5)

if __name__ == "__main__":
    unittest.main()
