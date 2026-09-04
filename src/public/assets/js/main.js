/* ============================================================
   codexrelic.com — Core JavaScript
   ============================================================ */

/* ── Theme: init before paint to prevent flash ── */
(function () {
  const stored = localStorage.getItem('cr-theme');
  const preferred = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', stored || preferred);
})();

/* ── Main Init ── */
document.addEventListener('DOMContentLoaded', () => {

  /* Theme Toggle */
  const toggle = document.getElementById('theme-toggle');
  const root   = document.documentElement;

  function getTheme() {
    return root.getAttribute('data-theme') || 'dark';
  }

  function setTheme(theme) {
    root.setAttribute('data-theme', theme);
    localStorage.setItem('cr-theme', theme);
    if (toggle) {
      const label = toggle.querySelector('.toggle-label');
      const icon  = toggle.querySelector('.toggle-icon');
      if (label) label.textContent = theme === 'dark' ? 'Light mode' : 'Dark mode';
      if (icon)  icon.innerHTML    = theme === 'dark' ? sunIcon() : moonIcon();
    }
    // Swap brand logo source dynamically
    document.querySelectorAll('.sidebar-brand img, img.brand-logo').forEach(img => {
      const src = img.getAttribute('src');
      if (src) {
        const baseDir = src.substring(0, src.lastIndexOf('/') + 1);
        img.setAttribute('src', baseDir + (theme === 'dark' ? 'logo-dark.png' : 'logo-light.png'));
      }
    });
  }

  if (toggle) {
    toggle.addEventListener('click', () => {
      setTheme(getTheme() === 'dark' ? 'light' : 'dark');
    });
    // Sync label on load
    setTheme(getTheme());
  }

  /* Palette Selector */
  const swatches = document.querySelectorAll('.palette-swatch');
  const savedPalette = localStorage.getItem('cr-palette') || 'default';
  
  swatches.forEach(swatch => {
    if (swatch.dataset.palette === savedPalette) {
      swatch.classList.add('active');
    } else {
      swatch.classList.remove('active');
    }
    
    swatch.addEventListener('click', () => {
      const pal = swatch.dataset.palette;
      document.documentElement.setAttribute('data-palette', pal);
      localStorage.setItem('cr-palette', pal);
      swatches.forEach(s => s.classList.remove('active'));
      swatch.classList.add('active');
    });
  });

  /* Active Nav Link */
  const path = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-link, .mobile-nav-item').forEach(link => {
    const href = (link.getAttribute('href') || '').split('/').pop();
    if (href === path || (path === '' && (href === 'index.html' || href === ''))) {
      link.classList.add('active');
    }
  });

  /* Scroll Reveal */
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

  /* Blog / Events category filter */
  const filterBtns  = document.querySelectorAll('.filter-btn');
  const filterItems = document.querySelectorAll('[data-category]');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const filter = btn.dataset.filter;
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      filterItems.forEach(item => {
        item.style.display =
          (filter === 'all' || item.dataset.category === filter) ? '' : 'none';
      });
    });
  });

  /* Role rotator (hero page) */
  const roles = document.querySelectorAll('.hero-role');
  if (roles.length > 1) {
    let idx = 0;
    setInterval(() => {
      roles[idx].classList.remove('active');
      idx = (idx + 1) % roles.length;
      roles[idx].classList.add('active');
    }, 2600);
  }

  /* CVE Security News Ticker */
  fetch('/api/cve-news')
    .then(response => response.json())
    .then(data => {
      if (data && data.length > 0) {
        const tickerContainer = document.createElement('div');
        tickerContainer.className = 'cve-ticker';
        
        const label = document.createElement('div');
        label.className = 'cve-ticker-label';
        label.innerHTML = '<span class="pulse-dot"></span> CVE FEED';
        tickerContainer.appendChild(label);

        const contentWrap = document.createElement('div');
        contentWrap.className = 'cve-ticker-wrap';

        const content = document.createElement('div');
        content.className = 'cve-ticker-content';

        data.forEach(item => {
          const alertLink = document.createElement('a');
          alertLink.href = item.link;
          alertLink.target = '_blank';
          alertLink.className = 'cve-ticker-item';
          alertLink.innerHTML = `<span class="cve-ticker-icon">⚠️</span> <span class="cve-ticker-title">${item.title}</span>`;
          content.appendChild(alertLink);
        });

        // Clone for infinite scroll effect
        contentWrap.appendChild(content);
        const clone = content.cloneNode(true);
        contentWrap.appendChild(clone);

        tickerContainer.appendChild(contentWrap);
        
        // Append to layout or body
        const mainEl = document.querySelector('.main') || document.body;
        mainEl.appendChild(tickerContainer);
      }
    })
    .catch(err => console.error('Error loading CVE news:', err));

});

/* ── SVG helpers ── */
function sunIcon() {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/>
    <line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/>
    <line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
  </svg>`;
}

function moonIcon() {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
  </svg>`;
}
