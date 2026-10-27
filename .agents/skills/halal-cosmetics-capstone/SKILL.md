---
name: halal-cosmetics-capstone
description: >-
  Prosedur dan workflow teknis untuk pengolahan dataset ulasan kosmetik halal Female Daily (Kaggle),
  preprocessing teks Bahasa Indonesia, fine-tuning model IndoBERT, eksekusi SHAP XAI,
  serta integrasi FastAPI backend dan web dashboard.
---

# Skill: Halal Cosmetics NLP & XAI Capstone Workflow

Skill ini berisi panduan prosedur teknis (cheatsheet & runbook) yang dipanggil oleh AI Agent saat mengeksekusi tahapan dalam pengembangan aplikasi NLP & Explainable AI untuk Kosmetik Halal.

---

## 1. Prosedur Ingestion Dataset Female Daily (Kaggle)
Dataset ulasan bersumber tunggal dari hasil ekstraksi Kaggle Female Daily (`00. InfoProduct.csv` dan `00. Review.csv` di `data/raw/`). Pengolahan dan penggabungan dilakukan melalui pipeline service `backend/services/ingest_female_daily.py`:
```python
import pandas as pd
from backend.services.ingest_female_daily import (
    validate_female_daily_schema,
    clean_female_daily_reviews,
)

def load_and_ingest_female_daily(raw_reviews_path: str, info_product_path: str) -> pd.DataFrame:
    # Memuat berkas ulasan dan informasi produk hasil ekstraksi Kaggle
    reviews_df = pd.read_csv(raw_reviews_path)
    products_df = pd.read_csv(info_product_path)
    
    # Penggabungan metadata produk (Merk, Category, Product) dengan isi ulasan
    merged_df = pd.merge(reviews_df, products_df, on="Product", how="left")
    
    # Validasi integritas skema dan pembersihan teks terstruktur
    is_valid, report = validate_female_daily_schema(merged_df)
    if is_valid:
        cleaned_df = clean_female_daily_reviews(merged_df)
        return cleaned_df
    raise ValueError(f"Schema validation failed: {report}")
```

---

## 2. Prosedur Cleaning & Normalisasi Teks Bahasa Indonesia
Lakukan langkah-langkah preprocessing wajib berikut:
1. Lowercase semua karakter.
2. Hapus URL (`http...`), mention (`@user`), hashtag (`#tag`), emoji, dan simbol non-alphanumeric.
3. Normalisasi kata slang Bahasa Indonesia menggunakan dictionary kamus gaul (misal: `tdk` -> `tidak`, `ori` -> `original`).
4. Hapus spasi berlebih.

---

## 3. Prosedur Fine-Tuning IndoBERT (PyTorch & Hugging Face)
1. gunakan pre-trained model: `indobenchmark/indobert-base-p1` atau `indolem/indobert-base-uncased`.
2. Gunakan `AutoTokenizer` dan `AutoModelForSequenceClassification`.
3. Set hyperparameter acuan:
   * `epochs`: 3 - 5
   * `batch_size`: 16 atau 32
   * `learning_rate`: `2e-5`
   * `optimizer`: AdamW
4. Hitung metrik evaluasi: Accuracy, Precision, Recall, Macro F1-score.

---

## 4. Prosedur Ekstraksi Explainable AI (SHAP)
Jalankan modul `shap.Explainer` pada model fine-tuned untuk mendapatkan skor atribusi kata:
```python
import shap
import torch

def get_text_explanation(text: str, model, tokenizer):
    def predict_prob(texts):
        inputs = tokenizer(texts.tolist(), padding=True, truncation=True, return_tensors="pt")
        outputs = model(**inputs)
        return torch.softmax(outputs.logits, dim=1).detach().numpy()

    explainer = shap.Explainer(predict_prob, tokenizer)
    shap_values = explainer([text])
    return shap_values
```

---

## 5. Prosedur Integrasi FastAPI
Pastikan endpoint `/api/v1/predict` dan `/api/v1/explain` mengembalikan respons JSON terstruktur dengan standar waktu tanggap < 1.5 detik.
