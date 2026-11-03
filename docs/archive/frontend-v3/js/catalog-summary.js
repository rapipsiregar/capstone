/**
 * CHARM - Per-Product Trust Parameters (Task 6.5)
 * Renders 3 KPI cards + 2 doughnut charts under the Level 3 product hero.
 * All values come from /api/v1/catalog/reviews -> product_info (all reviews of the product).
 */

const productSummaryState = { aspectChart: null, trustChart: null, lastProduct: null };

/* Styling only (not data): trust label colors + aspect color palette by index. */
const TRUST_LABEL_COLORS = { High_Trust: '#16A34A', Neutral: '#F59E0B', Low_Trust: '#DC2626' };
const ASPECT_COLOR_PALETTE = ['#0F766E', '#E11D48', '#6366F1', '#F59E0B', '#0EA5E9', '#A855F7'];

function prettySummaryLabel(key) {
  return String(key).replace(/_/g, ' ');
}

function orderedTrustEntries(dist) {
  const preferred = Object.keys(TRUST_LABEL_COLORS).filter(k => k in dist);
  const others = Object.keys(dist).filter(k => !preferred.includes(k));
  return [...preferred, ...others].map(k => [k, dist[k]]);
}

function destroyProductSummaryCharts() {
  if (productSummaryState.aspectChart) productSummaryState.aspectChart.destroy();
  if (productSummaryState.trustChart) productSummaryState.trustChart.destroy();
  productSummaryState.aspectChart = null;
  productSummaryState.trustChart = null;
}

function buildDoughnut(canvasId, entries, colors, total) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof Chart === 'undefined') return null;
  return new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels: entries.map(([k, v]) => `${prettySummaryLabel(k)} (${v})`),
      datasets: [{ data: entries.map(([, v]) => v), backgroundColor: colors, borderColor: '#ffffff', borderWidth: 2 }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '58%',
      plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } },
        tooltip: {
          callbacks: {
            label: ctx => {
              const count = ctx.raw;
              const pct = total ? ((count / total) * 100).toFixed(1) : '0.0';
              return ` ${prettySummaryLabel(entries[ctx.dataIndex][0])}: ${count} ulasan (${pct}%)`;
            }
          }
        }
      }
    }
  });
}

function renderProductSummary(info, totalReviews) {
  const box = document.getElementById('productSummaryContainer');
  if (!box) return;
  const aspects = info.aspect_distribution || {};
  const trust = info.trust_distribution || {};
  const total = totalReviews || info.total_reviews || 0;

  if (!total || (!Object.keys(aspects).length && !Object.keys(trust).length)) {
    destroyProductSummaryCharts();
    productSummaryState.lastProduct = null;
    box.innerHTML = '';
    return;
  }
  if (productSummaryState.lastProduct === info.product_name && productSummaryState.aspectChart) return;

  const trustEntries = orderedTrustEntries(trust);
  const aspectEntries = Object.entries(aspects);
  const highCount = trust.High_Trust || 0;
  const dominant = (info.dominant_aspects || []).map(prettySummaryLabel).join(' & ') || '-';
  const dominantCount = (info.dominant_aspects || []).length ? aspects[info.dominant_aspects[0]] : 0;

  box.innerHTML = `
    <div class="summary-kpi-grid">
      <div class="summary-kpi-card">
        <span class="summary-kpi-label">Total Ulasan</span>
        <span class="summary-kpi-value">${total}</span>
        <span class="summary-kpi-sub">seluruh ulasan produk ini</span>
      </div>
      <div class="summary-kpi-card">
        <span class="summary-kpi-label">Tingkat Kepercayaan</span>
        <span class="summary-kpi-value">${info.high_trust_pct ?? 0}%</span>
        <span class="summary-kpi-sub">${highCount} dari ${total} ulasan High Trust</span>
      </div>
      <div class="summary-kpi-card">
        <span class="summary-kpi-label">Aspek Dominan</span>
        <span class="summary-kpi-value summary-kpi-text">${dominant}</span>
        <span class="summary-kpi-sub">${dominantCount} dari ${total} ulasan</span>
      </div>
    </div>
    <div class="summary-chart-grid">
      <div class="summary-chart-card">
        <h4>Distribusi Aspek Komunikasi</h4>
        <p class="summary-chart-sub">dari ${total} ulasan</p>
        <div class="summary-chart-canvas"><canvas id="productAspectChart"></canvas></div>
      </div>
      <div class="summary-chart-card">
        <h4>Distribusi Sentimen Kepercayaan</h4>
        <p class="summary-chart-sub">dari ${total} ulasan</p>
        <div class="summary-chart-canvas"><canvas id="productTrustChart"></canvas></div>
      </div>
    </div>
  `;

  destroyProductSummaryCharts();
  const aspectColors = aspectEntries.map((_, i) => ASPECT_COLOR_PALETTE[i % ASPECT_COLOR_PALETTE.length]);
  const trustColors = trustEntries.map(([k]) => TRUST_LABEL_COLORS[k] || '#475569');
  productSummaryState.aspectChart = buildDoughnut('productAspectChart', aspectEntries, aspectColors, total);
  productSummaryState.trustChart = buildDoughnut('productTrustChart', trustEntries, trustColors, total);
  productSummaryState.lastProduct = info.product_name;
}

window.catalogSummary = { render: renderProductSummary, destroy: destroyProductSummaryCharts };
