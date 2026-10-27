"""
IndoBERT Fine-Tuner Service for Halal Cosmetics NLP.
Fine-tunes indobenchmark/indobert-base-p1 on GPU for trust and aspect classification
with mixed-precision FP16, genuine loss tracking per epoch, and evaluation checkpoints.
"""

import os
import json
import time
import torch
import pandas as pd
from typing import Dict, Any, List, Optional
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    get_linear_schedule_with_warmup,
)
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

BASE_MODEL_NAME = "indobenchmark/indobert-base-p1"
TRUST_LABEL_MAP = {"Low_Trust": 0, "Neutral": 1, "High_Trust": 2}
TRUST_ID2LABEL = {0: "Low_Trust", 1: "Neutral", 2: "High_Trust"}

ASPECT_LABEL_MAP = {
    "Sertifikasi_Halal_BPOM": 0,
    "Kandungan_Bahan_Sensitivitas": 1,
    "Klaim_Efikasi_Manfaat": 2,
    "Transparansi_Layanan_Harga": 3,
}
ASPECT_ID2LABEL = {
    0: "Sertifikasi_Halal_BPOM",
    1: "Kandungan_Bahan_Sensitivitas",
    2: "Klaim_Efikasi_Manfaat",
    3: "Transparansi_Layanan_Harga",
}


class ReviewDataset(Dataset):
    """PyTorch Dataset for tokenized review texts and integer labels."""
    def __init__(self, texts: List[str], labels: List[int], tokenizer, max_length: int = 128):
        self.encodings = tokenizer(
            texts,
            truncation=True,
            padding="max_length",
            max_length=max_length,
            return_tensors="pt"
        )
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        item["labels"] = self.labels[idx]
        return item


def evaluate_model(model, dataloader, device) -> Dict[str, float]:
    """Evaluates model performance on a given validation or test dataloader."""
    model.eval()
    total_loss = 0.0
    all_preds, all_labels = [], []

    criterion = torch.nn.CrossEntropyLoss()
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
            all_preds.extend(preds)
            all_labels.extend(labels.cpu().tolist())

    return {
        "loss": round(total_loss / len(all_labels), 4),
        "accuracy": round(float(accuracy_score(all_labels, all_preds)), 4),
        "macro_f1": round(float(f1_score(all_labels, all_preds, average="macro", zero_division=0)), 4),
        "precision_macro": round(float(precision_score(all_labels, all_preds, average="macro", zero_division=0)), 4),
        "recall_macro": round(float(recall_score(all_labels, all_preds, average="macro", zero_division=0)), 4),
    }


