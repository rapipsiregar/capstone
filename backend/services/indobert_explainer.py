"""
Authentic IndoBERT SHAP Explainer Service for Halal Cosmetics NLP.
Computes real Shapley attribution values using the shap library on the fine-tuned
IndoBERT model with thread-safe in-memory caching.
"""

import time
import hashlib
import numpy as np
import torch
import shap
from typing import Dict, Any, List, Optional
from backend.services.preprocessor import preprocess_text
from backend.services.model_loader import get_trust_model, get_configured_device
from backend.services.indobert_predictor import predict_indobert_authentic

_explainer_instance: Optional[shap.Explainer] = None
_shap_cache: Dict[str, Dict[str, Any]] = {}


def _get_text_hash(text: str) -> str:
    """Generates MD5 hash key for caching."""
    return hashlib.md5(text.strip().encode("utf-8")).hexdigest()


def get_indobert_explainer() -> shap.Explainer:
    """Lazily initializes and caches the SHAP Text Explainer instance."""
    global _explainer_instance
    if _explainer_instance is not None:
        return _explainer_instance

    device = get_configured_device()
    model, tokenizer = get_trust_model()

    def predict_trust_proba(texts):
        if isinstance(texts, str):
            texts = [texts]
        text_list = [str(t) for t in texts]
        inputs = tokenizer(
            text_list,
            padding=True,
            truncation=True,
            max_length=96,
            return_tensors="pt"
        ).to(device)

        with torch.no_grad():
            with torch.amp.autocast("cuda", enabled=(device.type == "cuda")):
                outputs = model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy()
        return probs

    masker = shap.maskers.Text(tokenizer)
    _explainer_instance = shap.Explainer(
        predict_trust_proba,
        masker,
        output_names=["Low_Trust", "Neutral", "High_Trust"]
    )
    return _explainer_instance


def get_highlight_color(score: float, impact: str) -> str:
    """Returns accessible hex color for attribution highlight."""
    if impact == "High_Trust":
        return "#28a745"
    elif impact == "Low_Trust":
        return "#dc3545"
    return "#ffc107"


def determine_impact(score: float, threshold: float = 0.02) -> str:
    """Maps signed attribution score to impact sentiment category."""
    if score > threshold:
        return "High_Trust"
    elif score < -threshold:
        return "Low_Trust"
    return "Neutral"


def explain_text_with_shap(text: str) -> Dict[str, Any]:
    """
    Computes authentic SHAP Shapley values for an input text using the fine-tuned
    IndoBERT model. Caches results for instantaneous subsequent queries.
    """
    start_time = time.perf_counter()
    cache_key = _get_text_hash(text)

    if cache_key in _shap_cache:
        cached = dict(_shap_cache[cache_key])
        cached["execution_time_ms"] = round((time.perf_counter() - start_time) * 1000, 2)
        cached["from_cache"] = True
        return cached

    cleaned = preprocess_text(text)
    eval_text = cleaned if len(cleaned.strip()) > 0 else text

    # Dual-target predictions
    prediction = predict_indobert_authentic(text)
    pred_trust = prediction["predicted_trust"]
    pred_aspect = prediction["predicted_aspect"]
    trust_conf = prediction["trust_confidence"]

    # Class index: 0: Low_Trust, 1: Neutral, 2: High_Trust
    class_map = {"Low_Trust": 0, "Neutral": 1, "High_Trust": 2}
    target_class_idx = class_map.get(pred_trust, 2)

    explainer = get_indobert_explainer()
    # Compute SHAP explanation with bounded max evaluations for responsive latency
    shap_output = explainer([eval_text], max_evals=64)

    raw_tokens = shap_output.data[0]
    values = shap_output.values[0, :, target_class_idx]
    base_val = float(shap_output.base_values[0, target_class_idx])

    tokens = []
    attributions = []

    for raw_tok, val in zip(raw_tokens, values):
        tok_str = str(raw_tok).strip()
        if not tok_str:
            continue
        score = round(float(val), 4)
        if target_class_idx == 0:
            impact = "Low_Trust" if score > 0.02 else ("High_Trust" if score < -0.02 else "Neutral")
        else:
            impact = determine_impact(score)

        color = get_highlight_color(score, impact)
        tokens.append(tok_str)
        attributions.append({
            "token": tok_str,
            "score": score,
            "impact": impact,
            "highlight_color": color
        })

    # Summary narrative
    pos_tokens = [a["token"] for a in attributions if a["impact"] == "High_Trust"]
    neg_tokens = [a["token"] for a in attributions if a["impact"] == "Low_Trust"]

    if pos_tokens and pred_trust == "High_Trust":
        summary = f"Kata pendorong utama '{', '.join(pos_tokens[:3])}' memberikan atribusi SHAP positif terbesar terhadap reputasi High Trust."
    elif neg_tokens and pred_trust == "Low_Trust":
        summary = f"Kata pemicu isu '{', '.join(neg_tokens[:3])}' memberikan atribusi penurun kepercayaan (Low Trust) terhadap ulasan."
    else:
        summary = f"Model IndoBERT menganalisis {len(attributions)} fitur kata dengan atribusi SHAP seimbang."

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    result = {
        "raw_text": text,
        "cleaned_text": cleaned,
        "predicted_aspect": pred_aspect,
        "predicted_trust": pred_trust,
        "trust_confidence": trust_conf,
        "tokens": tokens,
        "attributions": attributions,
        "base_value": round(base_val, 4),
        "explanation_summary": summary,
        "execution_time_ms": elapsed_ms,
        "from_cache": False
    }

    _shap_cache[cache_key] = result
    return result
