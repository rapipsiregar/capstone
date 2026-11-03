/**
 * Tab & Guidebook Navigation Module - CHARM Analytics
 * Manages clean centered header, URL hash routing, and refresh persistence:
 * 1. #reputation / #katalog -> tab-content-reputation (Homepage / Catalog & Analytics)
 * 2. #insight              -> tab-content-insight (Brand Reputation Analytics)
 * 3. #sandbox              -> tab-content-sandbox (XAI Simulation Playground)
 * 4. #metrics              -> tab-content-metrics (AI Model Evaluation & Thesis Metrics)
 */

const TAB_HASH_MAP = {
  'reputation': 'tab-content-reputation',
  'katalog': 'tab-content-reputation',
  'insight': 'tab-content-insight',
  'sandbox': 'tab-content-sandbox',
  'metrics': 'tab-content-metrics'
};

const PANEL_TO_HASH = {
  'tab-content-reputation': 'katalog',
  'tab-content-insight': 'insight',
  'tab-content-sandbox': 'sandbox',
  'tab-content-metrics': 'metrics'
};

function switchToTab(targetId, updateHash = true) {
  if (!targetId) return;

  const tabPanels = document.querySelectorAll('.tab-content-panel');
  const guidebookButtons = document.querySelectorAll('.btn-guidebook');
  const btnBackToHome = document.getElementById('btn-back-to-home');

  // Update panels
  tabPanels.forEach(panel => {
    if (panel.id === targetId) {
      panel.classList.add('active');
      panel.removeAttribute('hidden');
      panel.style.display = 'block';
    } else {
      panel.classList.remove('active');
      panel.setAttribute('hidden', 'true');
      panel.style.display = 'none';
    }
  });

  // Update guidebook button states
  guidebookButtons.forEach(btn => {
    if (btn.getAttribute('data-tab-target') === targetId) {
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');
    } else {
      btn.classList.remove('active');
      btn.setAttribute('aria-selected', 'false');
    }
  });

  // Control back to home button visibility in header
  if (btnBackToHome) {
    if (targetId === 'tab-content-reputation') {
      btnBackToHome.style.display = 'none';
    } else {
      btnBackToHome.style.display = 'inline-flex';
    }
  }

  // Persist state to URL Hash and sessionStorage
  const hashKey = PANEL_TO_HASH[targetId] || 'katalog';
  if (updateHash && window.location.hash.replace('#', '') !== hashKey) {
    history.pushState({ tab: targetId }, '', `#${hashKey}`);
  }
  try {
    sessionStorage.setItem('charm_active_tab', targetId);
  } catch (e) {
    // sessionStorage might be restricted in some iframe contexts
  }

  // Smooth scroll to top of main content
  window.scrollTo({ top: 0, behavior: 'smooth' });

  // If entering Insight Reputasi, ensure right sidebar analytics & charts are fresh
  if (targetId === 'tab-content-insight') {
    if (typeof renderRightSidebarAnalytics === 'function') {
      const brandVal = document.getElementById('brandFilter')?.value || 'ALL';
      renderRightSidebarAnalytics(brandVal);
    }
    if (typeof window.refreshCurrentAnalyticsCharts === 'function') {
      window.refreshCurrentAnalyticsCharts();
    }
  }

  // Refresh Chart.js dimensions and dynamic metrics if switching to insight or metrics
  setTimeout(() => {
    window.dispatchEvent(new Event('resize'));
    if (targetId === 'tab-content-insight' && typeof window.refreshCurrentAnalyticsCharts === 'function') {
      window.refreshCurrentAnalyticsCharts();
    }
    if (targetId === 'tab-content-metrics' && typeof renderComparisonChart === 'function') {
      renderComparisonChart();
    }
  }, 30);
}

function restoreTabFromHashOrStorage() {
  const currentHash = window.location.hash.replace('#', '').toLowerCase();
  let targetTabId = null;

  if (currentHash && TAB_HASH_MAP[currentHash]) {
    targetTabId = TAB_HASH_MAP[currentHash];
  } else {
    try {
      const stored = sessionStorage.getItem('charm_active_tab');
      if (stored && document.getElementById(stored)) {
        targetTabId = stored;
      }
    } catch (e) {
      // ignore
    }
  }

  if (targetTabId && targetTabId !== 'tab-content-reputation') {
    switchToTab(targetTabId, false);
  }
}

function initTabNavigation() {
  // Bind all buttons with data-tab-target
  document.querySelectorAll('[data-tab-target]').forEach(el => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = el.getAttribute('data-tab-target');
      switchToTab(targetId, true);
    });
  });

  // Handle browser back/forward buttons
  window.addEventListener('popstate', () => {
    const currentHash = window.location.hash.replace('#', '').toLowerCase();
    const targetId = TAB_HASH_MAP[currentHash] || 'tab-content-reputation';
    switchToTab(targetId, false);
  });

  // Restore on initial page load / refresh
  restoreTabFromHashOrStorage();

  // If page loads directly on #insight or #metrics, re-check charts after window loads
  window.addEventListener('load', () => {
    restoreTabFromHashOrStorage();
    if (typeof window.refreshCurrentAnalyticsCharts === 'function') {
      window.refreshCurrentAnalyticsCharts();
    }
  });

  // Expose to window for inline onclick handlers
  window.tabNavigation = {
    switchToTab,
    restoreTabFromHashOrStorage
  };
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initTabNavigation);
} else {
  initTabNavigation();
}
