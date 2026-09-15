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

  const practiceMap = document.querySelector('[data-practice-map]');
  const practiceMobile = document.querySelector('[data-practice-mobile]');
  const practiceDetail = document.querySelector('[data-practice-detail]');
  if (practiceMap && practiceMobile && practiceDetail) {
    const practiceData = [
      { id:'stakeholders', label:'Gestión de stakeholders', block:1, band:1, status:'central', size:3, dx:-38, dy:-34, description:'Identifica quién decide, quién hace el trabajo, quién recibe el efecto y quién queda sin voz.', refs:[['N05','Actores, poder, exposición, voz y reparación'],['N07','Entrevistas y episodios'],['N20','Autoridad y estrategia'],['N35','Comunicación y transferencia']] },
      { id:'risk', label:'Gestión de riesgos', block:1, band:2, status:'applied', size:3, dx:30, dy:-26, description:'Hace explícitos exposición, incertidumbre, consecuencias y condiciones para revisar una decisión.', refs:[['N04','Hipótesis, supuestos y decisiones'],['N18','Legado y regulación'],['N20','Estrategia situada'],['N28','Calidad según riesgo'],['N32','Riesgo y evidencia en IA']] },
      { id:'uml', label:'UML', block:1, band:3, status:'applied', size:2, dx:-34, dy:-16, description:'Aporta lenguajes de modelado cuando una vista precisa ayuda a conversar, verificar o decidir.', refs:[['N02','Sistema y aplicación'],['N12','Eventos, estados y comandos'],['N15','Selección de modelos'],['N16','Coherencia entre modelos']] },
      { id:'c4', label:'C4', block:1, band:3, status:'contextual', size:1, dx:36, dy:42, description:'Ubica personas, sistemas, contenedores y componentes sin confundir el mapa técnico con el sistema completo.', refs:[['N02','Frontera sociotécnica'],['N15','Pregunta, audiencia y nivel de detalle'],['N16','Relaciones entre modelos'],['N26','Ecosistema y arquitectura']] },

      { id:'discovery', label:'Product discovery', block:2, band:1, status:'central', size:3, dx:-38, dy:-36, description:'Investiga antes de comprometer una solución y compra evidencia en proporción a la incertidumbre.', refs:[['N06','Discovery como inversión'],['N07','Entrevistar episodios'],['N09','Experiencia end-to-end'],['N10','Problema y outcomes'],['N22','Hipótesis refutable']] },
      { id:'ux', label:'UX', block:2, band:1, status:'central', size:3, dx:36, dy:32, description:'Estudia la experiencia completa, incluidas fricciones, trabajo invisible, adopción y consecuencias.', refs:[['N07','Reconstrucción de episodios'],['N08','Trabajo real e invisible'],['N09','Experiencia end-to-end'],['N22','Hipótesis de valor']] },
      { id:'service-design', label:'Diseño de servicios', block:2, band:3, status:'central', size:3, dx:-40, dy:-36, description:'Relaciona la experiencia visible con procesos, reglas, información y trabajo que sostienen el servicio.', refs:[['N05','Personas y reparación'],['N08','Trabajo prescripto y real'],['N09','Experiencia end-to-end'],['N14','Proceso, handoffs y excepciones'],['N26','Ecosistema de servicios']] },
      { id:'accessibility', label:'Accesibilidad', block:2, band:3, status:'central', size:2, dx:34, dy:38, description:'Trata la accesibilidad como condición de la promesa y de la calidad, no como agregado posterior.', refs:[['N05','Voz y exposición'],['N09','Accesibilidad y adopción'],['N23','Capacidad para una población'],['N28','Atributos de calidad'],['N32','Disparidad y evaluación de IA']] },

      { id:'bpmn', label:'BPMN', block:3, band:3, status:'central', size:3, dx:-40, dy:-38, description:'Representa procesos, handoffs, colas y excepciones para localizar decisiones y trabajo real.', refs:[['N14','Procesos end-to-end'],['N15','Selección del modelo'],['N16','Coherencia y contradicciones']] },
      { id:'ui', label:'UI', block:3, band:3, status:'applied', size:2, dx:34, dy:34, description:'Trabaja la interfaz como una parte de la capacidad, nunca como sustituto del servicio completo.', refs:[['N09','Interfaz, experiencia y adopción'],['N19','Configurar, integrar o construir'],['N23','Componentes frente a capacidad']] },
      { id:'apis', label:'APIs', block:3, band:4, status:'applied', size:3, dx:-40, dy:-38, description:'Hace visibles contratos, eventos, autoridad, errores y límites entre servicios que deben coordinarse.', refs:[['N12','Eventos, comandos y autoridad'],['N13','Consistencia e idempotencia'],['N26','Ecosistema de servicios'],['N27','Contratos y terceros'],['N29','Integración y despliegue']] },
      { id:'data-ai', label:'Gestión de datos e IA', block:7, band:4, status:'central', size:3, dx:22, dy:-20, description:'Conecta procedencia, calidad y uso de datos con evaluación, operación y gobierno responsable de IA.', refs:[['N11','Dato, afirmación y evidencia'],['N12','Procedencia y autoridad'],['N13','Consistencia y reconciliación'],['N31','Capacidad y límites de IA'],['N32','Evaluación y riesgo'],['N33','Gobierno vivo']] },

      { id:'pmi', label:'PMI', block:4, band:2, status:'applied', size:2, dx:-48, dy:-44, description:'Aporta prácticas de dirección de proyectos que se seleccionan y adaptan según contexto y riesgo.', refs:[['N17','Lógicas predictivas e híbridas'],['N20','Estrategia, hitos y condiciones de salida'],['N21','Gobierno del proyecto y transición'],['N24','Decisiones de portfolio'],['N34','Cadena de decisión y gobierno']] },
      { id:'pmbok', label:'PMBOK', block:4, band:2, status:'applied', size:2, dx:36, dy:-8, description:'Se usa como cuerpo de conocimiento para elegir prácticas, no como receta que reemplaza el diagnóstico.', refs:[['N17','Principios, dominios y procesos'],['N20','Tailoring y gobierno'],['N21','Proyecto, valor y transición'],['N34','Integración del expediente']] },
      { id:'scrum', label:'Scrum', block:4, band:2, status:'applied', size:3, dx:-35, dy:46, description:'Ordena ciclos breves de inspección y adaptación cuando existe un producto y una incertidumbre que aprender.', refs:[['N17','Lógicas iterativas y adaptativas'],['N23','Slices verticales'],['N25','Flujo más allá de las ceremonias']] },
      { id:'change', label:'Gestión del cambio', block:4, band:1, status:'central', size:3, dx:30, dy:-24, description:'Prepara adopción, participación, comunicación y revisión sin reducir el cambio a un plan de difusión.', refs:[['N05','Actores y poder'],['N17','Estrategias de cambio'],['N18','Legado y restricciones'],['N20','Autoridad y secuencia'],['N35','Comunicación y transferencia'],['N36','Aprendizaje y revisión']] },
      { id:'procurement', label:'Gestión de adquisiciones', block:4, band:2, status:'contextual', size:2, dx:34, dy:55, description:'Examina comprar, contratar e integrar como decisiones con dependencia, evidencia y condiciones de salida.', refs:[['N19','Construir, comprar, configurar o integrar'],['N20','Decisión estratégica'],['N26','Terceros y ecosistema'],['N27','Contratos e interfaces']] },

      { id:'product', label:'Gestión de producto', block:5, band:2, status:'central', size:3, dx:-48, dy:-48, description:'Conecta problema, valor, outcome, capacidad, evidencia y decisión de inversión.', refs:[['N10','Problema y outcomes'],['N21','Producto, servicio y capacidad'],['N22','Hipótesis'],['N23','Cortes por outcome'],['N24','Priorización'],['N25','Flujo y aprendizaje']] },
      { id:'lean', label:'Lean', block:5, band:2, status:'central', size:3, dx:36, dy:-17, description:'Reduce lote, espera y trabajo sin aprendizaje para obtener evidencia útil con menor exposición.', refs:[['N06','Reducir incertidumbre'],['N22','Experimentos'],['N23','Cortes por aprendizaje'],['N24','Costo de demora y límites'],['N25','Lote, espera y feedback']] },
      { id:'kanban', label:'Kanban', block:5, band:2, status:'applied', size:2, dx:-42, dy:26, description:'Hace visible el flujo, limita trabajo en curso y ayuda a gestionar colas, bloqueos y capacidad.', refs:[['N24','Prioridad y capacidad'],['N25','Sistema de flujo y políticas explícitas'],['N30','Operación y aprendizaje']] },
      { id:'wip', label:'WIP', block:5, band:2, status:'applied', size:2, dx:28, dy:55, description:'Nombra el trabajo en curso que consume capacidad y alarga la espera cuando no se limita.', refs:[['N14','Colas y trabajo en proceso'],['N17','Lógicas de flujo'],['N24','Capacidad y renuncia'],['N25','Trabajo en curso, colas y espera'],['N26','Capacidad entre servicios']] },
      { id:'mvp', label:'MVP', block:5, band:1, status:'applied', size:3, dx:-36, dy:-22, description:'Es una versión defendible para probar valor y uso; no una entrega de baja calidad.', refs:[['N22','Hipótesis y experimento'],['N23','Corte vertical y aprendizaje'],['N24','Apuesta y condición de expansión']] },
      { id:'okr', label:'OKR', block:5, band:1, status:'contextual', size:2, dx:38, dy:40, description:'Ayuda a expresar objetivos y resultados observables cuando no se confunde el indicador con el propósito.', refs:[['N10','Outcomes y problema'],['N22','Hipótesis y medidas'],['N24','Valor y priorización']] },

      { id:'quality', label:'Gestión de calidad', block:6, band:2, status:'central', size:3, dx:-44, dy:-40, description:'Define calidad según uso, riesgo y población, y conserva evidencia para revisar si la promesa se sostiene.', refs:[['N28','Evidencia y atributos de calidad'],['N29','Controles de entrega'],['N30','Calidad operativa y SLO'],['N34','Coherencia de la intervención']] },
      { id:'itil', label:'ITIL', block:6, band:2, status:'applied', size:2, dx:38, dy:33, description:'Aporta prácticas de gestión de servicios, incidentes y mejora continua situadas en el sistema real.', refs:[['N26','Ecosistema de servicios'],['N28','Calidad de servicio'],['N30','Incidentes, problemas y aprendizaje']] },
      { id:'devops', label:'DevOps', block:6, band:4, status:'central', size:3, dx:-50, dy:-50, description:'Integra construcción, entrega y operación para acortar feedback sin trasladar riesgo a usuarios u operación.', refs:[['N23','Integración temprana'],['N25','Flujo y feedback'],['N29','Entrega, despliegue y rollback'],['N30','Operación y observabilidad']] },
      { id:'cicd', label:'CI/CD', block:5, band:4, status:'applied', size:3, dx:-42, dy:-42, description:'Automatiza integración y entrega con controles que permiten detectar, contener y revertir fallas.', refs:[['N23','Integración temprana'],['N29','Pipeline, despliegue y rollback'],['N30','Señales operativas']] },
      { id:'dora', label:'DORA', block:6, band:4, status:'applied', size:2, dx:-44, dy:5, description:'Relaciona velocidad y estabilidad mediante medidas de entrega que necesitan contexto para orientar decisiones.', refs:[['N25','Flujo y tiempo de aprendizaje'],['N29','Desempeño de entrega'],['N30','Medición y operación']] },
      { id:'sre', label:'SRE', block:6, band:4, status:'applied', size:2, dx:36, dy:25, description:'Vincula confiabilidad, objetivos de servicio, error tolerable, automatización y aprendizaje operativo.', refs:[['N28','Confiabilidad como calidad'],['N29','Rollback y protección'],['N30','SLI, SLO e incidentes']] },
      { id:'observability', label:'Observabilidad', block:6, band:4, status:'central', size:3, dx:-36, dy:56, description:'Permite inferir qué ocurre en el sistema a partir de señales diseñadas para investigar y decidir.', refs:[['N11','Dato y evidencia'],['N13','Eventos y consistencia'],['N29','Telemetría de entrega'],['N30','Señales e incidentes'],['N33','Monitoreo de IA']] },
      { id:'testing', label:'Testing / QA', block:6, band:3, status:'central', size:3, dx:-44, dy:-24, description:'Produce evidencia sobre comportamiento y calidad con pruebas proporcionales al riesgo y al uso esperado.', refs:[['N22','Prueba de hipótesis'],['N23','Prueba de capacidad'],['N28','Estrategia de calidad'],['N29','Controles de despliegue'],['N32','Evaluación de IA']] },
      { id:'security', label:'Seguridad', block:6, band:3, status:'applied', size:3, dx:38, dy:42, description:'Integra amenazas, controles y exposición en la decisión sin tratar seguridad como revisión tardía.', refs:[['N18','Regulación y restricciones'],['N27','Contratos y terceros'],['N28','Atributos de seguridad'],['N29','Controles de entrega'],['N32','Robustez y riesgo de IA']] },
      { id:'git', label:'Git', block:5, band:4, status:'applied', size:2, dx:38, dy:-10, description:'Conserva versiones y permite reconstruir qué cambió, quién lo cambió y cómo volver atrás.', refs:[['N12','Registro y autoridad'],['N29','Versionado y entrega'],['N34','Trazabilidad del expediente']] },
      { id:'github', label:'GitHub', block:5, band:4, status:'applied', size:2, dx:-34, dy:42, description:'Articula repositorios, revisión, automatización y evidencia de entrega alrededor del trabajo compartido.', refs:[['N12','Registro y procedencia'],['N29','Repositorio, revisión y pipeline'],['N34','Trazabilidad entre artefactos']] },
      { id:'lowcode', label:'Low-code', block:4, band:3, status:'contextual', size:1, dx:0, dy:0, description:'Es una alternativa de realización que también exige contratos, gobierno, seguridad y capacidad operativa.', refs:[['N19','Alternativas de realización'],['N27','Contratos y dependencia'],['N29','Gobierno del despliegue']] },

      { id:'cobit', label:'COBIT', block:7, band:2, status:'contextual', size:2, dx:-28, dy:-24, description:'Aporta objetivos y prácticas de gobierno para conectar decisiones, controles, responsabilidad y evidencia.', refs:[['N20','Gobierno y tailoring'],['N33','Gobierno vivo de IA'],['N34','Gobierno integrado']] },

      { id:'architecture', label:'Arquitectura e integración', block:8, band:3, status:'central', size:3, dx:-34, dy:-20, description:'Conecta representaciones, contratos y decisiones para que las partes funcionen como un sistema.', refs:[['N02','Sistema frente a aplicación'],['N12','Eventos y autoridad'],['N16','Coherencia entre modelos'],['N19','Configurar, integrar o construir'],['N26','Ecosistema y arquitectura'],['N27','Contratos'],['N29','Integración y despliegue'],['N34','Cadena completa']] },
      { id:'incidents', label:'Incidentes, rollback y continuidad', block:8, band:4, status:'central', size:3, dx:20, dy:-20, description:'Trata la falla, la reversión y la continuidad como parte del diseño y del aprendizaje, no como excepciones finales.', refs:[['N18','Continuidad y legado'],['N26','Servicios y terceros'],['N29','Rollback y protección'],['N30','Incidentes y aprendizaje'],['N33','Contención y retiro de IA'],['N34','Reconstrucción de la cadena']] }
    ];
    const blockLabels = ['Sistema','Investigar','Modelar','Estrategia','Producto','Operar','Gobernar IA','Integrar'];
    const bandLabels = ['Experiencia y personas','Gestión y proceso','Diseño y arquitectura','Tecnología y operación'];
    const statusLabels = { central:'Concepto central', applied:'Aplicación relevante', contextual:'Referencia contextual' };
    const pdfLinks = new Map([...document.querySelectorAll('.nucleus.available')].map((link) => [link.querySelector('b')?.textContent.trim(), link.getAttribute('href')]));

    const makeButton = (item, mobile = false) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = `practice-node ${item.status} size-${item.size}${mobile ? ' practice-node-mobile' : ''}`;
      button.dataset.practiceId = item.id;
      button.setAttribute('aria-label', `${item.label}. ${statusLabels[item.status]}. ${blockLabels[item.block - 1]}.`);
      if (!mobile) {
        button.style.setProperty('--x', `${(item.block - .5) * 12.5}%`);
        button.style.setProperty('--y', `${(item.band - .5) * 25}%`);
        button.style.setProperty('--dx', `${item.dx || 0}px`);
        button.style.setProperty('--dy', `${item.dy || 0}px`);
      }
      const dot = document.createElement('i');
      dot.setAttribute('aria-hidden', 'true');
      const label = document.createElement('span');
      label.textContent = item.label;
      button.append(dot, label);
      button.addEventListener('click', () => {
        selectPractice(item);
        if (mobile) practiceDetail.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'start' });
      });
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
      list.replaceChildren(...item.refs.map(([n, section]) => {
        const li = document.createElement('li');
        const href = pdfLinks.get(n);
        if (href) {
          const link = document.createElement('a');
          link.href = href;
          link.textContent = n;
          link.setAttribute('aria-label', `Abrir ${n}, ${section}`);
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

    practiceData.forEach((item) => practiceMap.append(makeButton(item)));
    for (let block = 1; block <= 8; block += 1) {
      const route = document.createElement('section');
      route.className = 'practice-route';
      route.id = `practice-block-${String.fromCharCode(96 + block)}`;
      const heading = document.createElement('h4');
      heading.innerHTML = `<b>${String.fromCharCode(64 + block)}</b><span>${blockLabels[block - 1]}</span>`;
      const list = document.createElement('div');
      practiceData.filter((item) => item.block === block).forEach((item) => list.append(makeButton(item, true)));
      route.append(heading, list);
      practiceMobile.append(route);
    }
    selectPractice(practiceData.find((item) => item.id === 'architecture'));
  }

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const revealTargets = document.querySelectorAll('.value-grid, .case-thread, .rhythm, .anatomy-grid, .guide-card, .cover-library, .quality-grid, .practice-map');
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
