/**
 * CHARM - Female Daily 3-Level Drill-Down Catalog Engine
 * Level 1: Categories -> Level 2: Products -> Level 3: Reviews & XAI
 */

const CATEGORY_ICONS = (typeof window !== 'undefined' && window.CATEGORY_ICONS) ? window.CATEGORY_ICONS : {};

const catalogState = {
  currentCategory: null,
  currentProduct: null,
  productsPage: 1,
  reviewsPage: 1
};

function getCatalogApiBase() {
  if (typeof API_BASE_URL !== 'undefined') return API_BASE_URL;
  return `http://${window.location.hostname || 'localhost'}:8000/api/v1`;
}

/** Badge only when the dataset flags halal_claim / bpom_claim for the product. */
function complianceLabel(halal_claim, bpom_claim) {
  if (halal_claim && bpom_claim) return 'Klaim Halal & BPOM';
  if (halal_claim) return 'Klaim Halal';
  if (bpom_claim) return 'Klaim BPOM';
  return '';
}

function trustBadgeHtml(trust) {
  const map = {
    High_Trust: ['#DCFCE7', '#166534', 'High Trust'],
    Low_Trust: ['#FEE2E2', '#991B1B', 'Low Trust'],
    Neutral: ['#FEF3C7', '#92400E', 'Neutral']
  };
  const [bg, fg, label] = map[trust] || map.Neutral;
  return `<span class="badge" style="background:${bg}; color:${fg}; font-weight:600; padding:0.2rem 0.5rem; border-radius:6px;">${label}</span>`;
}

async function loadCatalogCategories() {
  const container = document.getElementById("categoryGridContainer");
  if (!container) return;
  container.innerHTML = '<div class="text-center" style="grid-column: 1/-1; padding: 2rem; color: #64748B;">Memuat kategori skincare...</div>';

  try {
    const res = await fetch(`${getCatalogApiBase()}/catalog/categories`);
    const data = await res.json();
    if (data.status !== "success" || !data.categories) throw new Error("Gagal mengambil kategori");

    container.innerHTML = data.categories.map(cat => {
      const icon = (CATEGORY_ICONS[cat.category_name] || (cat.category_name || '').slice(0, 2)).toUpperCase();
      const img = `./images/categories/${cat.slug || 'skincare-general'}.jpg`;
      return `
        <button type="button" class="category-circle-item" onclick="catalogApp.openCategoryProducts('${cat.category_name.replace(/'/g, "\\'")}', 1)" title="${cat.category_name} (${cat.product_count} Produk)">
          <div class="category-circle-avatar" aria-hidden="true">
            <img src="${img}" alt="${cat.category_name}" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='block';"/>
            <span class="category-fallback-emoji" style="display:none;">${icon}</span>
          </div>
          <span class="category-name-label">${cat.category_name}</span>
          <span class="category-count-subtext">${cat.product_count} Produk</span>
        </button>`;
    }).join("");
  } catch (err) {
    container.innerHTML = `<div style="grid-column: 1/-1; color: #DC2626; text-align: center;">Gagal memuat kategori: ${err.message}</div>`;
  }
}

