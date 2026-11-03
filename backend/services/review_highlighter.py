"""
Inline SHAP highlighter for catalog review text.

Only words from the precomputed IndoBERT SHAP cache of that exact review are marked.
When a review has no cached attribution, the text is returned unmarked (no static
word-list fallback, finding F28).
"""

import html
import re
from backend.services.catalog_shap_cacher import get_cached_review_shap


def highlight_keywords(text: str) -> str:
    """Wraps cached positive/negative SHAP words in green/red highlight spans."""
    if not isinstance(text, str) or not text:
        return ""
    cached = get_cached_review_shap(text) or {}
    res = html.escape(text, quote=False)  # review text is inserted as HTML by the frontend
    for kw in cached.get("top_positive_words", []):
        if kw and len(kw) > 1:
            res = re.sub(rf"\b({re.escape(kw)})\b", r'<span class="xai-highlight-green">\1</span>', res, flags=re.IGNORECASE)
    for kw in cached.get("top_negative_words", []):
        if kw and len(kw) > 1:
            res = re.sub(rf"\b({re.escape(kw)})\b", r'<span class="xai-highlight-red">\1</span>', res, flags=re.IGNORECASE)
    return res
