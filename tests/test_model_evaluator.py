import os
import json
import pytest
import pandas as pd
from backend.services.indobert_trainer import train_indobert_model
from backend.services.model_evaluator import (
    evaluate_all_models,
    generate_confusion_matrix_dict,
    load_evaluation_results,
)


@pytest.fixture
def temp_eval_environment(tmp_path):
    data_dir = tmp_path / "data"
    models_dir = tmp_path / "models"
    data_dir.mkdir()
    models_dir.mkdir()

    # Create dummy annotated datasets
    test_df = pd.DataFrame({
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

    test_df.to_csv(data_dir / "train.csv", index=False)
    test_df.to_csv(data_dir / "test.csv", index=False)

    indobert_dir = str(models_dir / "indobert_halal")
    train_indobert_model(data_dir=str(data_dir), model_dir=indobert_dir)

    return str(data_dir), str(models_dir)


def test_generate_confusion_matrix_dict():
    y_true = ["High_Trust", "High_Trust", "Low_Trust", "Low_Trust"]
    y_pred = ["High_Trust", "Low_Trust", "Low_Trust", "Low_Trust"]
    labels = ["High_Trust", "Low_Trust"]

    cm_dict = generate_confusion_matrix_dict(y_true, y_pred, labels)

    assert "labels" in cm_dict
    assert "matrix" in cm_dict
    assert cm_dict["labels"] == labels
    assert len(cm_dict["matrix"]) == 2
    assert len(cm_dict["matrix"][0]) == 2


def test_evaluate_all_models(temp_eval_environment):
    data_dir, models_dir = temp_eval_environment
    output_json = os.path.join(models_dir, "evaluation_results.json")

    results = evaluate_all_models(
        data_dir=data_dir,
        models_base_dir=models_dir,
        output_path=output_json
    )

    assert "indobert" in results
    assert "accuracy" in results["indobert"]["trust"]
    assert "confusion_matrix" in results["indobert"]["trust"]
    assert "accuracy" in results["indobert"]["aspect"]

    assert os.path.exists(output_json)


def test_load_evaluation_results(temp_eval_environment):
    data_dir, models_dir = temp_eval_environment
    output_json = os.path.join(models_dir, "evaluation_results.json")

    evaluate_all_models(
        data_dir=data_dir,
        models_base_dir=models_dir,
        output_path=output_json
    )

    loaded = load_evaluation_results(output_json)
    assert "indobert" in loaded
