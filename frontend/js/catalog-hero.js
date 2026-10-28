/**
 * CHARM - Editorial Hero & Skincare Category Icons Engine
 * Provides distinct beauty icons for all 23 categories and instant product quick search.
 */

window.CATEGORY_ICONS = {
  "Acne Treatment": "🎯",
  "Brow & Lash Treatment": "👁️‍🗨️",
  "Cream & Lotion": "🧴",
  "Day Cream": "☀️",
  "Eye Treatment": "👁️",
  "Face Mist": "💦",
  "Face Oil": "🌿",
  "Facial Wash": "🫧",
  "Lotion & Emulsion": "🥛",
  "Makeup Remover": "🧻",
  "Mask Sheet": "🧖‍♀️",
  "Night Cream": "🌙",
  "Nose Pack": "👃",
  "Oil": "🫒",
  "Peeling": "🧪",
  "Scrub & Exfoliator": "✨",
  "Serum & Essence": "💧",
  "Skin Soothing Treatment": "🍃",
  "Skincare General": "🌸",
  "Sleeping Mask": "🛌",
  "Sun Protection": "🛡️",
  "Toner": "🍶",
  "Wash-Off": "🧼"
};

let searchDebounceTimer = null;
let lastSearchQuery = "";
let lastSearchPage = 1;

function initHomepageQuickSearch() {
  const input = document.getElementById("homepageQuickSearch");
  const dropdown = document.getElementById("heroSearchResultsDropdown");
  const clearBtn = document.getElementById("btnHeroSearchClear");
  if (!input || !dropdown) return;

  input.addEventListener("input", e => {
    const val = e.target.value.trim();
    if (clearBtn) clearBtn.style.display = val ? "block" : "none";

    if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
    if (val.length < 2) {
      dropdown.style.display = "none";
      dropdown.innerHTML = "";
      return;
    }

    searchDebounceTimer = setTimeout(async () => {
      dropdown.innerHTML = '<div style="padding: 1rem; color: #64748B; text-align: center;">Mencari produk...</div>';
      dropdown.style.display = "block";

      try {
        const apiBase = typeof API_BASE_URL !== 'undefined' ? API_BASE_URL : `http://${window.location.hostname || 'localhost'}:8000/api/v1`;
        const res = await fetch(`${apiBase}/catalog/products?search=${encodeURIComponent(val)}&limit=6`);
        const data = await res.json();
        const prods = data.products || [];
        const brands = data.matched_brands || [];
        const cats = data.matched_categories || [];

        if (!prods.length && !brands.length && !cats.length) {
          dropdown.innerHTML = `<div style="padding: 1rem; color: #475569; text-align: center;">Tidak ada produk cocok dengan "<strong>${val}</strong>"</div>`;
          return;
        }

        let html = "";
        if (brands.length) {
          html += '<div class="hero-search-section-title">🏷️ Brand Ditemukan</div>';
          html += brands.map(b => `
            <div class="hero-search-chip-item" onclick="catalogHeroApp.openSearchResults('${b.brand_name.replace(/'/g, "\\'")}')">
              <div><span class="product-brand-tag">${b.brand_name}</span> <span style="font-size: 0.78rem; color: #64748B;">${b.product_count} Produk (${b.review_count} Ulasan)</span></div>
              <span style="font-size: 0.78rem; color: #0F766E; font-weight: 700;">Lihat Semua &rarr;</span>
            </div>`).join("");
        }
        if (cats.length) {
          html += '<div class="hero-search-section-title">🧖‍♀️ Kategori Terkait</div>';
          html += cats.map(c => {
            const slug = (c.category_name || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
            return `
            <div class="hero-search-chip-item" onclick="catalogApp.openCategoryProducts('${c.category_name.replace(/'/g, "\\'")}', 1)">
              <div style="display:flex; align-items:center; gap:0.6rem;">
                <img src="./images/categories/${slug}.jpg" alt="${c.category_name}" style="width:28px;height:28px;border-radius:50%;object-fit:cover;border:1.5px solid #CBD5E1;" onerror="this.style.display='none';"/>
                <div><span style="font-weight:700; color:#0F172A; font-size:0.85rem;">${c.category_name}</span> <span style="font-size:0.78rem; color:#64748B;">(${c.product_count} Produk)</span></div>
              </div>
              <span style="font-size: 0.78rem; color: #0F766E; font-weight: 700;">Buka Kategori &rarr;</span>
            </div>`;
          }).join("");
        }
        if (prods.length) {
          html += '<div class="hero-search-section-title">✨ Produk Terpopuler</div>';
          html += prods.map(p => `
            <div class="hero-search-item" onclick="catalogHeroApp.selectSearchProduct('${p.product_name.replace(/'/g, "\\'")}')">
              <div>
                <div style="font-weight: 700; color: #0F172A; font-size: 0.88rem;">${p.product_name}</div>
                <div style="font-size: 0.76rem; color: #64748B;">${p.brand_name} • ${p.category_name}</div>
              </div>
              <div style="font-weight: 700; color: #E11D48; font-size: 0.85rem;">⭐ ${p.avg_rating.toFixed(1)}</div>
            </div>`).join("");
        }
        if (data.total_products > 0) {
          html += `<div class="hero-search-footer" onclick="catalogHeroApp.openSearchResults('${val.replace(/'/g, "\\'")}')">🔍 Lihat seluruh <strong>${data.total_products}</strong> produk untuk "${val}" &rarr;</div>`;
        }
        dropdown.innerHTML = html;
      } catch (err) {
        dropdown.innerHTML = `<div style="padding: 1rem; color: #DC2626; text-align: center;">Pencarian gagal: ${err.message}</div>`;
      }
    }, 250);
  });

  input.addEventListener("focus", () => {
    const val = input.value.trim();
    if (val.length >= 2 && dropdown.innerHTML.trim()) {
      dropdown.style.display = "block";
    }
  });

  input.addEventListener("keydown", e => {
    if (e.key === "Enter") {
      e.preventDefault();
      const val = input.value.trim();
      if (val.length >= 2) {
        openSearchResults(val);
      }
    } else if (e.key === "Escape") {
      dropdown.style.display = "none";
    }
  });

  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      input.value = "";
      clearBtn.style.display = "none";
      dropdown.style.display = "none";
      input.focus();
    });
  }

  document.addEventListener("click", e => {
    if (!input.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.style.display = "none";
    }
  });
}

