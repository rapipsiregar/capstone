"""
IndoBERT Fine-Tuner Service for Halal Cosmetics NLP.
Fine-tunes indobenchmark/indobert-base-p1 on GPU for trust sentiment classification
with mixed-precision FP16, genuine loss tracking per epoch, and evaluation checkpoints.
"""

import os
import json
import time
import torch
import pandas as pd
from typing import Dict, Any, List
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
    all_preds = []
    all_labels = []

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

    avg_loss = round(total_loss / len(all_labels), 4)
    acc = round(float(accuracy_score(all_labels, all_preds)), 4)
    f1_macro = round(float(f1_score(all_labels, all_preds, average="macro", zero_division=0)), 4)
    prec_macro = round(float(precision_score(all_labels, all_preds, average="macro", zero_division=0)), 4)
    rec_macro = round(float(recall_score(all_labels, all_preds, average="macro", zero_division=0)), 4)

    return {
        "loss": avg_loss,
        "accuracy": acc,
        "macro_f1": f1_macro,
        "precision_macro": prec_macro,
        "recall_macro": rec_macro,
    }


def train_indobert_trust_classifier(
    data_dir: str = "data/annotated",
    output_dir: str = "models/indobert_trust",
    epochs: int = 3,
    batch_size: int = 32,
    lr: float = 2e-5,
    max_length: int = 128,
) -> Dict[str, Any]:
    """
    Executes genuine IndoBERT fine-tuning on train.csv and validates on val.csv.
    Saves training history, final metrics, and model weights outside git.
    """
    start_time = time.time()
    train_path = os.path.join(data_dir, "train.csv")
    val_path = os.path.join(data_dir, "val.csv")

    if not os.path.exists(train_path) or not os.path.exists(val_path):
        raise FileNotFoundError(f"Dataset split files not found in {data_dir}")

    df_train = pd.read_csv(train_path)
    df_val = pd.read_csv(val_path)

    text_col = "teks_ulasan_bersih" if "teks_ulasan_bersih" in df_train.columns else "teks_bersih"
    X_train = df_train[text_col].fillna("").astype(str).tolist()
    y_train = [TRUST_LABEL_MAP.get(lbl, 1) for lbl in df_train["label_kepercayaan"]]

    X_val = df_val[text_col].fillna("").astype(str).tolist()
    y_val = [TRUST_LABEL_MAP.get(lbl, 1) for lbl in df_val["label_kepercayaan"]]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n[IndoBERT Trainer] Initializing training on device: {device}")
    if device.type == "cuda":
        print(f"  -> GPU: {torch.cuda.get_device_name(0)}")

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL_NAME,
        num_labels=3,
        id2label=TRUST_ID2LABEL,
        label2id=TRUST_LABEL_MAP,
        ignore_mismatched_sizes=True,
    ).to(device)

    train_dataset = ReviewDataset(X_train, y_train, tokenizer, max_length=max_length)
    val_dataset = ReviewDataset(X_val, y_val, tokenizer, max_length=max_length)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    total_steps = len(train_loader) * epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(total_steps * 0.1),
        num_training_steps=total_steps
    )
    scaler = torch.amp.GradScaler("cuda", enabled=(device.type == "cuda"))

    history = []
    log_lines = []

    print(f"[IndoBERT Trainer] Starting {epochs} epochs (Train: {len(X_train)}, Val: {len(X_val)}, Batch: {batch_size})...")

    for epoch in range(1, epochs + 1):
        model.train()
        epoch_start = time.time()
        running_loss = 0.0

        for step, batch in enumerate(train_loader, 1):
            optimizer.zero_grad()
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            with torch.amp.autocast("cuda", enabled=(device.type == "cuda")):
                outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
                loss = outputs.loss

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            scheduler.step()

            running_loss += loss.item() * len(labels)

        train_loss = round(running_loss / len(X_train), 4)
        val_metrics = evaluate_model(model, val_loader, device)
        epoch_duration = round(time.time() - epoch_start, 2)

        epoch_record = {
            "epoch": epoch,
            "train_loss": train_loss,
            "val_loss": val_metrics["loss"],
            "val_accuracy": val_metrics["accuracy"],
            "val_f1_macro": val_metrics["macro_f1"],
            "duration_sec": epoch_duration,
        }
        history.append(epoch_record)

        log_str = (
            f"Epoch {epoch}/{epochs} ({epoch_duration}s) | "
            f"Train Loss: {train_loss:.4f} | Val Loss: {val_metrics['loss']:.4f} | "
            f"Val Acc: {val_metrics['accuracy']:.4f} | Val F1: {val_metrics['macro_f1']:.4f}"
        )
        print(f"  -> {log_str}")
        log_lines.append(log_str)

    total_training_time = round(time.time() - start_time, 2)
    print(f"[IndoBERT Trainer] Training complete in {total_training_time}s!")

    # Save fine-tuned model artifacts and logs
    os.makedirs(output_dir, exist_ok=True)
    logs_dir = os.path.join("models", "training_logs")
    os.makedirs(logs_dir, exist_ok=True)

    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    history_path = os.path.join(output_dir, "training_history.json")
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump({
            "base_model": BASE_MODEL_NAME,
            "target_task": "label_kepercayaan",
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": lr,
            "device": str(device),
            "training_time_sec": total_training_time,
            "history": history,
            "final_val_metrics": history[-1] if history else {},
        }, f, indent=2)

    log_path = os.path.join(logs_dir, "train_trust_indobert.log")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + f"\nTotal training time: {total_training_time}s\n")

    return {
        "status": "success",
        "output_dir": os.path.abspath(output_dir),
        "log_path": os.path.abspath(log_path),
        "history_path": os.path.abspath(history_path),
        "training_time_sec": total_training_time,
        "final_epoch": history[-1] if history else {},
    }


if __name__ == "__main__":
    train_indobert_trust_classifier()
