"""
Honest IndoBERT Evaluator Service for Halal Cosmetics NLP.
Evaluates fine-tuned IndoBERT models (Trust & Aspect) on genuine test.csv split.
Computes real classification metrics and confusion matrices dynamically with zero hardcoded values.
"""

import os
import json
import torch
import pandas as pd
from typing import Dict, Any
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)
from backend.services.indobert_finetuner import (
    ReviewDataset,
    TRUST_LABEL_MAP,
    TRUST_ID2LABEL,
    ASPECT_LABEL_MAP,
    ASPECT_ID2LABEL,
)


def evaluate_single_task(
    model_dir: str,
    test_csv_path: str,
    target_column: str,
    label_map: Dict[str, int],
    id2label: Dict[int, str],
    device: torch.device,
    batch_size: int = 32,
    max_length: int = 128,
) -> Dict[str, Any]:
    """Runs genuine evaluation on test.csv using the saved fine-tuned model checkpoint."""
    if not os.path.exists(model_dir):
        raise FileNotFoundError(f"Model directory not found: {model_dir}")
    if not os.path.exists(test_csv_path):
        raise FileNotFoundError(f"Test dataset not found: {test_csv_path}")

    df_test = pd.read_csv(test_csv_path)
    text_col = "teks_ulasan_bersih" if "teks_ulasan_bersih" in df_test.columns else "teks_bersih"
    texts = df_test[text_col].fillna("").astype(str).tolist()
    y_true = [label_map[lbl] for lbl in df_test[target_column]]

    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir).to(device)
    model.eval()

    dataset = ReviewDataset(texts, y_true, tokenizer, max_length=max_length)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

    y_pred = []
    total_loss = 0.0

    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            with torch.amp.autocast("cuda", enabled=(device.type == "cuda")):
                outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
                loss = outputs.loss
                logits = outputs.logits

            total_loss += loss.item() * len(labels)
            preds = torch.argmax(logits, dim=1).cpu().tolist()
            y_pred.extend(preds)

    avg_loss = round(total_loss / len(y_true), 4)
    acc = round(float(accuracy_score(y_true, y_pred)), 4)
    prec_macro = round(float(precision_score(y_true, y_pred, average="macro", zero_division=0)), 4)
    rec_macro = round(float(recall_score(y_true, y_pred, average="macro", zero_division=0)), 4)
    f1_macro = round(float(f1_score(y_true, y_pred, average="macro", zero_division=0)), 4)

    target_names = [id2label[i] for i in range(len(label_map))]
    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(label_map)))).tolist()
    clf_report = classification_report(
        y_true, y_pred, target_names=target_names, output_dict=True, zero_division=0
    )

    return {
        "num_samples": len(y_true),
        "loss": avg_loss,
        "accuracy": acc,
        "precision_macro": prec_macro,
        "recall_macro": rec_macro,
        "f1_macro": f1_macro,
        "confusion_matrix": cm,
        "labels": target_names,
        "classification_report": clf_report,
    }


def evaluate_honest_indobert_models(
    data_dir: str = "data/annotated",
    trust_model_dir: str = "models/indobert_trust",
    aspect_model_dir: str = "models/indobert_aspect",
    output_json_path: str = "models/indobert_evaluation_results.json",
) -> Dict[str, Any]:
    """Evaluates both Trust and Aspect fine-tuned models on test.csv and exports honest JSON."""
    test_path = os.path.join(data_dir, "test.csv")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    trust_results = evaluate_single_task(
        model_dir=trust_model_dir,
        test_csv_path=test_path,
        target_column="label_kepercayaan",
        label_map=TRUST_LABEL_MAP,
        id2label=TRUST_ID2LABEL,
        device=device,
    )

    aspect_results = evaluate_single_task(
        model_dir=aspect_model_dir,
        test_csv_path=test_path,
        target_column="aspek_komunikasi",
        label_map=ASPECT_LABEL_MAP,
        id2label=ASPECT_ID2LABEL,
        device=device,
    )

    full_evaluation = {
        "status": "success",
        "dataset_split": "test.csv",
        "total_test_samples": trust_results["num_samples"],
        "device_used": str(device),
        "trust_classifier": trust_results,
        "aspect_classifier": aspect_results,
    }

    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(full_evaluation, f, indent=2)

    return full_evaluation


if __name__ == "__main__":
    evaluate_honest_indobert_models()
