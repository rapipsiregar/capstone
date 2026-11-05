"""
Review Explainer Service: Explainable AI & Per-Review Comment-Driven MSME Advice.
Generates structured explanations for individual cosmetics reviews where both
'Alasan Model' and 'Saran UMKM' are dynamically synthesized from each review's
specific text signals, SHAP word attributions, and skin profile (<= 256 LOC).
"""

import re
from typing import Dict, Any, List, Tuple
from backend.services.catalog_shap_cacher import get_cached_review_shap

NEG_SIGNALS: List[Tuple[List[str], str, str]] = [
    (["ganti kemasan", "ganti ingredient", "ganti formula", "formula baru"], "perubahan formula/kemasan dibanding versi sebelumnya", "sediakan informasi transisi komposisi baru dan uji kecocokan bertahap bagi pengguna lama"),
    (["komedogenik", "comedogenic", "komedo", "komedoan"], "indikasi komedogenik (memicu komedo/pori tersumbat)", "evaluasi bahan bersifat occlusive dan tambahkan klaim uji non-comedogenic"),
    (["panas", "perih", "cekit", "nyelekit", "terbakar"], "sensasi panas/perih di kulit saat pemakaian", "tinjau kadar bahan aktif/pewangi yang memicu sensasi hangat serta cantumkan anjuran patch-test"),
    (["bruntusan", "beruntusan", "breakout"], "reaksi bruntusan dan breakout", "tambahkan peringatan kecocokan jenis kulit pada kemasan serta edukasi pemakaian tipis di awal"),
    (["jerawat", "jerawatan"], "munculnya jerawat baru pasca pemakaian", "perjelas panduan tipe kulit pada label agar dihindari oleh kulit rentan berjerawat"),
    (["gatal", "gatel", "merah", "kemerahan", "iritasi", "alergi", "mengelupas", "ngelupas"], "reaksi iritasi (gatal/kemerahan/mengelupas)", "evaluasi potensi bahan iritan dan sarankan penghentian pemakaian bila muncul hipersensitivitas"),
    (["kucel", "kusam", "gelap", "abu-abu", "ashy", "oksidasi"], "efek tampilan wajah menjadi kusam/kucel", "optimalkan stabilitas oksidasi formula di kulit berminyak/kombinasi agar warna tetap cerah"),
    (["lengket", "berat", "greasy", "kilang minyak", "lem fox", "dempul", "whitecast", "white cast"], "tekstur yang terasa berat/lengket saat diaplikasikan", "perbaiki viskositas emulsi agar lebih ringan, bebas lengket, dan nyaman diratakan"),
    (["kering", "ketarik", "kesat"], "efek kulit terasa kering atau tertarik", "tambahkan agen humektan penyeimbang kelembaban agar skin barrier tetap terjaga"),
    (["bau", "menyengat", "parfum", "fragrance", "alkohol", "alcohol"], "aroma atau kandungan alkohol yang menyengat", "pertimbangkan opsi minim pewangi (fragrance-free/gentle scent) untuk kenyamanan pemakaian"),
    (["bocor", "patah", "tumpah", "susah keluar", "macet"], "keluhan fisik kemasan/aplikator", "perketat kontrol kualitas tutup dan wadah kemasan agar aman dibawa bepergian"),
    (["mahal", "kemahalan", "overprice", "overpriced", "gak worth", "ga worth"], "persepsi harga yang kurang sepadan dengan hasil", "hadirkan variasi ukuran ekonomis (mini/sachet) agar konsumen dapat mencoba lebih dulu"),
    (["biasa aja", "ga ngaruh", "gak ngaruh", "belum kelihatan", "kurang nampol", "kurang cocok", "ga cocok", "gak cocok", "tidak cocok"], "efek manfaat yang belum terasa signifikan di kulit", "cantumkan estimasi durasi pemakaian rutin pada kemasan agar ekspektasi konsumen terukur"),
]

