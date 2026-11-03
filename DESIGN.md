# DESIGN.md: CHARM V4 "Rose Blush & 3D Glossy Serum"

Acuan visual resmi CHARM. Disetujui user pada 2026-11-03 (Task 9.1) dari `Proposal_Mockup_Desain_Kustom_CHARM.pdf` Edisi V4.
Urutan prioritas aturan: `AGENTS.md` > `DESIGN.md` > anti-slop > taste-skill. Setiap keputusan di bawah punya alasan tertulis (R-31).

## 1. Jenis layar dan tugas utama

- **Jenis:** *app screen* (taste-skill `references/app-screens.md`), bukan landing page.
  *Alasan:* pengguna datang untuk menelusuri brand, produk, dan ulasan, lalu membaca alasan model. Tidak ada funnel pemasaran.
- **Keputusan utama per layar:**
  - Direktori Brand: "brand mana yang ingin saya periksa?" Kartu brand menampilkan jumlah produk, ulasan, rating, dan jumlah ulasan yang menyebut klaim halal/BPOM.
  - Produk Brand: "produk mana yang ulasannya ingin saya baca?" Kartu produk tanpa tombol berulang; seluruh kartu adalah tautan.
  - Detail Produk & XAI: "kenapa ulasan ini dinilai High/Low Trust?" Teks ulasan dengan sorotan kata SHAP adalah isi utama halaman.

## 2. Palet (proporsi 60-25-10-5)

| Token | Hex | Proporsi | Peran | Alasan |
| --- | --- | --- | --- | --- |
| `--blush-50` | `#FCF8F8` | 60% | Floating sheet dan ruang baca | Paling terang (L 98%), mata tidak lelah saat membaca ulasan panjang. |
| `--blush-100` | `#FBEFEF` | 25% | Kanvas L-Frame, sidebar filter, kartu brand, banner ringkasan | Satu langkah tonal dari sheet; memisahkan bidang tanpa garis tebal. |
| `--blush-200` | `#F9DFDF` | 10% | Border 1px, pill, sorotan entitas Halal/BPOM | Hanya sebagai garis dan isian kecil supaya layar tidak berlapis-lapis. Border 1.2:1 terhadap sheet (bisikan, sesuai taste app §5). |
| `--blush-400` | `#F5AFAF` | 5% | Header bar, checkbox aktif, bar grafik utama, dasar favicon | Warna pernyataan merek; dibatasi agar tetap berarti "di sini". |
| `--ink` | `#3D2228` | teks | Teks utama | 13.66:1 di `#FCF8F8`, 7.98:1 di `#F5AFAF`. Satu-satunya warna teks yang boleh di atas header. |
| `--ink-muted` | `#75545A` | teks | Teks sekunder | 6.28:1 di `#FCF8F8`, 5.25:1 di `#F9DFDF`. |
| `--accent-text` | `#A84A58` | teks | Tautan, angka metrik, label filter | 5.26:1 di `#FCF8F8`, 4.94:1 di `#FBEFEF`. **Tidak dipakai di atas `#F9DFDF` (4.4:1) atau header.** |
| `--trust-high` | `#1E6B47` | status | High Trust, sorotan SHAP positif | Hijau sesuai AGENTS.md §2.3; 6.13:1 di sheet. |
| `--trust-neutral` | `#8A5A0B` | status | Neutral | Kuning-tua agar teks tetap 5.61:1. |
| `--trust-low` | `#A3262E` | status | Low Trust, sorotan SHAP negatif | Merah sesuai AGENTS.md §2.3; 6.93:1 di sheet. |
| `--white` | `#FFFFFF` | permukaan | Kartu produk, kotak ulasan | Membuat foto kemasan asli tampil netral. |

- **Dilarang:** keluarga krem + terakota dan ungu/indigo (taste `colour.md` §9). Hue palet ini 0° dan 347°, di luar rentang terakota (6–30°).
- **Bayangan dan gradasi:** tidak ada di UI. Pengecualian tertulis: dropdown pencarian (overlay sungguhan) boleh bayangan tipis; favicon boleh gradasi glossy (keputusan user, §7).

## 3. Tipografi (2 family, 5 ukuran)

