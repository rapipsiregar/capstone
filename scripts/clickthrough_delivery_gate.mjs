import { Browser } from '../.agents/skills/taste-skill/scripts/lib/cdp.mjs';

async function runClickthrough() {
  console.log('=== CHARM V4 Interactive Click-Through & Delivery Gate Verification ===');
  const browser = await Browser.launch();
  const results = { steps: [], errors: [], pass: true };

  try {
    const page = await browser.newPage({ width: 1440, height: 900 });

    console.log('[1/7] Loading V4 Brand Directory (http://127.0.0.1:3000/#/)...');
    await page.goto('http://127.0.0.1:3000/#/', { settleMs: 2500 });
    const dirCheck = await page.eval(() => ({
      cards: document.querySelectorAll('#brandGrid .brand-card').length,
      categories: document.querySelectorAll('#facetPanel input[data-category]').length,
      brandOpts: document.getElementById('facetBrand')?.options?.length || 0
    }));
    results.steps.push({
      step: 'Level 1 Brand Directory & Faceted Filter',
      status: (dirCheck.cards > 0 && dirCheck.categories > 0 && dirCheck.brandOpts > 200) ? 'PASS' : 'FAIL',
      detail: `Brand cards: ${dirCheck.cards}, Category checkboxes: ${dirCheck.categories}, Brand options: ${dirCheck.brandOpts}`
    });

    console.log('[2/7] Testing Header Quick Search autocomplete...');
    const searchRes = await page.eval(async () => {
      const input = document.getElementById('headerSearch');
      if (!input) return { found: false, totalMatches: 0 };
      input.value = 'Wardah';
      input.dispatchEvent(new Event('input', { bubbles: true }));
      await new Promise(r => setTimeout(r, 900));
      const dropdown = document.getElementById('searchResults');
      const items = dropdown ? dropdown.querySelectorAll('.search-item').length : 0;
      input.value = '';
      input.dispatchEvent(new Event('input', { bubbles: true }));
      return { found: true, totalMatches: items };
    });
    results.steps.push({
      step: 'Header Search Autocomplete',
      status: (searchRes.found && searchRes.totalMatches > 0) ? 'PASS' : 'FAIL',
      detail: `Dropdown matches for 'Wardah': ${searchRes.totalMatches}`
    });

    console.log('[3/7] Testing Level 1 -> Level 2 Brand Products Drilldown...');
    const l2Res = await page.eval(async () => {
      const card = document.querySelector('#brandGrid .brand-card');
      if (!card) return { clicked: false };
      card.click();
      await new Promise(r => setTimeout(r, 1500));
      const viewVisible = !document.querySelector('[data-view="brand"]')?.hidden;
      const products = document.querySelectorAll('#productGrid .product-card').length;
      const summaryName = document.querySelector('#brandBanner h1')?.textContent?.trim() || '';
      return { clicked: true, viewVisible, productsCount: products, summaryName };
    });
    results.steps.push({
      step: 'Level 2 Brand Products View',
      status: (l2Res.clicked && l2Res.viewVisible && l2Res.productsCount > 0) ? 'PASS' : 'FAIL',
      detail: `Brand: ${l2Res.summaryName}, Products rendered: ${l2Res.productsCount}`
    });

    console.log('[4/7] Testing Level 2 -> Level 3 Product Detail Dossier & SHAP Reviews...');
    const l3Res = await page.eval(async () => {
      const firstProduct = document.querySelector('#productGrid .product-card');
      if (!firstProduct) return { productFound: false };
      firstProduct.click();
      await new Promise(r => setTimeout(r, 1800));
      const viewVisible = !document.querySelector('[data-view="detail"]')?.hidden;
      const title = document.querySelector('#productDossier h1')?.textContent?.trim() || '';
      const reviews = document.querySelectorAll('#reviewFeed .review-card').length;
      const shapMarks = document.querySelectorAll('#reviewFeed .xai-highlight-green, #reviewFeed .xai-highlight-red').length;
      const bcRoot = document.querySelector('#crumbs a[href="#/"]');
      if (bcRoot) bcRoot.click();
      await new Promise(r => setTimeout(r, 1000));
      const backToDir = !document.querySelector('[data-view="directory"]')?.hidden;
      return { productFound: true, viewVisible, title, reviews, shapMarks, backToDir };
    });
    results.steps.push({
      step: 'Level 3 Product Detail Dossier, SHAP Reviews & Breadcrumb',
      status: (l3Res.productFound && l3Res.viewVisible && l3Res.reviews > 0 && l3Res.backToDir) ? 'PASS' : 'FAIL',
      detail: `Product: ${l3Res.title}, Reviews: ${l3Res.reviews}, SHAP highlights: ${l3Res.shapMarks}, Breadcrumb back: ${l3Res.backToDir}`
    });

    console.log('[5/7] Testing Guidebook 1: Insight Reputasi (#/insight)...');
    await page.eval(async () => { window.location.hash = '#/insight'; await new Promise(r => setTimeout(r, 1200)); });
    const gb1Res = await page.eval(async () => {
      const brandSelect = document.getElementById('brandFilter');
      const initialOptions = brandSelect ? brandSelect.options.length : 0;
      if (brandSelect) {
        brandSelect.value = 'Wardah';
        brandSelect.dispatchEvent(new Event('change', { bubbles: true }));
        await new Promise(r => setTimeout(r, 1200));
      }
      const driverPills = document.querySelectorAll('#highTrustDriversList .badge, #lowTrustDriversList .badge').length;
      const factorRows = document.querySelectorAll('#trustFactorMapList .meter-row').length;
      return { brandOptionsCount: initialOptions, driverPillsCount: driverPills, factorRows };
    });
    results.steps.push({
      step: 'Guidebook 1 (Insight Reputasi & Brand Analytics)',
      status: (gb1Res.brandOptionsCount > 200 && gb1Res.driverPillsCount > 0 && gb1Res.factorRows > 0) ? 'PASS' : 'FAIL',
      detail: `Brand options: ${gb1Res.brandOptionsCount}, Driver pills: ${gb1Res.driverPillsCount}, Factor map rows: ${gb1Res.factorRows}`
    });

    console.log('[6/6] Testing Guidebook 2: Metrik Skripsi (#/metrics)...');
    await page.eval(async () => { window.location.hash = '#/metrics'; await new Promise(r => setTimeout(r, 1200)); });
    const gb3Res = await page.eval(() => ({
      chartPresent: !!document.getElementById('comparisonChart'),
      testSamples: document.getElementById('metricsTestSampleCount')?.textContent?.trim() || '',
      totalSplit: document.getElementById('metricsSplitTotal')?.textContent?.trim() || ''
    }));
    results.steps.push({
      step: 'Guidebook 2 (Metrik Skripsi)',
      status: (gb3Res.chartPresent && gb3Res.totalSplit !== '–' && gb3Res.testSamples !== '–') ? 'PASS' : 'FAIL',
      detail: `Split total: ${gb3Res.totalSplit}, Test samples: ${gb3Res.testSamples}, Chart present: ${gb3Res.chartPresent}`
    });

    if (page.consoleErrors?.length) results.errors.push(...page.consoleErrors);
    results.steps.push({
      step: 'Console Integrity',
      status: results.errors.length ? 'FAIL' : 'PASS',
      detail: results.errors.length ? results.errors.join('; ') : 'Zero console errors during all user interactions'
    });
  } catch (err) {
    results.pass = false;
    results.errors.push(`Exception: ${err.message}`);
  } finally {
    await browser.close();
  }

  console.log('\n=== CLICK-THROUGH TEST RESULTS ===');
  for (const s of results.steps) {
    console.log(`[${s.status}] ${s.step}: ${s.detail}`);
    if (s.status === 'FAIL') results.pass = false;
  }
  process.exit(results.pass ? 0 : 1);
}

runClickthrough();
