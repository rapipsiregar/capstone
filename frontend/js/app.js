/**
 * CHARM guidebook controller: Insight Reputasi filters, KPI, charts and SHAP drivers.
 * Every number comes from the API. A selected product uses its own review distributions
 * from /catalog/reviews (no estimated splits, finding F26).
 */

document.addEventListener('DOMContentLoaded', async () => {
  const exportLink = document.getElementById('btnExportSummary');
  if (exportLink) exportLink.href = `${API_BASE_URL}/export/summary?format=csv`;
  if (typeof bindSandboxEvents === 'function') bindSandboxEvents();
  if (typeof bindPaginationEvents === 'function') bindPaginationEvents();
  document.getElementById('btn-refresh-history')?.addEventListener('click', () => renderHistoryWithPagination(1));
  bindFilterEvents();
  populateAllCategoriesDropdown();
  await loadAnalyticsData('ALL', 'ALL', 'ALL');
  populateAllBrandsDropdown();
  if (typeof renderHistoryWithPagination === 'function') renderHistoryWithPagination(1);
});

window.charmViews = window.charmViews || {};
window.charmViews.insight = { render: () => setTimeout(() => window.refreshCurrentAnalyticsCharts(), 40) };
window.charmViews.sandbox = { render: () => {} };
window.charmViews.metrics = { render: () => setTimeout(() => renderComparisonChart(), 40) };

async function populateAllBrandsDropdown() {
  const select = document.getElementById('brandFilter');
  if (!select) return;
  try {
    const data = await fetchBrandAnalytics('ALL', 'ALL');
    const brands = (data?.all_brands || []).slice().sort((a, b) => a.localeCompare(b));
    select.innerHTML = `<option value="ALL">Semua brand (${brands.length})</option>` +
      brands.map(b => `<option value="${window.charmUI.esc(b)}">${window.charmUI.esc(b)}</option>`).join('');
  } catch (e) {
    console.warn('Daftar brand tidak termuat:', e);
  }
}

async function populateAllCategoriesDropdown() {
  const select = document.getElementById('categoryFilter');
  if (!select) return;
  try {
    const data = await window.charmUI.charmFetch('/catalog/categories');
    const cats = (data.categories || []).map(c => c.category_name).sort((a, b) => a.localeCompare(b));
    select.innerHTML = `<option value="ALL">Semua kategori (${cats.length})</option>` +
      cats.map(c => `<option value="${window.charmUI.esc(c)}">${window.charmUI.esc(c)}</option>`).join('');
  } catch (e) {
    console.warn('Daftar kategori tidak termuat:', e);
  }
}

/** Real per-product distributions: product_info from /catalog/reviews covers all its reviews. */
async function fetchProductStats(productName) {
  const data = await window.charmUI.charmFetch(`/catalog/reviews?product_name=${encodeURIComponent(productName)}&limit=1`);
  const info = data.product_info || {};
  const aspects = info.aspect_distribution || {};
  const top = Object.entries(aspects).sort((a, b) => b[1] - a[1])[0];
  return {
    total: data.total_reviews || 0,
    highTrustPct: Math.round(info.high_trust_pct || 0),
    topAspect: top ? top[0] : '–',
    aspectCounts: aspects,
    trustCounts: info.trust_distribution || {}
  };
}

function statsFromScope(scope, apiData) {
  return {
    total: scope.total_reviews,
    highTrustPct: Math.round((scope.high_trust_ratio || 0) * 100),
    topAspect: scope.top_aspect || '–',
    aspectCounts: scope.aspect_distribution || {},
    trustCounts: scope.trust_counts || null,
    trust_drivers: apiData.trust_drivers || null,
    compliance: apiData.compliance || null
  };
}

