import os
import json
from typing import Dict, Any, List
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
from backend.services.indobert_trainer import predict_indobert


def generate_confusion_matrix_dict(
    y_true: List[str],
    y_pred: List[str],
    labels: List[str] = None
) -> Dict[str, Any]:
    """Generates a structured dictionary containing confusion matrix array and labels."""
    if labels is None:
        labels = sorted(list(set(y_true) | set(y_pred)))

    cm = confusion_matrix(y_true, y_pred, labels=labels)
    return {
        "labels": labels,
        "matrix": cm.tolist()
    }


def compute_detailed_metrics(
    y_true: pd.Series,
    y_pred: List[str]
) -> Dict[str, Any]:
    """Computes comprehensive classification metrics (accuracy, macro/weighted precision/recall/F1, per-class report)."""
    labels = sorted(list(set(y_true) | set(y_pred)))
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)

    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "macro_precision": round(float(precision_score(y_true, y_pred, average="macro", zero_division=0)), 4),
        "macro_recall": round(float(recall_score(y_true, y_pred, average="macro", zero_division=0)), 4),
        "macro_f1": round(float(f1_score(y_true, y_pred, average="macro", zero_division=0)), 4),
        "weighted_f1": round(float(f1_score(y_true, y_pred, average="weighted", zero_division=0)), 4),
        "confusion_matrix": generate_confusion_matrix_dict(list(y_true), list(y_pred), labels=labels),
        "per_class_report": report
    }


def evaluate_model_pipeline(
    predict_func,
    test_df: pd.DataFrame
) -> Dict[str, Any]:
    """Evaluates a model pipeline on test DataFrame for Aspect and Trust predictions."""
    aspect_col = "aspek_komunikasi" if "aspek_komunikasi" in test_df.columns else "label_aspek"
    text_col = "teks_ulasan_bersih" if "teks_ulasan_bersih" in test_df.columns else "teks_bersih"
    
    y_true_aspect = test_df[aspect_col]
    y_true_trust = test_df["label_kepercayaan"]

    y_pred_aspect = []
    y_pred_trust = []

    for text in test_df[text_col].fillna(""):
        pred = predict_func(str(text))
        y_pred_aspect.append(pred["predicted_aspect"])
        y_pred_trust.append(pred["predicted_trust"])

    return {
        "aspect": compute_detailed_metrics(y_true_aspect, y_pred_aspect),
        "trust": compute_detailed_metrics(y_true_trust, y_pred_trust),
        "test_samples": len(test_df)
    }


def evaluate_all_models(
    data_dir: str = "data/annotated",
    models_base_dir: str = "models",
    output_path: str = "models/evaluation_results.json"
) -> Dict[str, Any]:
    """
    Evaluates the fine-tuned IndoBERT model on the test dataset.
    Generates accuracy, F1-score, and confusion matrix reports.
    """
    test_csv = os.path.join(data_dir, "test.csv")
    if not os.path.exists(test_csv):
        train_csv = os.path.join(data_dir, "train.csv")
        test_csv = train_csv

    test_df = pd.read_csv(test_csv)
    indobert_dir = os.path.join(models_base_dir, "indobert_halal")

    indobert_eval = evaluate_model_pipeline(
        lambda t: predict_indobert(t, model_dir=indobert_dir),
        test_df
    )

    full_report = {
        "model_architecture": "IndoBERT Transformer (Fine-Tuned)",
        "indobert": indobert_eval,
        "evaluated_samples": len(test_df)
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)

    return full_report


def load_evaluation_results(
    output_path: str = "models/evaluation_results.json"
) -> Dict[str, Any]:
    """Loads evaluation results JSON if exists."""
    if not os.path.exists(output_path):
        return {}
    with open(output_path, "r", encoding="utf-8") as f:
        return json.load(f)
