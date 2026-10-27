"""Unit & Integration Tests for IndoBERT Model Evaluator Service."""

import os
import unittest
from backend.services.female_daily_evaluator import (
    evaluate_indobert_female_daily
)


class TestFemaleDailyEvaluatorService(unittest.TestCase):

    def setUp(self):
        self.test_csv_path = os.path.join("data", "annotated", "test.csv")
        self.output_eval_path = os.path.join("models", "female_daily_evaluation_results.json")

    def test_evaluate_indobert_female_daily(self):
        """Test IndoBERT model evaluation execution on test.csv."""
        if os.path.exists(self.test_csv_path):
            metrics = evaluate_indobert_female_daily(test_csv=self.test_csv_path)
            self.assertIn("indobert", metrics)
            self.assertIn("accuracy_trust", metrics["indobert"])
            self.assertGreater(metrics["indobert"]["accuracy_trust"], 0.70)
            self.assertTrue(os.path.exists(self.output_eval_path))


if __name__ == "__main__":
    unittest.main()
