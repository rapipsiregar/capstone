import os
import pytest
import pandas as pd
from backend.services.indobert_trainer import train_indobert_model
from backend.services.xai_explainer import (
    explain_text_shap,
    get_highlight_color,
    format_shap_attributions,
)


@pytest.fixture
def temp_model_environment(tmp_path):
    data_dir = tmp_path / "data"
    model_dir = tmp_path / "models"
    data_dir.mkdir()
    model_dir.mkdir()

    train_df = pd.DataFrame({
        "teks_bersih": [
            "sangat bagus sertifikasi halal bpom resmi",
            "kandungan bahan aman tanpa alkohol",
            "klaim efikasi terbukti mencerahkan",
            "layanan penjual cepat dan transparan",
            "tidak ada logo halal meragukan",
            "efek samping membuat iritasi kulit"
        ] * 4,
        "label_aspek": [
            "Sertifikasi_Halal_BPOM",
            "Kandungan_Bahan",
            "Klaim_Efikasi_Manfaat",
            "Transparansi_Layanan",
            "Sertifikasi_Halal_BPOM",
            "Kandungan_Bahan"
        ] * 4,
        "label_kepercayaan": [
            "High_Trust",
            "High_Trust",
            "High_Trust",
            "High_Trust",
            "Low_Trust",
            "Low_Trust"
        ] * 4
    })

    train_df.to_csv(data_dir / "train.csv", index=False)
    train_indobert_model(data_dir=str(data_dir), model_dir=str(model_dir))

    return str(model_dir)


def test_get_highlight_color():
    assert get_highlight_color(0.25) == "#28a745"  # Positive contribution (Green)
    assert get_highlight_color(-0.18) == "#dc3545"  # Negative contribution (Red)
    assert get_highlight_color(0.01) == "#ffc107"  # Neutral contribution (Yellow)


def test_format_shap_attributions():
    tokens = ["halal", "bpom", "palsu"]
    scores = [0.4, 0.3, -0.5]
    attributions = format_shap_attributions(tokens, scores)

    assert len(attributions) == 3
    assert attributions[0]["token"] == "halal"
    assert attributions[0]["score"] == 0.4
    assert attributions[0]["highlight_color"] == "#28a745"
    assert attributions[0]["impact"] == "High_Trust"

    assert attributions[2]["token"] == "palsu"
    assert attributions[2]["score"] == -0.5
    assert attributions[2]["highlight_color"] == "#dc3545"
    assert attributions[2]["impact"] == "Low_Trust"


def test_explain_text_shap(temp_model_environment):
    model_dir = temp_model_environment
    test_text = "Produk ini bersertifikat halal resmi dari BPOM."

    explanation = explain_text_shap(text=test_text, model_dir=model_dir)

    assert "raw_text" in explanation
    assert "cleaned_text" in explanation
    assert "predicted_aspect" in explanation
    assert "predicted_trust" in explanation
    assert "tokens" in explanation
    assert "attributions" in explanation
    assert "base_value" in explanation
    assert "explanation_summary" in explanation

    assert isinstance(explanation["tokens"], list)
    assert isinstance(explanation["attributions"], list)
    assert len(explanation["attributions"]) > 0
