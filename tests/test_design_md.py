"""
Task 9.2: DESIGN.md must formalise the approved V4 Rose Blush direction with written reasons (R-31).
"""

from pathlib import Path

DESIGN = Path(__file__).resolve().parent.parent / "DESIGN.md"


def _text():
    assert DESIGN.exists(), "DESIGN.md must exist at the repo root"
    return DESIGN.read_text(encoding="utf-8")


def test_design_md_declares_the_four_user_colours_with_proportions():
    text = _text()
    for hex_code, share in [("#FCF8F8", "60%"), ("#FBEFEF", "25%"), ("#F9DFDF", "10%"), ("#F5AFAF", "5%")]:
        assert hex_code in text and share in text


def test_design_md_declares_ink_accent_and_trust_tokens():
    text = _text()
    for hex_code in ["#3D2228", "#75545A", "#A84A58", "#1E6B47"]:
        assert hex_code in text


def test_design_md_limits_typefaces_to_two_and_five_sizes():
    text = _text()
    assert "Playfair Display" in text and "Inter" in text
    assert "2 family" in text and "5 ukuran" in text


def test_design_md_records_reasons_dials_and_honesty_rules():
    text = _text()
    assert text.count("Alasan") >= 3
    for word in ["ENERGY", "RHYTHM", "MOTION", "L-Frame", "Faceted", "favicon", "Foto belum tersedia"]:
        assert word in text
    assert "terakota" in text.lower()

