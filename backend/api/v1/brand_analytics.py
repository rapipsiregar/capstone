"""
Brand & Category Analytics REST API Endpoint.
Provides real-time trust sentiment ratios, aspect distributions,
and brand breakdown statistics for Female Daily Halal Cosmetics dataset.
"""

import os
import pandas as pd
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from backend.services.empirical_drivers import compute_empirical_trust_drivers

router = APIRouter(tags=["Analytics"])

ANNOTATED_CSV_PATH = os.path.join("data", "annotated", "female_daily_skincare_annotated.csv")
CLEANED_CSV_PATH = os.path.join("data", "cleaned", "female_daily_skincare_cleaned.csv")


def get_active_dataset_dataframe() -> pd.DataFrame:
    """Helper to load active annotated/cleaned dataset DataFrame."""
    if os.path.exists(ANNOTATED_CSV_PATH):
        return pd.read_csv(ANNOTATED_CSV_PATH)
    elif os.path.exists(CLEANED_CSV_PATH):
        return pd.read_csv(CLEANED_CSV_PATH)
    else:
        # Return fallback sample dataframe
        return pd.DataFrame([
            {
                "merek_umkm": "Wardah",
                "nama_produk": "Lightening Night Cream",
                "kategori_produk": "Night Cream",
                "label_kepercayaan": "High_Trust",
                "aspek_komunikasi": "Sertifikasi_Halal_BPOM"
            },
            {
                "merek_umkm": "Emina",
                "nama_produk": "Sun Battle SPF 30",
                "kategori_produk": "Sun Protection",
                "label_kepercayaan": "Low_Trust",
                "aspek_komunikasi": "Kandungan_Bahan_Sensitivitas"
            }
        ])


