# Guidelines & Project Rules: Capstone Design Kosmetik Halal


Dokumen ini berisi pedoman utama, standar pengkodean, dan aturan yang WAJIB dipatuhi oleh AI Agent dan pengembang selama mengerjakan proyek skripsi/capstone ini.

---

## 1. Identitas & Standar Proyek
* **Judul Proyek**: Pengembangan Aplikasi NLP dan Explainable AI untuk Analisis Kepercayaan Publik terhadap Komunikasi UMKM Kosmetik Halal
* **Target Utama**: Aplikasi Web Dashboard Interaktif, Model Fine-Tuned IndoBERT, dan Visualisasi Explainable AI (SHAP/LIME).
* **Bahasa Pemrograman Utama**: Python 3.10+, JavaScript / HTML5 / CSS3.
* **Framework & Library Utama**:
  * **NLP / ML**: `PyTorch`, `Hugging Face Transformers`, `scikit-learn`, `pandas`, `numpy`, `shap`.
  * **Backend**: `FastAPI`, `Uvicorn`, `Pydantic`, `SQLite` / `PostgreSQL`.
  * **Frontend**: `Vite` + `React` (atau Vanilla JS/HTML5 + `Chart.js`).

---

## 2. Aturan Pengkodean (Coding Standards)
1. **Kebersihan Kode (Clean Code)**:
   * Gunakan type hinting pada Python (misal: `def predict_sentiment(text: str) -> dict:`).
   * Sertakan docstring pada setiap fungsi backend dan model.
   * Hindari hardcode API key, kredensial, atau path lokal absolut. Gunakan file `.env`.
2. **Penanganan Bahasa & Teks (NLP Standard)**:
   * Semua data ulasan harus melalui tahap cleaning standar (lowercase, hapus URL/emoji/mention, normalisasi kata slang Bahasa Indonesia).
   * Tanda kehalalan & klaim BPOM harus diperlakukan sebagai entitas kata kunci penting (jangan terhapus pada tahap stopword removal).
3. **Standar Explainable AI (XAI)**:
   * Modul XAI utama menggunakan **SHAP (SHapley Additive exPlanations)** berbasis matematika *Game Theory* untuk mengukur bobot kontribusi tiap kata terhadap prediksi model IndoBERT.
   * Modul XAI wajib mengembalikan bobot atribusi dalam format JSON yang dikonsumsi langsung oleh frontend untuk kalkulasi highlight warna (sorotan **Hijau** untuk kontribusi *High Trust*, **Merah/Kuning** untuk kontribusi *Low Trust*).


---

## 3. Struktur Proyek (Directory Layout)
```text
c:\z_Siregar\4. CD\Kosmetik Halal\
├── .agents/                        <-- Folder Konfigurasi Custom Agent & Rules
│   └── skills/
│       └── halal-cosmetics-capstone/
│           └── SKILL.md            <-- Runbook & Kode Prosedur NLP/XAI
├── AGENTS.md                       <-- Aturan Main, Shortcut & Standards
├── SKILLS.md                       <-- 5 Peran Eksekusi (Architect, Backend, Frontend, QA, Hardware)
├── NEXT_AND_ENHANCEMENT.md         <-- Roadmap TODO & DONE Checklist
├── Rencana_Implementasi_Capstone.pdf <-- Berkas PDF Implementasi (Siap Cetak)
├── docs/                           <-- Dokumentasi Proyek
│   ├── feature-list.md             <-- Katalog Fitur Aktif
│   ├── log/                        <-- Log Harian Setiap Iterasi e/n (Project Diary)
│   └── vibe-coding/                <-- Panduan Integrasi IDE/AI Coding Tools
├── data/                           <-- Folder Penyimpanan Data

│   ├── raw/                        <-- Data Mentah Ekstrak Kaggle (Female Daily Dataset)
│   ├── cleaned/                    <-- Data Hasil Pembersihan Teks
│   └── annotated/                  <-- Data Hasil Anotasi Aspek & Trust
├── models/                         <-- Folder Penyimpanan Bobot Model AI
│   └── indobert_halal/             <-- Weights Model Fine-Tuned IndoBERT
├── backend/                        <-- Source Code Server API (Python)
│   ├── main.py                     <-- Entrypoint Server FastAPI
│   ├── api/                        <-- Endpoint API (/predict, /explain)
│   └── services/                   <-- Logic Loading Model IndoBERT & SHAP
└── frontend/                       <-- Source Code Web Dashboard (React/Vite)
```


