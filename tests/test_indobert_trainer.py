import os
import json
import pytest
import pandas as pd
from backend.services.indobert_trainer import (
    train_indobert_model,
    predict_indobert,
    generate_colab_notebook,
    load_indobert_metrics,
)


@pytest.fixture
def temp_indobert_environment(tmp_path):
    data_dir = tmp_path / "data"
    model_dir = tmp_path / "models_indobert"
    notebook_dir = tmp_path / "notebooks"
    data_dir.mkdir()
    model_dir.mkdir()
    notebook_dir.mkdir()

    # Create dummy dataset for testing
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
    train_df.to_csv(data_dir / "val.csv", index=False)
    train_df.to_csv(data_dir / "test.csv", index=False)

    return str(data_dir), str(model_dir), str(notebook_dir / "indobert_colab.ipynb")


def test_generate_colab_notebook(temp_indobert_environment):
    _, _, notebook_path = temp_indobert_environment
    saved_path = generate_colab_notebook(output_path=notebook_path)

    assert os.path.exists(saved_path)
    with open(saved_path, "r", encoding="utf-8") as f:
        nb_data = json.load(f)
    assert "cells" in nb_data
    assert len(nb_data["cells"]) > 0


def test_train_indobert_model(temp_indobert_environment):
    data_dir, model_dir, _ = temp_indobert_environment
    results = train_indobert_model(data_dir=data_dir, model_dir=model_dir, epochs=1, batch_size=4)

    assert "aspect" in results
    assert "trust" in results
    assert "accuracy" in results["aspect"]
    assert "macro_f1" in results["aspect"]

    assert os.path.exists(os.path.join(model_dir, "config.json"))
    assert os.path.exists(os.path.join(model_dir, "metrics.json"))
    assert os.path.exists(os.path.join(model_dir, "model_metadata.json"))


def test_predict_indobert(temp_indobert_environment):
    data_dir, model_dir, _ = temp_indobert_environment
    train_indobert_model(data_dir=data_dir, model_dir=model_dir, epochs=1, batch_size=4)

    test_text = "Produk Wardah ini terbukti halal dan berizin BPOM."
    pred = predict_indobert(text=test_text, model_dir=model_dir)

    assert "cleaned_text" in pred
    assert "predicted_aspect" in pred
    assert "predicted_trust" in pred
    assert "aspect_confidence" in pred
    assert "trust_confidence" in pred
    assert isinstance(pred["aspect_confidence"], float)
    assert isinstance(pred["trust_confidence"], float)


def test_load_indobert_metrics(temp_indobert_environment):
    data_dir, model_dir, _ = temp_indobert_environment
    train_indobert_model(data_dir=data_dir, model_dir=model_dir, epochs=1, batch_size=4)

    metrics = load_indobert_metrics(model_dir=model_dir)
    assert "aspect" in metrics
    assert "trust" in metrics
