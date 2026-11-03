"""
Unit test for Task 10.1: Verify zero emoji in UI code.
Taste-skill compliance: Interface elements, titles, buttons, and badges must use
authentic semantic text or SVG icons, not emojis.
"""

from pathlib import Path
import re

EMOJI_PATTERN = re.compile(r"[\U0001F300-\U0001FAFF\u2700-\u27BF\u2600-\u26FF]")

REPO_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = REPO_ROOT / "frontend"


def test_no_emojis_in_frontend_source_files():
    """All frontend HTML, CSS, and JS source files must contain 0 emojis."""
    offending_files = []

    for file_path in FRONTEND_DIR.rglob("*"):
        if file_path.suffix.lower() in {".html", ".js", ".css"}:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            matches = EMOJI_PATTERN.findall(content)
            if matches:
                offending_files.append((str(file_path.relative_to(REPO_ROOT)), len(matches)))

    assert not offending_files, f"Found emojis in frontend source files: {offending_files}"


def test_index_html_headings_clean_from_emojis():
    """Verify the V4 index.html headings and labels are plain text without emojis."""
    index_path = FRONTEND_DIR / "index.html"
    assert index_path.exists(), "frontend/index.html not found"

    html = index_path.read_text(encoding="utf-8")
    assert "Ulasan konsumen dan bobot SHAP IndoBERT" in html
    assert "Insight Reputasi" in html
    assert "Unduh laporan CSV" in html
    assert "Pendorong High Trust" in html
    assert "Pemicu Low Trust" in html
    assert "Metrik Skripsi" in html
    assert "Simulasi XAI" not in html
