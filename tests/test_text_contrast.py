"""
TDD Tests for Task 9.11: Elimination of Low-Contrast Text (#94A3B8) and WCAG Compliance.
Verifies:
1. No #94A3B8 in frontend/ (CSS and JS files).
2. The replacement #475569 passes WCAG 4.5:1 on white (#FFFFFF) and background (#F8FAFC).
3. Executes contrast-check.py to confirm PASS for normal text.
"""

import glob
import os
import re
import subprocess
import pytest

FRONTEND_DIR = "frontend"
CONTRAST_SCRIPT = os.path.join(".agents", "skills", "antislop-human", "contrast-check.py")


def test_zero_94a3b8_in_frontend():
    """frontend/ must have 0 occurrences of low-contrast #94A3B8 / #94a3b8."""
    target_files = []
    for ext in ("*.css", "*.js", "*.html"):
        target_files.extend(glob.glob(os.path.join(FRONTEND_DIR, "**", ext), recursive=True))

    violations = []
    for fpath in target_files:
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if re.search(r"94a3b8", content, re.IGNORECASE):
            violations.append(fpath)

    assert violations == [], f"Found low-contrast #94A3B8 in: {violations}"


def test_contrast_check_replacement_passes_wcag():
    """Replacement color #475569 must PASS on #FFFFFF and #F8FAFC per contrast-check.py."""
    for bg in ("#FFFFFF", "#F8FAFC"):
        res = subprocess.run(
            [".venv/Scripts/python", CONTRAST_SCRIPT, "#475569", bg],
            capture_output=True,
            text=True
        )
        assert res.returncode == 0, f"contrast-check.py failed for #475569 on {bg}: {res.stdout}"
        assert "normal text (4.5:1): PASS" in res.stdout
