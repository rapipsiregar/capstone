"""
Unit Tests for IndoBERT Model Loader Service.
Verifies loading from environment configuration, singleton caching,
and clear error messaging when weights do not exist.
"""

import os
import unittest
import torch
from unittest.mock import patch
from backend.services.model_loader import (
    get_trust_model,
    get_aspect_model,
    get_trust_model_path,
    get_aspect_model_path,
    get_configured_device,
    load_model_and_tokenizer,
    reset_cached_models,
)


class TestModelLoader(unittest.TestCase):

    def setUp(self):
        reset_cached_models()

    def tearDown(self):
        reset_cached_models()

    def test_default_paths_and_device(self):
        """Verifies default environment path resolution."""
        self.assertEqual(get_trust_model_path(), "models/indobert_trust")
        self.assertEqual(get_aspect_model_path(), "models/indobert_aspect")

        expected_device = "cuda" if torch.cuda.is_available() else "cpu"
        self.assertEqual(get_configured_device().type, expected_device)

    def test_device_env_override(self):
        """Verifies TORCH_DEVICE overrides the device."""
        with patch.dict(os.environ, {"TORCH_DEVICE": "cpu"}):
            self.assertEqual(get_configured_device().type, "cpu")

    def test_load_trust_model_from_configured_path(self):
        """Verifies loading fine-tuned trust model from default local path."""
        model, tokenizer = get_trust_model()
        self.assertIsNotNone(model)
        self.assertIsNotNone(tokenizer)
        self.assertFalse(model.training)
        self.assertEqual(model.num_labels, 3)

    def test_load_aspect_model_from_configured_path(self):
        """Verifies loading fine-tuned aspect model from default local path."""
        model, tokenizer = get_aspect_model()
        self.assertIsNotNone(model)
        self.assertIsNotNone(tokenizer)
        self.assertFalse(model.training)
        self.assertEqual(model.num_labels, 4)

    def test_singleton_caching_behavior(self):
        """Verifies subsequent calls reuse cached model instances."""
        model1, tok1 = get_trust_model()
        model2, tok2 = get_trust_model()
        self.assertIs(model1, model2)
        self.assertIs(tok1, tok2)

    def test_clear_error_message_on_missing_weights(self):
        """Verifies informative FileNotFoundError when model path does not exist."""
        non_existent_path = "models/non_existent_model_checkpoint"
        with self.assertRaises(FileNotFoundError) as ctx:
            load_model_and_tokenizer(non_existent_path)

        err_msg = str(ctx.exception)
        self.assertIn("IndoBERT model weights not found at", err_msg)
        self.assertIn(non_existent_path, err_msg)


if __name__ == "__main__":
    unittest.main()
