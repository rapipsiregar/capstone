"""
Brand directory service for the V4 Rose Blush catalog (homepage + brand page).

Every value is aggregated from the annotated Female Daily dataset as-is:
- high_trust_pct and top_aspect expose what drives consumer trust per brand/product (Solusi 2).
- halal/BPOM mentions are kept for backward API compatibility.
- photo paths are only returned when the packshot file really exists.
"""

import os
import re
from typing import Any, Dict, List, Optional

import pandas as pd

PHOTO_DIR = os.path.join("frontend", "images", "products")
BRAND, PRODUCT, CATEGORY, RATING = "merek_umkm", "nama_produk", "kategori_produk", "rating_bintang"
HALAL, BPOM, TRUST, ASPECT = "klaim_halal", "klaim_bpom", "label_kepercayaan", "aspek_komunikasi"


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


def _split_csv(val: Optional[str]) -> List[str]:
    if not val:
        return []
    return [c.strip().lower() for c in str(val).split(",") if c.strip()]


def _top_aspect(sub: pd.DataFrame) -> str:
    if ASPECT not in sub.columns or sub[ASPECT].dropna().empty:
        return ""
    return str(sub[ASPECT].mode().iloc[0])


def _high_trust_pct(sub: pd.DataFrame) -> float:
    total = len(sub)
    if not total or TRUST not in sub.columns:
        return 0.0
    return round(int((sub[TRUST] == "High_Trust").sum()) / total * 100, 1)


def _brand_row(name: str, sub: pd.DataFrame) -> Dict[str, Any]:
    counts = sub[PRODUCT].value_counts()
    top_name = str(counts.index[0])
    top = sub[sub[PRODUCT] == top_name]
    return {
        "brand_name": str(name),
        "product_count": int(sub[PRODUCT].nunique()),
        "review_count": int(len(sub)),
        "avg_rating": round(float(sub[RATING].mean()), 2),
        "high_trust_pct": _high_trust_pct(sub),
        "top_aspect": _top_aspect(sub),
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
                          page: int = 1, limit: int = 12, aspect: Optional[str] = None,
                          high_trust: bool = False) -> Dict[str, Any]:
    """Faceted, paginated brand list sorted by review volume."""
    full_cats = df.groupby(CATEGORY).agg(brand_count=(BRAND, "nunique"), product_count=(PRODUCT, "nunique"))
    facets_categories = [
        {"category_name": str(k), "brand_count": int(v.brand_count), "product_count": int(v.product_count)}
        for k, v in full_cats.sort_values("brand_count", ascending=False).iterrows()
    ]

    scope = df
    cats = _split_csv(category)
    if cats:
        scope = scope[scope[CATEGORY].str.strip().str.lower().isin(cats)]
    if search and search.strip():
        scope = scope[scope[BRAND].str.lower().str.contains(search.strip().lower(), na=False, regex=False)]

    grouped = scope.groupby(BRAND)
    stats = grouped.agg(avg=(RATING, "mean"), reviews=(RATING, "size"))
    ht_map = {b: _high_trust_pct(g) for b, g in grouped}
    asp_map = {b: _top_aspect(g) for b, g in grouped}
    halal_brands = set(scope[scope[HALAL] == 1][BRAND]) if HALAL in scope.columns else set()
    bpom_brands = set(scope[scope[BPOM] == 1][BRAND]) if BPOM in scope.columns else set()

    asp_counts = pd.Series(list(asp_map.values())).value_counts() if asp_map else pd.Series(dtype=int)
    facets_aspects = [{"aspect_key": str(k), "brand_count": int(v)} for k, v in asp_counts.items() if k]

    keep = stats.index.to_series()
    if halal:
        keep = keep[keep.isin(halal_brands)]
    if bpom:
        keep = keep[keep.isin(bpom_brands)]
    if high_trust:
        keep = keep[keep.map(lambda b: ht_map.get(b, 0.0) >= 50.0)]
    aspects_filter = _split_csv(aspect)
    if aspects_filter:
        keep = keep[keep.map(lambda b: asp_map.get(b, "").lower() in aspects_filter)]
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
            "aspects": facets_aspects,
            "high_trust_brands": sum(1 for v in ht_map.values() if v >= 50.0),
            "halal_brands": len(halal_brands),
            "bpom_brands": len(bpom_brands),
            "rating_4_brands": int((stats["avg"] >= 4).sum()),
        },
    }


def build_brand_profile(df: pd.DataFrame, brand: str) -> Optional[Dict[str, Any]]:
    """Header numbers, category facet, and trust-source facets for one brand page."""
    sub = df[df[BRAND].str.strip().str.lower() == brand.strip().lower()]
    if sub.empty:
        return None
    cats = sub.groupby(CATEGORY)[PRODUCT].nunique().sort_values(ascending=False)
    prod_groups = list(sub.groupby(PRODUCT))
    prod_aspects = pd.Series([_top_aspect(g) for _, g in prod_groups]).value_counts()
    high_trust_prods = sum(1 for _, g in prod_groups if _high_trust_pct(g) >= 50.0)
    return {
        "status": "success",
        "brand_name": str(sub[BRAND].iloc[0]),
        "product_count": int(sub[PRODUCT].nunique()),
        "review_count": int(len(sub)),
        "avg_rating": round(float(sub[RATING].mean()), 2),
        "halal_mentions": _mentions(sub, HALAL),
        "bpom_mentions": _mentions(sub, BPOM),
        "high_trust_pct": _high_trust_pct(sub),
        "top_aspect": _top_aspect(sub),
        "high_trust_products": int(high_trust_prods),
        "aspects": [{"aspect_key": str(k), "product_count": int(v)} for k, v in prod_aspects.items() if k],
        "categories": [{"category_name": str(k), "product_count": int(v)} for k, v in cats.items()],
    }


def refine_products(products: List[Dict[str, Any]], halal: bool = False, bpom: bool = False,
                    min_rating: Optional[float] = None, aspect: Optional[str] = None,
                    high_trust: bool = False) -> List[Dict[str, Any]]:
    """Applies trust-source, certification, and rating facets to product rows."""
    aspects_filter = _split_csv(aspect)
    out = []
    for p in products:
        if halal and not p.get("halal_claim"):
            continue
        if bpom and not p.get("bpom_claim"):
            continue
        if high_trust and p.get("high_trust_pct", 0.0) < 50.0:
            continue
        if aspects_filter and str(p.get("top_aspect", "")).lower() not in aspects_filter:
            continue
        if min_rating is not None and p.get("avg_rating", 0) < min_rating:
            continue
        out.append({**p, "photo": product_photo(p["brand_name"], p["product_name"])})
    return out
