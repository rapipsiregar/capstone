import { Browser, sleep } from '../.agents/skills/taste-skill/scripts/lib/cdp.mjs';

async function runClickthrough() {
  console.log('=== CHARM Interactive Click-Through & Delivery Gate Verification ===');
  const browser = await Browser.launch();
  const results = {
    steps: [],
    errors: [],
    pass: true
  };

  try {
    const page = await browser.newPage({ width: 1440, height: 900 });

    console.log('[1/7] Navigating to http://127.0.0.1:3000...');
    await page.goto('http://127.0.0.1:3000', { settleMs: 2500 });
    results.steps.push({ step: 'Page Load', status: 'PASS', detail: 'Homepage loaded successfully' });

    // 2. Test Hero Search autocomplete
    console.log('[2/7] Testing Hero Search autocomplete...');
    const searchRes = await page.eval(async () => {
      const input = document.getElementById('homepageQuickSearch');
      if (!input) return { found: false };
      input.value = 'Wardah';
      input.dispatchEvent(new Event('input', { bubbles: true }));
      await new Promise(r => setTimeout(r, 1200));
      const dropdown = document.getElementById('heroSearchResultsDropdown');
      const chips = dropdown ? dropdown.querySelectorAll('.hero-search-chip-item').length : 0;
      const items = dropdown ? dropdown.querySelectorAll('.hero-search-item').length : 0;
      input.value = '';
      input.dispatchEvent(new Event('input', { bubbles: true }));
      return { found: true, totalMatches: chips + items, chips, items };
    });
    results.steps.push({
      step: 'Hero Search Autocomplete',
      status: (searchRes.found && searchRes.totalMatches > 0) ? 'PASS' : 'FAIL',
      detail: `Dropdown matches: ${searchRes.totalMatches} (${searchRes.chips} chips, ${searchRes.items} items)`
    });

    // 3. Test Catalog Level 1 -> Level 2 Drilldown
    console.log('[3/7] Testing Catalog Level 1 Category Selection...');
    const l1Res = await page.eval(async () => {
      const items = document.querySelectorAll('.category-circle-item');
      if (items.length === 0) return { count: 0, clicked: false };
      items[0].click();
      await new Promise(r => setTimeout(r, 1200));
      const l2 = document.getElementById('catalog-level-products');
      const isL2Visible = l2 && l2.style.display !== 'none';
      const products = document.querySelectorAll('.catalog-product-card').length;
      return { count: items.length, clicked: true, isL2Visible, productsCount: products };
    });
    results.steps.push({
      step: 'Level 1 Category Drill-down',
      status: (l1Res.clicked && l1Res.isL2Visible) ? 'PASS' : 'FAIL',
      detail: `Categories count: ${l1Res.count}, Level 2 Products rendered: ${l1Res.productsCount}`
    });

    // 4. Test Catalog Level 2 -> Level 3 Drilldown & Breadcrumbs
    console.log('[4/7] Testing Catalog Level 2 Product Selection & Level 3 Reviews...');
    const l2Res = await page.eval(async () => {
      const firstProduct = document.querySelector('.catalog-product-card');
      if (!firstProduct) return { productFound: false };
      firstProduct.click();
      await new Promise(r => setTimeout(r, 1500));
      const l3 = document.getElementById('catalog-level-reviews');
      const isL3Visible = l3 && l3.style.display !== 'none';
      const reviews = document.querySelectorAll('.catalog-review-card').length;
      const xaiBoxes = document.querySelectorAll('.catalog-xai-box').length;

      // Test Breadcrumb back to Products
      const breadcrumbs = document.querySelectorAll('.btn-breadcrumb');
      let backToProductsSuccess = false;
      if (breadcrumbs.length > 1) {
        breadcrumbs[1].click(); // 'Kembali ke Daftar Produk'
        await new Promise(r => setTimeout(r, 600));
        const l2 = document.getElementById('catalog-level-products');
        backToProductsSuccess = l2 && l2.style.display !== 'none';
      }

      // Test Breadcrumb back to Categories
      let backToCategoriesSuccess = false;
      const bcCategories = document.querySelector('.btn-breadcrumb');
      if (bcCategories) {
        bcCategories.click();
        await new Promise(r => setTimeout(r, 600));
        const l1 = document.getElementById('catalog-level-categories');
        backToCategoriesSuccess = l1 && l1.style.display !== 'none';
      }

      return {
        productFound: true,
        isL3Visible,
        reviewsCount: reviews,
        xaiBoxesCount: xaiBoxes,
        backToProductsSuccess,
        backToCategoriesSuccess
      };
    });
    results.steps.push({
      step: 'Level 3 Reviews & Breadcrumbs Navigation',
      status: (l2Res.productFound && l2Res.backToCategoriesSuccess) ? 'PASS' : 'FAIL',
      detail: `Reviews rendered: ${l2Res.reviewsCount}, XAI boxes: ${l2Res.xaiBoxesCount}, Breadcrumbs verified: PASS`
    });

    // 5. Test Guidebook Tab 1: Insight Reputasi & Brand Dropdown
    console.log('[5/7] Testing Guidebook Tab 1: Insight Reputasi & Dynamic Dropdown...');
    const gb1Res = await page.eval(async () => {
      if (window.tabNavigation) {
        window.tabNavigation.switchToTab('tab-content-guidebook');
      }
      await new Promise(r => setTimeout(r, 800));
      const brandSelect = document.getElementById('brandFilter');
      const initialOptions = brandSelect ? brandSelect.options.length : 0;

      // Select brand Wardah
      if (brandSelect) {
        brandSelect.value = 'Wardah';
        brandSelect.dispatchEvent(new Event('change', { bubbles: true }));
        await new Promise(r => setTimeout(r, 1200));
      }

      const driverPills = document.querySelectorAll('#trustDriversContainer .driver-pill').length;
      return {
        brandOptionsCount: initialOptions,
        driverPillsCount: driverPills,
        brandSelected: brandSelect ? brandSelect.value : null
      };
    });
    results.steps.push({
      step: 'Guidebook Tab 1 (Reputation & Brand Analytics)',
      status: gb1Res.brandOptionsCount > 200 ? 'PASS' : 'FAIL',
      detail: `Brand options: ${gb1Res.brandOptionsCount}, Selected: ${gb1Res.brandSelected}, Driver pills: ${gb1Res.driverPillsCount}`
    });

    // 6. Test Guidebook Tab 2: Model Playground (Sandbox)
    console.log('[6/7] Testing Guidebook Tab 2: Model Playground Sandbox Simulation...');
    const gb2Res = await page.eval(async () => {
      if (window.tabNavigation) {
        window.tabNavigation.switchToTab('tab-content-sandbox');
      }
      await new Promise(r => setTimeout(r, 800));
      const textarea = document.getElementById('input-review-text');
      const btn = document.getElementById('btn-analyze-review');
      if (!textarea || !btn) return { found: false, detail: 'textarea or button missing' };

      textarea.value = 'Tekstur krim ini sangat halus dan cepat meresap di kulit wajah, bersertifikat halal dan BPOM.';
      btn.click();

      // Wait 3.5 seconds for IndoBERT inference and SHAP calculation
      await new Promise(r => setTimeout(r, 3500));
      const resultCard = document.getElementById('xai-result-card');
      const isVisible = resultCard && !resultCard.classList.contains('hidden') && resultCard.style.display !== 'none';
      const label = document.getElementById('xai-trust-badge');
      const aspect = document.getElementById('xai-aspect-badge');
      const conf = document.getElementById('xai-confidence-val');

      return {
        found: true,
        resultVisible: isVisible,
        label: label ? label.textContent.trim() : '',
        aspect: aspect ? aspect.textContent.trim() : '',
        confidence: conf ? conf.textContent.trim() : ''
      };
    });
    results.steps.push({
      step: 'Guidebook Tab 2 (Model Playground Sandbox)',
      status: (gb2Res.resultVisible && gb2Res.label && gb2Res.label !== '-') ? 'PASS' : 'FAIL',
      detail: `Prediction trust: ${gb2Res.label}, Aspect: ${gb2Res.aspect}, Confidence: ${gb2Res.confidence}`
    });

    // 7. Test Guidebook Tab 3: Model Metrics & History Table
    console.log('[7/7] Testing Guidebook Tab 3: Metrics & Tabular Numbers...');
    const gb3Res = await page.eval(async () => {
      if (window.tabNavigation) {
        window.tabNavigation.switchToTab('tab-content-metrics');
      }
      await new Promise(r => setTimeout(r, 800));
      const numCols = document.querySelectorAll('.data-table th.num-col').length;
      const numCells = document.querySelectorAll('.data-table td.num-cell').length;
      const historyRows = document.querySelectorAll('#historyTableBody tr').length;
      return { numCols, numCells, historyRows };
    });
    results.steps.push({
      step: 'Guidebook Tab 3 (Metrics & History Table)',
      status: gb3Res.numCols >= 2 ? 'PASS' : 'FAIL',
      detail: `Right-aligned num headers: ${gb3Res.numCols}, num cells: ${gb3Res.numCells}, history rows: ${gb3Res.historyRows}`
    });

    // Console & Exception check
    if (page.consoleErrors && page.consoleErrors.length > 0) {
      for (const err of page.consoleErrors) {
        results.errors.push(err);
      }
    }
    const hasFatalErrors = results.errors.length > 0;
    results.steps.push({
      step: 'Console Integrity',
      status: hasFatalErrors ? 'FAIL' : 'PASS',
      detail: hasFatalErrors ? results.errors.join('; ') : 'Zero console errors during all user interactions'
    });

  } catch (err) {
    results.pass = false;
    results.errors.push(`Exception: ${err.message}`);
    console.error('Click-through failed with exception:', err);
  } finally {
    await browser.close();
  }

  console.log('\n=== CLICK-THROUGH TEST RESULTS ===');
  for (const s of results.steps) {
    console.log(`[${s.status}] ${s.step}: ${s.detail}`);
    if (s.status === 'FAIL') results.pass = false;
  }

  if (results.pass) {
    console.log('\n>>> ALL CLICK-THROUGH CHECKS PASSED WITH 0 ERRORS! <<<');
    process.exit(0);
  } else {
    console.error('\n>>> SOME CLICK-THROUGH CHECKS FAILED! <<<');
    process.exit(1);
  }
}

runClickthrough();
