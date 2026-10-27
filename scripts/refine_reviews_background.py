"""
CHARM - Background Pipeline to Progressively Fetch Full Review Texts from Female Daily.
Target: Resolves truncated reviews containing '... Read more' with polite rate limiting.
"""

import os
import sys

# Ensure workspace root is in python path
sys.path.insert(0, os.path.abspath("."))
import re
import time
import json
import logging
import urllib.request
import urllib.parse
import pandas as pd
from typing import Dict, Any, Optional

from backend.services.review_refiner import (
    create_dataset_backup,
    validate_and_merge_text,
    load_json_store,
    save_json_store,
    DATASET_PATH,
    CHECKPOINT_PATH,
    CACHE_PROD_ID_PATH,
    FD_API_BASE,
    FD_HEADERS
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [SCRAPER] %(message)s")


def slugify(text: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]+', '-', str(text)).lower().strip('-')


def resolve_product_id(brand: str, product_name: str, category: str, prod_cache: Dict[str, Any]) -> Optional[int]:
    """Tries cached ID or queries Female Daily product page HTML for storeProduct id."""
    key = f"{brand}::{product_name}"
    if key in prod_cache:
        return prod_cache[key]
    
    b_slug = slugify(brand)
    p_slug = slugify(product_name)
    c_slug = slugify(category)
    
    # Candidate URLs on Female Daily
    candidates = [
        f"https://reviews.femaledaily.com/products/{c_slug}/{b_slug}/{p_slug}",
        f"https://reviews.femaledaily.com/products/treatment/{c_slug}/{b_slug}/{p_slug}",
        f"https://reviews.femaledaily.com/products/cleanser/{c_slug}/{b_slug}/{p_slug}",
        f"https://reviews.femaledaily.com/products/moisturizer/{c_slug}/{b_slug}/{p_slug}"
    ]
    
    for url in candidates:
        try:
            req = urllib.request.Request(url, headers=FD_HEADERS)
            with urllib.request.urlopen(req, timeout=8) as res:
                html = res.read().decode("utf-8", errors="ignore")
                idx = html.find('__NEXT_DATA__ = ')
                if idx != -1:
                    sub = html[idx + len('__NEXT_DATA__ = '):]
                    obj, _ = json.JSONDecoder().raw_decode(sub)
                    pid = obj.get("props", {}).get("initialState", {}).get("storeProduct", {}).get("data", {}).get("id")
                    if pid:
                        prod_cache[key] = int(pid)
                        save_json_store(CACHE_PROD_ID_PATH, prod_cache)
                        return int(pid)
        except Exception:
            continue
    return None


def fetch_all_reviews_for_product(product_id: int, max_pages: int = 20, delay: float = 2.0) -> Dict[str, str]:
    """Fetches online reviews for product and returns username -> full_text map."""
    reviews_map = {}
    for page in range(1, max_pages + 1):
        params = {"product_id": str(product_id), "limit": "20", "page": str(page)}
        url = f"{FD_API_BASE}/reviews?{urllib.parse.urlencode(params)}"
        try:
            req = urllib.request.Request(url, headers=FD_HEADERS)
            with urllib.request.urlopen(req, timeout=10) as res:
                data = json.loads(res.read().decode("utf-8"))
                items = data.get("data", [])
                if not items:
                    break
                for item in items:
                    uname = str(item.get("user", {}).get("username", "")).strip().lower()
                    txt = str(item.get("text", "")).strip()
                    if uname and txt:
                        reviews_map[uname] = txt
            time.sleep(delay)
        except Exception as e:
            logging.warning("Error fetching reviews page %s for prod %s: %s", page, product_id, e)
            break
    return reviews_map


def run_full_pipeline(delay_between_requests: float = 2.0):
    """Main background loop processing products with truncated reviews."""
    create_dataset_backup()
    df = pd.read_csv(DATASET_PATH)
    
    checkpoints = load_json_store(CHECKPOINT_PATH)
    prod_cache = load_json_store(CACHE_PROD_ID_PATH)
    
    # Pre-seed verified DHC ID
    prod_cache["DHC::Deep Cleansing Oil"] = 6203
    save_json_store(CACHE_PROD_ID_PATH, prod_cache)
    
    truncated_mask = df["teks_ulasan_mentah"].str.contains("Read more", na=False)
    total_truncated = int(truncated_mask.sum())
    logging.info("Found %d truncated reviews in dataset.", total_truncated)
    
    prods_with_cuts = df[truncated_mask][["merek_umkm", "nama_produk", "kategori_produk"]].drop_duplicates()
    logging.info("Found %d unique products needing refinement.", len(prods_with_cuts))
    
    refined_count = checkpoints.get("total_refined", 0)
    prods_completed = set(checkpoints.get("completed_products", []))
    
    for idx, (_, row) in enumerate(prods_with_cuts.iterrows()):
        brand = str(row["merek_umkm"]).strip()
        pname = str(row["nama_produk"]).strip()
        cat = str(row["kategori_produk"]).strip()
        pkey = f"{brand}::{pname}"
        
        if pkey in prods_completed:
            continue
            
        logging.info("[%d/%d] Processing product: %s (%s)", idx + 1, len(prods_with_cuts), pname, brand)
        pid = resolve_product_id(brand, pname, cat, prod_cache)
        time.sleep(delay_between_requests)
        
        if not pid:
            logging.info("  Skipping: Product ID not resolved yet for %s", pname)
            continue
            
        online_reviews = fetch_all_reviews_for_product(pid, max_pages=15, delay=delay_between_requests)
        if not online_reviews:
            logging.info("  No online reviews returned for prod ID %s", pid)
            continue
            
        # Match with local reviews for this product
        p_mask = (df["merek_umkm"] == brand) & (df["nama_produk"] == pname) & truncated_mask
        local_indices = df[p_mask].index
        
        updated_for_prod = 0
        for l_idx in local_indices:
            user = str(df.loc[l_idx, "penulis_ulasan"]).strip().lower()
            if user in online_reviews:
                cut_txt = str(df.loc[l_idx, "teks_ulasan_mentah"])
                full_txt = online_reviews[user]
                merged, is_valid = validate_and_merge_text(cut_txt, full_txt)
                if is_valid and merged != cut_txt:
                    df.loc[l_idx, "teks_ulasan_mentah"] = merged
                    # Recompute cleaned text if column exists
                    if "teks_ulasan_bersih" in df.columns:
                        clean_str = re.sub(r'[^a-zA-Z0-9\s]+', ' ', merged).lower()
                        df.loc[l_idx, "teks_ulasan_bersih"] = ' '.join(clean_str.split())
                    refined_count += 1
                    updated_for_prod += 1
                    
        logging.info("  Updated %d reviews for %s (Total Refined: %d)", updated_for_prod, pname, refined_count)
        prods_completed.add(pkey)
        
        # Save checkpoints and CSV periodically
        checkpoints["total_refined"] = refined_count
        checkpoints["completed_products"] = list(prods_completed)
        checkpoints["last_updated"] = time.time()
        save_json_store(CHECKPOINT_PATH, checkpoints)
        df.to_csv(DATASET_PATH, index=False)
        logging.info("  Saved checkpoint and dataset CSV.")

    logging.info("Refinement Worker Finished. Total refined reviews: %d", refined_count)


if __name__ == "__main__":
    run_full_pipeline(delay_between_requests=2.0)