---

# Agent Instructions

You must follow these workflow rules strictly to support rapid, iterative enhancements of the platform:

## 1. Trigger "e" or "enhance"
If the user types "e", "enhance", or requests an enhancement plan:
- Read `NEXT_AND_ENHANCEMENT.md` to understand the current platform structure, history, and active tasks.
- Overwrite or update the active tasks list inside `NEXT_AND_ENHANCEMENT.md`.
- The plan must cover each main section/module of the application.
- Inside the tasks list, define **exactly 3 new enhancements per section** with:
  1. A unique number (e.g., `1.1`, `1.2`, `1.3`).
  2. A clear, specific description of the functional change.
  3. A status (initially set to `[TODO]`).
- Present this plan to the user in your final summary response.

## 2. Trigger "n", "next", or "n{x}"
If the user types "n", "next", "n{x}" (where `{x}` is a positive integer representing the number of enhancements, e.g., "n3"), or requests execution of the next enhancement task(s):
- Read `NEXT_AND_ENHANCEMENT.md` to check the status of tasks.
- If all enhancement tasks in `NEXT_AND_ENHANCEMENT.md` are marked `[DONE]` (or there are no tasks marked `[TODO]`), automatically execute the **Trigger "e" or "enhance"** workflow to generate a new set of tasks.
- Otherwise, identify and select the most impactful enhancement task(s) currently marked `[TODO]` (evaluating which tasks have the highest strategic value, functional impact, or user experience contribution). If `{x}` is specified, select the top `{x}` most impactful enhancement tasks and execute them sequentially.
### 2a. Clarify before building ("Grill Me" step)
Before implementing a task, check whether its scope or acceptance criteria are genuinely ambiguous (multiple valid interpretations, unspecified UI/data behavior, no clear "done" condition). If so:
- Ask clarifying questions **one at a time** until the task is unambiguous — use your tool's native mechanism (`ask_question` / `AskUserQuestion`) where available, otherwise ask inline and wait for the answer before continuing.
- Record the resolved acceptance criteria as a short 1-3 line note next to the task entry in `NEXT_AND_ENHANCEMENT.md` before writing any code.
- Skip this step entirely when the task is already unambiguous — don't grill the user on obvious work.

- Implement the selected enhancement task(s) fully in the codebase, applying the relevant role(s) from `SKILLS.md` (Architect, Backend, Frontend, QA, Hardware/Compatibility).
- Once completed:
  1. Update the specific task(s) status of `NEXT_AND_ENHANCEMENT.md` to `[DONE]`.
  2. Document the new or updated feature(s) in the `docs/feature-list.md` file (maintaining an organized list of all platform features under the appropriate section heading).
- Verify the build integrity of the workspace (Automated tests + Browser subagent verification).
- In your final response, state which task(s) have been completed and inform the user of the exact menu or navigation path where they can view and interact with the new/updated feature(s).
- Write an iteration log per §2b before finishing.

### 2b. Iteration Log (`docs/log/`)
Every run of "e"/"enhance" or "n"/"next"/"n{x}" must produce its own log file in `docs/log/`, in addition to (not instead of) the `docs/feature-list.md` update:
- **Filename**: `docs/log/<YYYY-MM-DD-HHmm>-<trigger>.md`, e.g. `docs/log/2026-10-15-1730-n1.md`.
- **Content**:
  - What was requested, and which task/section numbers were touched.
  - Steps taken, in order — what was tried.
  - Outcome: what succeeded, what failed, and resolution.
  - Current state of the codebase/feature after this iteration.
  - Considerations for next time: open risks, deferred items.

## 3. File Size & Refactoring Rules
- **Threshold Rule**: Any new or refactored file exceeding 256 lines of code (LOC) must be refactored and split into multiple smaller, modular, and logical components/files.


## 4. Ad-hoc Feature Requests
- For direct feature requests not using "n"/"next", implement the feature and document it in `docs/feature-list.md`.

