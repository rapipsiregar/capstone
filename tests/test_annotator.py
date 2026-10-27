import pytest
import pandas as pd
from backend.services.annotator import annotate_single_review, annotate_dataset, ASPECT_LABELS, TRUST_LABELS

def test_annotate_single_review_sertifikasi_high_trust():
    text = "dus packaging tertera logo bpom dan sertifikat halal mui resmi"
    rating = 5
    aspect, trust = annotate_single_review(text, rating)
    assert aspect == "Sertifikasi_Halal_BPOM"
    assert trust == "High_Trust"

def test_annotate_single_review_kandungan_low_trust():
    text = "baunya menyengat meragukan dan tidak ada logo bpom halal"
    rating = 1
    aspect, trust = annotate_single_review(text, rating)
    assert trust == "Low_Trust"

def test_annotate_dataset_dataframe():
    df_cleaned = pd.DataFrame({
        "item_id": [101, 102, 103],
        "merek_umkm": ["Wardah", "Hanasui", "Somethinc"],
        "rating_bintang": [5, 1, 4],
        "teks_ulasan": [
            "Resmi BPOM halal MUI terdaftar.",
            "Produk palsu meragukan tidak ada BPOM.",
            "Apakah aman untuk bumil?"
        ],
        "teks_bersih": [
            "resmi bpom halal mui terdaftar",
            "produk palsu meragukan tidak ada bpom",
            "apakah aman untuk bumil"
        ]
    })
    df_annotated = annotate_dataset(df_cleaned)
    assert "label_aspek" in df_annotated.columns
    assert "label_kepercayaan" in df_annotated.columns
    assert set(df_annotated["label_aspek"].unique()).issubset(set(ASPECT_LABELS))
    assert set(df_annotated["label_kepercayaan"].unique()).issubset(set(TRUST_LABELS))
    assert len(df_annotated) == 3


def test_calculate_cohens_kappa():
    from backend.services.annotator import calculate_cohens_kappa
    a = ["High_Trust", "High_Trust", "Low_Trust", "Neutral"]
    b = ["High_Trust", "High_Trust", "Low_Trust", "Low_Trust"]
    kappa = calculate_cohens_kappa(a, b)
    assert isinstance(kappa, float)
    assert -1.0 <= kappa <= 1.0
    assert kappa > 0.4  # Moderate agreement expected


def test_select_uncertain_samples_for_active_learning():
    from backend.services.annotator import select_uncertain_samples_for_active_learning
    df = pd.DataFrame({
        "item_id": [1, 2, 3, 4],
        "teks_bersih": [
            "sertifikat bpom halal mui resmi",
            "apakah produk ini aman dan original?",
            "tekstur cair agak aneh",
            "bagus sekali memuaskan"
        ],
        "rating_bintang": [5, 3, 3, 5]
    })
    df_uncertain = select_uncertain_samples_for_active_learning(df, sample_size=2)
    assert isinstance(df_uncertain, pd.DataFrame)
    assert len(df_uncertain) <= 2


def test_validate_dataset_annotation_quality():
    from backend.services.annotator import validate_dataset_annotation_quality
    df = pd.DataFrame({
        "label_aspek": ["Sertifikasi_Halal_BPOM", "Kandungan_Bahan", "Sertifikasi_Halal_BPOM"],
        "label_kepercayaan": ["High_Trust", "Low_Trust", "High_Trust"]
    })
    report = validate_dataset_annotation_quality(df)
    assert isinstance(report, dict)
    assert report["total_samples"] == 3
    assert report["is_valid"] is True
    assert "aspect_distribution" in report
    assert "trust_distribution" in report

