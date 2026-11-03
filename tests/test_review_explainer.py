import pytest
from backend.services.review_explainer import generate_review_xai_explanation


def test_generate_review_xai_explanation_high_trust_halal():
    review_data = {
        "merek_umkm": "Wardah",
        "nama_produk": "Lightening Night Cream",
        "kondisi_kulit_usia": "Dry, 20s",
        "rating_bintang": 5,
        "label_kepercayaan": "High_Trust",
        "aspek_komunikasi": "Sertifikasi_Halal_BPOM",
        "klaim_halal": True,
        "klaim_bpom": True
    }
    raw_text = "Suka banget melembabkan kulit keringku. Ada sertifikat halal MUI dan terdaftar BPOM resmi."
    
    explanation = generate_review_xai_explanation(review_data, raw_text)
    
    assert isinstance(explanation, dict)
    assert "trust_reason" in explanation
    assert "skin_analysis" in explanation
    assert "umkm_recommendation" in explanation
    assert "suitable_skin_types" in explanation
    assert "Halal" in explanation["trust_reason"] or "BPOM" in explanation["trust_reason"]
    assert "Kering" in explanation["skin_analysis"] or "Dry" in explanation["skin_analysis"]


def test_generate_review_xai_explanation_low_trust_breakout():
    review_data = {
        "merek_umkm": "Emina",
        "nama_produk": "Acne Defense Gel",
        "kondisi_kulit_usia": "Oily, Acne-prone",
        "rating_bintang": 1,
        "label_kepercayaan": "Low_Trust",
        "aspek_komunikasi": "Kandungan_Bahan_Sensitivitas",
        "klaim_halal": False,
        "klaim_bpom": False
    }
    raw_text = "Nggak cocok sama sekali, malah bikin bruntusan merah dan breakout gatal di hidung."
    
    explanation = generate_review_xai_explanation(review_data, raw_text)
    
    assert "Low Trust" in explanation["trust_reason"] or "keluhan" in explanation["trust_reason"].lower()
    assert "Berminyak" in explanation["skin_analysis"] or "Acne" in explanation["skin_analysis"] or "bruntusan" in explanation["skin_analysis"]
    assert len(explanation["umkm_recommendation"]) > 10


def test_generate_review_xai_explanation_neutral_fallback():
    review_data = {
        "merek_umkm": "Safi",
        "nama_produk": "White Natural Cream",
        "kondisi_kulit_usia": "Combination",
        "rating_bintang": 3,
        "label_kepercayaan": "Neutral",
        "aspek_komunikasi": "Klaim_Efikasi_Manfaat",
        "klaim_halal": False,
        "klaim_bpom": False
    }
    raw_text = "Biasa aja di kulit kombinasi, gak ada efek mencerahkan tapi gak bikin jerawat juga."
    
    explanation = generate_review_xai_explanation(review_data, raw_text)
    
    assert "Netral" in explanation["trust_reason"] or "cukup" in explanation["trust_reason"].lower()
    assert "Kombinasi" in explanation["skin_analysis"]


def test_solusi_a_contextual_umkm_recommendation_per_aspect_and_trust():
    """Solusi A: UMKM recommendations must be specific to the review's aspect & trust level, not hardcoded to Halal."""
    base = {"merek_umkm": "Wardah", "nama_produk": "Serum", "kondisi_kulit_usia": "Normal, 20s", "rating_bintang": 5}

    ef_high = generate_review_xai_explanation(
        {**base, "label_kepercayaan": "High_Trust", "aspek_komunikasi": "Klaim_Efikasi_Manfaat"},
        "Kulit jadi cerah dan lembab banget setelah seminggu pemakaian rutin."
    )
    assert "sertifikasi halal" not in ef_high["umkm_recommendation"].lower()
    assert "efikasi" in ef_high["umkm_recommendation"].lower() or "manfaat" in ef_high["umkm_recommendation"].lower()

    kb_high = generate_review_xai_explanation(
        {**base, "label_kepercayaan": "High_Trust", "aspek_komunikasi": "Kandungan_Bahan_Sensitivitas"},
        "Teksturnya ringan, cepat meresap, dan kandungan niacinamide-nya aman di kulit."
    )
    assert "sertifikasi halal" not in kb_high["umkm_recommendation"].lower()
    assert "bahan" in kb_high["umkm_recommendation"].lower() or "komposisi" in kb_high["umkm_recommendation"].lower()

    pr_high = generate_review_xai_explanation(
        {**base, "label_kepercayaan": "High_Trust", "aspek_komunikasi": "Transparansi_Layanan_Harga"},
        "Harganya terjangkau banget dan kemasan tube-nya praktis dibawa traveling."
    )
    assert "sertifikasi halal" not in pr_high["umkm_recommendation"].lower()
    assert "harga" in pr_high["umkm_recommendation"].lower() or "kemasan" in pr_high["umkm_recommendation"].lower()

    pr_low = generate_review_xai_explanation(
        {**base, "label_kepercayaan": "Low_Trust", "aspek_komunikasi": "Transparansi_Layanan_Harga", "rating_bintang": 2},
        "Kemasan tutupnya gampang patah dan bocor di tas, harganya juga kemahalan."
    )
    assert "kemasan" in pr_low["umkm_recommendation"].lower() or "harga" in pr_low["umkm_recommendation"].lower()

    hl_high = generate_review_xai_explanation(
        {**base, "label_kepercayaan": "High_Trust", "aspek_komunikasi": "Sertifikasi_Halal_BPOM"},
        "Tenang pakainya karena sudah ada nomor BPOM dan logo halal resmi di kemasan."
    )
    assert "halal" in hl_high["umkm_recommendation"].lower() or "bpom" in hl_high["umkm_recommendation"].lower()

