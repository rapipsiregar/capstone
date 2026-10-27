"""
TDD Tests for Review Refiner Service (Task 1.1 / Data Refinement Pipeline).
Verifies safe backup, text matching, prefix validation, and checkpointing.
"""

import os
import unittest
import json
from backend.services.review_refiner import (
    validate_and_merge_text,
    create_dataset_backup,
    DATASET_PATH,
    BACKUP_PATH
)


class TestReviewRefiner(unittest.TestCase):

    def test_validate_and_merge_text_success(self):
        cut_text = "Saya beli ini karena bagus banget, bikin cerah dan ... Read more"
        full_text = "Saya beli ini karena bagus banget, bikin cerah dan halus di kulit seharian tanpa rasa berminyak."
        
        merged, is_valid = validate_and_merge_text(cut_text, full_text)
        self.assertTrue(is_valid)
        self.assertEqual(merged, full_text)
        self.assertNotIn("Read more", merged)

    def test_validate_and_merge_text_rejects_unrelated_text(self):
        cut_text = "Saya beli ini karena bagus banget ... Read more"
        unrelated = "Produk ini sangat buruk dan bikin jerawatan parah."
        
        merged, is_valid = validate_and_merge_text(cut_text, unrelated)
        self.assertFalse(is_valid)
        self.assertEqual(merged, cut_text)  # keeps original if mismatch

    def test_create_dataset_backup(self):
        backup_created = create_dataset_backup()
        self.assertTrue(backup_created)
        self.assertTrue(os.path.exists(BACKUP_PATH))
        self.assertGreater(os.path.getsize(BACKUP_PATH), 1000000)


if __name__ == "__main__":
    unittest.main()