@router.get("/analytics/brands", response_model=Dict[str, Any])
async def get_brand_analytics(
    brand: Optional[str] = Query(None, description="Filter specific brand name"),
    category: Optional[str] = Query(None, description="Filter specific category name")
) -> Dict[str, Any]:
    """
    GET /api/v1/analytics/brands
    Returns aggregated public trust analytics per brand, products breakdown, and skincare product category.
    """
    df = get_active_dataset_dataframe()
    
    brand_col = "merek_umkm" if "merek_umkm" in df.columns else ("Merk" if "Merk" in df.columns else "")
    trust_col = "label_kepercayaan" if "label_kepercayaan" in df.columns else ("label_sentimen" if "label_sentimen" in df.columns else "")
    aspect_col = "aspek_komunikasi" if "aspek_komunikasi" in df.columns else ""
    cat_col = "kategori_produk" if "kategori_produk" in df.columns else ("Category" if "Category" in df.columns else "")
    prod_col = "nama_produk" if "nama_produk" in df.columns else ""
    
    if not brand_col or not trust_col:
        raise HTTPException(status_code=500, detail="Required dataset columns missing for brand analytics.")

    if category and category.strip() and category.strip().upper() != "ALL" and cat_col:
        df = df[df[cat_col].str.strip().str.lower() == category.strip().lower()]

    total_reviews = len(df)
    unique_brands = df[brand_col].nunique()
    unique_categories = df[cat_col].nunique() if cat_col else 0

    all_dataset_brands = sorted(
        [str(b) for b in get_active_dataset_dataframe()[brand_col].dropna().unique().tolist()],
        key=lambda s: s.lower()
    )

    if brand and brand.strip() and brand.strip().upper() != "ALL":
        target_brands = df[df[brand_col].str.strip().str.lower() == brand.strip().lower()][brand_col].unique().tolist()
    else:
        target_brands = df[brand_col].value_counts().head(30).index.tolist()

    brands_summary: List[Dict[str, Any]] = []


    # Vectorized aggregations for maximum speed (<50ms)
    high_mask = df[trust_col] == "High_Trust"
    low_mask = df[trust_col] == "Low_Trust"
    neutral_mask = df[trust_col] == "Neutral"

    b_counts = df[brand_col].value_counts()
    b_high = df[high_mask].groupby(brand_col).size()
    b_low = df[low_mask].groupby(brand_col).size()
    b_neutral = df[neutral_mask].groupby(brand_col).size()

    # Precompute aspect distributions and top aspects per brand if aspect_col exists
    brand_aspect_counts = df.groupby([brand_col, aspect_col]).size() if aspect_col else None
    bp_counts = df.groupby([brand_col, prod_col]).size() if prod_col else None
    bp_high = df[high_mask].groupby([brand_col, prod_col]).size() if prod_col else None

    for b_name in target_brands:
        b_count = int(b_counts.get(b_name, 0))
        if b_count == 0:
            continue

        high_trust = int(b_high.get(b_name, 0))
        low_trust = int(b_low.get(b_name, 0))
        neutral = int(b_neutral.get(b_name, 0))

        # Brand aspect distribution
        aspect_dist = {}
        top_asp = "Klaim_Efikasi_Manfaat"
        if brand_aspect_counts is not None:
            try:
                aspect_series = brand_aspect_counts.loc[b_name]
                aspect_dist = aspect_series.to_dict()
                if not aspect_series.empty:
                    top_asp = str(aspect_series.idxmax())
            except KeyError:
                pass

        products_list: List[Dict[str, Any]] = []
        if bp_counts is not None:
            try:
                b_prods = bp_counts.loc[b_name].sort_values(ascending=False)
                for p_name, p_rev_count in b_prods.items():
                    p_high = int(bp_high.get((b_name, p_name), 0)) if bp_high is not None else 0
                    products_list.append({
                        "product_name": str(p_name),
                        "total_reviews": int(p_rev_count),
                        "high_trust_ratio": round(float(p_high / p_rev_count), 4) if p_rev_count > 0 else 0.0,
                        "top_aspect": str(top_asp)
                    })
            except KeyError:
                pass

        brands_summary.append({
            "brand_name": str(b_name),
            "total_reviews": int(b_count),
            "high_trust_ratio": round(float(high_trust / b_count), 4) if b_count > 0 else 0.0,
            "low_trust_ratio": round(float(low_trust / b_count), 4) if b_count > 0 else 0.0,
            "neutral_ratio": round(float(neutral / b_count), 4) if b_count > 0 else 0.0,
            "top_aspect": str(top_asp),
            "aspect_distribution": aspect_dist,
            "products": products_list
        })

    category_summary: List[Dict[str, Any]] = []
    if cat_col:
        top_cats = df[cat_col].value_counts().head(10).to_dict()
        for cat_name, cat_count in top_cats.items():
            category_summary.append({
                "category_name": str(cat_name),
                "review_count": int(cat_count)
            })

    # Overall metrics for the current filtered scope (supports ALL brands with specific Category)
    overall_aspects = df[aspect_col].value_counts().to_dict() if aspect_col else {}
    overall_trust = df[trust_col].value_counts().to_dict() if trust_col else {}
    overall_high = overall_trust.get("High_Trust", overall_trust.get("Positif", 0))
    overall_top_aspect = df[aspect_col].mode()[0] if aspect_col and not df[aspect_col].empty else "Klaim_Efikasi_Manfaat"
    
    # Products available in current filtered scope (fully vectorized, 0ms)
    all_filtered_products: List[Dict[str, Any]] = []
    if prod_col:
        p_counts = df[prod_col].value_counts()
        p_high_counts = df[high_mask].groupby(prod_col).size()
        for p_name, p_cnt in p_counts.items():
            p_high = int(p_high_counts.get(p_name, 0))
            all_filtered_products.append({
                "product_name": str(p_name),
                "total_reviews": int(p_cnt),
                "high_trust_ratio": round(float(p_high / p_cnt), 4) if p_cnt > 0 else 0.0,
                "top_aspect": str(overall_top_aspect)
            })

    # Dynamic Empirical Trust Drivers with caching (cache_key based on filter)
    driver_df = df
    if brand and brand.strip() and brand.strip().upper() != "ALL":
        driver_df = df[df[brand_col].str.strip().str.lower() == brand.strip().lower()]

    driver_cache_key = f"{brand or 'ALL'}_{category or 'ALL'}"
    empirical_drivers = compute_empirical_trust_drivers(driver_df, top_k=5, cache_key=driver_cache_key)

    has_halal = "klaim_halal" in driver_df.columns
    has_bpom = "klaim_bpom" in driver_df.columns
    either_mask = (driver_df["klaim_halal"] == 1) | (driver_df["klaim_bpom"] == 1) if (has_halal and has_bpom) else pd.Series(False, index=driver_df.index)
    comp_total = len(driver_df)
    comp_count = int(either_mask.sum())
    comp_ratio = round(float(comp_count / comp_total), 4) if comp_total > 0 else 0.0

    compliance_data = {
        "halal_count": int((driver_df["klaim_halal"] == 1).sum()) if has_halal else 0,
        "bpom_count": int((driver_df["klaim_bpom"] == 1).sum()) if has_bpom else 0,
        "either_count": comp_count,
        "total_reviews": comp_total,
        "compliance_ratio": comp_ratio,
        "compliance_percentage": f"{round(comp_ratio * 100, 1)}%"
    }

    return {
        "status": "success",
        "total_reviews": total_reviews,
        "total_brands": unique_brands,
        "total_categories": unique_categories,
        "high_trust_ratio": round(float(overall_high / total_reviews), 4) if total_reviews > 0 else 0.0,
        "top_aspect": str(overall_top_aspect),
        "aspect_distribution": overall_aspects,
        "trust_counts": {
            "High_Trust": int(overall_trust.get("High_Trust", 0)),
            "Low_Trust": int(overall_trust.get("Low_Trust", 0)),
            "Neutral": int(overall_trust.get("Neutral", 0))
        },
        "trust_drivers": empirical_drivers,
        "compliance": compliance_data,
        "all_brands": all_dataset_brands,
        "all_products": all_filtered_products,
        "brands_summary": brands_summary,
        "category_summary": category_summary
    }



