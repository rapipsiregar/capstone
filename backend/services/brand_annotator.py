"""
Brand-Specific Halal Entity & Aspect Annotator Service.
Extracts halal certification, BPOM compliance, skin sensitivity triggers (breakout/bruntusan),
and performs dual-taxonomy aspect & trust sentiment annotation on Female Daily skincare reviews.
"""

import os
import time
import pandas as pd
from typing import Dict, Any, Tuple

ANNOTATED_DATA_DIR = os.path.join("data", "annotated")
os.makedirs(ANNOTATED_DATA_DIR, exist_ok=True)

# Entity Keyword Dictionaries
HALAL_BPOM_KEYWORDS = ["halal", "bpom", "mui", "bpjph", "segel", "original", "resmi", "terdaftar", "ori"]
BREAKOUT_SENSITIVITY_KEYWORDS = ["breakout", "beruntusan", "bruntusan", "iritasi", "gatal", "panas", "merah", "perih", "perihh", "alergis"]
PACKAGING_PRICE_KEYWORDS = ["harga", "mahal", "murah", "bocor", "penyok", "kemasan", "dus", "botol", "pengiriman", "diskon"]
EFFICACY_TEXTURE_KEYWORDS = ["melembabkan", "mencerahkan", "halus", "lembut", "cepat meresap", "glowing", "kenyal", "tekstur", "wangi", "aroma"]


def extract_brand_halal_entities(text: str) -> Dict[str, bool]:
    """
    Extracts brand-specific halal entities and skin sensitivity triggers from text.
    """
    if not isinstance(text, str):
        text = ""
    text_lower = text.lower()
    
    return {
        "has_halal_claim": any(w in text_lower for w in ["halal", "mui", "bpjph"]),
        "has_bpom_claim": any(w in text_lower for w in ["bpom", "terdaftar", "segel", "resmi", "original", "ori"]),
        "has_breakout_issue": any(w in text_lower for w in BREAKOUT_SENSITIVITY_KEYWORDS),
        "has_packaging_issue": any(w in text_lower for w in ["bocor", "penyok", "rusak", "pecah"]),
        "has_efficacy_mention": any(w in text_lower for w in EFFICACY_TEXTURE_KEYWORDS)
    }


def annotate_halal_aspect_and_trust(row: Dict[str, Any]) -> Tuple[str, str]:
    """
    Annotates aspect taxonomy and trust sentiment label based on entity triggers, rating & text.
    """
    text = str(row.get("teks_ulasan_bersih", "")).lower()
    rating = int(row.get("rating_bintang", 5))
    recommend = str(row.get("status_rekomendasi", "")).lower()
    
    entities = extract_brand_halal_entities(text)
    
    # 1. Aspect Taxonomy Classification
    if entities["has_breakout_issue"]:
        aspect = "Kandungan_Bahan_Sensitivitas"
    elif entities["has_halal_claim"] or (entities["has_bpom_claim"] and "tidak" not in text):
        aspect = "Sertifikasi_Halal_BPOM"
    elif any(k in text for k in PACKAGING_PRICE_KEYWORDS) or entities["has_packaging_issue"]:
        aspect = "Transparansi_Layanan_Harga"
    else:
        aspect = "Klaim_Efikasi_Manfaat"
        
    # 2. Trust Sentiment Classification (High_Trust, Neutral, Low_Trust)
    if rating <= 2 or "does not recommend" in recommend or entities["has_breakout_issue"] or entities["has_packaging_issue"]:
        trust = "Low_Trust"
    elif rating == 3 or "biasa" in text or "lumayan" in text:
        trust = "Neutral"
    else:
        trust = "High_Trust"
        
    return aspect, trust


def annotate_female_daily_dataset(
    cleaned_csv_path: str = "data/cleaned/female_daily_skincare_cleaned.csv",
    output_csv_path: str = "data/annotated/female_daily_skincare_annotated.csv"
) -> Tuple[str, int]:
    """
    Batch annotates cleaned Female Daily dataset and exports to data/annotated directory.
    """
    if not os.path.exists(cleaned_csv_path):
        raise FileNotFoundError(f"Cleaned dataset not found at: {cleaned_csv_path}")
        
    df = pd.read_csv(cleaned_csv_path)
    print(f"\n[Brand Annotator] Batch annotating {len(df)} cleaned records...")
    
    aspects = []
    trusts = []
    halal_claims = []
    bpom_claims = []
    breakout_issues = []
    
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        aspect, trust = annotate_halal_aspect_and_trust(row_dict)
        entities = extract_brand_halal_entities(str(row_dict.get("teks_ulasan_bersih", "")))
        
        aspects.append(aspect)
        trusts.append(trust)
        halal_claims.append(entities["has_halal_claim"])
        bpom_claims.append(entities["has_bpom_claim"])
        breakout_issues.append(entities["has_breakout_issue"])
        
    df["aspek_komunikasi"] = aspects
    df["label_kepercayaan"] = trusts
    df["klaim_halal"] = halal_claims
    df["klaim_bpom"] = bpom_claims
    df["isu_breakout"] = breakout_issues
    
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
    
    print(f"  -> Annotated dataset saved to: {os.path.abspath(output_csv_path)}")
    print(f"  -> Total annotated records: {len(df)}")
    print(f"  -> Aspect Distribution:\n{df['aspek_komunikasi'].value_counts()}")
    print(f"  -> Trust Distribution:\n{df['label_kepercayaan'].value_counts()}")
    return os.path.abspath(output_csv_path), len(df)


if __name__ == "__main__":
    annotate_female_daily_dataset()
