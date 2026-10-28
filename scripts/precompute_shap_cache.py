"""
Batch SHAP precompute for every review in the annotated dataset (Task 8.10).

Usage:
    .venv\\Scripts\\python scripts\\precompute_shap_cache.py [--limit N] [--save-every 200]

Resumable: reviews already cached with the current attribution method are skipped.
Writes data/cache/review_shap_cache.json (compact JSON). Restart uvicorn afterwards,
because the server keeps the cache in memory.
"""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd  # noqa: E402

from backend.services.catalog_shap_cacher import precompute_review_cache  # noqa: E402

DATASET = os.path.join("data", "annotated", "female_daily_skincare_annotated.csv")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="only the first N reviews (trial run)")
    parser.add_argument("--save-every", type=int, default=200)
    args = parser.parse_args()

    texts = pd.read_csv(DATASET)["teks_ulasan_mentah"].dropna().astype(str).tolist()
    if args.limit:
        texts = texts[: args.limit]
    print(f"dataset reviews: {len(texts)}", flush=True)

    start = time.perf_counter()

    def progress(done: int, total: int) -> None:
        if done % 100 == 0 or done == total:
            elapsed = time.perf_counter() - start
            eta_min = (total - done) * (elapsed / done) / 60
            print(f"{done}/{total} computed, {elapsed / done:.3f}s/review, ETA {eta_min:.1f} min", flush=True)

    added = precompute_review_cache(texts, save_every=args.save_every, progress=progress)
    print(f"done: {added} new records in {(time.perf_counter() - start) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