POS_SIGNALS: List[Tuple[List[str], str, str]] = [
    (["halal", "mui", "bpom", "resmi", "segel", "original", "ori"], "jaminan sertifikasi Halal/BPOM resmi", "pertahankan pencantuman nomor BPOM dan logo Halal secara jelas pada kemasan dan toko resmi"),
    (["blue light", "spf", "uv", "radiasi", "protection", "melindungi"], "fitur perlindungan kulit (UV/Blue Light Protection)", "tonjolkan klaim proteksi sinar UV/Blue Light sebagai nilai jual utama produk harian"),
    (["niacinamide", "vitamin c", "vit c", "centella", "cica", "salicylic", "aha", "bha", "hyaluronic", "ceramide", "aloe", "tea tree", "collagen", "retinol"], "daya tarik kandungan bahan aktif", "perkuat edukasi manfaat bahan aktif unggulan tersebut pada materi komunikasi brand"),
    (["cepet menyerap", "cepat menyerap", "mudah meresap", "cepat meresap", "meresap", "ringan", "gampang di blend", "mudah dibaurkan", "tekstur gel", "creamy"], "tekstur nyaman yang mudah dibaurkan dan cepat meresap", "jadikan kenyamanan tekstur dan daya serap cepat sebagai poin unggulan di ulasan promosi"),
    (["melembabkan", "melembapkan", "lembab", "lembap", "hydrating", "kenyal", "plumpy", "adem", "soothing", "lembut", "halus"], "kemampuan melembabkan dan menghaluskan kulit", "pertahankan performa hidrasi formula dan komunikasikan manfaat kelembabannya secara konsisten"),
    (["mencerahkan", "cerah", "cerahan", "glowing", "putih", "memudarkan", "bersih", "fresh"], "efek mencerahkan dan membuat wajah tampak segar", "angkat bukti nyata efek mencerahkan dari ulasan konsumen sebagai testimoni produk"),
    (["kempes", "mengurangi minyak", "oil control", "angkat komedo", "angkat kotoran"], "efektivitas mengontrol minyak dan membersihkan pori", "fokuskan penargetan produk pada segmen konsumen dengan masalah sebum dan pori"),
    (["affordable", "murah", "terjangkau", "worth it", "worth", "hemat", "awet", "anak sekolah", "pelajar", "ramah di kantong"], "harga terjangkau (affordable / value-for-money)", "pertahankan daya saing harga yang ramah kantong pelajar/mahasiswa untuk menjaga loyalitas"),
    (["wanginya sih enak", "wanginya enak", "wangi enak", "harum", "kalem", "segar"], "aroma produk yang nyaman dan disukai", "jaga konsistensi karakter aroma yang lembut sebagai ciri khas produk"),
    (["travel friendly", "travel", "praktis", "higienis", "tube", "pump"], "desain kemasan yang praktis dan higienis", "pertahankan ergonomi kemasan yang mudah dibawa bepergian"),
]


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
    return " & ".join(detected[:2]) if detected else "Kulit Normal / Umum"


def _extract_matches(text_lower: str, signals: List[Tuple[List[str], str, str]], is_pos: bool = True) -> List[Tuple[str, str, str]]:
    """Returns list of (matched_keyword, finding_label, action_phrase) using word-boundary and negation checks."""
    found = []
    neg_prefixes = ("tidak ", "tak ", "gak ", "ga ", "nggak ", "ngga ", "kurang ", "belum ", "bukan ", "tanpa ", "bebas ", "anti ")
    relief_prefixes = neg_prefixes + ("hilang", "mengurangi", "ngempesin", "kempes", "memudarkan", "hempas", "bikin gak ", "bikin ga ")
    for keywords, label, action in signals:
        for kw in keywords:
            m = re.search(rf"\b{re.escape(kw)}(?:nya|ku|mu)?\b", text_lower)
            if m:
                prefix_window = text_lower[max(0, m.start() - 22):m.start()]
                if is_pos and any(p in prefix_window for p in neg_prefixes):
                    continue
                if not is_pos and any(p in prefix_window for p in relief_prefixes):
                    continue
                found.append((kw, label, action))
                break
    return found


def _salient_snippet(raw_text: str) -> str:
    """Extracts 2-3 distinctive words from the review text so every comment has a unique anchor."""
    words = [w.lower() for w in re.findall(r"[a-zA-Z]{4,}", raw_text) if w.lower() not in {
        "yang", "untuk", "dengan", "karena", "sama", "banget", "bikin", "jadi", "udah", "saya",
        "aku", "pake", "pakai", "kulit", "produk", "wardah", "emina", "safi", "tapi", "kalo", "kalau"
    }]
    unique_words = list(dict.fromkeys(words))[:3]
    return ", ".join(unique_words) if unique_words else raw_text[:24].strip()


