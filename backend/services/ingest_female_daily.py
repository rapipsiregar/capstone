"""
Female Daily Dataset Ingestion & Validation Pipeline Service.
Cleans 10,826+ raw skincare ulasan, normalizes Indonesian slang/emojis,
validates schema integrity, and maps ratings to sentiment & aspect categories.
"""

import os
import re
import time
import pandas as pd
from typing import Tuple, Dict, Any, List

RAW_DATA_DIR = os.path.join("data", "raw")
CLEANED_DATA_DIR = os.path.join("data", "cleaned")
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(CLEANED_DATA_DIR, exist_ok=True)

# Common Indonesian Slang Normalization Dictionary for Cosmetics Reviews
SLANG_MAP: Dict[str, str] = {
    "bgt": "banget",
    "bgtt": "banget",
    "bngt": "banget",
    "blm": "belum",
    "g": "tidak",
    "ga": "tidak",
    "gak": "tidak",
    "nggak": "tidak",
    "bruntusan": "beruntusan",
    "breakout": "iritasi breakout",
    "bs": "bisa",
    "sdh": "sudah",
    "udh": "sudah",
    "dgn": "dengan",
    "utk": "untuk",
    "tp": "tapi",
    "tpi": "tapi",
    "bkn": "bukan",
    "klo": "kalau",
    "kalo": "kalau",
    "muka": "wajah",
    "ori": "original",
    "recomended": "direkomendasikan",
    "recommended": "direkomendasikan",
    "recsell": "rekomendasi",
    "cepet": "cepat",
    "tetep": "tetap",
    "pake": "pakai",
    "pakek": "pakai",
    "makai": "pakai"
}

REQUIRED_SCHEMA_COLUMNS = ["Merk", "Category", "Product", "Rating", "Review"]


