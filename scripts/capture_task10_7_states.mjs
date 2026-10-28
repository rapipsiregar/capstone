import { Browser, sleep } from '../.agents/skills/taste-skill/scripts/lib/cdp.mjs';
import { resolve } from 'node:path';

const ARTIFACT_DIR = 'C:/Users/rafif/.gemini/antigravity/brain/765091c6-444d-4ee4-8523-6c4c970c06e2';

async function run() {
  console.log('Launching browser via CDP...');
  const browser = await Browser.launch();
  try {
    const page = await browser.newPage({ width: 1280, height: 800 });
    console.log('Navigating to http://127.0.0.1:3000...');
    await page.goto('http://127.0.0.1:3000', { settleMs: 2000 });

    // 1. Screenshot: Level 1 Categories
    const pathL1 = resolve(ARTIFACT_DIR, 'task10_7_state_level1_categories.png');
    await page.screenshot({ path: pathL1, format: 'png' });
    console.log('Saved Level 1 Categories screenshot to', pathL1);

    // 2. Screenshot: Level 2 Empty State (trigger non-existent category)
    await page.eval(() => {
      catalogApp.openCategoryProducts('Kategori_Uji_Kosong', 1);
    });
    await sleep(1000);
    const pathL2Empty = resolve(ARTIFACT_DIR, 'task10_7_state_level2_empty.png');
    await page.screenshot({ path: pathL2Empty, format: 'png' });
    console.log('Saved Level 2 Empty State screenshot to', pathL2Empty);

    // 3. Screenshot: Level 2 Real Products
    await page.eval(() => {
      catalogApp.openCategoryProducts('Day Cream', 1);
    });
    await sleep(1500);
    const pathL2Loaded = resolve(ARTIFACT_DIR, 'task10_7_state_level2_loaded.png');
    await page.screenshot({ path: pathL2Loaded, format: 'png' });
    console.log('Saved Level 2 Loaded screenshot to', pathL2Loaded);

    // 4. Screenshot: Level 3 Reviews & XAI
    await page.eval(() => {
      const firstCard = document.querySelector('.catalog-product-card');
      if (firstCard) firstCard.click();
    });
    await sleep(1500);
    const pathL3Loaded = resolve(ARTIFACT_DIR, 'task10_7_state_level3_loaded.png');
    await page.screenshot({ path: pathL3Loaded, format: 'png' });
    console.log('Saved Level 3 Loaded screenshot to', pathL3Loaded);

    // 5. Screenshot: Level 3 Reviews Empty State
    await page.eval(() => {
      catalogApp.openProductReviews('Produk_Uji_Tanpa_Ulasan', 1);
    });
    await sleep(1000);
    const pathL3Empty = resolve(ARTIFACT_DIR, 'task10_7_state_level3_empty.png');
    await page.screenshot({ path: pathL3Empty, format: 'png' });
    console.log('Saved Level 3 Empty State screenshot to', pathL3Empty);

    // 6. Screenshot: Guidebook Tab 2 (Sandbox)
    await page.eval(() => {
      tabNavigation.switchToTab('tab-content-sandbox');
    });
    await sleep(1000);
    const pathTab2 = resolve(ARTIFACT_DIR, 'task10_7_state_tab2_sandbox.png');
    await page.screenshot({ path: pathTab2, format: 'png' });
    console.log('Saved Tab 2 Sandbox screenshot to', pathTab2);

    // 7. Screenshot: Guidebook Tab 3 (Metrics & History Table)
    await page.eval(() => {
      tabNavigation.switchToTab('tab-content-metrics');
    });
    await sleep(1500);
    const pathTab3 = resolve(ARTIFACT_DIR, 'task10_7_state_tab3_history.png');
    await page.screenshot({ path: pathTab3, format: 'png' });
    console.log('Saved Tab 3 History Table screenshot to', pathTab3);

    console.log('All states demonstrated and captured successfully!');
  } finally {
    await browser.close();
  }
}

run().catch(err => {
  console.error('Capture failed:', err);
  process.exit(1);
});

