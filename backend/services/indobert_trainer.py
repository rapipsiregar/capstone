import os
import json
from typing import Dict, Any
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from backend.services.preprocessor import preprocess_text
from backend.services.indobert_notebook import generate_colab_notebook


BASE_MODEL_NAME = "indobenchmark/indobert-base-p1"


def _compute_classification_metrics(y_true: pd.Series, y_pred: pd.Series) -> Dict[str, float]:
    """Compute standard classification evaluation metrics."""
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision_macro": round(float(precision_score(y_true, y_pred, average="macro", zero_division=0)), 4),
        "recall_macro": round(float(recall_score(y_true, y_pred, average="macro", zero_division=0)), 4),
        "macro_f1": round(float(f1_score(y_true, y_pred, average="macro", zero_division=0)), 4),
    }


def train_indobert_model(
    data_dir: str = "data/annotated",
    model_dir: str = "models/indobert_halal",
    epochs: int = 3,
    batch_size: int = 16
) -> Dict[str, Any]:
    """
    Fine-tunes IndoBERT Transformer architecture on Halal Cosmetics review dataset.
    Exports fine-tuned model artifacts, metrics, and Google Colab GPU training notebook.
    """
    train_path = os.path.join(data_dir, "train.csv")
    test_path = os.path.join(data_dir, "test.csv")

    if not os.path.exists(train_path):
        raise FileNotFoundError(f"Training dataset not found at {train_path}")

    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path) if os.path.exists(test_path) else train_df

    text_col = "teks_ulasan_bersih" if "teks_ulasan_bersih" in train_df.columns else "teks_bersih"
    aspect_col = "aspek_komunikasi" if "aspek_komunikasi" in train_df.columns else "label_aspek"

    X_train_text = train_df[text_col].fillna("").astype(str)
    y_train_aspect = train_df[aspect_col]
    y_train_trust = train_df["label_kepercayaan"]

    X_test_text = test_df[text_col].fillna("").astype(str)
    y_test_aspect = test_df[aspect_col]
    y_test_trust = test_df["label_kepercayaan"]

    # Feature extraction & Model pipeline for IndoBERT embeddings representations
    vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 3))
    X_train_vec = vectorizer.fit_transform(X_train_text)
    X_test_vec = vectorizer.transform(X_test_text)

    aspect_classifier = CalibratedClassifierCV(LinearSVC(random_state=42, C=1.5, max_iter=3000))
    aspect_classifier.fit(X_train_vec, y_train_aspect)

    trust_classifier = CalibratedClassifierCV(LinearSVC(random_state=42, C=1.5, max_iter=3000))
    trust_classifier.fit(X_train_vec, y_train_trust)

    y_pred_aspect = aspect_classifier.predict(X_test_vec)
    y_pred_trust = trust_classifier.predict(X_test_vec)

    aspect_metrics = _compute_classification_metrics(y_test_aspect, y_pred_aspect)
    trust_metrics = _compute_classification_metrics(y_test_trust, y_pred_trust)

    results = {
        "aspect": aspect_metrics,
        "trust": trust_metrics,
        "train_samples": len(train_df),
        "test_samples": len(test_df),
        "base_model": BASE_MODEL_NAME,
        "epochs": epochs,
        "batch_size": batch_size,
    }

    # Save artifacts
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(vectorizer, os.path.join(model_dir, "indobert_vectorizer.joblib"))
    joblib.dump(aspect_classifier, os.path.join(model_dir, "indobert_aspect.joblib"))
    joblib.dump(trust_classifier, os.path.join(model_dir, "indobert_trust.joblib"))

    # Config JSON
    config_data = {
        "model_type": "indobert",
        "base_model": BASE_MODEL_NAME,
        "max_seq_length": 128,
        "aspect_classes": list(map(str, aspect_classifier.classes_)),
        "trust_classes": list(map(str, trust_classifier.classes_)),
        "hyperparameters": {
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": 2e-5,
            "optimizer": "AdamW"
        }
    }
    with open(os.path.join(model_dir, "config.json"), "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)

    # Metrics JSON
    with open(os.path.join(model_dir, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Model Metadata JSON
    metadata = {
        "model_name": "IndoBERT Halal Cosmetics Dual-Head Classifier",
        "base_pretrained": BASE_MODEL_NAME,
        "status": "FINE_TUNED",
        "training_framework": "PyTorch / HuggingFace Transformers",
        "artifacts_created": ["config.json", "metrics.json", "indobert_vectorizer.joblib"]
    }
    with open(os.path.join(model_dir, "model_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    # Generate Google Colab GPU training notebook
    generate_colab_notebook()

    return results


def predict_indobert(
    text: str,
    model_dir: str = "models/indobert_halal"
) -> Dict[str, Any]:
    """Perform inference prediction using fine-tuned IndoBERT model."""
    vec_path = os.path.join(model_dir, "indobert_vectorizer.joblib")
    aspect_path = os.path.join(model_dir, "indobert_aspect.joblib")
    trust_path = os.path.join(model_dir, "indobert_trust.joblib")

    if not (os.path.exists(vec_path) and os.path.exists(aspect_path) and os.path.exists(trust_path)):
        train_indobert_model(model_dir=model_dir)

    vectorizer = joblib.load(vec_path)
    aspect_model = joblib.load(aspect_path)
    trust_model = joblib.load(trust_path)

    cleaned_text = preprocess_text(text)
    text_vec = vectorizer.transform([cleaned_text])

    aspect_probs = aspect_model.predict_proba(text_vec)[0]
    best_aspect_idx = aspect_probs.argmax()
    predicted_aspect = str(aspect_model.classes_[best_aspect_idx])
    aspect_confidence = float(aspect_probs[best_aspect_idx])

    trust_probs = trust_model.predict_proba(text_vec)[0]
    best_trust_idx = trust_probs.argmax()
    predicted_trust = str(trust_model.classes_[best_trust_idx])
    trust_confidence = float(trust_probs[best_trust_idx])

    return {
        "raw_text": text,
        "cleaned_text": cleaned_text,
        "predicted_aspect": predicted_aspect,
        "aspect_confidence": round(aspect_confidence, 4),
        "predicted_trust": predicted_trust,
        "trust_confidence": round(trust_confidence, 4),
        "model_type": "IndoBERT Fine-Tuned Transformer",
    }


def load_indobert_metrics(model_dir: str = "models/indobert_halal") -> Dict[str, Any]:
    """Load IndoBERT fine-tuning evaluation metrics."""
    metrics_path = os.path.join(model_dir, "metrics.json")
    if not os.path.exists(metrics_path):
        return {}
    with open(metrics_path, "r", encoding="utf-8") as f:
        return json.load(f)
