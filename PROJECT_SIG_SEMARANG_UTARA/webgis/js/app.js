/* ==========================================================================
   SEMARANG FLOOD & ROB GIS — SHARED INTERACTION LAYER
   v3.0
   ========================================================================== */
(function () {
  'use strict';

  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ------------------------------------------------------------------ */
  /* 1. Sticky navigation + scroll progress                              */
  /* ------------------------------------------------------------------ */
  const nav = $('#siteNav');
  const progress = $('#scrollProgress');

  const onScroll = () => {
    const y = window.scrollY || document.documentElement.scrollTop;
    if (nav) nav.classList.toggle('is-scrolled', y > 12);
    if (progress) {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      progress.style.width = max > 0 ? `${Math.min(100, (y / max) * 100)}%` : '0%';
    }
    const backTop = $('#backToTop');
    if (backTop) backTop.classList.toggle('is-visible', y > 520);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ------------------------------------------------------------------ */
  /* 2. Active nav item (path-aware)                                     */
  /* ------------------------------------------------------------------ */
  const currentPage = location.pathname.split('/').pop() || 'index.html';
  $$('.site-nav-links .nav-link').forEach(link => {
    const href = (link.getAttribute('href') || '').split('#')[0];
    if (!href) return;
    if (href === currentPage || (currentPage === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });

  /* ------------------------------------------------------------------ */
  /* 3. Reveal-on-scroll                                                 */
  /* ------------------------------------------------------------------ */
  const revealItems = $$('.reveal');
  if (revealItems.length) {
    if (reduceMotion || !('IntersectionObserver' in window)) {
      revealItems.forEach(el => el.classList.add('is-visible'));
    } else {
      document.body.classList.add('reveal-ready');
      const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
      revealItems.forEach(el => observer.observe(el));
    }
  }

  /* ------------------------------------------------------------------ */
  /* 4. Animated counters                                                */
  /* ------------------------------------------------------------------ */
  const counters = $$('[data-count]');
  const animateCounter = el => {
    const target = parseFloat(el.dataset.count);
    if (!Number.isFinite(target)) return;
    const decimals = parseInt(el.dataset.decimals || '0', 10);
    const prefix = el.dataset.prefix || '';
    const suffix = el.dataset.suffix || '';
    const duration = reduceMotion ? 0 : 1100;
    const start = performance.now();
    const format = value => prefix + value.toLocaleString('id-ID', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }) + suffix;

    const tick = now => {
      const t = duration === 0 ? 1 : Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3);
      el.textContent = format(target * eased);
      if (t < 1) requestAnimationFrame(tick);
      else el.textContent = format(target);
    };
    requestAnimationFrame(tick);
    // Guarantee the exact final value even if animation frames are throttled
    setTimeout(() => { el.textContent = format(target); }, duration + 250);
  };

  if (counters.length) {
    if (!('IntersectionObserver' in window)) {
      counters.forEach(animateCounter);
    } else {
      const countObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            animateCounter(entry.target);
            countObserver.unobserve(entry.target);
          }
        });
      }, { threshold: 0.35 });
      counters.forEach(el => countObserver.observe(el));
    }
  }

  /* ------------------------------------------------------------------ */
  /* 5. Back to top                                                      */
  /* ------------------------------------------------------------------ */
  const backTop = $('#backToTop');
  if (backTop) {
    backTop.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
    });
  }

  /* ------------------------------------------------------------------ */
  /* 6. Mobile nav auto-close                                            */
  /* ------------------------------------------------------------------ */
  const navMenu = $('#siteNavMenu');
  $$('#siteNavMenu .nav-link, #siteNavMenu .nav-cta').forEach(link => {
    link.addEventListener('click', () => {
      if (navMenu && navMenu.classList.contains('show') && window.bootstrap) {
        bootstrap.Collapse.getOrCreateInstance(navMenu).hide();
      }
    });
  });

  /* ------------------------------------------------------------------ */
  /* 7. Quick navigation / command palette                               */
  /* ------------------------------------------------------------------ */
  const quickItems = [
    { title: 'Beranda', desc: 'Ringkasan risiko & peta utama', href: 'index.html', icon: 'fa-house' },
    { title: 'Peta WebGIS', desc: 'Eksplorasi 7 layer spasial interaktif', href: 'map.html', icon: 'fa-map-location-dot' },
    { title: 'Dashboard Statistik', desc: 'KPI, grafik, dan peringkat kelurahan', href: 'dashboard.html', icon: 'fa-chart-pie' },
    { title: 'Analisis Spasial', desc: 'Buffer, overlay, matriks & rekomendasi', href: 'analysis.html', icon: 'fa-layer-group' },
    { title: 'Metodologi', desc: 'Metode, unduhan, dan tim pengembang', href: 'methodology.html', icon: 'fa-circle-info' },
    { title: 'Tim Pengembang', desc: 'Profil anggota & pembagian tugas', href: 'methodology.html#team', icon: 'fa-users-gear' },
    { title: 'Pusat Unduhan', desc: 'Laporan, peta, GeoPackage, presentasi', href: 'methodology.html#downloadCenter', icon: 'fa-download' },
    { title: 'Pertanyaan Spasial', desc: '4 jawaban analisis utama', href: 'index.html#pertanyaan-spasial', icon: 'fa-clipboard-question' }
  ];

  let palette = null;
  let paletteInput = null;
  let paletteList = null;
  let highlighted = 0;

  const renderPalette = query => {
    if (!paletteList) return;
    const q = (query || '').toLowerCase().trim();
    const filtered = quickItems.filter(item =>
      !q || `${item.title} ${item.desc}`.toLowerCase().includes(q)
    );
    highlighted = 0;
    if (!filtered.length) {
      paletteList.innerHTML = '<div class="quick-nav-empty"><i class="fa-solid fa-magnifying-glass me-2"></i>Tidak ada halaman yang cocok.</div>';
      return;
    }
    paletteList.innerHTML = filtered.map((item, index) => `
      <a class="quick-nav-item${index === 0 ? ' is-highlighted' : ''}" href="${item.href}" data-index="${index}">
        <i class="fa-solid ${item.icon}"></i>
        <span><strong>${item.title}</strong><small>${item.desc}</small></span>
      </a>
    `).join('');
  };

  const openPalette = () => {
    if (!palette) {
      palette = document.createElement('div');
      palette.className = 'quick-nav';
      palette.id = 'quickNav';
      palette.innerHTML = `
        <div class="quick-nav-dialog" role="dialog" aria-modal="true" aria-label="Navigasi cepat">
          <div class="quick-nav-search">
            <i class="fa-solid fa-magnifying-glass"></i>
            <input type="text" id="quickNavInput" placeholder="Cari halaman, fitur, atau data..." autocomplete="off" aria-label="Cari halaman">
            <kbd>ESC</kbd>
          </div>
          <div class="quick-nav-list" id="quickNavList"></div>
        </div>`;
      document.body.appendChild(palette);
      paletteInput = $('#quickNavInput', palette);
      paletteList = $('#quickNavList', palette);

      palette.addEventListener('click', event => {
        if (event.target === palette) closePalette();
      });
      paletteInput.addEventListener('input', () => renderPalette(paletteInput.value));
      paletteInput.addEventListener('keydown', event => {
        const items = $$('.quick-nav-item', paletteList);
        if (!items.length) return;
        if (event.key === 'ArrowDown') {
          event.preventDefault();
          highlighted = (highlighted + 1) % items.length;
        } else if (event.key === 'ArrowUp') {
          event.preventDefault();
          highlighted = (highlighted - 1 + items.length) % items.length;
        } else if (event.key === 'Enter') {
          event.preventDefault();
          items[highlighted].click();
          return;
        } else {
          return;
        }
        items.forEach((item, index) => item.classList.toggle('is-highlighted', index === highlighted));
        items[highlighted].scrollIntoView({ block: 'nearest' });
      });
    }
    renderPalette('');
    palette.classList.add('is-open');
    document.body.style.overflow = 'hidden';
    setTimeout(() => paletteInput && paletteInput.focus(), 30);
  };

  const closePalette = () => {
    if (!palette) return;
    palette.classList.remove('is-open');
    document.body.style.overflow = '';
  };

  const quickBtn = $('#quickNavBtn');
  if (quickBtn) quickBtn.addEventListener('click', openPalette);

  document.addEventListener('keydown', event => {
    const isTyping = /input|textarea|select/i.test(document.activeElement.tagName);
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      openPalette();
    } else if (event.key === '/' && !isTyping) {
      event.preventDefault();
      openPalette();
    } else if (event.key === 'Escape') {
      closePalette();
    }
  });

  /* ------------------------------------------------------------------ */
  /* 8. Toast helper                                                     */
  /* ------------------------------------------------------------------ */
  const ensureToastStack = () => {
    let stack = $('#toastStack');
    if (!stack) {
      stack = document.createElement('div');
      stack.className = 'toast-stack';
      stack.id = 'toastStack';
      stack.setAttribute('aria-live', 'polite');
      document.body.appendChild(stack);
    }
    return stack;
  };

  window.appToast = (message, icon = 'fa-circle-check', duration = 3200) => {
    const stack = ensureToastStack();
    const toast = document.createElement('div');
    toast.className = 'app-toast';
    toast.innerHTML = `<i class="fa-solid ${icon}"></i><span>${message}</span>`;
    stack.appendChild(toast);
    setTimeout(() => {
      toast.classList.add('is-leaving');
      setTimeout(() => toast.remove(), 260);
    }, duration);
  };

  document.addEventListener('click', event => {
    const link = event.target.closest('[data-download-toast]');
    if (!link) return;
    window.appToast(link.dataset.downloadToast || 'Unduhan dimulai.', 'fa-download');
  });

  /* ------------------------------------------------------------------ */
  /* 9. Footer year                                                      */
  /* ------------------------------------------------------------------ */
  $$('[data-year]').forEach(el => { el.textContent = new Date().getFullYear(); });

  /* ------------------------------------------------------------------ */
  /* 10. Subtle pointer glow on cards (desktop only)                     */
  /* ------------------------------------------------------------------ */
  if (!reduceMotion && window.matchMedia('(pointer: fine)').matches) {
    $$('.stat-card, .question-card, .download-card, .team-mini-card').forEach(card => {
      card.addEventListener('pointermove', event => {
        const rect = card.getBoundingClientRect();
        card.style.setProperty('--mx', `${((event.clientX - rect.left) / rect.width) * 100}%`);
        card.style.setProperty('--my', `${((event.clientY - rect.top) / rect.height) * 100}%`);
      });
    });
  }
})();
