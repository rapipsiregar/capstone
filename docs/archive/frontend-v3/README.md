# Arsip frontend V3 (tidak dipakai aplikasi)

Berkas di folder ini adalah stylesheet dan skrip antarmuka V3 (katalog kategori → produk → ulasan, header teal) yang digantikan oleh desain V4 "Rose Blush" pada 2026-11-03 (lihat [`../../../DESIGN.md`](../../../DESIGN.md)).

- Berkas **dipindahkan, bukan dihapus**, karena aturan `NEXT_AND_ENHANCEMENT.md` mewajibkan persetujuan per item sebelum menghapus file.
- `frontend/index.html` tidak lagi memuat berkas ini, sehingga tidak ikut dilayani ke pengguna.
- Bila user menyetujui, folder ini boleh dihapus seluruhnya.

| Berkas V3 | Pengganti V4 |
| --- | --- |
| `css/styles.css`, `css/sidebar.css`, `css/tabs.css`, `css/xai-explainer.css` | `frontend/css/tokens.css`, `shell.css`, `guidebook.css` |
| `css/catalog*.css` (7 berkas) | `frontend/css/catalog-views.css`, `detail.css` |
| `js/catalog.js`, `js/catalog-hero.js` | `frontend/js/directory.js`, `brand-products.js`, `product-detail.js`, `header-search.js` |
| `js/catalog-summary.js` | Bar distribusi di `frontend/js/product-detail.js` |
| `js/tabs.js` | `frontend/js/router.js` |
| `js/data.js` | Tidak diperlukan (placeholder kosong sejak Task 11.3) |

