"""
Unit & Integration Tests for Stratified Dataset Splitter & Sampling Engine Service.
Verifies 80/10/10 ratio, class distribution preservation, deterministic reproducibility,
and SHA256 checksum integrity.
"""

import os
import tempfile
import unittest
import pandas as pd
from backend.services.female_daily_splitter import (
    split_female_daily_dataset,
    compute_file_sha256,
)

EXPECTED_TRAIN_SHA256 = "d1a1c0ea90b7b6a728883801da13f3a8fb9b35240691e4883987a331674d2ed7"
EXPECTED_VAL_SHA256 = "17708160c5aa1fb93f6fed6139d774caf3edbe5f5fde410201c30411cfa524f5"
EXPECTED_TEST_SHA256 = "f11b0b811f597ba4dfa8ed6efe8b698159a4cd18fca31855910f4d81b65277c9"


class TestFemaleDailySplitterService(unittest.TestCase):

    def setUp(self):
        self.annotated_data_path = os.path.join("data", "annotated", "female_daily_skincare_annotated.csv")
        self.repo_train_path = os.path.join("data", "annotated", "train.csv")
        self.repo_val_path = os.path.join("data", "annotated", "val.csv")
        self.repo_test_path = os.path.join("data", "annotated", "test.csv")

    def test_split_female_daily_dataset_execution(self):
        """Test stratified 80/10/10 dataset split execution in isolated directory."""
        if not os.path.exists(self.annotated_data_path):
            self.skipTest("Annotated dataset not found")

        with tempfile.TemporaryDirectory() as tmpdir:
            results = split_female_daily_dataset(
                annotated_csv_path=self.annotated_data_path,
                output_dir=tmpdir,
                train_ratio=0.8,
                val_ratio=0.1,
                test_ratio=0.1,
                random_seed=42,
            )

            train_file = os.path.join(tmpdir, "train.csv")
            val_file = os.path.join(tmpdir, "val.csv")
            test_file = os.path.join(tmpdir, "test.csv")

            self.assertTrue(os.path.exists(train_file))
            self.assertTrue(os.path.exists(val_file))
            self.assertTrue(os.path.exists(test_file))

            df_train = pd.read_csv(train_file)
            df_val = pd.read_csv(val_file)
            df_test = pd.read_csv(test_file)

            total_split = len(df_train) + len(df_val) + len(df_test)
            df_orig = pd.read_csv(self.annotated_data_path)

            self.assertEqual(total_split, len(df_orig))
            self.assertEqual(len(df_train), 6692)
            self.assertEqual(len(df_val), 836)
            self.assertEqual(len(df_test), 837)

            # Verify stratification balance for trust sentiment labels
            train_trust_dist = df_train["label_kepercayaan"].value_counts(normalize=True).to_dict()
            test_trust_dist = df_test["label_kepercayaan"].value_counts(normalize=True).to_dict()

            for trust_label in ["High_Trust", "Neutral", "Low_Trust"]:
                if trust_label in train_trust_dist and trust_label in test_trust_dist:
                    self.assertAlmostEqual(train_trust_dist[trust_label], test_trust_dist[trust_label], delta=0.05)

    def test_split_deterministic_reproducibility(self):
        """Task 8.2 DoD: Test proves split is 100% reproducible with identical SHA256 hashes on repeated runs."""
        if not os.path.exists(self.annotated_data_path):
            self.skipTest("Annotated dataset not found")

        with tempfile.TemporaryDirectory() as tmpdir1, tempfile.TemporaryDirectory() as tmpdir2:
            res1 = split_female_daily_dataset(
                annotated_csv_path=self.annotated_data_path,
                output_dir=tmpdir1,
                random_seed=42,
            )
            res2 = split_female_daily_dataset(
                annotated_csv_path=self.annotated_data_path,
                output_dir=tmpdir2,
                random_seed=42,
            )

            # Hash between two independent runs must be byte-for-byte identical
            self.assertEqual(res1["train_sha256"], res2["train_sha256"])
            self.assertEqual(res1["val_sha256"], res2["val_sha256"])
            self.assertEqual(res1["test_sha256"], res2["test_sha256"])

            # Verify against verified ground truth hashes
            self.assertEqual(res1["train_sha256"], EXPECTED_TRAIN_SHA256)
            self.assertEqual(res1["val_sha256"], EXPECTED_VAL_SHA256)
            self.assertEqual(res1["test_sha256"], EXPECTED_TEST_SHA256)

    def test_repository_split_files_integrity(self):
        """Verifies that repository data/annotated split files match exact deterministic checksums."""
        self.assertTrue(os.path.exists(self.repo_train_path), "train.csv not found")
        self.assertTrue(os.path.exists(self.repo_val_path), "val.csv not found")
        self.assertTrue(os.path.exists(self.repo_test_path), "test.csv not found")

        self.assertEqual(compute_file_sha256(self.repo_train_path), EXPECTED_TRAIN_SHA256)
        self.assertEqual(compute_file_sha256(self.repo_val_path), EXPECTED_VAL_SHA256)
        self.assertEqual(compute_file_sha256(self.repo_test_path), EXPECTED_TEST_SHA256)

        self.assertEqual(len(pd.read_csv(self.repo_train_path)), 6692)
        self.assertEqual(len(pd.read_csv(self.repo_val_path)), 836)
        self.assertEqual(len(pd.read_csv(self.repo_test_path)), 837)


if __name__ == "__main__":
    unittest.main()

