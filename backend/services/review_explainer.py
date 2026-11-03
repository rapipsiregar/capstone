"""
Review Explainer Service: Explainable AI & Contextual Skin-Type Analysis (Solusi A).
Generates structured narrative explanations for individual cosmetics reviews,
mapping trust decisions and MSME recommendations to each communication aspect
(Efikasi & Manfaat, Kandungan & Sensitivitas, Harga & Kemasan, Legalitas & Keaslian).
"""

from typing import Dict, Any
from backend.services.catalog_shap_cacher import get_cached_review_shap

ASPECT_LABELS = {
    "Klaim_Efikasi_Manfaat": "Efikasi & Manfaat",
    "Kandungan_Bahan_Sensitivitas": "Kandungan & Sensitivitas",
    "Transparansi_Layanan_Harga": "Harga & Kemasan",
    "Sertifikasi_Halal_BPOM": "Legalitas & Keaslian",
}


def _detect_skin_profile(profile_str: str, text: str) -> str:
    """Detects and normalizes consumer skin condition from profile metadata or text."""
    combined = f"{profile_str} {text}".lower()
    detected = []

    if "dry" in combined or "kering" in combined:
        detected.append("Kulit Kering")
    if "oily" in combined or "berminyak" in combined or "sebum" in combined:
        detected.append("Kulit Berminyak")
    if "sensitive" in combined or "sensitif" in combined or "gampang merah" in combined:
        detected.append("Kulit Sensitif")
    if "acne" in combined or "jerawat" in combined or "bruntus" in combined or "beruntus" in combined:
        detected.append("Kulit Berjerawat (Acne-prone)")
    if "combination" in combined or "kombinasi" in combined:
        detected.append("Kulit Kombinasi")

    if not detected:
        return "Kulit Normal / Umum"
    return " & ".join(detected[:2])


def _skin_analysis(skin_profile: str, has_breakout: bool) -> tuple[str, str]:
    """Returns (skin_analysis_text, suitable_skin_types_label)."""
    if "Kering" in skin_profile:
        if has_breakout:
            return (
                f"Profil Pengulas: {skin_profile}. Formula terindikasi kurang memberi kelembaban atau memicu iritasi pada lapisan pelindung kulit (skin barrier).",
                "Lebih Sesuai: Kulit Berminyak / Kombinasi (Perlu pelembab ekstra untuk kulit kering)",
            )
        return (
            f"Profil Pengulas: {skin_profile}. Formulasi hidrasi produk dinilai kompatibel dan efektif mengunci kelembaban.",
            "Sangat Sesuai: Kulit Normal hingga Kering",
        )
    if "Berminyak" in skin_profile or "Acne" in skin_profile:
        if has_breakout:
            return (
                f"Profil Pengulas: {skin_profile}. Produk diduga bertekstur terlalu tebal (occlusive) sehingga menyumbat pori dan memicu bruntusan.",
                "Lebih Sesuai: Kulit Kering / Dehidrasi (Hindari untuk kulit berminyak berpori besar)",
            )
        return (
            f"Profil Pengulas: {skin_profile}. Tekstur produk dinilai ringan, cepat meresap, dan tidak menyumbat pori (non-comedogenic).",
            "Sangat Sesuai: Kulit Berminyak & Acne-Prone",
        )
    if "Sensitif" in skin_profile:
        if has_breakout:
            return (
                f"Profil Pengulas: {skin_profile}. Terjadi reaksi iritasi ringan; pewangi atau bahan aktif tertentu berpotensi memicu hipersensitivitas.",
                "Perhatian Khusus: Lakukan patch-test, lebih ditujukan untuk kulit normal",
            )
        return (
            f"Profil Pengulas: {skin_profile}. Formula minim bahan iritan dan teruji lembut di kulit yang rentan kemerahan.",
            "Sangat Sesuai: Kulit Sensitif & Kulit Halus",
        )
    return (
        f"Profil Pengulas: {skin_profile}. Toleransi kulit konsumen terhadap formula dinilai stabil untuk penggunaan harian.",
        "Sesuai: Semua Jenis Kulit (Kulit Normal & Kombinasi)",
    )


