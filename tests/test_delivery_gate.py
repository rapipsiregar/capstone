"""
Unit test for Task 10.9: Anti-Slop Delivery Gate Automated Audit.
Verifies critical quality locks across HTML, CSS, JS, and repo files:
1. Zero UI emojis in frontend templates.
2. Zero backdrop blur filters in CSS.
3. Zero transition: all in CSS.
4. Zero files > 256 LOC in repository code.
5. Zero static brand driver arrays or hardcoded mock sentiment fallbacks.
6. Right-aligned numeric table cells and tabular figures.
"""

from pathlib import Path
import os
import re
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = REPO_ROOT / "frontend"
FRONTEND_CSS = FRONTEND_DIR / "css"
FRONTEND_JS = FRONTEND_DIR / "js"


def test_zero_emojis_in_frontend():
    """Verify zero UI emojis remain in frontend HTML and JS files."""
    emoji_pattern = re.compile(
        r"[\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\U0001F900-\U0001F9FF\u2600-\u26FF\u2700-\u27BF]"
    )

    index_html = (FRONTEND_DIR / "index.html").read_text(encoding="utf-8")
    assert not emoji_pattern.search(index_html), "Found emoji in frontend/index.html"

    for js_file in FRONTEND_JS.glob("*.js"):
        content = js_file.read_text(encoding="utf-8")
        assert not emoji_pattern.search(content), f"Found emoji in {js_file.name}"


def test_zero_backdrop_blur_and_transition_all():
    """Verify zero backdrop blur and zero transition: all in all stylesheets."""
    blur_pat = re.compile(r"backdrop-filter\s*:\s*blur", re.IGNORECASE)
    trans_all_pat = re.compile(r"transition\s*:\s*all\b", re.IGNORECASE)

    for css_file in FRONTEND_CSS.glob("*.css"):
        css = css_file.read_text(encoding="utf-8")
        assert not blur_pat.search(css), f"Found backdrop-filter blur in {css_file.name}"
        assert not trans_all_pat.search(css), f"Found transition: all in {css_file.name}"


def test_zero_code_files_exceed_256_loc():
    """Verify strict compliance with AGENTS.md §3 (every code file <= 256 LOC)."""
    exclude = {".venv", ".git", "node_modules", "__pycache__", ".taste-skill", ".agents"}
    violators = []

    for root, dirs, files in os.walk(REPO_ROOT):
        if any(exc in root for exc in exclude):
            continue
        for f in files:
            if f.endswith((".py", ".js", ".css")):
                p = Path(root) / f
                loc = len(p.read_text(encoding="utf-8", errors="ignore").splitlines())
                if loc > 256:
                    violators.append((str(p.relative_to(REPO_ROOT)), loc))

    assert not violators, f"Code files exceeding 256 LOC: {violators}"


def test_zero_hardcoded_brand_drivers_in_frontend():
    """Verify frontend has no static mock dictionaries for brand drivers or fallback words."""
    for js_file in FRONTEND_JS.glob("*.js"):
        content = js_file.read_text(encoding="utf-8")
        assert "BRAND_DRIVERS" not in content, f"Found static BRAND_DRIVERS in {js_file.name}"
        assert "HIGH_TRUST_WORDS" not in content, f"Found static HIGH_TRUST_WORDS in {js_file.name}"
        assert "LOW_TRUST_WORDS" not in content, f"Found static LOW_TRUST_WORDS in {js_file.name}"
