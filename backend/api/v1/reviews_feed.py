"""
Real Female Daily Reviews Feed REST API Endpoint.
Serves real reviews from data/annotated/female_daily_skincare_annotated.csv
with multi-parameter filtering (brand, category, rating, trust, search) and pagination.
"""

import os
import re
import pandas as pd
from typing import Dict, Any, List, Optional
from functools import lru_cache
from fastapi import APIRouter, Query
from backend.services.review_explainer import generate_review_xai_explanation

router = APIRouter(tags=["Reviews Feed"])

DATASET_CSV = os.path.join("data", "annotated", "female_daily_skincare_annotated.csv")

HIGH_TRUST_WORDS = ["bpom", "halal", "mui", "original", "resmi", "melembabkan", "mencerahkan", "bagus", "cocok", "segel", "ringan", "alami"]
LOW_TRUST_WORDS = ["breakout", "beruntusan", "bruntusan", "iritasi", "gatal", "panas", "perih", "bocor", "penyok", "meragukan", "palsu"]


@lru_cache(maxsize=1)
def load_cached_reviews_dataframe() -> pd.DataFrame:
    """Loads and caches the 10,826 Female Daily skincare dataset."""
    if os.path.exists(DATASET_CSV):
        df = pd.read_csv(DATASET_CSV)
    else:
        df = pd.DataFrame(columns=[
            "merek_umkm", "nama_produk", "kategori_produk", "penulis_ulasan",
            "kondisi_kulit_usia", "rating_bintang", "status_rekomendasi",
            "teks_ulasan_mentah", "aspek_komunikasi", "label_kepercayaan"
        ])
    return df


def highlight_xai_shap_inline(text: str) -> str:
    """Injects SHAP XAI inline span classes for trust keywords."""
    if not isinstance(text, str) or not text:
        return ""
    res = text
    for kw in HIGH_TRUST_WORDS:
        res = re.sub(rf"\b({re.escape(kw)})\b", r'<span class="xai-highlight-green">\1</span>', res, flags=re.IGNORECASE)
    for kw in LOW_TRUST_WORDS:
        res = re.sub(rf"\b({re.escape(kw)})\b", r'<span class="xai-highlight-red">\1</span>', res, flags=re.IGNORECASE)
    return res


@router.get("/reviews/feed")
def get_reviews_feed(
    brand: str = Query("ALL"),
    category: str = Query("ALL"),
    rating: str = Query("ALL"),
    trust: str = Query("ALL"),
    search: str = Query(""),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
) -> Dict[str, Any]:
    """
    Returns real review cards from Female Daily dataset with active filtering & pagination.
    """
    df = load_cached_reviews_dataframe()
    total_dataset = len(df)

    # Filtering pipeline
    filtered = df
    if brand and brand != "ALL":
        filtered = filtered[filtered["merek_umkm"].astype(str).str.lower().str.contains(brand.lower(), regex=False)]
    if category and category != "ALL":
        filtered = filtered[filtered["kategori_produk"].astype(str).str.lower() == category.lower()]
    if rating and rating != "ALL":
        try:
            r_int = int(rating)
            filtered = filtered[filtered["rating_bintang"].fillna(0).astype(float).astype(int) == r_int]
        except ValueError:
            pass
    if trust and trust != "ALL":
        filtered = filtered[filtered["label_kepercayaan"].astype(str) == trust]
    if search:
        s_lower = search.lower()
        mask = (
            filtered["teks_ulasan_mentah"].astype(str).str.lower().str.contains(s_lower, regex=False) |
            filtered["nama_produk"].astype(str).str.lower().str.contains(s_lower, regex=False) |
            filtered["merek_umkm"].astype(str).str.lower().str.contains(s_lower, regex=False)
        )
        filtered = filtered[mask]

    filtered_count = len(filtered)
    total_pages = max(1, (filtered_count + limit - 1) // limit)
    offset = (page - 1) * limit
    page_df = filtered.iloc[offset:offset + limit]

    reviews: List[Dict[str, Any]] = []
    for idx, row in page_df.iterrows():
        raw_text = str(row.get("teks_ulasan_mentah", ""))
        xai_exp = generate_review_xai_explanation(row.to_dict(), raw_text)
        reviews.append({
            "id": int(idx) + 1,
            "brand": str(row.get("merek_umkm", "Unknown")),
            "product": str(row.get("nama_produk", "Produk Kosmetik")),
            "category": str(row.get("kategori_produk", "Skincare")),
            "rating": float(row.get("rating_bintang", 5.0)),
            "user": str(row.get("penulis_ulasan", f"Pengulas #{idx+1}")),
            "age_skin": str(row.get("kondisi_kulit_usia", "Kulit Normal")),
            "trust": str(row.get("label_kepercayaan", "High_Trust")),
            "aspect": str(row.get("aspek_komunikasi", "Klaim_Efikasi_Manfaat")),
            "text": raw_text,
            "highlighted_text": highlight_xai_shap_inline(raw_text),
            "halal_claim": bool(row.get("klaim_halal", False)),
            "bpom_claim": bool(row.get("klaim_bpom", False)),
            "xai_explanation": xai_exp
        })

    return {
        "total_dataset": total_dataset,
        "filtered_count": filtered_count,
        "page": page,
        "total_pages": total_pages,
        "limit": limit,
        "reviews": reviews
    }
