import pytest
import pandas as pd
from backend.services.preprocessor import clean_indonesian_text, normalize_slang_words, preprocess_review_dataframe

def test_clean_indonesian_text_removes_urls_mentions_emojis():
    raw_text = "Sunscreen Azarine bagus bgt!! 👍😍 Check at http://shopee.co.id/item @user123 #halalBPOM 100%"
    cleaned = clean_indonesian_text(raw_text)
    assert "http" not in cleaned
    assert "@user123" not in cleaned
    assert "👍" not in cleaned
    assert "100" not in cleaned
    assert "halalbpom" in cleaned or "halal" in cleaned

def test_normalize_slang_words():
    raw_text = "tdk ori tp ttp dpt logo bpom dan sertifikat halal mui bgt"
    normalized = normalize_slang_words(raw_text)
    assert "tidak" in normalized
    assert "original" in normalized
    assert "tetap" in normalized
    assert "dapat" in normalized
    assert "sertifikat halal mui" in normalized

def test_preprocess_review_dataframe():
    df_raw = pd.DataFrame({
        "item_id": [1, 2],
        "merek_umkm": ["Wardah", "Kahf"],
        "rating_bintang": [5, 1],
        "teks_ulasan": [
            "Bagus bgt, ori n terdaftar BPOM halal!! https://shopee.co.id",
            "Tdk recommended, palsu bgt dan tdk ada logo halal!!"
        ]
    })
    df_cleaned = preprocess_review_dataframe(df_raw)
    assert "teks_bersih" in df_cleaned.columns
    assert len(df_cleaned) == 2
    assert "tidak" in df_cleaned.iloc[1]["teks_bersih"]
    assert "original" in df_cleaned.iloc[0]["teks_bersih"]


def test_convert_emoticons_to_sentiment_words():
    from backend.services.preprocessor import convert_emoticons_to_sentiment_words
    text = "Produk Wardah bagus bgt 👍😍 tapi yang satu lg cacat 👎😡"
    mapped = convert_emoticons_to_sentiment_words(text)
    assert "bagus" in mapped
    assert "kecewa" in mapped or "buruk" in mapped


def test_correct_indonesian_typos():
    from backend.services.preprocessor import correct_indonesian_typos
    raw_text = "baguusssss bpon halallll murahhh dan terdaftarr"
    corrected = correct_indonesian_typos(raw_text)
    assert "bagus" in corrected
    assert "bpom" in corrected
    assert "halal" in corrected
    assert "murah" in corrected


def test_preprocess_text_advanced():
    from backend.services.preprocessor import preprocess_text_advanced
    raw = "Baguusss bgt 😍 bpon halal MUI!! https://shopee.co.id @seller"
    processed = preprocess_text_advanced(raw)
    assert "bagus" in processed
    assert "banget" in processed
    assert "bpom" in processed
    assert "halal" in processed
    assert "http" not in processed