def train_indobert_classifier(
    task: str = "trust",
    data_dir: str = "data/annotated",
    output_dir: Optional[str] = None,
    epochs: int = 3,
    batch_size: int = 32,
    lr: float = 2e-5,
    max_length: int = 128,
) -> Dict[str, Any]:
    """Fine-tunes IndoBERT for trust or aspect classification with genuine metrics."""
    start_time = time.time()
    is_aspect = (task == "aspect")
    target_col = "aspek_komunikasi" if is_aspect else "label_kepercayaan"
    label_map = ASPECT_LABEL_MAP if is_aspect else TRUST_LABEL_MAP
    id2label = ASPECT_ID2LABEL if is_aspect else TRUST_ID2LABEL
    default_out = "models/indobert_aspect" if is_aspect else "models/indobert_trust"
    out_dir = output_dir or default_out
    log_file = "train_aspect_indobert.log" if is_aspect else "train_trust_indobert.log"

    train_path = os.path.join(data_dir, "train.csv")
    val_path = os.path.join(data_dir, "val.csv")
    if not os.path.exists(train_path) or not os.path.exists(val_path):
        raise FileNotFoundError(f"Dataset split files not found in {data_dir}")

    df_train, df_val = pd.read_csv(train_path), pd.read_csv(val_path)
    text_col = "teks_ulasan_bersih" if "teks_ulasan_bersih" in df_train.columns else "teks_bersih"
    X_train = df_train[text_col].fillna("").astype(str).tolist()
    y_train = [label_map[lbl] for lbl in df_train[target_col]]
    X_val = df_val[text_col].fillna("").astype(str).tolist()
    y_val = [label_map[lbl] for lbl in df_val[target_col]]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n[IndoBERT Trainer] Task: {task.upper()} | Device: {device}", flush=True)

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL_NAME,
        num_labels=len(label_map),
        id2label=id2label,
        label2id=label_map,
        ignore_mismatched_sizes=True,
    ).to(device)

    train_loader = DataLoader(ReviewDataset(X_train, y_train, tokenizer, max_length), batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(ReviewDataset(X_val, y_val, tokenizer, max_length), batch_size=batch_size, shuffle=False)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    total_steps = len(train_loader) * epochs
    scheduler = get_linear_schedule_with_warmup(optimizer, int(total_steps * 0.1), total_steps)
    scaler = torch.amp.GradScaler("cuda", enabled=(device.type == "cuda"))

    history, log_lines = [], []
    print(f"[IndoBERT Trainer] Starting {epochs} epochs (Train: {len(X_train)}, Val: {len(X_val)})...", flush=True)

    for epoch in range(1, epochs + 1):
        model.train()
        epoch_start, running_loss = time.time(), 0.0
        for batch in train_loader:
            optimizer.zero_grad()
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            with torch.amp.autocast("cuda", enabled=(device.type == "cuda")):
                loss = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels).loss

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            scheduler.step()
            running_loss += loss.item() * len(labels)

        train_loss = round(running_loss / len(X_train), 4)
        val_metrics = evaluate_model(model, val_loader, device)
        dur = round(time.time() - epoch_start, 2)
        rec = {
            "epoch": epoch,
            "train_loss": train_loss,
            "val_loss": val_metrics["loss"],
            "val_accuracy": val_metrics["accuracy"],
            "val_f1_macro": val_metrics["macro_f1"],
            "duration_sec": dur,
        }
        history.append(rec)
        log_str = (
            f"Epoch {epoch}/{epochs} ({dur}s) | Train Loss: {train_loss:.4f} | "
            f"Val Loss: {val_metrics['loss']:.4f} | Val Acc: {val_metrics['accuracy']:.4f} | "
            f"Val F1: {val_metrics['macro_f1']:.4f}"
        )
        print(f"  -> {log_str}", flush=True)
        log_lines.append(log_str)

    total_time = round(time.time() - start_time, 2)
    os.makedirs(out_dir, exist_ok=True)
    logs_dir = os.path.join("models", "training_logs")
    os.makedirs(logs_dir, exist_ok=True)

    model.save_pretrained(out_dir)
    tokenizer.save_pretrained(out_dir)

    history_path = os.path.join(out_dir, "training_history.json")
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump({
            "base_model": BASE_MODEL_NAME,
            "target_task": target_col,
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": lr,
            "device": str(device),
            "training_time_sec": total_time,
            "history": history,
            "final_val_metrics": history[-1] if history else {},
        }, f, indent=2)

    log_path = os.path.join(logs_dir, log_file)
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + f"\nTotal training time: {total_time}s\n")

    return {
        "status": "success",
        "output_dir": os.path.abspath(out_dir),
        "log_path": os.path.abspath(log_path),
        "history_path": os.path.abspath(history_path),
        "training_time_sec": total_time,
        "final_epoch": history[-1] if history else {},
    }


def train_indobert_trust_classifier(**kwargs):
    """Wrapper to train trust sentiment classifier."""
    return train_indobert_classifier(task="trust", **kwargs)


def train_indobert_aspect_classifier(**kwargs):
    """Wrapper to train aspect category classifier."""
    return train_indobert_classifier(task="aspect", **kwargs)


if __name__ == "__main__":
    train_indobert_aspect_classifier()