function selectSearchProduct(productName) {
  const dropdown = document.getElementById("heroSearchResultsDropdown");
  if (dropdown) dropdown.style.display = "none";
  if (window.catalogApp && window.catalogApp.openProductReviews) {
    window.catalogApp.openProductReviews(productName, 1);
  }
}

async function openSearchResults(query, page = 1) {
  lastSearchQuery = query;
  lastSearchPage = page;

  const dropdown = document.getElementById("heroSearchResultsDropdown");
  if (dropdown) dropdown.style.display = "none";

  if (window.catalogState) {
    window.catalogState.currentCategory = null;
  }

  const catView = document.getElementById("catalog-level-categories");
  const prodView = document.getElementById("catalog-level-products");
  const revView = document.getElementById("catalog-level-reviews");
  if (catView) catView.style.display = "none";
  if (prodView) prodView.style.display = "block";
  if (revView) revView.style.display = "none";

  const breadcrumb = document.getElementById("currentCategoryBreadcrumb");
  const title = document.getElementById("catalogCategoryTitle");
  const subtitle = document.getElementById("catalogCategorySubtitle");
  if (breadcrumb) breadcrumb.textContent = `Pencarian: "${query}"`;
  if (title) title.textContent = `🔍 Hasil Pencarian: "${query}"`;
  if (subtitle) subtitle.textContent = "Mencari produk kosmetik...";

  const grid = document.getElementById("catalogProductsGrid");
  if (!grid) return;
  grid.innerHTML = '<div style="grid-column: 1/-1; padding: 2rem; color: #64748B; text-align: center;">Mencari produk kosmetik...</div>';

  prodView.scrollIntoView({ behavior: "smooth", block: "start" });

  try {
    const apiBase = typeof API_BASE_URL !== 'undefined' ? API_BASE_URL : `http://${window.location.hostname || 'localhost'}:8000/api/v1`;
    const res = await fetch(`${apiBase}/catalog/products?search=${encodeURIComponent(query)}&page=${page}&limit=12`);
    const data = await res.json();
    const prods = data.products || [];

    if (subtitle) subtitle.textContent = `Ditemukan ${data.total_products} produk yang cocok di seluruh kategori`;

    if (!prods.length) {
      grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 2.5rem; color: #475569;">Tidak ada produk yang cocok dengan "<strong>${query}</strong>".</div>`;
      return;
    }

    grid.innerHTML = prods.map(p => {
      const pSlug = (p.brand_name + '-' + p.product_name).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
      const cSlug = (p.category_name || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
      return `
      <div class="catalog-product-card" onclick="catalogApp.openProductReviews('${p.product_name.replace(/'/g, "\\'")}', 1)">
        <div class="product-card-thumb-wrap">
          <img src="./images/products/${pSlug}.jpg?v=2" class="product-card-thumb-img" alt="${p.product_name}" loading="lazy" onerror="this.onerror=null;this.parentElement.classList.add('no-photo');this.parentElement.innerHTML='<div class=\\'no-photo-badge\\'><span class=\\'no-photo-icon\\'>🧴</span><span class=\\'no-photo-text\\'>Foto belum tersedia</span></div>';" />
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
          <span class="product-brand-tag">${p.brand_name}</span>
          <span style="font-size: 0.72rem; color: #0F766E; background: #CCFBF1; padding: 0.15rem 0.5rem; border-radius: 4px; font-weight: 600;">${p.category_name}</span>
        </div>
        <h3 class="catalog-product-title">${p.product_name}</h3>
        <div class="product-metrics-row">
          <span class="product-rating-stars">⭐ ${p.avg_rating.toFixed(1)}</span>
          <span class="product-review-badge">(${p.review_count} ulasan)</span>
        </div>
        <button type="button" class="btn-view-reviews">Lihat Ulasan & Analisis XAI ➔</button>
      </div>`;
    }).join("");

    const paginationContainer = document.getElementById("catalogProductsPagination");
    if (paginationContainer) {
      renderSearchPagination(paginationContainer, data.page, data.total_pages, query);
    }
  } catch (err) {
    grid.innerHTML = `<div style="grid-column: 1/-1; color: #DC2626; text-align: center;">Gagal memuat hasil: ${err.message}</div>`;
  }
}

function renderSearchPagination(container, currentPage, totalPages, query) {
  if (!totalPages || totalPages <= 1) { container.innerHTML = ""; return; }
  let html = "";
  if (currentPage > 1) {
    html += `<button type="button" class="btn-breadcrumb" onclick="catalogHeroApp.openSearchResults('${query.replace(/'/g, "\\'")}', ${currentPage - 1})">◀ Hal Sebelumnya</button>`;
  }
  html += `<span style="font-size: 0.85rem; color: #64748B; font-weight: 500;">Halaman ${currentPage} dari ${totalPages}</span>`;
  if (currentPage < totalPages) {
    html += `<button type="button" class="btn-breadcrumb" onclick="catalogHeroApp.openSearchResults('${query.replace(/'/g, "\\'")}', ${currentPage + 1})">Hal Berikutnya ▶</button>`;
  }
  container.innerHTML = html;
}

window.catalogHeroApp = {
  initHomepageQuickSearch,
  selectSearchProduct,
  openSearchResults,
  get lastSearchQuery() { return lastSearchQuery; },
  get lastSearchPage() { return lastSearchPage; }
};

document.addEventListener("DOMContentLoaded", () => {
  initHomepageQuickSearch();
});
