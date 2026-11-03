/**
 * CHARM V4 hash router.
 *   #/                                  -> Direktori Brand (facets in query: category, halal, bpom, rating, page)
 *   #/brand/products?brand={name}       -> Produk Brand
 *   #/product/detail?id={product name}  -> Detail Produk, Ulasan & XAI
 *   #/insight  #/metrics                -> Guidebook
 * Hash routing is used because the static frontend server has no SPA rewrite for real paths.
 */

const ROUTES = {
  '/': { view: 'directory', nav: 'catalog', wide: false },
  '/brand/products': { view: 'brand', nav: 'catalog', wide: false },
  '/product/detail': { view: 'detail', nav: 'catalog', wide: true },
  '/insight': { view: 'insight', nav: 'insight', wide: true, title: 'Insight Reputasi' },
  '/metrics': { view: 'metrics', nav: 'metrics', wide: true, title: 'Metrik Skripsi' }
};
const LEGACY_HASH = { katalog: '/', reputation: '/', insight: '/insight', metrics: '/metrics' };

window.charmViews = window.charmViews || {};
let lastRouteKey = null;

function parseHash() {
  const raw = (window.location.hash || '').replace(/^#/, '');
  if (LEGACY_HASH[raw.toLowerCase()]) return { path: LEGACY_HASH[raw.toLowerCase()], params: new URLSearchParams() };
  const [pathPart, queryPart = ''] = raw.split('?');
  const path = pathPart && pathPart.startsWith('/') ? pathPart.replace(/\/+$/, '') || '/' : '/';
  return { path: ROUTES[path] ? path : '/', params: new URLSearchParams(queryPart) };
}

/** Breadcrumb items: [{label, href?}]; the last item is the current page. */
function setCrumbs(items) {
  const nav = document.getElementById('crumbs');
  if (!nav) return;
  const { esc } = window.charmUI;
  nav.innerHTML = items.map((item, i) => {
    const last = i === items.length - 1;
    const sep = i ? '<span class="crumb-sep" aria-hidden="true">&rsaquo;</span>' : '';
    if (last) return `${sep}<span class="crumb-current" aria-current="page" title="${esc(item.label)}">${esc(item.label)}</span>`;
    return `${sep}<a href="${esc(item.href || '#/')}">${esc(item.label)}</a>`;
  }).join('');
  document.title = `${items[items.length - 1].label} | CHARM`;
}

function showRoute() {
  const { path, params } = parseHash();
  const route = ROUTES[path];
  const key = `${path}?${params.toString()}`;
  const viewChanged = !lastRouteKey || lastRouteKey.split('?')[0] !== path;
  lastRouteKey = key;

  document.querySelectorAll('.view').forEach(section => {
    const active = section.dataset.view === route.view;
    section.hidden = !active;
    if (active && section.parentElement) section.parentElement.prepend(section);
  });
  document.getElementById('frameBody')?.classList.toggle('is-wide', route.wide);
  document.querySelectorAll('.guide-nav a').forEach(a => {
    if (a.dataset.nav === route.nav) a.setAttribute('aria-current', 'page');
    else a.removeAttribute('aria-current');
  });

  if (route.title) setCrumbs([{ label: 'Katalog', href: '#/' }, { label: route.title }]);
  const view = window.charmViews[route.view];
  if (view && typeof view.render === 'function') view.render(params, { viewChanged });

  if (viewChanged) window.scrollTo({ top: 0 });
  setTimeout(() => window.dispatchEvent(new Event('resize')), 30);
}

function go(hash) {
  if (window.location.hash === hash) showRoute();
  else window.location.hash = hash;
}

window.addEventListener('hashchange', showRoute);
document.addEventListener('DOMContentLoaded', showRoute);
// A link to the route that is already open (e.g. "Coba lagi") reloads that view instead of doing nothing.
document.addEventListener('click', e => {
  const a = e.target.closest && e.target.closest('a[href^="#/"]');
  if (a && a.getAttribute('href') === window.location.hash) {
    e.preventDefault();
    lastRouteKey = null;
    showRoute();
  }
});

window.charmRouter = { go, setCrumbs, parseHash, showRoute };