def _build_dynamic_umkm_recommendation(
    brand: str, trust: str, raw_text: str, profile_raw: str, suitable_types: str,
    pos_matches: List[Tuple[str, str, str]], neg_matches: List[Tuple[str, str, str]],
    top_pos: List[str], top_neg: List[str]
) -> str:
    """Constructs a review-specific UMKM recommendation directly from the comment's findings and SHAP words."""
    profile_note = f"pengulas ({profile_raw})" if profile_raw and profile_raw != "nan" else f"segmen {suitable_types}"
    snippet = _salient_snippet(raw_text)
    shap_pos_str = ", ".join(top_pos[:3]) if top_pos else snippet
    shap_neg_str = ", ".join(top_neg[:3]) if top_neg else snippet

    if trust == "Low_Trust" or (neg_matches and trust != "High_Trust"):
        neg_desc = " serta ".join(f"{m[1]} ('{m[0]}')" for m in neg_matches[:2]) if neg_matches else f"keluhan pada kata '{shap_neg_str}'"
        neg_act = neg_matches[0][2] if neg_matches else f"tambahkan panduan pemakaian untuk ({suitable_types})"
        if pos_matches:
            pos_desc = " dan ".join(f"{m[1]} ('{m[0]}')" for m in pos_matches[:2])
            return (
                f"Saran UMKM ({brand}): Tindak lanjuti {neg_desc} (sorotan: '{shap_neg_str}') pada {profile_note} — "
                f"{neg_act}, sambil tetap mempertahankan apresiasi pengulas terhadap {pos_desc}."
            )
        return (
            f"Saran UMKM ({brand}): Mitigasi {neg_desc} (sorotan: '{shap_neg_str}') yang dialami {profile_note} — "
            f"{neg_act} ({suitable_types})."
        )

    if trust == "High_Trust":
        pos_desc = " serta ".join(f"{m[1]} ('{m[0]}')" for m in pos_matches[:2]) if pos_matches else f"poin positif pada kata '{shap_pos_str}'"
        pos_act = pos_matches[0][2] if pos_matches else f"tonjolkan testimoni positif ini untuk target ({suitable_types})"
        neg_note = f", sekaligus perhatikan catatan kecil terkait {neg_matches[0][1]} ('{neg_matches[0][0]}')" if neg_matches else ""
        return (
            f"Saran UMKM ({brand}): Manfaatkan ulasan positif {profile_note} mengenai {pos_desc} "
            f"(pendorong SHAP: '{shap_pos_str}') — {pos_act}{neg_note}."
        )

    obs = []
    if pos_matches:
        obs.append(f"kelebihan {pos_matches[0][1]} ('{pos_matches[0][0]}')")
    if neg_matches:
        obs.append(f"catatan {neg_matches[0][1]} ('{neg_matches[0][0]}')")
    obs_str = f"{' dengan '.join(obs)} (konteks: '{snippet}')" if obs else f"evaluasi seimbang pada kata '{snippet}'"
    act = neg_matches[0][2] if neg_matches else (pos_matches[0][2] if pos_matches else f"perjelas panduan hasil pemakaian untuk ({suitable_types})")
    return f"Saran UMKM ({brand}): Tanggapi ulasan netral {profile_note} yang menyoroti {obs_str} — {act}."


