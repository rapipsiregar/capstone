/**
 * CHARM charts & evaluation tables (Chart.js + Solusi C per-class evaluation & confusion matrix).
 * Colours follow DESIGN.md section 8: rose hue family for categories, status colours for trust.
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
  const labelFn = window.charmUI?.aspectLabel || (k => k.replace(/_/g, ' '));
  if (aspectChartInstance) aspectChartInstance.destroy();
  aspectChartInstance = new Chart(canvas.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: entries.map(([k]) => labelFn(k)),
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

function renderPerClassMetrics(metrics) {
  const tbody = document.getElementById('perClassMetricsBody');
  const cmGrid = document.getElementById('confusionMatrixGrid');
  if (!tbody) return;
  const { esc, fmtNum, aspectLabel } = window.charmUI;
  if (!metrics || (!metrics.trust_classifier && !metrics.aspect_classifier)) {
    tbody.innerHTML = '<tr><td colspan="6" class="text-center"><div class="state-box is-error" role="alert"><strong>Metrik evaluasi tidak dapat dimuat</strong><p>Server API di port 8000 belum merespons.</p></div></td></tr>';
    if (cmGrid) cmGrid.innerHTML = '<span class="muted">Confusion matrix belum dapat dimuat dari API.</span>';
    return;
  }

  const pct = v => `${(Number(v || 0) * 100).toFixed(2)}%`;
  const rows = [];
  const addGroup = (modelTitle, clf, isAspect) => {
    const report = clf?.classification_report || {};
    (clf?.labels || []).forEach(label => {
      const r = report[label];
      if (!r) return;
      const displayLabel = isAspect ? aspectLabel(label) : label.replace(/_/g, ' ');
      rows.push(`
        <tr>
          <td><strong>${esc(modelTitle)}</strong></td>
          <td><span class="pill">${esc(displayLabel)}</span></td>
          <td class="num-cell">${pct(r.precision)}</td>
          <td class="num-cell">${pct(r.recall)}</td>
          <td class="num-cell"><strong>${pct(r['f1-score'])}</strong></td>
          <td class="num-cell">${fmtNum(Math.round(r.support || 0))}</td>
        </tr>`);
    });
  };
  addGroup('IndoBERT Kepercayaan', metrics.trust_classifier, false);
  addGroup('IndoBERT Aspek Komunikasi', metrics.aspect_classifier, true);
  tbody.innerHTML = rows.join('');

  if (cmGrid) {
    const buildMatrix = (title, clf, isAspect) => {
      const labels = (clf?.labels || []).map(l => isAspect ? aspectLabel(l) : l.replace(/_/g, ' '));
      const matrix = clf?.confusion_matrix || [];
      return `
        <div class="cm-card">
          <h3>${esc(title)} (Total ${fmtNum(clf?.num_samples || 0)} sampel)</h3>
          <div class="table-wrapper">
            <table class="data-table cm-table">
              <thead><tr><th>Aktual \\ Prediksi</th>${labels.map(l => `<th class="num-col">${esc(l)}</th>`).join('')}</tr></thead>
              <tbody>
                ${matrix.map((row, i) => `
                  <tr>
                    <td><strong>${esc(labels[i] || '')}</strong></td>
                    ${row.map((val, j) => `<td class="num-cell ${i === j ? 'cm-diag' : ''}">${fmtNum(val)}</td>`).join('')}
                  </tr>`).join('')}
              </tbody>
            </table>
          </div>
        </div>`;
    };
    cmGrid.innerHTML = buildMatrix('Confusion Matrix Kepercayaan (3×3)', metrics.trust_classifier, false) +
      buildMatrix('Confusion Matrix Aspek Komunikasi (4×4)', metrics.aspect_classifier, true);
  }
}

async function renderComparisonChart(preloadedMetrics = null) {
  const canvas = document.getElementById('comparisonChart');
  if (!canvas || typeof Chart === 'undefined') return;
  let metrics = preloadedMetrics;
  if (!metrics && typeof fetchModelEvaluationMetrics === 'function') metrics = await fetchModelEvaluationMetrics();

  renderPerClassMetrics(metrics);

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
