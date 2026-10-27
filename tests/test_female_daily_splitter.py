"""
Unit & Integration Tests for Stratified Dataset Splitter & Sampling Engine Service.
"""

import os
import unittest
import pandas as pd
from backend.services.female_daily_splitter import split_female_daily_dataset

class TestFemaleDailySplitterService(unittest.TestCase):

    def setUp(self):
        self.annotated_data_path = os.path.join("data", "annotated", "female_daily_skincare_annotated.csv")
        self.train_path = os.path.join("data", "annotated", "train.csv")
        self.val_path = os.path.join("data", "annotated", "val.csv")
        self.test_path = os.path.join("data", "annotated", "test.csv")

    def test_split_female_daily_dataset_execution(self):
        """Test stratified 80/10/10 dataset split execution."""
        if os.path.exists(self.annotated_data_path):
            results = split_female_daily_dataset(
                annotated_csv_path=self.annotated_data_path,
                train_ratio=0.8,
                val_ratio=0.1,
                test_ratio=0.1,
                random_seed=42
            )
            
            self.assertTrue(os.path.exists(self.train_path))
            self.assertTrue(os.path.exists(self.val_path))
            self.assertTrue(os.path.exists(self.test_path))
            
            df_train = pd.read_csv(self.train_path)
            df_val = pd.read_csv(self.val_path)
            df_test = pd.read_csv(self.test_path)
            
            total_split = len(df_train) + len(df_val) + len(df_test)
            df_orig = pd.read_csv(self.annotated_data_path)
            
            self.assertEqual(total_split, len(df_orig))
            self.assertGreater(len(df_train), len(df_val))
            self.assertGreater(len(df_train), len(df_test))
            
            # Verify stratification balance for trust sentiment labels
            train_trust_dist = df_train["label_kepercayaan"].value_counts(normalize=True).to_dict()
            test_trust_dist = df_test["label_kepercayaan"].value_counts(normalize=True).to_dict()
            
            for trust_label in ["High_Trust", "Neutral", "Low_Trust"]:
                if trust_label in train_trust_dist and trust_label in test_trust_dist:
                    self.assertAlmostEqual(train_trust_dist[trust_label], test_trust_dist[trust_label], delta=0.05)

if __name__ == "__main__":
    unittest.main()
