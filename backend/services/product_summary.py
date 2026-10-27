"""
Per-product trust parameter summary (Task 6.5).
Computes KPI and distribution values from ALL reviews of one product, as-is.
Category keys (aspects / trust labels) are taken from the full dataset so
zero-count categories are kept as 0 instead of hidden.
"""

from typing import Any, Dict, List
import pandas as pd

ASPECT_COL = "aspek_komunikasi"
TRUST_COL = "label_kepercayaan"
HIGH_TRUST_LABEL = "High_Trust"


def _distribution(full_df: pd.DataFrame, subset: pd.DataFrame, col: str) -> Dict[str, int]:
    """Counts per category for `subset`, using every category present in `full_df`."""
    if col not in full_df.columns:
        return {}
    keys = sorted(str(k) for k in full_df[col].dropna().unique())
    counts = subset[col].astype(str).value_counts().to_dict() if col in subset.columns else {}
    return {k: int(counts.get(k, 0)) for k in keys}


def _dominant(dist: Dict[str, int]) -> List[str]:
    """All categories sharing the highest non-zero count (ties are kept honestly)."""
    if not dist:
        return []
    top = max(dist.values())
    if top == 0:
        return []
    return [k for k, v in dist.items() if v == top]


def build_product_summary(full_df: pd.DataFrame, matched: pd.DataFrame) -> Dict[str, Any]:
    """Returns trust/aspect distributions, % High Trust and dominant aspect(s)."""
    trust_dist = _distribution(full_df, matched, TRUST_COL)
    aspect_dist = _distribution(full_df, matched, ASPECT_COL)
    total = len(matched)
    high = trust_dist.get(HIGH_TRUST_LABEL, 0)
    return {
        "trust_distribution": trust_dist,
        "aspect_distribution": aspect_dist,
        "high_trust_pct": round(high / total * 100, 1) if total else 0.0,
        "dominant_aspects": _dominant(aspect_dist),
    }
