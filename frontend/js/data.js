/**
 * CHARM - Halal Cosmetics Analytics Platform
 * Dynamic Data Loader & Architecture
 *
 * All dataset benchmark statistics, brand drivers, and product metrics
 * are loaded dynamically from authentic backend REST APIs:
 * - GET /api/v1/analytics/brands (Dynamic Trust & Empirical SHAP Drivers)
 * - GET /api/v1/catalog/stats (Live Review, Product, Brand, & Compliance Counts)
 * - GET /api/v1/catalog/categories & /api/v1/catalog/products
 * - GET /api/v1/model/metrics (Empirical IndoBERT Evaluation Results)
 *
 * Static benchmark data was deprecated in Task 11.3.
 */

// Global namespace placeholder for backward compatibility
window.CHARM_DATA = {
  isDynamic: true,
  source: "API"
};
