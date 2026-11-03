"""
Brand directory service for the V4 Rose Blush catalog (homepage + brand page).

Every value is aggregated from the annotated Female Daily dataset as-is:
- halal/BPOM "mentions" count reviews whose text names a halal/BPOM claim
  (columns klaim_halal / klaim_bpom); they are not official certificates.
- photo paths are only returned when the packshot file really exists.
"""

import os
import re
from typing import Any, Dict, List, Optional

import pandas as pd

PHOTO_DIR = os.path.join("frontend", "images", "products")
BRAND, PRODUCT, CATEGORY, RATING = "merek_umkm", "nama_produk", "kategori_produk", "rating_bintang"
HALAL, BPOM, TRUST = "klaim_halal", "klaim_bpom", "label_kepercayaan"


def product_slug(brand: str, product: str) -> str:
    """Same slug rule as the frontend: lowercase, non-alphanumerics collapsed to '-'."""
    return re.sub(r"[^a-z0-9]+", "-", f"{brand}-{product}".lower()).strip("-")


def product_photo(brand: str, product: str) -> Optional[str]:
    """Relative URL of the real packshot, or None when no verified photo exists."""
    slug = product_slug(brand, product)
    if os.path.exists(os.path.join(PHOTO_DIR, f"{slug}.jpg")):
        return f"./images/products/{slug}.jpg"
    return None


def _mentions(sub: pd.DataFrame, col: str) -> int:
    return int((sub[col] == 1).sum()) if col in sub.columns else 0


def _split_categories(category: Optional[str]) -> List[str]:
    if not category:
        return []
    return [c.strip().lower() for c in str(category).split(",") if c.strip()]


def _brand_row(name: str, sub: pd.DataFrame) -> Dict[str, Any]:
    counts = sub[PRODUCT].value_counts()
    top_name = str(counts.index[0])
    top = sub[sub[PRODUCT] == top_name]
    return {
        "brand_name": str(name),
        "product_count": int(sub[PRODUCT].nunique()),
        "review_count": int(len(sub)),
        "avg_rating": round(float(sub[RATING].mean()), 2),
        "halal_mentions": _mentions(sub, HALAL),
        "bpom_mentions": _mentions(sub, BPOM),
        "top_product": {
            "product_name": top_name,
            "category_name": str(top[CATEGORY].iloc[0]),
            "review_count": int(len(top)),
            "avg_rating": round(float(top[RATING].mean()), 2),
            "photo": product_photo(str(name), top_name),
        },
    }


def build_brand_directory(df: pd.DataFrame, category: Optional[str] = None, halal: bool = False,
                          bpom: bool = False, min_rating: Optional[float] = None, search: str = "",
                          page: int = 1, limit: int = 12) -> Dict[str, Any]:
    """Faceted, paginated brand list sorted by review volume."""
    full_cats = df.groupby(CATEGORY).agg(brand_count=(BRAND, "nunique"), product_count=(PRODUCT, "nunique"))
    facets_categories = [
        {"category_name": str(k), "brand_count": int(v.brand_count), "product_count": int(v.product_count)}
        for k, v in full_cats.sort_values("brand_count", ascending=False).iterrows()
    ]

    scope = df
    cats = _split_categories(category)
    if cats:
        scope = scope[scope[CATEGORY].str.strip().str.lower().isin(cats)]
    if search and search.strip():
        scope = scope[scope[BRAND].str.lower().str.contains(search.strip().lower(), na=False, regex=False)]

    grouped = scope.groupby(BRAND)
    stats = grouped.agg(avg=(RATING, "mean"), reviews=(RATING, "size"))
    halal_brands = set(scope[scope[HALAL] == 1][BRAND]) if HALAL in scope.columns else set()
    bpom_brands = set(scope[scope[BPOM] == 1][BRAND]) if BPOM in scope.columns else set()

    keep = stats.index.to_series()
    if halal:
        keep = keep[keep.isin(halal_brands)]
    if bpom:
        keep = keep[keep.isin(bpom_brands)]
    if min_rating is not None:
        keep = keep[keep.map(lambda b: stats.loc[b, "avg"] >= min_rating)]

    ordered = stats.loc[keep.index].sort_values("reviews", ascending=False).index.tolist()
    total = len(ordered)
    total_pages = max(1, -(-total // limit))
    page_names = ordered[(page - 1) * limit:(page - 1) * limit + limit]
    in_scope = scope[scope[BRAND].isin(ordered)]

    return {
        "status": "success",
        "total_brands": total,
        "total_products": int(in_scope[PRODUCT].nunique()),
        "total_reviews": int(len(in_scope)),
        "page": page,
        "total_pages": total_pages,
        "brands": [_brand_row(n, grouped.get_group(n)) for n in page_names],
        "facets": {
            "brand_names": sorted((str(b) for b in df[BRAND].dropna().unique()), key=str.lower),
            "categories": facets_categories,
            "halal_brands": len(halal_brands),
            "bpom_brands": len(bpom_brands),
            "rating_4_brands": int((stats["avg"] >= 4).sum()),
        },
    }


def build_brand_profile(df: pd.DataFrame, brand: str) -> Optional[Dict[str, Any]]:
    """Header numbers and category facet for one brand page; None when the brand is unknown."""
    sub = df[df[BRAND].str.strip().str.lower() == brand.strip().lower()]
    if sub.empty:
        return None
    total = len(sub)
    high = int((sub[TRUST] == "High_Trust").sum()) if TRUST in sub.columns else 0
    cats = sub.groupby(CATEGORY)[PRODUCT].nunique().sort_values(ascending=False)
    return {
        "status": "success",
        "brand_name": str(sub[BRAND].iloc[0]),
        "product_count": int(sub[PRODUCT].nunique()),
        "review_count": int(total),
        "avg_rating": round(float(sub[RATING].mean()), 2),
        "halal_mentions": _mentions(sub, HALAL),
        "bpom_mentions": _mentions(sub, BPOM),
        "high_trust_pct": round(high / total * 100, 1) if total else 0.0,
        "categories": [{"category_name": str(k), "product_count": int(v)} for k, v in cats.items()],
    }


def refine_products(products: List[Dict[str, Any]], halal: bool = False, bpom: bool = False,
                    min_rating: Optional[float] = None) -> List[Dict[str, Any]]:
    """Applies certification/rating facets to product rows and attaches the verified photo path."""
    out = []
    for p in products:
        if halal and not p.get("halal_claim"):
            continue
        if bpom and not p.get("bpom_claim"):
            continue
        if min_rating is not None and p.get("avg_rating", 0) < min_rating:
            continue
        out.append({**p, "photo": product_photo(p["brand_name"], p["product_name"])})
    return out
