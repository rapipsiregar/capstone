/**
 * CHARM V4 view: Direktori Brand (route #/).
 * Data: GET /catalog/brands (brands + facet counts). Facet state lives in the URL hash.
 */
(function () {
  const PAGE_SIZE = 12;
  const TOP_CATEGORIES = 6;
  let showAllCategories = false;

  function readFilters(params) {
    return {
      category: (params.get('category') || '').split(',').filter(Boolean),
      halal: params.get('halal') === '1',
      bpom: params.get('bpom') === '1',
      rating: params.get('rating') === '4',
      page: Math.max(1, parseInt(params.get('page') || '1', 10) || 1)
    };
  }

  function hrefFor(f, patch = {}) {
    const next = { ...f, page: 1, ...patch };
    return window.charmUI.routeWith('/', {
      category: next.category, halal: next.halal ? 1 : '', bpom: next.bpom ? 1 : '',
      rating: next.rating ? 4 : '', page: next.page > 1 ? next.page : ''
    });
  }

  function apiQuery(f) {
    const q = new URLSearchParams({ page: f.page, limit: PAGE_SIZE });
    if (f.category.length) q.set('category', f.category.join(','));
    if (f.halal) q.set('halal', 'true');
    if (f.bpom) q.set('bpom', 'true');
    if (f.rating) q.set('min_rating', '4');
    return `/catalog/brands?${q.toString()}`;
  }

  function option(id, label, checked, count) {
    const { esc, fmtNum } = window.charmUI;
    return `<label class="facet-option"><input type="checkbox" id="${esc(id)}" ${checked ? 'checked' : ''}><span>${esc(label)}</span><span class="facet-count">${fmtNum(count)}</span></label>`;
  }

  function renderFacets(f, facets) {
    const panel = document.getElementById('facetPanel');
    if (!panel || !facets) return;
    const { esc, fmtNum } = window.charmUI;
    const cats = facets.categories || [];
    const visible = showAllCategories ? cats : cats.filter((c, i) => i < TOP_CATEGORIES || f.category.includes(c.category_name));
    const focusedId = document.activeElement && panel.contains(document.activeElement) ? document.activeElement.id : null;

    panel.innerHTML = `
      <div class="facet-group">
        <h2><label for="facetBrand">Pilih brand</label></h2>
        <select id="facetBrand" class="facet-select">
          <option value="">Semua brand (${fmtNum((facets.brand_names || []).length)})</option>
          ${(facets.brand_names || []).map(b => `<option value="${esc(b)}">${esc(b)}</option>`).join('')}
        </select>
      </div>
      <div class="facet-group">
        <h2>Kategori skincare</h2>
        ${visible.map((c, i) => option(`facetCat${i}`, c.category_name, f.category.includes(c.category_name), c.brand_count).replace('<input', `<input data-category="${esc(c.category_name)}"`)).join('')}
        ${cats.length > TOP_CATEGORIES ? `<button type="button" class="btn-link facet-more" id="facetMore">${showAllCategories ? 'Tampilkan lebih sedikit' : `Tampilkan semua (${cats.length})`}</button>` : ''}
        <p class="facet-note">Angka = jumlah brand.</p>
      </div>
      <div class="facet-group">
        <h2>Klaim di ulasan</h2>
        ${option('facetHalal', 'Halal disebut', f.halal, facets.halal_brands)}
        ${option('facetBpom', 'BPOM disebut', f.bpom, facets.bpom_brands)}
        <p class="facet-note">Dihitung dari teks ulasan yang menyebut klaim, bukan sertifikat resmi.</p>
      </div>
      <div class="facet-group">
        <h2>Rating konsumen</h2>
        ${option('facetRating', 'Rata-rata ≥ 4.0', f.rating, facets.rating_4_brands)}
      </div>
      <a class="btn btn-secondary facet-reset" href="#/">Hapus semua filter</a>`;

    const go = window.charmRouter.go;
    panel.querySelector('#facetBrand').addEventListener('change', e => { if (e.target.value) go(window.charmUI.brandHref(e.target.value)); });
    panel.querySelectorAll('input[data-category]').forEach(input => input.addEventListener('change', () => {
      const name = input.dataset.category;
      const category = input.checked ? [...f.category, name] : f.category.filter(c => c !== name);
      go(hrefFor(f, { category }));
    }));
    panel.querySelector('#facetHalal').addEventListener('change', e => go(hrefFor(f, { halal: e.target.checked })));
    panel.querySelector('#facetBpom').addEventListener('change', e => go(hrefFor(f, { bpom: e.target.checked })));
    panel.querySelector('#facetRating').addEventListener('change', e => go(hrefFor(f, { rating: e.target.checked })));
    panel.querySelector('#facetMore')?.addEventListener('click', () => { showAllCategories = !showAllCategories; renderFacets(f, facets); document.getElementById('facetMore')?.focus(); });
    if (focusedId) document.getElementById(focusedId)?.focus();
  }

  function brandCard(b) {
    const { esc, fmtNum, fmtRating, photoHtml, claimPills, brandHref } = window.charmUI;
    const t = b.top_product || {};
    return `
      <a class="brand-card" href="${esc(brandHref(b.brand_name))}">
        <div class="brand-card-head"><span class="brand-card-name">${esc(b.brand_name)}</span></div>
        <div class="brand-card-meta">${fmtNum(b.product_count)} produk · ${fmtNum(b.review_count)} ulasan · rating ${fmtRating(b.avg_rating)}</div>
        <div class="brand-card-claims">${claimPills(b.halal_mentions, b.bpom_mentions)}</div>
        <div class="top-product">
          ${photoHtml(t.photo, t.product_name, 'top-product-thumb')}
          <div><div class="top-product-name">${esc(t.product_name)}</div>
          <div class="top-product-meta">Paling banyak diulas · ${fmtNum(t.review_count)} ulasan · ${fmtRating(t.avg_rating)}</div></div>
        </div>
        <span class="brand-card-link">Buka seluruh produk ${esc(b.brand_name)} &rarr;</span>
      </a>`;
  }

  async function render(params) {
    const f = readFilters(params);
    const { charmFetch, fmtNum, stateBox, pagerHtml } = window.charmUI;
    window.charmRouter.setCrumbs([{ label: 'Katalog', href: '#/' }, { label: 'Direktori Brand' }]);
    const grid = document.getElementById('brandGrid');
    const summary = document.getElementById('directorySummary');
    const countPill = document.getElementById('directoryCount');
    const pager = document.getElementById('brandPager');
    grid.innerHTML = stateBox('loading', 'Memuat direktori brand...', 'Mengambil brand, produk, dan jumlah ulasan dari dataset Female Daily.');
    pager.innerHTML = '';

    try {
      const data = await charmFetch(apiQuery(f));
      renderFacets(f, data.facets);
      summary.textContent = `${fmtNum(data.total_brands)} brand, ${fmtNum(data.total_products)} produk, dan ${fmtNum(data.total_reviews)} ulasan konsumen Female Daily sesuai filter.`;
      countPill.textContent = `${fmtNum(data.total_brands)} brand`;
      if (!data.brands.length) {
        grid.innerHTML = stateBox('empty', 'Tidak ada brand yang cocok dengan filter ini', 'Kombinasi kategori, klaim, dan rating terlalu sempit. Hapus salah satu filter untuk melihat brand lain.', 'Hapus semua filter', '#/');
        return;
      }
      grid.innerHTML = data.brands.map(brandCard).join('');
      pager.innerHTML = pagerHtml(data.page, data.total_pages, p => hrefFor(f, { page: p }));
    } catch (err) {
      summary.textContent = '';
      countPill.textContent = '';
      grid.innerHTML = stateBox('error', `Gagal memuat direktori brand (${err.message})`, 'Server API di port 8000 tidak merespons. Jalankan backend lalu muat ulang.', 'Coba lagi', hrefFor(f, { page: f.page }));
    }
  }

  window.charmViews.directory = { render };
})();

