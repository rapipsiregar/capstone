"""
Explainable AI (XAI) SHAP Attribution Service for Halal Cosmetics NLP.
Delegates to authentic IndoBERT explainer service (backend.services.indobert_explainer).
Legacy joblib, TF-IDF vectorizer, and linear coefficients are completely removed (Task 8.14).
"""

from typing import Dict, Any, List
from backend.services.indobert_explainer import (
    explain_text_with_shap,
    get_highlight_color as explainer_highlight_color,
    determine_impact as explainer_determine_impact,
)


def get_highlight_color(score: float, threshold: float = 0.05) -> str:
    """Returns hex color code based on SHAP contribution score."""
    if score > threshold:
        return "#28a745"
    elif score < -threshold:
        return "#dc3545"
    return "#ffc107"


def get_impact_label(score: float, threshold: float = 0.05) -> str:
    """Categorizes token impact into High_Trust, Low_Trust, or Neutral."""
    if score > threshold:
        return "High_Trust"
    elif score < -threshold:
        return "Low_Trust"
    return "Neutral"


def format_shap_attributions(tokens: List[str], scores: List[float]) -> List[Dict[str, Any]]:
    """Formats token strings and SHAP numerical scores into structured attribution dicts."""
    attributions = []
    for token, score in zip(tokens, scores):
        rounded_score = round(float(score), 4)
        attributions.append({
            "token": token,
            "score": rounded_score,
            "impact": get_impact_label(rounded_score),
            "highlight_color": get_highlight_color(rounded_score)
        })
    return attributions


def explain_text_shap(
    text: str,
    model_dir: str = "models/indobert_halal"
) -> Dict[str, Any]:
    """
    Generates authentic Explainable AI (XAI) word-level SHAP attribution values
    using fine-tuned IndoBERT Transformer model.
    """
    return explain_text_with_shap(text)
