"""
Data Annotation Service for Halal Cosmetics Capstone.
Implements taxonomy labeling for Aspect Communication & Public Trust Sentiment.
"""

import os
import pandas as pd
from typing import Tuple, List

ASPECT_LABELS: List[str] = [
    "Sertifikasi_Halal_BPOM", 
    "Kandungan_Bahan", 
    "Klaim_Efikasi_Manfaat", 
    "Transparansi_Layanan"
]

TRUST_LABELS: List[str] = [
    "High_Trust", 
    "Neutral", 
    "Low_Trust"
]

# Keyword dictionaries for aspect taxonomy classification
BPOM_KEYWORDS = ["bpom", "halal", "sertifikat", "mui", "bpjph", "logo", "segel", "terdaftar", "dusnya"]
INGREDIENT_KEYWORDS = ["kandungan", "bahan", "alkohol", "kimia", "merkuri", "niacinamide", "alami", "sensitif", "bumil", "iritasi"]
EFFICACY_KEYWORDS = ["tekstur", "meresap", "mencerahkan", "jerawat", "hasil", "bruntusan", "efek", "muka", "kulit"]
SERVICE_KEYWORDS = ["penjual", "seller", "pengiriman", "toko", "ramah", "respon", "kemasan", "penyok", "packaging", "palsu", "ori", "original", "keaslian"]


def annotate_single_review(text: str, rating_star: int = 5) -> Tuple[str, str]:
    """
    Annotates a single cleaned review text into (label_aspek, label_kepercayaan).
    """
    text_lower = str(text).lower()
    
    # 1. Determine Aspect Label
    scores = {
        "Sertifikasi_Halal_BPOM": sum(1 for kw in BPOM_KEYWORDS if kw in text_lower),
        "Kandungan_Bahan": sum(1 for kw in INGREDIENT_KEYWORDS if kw in text_lower),
        "Klaim_Efikasi_Manfaat": sum(1 for kw in EFFICACY_KEYWORDS if kw in text_lower),
        "Transparansi_Layanan": sum(1 for kw in SERVICE_KEYWORDS if kw in text_lower)
    }
    
    # Select aspect with highest keyword frequency, default to Sertifikasi_Halal_BPOM if tied
    max_score = max(scores.values())
    if max_score > 0:
        aspect = max(scores, key=scores.get)
    else:
        aspect = "Sertifikasi_Halal_BPOM"
        
    # 2. Determine Public Trust Label
    low_trust_words = ["palsu", "meragukan", "tidak ada", "kecewa", "bruntusan", "penyok", "ragu", "overclaim", "lama"]
    high_trust_words = ["resmi", "mantap", "puas", "terdaftar", "cocok", "bagus", "cepat", "ramah", "aman"]
    
    has_low_signal = any(w in text_lower for w in low_trust_words) or rating_star <= 2
    has_high_signal = any(w in text_lower for w in high_trust_words) or rating_star >= 4
    
    if has_low_signal and not (rating_star >= 4 and not any(w in text_lower for w in low_trust_words)):
        trust = "Low_Trust"
    elif "?" in text_lower or rating_star == 3 or "apakah" in text_lower:
        trust = "Neutral"
    elif has_high_signal:
        trust = "High_Trust"
    else:
        trust = "Neutral"
        
    return aspect, trust


