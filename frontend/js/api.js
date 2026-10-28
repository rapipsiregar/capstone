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
    return { status: 'offline', version: '1.0.0', service: 'Halal Cosmetics NLP API' };
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
    // No stand-in numbers: the UI keeps its "–" placeholders when the API is unreachable.
    console.error('Error fetching brand analytics:', err);
    return null;
  }
}



async function fetchReviewHistory(limit = 25, page = 1) {
  try {
    const res = await fetch(`${API_BASE_URL}/history?limit=${limit}&page=${page}`);
    if (!res.ok) throw new Error('Failed to fetch history');
    return await res.json();
  } catch (err) {
    return {
      count: 3,
      logs: [
        {
          id: 1,
          raw_text: "Sertifikat halal produk Wardah ini jelas dan terdaftar BPOM resmi.",
          cleaned_text: "sertifikat halal produk wardah ini jelas dan terdaftar bpom resmi",
          predicted_aspect: "Sertifikasi_Halal_BPOM",
          aspect_confidence: 0.9619,
          predicted_trust: "High_Trust",
          trust_confidence: 0.8845,
          model_type: "IndoBERT Transformer",
          execution_time_ms: 12.45
        },
        {
          id: 2,
          raw_text: "Kandungan skincare tanpa paraben dan bahan kimia berbahaya.",
          cleaned_text: "kandungan skincare tanpa paraben dan bahan kimia berbahaya",
          predicted_aspect: "Kandungan_Bahan",
          aspect_confidence: 0.9210,
          predicted_trust: "High_Trust",
          trust_confidence: 0.7950,
          model_type: "IndoBERT Transformer",
          execution_time_ms: 11.20
        },
        {
          id: 3,
          raw_text: "Kemasan rusak dan seller tidak merespon chat sertifikasi.",
          cleaned_text: "kemasan rusak dan penjual tidak merespon chat sertifikasi",
          predicted_aspect: "Transparansi_Layanan",
          aspect_confidence: 0.8940,
          predicted_trust: "Low_Trust",
          trust_confidence: 0.8410,
          model_type: "IndoBERT Transformer",
          execution_time_ms: 12.50
        }
      ]
    };
  }
}

async function requestPrediction(text, modelChoice = 'indobert') {
  const res = await fetch(`${API_BASE_URL}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, model_choice: modelChoice })
  });
  return await res.json();
}

async function requestExplanation(text, modelChoice = 'indobert') {
  const res = await fetch(`${API_BASE_URL}/explain`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, model_choice: modelChoice })
  });
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

async function loadHomepageHeroStats() {
  const stats = await fetchCatalogStats();
  if (!stats) return;

  const elProds = document.getElementById('heroCountProducts');
  const elBrands = document.getElementById('heroCountBrands');
  const elReviews = document.getElementById('heroCountReviews');
  const elCompliance = document.getElementById('heroCountCompliance');

  if (elProds && stats.total_products) {
    elProds.textContent = Number(stats.total_products).toLocaleString('id-ID');
  }
  if (elBrands && stats.total_brands) {
    elBrands.textContent = Number(stats.total_brands).toLocaleString('id-ID');
  }
  if (elReviews && stats.total_reviews) {
    elReviews.textContent = Number(stats.total_reviews).toLocaleString('id-ID');
  }
  if (elCompliance && stats.halal_claimed_reviews !== undefined) {
    elCompliance.textContent = `${stats.halal_claimed_reviews} Halal & ${stats.bpom_claimed_reviews} BPOM`;
  }

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
  document.addEventListener('DOMContentLoaded', () => {
    loadHomepageHeroStats();
  });
}



