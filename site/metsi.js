(() => {
  const header = document.querySelector('[data-header]');
  const progress = document.createElement('div');
  const progressFill = document.createElement('span');
  progress.className = 'reading-progress';
  progress.setAttribute('aria-hidden', 'true');
  progress.append(progressFill);
  document.body.prepend(progress);

  const onScroll = () => {
    const top = window.scrollY;
    const max = document.documentElement.scrollHeight - window.innerHeight;
    if (header) header.classList.toggle('scrolled', top > 80);
    progressFill.style.width = `${max > 0 ? Math.min(100, (top / max) * 100) : 0}%`;
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  const menuToggle = document.querySelector('[data-menu-toggle]');
  const menu = document.querySelector('[data-menu]');
  const closeMenu = ({ restoreFocus = false } = {}) => {
    if (!header || !menuToggle || !menu) return;
    header.classList.remove('menu-open');
    menuToggle.setAttribute('aria-expanded', 'false');
    menuToggle.setAttribute('aria-label', 'Abrir menú');
    document.body.classList.remove('menu-is-open');
    if (restoreFocus) menuToggle.focus();
  };
  const openMenu = () => {
    if (!header || !menuToggle || !menu) return;
    header.classList.add('menu-open');
    menuToggle.setAttribute('aria-expanded', 'true');
    menuToggle.setAttribute('aria-label', 'Cerrar menú');
    document.body.classList.add('menu-is-open');
    menu.querySelector('a')?.focus();
  };
  if (menuToggle && menu) {
    menuToggle.addEventListener('click', () => {
      if (menuToggle.getAttribute('aria-expanded') === 'true') closeMenu();
      else openMenu();
    });
    menu.addEventListener('click', (event) => {
      if (event.target.closest('a')) closeMenu();
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && menuToggle.getAttribute('aria-expanded') === 'true') {
        closeMenu({ restoreFocus: true });
      }
    });
    document.addEventListener('click', (event) => {
      if (menuToggle.getAttribute('aria-expanded') === 'true' && !header.contains(event.target)) closeMenu();
    });
    window.addEventListener('resize', () => {
      if (window.innerWidth > 900) closeMenu();
    });
  }

  const tabs = [...document.querySelectorAll('[role="tab"]')];
  const panels = [...document.querySelectorAll('[role="tabpanel"]')];
  const activateTab = (tab) => {
    tabs.forEach((item) => {
      const selected = item === tab;
      item.setAttribute('aria-selected', String(selected));
      item.tabIndex = selected ? 0 : -1;
    });
    panels.forEach((panel) => { panel.hidden = panel.dataset.panel !== tab.dataset.tab; });
  };
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activateTab(tab));
    tab.addEventListener('keydown', (event) => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      let next = index;
      if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
      if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = tabs.length - 1;
      activateTab(tabs[next]);
      tabs[next].focus();
    });
  });

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const revealTargets = document.querySelectorAll('.value-grid, .case-thread, .rhythm, .anatomy-grid, .guide-card, .cover-library, .quality-grid');
  revealTargets.forEach((item) => item.setAttribute('data-reveal', ''));
  if (reduced || !('IntersectionObserver' in window)) {
    revealTargets.forEach((item) => item.classList.add('revealed'));
  } else {
    const revealObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('revealed');
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.12 });
    revealTargets.forEach((item) => revealObserver.observe(item));
  }

  const journeyItems = document.querySelectorAll('.journey-track li');
  if ('IntersectionObserver' in window) {
    const journeyObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => entry.target.classList.toggle('is-visible', entry.isIntersecting));
    }, { rootMargin: '-25% 0px -45% 0px', threshold: 0.1 });
    journeyItems.forEach((item) => journeyObserver.observe(item));
  }
})();