def annotate_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Annotates full DataFrame with 'label_aspek' and 'label_kepercayaan'.
    """
    df = df.copy()
    aspects = []
    trusts = []
    
    text_col = "teks_bersih" if "teks_bersih" in df.columns else "teks_ulasan"
    rating_col = "rating_bintang" if "rating_bintang" in df.columns else None
    
    for idx, row in df.iterrows():
        text = row[text_col]
        rating = row[rating_col] if rating_col and pd.notna(row[rating_col]) else 5
        asp, trs = annotate_single_review(text, int(rating))
        aspects.append(asp)
        trusts.append(trs)
        
    df["label_aspek"] = aspects
    df["label_kepercayaan"] = trusts
    return df


def calculate_cohens_kappa(annotations_a: List[str], annotations_b: List[str]) -> float:
    """
    Calculates Cohen's Kappa coefficient (inter-annotator agreement score).
    kappa = (p_o - p_e) / (1 - p_e)
    """
    if not annotations_a or not annotations_b or len(annotations_a) != len(annotations_b):
        return 0.0
        
    n = len(annotations_a)
    categories = list(set(annotations_a).union(set(annotations_b)))
    if not categories:
        return 1.0
        
    # Observed agreement
    p_o = sum(1 for a, b in zip(annotations_a, annotations_b) if a == b) / n
    
    # Expected agreement
    p_e = 0.0
    for cat in categories:
        count_a = sum(1 for a in annotations_a if a == cat)
        count_b = sum(1 for b in annotations_b if b == cat)
        p_e += (count_a / n) * (count_b / n)
        
    if p_e == 1.0:
        return 1.0
        
    kappa = (p_o - p_e) / (1.0 - p_e)
    return float(round(kappa, 4))


def select_uncertain_samples_for_active_learning(df: pd.DataFrame, sample_size: int = 10) -> pd.DataFrame:
    """
    Identifies low-confidence, neutral, or ambiguous reviews for active learning human re-annotation.
    """
    if df.empty:
        return df.copy()
        
    df_copy = df.copy()
    text_col = "teks_bersih" if "teks_bersih" in df_copy.columns else "teks_ulasan"
    rating_col = "rating_bintang" if "rating_bintang" in df_copy.columns else None
    
    ambiguous_indices = []
    for idx, row in df_copy.iterrows():
        text = str(row[text_col]).lower()
        rating = row[rating_col] if rating_col and pd.notna(row[rating_col]) else 3
        
        # Ambiguity heuristics: neutral rating 3, questions '?', or multi-keyword tie
        is_question = "?" in text or "apakah" in text
        is_neutral_rating = rating == 3
        is_short = len(text.split()) < 4
        
        if is_question or is_neutral_rating or is_short:
            ambiguous_indices.append(idx)
            
    if not ambiguous_indices:
        return df_copy.head(sample_size)
        
    return df_copy.loc[ambiguous_indices].head(sample_size)


def validate_dataset_annotation_quality(df: pd.DataFrame) -> dict:
    """
    Validates dataset annotation quality, checking distribution balance and missing fields.
    """
    total = len(df)
    if total == 0:
        return {"total_samples": 0, "is_valid": False, "reason": "Dataset is empty"}
        
    has_aspect = "label_aspek" in df.columns
    has_trust = "label_kepercayaan" in df.columns
    
    aspect_dist = df["label_aspek"].value_counts().to_dict() if has_aspect else {}
    trust_dist = df["label_kepercayaan"].value_counts().to_dict() if has_trust else {}
    
    is_valid = has_aspect and has_trust and total > 0
    return {
        "total_samples": total,
        "is_valid": is_valid,
        "aspect_distribution": aspect_dist,
        "trust_distribution": trust_dist,
        "has_missing_labels": df["label_aspek"].isnull().any() if has_aspect else True
    }



def process_and_save_annotated_dataset(
    cleaned_csv_path: str = "data/cleaned/female_daily_skincare_cleaned.csv",
    output_csv_path: str = "data/annotated/female_daily_skincare_annotated.csv"
) -> str:
    """
    Reads cleaned CSV dataset, applies taxonomy annotation, and saves annotated dataset.
    """
    if not os.path.exists(cleaned_csv_path):
        raise FileNotFoundError(f"Cleaned dataset not found at {cleaned_csv_path}")
        
    df_cleaned = pd.read_csv(cleaned_csv_path)
    df_annotated = annotate_dataset(df_cleaned)
    
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df_annotated.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
    
    return os.path.abspath(output_csv_path)


if __name__ == "__main__":
    saved_path = process_and_save_annotated_dataset()
    print(f"[Annotator Success] Annotated dataset saved to {saved_path}")