| Peran | Family | Alasan |
| --- | --- | --- |
| Display (nama CHARM, judul halaman, nama brand) | Playfair Display 600/700 | Nuansa editorial majalah kecantikan, sesuai mockup V4. |
| Teks, UI, angka | Inter 400/500/600/700 | Terbaca di 14–16px; mendukung `tabular-nums` untuk angka rata kanan. |

Outfit dan JetBrains Mono dari mockup **tidak dipakai** di aplikasi: aturan taste "maksimal 2 typeface" (Task 10.5) dan mono hanya untuk kode.

Skala (5 ukuran): `--fs-1` 12px (meta), `--fs-2` 14px (UI, label), `--fs-3` 16px (teks ulasan dan paragraf), `--fs-4` 20px (judul seksi), `--fs-5` 28px (judul halaman). Headline maksimal 2 baris di 390px.

## 4. Layout

- **Header simetris:** breadcrumb kiri, logo + "CHARM" tengah, pill pencarian kanan; latar `#F5AFAF`. Di bawahnya baris navigasi tenang: Katalog Brand · Insight Reputasi · Simulasi XAI · Metrik Skripsi.
  *Alasan:* mockup V4 menempatkan merek di tengah; navigasi guidebook harus tetap terjangkau tanpa menu admin.
- **Unified L-Frame:** header + sidebar duduk di kanvas `#FBEFEF` yang sama, membungkus floating sheet `#FCF8F8`.
- **Faceted Skincare Filter (sidebar):** Pilih Brand, Kategori Skincare, Klaim di Ulasan (Halal / BPOM), Rating Konsumen. Halaman Detail dan Guidebook memakai sheet lebar penuh tanpa sidebar.
- **Responsif:** 1440px (sidebar 220px + sheet), 768px (sidebar menjadi panel di atas sheet), 390px (satu kolom, header bertumpuk; pill pencarian lebar penuh).
- **Radius:** 12px untuk frame/sheet, 8px untuk kartu, 9999px hanya untuk pill dan pencarian.

## 5. Kejujuran data (AGENTS.md §12–§14)

- Semua angka dari API (`/catalog/brands`, `/catalog/brand-profile`, `/catalog/products`, `/catalog/reviews`, `/analytics/brands`, `/model/metrics`).
- Label "Halal MUI Verified", "BPOM Resmi", tagline brand, dan angka contoh dari mockup **tidak dipakai**, karena dataset hanya mencatat *penyebutan* klaim di teks ulasan (`klaim_halal`, `klaim_bpom`). UI menulis "Klaim halal disebut di N ulasan".
- Produk tanpa packshot terverifikasi menampilkan teks "Foto belum tersedia".

## 6. Dial dan gerak

- **ENERGY 1** (tenang): satu aksen, tanpa dekorasi latar. **RHYTHM 1** (katalog terstruktur): grid seragam karena kontennya seragam. **MOTION 1**: hanya hover/fokus 150 ms ease-out pada `background-color`, `border-color`, `color`; tanpa loop.
- Fokus keyboard: `outline: 2px solid #A84A58; outline-offset: 2px` pada semua kontrol.

## 7. Logo dan favicon

- Konsep D "Purity Droplet & Crescent", varian Blossom Gloss: squircle `#F5AFAF`→`#F9DFDF`, bulan sabit mutiara `#FCF8F8`→`#F9DFDF`, tetesan serum radial `#FFFFFF`→`#F5AFAF` dengan pantulan specular.
- **Gradasi diizinkan hanya di favicon/logo** atas permintaan eksplisit user (2026-11-03: "lebih mengkilap dan glossy"). Tanpa garis putus-putus, tanpa warna gelap.

## 8. Grafik (Task 10.4)

- Satu keluarga hue per grafik. Aspek (kategori): tangga rose `#F5AFAF`, `#E8959B`, `#C9636F`, `#A84A58` dengan pemisah putih 2px. Kepercayaan: warna status §2 (hijau/kuning-tua/merah). Metrik model: batang `#F5AFAF` bergaris `#A84A58` (garis memberi 3:1 terhadap putih).
- Judul grafik menyebut pertanyaannya, misalnya "Distribusi aspek dari N ulasan".
