/**
 * CHARM V4 header search pill: brands and products from the API, keyboard friendly.
 * Data: GET /catalog/brands?search= and GET /catalog/products?search=
 */
(function () {
  let timer = null;
  let seq = 0;

  function close(box, input) {
    box.hidden = true;
    input.setAttribute('aria-expanded', 'false');
  }

  async function runSearch(q, box, input) {
    const { charmFetch, esc, fmtNum, fmtRating, brandHref, productHref } = window.charmUI;
    const mine = ++seq;
    box.hidden = false;
    input.setAttribute('aria-expanded', 'true');
    box.innerHTML = '<div class="search-group-title" role="status">Mencari...</div>';
    try {
      const [brands, products] = await Promise.all([
        charmFetch(`/catalog/brands?search=${encodeURIComponent(q)}&limit=4`),
        charmFetch(`/catalog/products?search=${encodeURIComponent(q)}&limit=5`)
      ]);
      if (mine !== seq) return;
      const b = brands.brands || [];
      const p = products.products || [];
      if (!b.length && !p.length) {
        box.innerHTML = `<div class="search-group-title" role="status">Tidak ada brand atau produk untuk "${esc(q)}". Coba nama brand lain.</div>`;
        return;
      }
      box.innerHTML = [
        b.length ? `<div class="search-group-title">Brand</div>${b.map(x => `<a class="search-item" href="${esc(brandHref(x.brand_name))}"><span>${esc(x.brand_name)}</span><small>${fmtNum(x.product_count)} produk</small></a>`).join('')}` : '',
        p.length ? `<div class="search-group-title">Produk (${fmtNum(products.total_products)} cocok)</div>${p.map(x => `<a class="search-item" href="${esc(productHref(x.product_name, x.brand_name))}"><span>${esc(x.product_name)}<br><small>${esc(x.brand_name)} · ${esc(x.category_name)}</small></span><small>${fmtRating(x.avg_rating)}</small></a>`).join('')}` : ''
      ].join('');
    } catch (err) {
      if (mine !== seq) return;
      box.innerHTML = `<div class="search-group-title" role="alert">Pencarian gagal (${esc(err.message)}). Pastikan backend aktif di port 8000.</div>`;
    }
  }

  function init() {
    const input = document.getElementById('headerSearch');
    const box = document.getElementById('searchResults');
    if (!input || !box) return;

    input.addEventListener('input', () => {
      clearTimeout(timer);
      const q = input.value.trim();
      if (q.length < 2) { seq++; close(box, input); return; }
      timer = setTimeout(() => runSearch(q, box, input), 250);
    });
    input.addEventListener('keydown', e => {
      const items = [...box.querySelectorAll('.search-item')];
      if (e.key === 'Escape') close(box, input);
      if (e.key === 'ArrowDown' && items.length) { e.preventDefault(); items[0].focus(); }
      if (e.key === 'Enter' && items.length) { e.preventDefault(); items[0].click(); }
    });
    box.addEventListener('keydown', e => {
      const items = [...box.querySelectorAll('.search-item')];
      const i = items.indexOf(document.activeElement);
      if (e.key === 'ArrowDown' && i < items.length - 1) { e.preventDefault(); items[i + 1].focus(); }
      if (e.key === 'ArrowUp') { e.preventDefault(); (i > 0 ? items[i - 1] : input).focus(); }
      if (e.key === 'Escape') { close(box, input); input.focus(); }
    });
    box.addEventListener('click', e => {
      if (e.target.closest('.search-item')) { close(box, input); input.value = ''; }
    });
    document.addEventListener('click', e => {
      if (!box.contains(e.target) && e.target !== input) close(box, input);
    });
  }

  document.addEventListener('DOMContentLoaded', init);
})();

