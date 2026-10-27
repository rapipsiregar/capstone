"""
Review Explainer Service: Explainable AI & Contextual Skin-Type Analysis.
Generates structured narrative explanations for individual cosmetics reviews,
clarifying trust decisions, skin-type suitability, and actionable insights for MSMEs.
"""

import re
from typing import Dict, Any


SKIN_TYPE_MAP = {
    "dry": "Kulit Kering",
    "oily": "Kulit Berminyak",
    "combination": "Kulit Kombinasi",
    "sensitive": "Kulit Sensitif",
    "acne": "Kulit Berjerawat (Acne-prone)",
    "normal": "Kulit Normal"
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


def generate_review_xai_explanation(review_data: Dict[str, Any], raw_text: str) -> Dict[str, str]:
    """
    Generates a clear 3-point XAI narrative explanation for an individual review:
    1. Alasan Tingkat Kepercayaan (Trust Reason)
    2. Analisis Karakteristik Kulit (Skin Analysis)
    3. Rekomendasi Aksi untuk UMKM (MSME Actionable Takeaway)
    """
    text_lower = str(raw_text or "").lower()
    trust = str(review_data.get("label_kepercayaan", "High_Trust"))
    aspect = str(review_data.get("aspek_komunikasi", "Klaim_Efikasi_Manfaat"))
    brand = str(review_data.get("merek_umkm", "UMKM"))
    skin_profile = _detect_skin_profile(str(review_data.get("kondisi_kulit_usia", "")), text_lower)
    
    # 1. Alasan Kepercayaan
    has_halal = any(k in text_lower for k in ["halal", "mui", "bpom", "segel", "resmi", "original", "ori"])
    has_breakout = any(k in text_lower for k in ["breakout", "beruntusan", "bruntusan", "iritasi", "gatal", "perih", "panas"])
    
    if trust == "High_Trust":
        if has_halal:
            trust_reason = "Tingkat Kepercayaan Tinggi: Kehadiran kata kunci legalitas & sertifikasi resmi (Halal MUI / BPOM) serta respon kepuasan tekstur memberikan bobot atribusi positif terbesar."
        else:
            trust_reason = "Tingkat Kepercayaan Tinggi: Ulasan didominasi oleh kata pendorong positif terkait efektivitas formula, kelembaban, dan kenyamanan pemakaian jangka panjang."
    elif trust == "Low_Trust":
        if has_breakout:
            trust_reason = "Tingkat Kepercayaan Rendah: Sistem mendeteksi kata pemicu keluhan sensitivitas kulit (breakout, beruntusan, perih) yang menurunkan skor kepercayaan publik secara signifikan."
        else:
            trust_reason = "Tingkat Kepercayaan Rendah: Konsumen menyatakan kekecewaan terhadap hasil pemakaian atau kemasan yang tidak memenuhi ekspektasi klaim produk."
    else:
        trust_reason = "Tingkat Kepercayaan Netral: Konsumen mengevaluasi produk dengan sentimen berimbang; produk dinilai cukup baik namun efikasinya belum optimal."

    # 2. Analisis Karakteristik Kulit
    if "Kering" in skin_profile:
        if has_breakout:
            skin_analysis = f"Profil Pengulas: {skin_profile}. Formula produk terindikasi kurang memberi kelembaban atau memiliki kandungan astringent yang memicu rasa kering/iritasi pada lapisan pelindung kulit (skin barrier)."
            suitable_types = "Lebih Sesuai: Kulit Berminyak / Kombinasi (Perlu pelembab ekstra untuk kulit kering)"
        else:
            skin_analysis = f"Profil Pengulas: {skin_profile}. Formulasi hidrasi produk dinilai kompatibel dan efektif mengunci kelembaban tanpa menimbulkan rasa menyengat."
            suitable_types = "Sangat Sesuai: Kulit Normal hingga Kering"
    elif "Berminyak" in skin_profile or "Acne" in skin_profile:
        if has_breakout:
            skin_analysis = f"Profil Pengulas: {skin_profile}. Produk diduga mengandung bahan komedogenik atau konsistensi yang terlalu tebal (*occlusive*), sehingga menyumbat pori dan memicu bruntusan/komedo."
            suitable_types = "Lebih Sesuai: Kulit Kering / Dehidrasi (Hindari untuk kulit berminyak berpori besar)"
        else:
            skin_analysis = f"Profil Pengulas: {skin_profile}. Tekstur produk dinilai ringan, cepat meresap, dan tidak menyumbat pori (*non-comedogenic*), aman untuk kontrol sebum."
            suitable_types = "Sangat Sesuai: Kulit Berminyak & Acne-Prone"
    elif "Sensitif" in skin_profile:
        if has_breakout:
            skin_analysis = f"Profil Pengulas: {skin_profile}. Terjadi reaksi alergi/iritasi kontak ringan. Bahan pewangi (*fragrance*) atau pengawet tertentu berpotensi menjadi pemicu hipersensitivitas."
            suitable_types = "Perhatian Khusus: Lakukan patch-test, lebih ditujukan untuk kulit resisten/normal"
        else:
            skin_analysis = f"Profil Pengulas: {skin_profile}. Formula minim bahan iritan berbahaya, teruji lembut di kulit yang rentan kemerahan."
            suitable_types = "Sangat Sesuai: Kulit Sensitif & Kulit Halus"
    else:
        skin_analysis = f"Profil Pengulas: {skin_profile}. Toleransi kulit konsumen terhadap formula dinilai stabil untuk penggunaan harian."
        suitable_types = "Sesuai: Semua Jenis Kulit (Kulit Normal & Kombinasi)"

    # 3. Rekomendasi untuk UMKM
    if trust == "Low_Trust":
        umkm_rec = f"Saran UMKM ({brand}): Tambahkan anjuran tipe kulit pada label kemasan secara eksplisit ('Disarankan untuk {suitable_types}'), serta edukasikan cara pemakaian bertahap guna memitigasi keluhan konsumen."
    else:
        umkm_rec = f"Saran UMKM ({brand}): Pertahankan konsistensi formula dan tonjolkan klaim keaslian serta sertifikasi halal pada materi promosi digital untuk terus memperkuat loyalitas konsumen."

    return {
        "trust_reason": trust_reason,
        "skin_analysis": skin_analysis,
        "umkm_recommendation": umkm_rec,
        "suitable_skin_types": suitable_types
    }
