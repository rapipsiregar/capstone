/**
 * Simulasi XAI controller: IndoBERT prediction + SHAP word attributions.
 * Shows "–" when the API omits a value instead of a made-up default.
 */

function bindSandboxEvents() {
  document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = document.getElementById('input-review-text');
      if (input) input.value = btn.getAttribute('data-sample') || '';
    });
  });

  document.getElementById('btn-analyze-review')?.addEventListener('click', async () => {
    const text = document.getElementById('input-review-text')?.value?.trim();
    const resultCard = document.getElementById('xai-result-card');
    const summary = document.getElementById('xai-summary-text');
    const tokens = document.getElementById('xai-highlighted-text');
    resultCard?.classList.remove('hidden');
    if (!text) {
      if (tokens) tokens.innerHTML = '';
      summary.textContent = 'Teks ulasan masih kosong. Ketik ulasan kosmetik atau pilih salah satu contoh di atas.';
      return;
    }
    summary.textContent = 'Memproses inferensi IndoBERT dan menghitung bobot SHAP...';

    try {
      const pred = await requestPrediction(text, 'indobert');
      const conf = typeof pred.trust_confidence === 'number' ? `${Math.round(pred.trust_confidence * 100)}%` : '–';
      const latency = typeof pred.execution_time_ms === 'number' ? `${pred.execution_time_ms} ms` : '–';
      const trustBadge = document.getElementById('xai-trust-badge');
      document.getElementById('xai-aspect-badge').textContent = (pred.predicted_aspect || '–').replace(/_/g, ' ');
      trustBadge.textContent = (pred.predicted_trust || '–').replace(/_/g, ' ');
      trustBadge.className = `pill ${pred.predicted_trust === 'High_Trust' ? 'pill-trust-high' : pred.predicted_trust === 'Low_Trust' ? 'pill-trust-low' : 'pill-trust-neutral'}`;
      document.getElementById('xai-confidence-val').textContent = conf;
      document.getElementById('xai-latency-val').textContent = latency;

      const explain = await requestExplanation(text, 'indobert');
      if (tokens && explain.word_attributions) {
        const { esc } = window.charmUI;
        tokens.innerHTML = explain.word_attributions.map(item => {
          const cls = item.impact === 'High_Trust' ? 'xai-token-green' : item.impact === 'Low_Trust' ? 'xai-token-red' : 'xai-token-yellow';
          const w = Number(item.weight);
          return `<span class="xai-token ${cls}" title="Bobot SHAP: ${w > 0 ? '+' : ''}${w.toFixed(3)}">${esc(item.word)}</span>`;
        }).join(' ');
      }
      summary.textContent = explain.summary || 'Analisis selesai.';
    } catch (e) {
      summary.textContent = `Gagal menganalisis ulasan (${e.message}). Pastikan server backend aktif di port 8000.`;
    }
  });
}