def generate_review_xai_explanation(review_data: Dict[str, Any], raw_text: str) -> Dict[str, str]:
    """Generates a 3-point XAI explanation tailored to each individual review's exact text and SHAP tokens."""
    text_lower = str(raw_text or "").lower()
    trust = str(review_data.get("label_kepercayaan", "High_Trust"))
    brand = str(review_data.get("merek_umkm", "UMKM"))
    profile_raw = str(review_data.get("kondisi_kulit_usia", "")).strip()
    skin_profile = _detect_skin_profile(profile_raw, text_lower)

    pos_matches = _extract_matches(text_lower, POS_SIGNALS, is_pos=True)
    neg_matches = _extract_matches(text_lower, NEG_SIGNALS, is_pos=False)
    has_halal = any(m[1] == "jaminan sertifikasi Halal/BPOM resmi" for m in pos_matches)
    has_breakout = any(k in text_lower for k in ["breakout", "beruntusan", "bruntusan", "iritasi", "gatal", "perih", "panas", "jerawat", "komedo"])

    cached_shap = get_cached_review_shap(raw_text)
    top_pos = list(dict.fromkeys(cached_shap.get("top_positive_words", []))) if cached_shap else []
    top_neg = list(dict.fromkeys(cached_shap.get("top_negative_words", []))) if cached_shap else []

    if cached_shap:
        if trust == "High_Trust" and top_pos:
            trust_reason = f"Tingkat Kepercayaan Tinggi (SHAP Transformer): Kata pendorong utama '{', '.join(top_pos[:3])}' memberikan atribusi Shapley positif tertinggi."
        elif trust == "Low_Trust" and top_neg:
            trust_reason = f"Tingkat Kepercayaan Rendah (SHAP Transformer): Kata pemicu keluhan '{', '.join(top_neg[:3])}' memberikan atribusi negatif signifikan."
        else:
            trust_reason = cached_shap.get("explanation_summary", f"Analisis SHAP menunjukkan atribusi berimbang pada kata '{_salient_snippet(raw_text)}'.")
    elif trust == "High_Trust":
        if has_halal:
            trust_reason = "Tingkat Kepercayaan Tinggi: Kehadiran kata kunci legalitas & sertifikasi resmi (Halal MUI / BPOM) serta kepuasan pemakaian memberikan bobot atribusi positif terbesar."
        else:
            kw = ", ".join(m[0] for m in pos_matches[:2]) or _salient_snippet(raw_text)
            trust_reason = f"Tingkat Kepercayaan Tinggi: Ulasan didominasi oleh ekspresi kepuasan pada kata '{kw}' terkait manfaat dan kenyamanan produk."
    elif trust == "Low_Trust":
        kw = ", ".join(m[0] for m in neg_matches[:2]) or _salient_snippet(raw_text)
        trust_reason = f"Tingkat Kepercayaan Rendah: Sistem mendeteksi pemicu keluhan konsumen pada kata '{kw}' yang menurunkan skor kepercayaan."
    else:
        trust_reason = f"Tingkat Kepercayaan Netral: Konsumen mengevaluasi produk dengan sentimen berimbang (kata kunci: '{_salient_snippet(raw_text)}') namun hasilnya dinilai belum optimal."

    if "Kering" in skin_profile:
        suitable_types = "Lebih Sesuai: Kulit Berminyak / Kombinasi (Perlu pelembab ekstra untuk kulit kering)" if has_breakout else "Sangat Sesuai: Kulit Normal hingga Kering"
        skin_analysis = f"Profil Pengulas: {skin_profile}. {'Formula terindikasi kurang melembabkan atau memicu iritasi.' if has_breakout else 'Formulasi hidrasi dinilai kompatibel mengunci kelembaban.'}"
    elif "Berminyak" in skin_profile or "Acne" in skin_profile:
        suitable_types = "Lebih Sesuai: Kulit Kering / Dehidrasi (Hindari untuk kulit berminyak berpori besar)" if has_breakout else "Sangat Sesuai: Kulit Berminyak & Acne-Prone"
        skin_analysis = f"Profil Pengulas: {skin_profile}. {'Produk diduga memicu penyumbatan pori/bruntusan.' if has_breakout else 'Tekstur dinilai ringan dan aman untuk kontrol sebum.'}"
    elif "Sensitif" in skin_profile:
        suitable_types = "Perhatian Khusus: Lakukan patch-test, lebih ditujukan untuk kulit normal" if has_breakout else "Sangat Sesuai: Kulit Sensitif & Kulit Halus"
        skin_analysis = f"Profil Pengulas: {skin_profile}. {'Terjadi reaksi iritasi/hipersensitivitas.' if has_breakout else 'Formula minim bahan iritan dan lembut di kulit.'}"
    else:
        suitable_types = "Sesuai: Semua Jenis Kulit (Kulit Normal & Kombinasi)"
        skin_analysis = f"Profil Pengulas: {skin_profile}. Toleransi kulit konsumen terhadap formula dinilai stabil untuk penggunaan harian."

    umkm_rec = _build_dynamic_umkm_recommendation(
        brand, trust, raw_text, profile_raw, suitable_types, pos_matches, neg_matches, top_pos, top_neg
    )

    return {
        "trust_reason": trust_reason,
        "skin_analysis": skin_analysis,
        "umkm_recommendation": umkm_rec,
        "suitable_skin_types": suitable_types,
    }
