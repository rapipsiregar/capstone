/**
 * CHARM V4 view: Detail Produk, Ulasan & XAI (route #/product/detail?id={product name}).
 * Data: GET /catalog/reviews -> product_info (all reviews of the product) + one page of reviews
 * with SHAP-highlighted text from the precomputed IndoBERT cache.
 */
(function () {
  const PAGE_SIZE = 6;
  const TRUST_ORDER = [['High_Trust', 'High Trust', 'is-high'], ['Neutral', 'Neutral', 'is-neutral'], ['Low_Trust', 'Low Trust', 'is-low']];

  function hrefFor(product, brand, page) {
    return window.charmUI.routeWith('/product/detail', { id: product, brand, page: page > 1 ? page : '' });
  }

  function barRow(label, count, total, cls = '') {
    const pct = total ? (count / total) * 100 : 0;
    const { esc, fmtNum } = window.charmUI;
    return `
      <div class="dist-row">
        <div class="dist-label"><span>${esc(label)}</span><b>${fmtNum(count)} · ${pct.toFixed(1)}%</b></div>
        <div class="dist-track" role="img" aria-label="${esc(label)}: ${count} dari ${total} ulasan"><div class="dist-fill ${cls}" style="width:${pct.toFixed(1)}%"></div></div>
      </div>`;
  }

  function dossierHtml(info, total) {
    const { esc, fmtNum, fmtRating, photoHtml, brandHref, prettyLabel } = window.charmUI;
    const aspects = Object.entries(info.aspect_distribution || {}).sort((a, b) => b[1] - a[1]);
    const trust = info.trust_distribution || {};
    const claims = [
      info.halal_claim ? '<span class="pill pill-claim">Klaim halal disebut di ulasan</span>' : '',
      info.bpom_claim ? '<span class="pill pill-claim">Klaim BPOM disebut di ulasan</span>' : ''
    ].join('');
    return `
      ${photoHtml(info.photo, info.product_name)}
      <div>
        <span class="dossier-label"><a href="${esc(brandHref(info.brand_name))}">${esc(info.brand_name)}</a> · ${esc(info.category_name)}</span>
        <h1>${esc(info.product_name)}</h1>
        <div class="dossier-claims">${claims}</div>
        <div class="stat-row">
          <div class="stat-box"><strong class="is-trust">${info.high_trust_pct ?? 0}%</strong><span>Ulasan High Trust</span></div>
          <div class="stat-box"><strong class="is-accent">${fmtRating(info.avg_rating)}</strong><span>Rata-rata rating</span></div>
          <div class="stat-box"><strong>${fmtNum(total)}</strong><span>Total ulasan</span></div>
        </div>
      </div>
      <div class="dist-panel">
        <div><h2>Distribusi aspek dari ${fmtNum(total)} ulasan</h2>${aspects.map(([k, v]) => barRow(prettyLabel(k), v, total)).join('')}</div>
        <div><h2>Distribusi kepercayaan</h2>${TRUST_ORDER.filter(([k]) => k in trust).map(([k, label, cls]) => barRow(label, trust[k], total, cls)).join('')}</div>
      </div>`;
  }

  function reviewCard(r) {
    const { esc, trustPill, prettyLabel } = window.charmUI;
    const xai = r.xai_explanation || {};
    const advice = (xai.umkm_recommendation || '').replace(/^Saran UMKM \([^)]*\):\s*/, '');
    const body = (r.highlighted_text || esc(r.text)).replace(/\s*\.\.\.\s*Read more/gi, '...');
    return `
      <article class="review-card">
        <div class="review-head">
          <div class="review-who"><strong>${esc(r.user)}</strong> <span>· ${esc(r.age_skin)}</span></div>
          <div class="review-score"><b>${Number(r.rating).toFixed(0)}/5</b>${trustPill(r.trust)}<span class="pill">${esc(prettyLabel(r.aspect))}</span></div>
        </div>
        <p class="review-body">${body}</p>
        <dl class="review-note">
          <dt>Alasan model</dt><dd>${esc(xai.trust_reason || 'Penjelasan belum tersedia untuk ulasan ini.')}${xai.suitable_skin_types ? ` (${esc(xai.suitable_skin_types)})` : ''}</dd>
          <dt>Saran UMKM</dt><dd>${esc(advice || 'Belum ada saran untuk ulasan ini.')}</dd>
        </dl>
      </article>`;
  }

  async function render(params) {
    const product = params.get('id') || '';
    const brand = params.get('brand') || '';
    const page = Math.max(1, parseInt(params.get('page') || '1', 10) || 1);
    const { charmFetch, fmtNum, stateBox, pagerHtml, brandHref } = window.charmUI;
    const dossier = document.getElementById('productDossier');
    const feed = document.getElementById('reviewFeed');
    const pager = document.getElementById('reviewPager');
    const feedSub = document.getElementById('reviewFeedSub');
    const crumbs = [{ label: 'Katalog', href: '#/' }];
    if (brand) crumbs.push({ label: brand, href: brandHref(brand) });
    window.charmRouter.setCrumbs([...crumbs, { label: product || 'Produk' }]);
    pager.innerHTML = '';

    if (!product) {
      dossier.innerHTML = '';
      feed.innerHTML = stateBox('empty', 'Produk belum dipilih', 'Buka sebuah brand lalu pilih produk untuk membaca ulasannya.', 'Buka direktori brand', '#/');
      return;
    }
    feed.innerHTML = stateBox('loading', 'Memuat ulasan dan bobot SHAP...', `Mengambil ulasan asli untuk "${product}".`);

    try {
      const data = await charmFetch(`/catalog/reviews?product_name=${encodeURIComponent(product)}&page=${page}&limit=${PAGE_SIZE}`);
      const info = data.product_info || {};
      if (!data.total_reviews) {
        dossier.innerHTML = '';
        feed.innerHTML = stateBox('empty', `Belum ada ulasan untuk "${product}"`, 'Produk ini tidak ditemukan di dataset ulasan. Uji kalimat ulasan sendiri di Simulasi XAI.', 'Buka Simulasi XAI', '#/sandbox');
        return;
      }
      if (!brand) window.charmRouter.setCrumbs([{ label: 'Katalog', href: '#/' }, { label: info.brand_name, href: brandHref(info.brand_name) }, { label: info.product_name }]);
      dossier.innerHTML = dossierHtml(info, data.total_reviews);
      feedSub.textContent = `Ulasan asli Female Daily, ${fmtNum(data.total_reviews)} ulasan. Hijau = kata yang mendorong High Trust, merah = kata yang mendorong Low Trust (bobot SHAP IndoBERT).`;
      feed.innerHTML = data.reviews.map(reviewCard).join('');
      pager.innerHTML = pagerHtml(data.page, data.total_pages, p => hrefFor(product, brand, p));
    } catch (err) {
      dossier.innerHTML = '';
      feed.innerHTML = stateBox('error', `Gagal memuat ulasan (${err.message})`, 'Layanan API ulasan di port 8000 tidak dapat dijangkau.', 'Coba lagi', hrefFor(product, brand, page));
    }
  }

  window.charmViews.detail = { render };
})();

