"""
Authentic IndoBERT Inference Predictor Service for Halal Cosmetics NLP.
Performs dual-target inference (Trust sentiment and Aspect communication)
using fine-tuned indobenchmark/indobert-base-p1 models loaded via model_loader.
"""

import time
import torch
from typing import Dict, Any
from backend.services.preprocessor import preprocess_text as clean_text
from backend.services.model_loader import (
    get_trust_model,
    get_aspect_model,
    get_configured_device,
)


def predict_indobert_authentic(text: str) -> Dict[str, Any]:
    """
    Performs real-time forward-pass inference on fine-tuned IndoBERT models
    for public trust sentiment (3 classes) and aspect communication (4 classes).
    """
    device = get_configured_device()
    trust_model, trust_tokenizer = get_trust_model()
    aspect_model, aspect_tokenizer = get_aspect_model()

    start_time = time.perf_counter()
    cleaned = clean_text(text)
    eval_text = cleaned if len(cleaned.strip()) > 0 else text

    # Tokenize input text for trust model
    trust_inputs = trust_tokenizer(
        eval_text,
        truncation=True,
        max_length=128,
        padding="max_length",
        return_tensors="pt",
    ).to(device)

    # Tokenize input text for aspect model
    aspect_inputs = aspect_tokenizer(
        eval_text,
        truncation=True,
        max_length=128,
        padding="max_length",
        return_tensors="pt",
    ).to(device)

    with torch.no_grad():
        with torch.amp.autocast("cuda", enabled=(device.type == "cuda")):
            trust_outputs = trust_model(**trust_inputs)
            aspect_outputs = aspect_model(**aspect_inputs)

            trust_probs = torch.softmax(trust_outputs.logits, dim=-1)
            aspect_probs = torch.softmax(aspect_outputs.logits, dim=-1)

            trust_pred_id = int(torch.argmax(trust_probs, dim=-1).item())
            trust_conf = round(float(torch.max(trust_probs).item()), 4)

            aspect_pred_id = int(torch.argmax(aspect_probs, dim=-1).item())
            aspect_conf = round(float(torch.max(aspect_probs).item()), 4)

    # Decode labels from model config id2label
    trust_label = trust_model.config.id2label.get(
        trust_pred_id,
        trust_model.config.id2label.get(str(trust_pred_id), "Neutral")
    )
    aspect_label = aspect_model.config.id2label.get(
        aspect_pred_id,
        aspect_model.config.id2label.get(str(aspect_pred_id), "Klaim_Efikasi_Manfaat")
    )

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return {
        "raw_text": text,
        "cleaned_text": cleaned,
        "predicted_aspect": aspect_label,
        "aspect_confidence": aspect_conf,
        "predicted_trust": trust_label,
        "trust_confidence": trust_conf,
        "model_type": "IndoBERT Transformer Fine-Tuned Model",
        "execution_time_ms": elapsed_ms,
    }
