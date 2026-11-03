# Arsip test V3 (tidak dikumpulkan pytest)

Suite ini menguji struktur antarmuka V3 (katalog kategori, `catalog.js`, `catalog-hero.js`, `catalog-summary.js`, `styles.css`, `tabs.css`) yang digantikan desain V4 pada 2026-11-03.
`pytest.ini` hanya mengumpulkan folder `tests/`, jadi berkas di sini tidak dijalankan.

Jaminan penting dari suite ini dipindahkan ke versi V4:

| Suite V3 | Jaminan | Pengganti V4 |
| --- | --- | --- |
| `test_category_focus.py` | Fokus keyboard terlihat | `tests/test_v4_regressions.py::test_focus_visible_on_every_control` |
| `test_mobile_header_layout.py` | Header rapi di 390px | `test_mobile_header_stacks_and_search_spans_width` |
| `test_product_photos.py` | Foto asli atau teks jujur | `test_product_photos_are_real_files_or_honest_text` |
| `test_fd_header_ui.py`, `test_catalog_search.py` | Header sticky + dropdown pencarian | `test_sticky_header_with_search_dropdown` |
| `test_fd_review_cards_ui.py`, `test_review_browser_ui.py` | Kartu ulasan + SHAP + saran UMKM | `test_review_cards_show_shap_text_trust_and_advice` |
| `test_product_summary_ui.py` | Ringkasan dari seluruh ulasan produk | `test_product_summary_uses_all_reviews_of_the_product` |
| `test_homepage_layout.py` | Beranda = katalog; analitik di Insight; tanpa klaim 100% | `test_homepage_is_the_catalog_and_analytics_live_in_insight`, `test_claim_badges_are_data_driven` |
| `test_fd_design_system.py` | Token desain + kelas sorotan SHAP | `tests/test_v4_layout_ui.py::test_tokens_declare_palette_and_text_roles`, `test_claim_badges_are_data_driven` |
| `test_catalog_ui.py`, `test_catalog_hero_ui.py` | Drill-down kategori V3 | Alur V4 Direktori Brand → Produk → Detail: `tests/test_v4_layout_ui.py`, `tests/test_brand_directory_api.py` |