def validate_female_daily_schema(df: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
    """
    Validates dataset schema integrity, checking columns, row counts, and null ratios.
    """
    if df.empty:
        return False, {"error": "Dataset is empty", "total_rows": 0}
        
    missing_cols = [col for col in REQUIRED_SCHEMA_COLUMNS if col not in df.columns]
    if missing_cols:
        return False, {"error": f"Missing required columns: {missing_cols}", "total_rows": len(df)}
        
    null_counts = df[REQUIRED_SCHEMA_COLUMNS].isnull().sum().to_dict()
    report = {
        "status": "valid",
        "total_rows": len(df),
        "columns": df.columns.tolist(),
        "null_counts": null_counts,
        "unique_brands": df["Merk"].nunique() if "Merk" in df.columns else 0,
        "unique_categories": df["Category"].nunique() if "Category" in df.columns else 0
    }
    return True, report


def normalize_indonesian_text(text: str) -> str:
    """
    Cleans raw review text: lowercasing, regex symbol removal, and slang normalization.
    """
    if not isinstance(text, str):
        return ""
        
    text = text.lower().strip()
    # Remove HTML tags & URLs
    text = re.sub(r'http\S+|www\S+|<[^>]*>', '', text)
    # Remove non-alphabetical punctuation except basic spaces
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    
    words = text.split()
    normalized_words = [SLANG_MAP.get(w, w) for w in words]
    cleaned_text = " ".join(normalized_words)
    # Multiple whitespace collapse
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text


def classify_aspect_category(text: str, category: str) -> str:
    """
    Classifies aspect category: BPOM & Halal, Efikasi & Hasil, Keamanan & Iritasi, Layanan & Harga.
    """
    text_lower = text.lower()
    if any(k in text_lower for k in ["halal", "bpom", "mui", "segel", "ori", "original", "resmi"]):
        return "Sertifikasi BPOM & Halal"
    elif any(k in text_lower for k in ["breakout", "iritasi", "gatal", "panas", "merah", "perih", "bruntusan"]):
        return "Keamanan & Sensitivitas Kulit"
    elif any(k in text_lower for k in ["harga", "mahal", "murah", "diskon", "pengiriman", "kemasan", "bocor", "penyok"]):
        return "Harga & Kemasan Produk"
    else:
        return "Efikasi & Tekstur Produk"


def map_rating_to_sentiment(rating: int, text: str, recommend: str = "") -> str:
    """
    Maps 1-5 rating & text keywords to sentiment label (Positif, Negatif, Netral).
    """
    text_lower = text.lower()
    neg_words = ["breakout", "bruntusan", "iritasi", "gatal", "kecewa", "jelek", "bocor", "penyok", "tidak terdaftar", "palsu"]
    rec_lower = str(recommend).lower()
    
    if rating <= 2 or "does not recommend" in rec_lower or any(w in text_lower for w in neg_words):
        return "Negatif"
    elif rating == 3 or "biasa aja" in text_lower or "lumayan" in text_lower:
        return "Netral"
    else:
        return "Positif"


def clean_female_daily_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """
    Main transformation engine: cleans review text, generates aspect & sentiment labels.
    """
    df_clean = df.copy()
    
    # Fill missing strings
    df_clean["Merk"] = df_clean["Merk"].fillna("Kosmetik Halal General")
    df_clean["Category"] = df_clean["Category"].fillna("Skincare General")
    df_clean["Product"] = df_clean["Product"].fillna("Produk Kosmetik")
    df_clean["Review"] = df_clean["Review"].fillna("")
    df_clean["Rating"] = pd.to_numeric(df_clean["Rating"], errors="coerce").fillna(5).astype(int)
    
    # Process text & labels
    df_clean["teks_ulasan_mentah"] = df_clean["Review"]
    df_clean["teks_ulasan_bersih"] = df_clean["Review"].apply(normalize_indonesian_text)
    
    aspects = []
    sentiments = []
    
    for idx, row in df_clean.iterrows():
        raw_txt = str(row["Review"])
        clean_txt = str(row["teks_ulasan_bersih"])
        rating = int(row["Rating"])
        rec = str(row.get("Recommend", ""))
        cat = str(row["Category"])
        
        aspects.append(classify_aspect_category(clean_txt, cat))
        sentiments.append(map_rating_to_sentiment(rating, raw_txt, rec))
        
    df_clean["aspek_komunikasi"] = aspects
    df_clean["label_sentimen"] = sentiments
    
    # Map to standardized project schema
    df_standard = pd.DataFrame({
        "sumber_api": "Female Daily Benchmark",
        "merek_umkm": df_clean["Merk"],
        "kategori_produk": df_clean["Category"],
        "nama_produk": df_clean["Product"],
        "penulis_ulasan": df_clean.get("UserName", "FemaleDailyUser"),
        "kondisi_kulit_usia": df_clean.get("SkinCond_Age", "General Skin"),
        "rating_bintang": df_clean["Rating"],
        "status_rekomendasi": df_clean.get("Recommend", "Recommends"),
        "teks_ulasan_mentah": df_clean["teks_ulasan_mentah"],
        "teks_ulasan_bersih": df_clean["teks_ulasan_bersih"],
        "aspek_komunikasi": df_clean["aspek_komunikasi"],
        "label_sentimen": df_clean["label_sentimen"],
        "waktu_timestamp": 1793108586
    })
    
    # Filter out empty clean reviews
    df_standard = df_standard[df_standard["teks_ulasan_bersih"].str.len() > 3].reset_index(drop=True)
    return df_standard


def ingest_female_daily_pipeline(
    raw_csv_path: str = "data/raw/female_daily_skincare_reviews_raw.csv",
    output_csv_path: str = "data/cleaned/female_daily_skincare_cleaned.csv"
) -> Tuple[str, int]:
    """
    Executes full ingestion & cleaning pipeline on raw Female Daily dataset.
    """
    if not os.path.exists(raw_csv_path):
        raise FileNotFoundError(f"Raw dataset file not found at: {raw_csv_path}")
        
    raw_df = pd.read_csv(raw_csv_path)
    is_valid, report = validate_female_daily_schema(raw_df)
    if not is_valid:
        raise ValueError(f"Dataset schema validation failed: {report}")
        
    print(f"\n[Female Daily Ingestion] Validated {report['total_rows']} raw records across {report['unique_brands']} brands.")
    cleaned_df = clean_female_daily_reviews(raw_df)
    
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    cleaned_df.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
    
    print(f"  -> Cleaned dataset saved to: {os.path.abspath(output_csv_path)}")
    print(f"  -> Total valid cleaned ulasan records: {len(cleaned_df)}")
    return os.path.abspath(output_csv_path), len(cleaned_df)


if __name__ == "__main__":
    ingest_female_daily_pipeline()