async function loadAnalyticsData(brandName = 'ALL', categoryName = 'ALL', productName = 'ALL') {
  let stats = null;
  try {
    const apiData = await fetchBrandAnalytics(brandName, categoryName);
    if (!apiData) return;
    let products = apiData.all_products || [];
    let scope = apiData;
    if (brandName !== 'ALL') {
      const found = (apiData.brands_summary || []).find(b => b.brand_name.toLowerCase() === brandName.toLowerCase());
      if (!found) return;
      products = found.products || [];
      const counts = { High_Trust: 0, Neutral: 0, Low_Trust: 0 };
      // brands_summary carries ratios; counts are derived back from the exact totals of that brand
      counts.High_Trust = Math.round(found.total_reviews * found.high_trust_ratio);
      counts.Low_Trust = Math.round(found.total_reviews * found.low_trust_ratio);
      counts.Neutral = found.total_reviews - counts.High_Trust - counts.Low_Trust;
      scope = { ...found, trust_counts: counts };
    }
    updateProductDropdown(products, productName, brandName);
    stats = productName !== 'ALL' ? await fetchProductStats(productName) : statsFromScope(scope, apiData);
    stats.trust_drivers = apiData.trust_drivers || null;
    stats.compliance = apiData.compliance || null;
  } catch (e) {
    console.warn('Analitik tidak termuat:', e);
  }
  if (!stats) return;
  window._currentStats = stats;

  const set = (id, text) => { const el = document.getElementById(id); if (el) el.textContent = text; };
  set('stat-total-reviews', Number(stats.total).toLocaleString('id-ID'));
  set('stat-high-trust', `${stats.highTrustPct}%`);
  set('stat-top-aspect', String(stats.topAspect).replace(/_/g, ' '));
  renderAspectChart(stats.aspectCounts);
  if (stats.trustCounts) renderTrustChart(stats.trustCounts);
  renderRightSidebarAnalytics(brandName, stats.trust_drivers, stats.compliance);
}

window.refreshCurrentAnalyticsCharts = function () {
  const s = window._currentStats;
  if (!s) return;
  renderAspectChart(s.aspectCounts);
  if (s.trustCounts) renderTrustChart(s.trustCounts);
};

function updateProductDropdown(products, selected = 'ALL', brandName = 'ALL') {
  const select = document.getElementById('productFilter');
  const group = document.getElementById('productFilterGroup');
  if (!select) return;
  const { esc } = window.charmUI;
  if (!products || !products.length) {
    if (group) group.hidden = true;
    select.innerHTML = '<option value="ALL">Tidak ada produk</option>';
    return;
  }
  if (group) group.hidden = false;
  const label = brandName === 'ALL' ? `Semua produk (${products.length})` : `Semua produk ${esc(brandName)} (${products.length})`;
  select.innerHTML = `<option value="ALL">${label}</option>` + products.map(p =>
    `<option value="${esc(p.product_name)}" ${p.product_name === selected ? 'selected' : ''}>${esc(p.product_name)} (${p.total_reviews} ulasan)</option>`).join('');
}

function bindFilterEvents() {
  const brand = document.getElementById('brandFilter');
  const category = document.getElementById('categoryFilter');
  const product = document.getElementById('productFilter');
  const reload = () => loadAnalyticsData(brand?.value || 'ALL', category?.value || 'ALL', product?.value || 'ALL');
  brand?.addEventListener('change', () => { if (product) product.value = 'ALL'; reload(); });
  category?.addEventListener('change', () => { if (product) product.value = 'ALL'; reload(); });
  product?.addEventListener('change', reload);
}

function renderRightSidebarAnalytics(brandName = 'ALL', drivers = null, compliance = null) {
  renderBrandTrustInsightCard(brandName, drivers);
  if (compliance) {
    const pct = compliance.compliance_percentage || `${Math.round((compliance.compliance_ratio || 0) * 100)}%`;
    const bar = document.getElementById('halalComplianceProgressBar');
    const text = document.getElementById('halalComplianceRatioText');
    const count = document.getElementById('complianceInfoReviewCount');
    if (bar) bar.style.width = pct;
    if (text) text.textContent = `${pct} (${compliance.either_count} dari ${compliance.total_reviews})`;
    if (count) count.textContent = Number(compliance.total_reviews).toLocaleString('id-ID');
  }
}

/** SHAP driver words from the API (IndoBERT SHAP cache); empty lists show an honest note. */
function renderBrandTrustInsightCard(brandName = 'ALL', dynamicDrivers = null) {
  const { esc } = window.charmUI;
  const title = document.getElementById('insightCardBrandTitle');
  if (title) title.textContent = brandName === 'ALL' ? 'Semua brand' : brandName;
  const list = (items, cls, emptyText) => (items && items.length)
    ? items.map(d => `<span class="badge ${cls}" title="Atribusi SHAP: ${esc(d.raw_score ?? d.score)}">${esc(d.word)} (${esc(d.score)})</span>`).join(' ')
    : `<span class="muted">${emptyText}</span>`;
  const high = document.getElementById('highTrustDriversList');
  const low = document.getElementById('lowTrustDriversList');
  if (high) high.innerHTML = list(dynamicDrivers?.high, 'badge-green', 'Data kata belum cukup untuk filter ini.');
  if (low) low.innerHTML = list(dynamicDrivers?.low, 'badge-red', 'Tidak ada pemicu Low Trust dominan.');
}