async function openCategoryProducts(categoryName, page = 1) {
  catalogState.currentCategory = categoryName;
  catalogState.productsPage = page;

  document.getElementById("catalog-level-categories").style.display = "none";
  document.getElementById("catalog-level-products").style.display = "block";
  document.getElementById("catalog-level-reviews").style.display = "none";

  const breadcrumb = document.getElementById("currentCategoryBreadcrumb");
  const title = document.getElementById("catalogCategoryTitle");
  const slug = (categoryName || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  if (breadcrumb) breadcrumb.textContent = categoryName;
  if (title) {
    title.innerHTML = `<span style="display:inline-flex;align-items:center;gap:0.75rem;"><img src="./images/categories/${slug}.jpg" alt="${categoryName}" style="width:36px;height:36px;border-radius:50%;object-fit:cover;border:2px solid #0F766E;box-shadow:0 2px 8px rgba(15,118,110,0.2);" onerror="this.style.display='none';"/>${categoryName}</span>`;
  }

  const grid = document.getElementById("catalogProductsGrid");
  if (!grid) return;
  grid.innerHTML = '<div class="text-center" style="grid-column: 1/-1; padding: 2rem; color: #64748B;">Memuat produk...</div>';

  try {
    const res = await fetch(`${getCatalogApiBase()}/catalog/products?category=${encodeURIComponent(categoryName)}&page=${page}&limit=12`);
    const data = await res.json();

    const subtitle = document.getElementById("catalogCategorySubtitle");
    if (subtitle) subtitle.textContent = `Ditemukan ${data.total_products} produk kosmetik dari brand terverifikasi`;

    if (!data.products || data.products.length === 0) {
      grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 2rem;">Tidak ada produk ditemukan.</div>';
      return;
    }

    grid.innerHTML = data.products.map(p => {
      const pSlug = (p.brand_name + '-' + p.product_name).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
      const cSlug = (categoryName || p.category_name || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
      return `
      <div class="catalog-product-card" onclick="catalogApp.openProductReviews('${p.product_name.replace(/'/g, "\\'")}', 1)">
        <div class="product-card-thumb-wrap">
          <img src="./images/products/${pSlug}.jpg?v=2" class="product-card-thumb-img" alt="${p.product_name}" loading="lazy" onerror="this.onerror=null;this.parentElement.classList.add('no-photo');this.parentElement.innerHTML='<div class=\\'no-photo-badge\\'><span class=\\'no-photo-icon\\'>PROD</span><span class=\\'no-photo-text\\'>Foto belum tersedia</span></div>';" />
        </div>
        <span class="product-brand-tag">${p.brand_name}</span>
        <h3 class="catalog-product-title">${p.product_name}</h3>
        <div class="product-metrics-row">
          <span class="product-rating-stars">Rating ${p.avg_rating.toFixed(1)}</span>
          <span class="product-review-badge">(${p.review_count} ulasan)</span>
          <span style="font-size: 0.75rem; color: #0F766E; margin-left: auto;" title="Disebut dalam ulasan konsumen">${complianceLabel(p.halal_claim, p.bpom_claim)}</span>
        </div>
        <button type="button" class="btn-view-reviews">Lihat Ulasan & Analisis XAI &rarr;</button>
      </div>`;
    }).join("");

    renderPagination("catalogProductsPagination", data.page, data.total_pages, p => openCategoryProducts(categoryName, p));
  } catch (err) {
    grid.innerHTML = `<div style="grid-column: 1/-1; color: #DC2626;">Gagal memuat produk: ${err.message}</div>`;
  }
}

async function openProductReviews(productName, page = 1) {
  catalogState.currentProduct = productName;
  catalogState.reviewsPage = page;

  document.getElementById("catalog-level-categories").style.display = "none";
  document.getElementById("catalog-level-products").style.display = "none";
  document.getElementById("catalog-level-reviews").style.display = "block";

  const breadcrumb = document.getElementById("currentProductBreadcrumb");
  if (breadcrumb) breadcrumb.textContent = productName;

  const hero = document.getElementById("productHeroContainer");
  const feed = document.getElementById("catalogReviewsFeed");
  if (feed) feed.innerHTML = '<div class="text-center" style="padding: 2rem; color: #64748B;">Memuat ulasan dan analisis XAI...</div>';

  try {
    const res = await fetch(`${getCatalogApiBase()}/catalog/reviews?product_name=${encodeURIComponent(productName)}&page=${page}&limit=8`);
    const data = await res.json();
    const info = data.product_info || {};

    if (hero) {
      hero.innerHTML = `
        <div class="product-hero-title">
          <span class="product-brand-tag">${info.brand_name || 'Brand'}</span>
          <h2>${info.product_name || productName}</h2>
          <p style="font-size: 0.88rem; color: #64748B; margin-top: 0.25rem;">Kategori: <strong>${info.category_name || '-'}</strong>${complianceLabel(info.halal_claim, info.bpom_claim) ? ` • <strong>${complianceLabel(info.halal_claim, info.bpom_claim)}</strong>` : ''}</p>
        </div>
        <div style="text-align: right;">
          <div style="font-size: 1.5rem; font-weight: 700; color: #0F766E;">Rating ${(info.avg_rating || 5.0).toFixed(1)}</div>
          <div style="font-size: 0.85rem; color: #64748B;">Dari ${data.total_reviews} Ulasan Konsumen</div>
        </div>
      `;
    }

    if (window.catalogSummary) window.catalogSummary.render(info, data.total_reviews);

    if (!data.reviews || data.reviews.length === 0) {
      if (feed) feed.innerHTML = '<div style="text-align: center; padding: 2rem;">Belum ada ulasan untuk produk ini.</div>';
      return;
    }

    if (feed) {
      feed.innerHTML = data.reviews.map(r => {
        const xai = r.xai_explanation || {};
        const umkmRec = (xai.umkm_recommendation || '').replace(/^Saran UMKM \([^)]*\):\s*/, '');
        return `
          <div class="catalog-review-card">
            <div class="catalog-review-header">
              <div style="display: flex; align-items: center; gap: 0.6rem;">
                <span class="catalog-user-badge">${r.user}</span>
                <span class="catalog-skin-tag">${r.age_skin}</span>
              </div>
              <div style="display: flex; align-items: center; gap: 0.6rem;">
                <span style="color: #0F766E; font-weight: 700;">Rating ${r.rating}</span>
                ${trustBadgeHtml(r.trust)}
              </div>
            </div>
            <div class="catalog-review-body">${(r.highlighted_text || r.text || '').replace(/\s*\.\.\.\s*Read more/gi, '...')}</div>
            <div class="catalog-xai-box">
              <div class="catalog-xai-row">
                <span class="catalog-xai-label" style="color: #0F766E;">Alasan AI:</span>
                <span>${xai.trust_reason || '-'}${xai.suitable_skin_types ? ` (${xai.suitable_skin_types})` : ''}</span>
              </div>
              <div class="catalog-xai-row">
                <span class="catalog-xai-label" style="color: #B45309;">Saran UMKM:</span>
                <span>${umkmRec || '-'}</span>
              </div>
            </div>
          </div>
        `;
      }).join("");
    }

    renderPagination("catalogReviewsPagination", data.page, data.total_pages, p => openProductReviews(productName, p));
  } catch (err) {
    if (feed) feed.innerHTML = `<div style="color: #DC2626;">Gagal memuat ulasan: ${err.message}</div>`;
  }
}

function renderPagination(elementId, currentPage, totalPages, onPageClick) {
  const container = document.getElementById(elementId);
  if (!container) return;
  if (!totalPages || totalPages <= 1) { container.innerHTML = ""; return; }

  let html = "";
  if (currentPage > 1) {
    html += `<button type="button" class="btn-breadcrumb" onclick="window._pageCallback(${currentPage - 1})">&larr; Hal Sebelumnya</button>`;
  }
  html += `<span style="font-size: 0.85rem; color: #64748B; font-weight: 500;">Halaman ${currentPage} dari ${totalPages}</span>`;
  if (currentPage < totalPages) {
    html += `<button type="button" class="btn-breadcrumb" onclick="window._pageCallback(${currentPage + 1})">Hal Berikutnya &rarr;</button>`;
  }
  window._pageCallback = onPageClick;
  container.innerHTML = html;
}

function backToCategories() {
  document.getElementById("catalog-level-categories").style.display = "block";
  document.getElementById("catalog-level-products").style.display = "none";
  document.getElementById("catalog-level-reviews").style.display = "none";
  document.getElementById("catalog-drilldown-container").scrollIntoView({ behavior: "smooth" });
}

function backToProducts() {
  if (catalogState.currentCategory) {
    openCategoryProducts(catalogState.currentCategory, catalogState.productsPage);
  } else if (window.catalogHeroApp && window.catalogHeroApp.lastSearchQuery) {
    window.catalogHeroApp.openSearchResults(window.catalogHeroApp.lastSearchQuery, window.catalogHeroApp.lastSearchPage || 1);
  } else {
    backToCategories();
  }
}

window.catalogApp = { loadCatalogCategories, openCategoryProducts, openProductReviews, backToCategories, backToProducts };

document.addEventListener("DOMContentLoaded", () => {
  const p = new URLSearchParams(window.location.search);
  if (p.get('product')) openProductReviews(p.get('product'));
  else if (p.get('category')) openCategoryProducts(p.get('category'));
  else loadCatalogCategories();
});
