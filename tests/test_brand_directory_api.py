"""
TDD tests for the V4 Rose Blush brand directory (Task 9.2 / mockup V4 halaman 2-3).
Every expected number is recomputed from the annotated CSV, so the API may not invent values.
"""

import os
import re
import pandas as pd
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
DATASET = os.path.join("data", "annotated", "female_daily_skincare_annotated.csv")


def _df():
    return pd.read_csv(DATASET)


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")


def test_brand_directory_counts_match_dataset():
    df = _df()
    resp = client.get("/api/v1/catalog/brands", params={"limit": 12})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["total_brands"] == df["merek_umkm"].nunique()
    assert data["total_reviews"] == len(df)
    assert len(data["brands"]) == 12
    first = data["brands"][0]
    sub = df[df["merek_umkm"] == first["brand_name"]]
    assert first["review_count"] == len(sub)
    assert first["product_count"] == sub["nama_produk"].nunique()
    assert first["avg_rating"] == round(float(sub["rating_bintang"].mean()), 2)
    assert first["halal_mentions"] == int((sub["klaim_halal"] == 1).sum())
    assert first["bpom_mentions"] == int((sub["klaim_bpom"] == 1).sum())
    top_name = sub["nama_produk"].value_counts().index[0]
    assert first["top_product"]["product_name"] == top_name
    assert first["top_product"]["review_count"] == int((sub["nama_produk"] == top_name).sum())


def test_brand_directory_sorted_by_review_count_and_paginated():
    data = client.get("/api/v1/catalog/brands", params={"limit": 10, "page": 2}).json()
    counts = [b["review_count"] for b in data["brands"]]
    assert counts == sorted(counts, reverse=True)
    assert data["page"] == 2
    assert data["total_pages"] == -(-data["total_brands"] // 10)


def test_brand_directory_category_facet_filters_brands():
    df = _df()
    cat = df["kategori_produk"].value_counts().index[0]
    data = client.get("/api/v1/catalog/brands", params={"category": cat, "limit": 50}).json()
    expected = df[df["kategori_produk"] == cat]["merek_umkm"].nunique()
    assert data["total_brands"] == expected
    facet = {c["category_name"]: c for c in data["facets"]["categories"]}
    assert facet[cat]["brand_count"] == expected
    assert len(facet) == df["kategori_produk"].nunique()
    assert len(data["facets"]["brand_names"]) == df["merek_umkm"].nunique()


def test_brand_directory_halal_and_rating_facets_are_honest():
    df = _df()
    data = client.get("/api/v1/catalog/brands", params={"halal": "true", "limit": 50}).json()
    halal_brands = df[df["klaim_halal"] == 1]["merek_umkm"].nunique()
    assert data["total_brands"] == halal_brands
    assert all(b["halal_mentions"] > 0 for b in data["brands"])

    data = client.get("/api/v1/catalog/brands", params={"min_rating": 4, "limit": 50}).json()
    means = df.groupby("merek_umkm")["rating_bintang"].mean()
    assert data["total_brands"] == int((means >= 4).sum())
    assert all(b["avg_rating"] >= 4 for b in data["brands"])


def test_brand_directory_search_and_photo_field():
    data = client.get("/api/v1/catalog/brands", params={"search": "wardah"}).json()
    assert data["total_brands"] >= 1
    assert all("wardah" in b["brand_name"].lower() for b in data["brands"])
    for b in data["brands"]:
        photo = b["top_product"]["photo"]
        if photo:
            path = os.path.join("frontend", photo.lstrip("./").replace("/", os.sep))
            assert os.path.exists(path), f"photo path must point to a real file: {photo}"


def test_brand_profile_matches_dataset():
    df = _df()
    brand = df["merek_umkm"].value_counts().index[0]
    resp = client.get("/api/v1/catalog/brand-profile", params={"brand": brand})
    assert resp.status_code == 200
    info = resp.json()
    sub = df[df["merek_umkm"] == brand]
    assert info["brand_name"] == brand
    assert info["review_count"] == len(sub)
    assert info["product_count"] == sub["nama_produk"].nunique()
    high = int((sub["label_kepercayaan"] == "High_Trust").sum())
    assert info["high_trust_pct"] == round(high / len(sub) * 100, 1)
    cats = {c["category_name"]: c["product_count"] for c in info["categories"]}
    expected = sub.groupby("kategori_produk")["nama_produk"].nunique().to_dict()
    assert cats == {k: int(v) for k, v in expected.items()}


def test_brand_profile_unknown_brand_returns_404():
    resp = client.get("/api/v1/catalog/brand-profile", params={"brand": "brand-yang-tidak-ada-xyz"})
    assert resp.status_code == 404


def test_products_endpoint_supports_certification_and_rating_facets():
    df = _df()
    brand = df["merek_umkm"].value_counts().index[0]
    data = client.get("/api/v1/catalog/products", params={"brand": brand, "min_rating": 4, "limit": 50}).json()
    sub = df[df["merek_umkm"] == brand]
    means = sub.groupby("nama_produk")["rating_bintang"].mean()
    assert data["total_products"] == int((means >= 4).sum())
    data = client.get("/api/v1/catalog/products", params={"brand": brand, "halal": "true", "limit": 50}).json()
    halal_products = sub[sub["klaim_halal"] == 1]["nama_produk"].nunique()
    assert data["total_products"] == halal_products
    for p in data["products"]:
        assert p["halal_claim"] is True
        assert "photo" in p
        expected_file = os.path.join("frontend", "images", "products", f"{_slug(p['brand_name'] + '-' + p['product_name'])}.jpg")
        assert (p["photo"] is not None) == os.path.exists(expected_file)
