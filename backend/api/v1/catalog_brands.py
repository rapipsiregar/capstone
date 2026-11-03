"""
Brand directory REST endpoints for the V4 Rose Blush catalog.
GET /api/v1/catalog/brands         -> faceted, paginated brand directory (homepage)
GET /api/v1/catalog/brand-profile  -> one brand's header numbers + category & aspect facets (brand page)
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Query

from backend.api.v1.catalog import load_dataset_dataframe
from backend.services.brand_directory import build_brand_directory, build_brand_profile

router = APIRouter(prefix="/catalog", tags=["Catalog"])


@router.get("/brands")
def get_brand_directory(
    category: Optional[str] = Query(None, description="One or more categories, comma separated"),
    aspect: Optional[str] = Query(None, description="One or more dominant communication aspects, comma separated"),
    high_trust: bool = Query(False, description="Only brands with High Trust >= 50%"),
    halal: bool = Query(False, description="Only brands with reviews mentioning a halal claim"),
    bpom: bool = Query(False, description="Only brands with reviews mentioning a BPOM claim"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum average rating"),
    search: str = Query("", description="Brand name keyword"),
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=60),
) -> Dict[str, Any]:
    """Brand directory aggregated from the annotated dataset."""
    df = load_dataset_dataframe()
    if df.empty:
        return {"status": "success", "total_brands": 0, "total_products": 0, "total_reviews": 0,
                "page": page, "total_pages": 0, "brands": [], "facets": {"categories": [], "aspects": []}}
    return build_brand_directory(df, category, halal, bpom, min_rating, search, page, limit, aspect, high_trust)


@router.get("/brand-profile")
def get_brand_profile(brand: str = Query(..., description="Exact brand name")) -> Dict[str, Any]:
    """Header numbers for the brand products page."""
    profile = build_brand_profile(load_dataset_dataframe(), brand)
    if profile is None:
        raise HTTPException(status_code=404, detail=f"Brand '{brand}' tidak ditemukan di dataset")
    return profile
