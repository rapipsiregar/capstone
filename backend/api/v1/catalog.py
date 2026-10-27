"""
Dynamic Skincare Catalog REST API Endpoint.
Powers the 3-Level Drill-Down Catalog (Category -> Products -> Reviews & XAI).
100% Dynamic from authentic female_daily_skincare_annotated.csv dataset.
"""

import os
import re
import pandas as pd
from typing import Dict, Any, List, Optional
from functools import lru_cache
from fastapi import APIRouter, Query, HTTPException
from backend.services.review_explainer import generate_review_xai_explanation
from backend.services.product_summary import build_product_summary
from backend.services.catalog_shap_cacher import get_cached_review_shap

router = APIRouter(prefix="/catalog", tags=["Catalog"])

DATASET_CSV = os.path.join("data", "annotated", "female_daily_skincare_annotated.csv")

HIGH_TRUST_WORDS = ["bpom", "halal", "mui", "original", "resmi", "melembabkan", "mencerahkan", "bagus", "cocok", "segel", "ringan", "alami"]
LOW_TRUST_WORDS = ["breakout", "beruntusan", "bruntusan", "iritasi", "gatal", "panas", "perih", "bocor", "penyok", "meragukan", "palsu"]


@lru_cache(maxsize=1)
def load_dataset_dataframe() -> pd.DataFrame:
    """Loads and caches authentic annotated dataset."""
    if os.path.exists(DATASET_CSV):
        return pd.read_csv(DATASET_CSV)
    return pd.DataFrame(columns=[
        "merek_umkm", "nama_produk", "kategori_produk", "penulis_ulasan",
        "kondisi_kulit_usia", "rating_bintang", "status_rekomendasi",
        "teks_ulasan_mentah", "aspek_komunikasi", "label_kepercayaan"
    ])


def highlight_keywords(text: str) -> str:
    """Highlights SHAP trust words in review text, prioritizing authentic cached SHAP attributions."""
    if not isinstance(text, str) or not text:
        return ""
    cached = get_cached_review_shap(text)
    pos = cached.get("top_positive_words", []) if cached else HIGH_TRUST_WORDS
    neg = cached.get("top_negative_words", []) if cached else LOW_TRUST_WORDS
    res = text
    for kw in pos:
        if kw and len(kw) > 1:
            res = re.sub(rf"\b({re.escape(kw)})\b", r'<span class="xai-highlight-green">\1</span>', res, flags=re.IGNORECASE)
    for kw in neg:
        if kw and len(kw) > 1:
            res = re.sub(rf"\b({re.escape(kw)})\b", r'<span class="xai-highlight-red">\1</span>', res, flags=re.IGNORECASE)
    return res


@router.get("/categories")
def get_catalog_categories() -> Dict[str, Any]:
    """Level 1: Returns all unique skincare categories with product & review counts."""
    df = load_dataset_dataframe()
    if df.empty:
        return {"status": "success", "total_categories": 0, "categories": []}

    grouped = df.groupby("kategori_produk")
    categories_list = []

    for cat_name, group in grouped:
        prod_count = int(group["nama_produk"].nunique())
        rev_count = len(group)
        avg_rating = round(float(group["rating_bintang"].mean()), 2) if "rating_bintang" in group.columns else 4.5
        top_brand = str(group["merek_umkm"].mode()[0]) if "merek_umkm" in group.columns and not group["merek_umkm"].empty else ""

        categories_list.append({
            "category_name": str(cat_name),
            "product_count": prod_count,
            "review_count": rev_count,
            "avg_rating": avg_rating,
            "top_brand": top_brand,
            "slug": re.sub(r'[^a-zA-Z0-9]+', '-', str(cat_name)).lower().strip('-')
        })

    # Sort descending by review count
    categories_list.sort(key=lambda x: x["review_count"], reverse=True)

    return {
        "status": "success",
        "total_categories": len(categories_list),
        "categories": categories_list
    }


