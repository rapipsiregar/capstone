import os
import pytest
from backend.services.database import (
    init_db,
    save_review_log,
    get_recent_logs,
    get_analytics_summary,
)


@pytest.fixture
def temp_db_path(tmp_path):
    db_file = tmp_path / "test_history.db"
    init_db(db_path=str(db_file))
    return str(db_file)


def test_init_db(temp_db_path):
    assert os.path.exists(temp_db_path)


def test_save_and_get_recent_logs(temp_db_path):
    log_id = save_review_log({
        "raw_text": "Sertifikat halal BPOM jelas.",
        "cleaned_text": "sertifikat halal bpom jelas",
        "predicted_aspect": "Sertifikasi_Halal_BPOM",
        "aspect_confidence": 0.95,
        "predicted_trust": "High_Trust",
        "trust_confidence": 0.90,
        "model_type": "IndoBERT Transformer",
        "execution_time_ms": 12.5
    }, db_path=temp_db_path)

    assert log_id > 0

    logs = get_recent_logs(limit=10, db_path=temp_db_path)
    assert len(logs) == 1
    assert logs[0]["raw_text"] == "Sertifikat halal BPOM jelas."
    assert logs[0]["predicted_aspect"] == "Sertifikasi_Halal_BPOM"
    assert logs[0]["predicted_trust"] == "High_Trust"


def test_get_analytics_summary(temp_db_path):
    save_review_log({
        "raw_text": "Produk halal BPOM aman.",
        "cleaned_text": "produk halal bpom aman",
        "predicted_aspect": "Sertifikasi_Halal_BPOM",
        "aspect_confidence": 0.95,
        "predicted_trust": "High_Trust",
        "trust_confidence": 0.90,
        "model_type": "IndoBERT",
        "execution_time_ms": 10.0
    }, db_path=temp_db_path)

    save_review_log({
        "raw_text": "Kemasan rusak dan tidak ada logo.",
        "cleaned_text": "kemasan rusak dan tidak ada logo",
        "predicted_aspect": "Transparansi_Layanan",
        "aspect_confidence": 0.85,
        "predicted_trust": "Low_Trust",
        "trust_confidence": 0.88,
        "model_type": "IndoBERT",
        "execution_time_ms": 11.0
    }, db_path=temp_db_path)

    summary = get_analytics_summary(db_path=temp_db_path)
    assert summary["total_reviews"] == 2
    assert "aspect_counts" in summary
    assert "trust_counts" in summary
    assert summary["aspect_counts"]["Sertifikasi_Halal_BPOM"] == 1
    assert summary["trust_counts"]["High_Trust"] == 1
    assert summary["trust_counts"]["Low_Trust"] == 1
