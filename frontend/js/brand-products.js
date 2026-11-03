/**
 * CHARM V4 view: Produk Brand (route #/brand/products?brand={name}).
 * Data: GET /catalog/brand-profile (banner + category facet) and GET /catalog/products (grid).
 */
(function () {
  const PAGE_SIZE = 12;

  function readFilters(params) {
    return {
      brand: params.get('brand') || '',
      category: params.get('category') || '',
      halal: params.get('halal') === '1',
      bpom: params.get('bpom') === '1',
      rating: params.get('rating') === '4',
      page: Math.max(1, parseInt(params.get('page') || '1', 10) || 1)
    };
  }

  function hrefFor(f, patch = {}) {
    const n = { ...f, page: 1, ...patch };
    return window.charmUI.routeWith('/brand/products', {
      brand: n.brand, category: n.category, halal: n.halal ? 1 : '', bpom: n.bpom ? 1 : '',
      rating: n.rating ? 4 : '', page: n.page > 1 ? n.page : ''
    });
  }

  function renderFacets(f, profile) {
    const panel = document.getElementById('facetPanel');
    if (!panel) return;
    const { esc, fmtNum } = window.charmUI;
    const cats = profile ? profile.categories : [];
    const radio = (value, label, count) => `
      <label class="facet-option"><input type="radio" name="brandCategory" value="${esc(value)}" ${f.category === value ? 'checked' : ''}>
      <span>${esc(label)}</span><span class="facet-count">${fmtNum(count)}</span></label>`;
    const check = (id, label, checked) => `<label class="facet-option"><input type="checkbox" id="${id}" ${checked ? 'checked' : ''}><span>${label}</span></label>`;

    panel.innerHTML = `
      <a class="btn-link" href="#/">&larr; Kembali ke direktori brand</a>
      <div class="facet-group">
        <h2>Kategori ${esc(profile ? profile.brand_name : f.brand)}</h2>
        ${radio('', 'Semua produk', profile ? profile.product_count : 0)}
        ${cats.map(c => radio(c.category_name, c.category_name, c.product_count)).join('')}
        <p class="facet-note">Angka = jumlah produk.</p>
      </div>
      <div class="facet-group">
        <h2>Klaim di ulasan</h2>
        ${check('brandHalal', 'Halal disebut', f.halal)}
        ${check('brandBpom', 'BPOM disebut', f.bpom)}
        <p class="facet-note">Produk yang ulasannya menyebut klaim tersebut.</p>
      </div>
      <div class="facet-group">
        <h2>Rating konsumen</h2>
        ${check('brandRating', 'Rata-rata ≥ 4.0', f.rating)}
      </div>`;

    const go = window.charmRouter.go;
    panel.querySelectorAll('input[name="brandCategory"]').forEach(r => r.addEventListener('change', () => go(hrefFor(f, { category: r.value }))));
    panel.querySelector('#brandHalal').addEventListener('change', e => go(hrefFor(f, { halal: e.target.checked })));
    panel.querySelector('#brandBpom').addEventListener('change', e => go(hrefFor(f, { bpom: e.target.checked })));
    panel.querySelector('#brandRating').addEventListener('change', e => go(hrefFor(f, { rating: e.target.checked })));
  }

  function bannerHtml(p) {
    const { esc, fmtNum, fmtRating, claimPills } = window.charmUI;
    return `
      <div>
        <div class="brand-banner-line"><h1>${esc(p.brand_name)}</h1>${claimPills(p.halal_mentions, p.bpom_mentions)}</div>
        <p>${fmtNum(p.product_count)} produk · ${fmtNum(p.review_count)} ulasan teranotasi · ${p.high_trust_pct}% ulasan High Trust</p>
      </div>
      <div class="banner-figure"><strong>${fmtRating(p.avg_rating)}</strong><span>Rata-rata rating konsumen</span></div>`;
  }

  function productCard(p) {
    const { esc, fmtNum, fmtRating, photoHtml, productHref } = window.charmUI;
    const claims = [p.halal_claim ? 'Halal' : '', p.bpom_claim ? 'BPOM' : ''].filter(Boolean).join(' & ');
    return `
      <a class="product-card" href="${esc(productHref(p.product_name, p.brand_name))}">
        ${photoHtml(p.photo, p.product_name)}
        <span class="product-card-title">${esc(p.product_name)}</span>
        ${claims ? `<span class="product-card-claim">Klaim ${claims} disebut di ulasan</span>` : ''}
        <span class="product-card-meta"><span>${esc(p.category_name)} · ${fmtNum(p.review_count)} ulasan</span><strong>${fmtRating(p.avg_rating)}</strong></span>
      </a>`;
  }

  async function render(params) {
    const f = readFilters(params);
    const { charmFetch, fmtNum, stateBox, pagerHtml } = window.charmUI;
    const banner = document.getElementById('brandBanner');
    const grid = document.getElementById('productGrid');
    const pager = document.getElementById('productPager');
    const heading = document.getElementById('productListHeading');
    window.charmRouter.setCrumbs([{ label: 'Katalog', href: '#/' }, { label: f.brand || 'Brand' }]);
    pager.innerHTML = '';

    if (!f.brand) {
      banner.innerHTML = '<div><h1>Brand belum dipilih</h1></div>';
      grid.innerHTML = stateBox('empty', 'Brand belum dipilih', 'Pilih brand dari direktori untuk melihat produknya.', 'Buka direktori brand', '#/');
      return;
    }
    banner.innerHTML = `<div><h1>${window.charmUI.esc(f.brand)}</h1></div>`;
    grid.innerHTML = stateBox('loading', `Memuat produk ${f.brand}...`, 'Mengambil daftar produk dan jumlah ulasan.');

    try {
      const profile = await charmFetch(`/catalog/brand-profile?brand=${encodeURIComponent(f.brand)}`);
      banner.innerHTML = bannerHtml(profile);
      renderFacets(f, profile);
      const q = new URLSearchParams({ brand: profile.brand_name, page: f.page, limit: PAGE_SIZE });
      if (f.category) q.set('category', f.category);
      if (f.halal) q.set('halal', 'true');
      if (f.bpom) q.set('bpom', 'true');
      if (f.rating) q.set('min_rating', '4');
      const data = await charmFetch(`/catalog/products?${q.toString()}`);
      heading.textContent = `${f.category || 'Semua produk'} · ${fmtNum(data.total_products)} produk`;
      if (!data.products.length) {
        grid.innerHTML = stateBox('empty', 'Tidak ada produk yang cocok', `Filter ini tidak menyisakan produk ${f.brand}. Hapus filter klaim atau rating.`, 'Tampilkan semua produk', hrefFor(f, { category: '', halal: false, bpom: false, rating: false }));
        return;
      }
      grid.innerHTML = data.products.map(productCard).join('');
      pager.innerHTML = pagerHtml(data.page, data.total_pages, p => hrefFor(f, { page: p }));
    } catch (err) {
      renderFacets(f, null);
      banner.innerHTML = '';
      heading.textContent = '';
      const missing = err.status === 404;
      grid.innerHTML = missing
        ? stateBox('empty', `Brand "${f.brand}" tidak ada di dataset`, 'Nama brand mungkin salah ketik. Cari ulang dari direktori.', 'Buka direktori brand', '#/')
        : stateBox('error', `Gagal memuat produk (${err.message})`, 'Server API di port 8000 tidak merespons. Jalankan backend lalu coba lagi.', 'Coba lagi', hrefFor(f, { page: f.page }));
    }
  }

  window.charmViews.brand = { render };
})();
