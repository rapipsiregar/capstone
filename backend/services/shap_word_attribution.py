"""
Word-level SHAP attribution for the IndoBERT trust model (Task 8.10 / 8.11).

Method (keputusan user 2026-10-28, Opsi A):
- Subword pieces from the SHAP text masker are merged into whole words by summing
  their SHAP values. This is valid because SHAP values are additive.
- Each word is scored as SHAP(High_Trust) - SHAP(Low_Trust), for every review
  regardless of the predicted class. Positive = pushes toward High Trust (pendorong),
  negative = pushes toward Low Trust (pemicu).
"""

import re
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

# Class order follows models/indobert_trust/config.json id2label.
LOW_IDX, NEUTRAL_IDX, HIGH_IDX = 0, 1, 2
IMPACT_THRESHOLD = 0.02
ATTRIBUTION_METHOD = "word_shap_high_minus_low_v1"

# Generic fillers that carry no product meaning; skipped when picking top words.
SEMANTIC_STOPWORDS = {
    "dan", "di", "ke", "dari", "ini", "itu", "buat", "yang", "untuk", "ada",
    "aku", "saya", "kamu", "dia", "mereka", "kita", "nya", "banget", "juga",
    "bisa", "karena", "kalau", "kalo", "udah", "sudah", "tapi", "lagi", "jadi",
    "sama", "agak", "terus", "sih", "dong", "kok", "ya", "kan", "deh", "aja", "saja",
    "pada", "dengan", "atau", "lebih", "paling", "kurang", "selalu", "pernah",
    "haha", "hahaha", "bgttt", "bangettt", "lumayan", "tidak", "cuma", "masih",
    "bgt", "tp", "gitu", "gak", "ngga", "ga", "kali", "baru", "pas"
}


def clean_feature_token(token: str) -> str:
    """Normalizes a token for aggregation: lowercase letters only."""
    return re.sub(r"[^a-zA-Z]", "", token.lower().strip())


def is_meaningful_word(token: str) -> bool:
    tok = clean_feature_token(token)
    return len(tok) >= 3 and tok not in SEMANTIC_STOPWORDS


def merge_subword_values(
    raw_tokens: Sequence[str], values: np.ndarray
) -> List[Tuple[str, np.ndarray]]:
    """
    Joins subword pieces into words. A piece ending in whitespace closes the word,
    as produced by shap.maskers.Text. Values of the pieces are summed per class.
    """
    words: List[Tuple[str, np.ndarray]] = []
    buf, acc = "", np.zeros(values.shape[1], dtype=float)
    for tok, val in zip(raw_tokens, values):
        piece = str(tok)
        if piece.strip():
            buf += piece.strip()
            acc = acc + np.asarray(val, dtype=float)
        if piece[-1:].isspace() and buf:
            words.append((buf, acc))
            buf, acc = "", np.zeros(values.shape[1], dtype=float)
    if buf:
        words.append((buf, acc))
    return words


def _impact(score: float) -> str:
    if score > IMPACT_THRESHOLD:
        return "High_Trust"
    if score < -IMPACT_THRESHOLD:
        return "Low_Trust"
    return "Neutral"


def build_direction_attributions(
    raw_tokens: Sequence[str], values: np.ndarray
) -> List[Dict[str, Any]]:
    """Returns one attribution per word with score = SHAP(High) - SHAP(Low)."""
    attributions = []
    for word, vec in merge_subword_values(raw_tokens, values):
        score = round(float(vec[HIGH_IDX] - vec[LOW_IDX]), 4)
        attributions.append({"token": word, "score": score, "impact": _impact(score)})
    return attributions


def select_top_words(attributions: List[Dict[str, Any]], k: int = 5) -> Tuple[List[str], List[str]]:
    """Top-k meaningful High Trust and Low Trust words, strongest first."""
    usable = [a for a in attributions if is_meaningful_word(a["token"])]
    pos = sorted((a for a in usable if a["impact"] == "High_Trust"), key=lambda a: -a["score"])
    neg = sorted((a for a in usable if a["impact"] == "Low_Trust"), key=lambda a: a["score"])
    return [a["token"] for a in pos[:k]], [a["token"] for a in neg[:k]]


def compute_word_shap_record(text: str, text_hash: str) -> Dict[str, Any]:
    """Runs IndoBERT SHAP on one review and returns a cache record (word-level, direction score)."""
    from backend.services.indobert_explainer import get_indobert_explainer
    from backend.services.indobert_predictor import predict_indobert_authentic
    from backend.services.preprocessor import preprocess_text

    cleaned = preprocess_text(text)
    eval_text = cleaned if cleaned.strip() else text
    prediction = predict_indobert_authentic(text)
    output = get_indobert_explainer()([eval_text], max_evals=64)

    attributions = build_direction_attributions(output.data[0], output.values[0])
    pos, neg = select_top_words(attributions)
    base = output.base_values[0]
    if pos and neg:
        summary = f"Pendorong kepercayaan: {', '.join(pos[:3])}. Pemicu keraguan: {', '.join(neg[:3])}."
    elif pos:
        summary = f"Pendorong kepercayaan: {', '.join(pos[:3])}."
    elif neg:
        summary = f"Pemicu keraguan: {', '.join(neg[:3])}."
    else:
        summary = "Tidak ada kata dengan atribusi SHAP di atas ambang 0,02."

    return {
        "text_hash": text_hash,
        "raw_text": text,
        "attribution_method": ATTRIBUTION_METHOD,
        "predicted_trust": prediction["predicted_trust"],
        "predicted_aspect": prediction["predicted_aspect"],
        "trust_confidence": prediction["trust_confidence"],
        "base_value": round(float(base[HIGH_IDX] - base[LOW_IDX]), 4),
        "attributions": attributions,
        "top_positive_words": pos,
        "top_negative_words": neg,
        "explanation_summary": summary,
    }
