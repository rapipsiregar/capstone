"""
Catalog & Homepage Statistics REST API Endpoint.
Serves authentic live counts for reviews, products, brands, categories,
and Halal & BPOM claim citations directly from female_daily_skincare_annotated.csv.
"""

import os
from typing import Dict, Any
from functools import lru_cache
import pandas as pd
from fastapi import APIRouter
from backend.api.v1.catalog import load_dataset_dataframe

router = APIRouter(prefix="/catalog", tags=["Catalog Stats"])
ANNOTATED_DIR = os.path.join("data", "annotated")


@lru_cache(maxsize=1)
def compute_catalog_stats() -> Dict[str, Any]:
    """Computes exact statistics from the authentic active annotated dataset."""
    df = load_dataset_dataframe()
    total_reviews = int(len(df))
    total_products = int(df["nama_produk"].nunique()) if "nama_produk" in df.columns else 0
    total_brands = int(df["merek_umkm"].nunique()) if "merek_umkm" in df.columns else 0
    total_categories = int(df["kategori_produk"].nunique()) if "kategori_produk" in df.columns else 0

    halal_reviews = int((df["klaim_halal"] == 1).sum()) if "klaim_halal" in df.columns else 0
    bpom_reviews = int((df["klaim_bpom"] == 1).sum()) if "klaim_bpom" in df.columns else 0

    halal_pct = round((halal_reviews / total_reviews) * 100, 2) if total_reviews > 0 else 0.0
    bpom_pct = round((bpom_reviews / total_reviews) * 100, 2) if total_reviews > 0 else 0.0

    return {
        "status": "success",
        "total_reviews": total_reviews,
        "total_products": total_products,
        "total_brands": total_brands,
        "total_categories": total_categories,
        "halal_claimed_reviews": halal_reviews,
        "bpom_claimed_reviews": bpom_reviews,
        "halal_percentage": halal_pct,
        "bpom_percentage": bpom_pct,
        "compliance_summary": f"{halal_reviews} Halal & {bpom_reviews} BPOM",
        "split_counts": count_split_rows(),
    }


def count_split_rows() -> Dict[str, int]:
    """Row counts of the stratified train/val/test files used for fine-tuning and evaluation."""
    counts = {}
    for split in ("train", "val", "test"):
        path = os.path.join(ANNOTATED_DIR, f"{split}.csv")
        counts[split] = int(len(pd.read_csv(path))) if os.path.exists(path) else 0
    return counts


@router.get("/stats")
def get_catalog_stats() -> Dict[str, Any]:
    """Returns authentic summary stats for catalog hero & homepage."""
    return compute_catalog_stats()
