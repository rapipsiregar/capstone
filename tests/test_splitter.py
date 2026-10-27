import pytest
import pandas as pd
from backend.services.splitter import split_dataset_stratified

def test_split_dataset_stratified_ratios():
    # Create sample annotated dataframe with 100 rows
    records = []
    for i in range(100):
        records.append({
            "item_id": i,
            "merek_umkm": "Wardah" if i % 2 == 0 else "Somethinc",
            "teks_bersih": f"ulasan contoh kehalalan dan bpom ke-{i}",
            "label_aspek": "Sertifikasi_Halal_BPOM" if i % 3 == 0 else "Kandungan_Bahan",
            "label_kepercayaan": "High_Trust" if i % 2 == 0 else "Low_Trust"
        })
    df_sample = pd.DataFrame(records)
    
    df_train, df_val, df_test = split_dataset_stratified(df_sample, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1, random_state=42)
    
    assert len(df_train) == 80
    assert len(df_val) == 10
    assert len(df_test) == 10
    assert len(set(df_train["item_id"]).intersection(set(df_val["item_id"]))) == 0
    assert len(set(df_train["item_id"]).intersection(set(df_test["item_id"]))) == 0
    assert len(set(df_val["item_id"]).intersection(set(df_test["item_id"]))) == 0

def test_split_dataset_stratified_preserves_columns():
    records = [{"item_id": i, "teks_bersih": "teks", "label_aspek": "A", "label_kepercayaan": "High_Trust"} for i in range(50)]
    df_sample = pd.DataFrame(records)
    df_tr, df_va, df_te = split_dataset_stratified(df_sample, 0.8, 0.1, 0.1)
    assert "label_aspek" in df_tr.columns
    assert "label_kepercayaan" in df_tr.columns
