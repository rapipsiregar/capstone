/**
 * Pagination & History Table Controller
 * Handles 25 items per page navigation for review inference logs
 */

let currentHistoryPage = 1;
const HISTORY_PAGE_SIZE = 25;

async function renderHistoryWithPagination(page = 1) {
  currentHistoryPage = page;
  const tbody = document.getElementById('historyTableBody');
  if (!tbody) return;

  try {
    const data = await fetchReviewHistory(HISTORY_PAGE_SIZE, currentHistoryPage);
    const logs = data.logs || [];
    const totalCount = data.total || logs.length;
    const totalPages = data.total_pages || Math.max(1, Math.ceil(totalCount / HISTORY_PAGE_SIZE));

    if (logs.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center" style="padding: 1.5rem; color: var(--text-muted);">Belum ada riwayat ulasan pada halaman ini.</td></tr>';
      updatePaginationControls(0, 0, 1, 1);
      return;
    }

    tbody.innerHTML = logs.map(log => `
      <tr>
        <td><strong>#${log.id}</strong></td>
        <td style="max-width: 280px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${log.raw_text}">${log.raw_text}</td>
        <td><span class="badge badge-blue">${(log.predicted_aspect || '').replace(/_/g, ' ')}</span></td>
        <td><span class="badge ${log.predicted_trust === 'High_Trust' ? 'badge-green' : log.predicted_trust === 'Low_Trust' ? 'badge-red' : 'badge-amber'}">${(log.predicted_trust || '').replace(/_/g, ' ')}</span></td>
        <td>${((log.trust_confidence || 0.9) * 100).toFixed(1)}%</td>
        <td>${log.model_type}</td>
        <td>${log.execution_time_ms} ms</td>
      </tr>
    `).join('');

    updatePaginationControls(logs.length, totalCount, currentHistoryPage, totalPages);
  } catch (err) {
    console.error('Error loading paginated history:', err);
    tbody.innerHTML = '<tr><td colspan="7" class="text-center" style="color: var(--danger-color);">Gagal memuat data riwayat ulasan.</td></tr>';
  }
}

function updatePaginationControls(pageCount, totalCount, page, totalPages) {
  const startIdx = totalCount === 0 ? 0 : (page - 1) * HISTORY_PAGE_SIZE + 1;
  const endIdx = totalCount === 0 ? 0 : Math.min(startIdx + pageCount - 1, totalCount);

  const infoElem = document.getElementById('paginationInfoText');
  if (infoElem) {
    infoElem.innerHTML = `Menampilkan <strong>${startIdx} - ${endIdx}</strong> dari total <strong>${totalCount}</strong> ulasan &nbsp;·&nbsp; (Halaman <strong>${page}</strong> dari <strong>${totalPages}</strong>)`;
  }

  const prevBtn = document.getElementById('btnPrevPage');
  const nextBtn = document.getElementById('btnNextPage');
  if (prevBtn) prevBtn.disabled = page <= 1;
  if (nextBtn) nextBtn.disabled = page >= totalPages;

  const pageNumbersContainer = document.getElementById('pageNumberButtons');
  if (pageNumbersContainer) {
    let html = '';
    for (let i = 1; i <= totalPages; i++) {
      const activeClass = i === page ? 'btn-primary' : 'btn-secondary';
      html += `<button class="btn ${activeClass} page-num-btn" data-page="${i}" style="padding: 0.25rem 0.65rem; font-size: 0.82rem; min-width: 32px;">${i}</button>`;
    }
    pageNumbersContainer.innerHTML = html;

    pageNumbersContainer.querySelectorAll('.page-num-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const targetPage = parseInt(btn.getAttribute('data-page'));
        if (targetPage && targetPage !== currentHistoryPage) {
          renderHistoryWithPagination(targetPage);
        }
      });
    });
  }
}

function bindPaginationEvents() {
  document.getElementById('btnPrevPage')?.addEventListener('click', () => {
    if (currentHistoryPage > 1) {
      renderHistoryWithPagination(currentHistoryPage - 1);
    }
  });

  document.getElementById('btnNextPage')?.addEventListener('click', () => {
    renderHistoryWithPagination(currentHistoryPage + 1);
  });
}
