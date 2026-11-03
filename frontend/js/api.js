/**
 * CHARM API client. No stand-in numbers: when the API is unreachable the UI keeps its "–"
 * placeholders or shows an honest error state (AGENTS.md 12, findings F27).
 */
const BACKEND_TUNNEL_URL = 'https://few-words-invent.loca.lt/api/v1';
const host = window.location.hostname || '127.0.0.1';
const normalizedHost = (host === 'localhost') ? '127.0.0.1' : host;
const API_BASE_URL = (host.includes('loca.lt') || window.location.protocol === 'https:')
  ? BACKEND_TUNNEL_URL
  : `http://${normalizedHost}:8000/api/v1`;

async function fetchHealthStatus() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (!res.ok) throw new Error('API Offline');
    return await res.json();
  } catch (err) {
    return { status: 'offline' };
  }
}

async function fetchBrandAnalytics(brand = null, category = null) {
  try {
    const params = new URLSearchParams();
    if (brand && brand !== 'ALL') params.append('brand', brand);
    if (category && category !== 'ALL') params.append('category', category);
    const qs = params.toString() ? `?${params.toString()}` : '';
    const res = await fetch(`${API_BASE_URL}/analytics/brands${qs}`);
    if (!res.ok) throw new Error('Failed to fetch brand analytics');
    return await res.json();
  } catch (err) {
    console.error('Error fetching brand analytics:', err);
    return null;
  }
}

/** Inference log. Offline returns an empty list flagged `offline` (no invented rows). */
async function fetchReviewHistory(limit = 25, page = 1) {
  try {
    const res = await fetch(`${API_BASE_URL}/history?limit=${limit}&page=${page}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return { count: 0, total: 0, logs: [], offline: true, error: err.message };
  }
}

async function requestPrediction(text, modelChoice = 'indobert') {
  const res = await fetch(`${API_BASE_URL}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, model_choice: modelChoice })
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

async function requestExplanation(text, modelChoice = 'indobert') {
  const res = await fetch(`${API_BASE_URL}/explain`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, model_choice: modelChoice })
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

async function fetchModelEvaluationMetrics() {
  try {
    const res = await fetch(`${API_BASE_URL}/model/metrics`);
    if (!res.ok) throw new Error('Failed to fetch model metrics');
    return await res.json();
  } catch (err) {
    console.error('Error fetching model evaluation metrics:', err);
    return null;
  }
}

async function fetchCatalogStats() {
  try {
    const res = await fetch(`${API_BASE_URL}/catalog/stats`);
    if (!res.ok) throw new Error('Failed to fetch catalog stats');
    return await res.json();
  } catch (err) {
    console.error('Error fetching catalog stats:', err);
    return null;
  }
}

/** Fills the dataset counts on the Metrik Skripsi page from /catalog/stats. */
async function loadDatasetStats() {
  const stats = await fetchCatalogStats();
  if (!stats) return;
  const fmt = (n) => Number(n).toLocaleString('id-ID');
  const setText = (id, value) => {
    const el = document.getElementById(id);
    if (el && value !== undefined && value !== null) el.textContent = value;
  };
  setText('metricsDatasetReviewCount', stats.total_reviews && fmt(stats.total_reviews));
  setText('metricsDatasetBrandCount', stats.total_brands && fmt(stats.total_brands));
  setText('metricsDatasetProductCount', stats.total_products && fmt(stats.total_products));
  setText('complianceInfoReviewCount', stats.total_reviews && fmt(stats.total_reviews));

  const split = stats.split_counts;
  if (split) {
    const total = split.train + split.val + split.test;
    const pct = (n) => (total ? ` (${Math.round((n / total) * 100)}%)` : '');
    setText('metricsSplitTotal', fmt(total));
    setText('metricsSplitTrain', fmt(split.train) + pct(split.train));
    setText('metricsSplitVal', fmt(split.val) + pct(split.val));
    setText('metricsSplitTest', fmt(split.test) + pct(split.test));
  }
}

if (typeof document !== 'undefined') {
  document.addEventListener('DOMContentLoaded', loadDatasetStats);
}