## 5. Relative Paths in Documentation
- Do not use absolute full paths or root-slashed paths in markdown files/documentation. Always use relative paths (e.g., `./` or `../` relative to the file's directory).

## 6. Self-Correction & Context Reset (Dump Zone Rule)
- **Dump Zone Awareness**: Jika agent mengalami disorientasi lokasi folder, kebingungan konteks repositori, atau menerima indikasi "dump zone" dari user:
  - Agent harus **segera melakukan verifikasi ulang lokasi working directory aktif** (misalnya mengecek file `package.json`, `pyproject.toml`, atau nama repositori tempat file yang sedang dibuka).
  - Agent wajib **melakukan reset pemahaman konteks (refresh state)** seolah-olah memulai percakapan baru (*new chat fresh state*), tanpa mengulangi asumsi dari percakapan atau repositori sebelumnya.
  - Berikan respon yang lugas, tepat sasaran, dan langsung berfokus pada repositori serta file aktif yang sedang dikerjakan user.

## 7. Prinsip Verifikasi Empiris & Etika Komunikasi Lugas (Precision & Zero-Assumption Protocol)
- **DILARANG BERSPEKULASI / ASUMSI**: Agent DILARANG KERAS memberikan klaim bahwa server berjalan, kode berhasil, data lengkap, atau foto asli tanpa bukti verifikasi empiris riil.
- **KOMUNIKASI LUGAS & PRESISI**: Jika pengguna meminta jawaban sederhana ("cukup jawab pertanyaanku, simpel"), Agent WAJIB menjawab secara langsung, ringkas, transparan, dan berbasis angka/fakta riil tanpa narasi panjang atau aksi yang tidak diminta.
- **BUKTI DAHULU, BARU LAPOR**: Setiap pernyataan status keberhasilan WAJIB menyertakan bukti output log/eksekusi terminal atau tangkapan layar riil yang membuktikan bahwa fitur/data tersebut benar-benar berfungsi 100%.
- **VERIFIKASI FILE DAHULU**: Sebelum mengubah atau mengarahkan path/file apa pun, Agent WAJIB memeriksa keberadaan file secara riil di sistem menggunakan perintah pencarian file/baca file.

## 8. Verifikasi Frontend UI via Browser Subagent
- **Browser Subagent Protocol**: AI WAJIB menggunakan `browser_subagent` untuk memverifikasi secara langsung tampilan antarmuka (frontend UI), komponen visual, sorotan warna XAI (highlight kata), dan responsivitas web dashboard pada browser nyata sebelum melaporkan bahwa fitur UI telah selesai.

## 9. Workflow Test-Driven Development (TDD)
- **TDD Workflow Protocol**: AI WAJIB menerapkan pendekatan Test-Driven Development (TDD) dalam pengembangan komponen backend & frontend:
  1. Tulis pengujian (unit test / integration test) terlebih dahulu sebelum mengimplementasikan logika fitur.
  2. Eksekusi test di terminal untuk memastikan status awal terverifikasi *fail* (Red state).
  3. Implementasikan kode fitur hingga pengujian lulus 100% (Green state).
  4. Lakukan refactoring kode dengan mempertahankan seluruh test tetap passing.

## 10. Penggunaan Slash Command /goal
- **Autonomous Execution via `/goal`**: AI WAJIB mendukung dan menggunakan slash command `/goal` sesuai dengan tupoksinya untuk tugas-tugas berdurasi panjang (*long-running autonomous tasks*). Saat mode `/goal` diaktifkan oleh user, AI akan bekerja ekstra menyeluruh, melakukan audit mandiri secara iteratif, dan tidak berhenti hingga seluruh target tercapai secara sempurna (ditandai dengan `<!-- GOAL_COMPLETE -->`).

## 11. Format Output & Prompt Tugas Berikutnya (Next Task Prompting Format)
- **Kondisi Khusus**: Format penutup opsi langkah berikutnya (`Cara Melanjutkan: Ketik n atau next...`) HANYA dicantumkan ketika user secara eksplisit memicu workflow enhancement melalui tombol/perintah `n`, `next`, `e`, atau `enhance`. Jangan tampilkan format penutup ini pada percakapan/pertanyaan biasa.

## 12. Larangan Mutlak Data Palsu, Duplikat, Mockup, dan Kamuflase (Strict Authentic Data Protocol)
- **DILARANG KERAS MENGGUNAKAN DATA PALSU / SIMULASI / DUPLIKAT**:
  - Dilarang membuat, memunculkan, atau menggunakan data dummy, data mockup, data sintetis, data palsu, maupun data hasil simulasi buatan.
  - Dilarang melakukan manipulasi penggabungan (merge) yang menyebabkan pelipatgandaan data ulasan (*Cartesian product duplication*).
  - Setiap ulasan dalam dataset wajib unik dan merefleksikan ulasan konsumen yang sesungguhnya.
- **LARANGAN MENYAMARKAN DATA HILANG (ANTI-CAMOUFLAGE PRINCIPLE)**:
  - Dilarang menutupi ketiadaan data dengan menduplikasi data/foto umum ke berbagai item berbeda seolah-olah data sudah lengkap.
  - Jika data atau aset belum ada, tampilkan status kosong secara jujur (*honest empty state*). Mengakui data belum lengkap jauh lebih bermartabat dan terpercaya daripada menyajikan data duplikat/sintetis.
- **INTEGRITAS TEKS ULASAN PENUH**:
  - Seluruh teks ulasan konsumen wajib dipastikan utuh (tidak terpotong `... Read more`) agar interpretasi NLP dan visualisasi Explainable AI (SHAP) valid.
- **HANYA DATA ASLI, REAL, DAN TIDAK DUPLIKAT**:
  - Seluruh pipeline NLP, dataset splitting (train/val/test), pelatihan model IndoBERT, evaluasi metrik, serta visualisasi dashboard **WAJIB 100% menggunakan data asli (real), otentik, dan bersih tanpa duplikasi**.
  - Sumber data empiris utama proyek ini adalah file asli **Kaggle Female Daily (`00. Review.csv`)** serta ulasan riil baru yang diinputkan pengguna pada aplikasi.

## 13. Larangan Keras Hardcoding Data & Komponen (Strict Dynamic Data Protocol)
- **DILARANG KERAS MENG-HARDCODE DATA DI FRONTEND / BACKEND**:
  - Dilarang menuliskan opsi kategori produk, daftar brand kosmetik, nama produk, jumlah statistik, atau ulasan secara statis/hardcoded di dalam tag HTML (`<option>`, `<button>`, `<div class="card">`, dll.) ataupun di dalam array/objek statis JavaScript frontend.
  - Seluruh kategori (23 kategori), brand kosmetik (216 brand), produk skincare (801 produk), dan ulasan konsumen (8.365 ulasan) **WAJIB dimuat secara 100% dinamis (dynamically loaded)** via endpoint REST API backend yang membaca langsung dari dataset asli `data/annotated/female_daily_skincare_annotated.csv`.
  - Jika dataset mengalami pembaruan, penambahan ulasan baru, atau sinkronisasi data, antarmuka web dashboard wajib secara otomatis merefleksikan data terkini tanpa memerlukan perubahan kode HTML/JS statis.

## 14. Integritas Visual & Foto Produk Asli (Strict Authentic Product Media Protocol)
- **DILARANG KERAS MENGGUNAKAN FOTO SALAH / JUNK / BLIND SCRAPING**:
  - Dilarang menggunakan skrip crawler yang mengambil fallback otomatis (`murls[0]`) dari mesin pencari web umum tanpa validasi domain resmi dan verifikasi visual.
  - Dilarang memasang foto non-kosmetik (seperti jok mobil, karabiner, poster, dokumen edaran dinas, buku, atau adegan drama) pada katalog kosmetik.
- **PRINSIP KEJUJURAN MEDIA (HONEST PLACEHOLDER PRINCIPLE)**:
  - Lebih baik membiarkan produk menampilkan status **"🧴 Foto belum tersedia"** daripada menampilkan kemasan fisik yang salah atau menyesatkan.
  - Pengguna memahami bentuk fisik asli produk di pasaran; menampilkan foto yang salah akan menghancurkan kepercayaan pengguna terhadap aplikasi.
- **PROTOKOL VERIFIKASI PACKSHOT RESMI**:
  - Seluruh foto produk wajib bersumber dari katalog resmi (Female Daily / Official Store).
  - Wajib diverifikasi secara visual melalui `browser_subagent` untuk memastikan gambar merupakan kemasan botol/tube/jar asli dari produk dan brand terkait.
- **DILARANG MEMBUAT KLAIM STATUS TANPA AUDIT VISUAL**:
  - Agent dilarang mengklaim kumpulan foto "sudah beres" atau "foto asli" hanya berdasarkan jumlah file atau ukuran byte di disk.
  - Klaim keberhasilan foto produk hanya sah jika didukung oleh bukti audit sampel visual nyata.

