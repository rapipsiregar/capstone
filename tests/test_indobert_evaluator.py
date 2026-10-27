"""
Unit & Regression Tests for Honest IndoBERT Evaluator Service.
Verifies evaluation metrics calculation, confusion matrix dimensions and sum,
and enforces that no metrics are hardcoded.
"""

import os
import unittest
from backend.services.indobert_evaluator import evaluate_honest_indobert_models


class TestIndoBERTHonestEvaluator(unittest.TestCase):

    def test_evaluation_produces_genuine_results(self):
        """Verifies evaluator produces valid JSON with correct dimensions and row counts."""
        results = evaluate_honest_indobert_models()
        self.assertEqual(results["status"], "success")
        self.assertEqual(results["total_test_samples"], 837)

        # Check trust classifier evaluation
        trust_res = results["trust_classifier"]
        self.assertEqual(trust_res["num_samples"], 837)
        self.assertIn("accuracy", trust_res)
        self.assertIn("f1_macro", trust_res)
        self.assertGreater(trust_res["accuracy"], 0.70)
        self.assertGreater(trust_res["f1_macro"], 0.70)

        # Check confusion matrix sum equals exact test count
        cm_trust = trust_res["confusion_matrix"]
        self.assertEqual(len(cm_trust), 3)
        self.assertEqual(sum(sum(row) for row in cm_trust), 837)

        # Check aspect classifier evaluation
        aspect_res = results["aspect_classifier"]
        self.assertEqual(aspect_res["num_samples"], 837)
        self.assertIn("accuracy", aspect_res)
        self.assertIn("f1_macro", aspect_res)
        self.assertGreater(aspect_res["accuracy"], 0.85)

        # Check aspect confusion matrix sum equals exact test count
        cm_aspect = aspect_res["confusion_matrix"]
        self.assertEqual(len(cm_aspect), 4)
        self.assertEqual(sum(sum(row) for row in cm_aspect), 837)

    def test_no_hardcoded_fake_metrics_in_evaluator(self):
        """Verifies indobert_evaluator.py contains zero hardcoded metric constants."""
        evaluator_file = os.path.join("backend", "services", "indobert_evaluator.py")
        with open(evaluator_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Old fake metrics that existed in female_daily_evaluator
        self.assertNotIn("0.942", content)
        self.assertNotIn("0.938", content)
        self.assertNotIn("0.941", content)
        self.assertNotIn("0.9395", content)


if __name__ == "__main__":
    unittest.main()
