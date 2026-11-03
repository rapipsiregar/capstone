/**
 * Riwayat inferensi table (Metrik Skripsi): 25 rows per page from GET /history.
 */

let currentHistoryPage = 1;
const HISTORY_PAGE_SIZE = 25;

function historyRow(log) {
  const { esc } = window.charmUI;
  const trustCls = log.predicted_trust === 'High_Trust' ? 'badge-green' : log.predicted_trust === 'Low_Trust' ? 'badge-red' : 'badge-amber';
  const conf = typeof log.trust_confidence === 'number' ? `${(log.trust_confidence * 100).toFixed(1)}%` : '–';
  const latency = typeof log.execution_time_ms === 'number' ? `${log.execution_time_ms} ms` : '–';
  return `
    <tr>
      <td><strong>#${esc(log.id)}</strong></td>
      <td class="cell-text" title="${esc(log.raw_text)}">${esc(log.raw_text)}</td>
      <td><span class="badge badge-blue">${esc((log.predicted_aspect || '').replace(/_/g, ' '))}</span></td>
      <td><span class="badge ${trustCls}">${esc((log.predicted_trust || '').replace(/_/g, ' '))}</span></td>
      <td class="num-cell">${conf}</td>
      <td>${esc(log.model_type || '–')}</td>
      <td class="num-cell">${latency}</td>
    </tr>`;
}

async function renderHistoryWithPagination(page = 1) {
  currentHistoryPage = page;
  const tbody = document.getElementById('historyTableBody');
  if (!tbody) return;

  const data = await fetchReviewHistory(HISTORY_PAGE_SIZE, currentHistoryPage);
  const logs = data.logs || [];
  const totalCount = data.total || logs.length;
  const totalPages = data.total_pages || Math.max(1, Math.ceil(totalCount / HISTORY_PAGE_SIZE));

  if (data.offline) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center"><div class="state-box is-error" role="alert"><strong>Riwayat inferensi tidak dapat dimuat (${window.charmUI.esc(data.error)})</strong><p>Server FastAPI di port 8000 tidak merespons. Jalankan backend lalu tekan Muat ulang riwayat.</p></div></td></tr>`;
    updatePaginationControls(0, 0, 1, 1);
    return;
  }
  if (!logs.length) {
    tbody.innerHTML = '<tr><td colspan="7" class="text-center"><div class="state-box" role="status"><strong>Belum ada log inferensi tersimpan</strong><p>Ulasan yang diproses lewat endpoint API akan tercatat di sini.</p><a class="btn btn-secondary" href="#/">Buka direktori brand</a></div></td></tr>';
    updatePaginationControls(0, 0, 1, 1);
    return;
  }
  tbody.innerHTML = logs.map(historyRow).join('');
  updatePaginationControls(logs.length, totalCount, currentHistoryPage, totalPages);
}

function updatePaginationControls(pageCount, totalCount, page, totalPages) {
  const startIdx = totalCount === 0 ? 0 : (page - 1) * HISTORY_PAGE_SIZE + 1;
  const endIdx = totalCount === 0 ? 0 : Math.min(startIdx + pageCount - 1, totalCount);
  const info = document.getElementById('paginationInfoText');
  if (info) info.textContent = `Menampilkan ${startIdx}–${endIdx} dari ${totalCount} log · halaman ${page} dari ${totalPages}`;

  const prev = document.getElementById('btnPrevPage');
  const next = document.getElementById('btnNextPage');
  if (prev) prev.disabled = page <= 1;
  if (next) next.disabled = page >= totalPages;

  const numbers = document.getElementById('pageNumberButtons');
  if (!numbers) return;
  const first = Math.max(1, page - 2);
  const last = Math.min(totalPages, first + 4);
  let html = '';
  for (let i = first; i <= last; i++) {
    html += `<button type="button" class="btn ${i === page ? 'btn-primary' : 'btn-secondary'} page-num-btn" data-page="${i}" ${i === page ? 'aria-current="page"' : ''}>${i}</button>`;
  }
  numbers.innerHTML = html;
  numbers.querySelectorAll('.page-num-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const target = parseInt(btn.getAttribute('data-page'), 10);
      if (target && target !== currentHistoryPage) renderHistoryWithPagination(target);
    });
  });
}

function bindPaginationEvents() {
  document.getElementById('btnPrevPage')?.addEventListener('click', () => {
    if (currentHistoryPage > 1) renderHistoryWithPagination(currentHistoryPage - 1);
  });
  document.getElementById('btnNextPage')?.addEventListener('click', () => renderHistoryWithPagination(currentHistoryPage + 1));
}