@router.get("/products")
def get_catalog_products(
    category: Optional[str] = Query(None, description="Category name to filter"),
    brand: Optional[str] = Query(None, description="Brand name to filter"),
    search: Optional[str] = Query("", description="Optional search keyword"),
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=50)
) -> Dict[str, Any]:
    """Level 2: Returns products for the selected category/brand with review metrics."""
    df = load_dataset_dataframe()
    if df.empty:
        return {"status": "success", "category": category or "", "brand": brand or "", "total_products": 0, "products": []}

    filtered = df
    if category and category.strip():
        filtered = filtered[filtered["kategori_produk"].str.strip().str.lower() == category.strip().lower()]

    if brand and brand.strip():
        filtered = filtered[filtered["merek_umkm"].str.strip().str.lower() == brand.strip().lower()]

    matched_categories: List[Dict[str, Any]] = []
    matched_brands: List[Dict[str, Any]] = []

    if search and search.strip():
        q = search.strip().lower()
        filtered = filtered[
            filtered["nama_produk"].str.lower().str.contains(q, na=False) |
            filtered["merek_umkm"].str.lower().str.contains(q, na=False) |
            filtered["kategori_produk"].str.lower().str.contains(q, na=False)
        ]
        for cat in df[df["kategori_produk"].str.lower().str.contains(q, na=False)]["kategori_produk"].unique():
            sub = df[df["kategori_produk"] == cat]
            matched_categories.append({"category_name": str(cat), "product_count": int(sub["nama_produk"].nunique())})
        for b in df[df["merek_umkm"].str.lower().str.contains(q, na=False)]["merek_umkm"].value_counts().index[:5]:
            sub = df[df["merek_umkm"] == b]
            matched_brands.append({"brand_name": str(b), "product_count": int(sub["nama_produk"].nunique()), "review_count": len(sub)})

    if filtered.empty:
        return {
            "status": "success",
            "category": category or "",
            "brand": brand or "",
            "matched_categories": matched_categories,
            "matched_brands": matched_brands,
            "total_products": 0,
            "page": page,
            "total_pages": 0,
            "products": []
        }

    grouped = filtered.groupby(["merek_umkm", "nama_produk"])
    products_list = []

    for (brand, prod_name), group in grouped:
        rev_count = len(group)
        avg_rating = round(float(group["rating_bintang"].mean()), 2) if "rating_bintang" in group.columns else 4.5
        high_trust = int((group["label_kepercayaan"] == "High_Trust").sum()) if "label_kepercayaan" in group.columns else 0
        halal_claimed = bool((group["klaim_halal"] == 1).any()) if "klaim_halal" in group.columns else False
        bpom_claimed = bool((group["klaim_bpom"] == 1).any()) if "klaim_bpom" in group.columns else False

        products_list.append({
            "brand_name": str(brand),
            "product_name": str(prod_name),
            "category_name": str(group["kategori_produk"].iloc[0]),
            "review_count": rev_count,
            "avg_rating": avg_rating,
            "high_trust_ratio": round(float(high_trust / rev_count), 2) if rev_count > 0 else 0.0,
            "halal_claim": halal_claimed,
            "bpom_claim": bpom_claimed
        })

    products_list.sort(key=lambda x: x["review_count"], reverse=True)
    total_prods = len(products_list)
    total_pages = max(1, (total_prods + limit - 1) // limit)
    start_idx = (page - 1) * limit
    paginated_prods = products_list[start_idx:start_idx + limit]

    return {
        "status": "success",
        "category": category or "",
        "brand": brand or "",
        "matched_categories": matched_categories,
        "matched_brands": matched_brands,
        "total_products": total_prods,
        "page": page,
        "total_pages": total_pages,
        "products": paginated_prods
    }


@router.get("/reviews")
def get_catalog_product_reviews(
    product_name: str = Query(..., description="Full product name"),
    page: int = Query(1, ge=1),
    limit: int = Query(8, ge=1, le=50)
) -> Dict[str, Any]:
    """Level 3: Returns customer reviews + XAI explanations for specific product."""
    df = load_dataset_dataframe()
    if df.empty:
        raise HTTPException(status_code=404, detail="Dataset not found")

    p_clean = product_name.strip().lower()
    matched = df[df["nama_produk"].str.strip().str.lower() == p_clean]

    if matched.empty:
        # Partial match fallback
        matched = df[df["nama_produk"].str.strip().str.lower().str.contains(re.escape(p_clean), na=False)]

    if matched.empty:
        return {"status": "success", "product_info": {}, "total_reviews": 0, "reviews": []}

    prod_info = {
        "product_name": str(matched["nama_produk"].iloc[0]),
        "brand_name": str(matched["merek_umkm"].iloc[0]),
        "category_name": str(matched["kategori_produk"].iloc[0]),
        "total_reviews": len(matched),
        "avg_rating": round(float(matched["rating_bintang"].mean()), 2) if "rating_bintang" in matched.columns else 5.0,
        "halal_claim": bool((matched["klaim_halal"] == 1).any()) if "klaim_halal" in matched.columns else False,
        "bpom_claim": bool((matched["klaim_bpom"] == 1).any()) if "klaim_bpom" in matched.columns else False
    }
    prod_info.update(build_product_summary(df, matched))

    total_reviews = len(matched)
    total_pages = max(1, (total_reviews + limit - 1) // limit)
    start_idx = (page - 1) * limit
    page_df = matched.iloc[start_idx:start_idx + limit]

    reviews_list = []
    for _, row in page_df.iterrows():
        raw_text = str(row.get("teks_ulasan_mentah", "") or row.get("teks_ulasan_bersih", ""))
        trust_label = str(row.get("label_kepercayaan", "Neutral"))
        skin_age = str(row.get("kondisi_kulit_usia", "Kulit Normal"))
        brand_str = str(row.get("merek_umkm", prod_info["brand_name"]))
        highlighted = highlight_keywords(raw_text)

        # Generate XAI Contextual Explanation
        review_dict = {
            "label_kepercayaan": trust_label,
            "aspek_komunikasi": str(row.get("aspek_komunikasi", "Klaim_Efikasi_Manfaat")),
            "merek_umkm": brand_str,
            "kondisi_kulit_usia": skin_age
        }
        xai_exp = generate_review_xai_explanation(review_dict, raw_text)

        reviews_list.append({
            "user": str(row.get("penulis_ulasan", "Pengguna")),
            "age_skin": skin_age,
            "rating": float(row.get("rating_bintang", 5.0)),
            "trust": trust_label,
            "aspect": str(row.get("aspek_komunikasi", "Klaim_Efikasi_Manfaat")),
            "text": raw_text,
            "highlighted_text": highlighted,
            "xai_explanation": xai_exp
        })

    return {
        "status": "success",
        "product_info": prod_info,
        "total_reviews": total_reviews,
        "page": page,
        "total_pages": total_pages,
        "reviews": reviews_list
    }
