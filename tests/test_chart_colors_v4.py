from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHARTS_JS = ROOT / "frontend" / "js" / "charts.js"


def test_charts_js_has_no_purple_or_indigo():
    text = CHARTS_JS.read_text(encoding="utf-8").lower()
    banned_purple = ["#8b5cf6", "#6366f1", "#7c3aed", "#a855f7", "139, 92, 246", "99, 102, 241"]
    for token in banned_purple:
        assert token not in text, f"Forbidden purple/indigo token '{token}' found in charts.js"


def test_charts_js_has_no_tailwind_framework_default_colours():
    text = CHARTS_JS.read_text(encoding="utf-8").lower()
    banned_framework = ["#10b981", "#3b82f6", "#ef4444", "#f59e0b"]
    for token in banned_framework:
        assert token not in text, f"Forbidden default framework colour '{token}' found in charts.js"


def test_charts_js_uses_rose_blush_and_design_md_semantic_colours():
    text = CHARTS_JS.read_text(encoding="utf-8").upper()
    for required in ["#F5AFAF", "#E8959B", "#C9636F", "#A84A58", "#1E6B47", "#A3262E"]:
        assert required in text, f"Expected DESIGN.md colour '{required}' in charts.js"
