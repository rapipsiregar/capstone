"""
Text Preprocessing Service for Halal Cosmetics NLP.
Handles lowercasing, regex cleaning (URLs, mentions, emojis, numbers), 
slang word normalization, and dataset transformation.
"""

import os
import re
import pandas as pd
from typing import Dict

# Dictionary for Indonesian slang / informal words normalization
SLANG_DICTIONARY: Dict[str, str] = {
    "tdk": "tidak", "gak": "tidak", "ga": "tidak", "ngga": "tidak", "g": "tidak",
    "bgt": "banget", "bgtu": "begitu", "ori": "original", "orig": "original",
    "tp": "tapi", "tpi": "tapi", "ttp": "tetap", "dpt": "dapat", "dapet": "dapat",
    "n": "dan", "dn": "dan", "klo": "kalau", "kalo": "kalau", "utk": "untuk",
    "dr": "dari", "sdh": "sudah", "udah": "sudah", "blm": "belum", "belummm": "belum",
    "krn": "karena", "krna": "karena", "bkin": "bikin", "gmn": "bagaimana", "sy": "saya",
    "scr": "secara", "hrg": "harga", "paking": "packaging", "bgs": "bagus",
    "rekomended": "recommended", "rekomen": "recommended", "recomended": "recommended",
    "blanja": "belanja", "seller": "penjual", "olshop": "toko online", "fast": "cepat", 
    "fastresp": "respon cepat", "mumer": "murah meriah", "beneran": "benar", "kmrn": "kemarin"
}

# Mapping for emoticons & emojis to sentiment-rich Indonesian words
EMOTICON_SENTIMENT_MAP: Dict[str, str] = {
    "👍": " bagus ", "😍": " suka ", "❤️": " cinta ", "⭐": " bintang ",
    "😊": " senang ", "🥰": " suka ", "🔥": " terbaik ", "💯": " sempurna ",
    "👎": " buruk ", "😡": " kecewa ", "😭": " sedih ", "🤮": " buruk ",
    "💔": " kecewa ", "💩": " buruk ", ":)": " senang ", ":-)": " senang ",
    ":(": " kecewa ", ":-(": " kecewa "
}


def convert_emoticons_to_sentiment_words(text: str) -> str:
    """
    Converts emoticons and emojis in text into sentiment-indicative Indonesian words.
    """
    if not isinstance(text, str):
        return ""
    for emo, word in EMOTICON_SENTIMENT_MAP.items():
        if emo in text:
            text = text.replace(emo, word)
    return text


def correct_indonesian_typos(text: str) -> str:
    """
    Corrects common Indonesian typos, repeated character elongation (e.g. baguusss -> bagus),
    and specific cosmetic/BPOM domain typos.
    """
    if not isinstance(text, str):
        return ""
        
    text = text.lower()
    
    # Common cosmetic domain typos
    domain_typos = {
        r'\bbpon\b': 'bpom',
        r'\bbpommm+\b': 'bpom',
        r'\bhalalll*\b': 'halal',
        r'\bbaguusss*\b': 'bagus',
        r'\bmurahhh*\b': 'murah',
        r'\bterdaftarrr*\b': 'terdaftar',
        r'\borii*\b': 'original',
        r'\brekomendedd*\b': 'recommended'
    }
    
    for pattern, replacement in domain_typos.items():
        text = re.sub(pattern, replacement, text)
        
    # Collapse 3+ repeated characters into a single character (e.g. sss -> s)
    text = re.sub(r'([a-zA-Z])\1{2,}', r'\1', text)
    
    return text


def clean_indonesian_text(text: str) -> str:
    """
    Cleans raw Indonesian review text by removing URLs, mentions, hashtags, 
    emojis, digits, and non-alphanumeric characters.
    """
    if not isinstance(text, str):
        return ""
        
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    
    # Remove user mentions
    text = re.sub(r'@\w+', ' ', text)
    
    # Strip hashtag symbol # but preserve the text inside (e.g. #halalBPOM -> halalbpom)
    text = re.sub(r'#(\w+)', r' \1 ', text)
    
    # Remove digits/numbers
    text = re.sub(r'\d+', ' ', text)
    
    # Remove non-alphanumeric characters (keeps letters and spaces, strips emojis/punctuations)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def normalize_slang_words(text: str) -> str:
    """
    Normalizes informal Indonesian words to formal standard Indonesian text.
    """
    words = text.split()
    normalized_words = [SLANG_DICTIONARY.get(w, w) for w in words]
    return " ".join(normalized_words)


def preprocess_text(text: str) -> str:
    """
    Full text preprocessing pipeline for a single string.
    Combines cleaning and slang normalization.
    """
    cleaned = clean_indonesian_text(text)
    return normalize_slang_words(cleaned)


def preprocess_text_advanced(text: str) -> str:
    """
    Advanced preprocessing pipeline incorporating emoticon sentiment conversion,
    typo correction, regex cleaning, and slang word normalization.
    """
    text_with_emo = convert_emoticons_to_sentiment_words(text)
    typo_corrected = correct_indonesian_typos(text_with_emo)
    cleaned = clean_indonesian_text(typo_corrected)
    return normalize_slang_words(cleaned)




def preprocess_review_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses a DataFrame containing raw review texts.
    Adds a 'teks_bersih' column.
    """
    df = df.copy()
    if "teks_ulasan" in df.columns:
        df["teks_bersih"] = df["teks_ulasan"].apply(lambda t: normalize_slang_words(clean_indonesian_text(str(t))))
    return df


def process_and_save_cleaned_dataset(
    raw_csv_path: str = "data/raw/shopee_reviews_raw.csv",
    output_csv_path: str = "data/cleaned/shopee_reviews_cleaned.csv"
) -> str:
    """
    Loads raw CSV dataset, performs preprocessing pipeline, and saves cleaned dataset.
    """
    if not os.path.exists(raw_csv_path):
        raise FileNotFoundError(f"Raw dataset not found at {raw_csv_path}")
        
    df_raw = pd.read_csv(raw_csv_path)
    df_cleaned = preprocess_review_dataframe(df_raw)
    
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df_cleaned.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
    
    return os.path.abspath(output_csv_path)


if __name__ == "__main__":
    saved_path = process_and_save_cleaned_dataset()
    print(f"[Preprocessor Success] Cleaned dataset saved to {saved_path}")
