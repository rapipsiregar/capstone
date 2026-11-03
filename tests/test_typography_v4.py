import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS_DIR = ROOT / "frontend" / "css"
TOKENS_CSS = CSS_DIR / "tokens.css"
INDEX_HTML = ROOT / "frontend" / "index.html"


def test_at_most_two_typefaces_in_tokens_and_html():
    tokens = TOKENS_CSS.read_text(encoding="utf-8")
    html = INDEX_HTML.read_text(encoding="utf-8")
    font_vars = re.findall(r"--font-[a-z0-9-]+:\s*([^;]+);", tokens)
    assert len(font_vars) == 2, f"Expected exactly 2 font-family tokens, got {font_vars}"
    assert "Playfair Display" in tokens
    assert "Inter" in tokens
    for banned in ("Outfit", "JetBrains Mono", "Roboto", "Poppins"):
        assert banned not in tokens, f"Banned font '{banned}' found in tokens.css"
        assert banned not in html, f"Banned font '{banned}' found in index.html"


def test_at_most_five_font_size_tokens():
    tokens = TOKENS_CSS.read_text(encoding="utf-8")
    fs_vars = re.findall(r"(--fs-[a-z0-9-]+)\s*:", tokens)
    assert 1 <= len(fs_vars) <= 5, f"Expected <= 5 font-size tokens, got {fs_vars}"


def test_all_css_modules_use_only_defined_font_tokens():
    for css_file in CSS_DIR.glob("*.css"):
        if css_file.name == "tokens.css":
            continue
        text = css_file.read_text(encoding="utf-8")
        families = re.findall(r"font-family:\s*([^;]+);", text)
        for fam in families:
            assert fam.strip() in ("var(--font-sans)", "var(--font-display)", "inherit"), (
                f"Unexpected font-family '{fam}' in {css_file.name}"
            )

