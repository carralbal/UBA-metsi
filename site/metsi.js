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

  const practiceBlocks = document.querySelector('[data-practice-blocks]');
  const practiceField = document.querySelector('[data-practice-field]');
  const practiceAtlas = document.querySelector('[data-practice-atlas]');
  const practiceDetail = document.querySelector('[data-practice-detail]');
  const practiceRadial = document.querySelector('[data-practice-radial]');
  const practiceSectors = document.querySelector('[data-practice-sectors]');
  const practiceAxes = document.querySelector('[data-practice-axes]');
  if (practiceBlocks && practiceField && practiceAtlas && practiceDetail && practiceRadial && practiceSectors && practiceAxes) {
    const practiceData = window.METSI_ATLAS.items;
    const blockMeta = window.METSI_ATLAS.blocks;
    const blockLabels = blockMeta.map((block) => block.label);
    const bandLabels = ['Experiencia y personas','Gestión y proceso','Diseño y arquitectura','Tecnología y operación'];
    const statusLabels = { central:'Concepto central', applied:'Aplicación relevante', contextual:'Referencia contextual' };
    let selectedBlock = 1;

    const makePracticeButton = (item, order) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = `practice-node ${item.status}`;
      button.dataset.practiceId = item.id;
      button.setAttribute('aria-label', `${item.label}. ${statusLabels[item.status]}. ${blockLabels[item.block - 1]}.`);
      button.style.setProperty('--node-order', order);
      const dot = document.createElement('i');
      dot.setAttribute('aria-hidden', 'true');
      const index = document.createElement('small');
      index.textContent = String(order + 1).padStart(2, '0');
      const label = document.createElement('span');
      label.textContent = item.label;
      button.append(index, dot, label);
      button.addEventListener('click', () => selectPractice(item));
      return button;
    };

    const selectPractice = (item) => {
      document.querySelectorAll('[data-practice-id]').forEach((node) => {
        const selected = node.dataset.practiceId === item.id;
        node.classList.toggle('is-selected', selected);
        node.setAttribute('aria-pressed', String(selected));
      });
      practiceDetail.dataset.status = item.status;
      practiceDetail.querySelector('[data-practice-status]').textContent = `${statusLabels[item.status]} · ${bandLabels[item.band - 1]}`;
      practiceDetail.querySelector('[data-practice-title]').textContent = item.label;
      practiceDetail.querySelector('[data-practice-description]').textContent = item.description;
      const list = practiceDetail.querySelector('[data-practice-documents]');
      practiceDetail.querySelector('.practice-detail-label').textContent = item.referenceLabel;
      list.replaceChildren(...item.refs.map(({code: n, section, page, href, title}) => {
        const li = document.createElement('li');
        if (href) {
          const link = document.createElement('a');
          link.href = href;
          link.textContent = `${n} · pág. ${page}`;
          link.target = '_blank';
          link.rel = 'noopener';
          link.setAttribute('aria-label', `Abrir ${n}: ${title}, ${section}, página ${page} (nueva pestaña)`);
          li.append(link);
        } else {
          const strong = document.createElement('strong');
          strong.textContent = n;
          li.append(strong);
        }
        li.append(document.createTextNode(` · ${section}`));
        return li;
      }));
    };

    const previewBlock = (block) => {
      practiceBlocks.querySelectorAll('[data-practice-block]').forEach((button) => {
        button.classList.toggle('is-active', Number(button.dataset.practiceBlock) === block);
      });
      practiceSectors.querySelectorAll('[data-practice-sector]').forEach((sector) => {
        sector.classList.toggle('is-active', Number(sector.dataset.practiceSector) === block);
      });

      const meta = blockMeta[block - 1];
      practiceAtlas.querySelector('[data-practice-block-letter]').textContent = String.fromCharCode(64 + block);
      practiceAtlas.querySelector('[data-practice-block-range]').textContent = meta.range;
      practiceAtlas.querySelector('[data-practice-block-title]').textContent = blockLabels[block - 1];
    };

    const selectBlock = (block) => {
      selectedBlock = block;
      practiceBlocks.querySelectorAll('[data-practice-block]').forEach((button) => {
        const selected = Number(button.dataset.practiceBlock) === block;
        button.classList.toggle('is-selected', selected);
        button.setAttribute('aria-selected', String(selected));
        button.tabIndex = selected ? 0 : -1;
      });
      previewBlock(block);

      const meta = blockMeta[block - 1];
      practiceAtlas.querySelector('[data-practice-block-claim]').textContent = meta.claim;
      practiceAtlas.querySelector('[data-practice-sheet-letter]').textContent = String.fromCharCode(64 + block);
      practiceAtlas.querySelector('[data-practice-sheet-range]').textContent = `${meta.range} · estación ${String(block).padStart(2, '0')}`;
      practiceAtlas.querySelector('[data-practice-sheet-title]').textContent = blockLabels[block - 1];

      const items = practiceData.filter((item) => item.block === block);
      const bands = bandLabels.flatMap((label, bandIndex) => {
        const bandItems = items.filter((item) => item.band === bandIndex + 1);
        if (!bandItems.length) return [];
        const section = document.createElement('section');
        section.className = 'practice-band';
        const heading = document.createElement('header');
        const bandNumber = document.createElement('span');
        bandNumber.textContent = String(bandIndex + 1).padStart(2, '0');
        const title = document.createElement('h5');
        title.textContent = label;
        heading.append(bandNumber, title);
        const nodes = document.createElement('div');
        nodes.className = 'practice-band-nodes';
        bandItems.forEach((item, order) => nodes.append(makePracticeButton(item, order)));
        section.append(heading, nodes);
        return [section];
      });
      practiceField.replaceChildren(...bands);
      selectPractice(items.find((item) => item.status === 'central') || items[0]);
    };

    const radialPoint = (radius, angle) => {
      const radians = (angle - 90) * Math.PI / 180;
      return [300 + radius * Math.cos(radians), 300 + radius * Math.sin(radians)];
    };
    const radialArc = (inner, outer, start, end) => {
      const [x1, y1] = radialPoint(outer, start);
      const [x2, y2] = radialPoint(outer, end);
      const [x3, y3] = radialPoint(inner, end);
      const [x4, y4] = radialPoint(inner, start);
      return `M ${x1} ${y1} A ${outer} ${outer} 0 0 1 ${x2} ${y2} L ${x3} ${y3} A ${inner} ${inner} 0 0 0 ${x4} ${y4} Z`;
    };

    blockLabels.forEach((label, index) => {
      const block = index + 1;
      const start = index * 45 + 2.2;
      const end = (index + 1) * 45 - 2.2;
      const sector = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      sector.classList.add('practice-radial-sector');
      sector.dataset.practiceSector = block;
      sector.setAttribute('d', radialArc(178, 238, start, end));
      sector.addEventListener('pointerenter', () => previewBlock(block));
      sector.addEventListener('click', () => selectBlock(block));
      practiceSectors.append(sector);

      const [axisX1, axisY1] = radialPoint(245, index * 45);
      const [axisX2, axisY2] = radialPoint(262, index * 45);
      const axis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      axis.classList.add('practice-radial-axis');
      axis.setAttribute('x1', axisX1);
      axis.setAttribute('y1', axisY1);
      axis.setAttribute('x2', axisX2);
      axis.setAttribute('y2', axisY2);
      practiceAxes.append(axis);

      const angle = index * 45 + 22.5;
      const [buttonX, buttonY] = radialPoint(270, angle);
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'practice-block';
      button.dataset.practiceBlock = block;
      button.setAttribute('role', 'tab');
      button.setAttribute('aria-label', `${String.fromCharCode(65 + index)}. ${label}. ${blockMeta[index].range}`);
      button.textContent = String.fromCharCode(65 + index);
      button.style.setProperty('--practice-left', `${buttonX / 6}%`);
      button.style.setProperty('--practice-top', `${buttonY / 6}%`);
      button.addEventListener('pointerenter', () => previewBlock(block));
      button.addEventListener('focus', () => previewBlock(block));
      button.addEventListener('click', () => selectBlock(block));
      button.addEventListener('keydown', (event) => {
        if (!['ArrowLeft','ArrowRight','Home','End'].includes(event.key)) return;
        event.preventDefault();
        let next = index;
        if (event.key === 'ArrowLeft') next = (index + 7) % 8;
        if (event.key === 'ArrowRight') next = (index + 1) % 8;
        if (event.key === 'Home') next = 0;
        if (event.key === 'End') next = 7;
        selectBlock(next + 1);
        practiceBlocks.children[next].focus();
      });
      practiceBlocks.append(button);
    });
    practiceRadial.addEventListener('pointerleave', () => previewBlock(selectedBlock));
    selectBlock(1);
  }

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const revealTargets = document.querySelectorAll('.value-grid, .case-thread, .rhythm, .anatomy-grid, .guide-card, .quality-grid, .practice-map');
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
