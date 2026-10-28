/**
 * Interactive XAI Sandbox Playground Controller
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
    if (!text) {
      if (resultCard) {
        resultCard.classList.remove('hidden');
        document.getElementById('xai-summary-text').textContent = 'Teks ulasan masih kosong. Ketik teks ulasan kosmetik atau pilih salah satu contoh preset di atas untuk menganalisis.';
      }
      return;
    }
    const model = 'indobert';
    resultCard?.classList.remove('hidden');
    document.getElementById('xai-summary-text').textContent = 'Memproses inferensi model IndoBERT dan menghitung bobot SHAP...';

    try {
      const pred = await requestPrediction(text, model);
      document.getElementById('xai-aspect-badge').textContent = (pred.predicted_aspect || 'Aspek').replace(/_/g, ' ');
      document.getElementById('xai-trust-badge').textContent = (pred.predicted_trust || 'Kepercayaan').replace(/_/g, ' ');
      document.getElementById('xai-confidence-val').textContent = `${Math.round((pred.trust_confidence || 0.95) * 100)}%`;
      document.getElementById('xai-latency-val').textContent = `${pred.execution_time_ms || 12} ms`;

      const explain = await requestExplanation(text, model);
      const container = document.getElementById('xai-highlighted-text');
      if (container && explain.word_attributions) {
        container.innerHTML = explain.word_attributions.map(item => {
          const colorClass = item.impact === 'High_Trust' ? 'xai-token-green' : item.impact === 'Low_Trust' ? 'xai-token-red' : 'xai-token-yellow';
          return `<span class="xai-token ${colorClass}" title="Bobot SHAP: ${item.weight > 0 ? '+' : ''}${item.weight.toFixed(3)}">${item.word}</span>`;
        }).join(' ');
      }
      document.getElementById('xai-summary-text').textContent = explain.summary || 'Analisis selesai.';
    } catch (e) {
      document.getElementById('xai-summary-text').textContent = `Gagal menganalisis ulasan: ${e.message}. Pastikan server backend aktif di port 8000.`;
    }
  });
}
