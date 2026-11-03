/**
 * CHARM V4 UI kit: small shared helpers for the catalog views.
 * No data lives here; every number shown comes from the REST API (AGENTS.md 13).
 */

function charmApiBase() {
  if (typeof API_BASE_URL !== 'undefined') return API_BASE_URL;
  return `http://${window.location.hostname || '127.0.0.1'}:8000/api/v1`;
}

async function charmFetch(path) {
  const res = await fetch(`${charmApiBase()}${path}`);
  if (!res.ok) {
    const err = new Error(`HTTP ${res.status}`);
    err.status = res.status;
    throw err;
  }
  return res.json();
}

function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
}

function fmtNum(n) {
  return Number(n || 0).toLocaleString('id-ID');
}

function fmtRating(r) {
  return `${Number(r || 0).toFixed(1)}/5`;
}

function prettyLabel(key) {
  return String(key || '').replace(/_/g, ' ');
}

function brandHref(brand, extra = {}) {
  const q = new URLSearchParams({ brand, ...extra });
  return `#/brand/products?${q.toString()}`;
}

function productHref(product, brand) {
  const q = new URLSearchParams({ id: product });
  if (brand) q.set('brand', brand);
  return `#/product/detail?${q.toString()}`;
}

/** Packshot when the API confirmed the file exists, otherwise honest text (AGENTS.md 14). */
function photoHtml(photo, alt, cls = '') {
  if (photo) {
    return `<div class="photo-frame ${cls}"><img src="${esc(photo)}" alt="${esc(alt)}" loading="lazy"></div>`;
  }
  return `<div class="photo-frame ${cls}"><span class="photo-missing">Foto belum tersedia</span></div>`;
}

/** Claim pills from mention counts: the dataset records mentions in review text, not certificates. */
function claimPills(halalMentions, bpomMentions) {
  const out = [];
  if (halalMentions > 0) out.push(`<span class="pill pill-claim" title="Jumlah ulasan yang menyebut klaim halal">Halal disebut ${fmtNum(halalMentions)} ulasan</span>`);
  if (bpomMentions > 0) out.push(`<span class="pill pill-claim" title="Jumlah ulasan yang menyebut BPOM">BPOM disebut ${fmtNum(bpomMentions)} ulasan</span>`);
  return out.join('');
}

function trustPill(trust) {
  const map = {
    High_Trust: ['pill-trust-high', 'High Trust'],
    Low_Trust: ['pill-trust-low', 'Low Trust'],
    Neutral: ['pill-trust-neutral', 'Neutral']
  };
  const [cls, label] = map[trust] || map.Neutral;
  return `<span class="pill ${cls}">${label}</span>`;
}

/** Empty / loading / error box that names the cause and the next step (R-27). */
function stateBox(kind, title, desc, actionLabel = '', actionHref = '') {
  const action = actionLabel ? `<a class="btn btn-secondary" href="${esc(actionHref)}">${esc(actionLabel)}</a>` : '';
  const role = kind === 'error' ? 'alert' : 'status';
  return `<div class="state-box is-${kind}" role="${role}"><strong>${esc(title)}</strong><p>${esc(desc)}</p>${action}</div>`;
}

/** Previous / next pager. `hrefFor(page)` returns the route for that page. */
function pagerHtml(page, totalPages, hrefFor) {
  if (!totalPages || totalPages <= 1) return '';
  const prev = page > 1 ? `<a class="btn btn-secondary" href="${esc(hrefFor(page - 1))}">Sebelumnya</a>` : '';
  const next = page < totalPages ? `<a class="btn btn-secondary" href="${esc(hrefFor(page + 1))}">Berikutnya</a>` : '';
  return `${prev}<span>Halaman ${page} dari ${totalPages}</span>${next}`;
}

/** Builds a hash route from a path and a params object, dropping empty values. */
function routeWith(path, params) {
  const q = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '' && v !== false && !(Array.isArray(v) && !v.length)) {
      q.set(k, Array.isArray(v) ? v.join(',') : String(v));
    }
  });
  const qs = q.toString();
  return `#${path}${qs ? `?${qs}` : ''}`;
}

window.charmUI = {
  charmApiBase, charmFetch, esc, fmtNum, fmtRating, prettyLabel, brandHref, productHref,
  photoHtml, claimPills, trustPill, stateBox, pagerHtml, routeWith
};

