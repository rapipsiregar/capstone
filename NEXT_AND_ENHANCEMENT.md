# Next Tasks & Enhancement Backlog

Dokumen tunggal untuk rencana (**TODO**) dan riwayat (**DONE**) proyek CHARM, Capstone Design Kosmetik Halal.

## Aturan Dokumen

- **Status:** `[ ]` TODO · `[x]` DONE · `[~]` digabung / dibatalkan (alasan ditulis).
- **Ukuran task:** satu tujuan, satu bukti. Tiap seksi berisi **tepat 3 task** (AGENTS.md shortcut `e`).
- **Eksekusi:** `n` mengerjakan task TODO teratas yang belum selesai, satu per satu, berurutan.
- **Kriteria selesai:** setiap task punya kriteria yang dapat dibuktikan (output terminal, test, atau screenshot `browser_subagent`). Tanpa bukti, task tidak ditandai DONE.
- **Prioritas temuan:** HIGH = Hard Gate anti-slop / integritas data; MEDIUM = Purpose-Gate; LOW = Quality Lock / taste WARN.
- **Penghapusan file:** hanya setelah initial commit (Task 7.1) dan dengan persetujuan per item.
- **Nomor lama** (Phase 4 dan 6) ditulis dalam kurung agar riwayat tetap terlacak.
- **Perpindahan ke DONE:** task selesai dicentang di tempat; seksi dipindah ke area DONE setelah ketiga task-nya selesai.
- **Git:** setiap task selesai di-commit dan di-push ke `origin/master`.

## Ringkasan Status (2026-10-27)

| Phase | Isi | Status |
| --- | --- | --- |
| 7 | Fondasi repo, aturan kerja, baseline | 6/6 (DONE) |
| 8 | Integritas model IndoBERT (fine-tuning sungguhan) | 12/15 (TODO 3/15) |
| 9 | Arah desain, angka jujur, aksesibilitas | TODO 0/12 |
| 10 | Pembersihan slop visual & gerbang akhir | TODO 0/9 |
| 11 | Pembersihan file duplikat & yatim | TODO 0/3 |
| Ditunda | Sisa Phase 4 (fitur lanjutan) | 10 task, 1 dibatalkan |
| 1–6 | Riwayat | DONE (dengan koreksi audit) |

## Keputusan User (2026-10-27)

1. Repo GitHub publik: `https://github.com/rapipsiregar/capstone.git` (branch `master`). `data/` dan `models/` ikut di-commit.
2. **Model hanya IndoBERT, di-fine-tune sungguhan.** Tidak ada perbandingan atau ensemble dengan model lain.
3. Struktur backlog Opsi C: seksi kecil, masing-masing 3 task.
4. Sumber aturan UI: `Leonxlnx/taste-skill` (`12af471`) dan `miqdadbadjuber/anti-slop` v3.2.23 (`5ca57fe`). CHARM diperlakukan sebagai **app screen**. Mode anti-slop **AFTER**: hanya temuan bernomor yang dikerjakan.
5. Klaim "100% Teranotasi" diganti angka terukur dari API. Teal `#0F766E` dipertahankan, peran rose `#E11D48` dievaluasi ulang (R-29).
6. Favicon dibuat ulang setelah arah desain ada dan konsepnya disetujui (R-23).
7. Kedua skill dipasang penuh ke `.agents/skills/`. Placeholder AGENTS.md §14 diubah menjadi teks tanpa emoji.
8. **Sumber Label Model (Task 8.1 / K7)**: Memilih **Opsi A (Weak Supervision / Distant Supervision)**. Dataset ulasan (8.365 baris) menggunakan label hasil aturan leksikon kata kunci dan rating konsumen dari `annotator.py`. Di skripsi (Bab 3 & Bab 4), metode ini diakui secara jujur dan terbuka sebagai *Rule-Based Weak Supervision* tanpa anotasi manual tambahan.

## Temuan Audit (2026-10-27)

### K. Integritas Model

| No | Prioritas | Temuan | Bukti |
| --- | --- | --- | --- |
| K1 | HIGH | Trainer IndoBERT tidak melatih apa pun; menulis loss/akurasi hardcoded berstatus `"trained"` | `backend/services/female_daily_indobert_trainer.py` |
| K2 | HIGH | Evaluator menulis metrik statis (0,942 / 0,9395 / 0,918 / 0,915); fungsi hitung tidak pernah dipanggil | `backend/services/female_daily_evaluator.py` |
| K3 | HIGH | Confusion matrix berjumlah 1.083, padahal `test.csv` berisi 837 baris | `models/` vs `data/annotated/test.csv` |
| K4 | HIGH | Model tersimpan dan dipakai `/predict` adalah TF-IDF + LinearSVC, bukan IndoBERT. Metrik aslinya: trust akurasi 0,7885 / F1-macro 0,7649; aspek 0,9188 / 0,7774 | `models/indobert_halal/indobert_*.joblib`, `backend/services/indobert_trainer.py` |
| K5 | HIGH | UI menampilkan metrik hardcoded dan label "IndoBERT Transformer (Fine-Tuned)" | `frontend/js/charts.js` baris 99, `frontend/index.html` baris 393, 454 |
| K6 | HIGH | Modul XAI memakai bobot linear `coef_`, bukan SHAP; akan rusak saat beralih ke IndoBERT | `xai_explainer.py`, `review_explainer.py`, `empirical_drivers.py` |
| K7 | HIGH | Label `label_kepercayaan` dan `aspek_komunikasi` dibuat aturan kata kunci + rating, bukan anotasi manusia. Melatih IndoBERT pada label ini berisiko menggelembungkan metrik | `backend/services/annotator.py` baris 51-65 |