def _contextual_umkm_advice(brand: str, aspect: str, trust: str, suitable_types: str) -> str:
    """Returns actionable MSME recommendation tailored to the review's communication aspect and trust level."""
    if aspect == "Sertifikasi_Halal_BPOM":
        if trust == "Low_Trust":
            return f"Saran UMKM ({brand}): Perkuat fitur verifikasi keaslian kemasan (segel resmi) serta cantumkan nomor BPOM dan sertifikasi halal secara jelas untuk menghilangkan keraguan konsumen."
        if trust == "Neutral":
            return f"Saran UMKM ({brand}): Tampilkan nomor izin edar BPOM dan informasi sertifikasi halal secara lebih mudah terbaca pada kemasan maupun deskripsi produk."
        return f"Saran UMKM ({brand}): Pertahankan transparansi nomor registrasi BPOM, logo Halal resmi, dan segel keaslian produk sebagai jaminan keamanan bagi konsumen."

    if aspect == "Kandungan_Bahan_Sensitivitas":
        if trust == "Low_Trust":
            return f"Saran UMKM ({brand}): Tambahkan panduan kecocokan tipe kulit secara eksplisit ('{suitable_types}') dan anjuran patch-test pada kemasan untuk mencegah reaksi sensitivitas."
        if trust == "Neutral":
            return f"Saran UMKM ({brand}): Cantumkan informasi konsentrasi bahan aktif dan panduan kombinasi pemakaian untuk {suitable_types} agar konsumen lebih yakin."
        return f"Saran UMKM ({brand}): Pertahankan keamanan komposisi bahan yang ramah kulit ({suitable_types}) dan tonjolkan keunggulan tekstur serta bahan aktif pada edukasi produk."

    if aspect == "Transparansi_Layanan_Harga":
        if trust == "Low_Trust":
            return f"Saran UMKM ({brand}): Tingkatkan kontrol kualitas fisik kemasan (tutup/aplikator/segel) dan evaluasi kesesuaian porsi isi terhadap harga produk."
        if trust == "Neutral":
            return f"Saran UMKM ({brand}): Pertimbangkan inovasi ukuran kemasan (travel/refill size) atau peningkatan kualitas kemasan agar sebanding dengan ekspektasi harga konsumen."
        return f"Saran UMKM ({brand}): Pertahankan daya saing harga (value-for-money) serta kepraktisan dan higienitas desain kemasan yang disukai konsumen."

    # Default: Klaim_Efikasi_Manfaat
    if trust == "Low_Trust":
        return f"Saran UMKM ({brand}): Evaluasi kesesuaian klaim manfaat dengan hasil nyata serta tambahkan panduan pemakaian bertahap ('Disarankan untuk {suitable_types}') guna memitigasi keluhan."
    if trust == "Neutral":
        return f"Saran UMKM ({brand}): Perjelas ekspektasi durasi pemakaian rutin pada kemasan agar manfaat efikasi produk (untuk {suitable_types}) dirasakan lebih optimal."
    return f"Saran UMKM ({brand}): Pertahankan konsistensi efikasi formula dan tonjolkan bukti manfaat nyata pemakaian (untuk {suitable_types}) pada komunikasi produk."


