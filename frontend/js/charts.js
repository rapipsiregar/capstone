/**
 * CHARM charts (Chart.js). Colours follow DESIGN.md section 8:
 * one rose hue family for categories, status colours for trust, rose bars for model metrics.
 */
let aspectChartInstance = null;
let trustChartInstance = null;
let comparisonChartInstance = null;

const CHART_INK = '#3D2228';
const CHART_MUTED = '#75545A';
const ROSE_RAMP = ['#F5AFAF', '#E8959B', '#C9636F', '#A84A58', '#F9DFDF', '#D97D87'];
const TRUST_COLOURS = { High_Trust: '#1E6B47', Neutral: '#D4A62A', Low_Trust: '#A3262E' };
const TRUST_ORDER = ['High_Trust', 'Neutral', 'Low_Trust'];

function legendOptions(position = 'bottom') {
  return { position, labels: { color: CHART_INK, font: { family: 'Inter', size: 12 }, boxWidth: 12 } };
}

function countTooltip(total) {
  return {
    callbacks: {
      label: ctx => ` ${ctx.label}: ${Number(ctx.raw).toLocaleString('id-ID')} ulasan (${total ? ((ctx.raw / total) * 100).toFixed(1) : '0.0'}%)`
    }
  };
}

function renderAspectChart(aspectData) {
  const canvas = document.getElementById('aspectChart');
  if (!canvas || typeof Chart === 'undefined') return;
  const entries = Object.entries(aspectData || {}).sort((a, b) => b[1] - a[1]);
  const total = entries.reduce((s, [, v]) => s + v, 0);
  if (aspectChartInstance) aspectChartInstance.destroy();
  aspectChartInstance = new Chart(canvas.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: entries.map(([k]) => k.replace(/_/g, ' ')),
      datasets: [{ data: entries.map(([, v]) => v), backgroundColor: entries.map((_, i) => ROSE_RAMP[i % ROSE_RAMP.length]), borderColor: '#FFFFFF', borderWidth: 2 }]
    },
    options: { responsive: true, maintainAspectRatio: false, animation: false, cutout: '55%', plugins: { legend: legendOptions(), tooltip: countTooltip(total) } }
  });
}

function renderTrustChart(trustData) {
  const canvas = document.getElementById('trustChart');
  if (!canvas || typeof Chart === 'undefined') return;
  const data = trustData || {};
  const keys = [...TRUST_ORDER.filter(k => k in data), ...Object.keys(data).filter(k => !TRUST_ORDER.includes(k))];
  const total = keys.reduce((s, k) => s + data[k], 0);
  if (trustChartInstance) trustChartInstance.destroy();
  trustChartInstance = new Chart(canvas.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: keys.map(k => k.replace(/_/g, ' ')),
      datasets: [{ data: keys.map(k => data[k]), backgroundColor: keys.map(k => TRUST_COLOURS[k] || CHART_MUTED), borderColor: '#FFFFFF', borderWidth: 2 }]
    },
    options: { responsive: true, maintainAspectRatio: false, animation: false, cutout: '55%', plugins: { legend: legendOptions(), tooltip: countTooltip(total) } }
  });
}

async function renderComparisonChart(preloadedMetrics = null) {
  const canvas = document.getElementById('comparisonChart');
  if (!canvas || typeof Chart === 'undefined') return;
  let metrics = preloadedMetrics;
  if (!metrics && typeof fetchModelEvaluationMetrics === 'function') metrics = await fetchModelEvaluationMetrics();

  // Values come straight from /model/metrics (computed on test.csv); missing values stay at 0 and the legend says so.
  const values = [
    metrics?.trust_classifier?.accuracy ?? 0,
    metrics?.trust_classifier?.f1_macro ?? 0,
    metrics?.aspect_classifier?.accuracy ?? 0,
    metrics?.aspect_classifier?.f1_macro ?? 0
  ];
  const numSamples = metrics?.total_test_samples ?? null;
  const sampleEl = document.getElementById('metricsTestSampleCount');
  if (sampleEl && numSamples !== null) sampleEl.textContent = Number(numSamples).toLocaleString('id-ID');

  if (comparisonChartInstance) comparisonChartInstance.destroy();
  comparisonChartInstance = new Chart(canvas.getContext('2d'), {
    type: 'bar',
    data: {
      labels: ['Akurasi kepercayaan', 'Macro F1 kepercayaan', 'Akurasi aspek', 'Macro F1 aspek'],
      datasets: [{
        label: numSamples !== null ? `IndoBERT fine-tuned, ${numSamples} data uji (test.csv)` : 'Metrik belum termuat dari API',
        data: values,
        backgroundColor: '#F5AFAF',
        borderColor: '#A84A58',
        borderWidth: 1.5,
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      scales: {
        y: { beginAtZero: true, max: 1, grid: { color: '#F9DFDF' }, ticks: { color: CHART_MUTED, callback: v => `${Math.round(v * 100)}%` } },
        x: { grid: { display: false }, ticks: { color: CHART_INK, font: { family: 'Inter', weight: '600' } } }
      },
      plugins: {
        legend: legendOptions('top'),
        tooltip: { callbacks: { label: ctx => ` Skor: ${(ctx.raw * 100).toFixed(2)}%` } }
      }
    }
  });
}
