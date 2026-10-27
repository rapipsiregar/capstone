"""
Unit & Integration Tests for IndoBERT Fine-Tuner Service.
Verifies Dataset tokenization, loss tracking data structures, and artifacts integrity.
"""

import os
import unittest
import torch
from transformers import AutoTokenizer
from backend.services.indobert_finetuner import (
    ReviewDataset,
    BASE_MODEL_NAME,
    TRUST_LABEL_MAP,
    TRUST_ID2LABEL,
    ASPECT_LABEL_MAP,
    ASPECT_ID2LABEL,
)


class TestIndoBERTFineTuner(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)

    def test_review_dataset_tokenization(self):
        """Test ReviewDataset tokenization outputs valid PyTorch tensors."""
        texts = [
            "Produk ini sangat bagus, halal mui resmi dan cocok di kulit.",
            "Kecewa banget barang palsu dan bikin muka beruntusan parah.",
            "Teksturnya biasa saja tidak ada efek apa apa."
        ]
        labels = [2, 0, 1]

        dataset = ReviewDataset(texts, labels, self.tokenizer, max_length=64)
        self.assertEqual(len(dataset), 3)

        sample = dataset[0]
        self.assertIn("input_ids", sample)
        self.assertIn("attention_mask", sample)
        self.assertIn("labels", sample)

        self.assertEqual(sample["input_ids"].shape[0], 64)
        self.assertEqual(sample["attention_mask"].shape[0], 64)
        self.assertEqual(sample["labels"].item(), 2)

    def test_trust_label_mappings_consistency(self):
        """Verify trust label mapping bidirectional consistency."""
        self.assertEqual(len(TRUST_LABEL_MAP), 3)
        self.assertEqual(len(TRUST_ID2LABEL), 3)

        for label_name, label_id in TRUST_LABEL_MAP.items():
            self.assertEqual(TRUST_ID2LABEL[label_id], label_name)

    def test_aspect_label_mappings_consistency(self):
        """Verify aspect label mapping bidirectional consistency."""
        self.assertEqual(len(ASPECT_LABEL_MAP), 4)
        self.assertEqual(len(ASPECT_ID2LABEL), 4)

        for label_name, label_id in ASPECT_LABEL_MAP.items():
            self.assertEqual(ASPECT_ID2LABEL[label_id], label_name)

    def test_training_paths_exist(self):
        """Verify training and validation split datasets exist."""
        train_path = os.path.join("data", "annotated", "train.csv")
        val_path = os.path.join("data", "annotated", "val.csv")
        self.assertTrue(os.path.exists(train_path), f"Train dataset missing at {train_path}")
        self.assertTrue(os.path.exists(val_path), f"Val dataset missing at {val_path}")

    def test_saved_training_artifacts_and_metrics(self):
        """Verify fine-tuning artifacts and genuine epoch metrics exist."""
        import json
        history_path = os.path.join("models", "indobert_trust", "training_history.json")
        log_path = os.path.join("models", "training_logs", "train_trust_indobert.log")
        weights_path = os.path.join("models", "indobert_trust", "model.safetensors")

        self.assertTrue(os.path.exists(history_path), f"Missing {history_path}")
        self.assertTrue(os.path.exists(log_path), f"Missing {log_path}")
        self.assertTrue(os.path.exists(weights_path), f"Missing {weights_path}")

        with open(history_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["epochs"], 3)
        self.assertEqual(len(data["history"]), 3)
        for ep in data["history"]:
            self.assertIn("train_loss", ep)
            self.assertIn("val_loss", ep)
            self.assertIn("val_accuracy", ep)
            self.assertIn("val_f1_macro", ep)
            self.assertGreater(ep["train_loss"], 0.0)
            self.assertGreater(ep["val_accuracy"], 0.70)

    def test_saved_aspect_training_artifacts_and_metrics(self):
        """Verify aspect fine-tuning artifacts and genuine epoch metrics exist."""
        import json
        history_path = os.path.join("models", "indobert_aspect", "training_history.json")
        log_path = os.path.join("models", "training_logs", "train_aspect_indobert.log")
        weights_path = os.path.join("models", "indobert_aspect", "model.safetensors")

        self.assertTrue(os.path.exists(history_path), f"Missing {history_path}")
        self.assertTrue(os.path.exists(log_path), f"Missing {log_path}")
        self.assertTrue(os.path.exists(weights_path), f"Missing {weights_path}")

        with open(history_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["epochs"], 3)
        self.assertEqual(len(data["history"]), 3)
        for ep in data["history"]:
            self.assertIn("train_loss", ep)
            self.assertIn("val_loss", ep)
            self.assertIn("val_accuracy", ep)
            self.assertIn("val_f1_macro", ep)
            self.assertGreater(ep["train_loss"], 0.0)
            self.assertGreater(ep["val_accuracy"], 0.85)


if __name__ == "__main__":
    unittest.main()
