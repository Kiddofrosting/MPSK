/* ══════════════════════════════════════════════════════════
   MPSK Main JS v2.0
══════════════════════════════════════════════════════════ */

// ── Navbar scroll effect ──────────────────────────────────
const nav = document.getElementById('mainNav');
if (nav) window.addEventListener('scroll', () => nav.classList.toggle('scrolled', scrollY > 60), {passive:true});

// ── Fade-up intersection observer ────────────────────────
const observer = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
document.querySelectorAll('.fade-up, .fade-in').forEach(el => observer.observe(el));

// ── Counter animation ────────────────────────────────────
function animateCounter(el, target, suffix='') {
  const dur = 1800, step = 16, inc = target / (dur / step);
  let start = 0;
  const t = setInterval(() => {
    start += inc;
    if (start >= target) { el.textContent = target + suffix; clearInterval(t); return; }
    el.textContent = Math.floor(start) + suffix;
  }, step);
}
const cObserver = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (!e.isIntersecting) return;
    const el = e.target, raw = el.textContent.trim();
    const num = parseInt(raw.replace(/\D/g, ''));
    const suffix = raw.replace(/[\d,]/g, '');
    if (!isNaN(num)) animateCounter(el, num, suffix);
    cObserver.unobserve(el);
  });
}, { threshold: 0.5 });
document.querySelectorAll('.hero-stat-num, .stat-pill-number').forEach(el => cObserver.observe(el));

// ── Lightbox ─────────────────────────────────────────────
let lbImgs = [], lbIdx = 0;
function buildLightbox() {
  const imgs = [];
  document.querySelectorAll('[data-lightbox]').forEach(el => {
    imgs.push({ src: el.dataset.lightbox, cap: el.dataset.caption || '' });
    el.addEventListener('click', () => openLightbox(imgs, imgs.findIndex(i => i.src === el.dataset.lightbox)));
  });
  lbImgs = imgs;
}
function openLightbox(imgs, idx) {
  lbImgs = imgs; lbIdx = idx;
  const lb = document.getElementById('lightbox');
  if (!lb) return;
  lb.querySelector('.lightbox-img').src = imgs[idx].src;
  lb.querySelector('.lightbox-caption').textContent = imgs[idx].cap;
  lb.classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeLightbox() {
  const lb = document.getElementById('lightbox');
  if (lb) { lb.classList.remove('open'); document.body.style.overflow = ''; }
}
function lightboxNav(dir) {
  lbIdx = (lbIdx + dir + lbImgs.length) % lbImgs.length;
  const lb = document.getElementById('lightbox');
  if (lb) {
    lb.querySelector('.lightbox-img').src = lbImgs[lbIdx].src;
    lb.querySelector('.lightbox-caption').textContent = lbImgs[lbIdx].cap;
  }
}
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeLightbox();
  if (e.key === 'ArrowLeft') lightboxNav(-1);
  if (e.key === 'ArrowRight') lightboxNav(1);
});
document.addEventListener('DOMContentLoaded', buildLightbox);

// ── Gallery filter ────────────────────────────────────────
function filterGallery(cat) {
  document.querySelectorAll('.filter-pill, .gallery-filter-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.cat === cat);
  });
  document.querySelectorAll('[data-cat-item]').forEach(item => {
    const match = cat === 'all' || item.dataset.catItem === cat;
    item.style.display = match ? '' : 'none';
    item.style.opacity = match ? '' : '0';
  });
}

// ── Toast ─────────────────────────────────────────────────
function showToast(message, type = 'success') {
  const t = document.createElement('div');
  t.className = `alert alert-${type} position-fixed shadow-lg`;
  t.style.cssText = 'top:80px;right:20px;z-index:9999;min-width:290px;border-radius:12px;animation:fadeIn .3s ease';
  t.innerHTML = `<div style="display:flex;align-items:center;gap:10px"><i class="bi bi-${type==='success'?'check-circle-fill':'exclamation-circle-fill'}"></i><span>${message}</span><button type="button" class="btn-close ms-auto" style="padding:0"></button></div>`;
  t.querySelector('.btn-close').onclick = () => t.remove();
  document.body.appendChild(t);
  setTimeout(() => { t.style.opacity='0'; t.style.transition='opacity .3s'; setTimeout(()=>t.remove(), 300); }, 4500);
}

// ── AJAX form helper ──────────────────────────────────────
async function submitForm(url, data) {
  const res = await fetch(url, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(data) });
  return res.json();
}

// ── Delete helper ─────────────────────────────────────────
async function deleteItem(url, rowId) {
  if (!confirm('Delete this item? This cannot be undone.')) return;
  try {
    const res = await fetch(url, { method:'POST' });
    const data = await res.json();
    if (data.success) {
      const row = document.getElementById(rowId);
      if (row) { row.style.opacity='0'; row.style.transition='opacity .3s'; setTimeout(()=>row.remove(), 300); }
      showToast('Deleted successfully.', 'success');
    } else showToast(data.message||'Failed.', 'danger');
  } catch { showToast('Network error.', 'danger'); }
}

// ── Newsletter form ───────────────────────────────────────
async function footerSubscribe() {
  const email = document.getElementById('footerNlEmail')?.value;
  if (!email) return;
  try {
    const d = await submitForm('/api/newsletter', {email});
    showToast(d.message, d.success ? 'success' : 'danger');
    if (d.success) document.getElementById('footerNlEmail').value = '';
  } catch { showToast('Something went wrong.', 'danger'); }
}

// ── Hero image slideshow ──────────────────────────────────
(function() {
  const bgEl = document.querySelector('.hero-bg-img');
  if (!bgEl || !bgEl.dataset.images) return;
  const imgs = JSON.parse(bgEl.dataset.images);
  if (imgs.length < 2) return;
  let idx = 0;
  setInterval(() => {
    idx = (idx + 1) % imgs.length;
    bgEl.style.opacity = '0';
    setTimeout(() => {
      bgEl.style.backgroundImage = `url('${imgs[idx]}')`;
      bgEl.style.opacity = '.22';
    }, 600);
  }, 6000);
})();

// ── Scroll cue ────────────────────────────────────────────
document.querySelector('.hero-scroll-cue')?.addEventListener('click', () => {
  document.querySelector('.ticker-wrap, section:not(.hero-section)')?.scrollIntoView({behavior:'smooth'});
});
