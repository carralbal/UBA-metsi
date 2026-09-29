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

  // This preference personalizes a public site; it is not an access credential.
  const profileDialog = document.getElementById('profile-dialog');
  const profileSwitch = document.querySelector('[data-profile-switch]');
  if (profileDialog && profileSwitch && typeof profileDialog.showModal === 'function') {
    const storageKey = 'metsi.audience.v1';
    const profiles = {
      student: {
        label: 'Estudiante', shortLabel: 'Estudiante', tab: 'estudiantes', title: 'Llegá a clase con una idea propia.',
        intro: 'Empezá por la guía. Después elegí la lectura del encuentro y prepará tus preguntas.',
        deck: 'Vas a aprender a entender un problema antes de salir a resolverlo. Las lecturas, los ejemplos y el caso Hotel Horizonte te ayudan a preparar la clase y a probar tus propias decisiones.',
        actions: [['Empezar por N00','pdf/N00-METSI-lectura-previa-v3-final.pdf'],['Explorar las lecturas','#biblioteca'],['Cómo se aprende','#experiencia']],
        route: [['Prepará el próximo encuentro','La guía N00 explica cómo leer y qué llevar a clase.','pdf/N00-METSI-lectura-previa-v3-final.pdf'],['Elegí tu lectura','36 lecturas con explicaciones, ejemplos y ejercicios.','#biblioteca'],['Ubicá cada concepto','El atlas conecta las prácticas con secciones de las lecturas.','#atlas-practicas']]
      },
      teacher: {
        label: 'Docente', shortLabel: 'Docente', tab: 'docencia', title: 'Prepará el encuentro, no sólo la explicación.',
        intro: 'Conectá la lectura previa, el trabajo en clase y la evaluación. Los materiales docentes son públicos por ahora.',
        deck: 'Las lecturas preparan el encuentro para que haya más tiempo de discutir, resolver y revisar. Encontrá materiales y ejemplos para explicar de distintas maneras y acompañar las preguntas del grupo.',
        actions: [['Ver el piloto de clase N01','pdf/presentaciones/N01/'],['Preparar el encuentro','#experiencia'],['Consultar el programa','#programa']],
        route: [['Probá la presentación N01','Piloto de clase con videos y notas de orador en otra pestaña.','pdf/presentaciones/N01/'],['Diseñá el encuentro','Lectura previa, discusión del caso y aplicación en clase.','#experiencia'],['Conectá enseñanza y evaluación','Revisá los objetivos y los criterios del programa.','#programa']]
      },
      authority: {
        label: 'Autoridad académica', shortLabel: 'Autoridad', tab: 'carrera', title: 'Conocé el aporte de METSI a la carrera.',
        intro: 'Revisá qué aprende el estudiante, cómo se organiza el recorrido y qué fundamentos lo sostienen.',
        deck: 'METSI conecta la formación técnica con la investigación, el diseño y la gestión. El programa, las lecturas y los casos muestran cómo se construye el criterio para intervenir en problemas profesionales.',
        actions: [['Consultar el programa','#programa'],['Recorrer los ocho bloques','#mapa'],['Ver referentes','#referentes']],
        route: [['Revisá el programa','Propósitos, contenidos, carga y criterios de evaluación.','#programa'],['Recorré la arquitectura curricular','Ocho bloques que conectan los aprendizajes de la materia.','#mapa'],['Conocé el respaldo académico','Referentes argentinos, latinoamericanos y globales.','#referentes']]
      },
      visitor: {
        label: 'Me interesa la propuesta', shortLabel: 'Interés general', tab: 'catedra', title: 'Llevá estas preguntas a tu propio contexto.',
        intro: 'Si trabajás con tecnología, equipos u organizaciones, podés empezar por el enfoque y seguir por el tema que te interese.',
        deck: 'A veces el pedido llega como una solución: una app, un sistema nuevo, una herramienta de IA. METSI propone empezar antes: entender qué pasa, comparar alternativas y comprobar si el cambio sirve.',
        actions: [['Conocer la propuesta','#propuesta'],['Explorar las prácticas','#atlas-practicas'],['Elegir una lectura','#biblioteca']],
        route: [['Descubrí el enfoque','Qué significa entender el problema antes de elegir una solución.','#propuesta'],['Conectá prácticas y problemas','Marcos y herramientas según la decisión que ayudan a tomar.','#atlas-practicas'],['Elegí una lectura','Buscá un tema y probá sus preguntas en tu contexto.','#biblioteca']]
      }
    };
    const choices = [...profileDialog.querySelectorAll('[data-profile-choice]')];
    let selected = null;
    let opener = null;
    let lockedScroll = null;
    let choosing = false;
    const validProfile = key => Object.hasOwn(profiles, key);
    const setDestination = (link, href) => {
      link.href = href;
      if (!href.startsWith('#')) { link.target = '_blank'; link.rel = 'noopener'; }
      else { link.removeAttribute('target'); link.removeAttribute('rel'); }
    };
    const applyProfile = key => {
      if (!validProfile(key)) return;
      selected = key;
      const profile = profiles[key];
      document.body.dataset.audience = key;
      document.querySelector('.hero-deck').textContent = profile.deck;
      document.querySelectorAll('.hero-actions a').forEach((link, i) => {
        link.textContent = profile.actions[i][0];
        setDestination(link, profile.actions[i][1]);
      });
      document.querySelector('[data-profile-label]').textContent = `Tu recorrido · ${profile.label}`;
      document.getElementById('profile-route-title').textContent = profile.title;
      document.querySelector('[data-profile-intro]').textContent = profile.intro;
      const route = document.querySelector('[data-profile-route]');
      route.replaceChildren(...profile.route.map(([title, description, href]) => {
        const li = document.createElement('li');
        const link = document.createElement('a');
        const copy = document.createElement('span');
        const heading = document.createElement('strong');
        const detail = document.createElement('small');
        const arrow = document.createElement('span');
        heading.textContent = title; detail.textContent = description;
        arrow.className = href.startsWith('#') ? 'profile-arrow profile-arrow-down' : 'profile-arrow';
        arrow.setAttribute('aria-hidden','true');
        copy.append(heading, detail); link.append(copy, arrow);
        setDestination(link, href); li.append(link); return li;
      }));
      document.querySelector('.profile-route').hidden = false;
      choices.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.profileChoice === key)));
      profileSwitch.querySelector('[data-profile-current]').textContent = profile.label;
      profileSwitch.querySelector('[data-profile-current-short]').textContent = profile.shortLabel;
      profileSwitch.setAttribute('aria-label', `Perfil actual: ${profile.label}. Cambiar perfil`);
      const tab = tabs.find(item => item.dataset.tab === profile.tab);
      if (tab) activateTab(tab);
    };
    const unlockScroll = () => {
      if (!lockedScroll) return;
      const { x, y, style } = lockedScroll;
      Object.assign(document.body.style, style);
      lockedScroll = null;
      window.scrollTo({left:x, top:y, behavior:'instant'});
    };
    const openProfiles = () => {
      if (profileDialog.open || choosing) return;
      opener = selected ? document.activeElement : null;
      closeMenu();
      const style = {};
      for (const property of ['position','top','left','width']) style[property] = document.body.style[property];
      lockedScroll = {x:window.scrollX, y:window.scrollY, style};
      Object.assign(document.body.style, {position:'fixed', top:`-${lockedScroll.y}px`, left:'0', width:'100%'});
      profileDialog.showModal();
      document.getElementById('profile-dialog-title').focus({preventScroll:true});
    };
    profileDialog.addEventListener('cancel', event => event.preventDefault());
    profileDialog.addEventListener('keydown', event => {
      if (event.key !== 'Tab') return;
      const first = choices[0], last = choices[choices.length - 1];
      if (event.shiftKey && (document.activeElement === first || document.activeElement.id === 'profile-dialog-title')) {
        event.preventDefault(); last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault(); first.focus();
      }
    });
    profileDialog.addEventListener('close', unlockScroll);
    choices.forEach(button => button.addEventListener('click', async () => {
      if (choosing) return;
      choosing = true;
      applyProfile(button.dataset.profileChoice);
      try { localStorage.setItem(storageKey, selected); } catch { /* Session-only when storage is unavailable. */ }
      if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches && profileDialog.animate) {
        await profileDialog.animate([{opacity:1},{opacity:0}], {duration:160}).finished.catch(() => {});
      }
      profileDialog.close();
      unlockScroll();
      (opener?.isConnected ? opener : document.querySelector('.hero-actions a')).focus({preventScroll:true});
      choosing = false;
    }));
    profileSwitch.hidden = false;
    profileSwitch.addEventListener('click', openProfiles);
    let saved;
    try { saved = localStorage.getItem(storageKey); } catch { /* First visit without persistent storage. */ }
    if (validProfile(saved)) applyProfile(saved);
    else openProfiles();
  }

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

  const ambientVideos = [...document.querySelectorAll('.hero [data-ambient-video], .case-study [data-ambient-video], .closing [data-ambient-video]')];
  if (ambientVideos.length) {
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    const conserveData = () => Boolean(connection?.saveData || ['slow-2g','2g'].includes(connection?.effectiveType));
    const updateVideos = () => ambientVideos.forEach((video) => {
      const section = video.parentElement;
      const box = section.getBoundingClientRect();
      const visible = box.top < innerHeight * .82 && box.bottom > innerHeight * .18;
      if (document.hidden || motion.matches || conserveData() || !visible) {
        video.pause();
      } else {
        const source = video.querySelector('source');
        if (source?.dataset.src && !source.hasAttribute('src')) {
          source.src = source.dataset.src;
          video.load();
        }
        if (video.paused) video.play().catch(() => {});
      }
    });
    ambientVideos.forEach((video) => {
      const section = video.parentElement;
      video.addEventListener('playing', () => {
        video.classList.add('is-playing');
        section.classList.add('video-active');
      });
      const conceal = () => {
        video.classList.remove('is-playing');
        section.classList.remove('video-active');
      };
      video.addEventListener('pause', conceal);
      video.addEventListener('error', conceal);
    });
    motion.addEventListener?.('change', updateVideos);
    connection?.addEventListener?.('change', updateVideos);
    document.addEventListener('visibilitychange', updateVideos);
    window.addEventListener('scroll', updateVideos, {passive:true});
    window.addEventListener('resize', updateVideos);
    updateVideos();
  }
})();