### F. Antarmuka (baseline beranda: `lint.mjs --app` 82 FAIL / 48 WARN, `inspect.mjs --app` 4 FAIL / 4 WARN, pytest 120 passed)

| No | Prioritas | Temuan | Bukti | Aturan |
| --- | --- | --- | --- | --- |
| F1 | HIGH | Pill "100% Teranotasi Halal & BPOM" menyesatkan | `klaim_halal` 55, `klaim_bpom` 468 dari 8.365 | R-17, R-36, AGENTS §12 |
| F2 | HIGH | Angka hero hardcoded | `frontend/index.html` baris 108, 121-124 | AGENTS §13 |
| F3 | HIGH | Fakta sama, nilai beda: 216/801 vs 215/797 | `frontend/index.html` baris 439 | C-5 |
| F4 | HIGH | 23 tombol kategori tanpa indikator fokus | `frontend/css/catalog.css` baris 109 | R-32 |
| F5 | HIGH | Teks `#94A3B8` kontras 2,56:1 (9 pemakaian) | `contrast-check.py` | R-25 |
| F6 | HIGH | Header terpotong di 390px | Screenshot inspector | R-03 |
| F7 | HIGH | Belum ada `DESIGN.md` | File tidak ada | R-37, R-31 |
| F8 | MEDIUM | 75 emoji sebagai UI | `lint.mjs` | R-04 |
| F9 | MEDIUM | Eyebrow pill uppercase di atas headline | Inspector `micro-label` | R-09 |
| F10 | MEDIUM | Gradient hero + 4 gradient lain | Inspector + lint | R-01 |
| F11 | MEDIUM | Shadow berat di 30 lokasi + 1 backdrop blur | Inspector `heavy-shadow` | R-12, R-10 |
| F12 | MEDIUM | Warna chart violet/indigo + default Tailwind | `charts.js`, `catalog-summary.js` | R-01, R-29 |
| F13 | MEDIUM | Favicon bergradient, glow, ikon bintang | `frontend/favicon.svg` | R-04, R-23 |
| F14 | LOW | 3 typeface (Inter, Arial fallback 19%, Outfit) | Inspector `font-count` | R-06 |
| F15 | LOW | Headline 3 baris di 390px | Inspector `headline-lines` | taste |
| F16 | LOW | Angka rata kiri (50/50 sel) | Inspector `numeric-align` | taste app §7.4 |
| F17 | LOW | 13 `transition: all` | `lint.mjs` | taste motion |
| F18 | LOW | State empty/loading/error tanpa penyebab & langkah lanjut | Audit kode | R-27 |
| F19 | HIGH | Teks "Foto belum tersedia" kontras rendah 2.5:1 (#94A3B8 on #F8FAFC) | `inspect.mjs` Level 2 | R-25 |
| F20 | MEDIUM | Border panel terlalu tegas/gelap (#0F766E pada putih, 5.47:1) di Level 3 | `inspect.mjs` Level 3 (`heavy-borders`) | taste app §5 |
| F21 | MEDIUM | Tombol aksi dengan shadow/glow di Guidebook Insight, Sandbox, Metrik | `inspect.mjs` (`button-fx`) | R-12, taste button |
| F22 | LOW | Kartu pendorong reputasi beda tinggi 139px (ragged-row) di Guidebook 1 | `inspect.mjs` Guidebook 1 | taste layout |
| F23 | LOW | Area kosong 40% (hero-void) pada Sandbox sebelum simulasi | `inspect.mjs` Guidebook 2 | taste layout |
| F24 | LOW | Angka pada tabel metrik belum memakai `font-variant-numeric: tabular-nums` | `inspect.mjs` Guidebook 3 (`tabular` 0%) | taste app §7.4 |
| F25 | LOW | Teks tepi (<16px dari margin kiri) di breakpoint 768px dan 390px | `inspect.mjs` Level 2, 3, Guidebooks | antislop-layoutmobile |

> Baseline seluruh 6 layar lengkap diukur pada Task 7.5 (Level 1: 4F/4W, Level 2: 3F/3W, Level 3: 3F/4W, GB1: 3F/4W, GB2: 2F/4W, GB3: 3F/4W). Temuan baru tercatat pada F19–F25.

---

## TODO

### Phase 8: Integritas Model IndoBERT (K1–K7)

#### 8E. Pembersihan Model Palsu
- [ ] **Task 8.13**: **Hapus Trainer & Evaluator Palsu** (K1, K2): `female_daily_indobert_trainer.py`, `female_daily_evaluator.py`, `model_evaluator.py` beserta test-nya.
  - *Kriteria selesai:* persetujuan per file; pytest tetap hijau.
- [ ] **Task 8.14**: **Hapus Artefak TF-IDF** (K4): `indobert_*.joblib`, jalur TF-IDF di `indobert_trainer.py`, `model_metadata.json` palsu.
  - *Kriteria selesai:* persetujuan per file; `grep` tidak menemukan `TfidfVectorizer` di `backend/`.
- [ ] **Task 8.15**: **Koreksi Dokumen**: `docs/feature-list.md` dan dokumen lain disesuaikan dengan model yang benar-benar ada.
  - *Kriteria selesai:* `grep` angka 0,942 / 94,20% tidak ditemukan di repo.

### Phase 9: Arah Desain, Angka Jujur & Aksesibilitas

#### 9A. Arah Desain (ex Task 6.4)
- [ ] **Task 9.1**: **Pilih Gaya**: `draw.mjs --app --keep palette`, ajukan 3 opsi ke user.
  - *Kriteria selesai:* pilihan user tercatat.
- [ ] **Task 9.2**: **Tulis `DESIGN.md`** (F7): Gaya, typeface, peran warna, dial ENERGY/RHYTHM/MOTION, alasan per keputusan.
  - *Kriteria selesai:* setiap keputusan punya alasan tertulis (R-31); user menyetujui.
- [ ] **Task 9.3**: **Favicon Baru** (F13): Ajukan konsep, buat setelah disetujui.
  - *Kriteria selesai:* tanpa gradient/glow; disetujui user; tampil di tab browser (screenshot).

#### 9B. Angka Jujur di Beranda
- [ ] **Task 9.4**: **Statistik Hero dari API** (F2).
  - *Kriteria selesai:* test (TDD) membuktikan angka DOM = hasil hitung dataset; tidak ada angka statistik literal di `index.html`.
- [ ] **Task 9.5**: **Ganti Pill 100%** (F1): Tampilkan jumlah ulasan yang menyebut klaim halal dan BPOM.
  - *Kriteria selesai:* angka pill = hitungan dataset (test).
- [ ] **Task 9.6**: **Satu Fakta Satu Nilai** (F3): Tab Metrik memakai sumber yang sama dengan beranda.
  - *Kriteria selesai:* tidak ada dua nilai berbeda untuk fakta yang sama (dicek berdasarkan peta Task 7.6).

#### 9C. Insight Reputasi Dinamis (ex Task 6.3)
- [ ] **Task 9.7**: **Dropdown dari API**: Brand (216) dan kategori (23).
  - *Kriteria selesai:* test membuktikan jumlah opsi = jumlah di dataset.
- [ ] **Task 9.8**: **Kata Pendorong dari API**: Memakai hasil Task 8.11.
  - *Kriteria selesai:* tidak ada array kata statis di `frontend/js/`.
- [ ] **Task 9.9**: **Rasio Compliance dari Dataset**: Halal dan BPOM dihitung backend.
  - *Kriteria selesai:* test membuktikan rasio = hitungan dataset.

#### 9D. Aksesibilitas Dasar
- [ ] **Task 9.10**: **Indikator Fokus** (F4).
  - *Kriteria selesai:* navigasi Tab menjangkau 23 kategori dengan fokus terlihat (screenshot).
- [ ] **Task 9.11**: **Kontras Teks** (F5).
  - *Kriteria selesai:* `contrast-check.py` PASS untuk semua pasangan warna teks.
- [ ] **Task 9.12**: **Header Mobile** (F6).
  - *Kriteria selesai:* screenshot 390px tanpa teks terpotong.

### Phase 10: Pembersihan Slop Visual & Gerbang Akhir

#### 10A. Emoji & Hero
- [ ] **Task 10.1**: **Emoji Keluar dari UI** (F8): Diganti kata, atau ikon dengan alasan tertulis di `DESIGN.md`.
  - *Kriteria selesai:* `lint.mjs --app` 0 FAIL `emoji`.
- [ ] **Task 10.2**: **Eyebrow & Gradient** (F9, F10).
  - *Kriteria selesai:* lint 0 FAIL `gradient`; inspector 0 `micro-label`.
- [ ] **Task 10.3**: **Shadow & Blur** (F11): Shadow hanya pada overlay (menu, dialog, tooltip).
  - *Kriteria selesai:* WARN `shadow` tersisa hanya pada overlay; 0 `backdrop-filter`.

#### 10B. Chart, Tipografi & Gerak
- [ ] **Task 10.4**: **Warna Chart** (F12): Satu hue data per chart dari `DESIGN.md`.
  - *Kriteria selesai:* lint 0 FAIL `purple`, 0 WARN `framework-colour`.
- [ ] **Task 10.5**: **Tipografi** (F14, F15): Maks 2 typeface, ≤ 5 ukuran, headline ≤ 2 baris.
  - *Kriteria selesai:* inspector 0 WARN `font-count` dan `headline-lines`.
- [ ] **Task 10.6**: **Angka & Transisi** (F16, F17): Angka rata kanan dengan tabular figures; `transition: all` diganti properti spesifik.
  - *Kriteria selesai:* inspector 0 WARN `numeric-align`; lint 0 WARN `transition-all`.

#### 10C. State & Gerbang Akhir
- [ ] **Task 10.7**: **State Lengkap** (F18): Empty, loading, error di katalog 3 level dan 3 guidebook menyebut penyebab dan langkah lanjut.
  - *Kriteria selesai:* tiap state diperagakan via `browser_subagent` dengan screenshot.
- [ ] **Task 10.8**: **Gerbang Otomatis**: `lint` + `inspect --app` di 1440/768/390 untuk semua layar.
  - *Kriteria selesai:* 0 FAIL di semua layar.
- [ ] **Task 10.9**: **Delivery Gate & Laporan**: Delivery Gate anti-slop dengan bukti per butir, click-through semua kontrol, laporan before/after.
  - *Kriteria selesai:* Delivery Gate tanpa FAIL; laporan di `docs/log/`.

### Phase 11: Pembersihan File

#### 11A. Duplikat & Yatim (persetujuan per item)
- [ ] **Task 11.1**: **Splitter Ganda**: `splitter.py` vs `female_daily_splitter.py` (aplikasi memakai yang kedua).
  - *Kriteria selesai:* satu splitter tersisa; pytest hijau.
- [ ] **Task 11.2**: **Modul Yatim**: `female_daily_xai.py` dan `frontend/js/empirical_drivers.json` tidak dirujuk aplikasi.
  - *Kriteria selesai:* `grep` membuktikan tidak ada rujukan sebelum dihapus; pytest hijau.
- [ ] **Task 11.3**: **Sisa Data Statis**: Bagian `frontend/js/data.js` yang tidak terpakai lagi setelah Phase 9C.
  - *Kriteria selesai:* UI tetap berfungsi (screenshot); tidak ada data benchmark statis tersisa.

### Backlog Ditunda (sisa Phase 4)

Dipecah ulang menjadi task kecil saat diaktifkan.

- [ ] (P4 Task 1.2) Active Learning Uncertainty Sampling Selector.
- [ ] (P4 Task 1.3) Kaggle Dataset Batch Ingestion & Sync API.
- [~] (P4 Task 2.1) IndoBERT & RoBERTa Ensemble: **dibatalkan**, bertentangan dengan keputusan model hanya IndoBERT.
- [ ] (P4 Task 2.2) Brand Aspect Sentiment Drift Detector.
- [ ] (P4 Task 2.3) Counterfactual XAI Generator (bergantung pada Phase 8).
- [ ] (P4 Task 3.1) Brand Reputation Benchmark API.
- [ ] (P4 Task 3.2) Model Health & Latency Endpoint.
- [ ] (P4 Task 3.3) Executive Summary PDF Exporter.
- [ ] (P4 Task 4.1) Brand Reputation Radar Chart.
- [ ] (P4 Task 4.2) Model Health Monitoring Panel.
- [ ] (P4 Task 4.3) Interactive Counterfactual Simulator.

---

## DONE

Urutan terbaru di atas. Catatan **Koreksi audit 2026-10-27** menandai klaim yang tidak sesuai kode; perbaikannya ada di task yang dirujuk.

### Phase 8: Integritas Model IndoBERT (K1–K7)
#### 8D. XAI Turunan & Tampilan Metrik
- [x] **Task 8.12**: **Metrik UI dari API** (K5): Grafik dan label model membaca JSON evaluasi lewat API.
  - *Kriteria selesai:* tidak ada angka metrik literal di `frontend/`; screenshot menunjukkan angka = JSON.
  - *Bukti (2026-10-28):* Endpoint `GET /api/v1/model/metrics` pada `backend/api/v1/model_metrics.py` (38 LOC) menyajikan hasil evaluasi otentik pada 837 sampel `test.csv`; `frontend/js/charts.js` (160 LOC) mem-fetch metrik dari API secara dinamis; seluruh angka metrik literal lama (0.9420, 0.9395, dll.) telah dihapus dari `frontend/` (0 temuan); verifikasi visual browser sukses tercatat di `thesis_metrics_indobert_1793129041219.png`; `tests/test_api_model_metrics.py` 1 passed, 147 pytest passed.
- [x] **Task 8.11**: **Kata Pendorong dari SHAP** (K6): `empirical_drivers.py` mengagregasi cache SHAP.
  - *Kriteria selesai:* test membuktikan kata pendorong = agregasi cache.
  - *Bukti (2026-10-28):* Modul `backend/services/empirical_drivers.py` (146 LOC) mengagregasi token-level attribution dari cache persistent SHAP IndoBERT; nol dependensi `joblib` dan `coef_` (teruji via `test_no_coef_or_joblib_in_empirical_drivers`); ranking kata pendorong High Trust & pemicu Low Trust terintegrasi ke REST API `GET /api/v1/analytics/brands`; seluruh 146 pytest passed.
- [x] **Task 8.10**: **Cache SHAP per Ulasan** (K6): Hitung SHAP offline untuk ulasan katalog, API katalog membaca cache.
  - *Kriteria selesai:* `review_explainer.py` tidak memakai `coef_`; test membaca cache.
  - *Bukti (2026-10-28):* Modul `backend/services/catalog_shap_cacher.py` (112 LOC) mengelola cache persistent `data/cache/review_shap_cache.json` dengan hash MD5 deterministik; `backend/services/review_explainer.py` (124 LOC) membaca cache SHAP tanpa `coef_` (teruji via test inspeksi AST/source code `test_review_explainer_does_not_use_coef`); endpoint katalog `backend/api/v1/catalog.py` (251 LOC) mengintegrasikan sorotan kata berbasis SHAP otentik; seluruh 142 pytest passed.

#### 8C. Integrasi Backend
- [x] **Task 8.9**: **SHAP Sungguhan di `/explain`** (K6): Pakai pustaka `shap` pada model IndoBERT, dengan cache.
  - *Kriteria selesai:* test membuktikan atribusi berasal dari `shap`; waktu respons tercatat.
  - *Bukti (2026-10-28):* Modul `backend/services/indobert_explainer.py` (165 LOC) mengimplementasikan `shap.Explainer` otentik dengan `shap.maskers.Text(tokenizer)` dan forward-pass probabilitas GPU IndoBERT; mengembalikan Shapley values nyata per token, base value, dan narasi penjelasan bahasa Indonesia; in-memory caching mempercepat respons ulasan berulang (< 200 ms); endpoint `backend/api/v1/explain.py` (58 LOC) diperbarui; `tests/test_indobert_explainer.py` dan `tests/test_api_explain.py` 4 passed (100%).
- [x] **Task 8.8**: **`/predict` Memakai IndoBERT** (K4).
  - *Kriteria selesai:* test API membuktikan prediksi berasal dari model IndoBERT; waktu respons tercatat.
  - *Bukti (2026-10-28):* Modul `backend/services/indobert_predictor.py` (84 LOC) mengintegrasikan model fine-tuned IndoBERT Kepercayaan (3 kelas) dan Aspek (4 kelas) via `model_loader.py` dengan forward-pass GPU/device; endpoint `backend/api/v1/predict.py` menyajikan inferensi otentik dengan pencatatan latensi riil `execution_time_ms` (~15-40 ms); `tests/test_api_predict.py` 3 passed (100%).
- [x] **Task 8.7**: **Pemuat Model**: Lokasi bobot dibaca dari `.env` (folder lokal atau Hugging Face Hub), dimuat sekali saat dibutuhkan.
  - *Kriteria selesai:* test memuat model dari path konfigurasi; pesan error jelas bila bobot tidak ada.
  - *Bukti (2026-10-28):* Layanan `backend/services/model_loader.py` mengimplementasikan lazy singleton caching untuk model & tokenizer IndoBERT Kepercayaan dan Aspek; konfigurasi path dibaca dari `.env` (`INDOBERT_TRUST_MODEL_PATH`, `INDOBERT_ASPECT_MODEL_PATH`); test `tests/test_model_loader.py` (6 passed) membuktikan pemuatan sukses dari path konfigurasi, singleton caching identik, dan error `FileNotFoundError` deskriptif saat bobot tidak ditemukan; 136 pytest passed.

#### 8B. Fine-Tuning & Evaluasi
- [x] **Task 8.6**: **Evaluator Jujur** (K2, K3): Metrik dihitung dari prediksi model pada `test.csv` dan ditulis ke JSON.
  - *Kriteria selesai:* test membuktikan jumlah confusion matrix = jumlah baris `test.csv`; tidak ada angka metrik literal di kode.
  - *Bukti (2026-10-28):* Evaluator otentik `backend/services/indobert_evaluator.py` mengevaluasi model IndoBERT Kepercayaan (Akurasi 83,87%, Macro F1 0,8218) dan Aspek (Akurasi 96,65%, Macro F1 0,8625) pada 837 data uji `test.csv`; total elemen confusion matrix Kepercayaan (231+204+402 = 837) dan Aspek (26+169+488+154 = 837) persis 837 baris; nol konstanta literal di kode teruji via `test_no_hardcoded_fake_metrics_in_evaluator`; seluruh 130 pytest passed.
- [x] **Task 8.5**: **Fine-Tune Klasifier Aspek**: Sama seperti 8.4 untuk `aspek_komunikasi`.
  - *Kriteria selesai:* log training asli tersimpan; bobot model tersimpan di luar git.
  - *Bukti (2026-10-28):* Fine-tuning otentik 3 epoch untuk 4 kelas `aspek_komunikasi` sukses di GPU RTX 3050 Laptop (PyTorch FP16 AMP, AdamW lr=2e-5, batch 32, durasi 236.43s); riwayat training otentik: Epoch 1 (Train 0.5663 / Val 0.2017 / Acc 0.9474 / F1 0.8298), Epoch 2 (Train 0.1450 / Val 0.1518 / Acc 0.9641 / F1 0.8455), Epoch 3 (Train 0.1121 / Val 0.1398 / Acc 0.9677 / F1 0.8708); bobot biner `model.safetensors` (498 MB) diabaikan git melalui `.gitignore`, log asli `train_aspect_indobert.log` & `training_history.json` tersimpan; 128 pytest passed.
- [x] **Task 8.4**: **Fine-Tune Klasifier Kepercayaan**: Fine-tune `indobenchmark/indobert-base-p1` untuk `label_kepercayaan` dengan loss per epoch dari training sungguhan.
  - *Kriteria selesai:* log training asli tersimpan; bobot model tersimpan di luar git.
  - *Bukti (2026-10-28):* Fine-tuning otentik 3 epoch terlaksana di GPU RTX 3050 Laptop (PyTorch FP16 AMP, AdamW lr=2e-5, batch 32, total durasi 244.1s); loss per epoch: Epoch 1 (Train 0.7243 / Val 0.4687 / Acc 0.8242 / F1 0.7920), Epoch 2 (Train 0.3547 / Val 0.4516 / Acc 0.8218 / F1 0.8027), Epoch 3 (Train 0.2408 / Val 0.4795 / Acc 0.8313 / F1 0.8107); bobot biner `model.safetensors` (498 MB) diabaikan git, riwayat json & log asli tersimpan; 125 pytest passed.

#### 8A. Data & Lingkungan
- [x] **Task 8.3**: **Lingkungan Training**: Pilih Colab GPU atau torch CUDA lokal (RTX 3050 6 GB; torch terpasang saat ini versi CPU).
  - *Kriteria selesai:* output `torch.cuda.is_available()` = `True` di lingkungan terpilih.
  - *Bukti (2026-10-28):* PyTorch 2.6.0+cu124 terpasang di `.venv` lokal (Python 3.12); `torch.cuda.is_available()` = `True`; GPU: `NVIDIA GeForce RTX 3050 6GB Laptop GPU` (VRAM 6.0 GB); matmul tensor GPU teruji sukses; seluruh 122 pytest passed.
- [x] **Task 8.2**: **Split Deterministik**: Split ulang dengan seed tetap, catat jumlah baris dan SHA256 tiap berkas split.
  - *Kriteria selesai:* test membuktikan split dapat direproduksi (hash sama pada dua kali jalan).
  - *Bukti (2026-10-27):* Partisi 80/10/10 deterministik (seed 42) diverifikasi: `train.csv` 6.692 baris (`d1a1c0ea90b7b6a728883801da13f3a8fb9b35240691e4883987a331674d2ed7`), `val.csv` 836 baris (`17708160c5aa1fb93f6fed6139d774caf3edbe5f5fde410201c30411cfa524f5`), `test.csv` 837 baris (`f11b0b811f597ba4dfa8ed6efe8b698159a4cd18fca31855910f4d81b65277c9`); test `test_split_deterministic_reproducibility` dan `test_repository_split_files_integrity` membuktikan hash SHA256 100% identik pada pengulangan.
- [x] **Task 8.1**: **Keputusan Sumber Label** (K7): Ajukan opsi ke user (mis. anotasi manual subset sebagai gold test set + Cohen's kappa, atau label lemah yang dinyatakan terbuka di skripsi) beserta dampaknya.
  - *Kriteria selesai:* keputusan user tercatat di bagian Keputusan User.
  - *Bukti (2026-10-27):* Keputusan tercatat di Keputusan User poin 8; user memilih Opsi A (Weak Supervision / Distant Supervision) berbasis leksikon kata kunci + rating `annotator.py` yang dinyatakan terbuka di skripsi tanpa anotasi manual tambahan.

### Phase 7: Fondasi Repo & Aturan Kerja
#### 7B. Skill & Baseline
- [x] **Task 7.6**: **Peta Sumber Angka**: Telusuri setiap angka statistik yang tampil di UI ke asalnya (hardcoded, API, atau berkas), termasuk asal selisih 215/797 dan klaim 10.826 ulasan.
  - *Kriteria selesai:* tabel angka → sumber → nilai benar di `docs/log/`; tidak ada perubahan kode.
  - *Bukti (2026-10-27):* Peta angka selesai di `docs/log/2026-10-27-2127-n.md`: 215/797 terbukti asal dari `00. InfoProduct.csv`, 10.826 terbukti korpus pra-deduplikasi; split 80/10/10 = 6.692/836/837 cocok dengan dataset aktif 8.365; tanpa perubahan kode.
- [x] **Task 7.5**: **Baseline Semua Layar**: `inspect.mjs --app` untuk Level 2, Level 3, dan 3 guidebook di 1440/768/390.
  - *Kriteria selesai:* angka FAIL/WARN per layar tercatat di `docs/log/`; temuan baru masuk tabel F.
  - *Bukti (2026-10-27):* 6 layar terukur via CDP Chrome di 1440/768/390: Level 1 (4F/4W), Level 2 (3F/3W), Level 3 (3F/4W), GB1 Insight (3F/4W), GB2 Sandbox (2F/4W), GB3 Metrik (3F/4W); temuan F19-F25 masuk tabel; pytest 120 passed.
- [x] **Task 7.4**: **Pasang Skill UI**: Salin `taste-skill` dan 6 skill anti-slop ke `.agents/skills/`, tambah `.taste-skill/` ke `.gitignore`.
  - *Kriteria selesai:* `lint.mjs` dan `inspect.mjs` berjalan dari `.agents/skills/`; `git status` tidak memuat `.taste-skill/`.
  - *Bukti (2026-10-27):* 7 skill terpasang di `.agents/skills/` (`taste-skill`, `antislop*`); `.taste-skill/` masuk `.gitignore` & tidak terlacak git; `lint.mjs` jalan (82 FAIL, 48 WARN); `inspect.mjs` jalan di localhost:3000 (4 FAIL, 4 WARN); pytest 120 passed.

#### 7A. Git & Aturan
- [x] **Task 7.3**: **Perbaiki SKILLS.md**: Hapus rujukan ke `plans/next-enhancements.md` dan switch Demo/Live, Cloud/Local yang tidak ada; rujukan section AGENTS.md disesuaikan.
  - *Kriteria selesai:* setiap path dan section yang dirujuk SKILLS.md benar-benar ada (dicek dengan `grep`).
  - *Bukti (2026-10-27):* SKILLS.md diselaraskan: rujukan NEXT_AND_ENHANCEMENT.md & AGENTS.md terverifikasi valid (`True`), 5 peran (Architect, Backend, Frontend, QA, Hardware) bebas rujukan fiktif, LOC 87 baris; pytest 120 passed.
- [x] **Task 7.2**: **Selaraskan AGENTS.md**: Urutan prioritas aturan (AGENTS.md > DESIGN.md > anti-slop > taste-skill), definisi selesai UI (lint + inspect + Delivery Gate), arti "red" TDD untuk task visual (lint/inspector FAIL), stack ditulis vanilla JS (bukan React/Vite), placeholder §14 jadi teks.
  - *Kriteria selesai:* diff AGENTS.md ditinjau user; tidak ada pernyataan yang bertentangan dengan kode.
  - *Bukti (2026-10-27):* AGENTS.md diselaraskan: stack Vanilla JS/SQLite, IndoBERT murni, SHAP empiris, layout pohon direktori riil, rules prioritas §15, kriteria selesai UI 4 lapis, Red visual TDD, placeholder foto teks polos; pytest 120 passed.
- [x] **Task 7.1**: **Initial Commit & Push**: Tetapkan isi commit pertama (`data/` 30 MB dan `models/` 3,1 MB ikut atau tidak), pastikan `.gitignore` menolak bobot model besar, lalu commit dan push ke `origin/master` setelah user konfirmasi.
  - *Kriteria selesai:* `git log` menunjukkan 1 commit; `git status` bersih; tidak ada file > 100 MB; push berhasil.
  - *Bukti (2026-10-27):* commit `9ff9a8d` (177 file); `git ls-remote` = `9ff9a8d…`; file terbesar 5,9 MB; `.env` tidak ikut; pindai rahasia bersih; pytest 120 passed.

### Phase 6: Homepage Cleanup & Insight Reputasi
- [x] **Task 6.5**: **Parameter Kepercayaan per Produk**: 3 KPI dan 2 grafik bulat di Level 3, dihitung backend dari seluruh ulasan produk (`backend/services/product_summary.py`, `frontend/js/catalog-summary.js`).
- [x] **Task 6.2**: **Integritas Data Katalog Beranda**: Badge klaim sesuai flag dataset, badge Neutral terpisah, kotak XAI memakai `umkm_recommendation` asli (`frontend/js/catalog.js`, `tests/test_homepage_layout.py`).
- [x] **Task 6.1**: **Homepage Cleanup & Guidebook Insight Reputasi**: Feed lama dihapus, KPI dan grafik dipindah ke panel guidebook (`frontend/index.html`, `frontend/js/app.js`).
- [~] Task 6.3 dipindah ke Phase 9C. Task 6.4 digabung ke Phase 9A.

### Phase 5: Katalog Drill-Down 3 Level
- [x] **Task 5.4**: **Level 3 Ulasan & XAI**: Hero produk, ulasan riil, kotak XAI 2 baris (`frontend/js/catalog.js`, `tests/test_catalog_ui.py`).
- [x] **Task 5.3**: **Level 2 Grid Produk & Breadcrumb** (`frontend/js/catalog.js`).
- [x] **Task 5.2**: **Level 1 Grid 23 Kategori** dari API (`frontend/js/catalog.js`).
- [x] **Task 5.1**: **API Katalog**: `/catalog/categories`, `/catalog/products`, `/catalog/reviews` (`backend/api/v1/catalog.py`).

### Phase 4: Data Ingestion (sebagian)
- [x] **Task 1.1**: **Deduplikasi & Pemulihan Teks Ulasan**: Pemulihan "... Read more" dengan rate limit 2 detik dan checkpoint (`backend/services/review_refiner.py`).

### Phase 3: UI/UX Overhaul
- [x] **Task 1.4**: **Sidebar Brand Trust & Compliance** (`tests/test_fd_sidebar_ui.py`). Sudah digantikan panel guidebook di Task 6.1.
- [x] **Task 1.3**: **Kartu Ulasan dengan Sorotan Kata** (`tests/test_fd_review_cards_ui.py`). *Koreksi audit:* sorotan memakai bobot linear, bukan SHAP (K6 → Task 8.10).
- [x] **Task 1.2**: **Header Sticky & Pencarian** (`tests/test_fd_header_ui.py`).
- [x] **Task 1.1**: **Design System Teal** (`frontend/css/styles.css`). Ditinjau ulang di Phase 9A.

### Phase 2: Integrasi Dataset Female Daily
- [x] **Task 4.3**: **Kartu Kata Pendorong per Brand** (`tests/test_xai_insight_ui.py`). *Koreksi audit:* dihitung dari bobot linear (K6 → Task 8.11).
- [x] **Task 4.2**: **Widget Pencarian Ulasan** (`tests/test_review_browser_ui.py`). *Koreksi audit:* angka "10.826 ulasan" belum diverifikasi (→ Task 7.6).
- [x] **Task 4.1**: **Filter Brand & Kategori** (`tests/test_brand_filter_ui.py`).
- [x] **Task 3.3**: **Endpoint Export Ringkasan** (`backend/api/v1/export_summary.py`).
- [x] **Task 3.2**: **Endpoint Ingest Dataset** (`backend/api/v1/dataset_ingest.py`).
- [x] **Task 3.1**: **Endpoint Analitik Brand** (`backend/api/v1/brand_analytics.py`).
- [x] **Task 2.3**: **Modul XAI Female Daily** (`backend/services/female_daily_xai.py`). *Koreksi audit:* modul tidak dipakai aplikasi (→ Task 11.2).
- [x] **Task 2.2**: **Evaluator Model** (`backend/services/female_daily_evaluator.py`). *Koreksi audit:* metrik 94,20% / 93,95% / 91,80% statis, bukan hasil hitung (K2, K3 → Task 8.6).
- [x] **Task 2.1**: **Trainer IndoBERT** (`backend/services/female_daily_indobert_trainer.py`). *Koreksi audit:* tidak ada training; metadata ditulis hardcoded (K1 → Task 8.4, 8.5).
- [x] **Task 1.3**: **Split Terstratifikasi** 6.692 / 836 / 837 (`backend/services/female_daily_splitter.py`).
- [x] **Task 1.2**: **Anotator Aspek & Kepercayaan** (`backend/services/brand_annotator.py`). *Catatan audit:* label berbasis aturan kata kunci + rating (K7 → Task 8.1).
- [x] **Task 1.1**: **Ingesti & Validasi Dataset** (`backend/services/ingest_female_daily.py`). *Koreksi audit:* angka 797 produk / 22 kategori / 215 brand berbeda dari dataset saat ini 801 / 23 / 216 (F3 → Task 7.6).

### Phase 1: Core System & Baseline
- [x] **Task 4.3**: **Responsif 1536 / 768 / 375 & ARIA** (`tests/test_frontend_responsiveness.py`).
- [x] **Task 4.2**: **XAI Sandbox** (`tests/test_frontend_xai_sandbox.py`). *Koreksi audit:* badge "IndoBERT Transformer" tidak sesuai model yang dipakai (K4, K5 → Task 8.8, 8.12).
- [x] **Task 4.1**: **Dashboard Chart.js** (`frontend/js/`). *Koreksi audit:* grafik evaluasi IndoBERT memakai angka hardcoded (K5 → Task 8.12).
- [x] **Task 3.4**: **SQLite Riwayat Inferensi** (`backend/services/database.py`, `backend/api/v1/history.py`).
- [x] **Task 3.3**: **Endpoint `/explain`** (`backend/api/v1/explain.py`). *Koreksi audit:* atribusi dari bobot linear, bukan SHAP (K6 → Task 8.9).
- [x] **Task 3.2**: **Endpoint `/predict`** (`backend/api/v1/predict.py`). *Koreksi audit:* memakai TF-IDF + LinearSVC, bukan `indobert-base-p1` (K4 → Task 8.8).
- [x] **Task 3.1**: **Inisialisasi FastAPI, CORS, Router, Health** (`backend/main.py`).
- [x] **Task 2.4**: **Integrasi SHAP** (`backend/services/xai_explainer.py`). *Koreksi audit:* modul tidak mengimpor `shap` (K6 → Task 8.9).
- [x] **Task 2.3**: **Evaluasi Model** (`backend/services/model_evaluator.py`). *Koreksi audit:* tergantikan evaluator jujur (→ Task 8.6, 8.13).
- [x] **Task 2.2**: **Pipeline Fine-Tuning & Notebook Colab** (`indobert_trainer.py`, `docs/notebooks/IndoBERT_Halal_Cosmetics_Finetuning.ipynb`). *Koreksi audit:* trainer melatih TF-IDF + LinearSVC; notebook belum pernah dijalankan untuk menghasilkan model yang dipakai (K4 → Task 8.4).
- [x] **Task 2.1**: **Arsitektur Klasifikasi Ganda** (`backend/services/indobert_trainer.py`). *Koreksi audit:* lihat Task 2.2.
- [x] **Task 1.4**: **Split Dataset** (`backend/services/splitter.py`). Duplikat dengan splitter Phase 2 (→ Task 11.1).
- [x] **Task 1.3**: **Engine Anotasi** (`backend/services/annotator.py`). *Catatan audit:* label berbasis aturan (K7 → Task 8.1).
- [x] **Task 1.2**: **Pembersihan Teks Bahasa Indonesia** (`backend/services/preprocessor.py`).
- [x] **Task 1.1**: **Ingesti Ulasan Female Daily Kaggle** (`data/raw/`).
- [x] Brainstorming awal & kesepakatan arsitektur.
- [x] Dokumen Implementation Plan (`Rencana_Implementasi_Capstone_Kosmetik_Halal.pdf`).
- [x] Aturan [`AGENTS.md`](AGENTS.md), prosedur [`SKILL.md`](.agents/skills/halal-cosmetics-capstone/SKILL.md), dan backlog ini.
- [x] Shortcut `n` (next task) dan `e` (enhancement) di `AGENTS.md`.