def generate_review_xai_explanation(review_data: Dict[str, Any], raw_text: str) -> Dict[str, str]:
    """Generates a 3-point XAI explanation tailored to aspect, trust level, SHAP words, and skin profile."""
    text_lower = str(raw_text or "").lower()
    trust = str(review_data.get("label_kepercayaan", "High_Trust"))
    aspect = str(review_data.get("aspek_komunikasi", "Klaim_Efikasi_Manfaat"))
    aspect_name = ASPECT_LABELS.get(aspect, aspect.replace("_", " "))
    brand = str(review_data.get("merek_umkm", "UMKM"))
    skin_profile = _detect_skin_profile(str(review_data.get("kondisi_kulit_usia", "")), text_lower)

    has_halal = any(k in text_lower for k in ["halal", "mui", "bpom", "segel", "resmi", "original", "ori"])
    has_breakout = any(k in text_lower for k in ["breakout", "beruntusan", "bruntusan", "iritasi", "gatal", "perih", "panas"])

    cached_shap = get_cached_review_shap(raw_text)
    if cached_shap:
        top_pos = cached_shap.get("top_positive_words", [])
        top_neg = cached_shap.get("top_negative_words", [])
        if trust == "High_Trust" and top_pos:
            trust_reason = f"Tingkat Kepercayaan Tinggi (SHAP IndoBERT · {aspect_name}): Kata pendorong utama '{', '.join(top_pos[:3])}' memberikan atribusi Shapley positif tertinggi."
        elif trust == "Low_Trust" and top_neg:
            trust_reason = f"Tingkat Kepercayaan Rendah (SHAP IndoBERT · {aspect_name}): Kata pemicu keluhan '{', '.join(top_neg[:3])}' memberikan atribusi negatif signifikan."
        else:
            trust_reason = cached_shap.get("explanation_summary", f"Analisis SHAP pada aspek {aspect_name} menunjukkan atribusi fitur yang seimbang.")
    elif trust == "High_Trust":
        if aspect == "Sertifikasi_Halal_BPOM" or has_halal:
            trust_reason = "Tingkat Kepercayaan Tinggi: Kehadiran kata kunci legalitas & sertifikasi resmi (Halal MUI / BPOM) serta kepuasan pemakaian memberikan bobot atribusi positif terbesar."
        elif aspect == "Transparansi_Layanan_Harga":
            trust_reason = "Tingkat Kepercayaan Tinggi: Konsumen menilai harga produk sepadan dengan kualitas (value-for-money) dan desain kemasan praktis."
        elif aspect == "Kandungan_Bahan_Sensitivitas":
            trust_reason = "Tingkat Kepercayaan Tinggi: Komposisi bahan dan tekstur produk dinilai aman, ringan, serta cocok dengan kondisi kulit pengulas."
        else:
            trust_reason = "Tingkat Kepercayaan Tinggi: Ulasan didominasi oleh kata pendorong positif terkait efektivitas manfaat formula dan kenyamanan pemakaian."
    elif trust == "Low_Trust":
        if has_breakout:
            trust_reason = "Tingkat Kepercayaan Rendah: Sistem mendeteksi kata pemicu keluhan sensitivitas kulit (breakout, beruntusan, perih) yang menurunkan skor kepercayaan."
        elif aspect == "Transparansi_Layanan_Harga":
            trust_reason = "Tingkat Kepercayaan Rendah: Konsumen mengeluhkan kualitas fisik kemasan atau harga yang dinilai kurang sepadan dengan isi produk."
        else:
            trust_reason = "Tingkat Kepercayaan Rendah: Konsumen menyatakan ketidakpuasan terhadap hasil efikasi pemakaian yang belum memenuhi ekspektasi klaim produk."
    else:
        trust_reason = f"Tingkat Kepercayaan Netral ({aspect_name}): Konsumen mengevaluasi produk dengan sentimen berimbang; produk dinilai cukup baik namun hasilnya belum maksimal."

    skin_analysis, suitable_types = _skin_analysis(skin_profile, has_breakout)
    umkm_rec = _contextual_umkm_advice(brand, aspect, trust, suitable_types)

    return {
        "trust_reason": trust_reason,
        "skin_analysis": skin_analysis,
        "umkm_recommendation": umkm_rec,
        "suitable_skin_types": suitable_types,
    }
