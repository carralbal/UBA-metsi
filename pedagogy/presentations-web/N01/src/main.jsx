import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const slides = [
  {
    stage: "APERTURA",
    video: "road",
    tone: "deep",
    layout: "opening",
    title: <>La solución llega formulada.<br />El problema, todavía no.</>,
    prompt: "¿Qué necesitamos comprender antes de comprometernos con una solución?",
    aside: <>Hoy no venimos a repetir N01.<br />Venimos a ponerlo a trabajar.</>,
    notes: `Quiero empezar sin explicar nada. Imaginen que somos el equipo que recibió un pedido muy claro: comprar un nuevo PMS para el Hotel Horizonte. La solución ya viene nombrada, incluso parece urgente. La pregunta es qué necesitamos comprender antes de comprometernos con ella.

Tómense unos segundos y elijan una palabra para nombrar el problema. Puede ser una falla, una demora, una descoordinación, una promesa comercial o algo distinto. No busco todavía la palabra correcta. Me interesa que escuchemos la diversidad de encuadres que aparece incluso cuando todos leímos el mismo material.

Voy a registrar esas palabras porque al final vamos a volver a ellas. Si nuestras palabras cambian, también cambia lo que consideramos evidencia, la acción que parece razonable y quién debería poder decidir.`,
  },
  {
    stage: "DECISIÓN INICIAL",
    video: "structure",
    tone: "light",
    layout: "decision",
    title: "¿Comprar el PMS ahora?",
    options: ["SÍ", "NO", "TODAVÍA NO"],
    prompt: "Una razón y una evidencia que falta",
    duration: "10 MIN",
    notes: `Ahora sí, cada persona va a tomar una posición. La pregunta es concreta: ¿compraríamos el PMS ahora? Sólo hay tres respuestas posibles: sí, no o todavía no.

Escriban su elección, una razón y una evidencia que hoy les falta. Una opción sin razón es apenas una preferencia. Una razón sin evidencia faltante corre el riesgo de convertirse en una conclusión cerrada.

Tienen dos minutos en silencio. Después voy a relevar la distribución, pero no vamos a debatir todavía cuál respuesta es correcta. Lo que quiero conservar es el punto de partida.

Si eligieron “todavía no”, no alcanza con decir que falta información. Nombren una observación posible, de qué fuente podría venir y qué decisión cambiaría. Si eligieron “sí” o “no”, hagan el mismo esfuerzo. Toda decisión profesional necesita mostrar qué la sostiene y qué podría revisarla.`,
  },
  {
    stage: "COMPARAR ENCUADRES",
    video: "wires",
    tone: "deep",
    layout: "definitions",
    title: "Tres palabras que suelen mezclarse",
    items: [
      ["PEDIDO", "Lo que alguien solicita"],
      ["PROBLEMA", "La situación que todavía debemos explicar"],
      ["SOLUCIÓN", "Una intervención posible"],
    ],
    prompt: "¿Qué diferencia cambiaría una decisión?",
    notes: `Vamos a comparar las palabras que aparecieron. Un pedido es lo que alguien solicita. Un problema es la situación que todavía necesitamos comprender. Una solución es una intervención posible. Las tres cosas pueden estar relacionadas, pero no son equivalentes.

Si alguien pide un nuevo PMS, eso demuestra que existe un pedido. No demuestra todavía que el software actual sea la causa dominante.

En grupos de cuatro, compartan el campo de HH-01 que les resultó más difícil y busquen dos diferencias entre sus versiones que podrían cambiar una decisión. No vale cerrar la conversación diciendo que falta toda la información. Elijan una diferencia concreta: qué actor queda fuera, qué propósito cambia, qué evidencia se considera suficiente o quién tiene autoridad.

Cuando volvamos, no me cuenten todo el memo. Tráiganme una diferencia y la consecuencia práctica que tendría.`,
  },
  {
    stage: "DOS VERSIONES",
    video: "lights",
    tone: "deep",
    layout: "comparison",
    title: "No gana el memo más prolijo",
    subtitle: "Gana la diferencia que vuelve visible una consecuencia.",
    items: [
      ["HH-01 · A", "El problema es el sistema actual", "Próxima acción: reemplazar"],
      ["HH-01 · B", "La promesa comercial no llega a operación", "Próxima acción: reconstruir el episodio"],
    ],
    prompt: "¿Qué evidencia permitiría distinguirlos?",
    notes: `Miren estas dos versiones. Las dos pueden estar bien escritas y las dos pueden parecer razonables. La primera convierte al sistema actual en el problema y habilita una acción de reemplazo. La segunda ubica la tensión entre una promesa comercial y la capacidad real de operación, y habilita una investigación del episodio.

No vamos a elegir la más linda ni la que usa palabras más técnicas. Vamos a preguntar qué diferencia cambia una decisión y qué evidencia permitiría distinguirlas.

Si el PMS respondió a tiempo, la primera explicación pierde fuerza. Si Comercial publicó una condición que Operaciones nunca validó, la segunda gana fuerza. Esto no significa que ya tengamos la verdad. Significa que el encuadre dejó de ser una opinión suelta y empezó a producir preguntas observables. Ese es el trabajo que vamos a hacer con nuestros propios memos.`,
  },
  {
    stage: "CLÍNICA CONCEPTUAL",
    video: "structure",
    tone: "light",
    layout: "questions",
    title: "Una prueba en cuatro preguntas",
    items: [
      "¿Qué incertidumbre reducimos?",
      "¿Antes de qué decisión?",
      "¿Mediante qué evidencia?",
      "¿Qué resultado cambiaría el camino?",
    ],
    aside: "Si una actividad no responde estas preguntas, todavía no produce aprendizaje útil.",
    notes: `Voy a detenerme sólo en dos confusiones que suelen aparecer. La primera es tomar el pedido como prueba del problema. La segunda es tomar una actividad como evidencia de aprendizaje.

Para revisar ambas vamos a usar cuatro preguntas. ¿Qué incertidumbre reducimos? ¿Antes de qué decisión? ¿Mediante qué evidencia? ¿Qué resultado cambiaría el camino? Si no podemos responderlas, quizás estamos haciendo cosas, pero todavía no sabemos qué aprendemos ni para qué sirve.

Apliquen la prueba a una acción de su memo. Por ejemplo, entrevistar a Recepción no es valioso por sí mismo. Se vuelve metodológicamente útil si busca distinguir entre una falla técnica y una regla operativa antes de decidir un reemplazo. Necesita evidencia del episodio y un resultado que nos haría abandonar la explicación inicial.`,
  },
  {
    stage: "RECONSTRUIR HH-01",
    video: "hotel",
    tone: "deep",
    layout: "sequence",
    title: <>Una versión común,<br />sin borrar el desacuerdo</>,
    items: ["Pedido", "Propósito", "Incertidumbre", "Evidencia", "Actores", "Autoridad", "Próxima decisión"],
    prompt: "Una versión que otra persona pueda objetar y revisar",
    duration: "23 MIN",
    notes: `Ahora cada equipo va a construir una segunda versión común de HH-01. No buscamos que todos piensen igual. Buscamos que el desacuerdo quede ubicado en un campo que podamos revisar.

Revisen pedido, propósito, incertidumbre, evidencia, actores, autoridad y próxima decisión. El memo no es un diagnóstico definitivo ni un plan completo. Es una forma de declarar qué creemos comprender, qué sigue abierto y qué acción pequeña queda autorizada.

Conserven al menos un desacuerdo relevante y nombren a un actor que podría cuestionar el propósito que formularon. Mientras trabajan, háganse una pregunta incómoda: ¿qué evidencia adversa estaríamos dispuestos a aceptar? Si la respuesta es “ninguna”, el memo está defendiendo una conclusión previa.

Tienen veintitrés minutos. El producto es una versión que otra persona pueda objetar y revisar, no una pieza cerrada.`,
  },
  {
    stage: "EVIDENCIA NUEVA",
    video: "wires",
    tone: "deep",
    layout: "evidence",
    title: "La evidencia debe poder incomodar",
    subtitle: "Cada equipo recibe dos piezas.",
    items: [
      "El PMS respondió a tiempo",
      "Recepción no pudo asignar la habitación",
      "Comercial publicó una condición no validada",
      "Una persona abandonó por accesibilidad",
      "El chatbot canceló sin confirmar identidad",
      "La sobreventa aparece sólo en un canal externo",
    ],
    prompt: "Qué cambia · qué se mantiene · qué acción queda autorizada",
    notes: `Ahora voy a entregar dos piezas de evidencia a cada equipo. No fueron elegidas para confirmar lo que ustedes ya sostienen. Fueron elegidas para ponerlo a prueba.

Puede aparecer que el PMS respondió a tiempo, que Recepción no pudo asignar una habitación declarada limpia, que Comercial publicó una condición no validada, que una persona abandonó por una barrera de accesibilidad, que el chatbot canceló sin confirmar identidad o que la sobreventa ocurre sólo en un canal externo.

Lean las dos piezas y registren tres cosas: qué campo de HH-01 cambia, cuál se mantiene y qué nueva acción queda autorizada. No intenten hacer que toda la evidencia encaje a la fuerza. Si una pieza contradice su explicación, esa contradicción es valiosa.

Al final necesito ver una revisión explícita, incluso si la revisión consiste en sostener el encuadre y explicar por qué esta evidencia todavía no alcanza para cambiarlo.`,
  },
  {
    stage: "REVISIÓN CRUZADA",
    video: "lights",
    tone: "deep",
    layout: "definitions",
    title: "Objetar no es resolver por otro",
    items: [
      ["CITAR", "El campo cuestionado"],
      ["MOSTRAR", "La relación que no se sostiene"],
      ["PROPONER", "Una prueba, no una solución"],
    ],
    prompt: "Dos objeciones por memo. Las dos deben poder usarse.",
    duration: "18 MIN",
    notes: `Intercambien ahora sus memos con otro equipo. La tarea no es corregir el trabajo ajeno ni imponer una solución. Cada equipo revisor va a formular dos objeciones que puedan usarse.

La primera debe señalar una relación entre evidencia y decisión que todavía no se sostiene. La segunda debe detectar una condición de revisión demasiado vaga o imposible de observar.

Para que la devolución sea útil, citen el campo cuestionado, expliquen qué relación es débil y propongan una prueba. Por ejemplo: “En evidencia afirman que el PMS falla, pero no muestran el tiempo acordado ni el registro del episodio. Proponemos contrastar logs y secuencia operativa”. Eso es distinto de decir “cambien el sistema”.

Cuando reciban las objeciones, no se defiendan enseguida. Primero prueben si permiten mejorar el memo. Una buena revisión no cierra la discusión. Hace más precisa la próxima decisión.`,
  },
  {
    stage: "DEFENSA",
    video: "hotel",
    tone: "deep",
    layout: "questions",
    title: "Noventa segundos. Cuatro frases.",
    items: [
      "Queremos sostener…",
      "La siguiente acción autorizada es…",
      "Por ahora no decidimos…",
      "Revisaríamos el encuadre si…",
    ],
    aside: "La defensa muestra una posición y también su límite.",
    notes: `Cada equipo dispone de noventa segundos. No necesitamos una descripción completa del memo. Necesitamos cuatro frases claras.

La primera nombra el propósito que quieren sostener. La segunda declara la siguiente acción autorizada. La tercera dice qué decisión permanece deliberadamente cerrada. La cuarta identifica la evidencia que podría cambiar el encuadre.

Voy a cuidar el tiempo porque la restricción nos obliga a priorizar. Si escuchamos sólo actividades, voy a preguntar qué decisión habilitan. Si escuchamos una conclusión sin límite, voy a preguntar qué no están autorizando todavía.

Defender no significa fingir certeza. Significa mostrar una posición suficientemente sostenida para actuar y suficientemente abierta para ser revisada. Mientras escuchan a los demás, registren una frase que les ayude a mejorar su propio memo.`,
  },
  {
    stage: "CIERRE Y PUENTE",
    video: "road",
    tone: "deep",
    layout: "reflection",
    title: "Lo que cambió deja una huella",
    items: [
      ["ANTES PENSABA", "Una idea inicial"],
      ["AHORA SOSTENGO", "Una posición revisada"],
      ["TODAVÍA CAMBIARÍA SI", "Una evidencia posible"],
    ],
    prompt: "N02 abre la frontera: ¿qué relaciones forman el sistema relevante?",
    notes: `Para cerrar, vuelvan a la posición que registraron al comienzo. Completen cinco frases: al comienzo pensaba, ahora sostengo, cambié por esta evidencia u objeción, todavía podría cambiar si, y para N02 necesito saber qué relaciones forman el sistema relevante.

Háganlo en silencio. No hace falta que el cambio sea total. Puede haber cambiado una palabra, una relación o el límite de una decisión. Lo importante es que podamos reconstruir por qué cambió. Esa huella es evidencia de aprendizaje mucho más valiosa que decir “entendí”.

Antes de irnos, quiero que miremos el recorrido completo: recibimos una solución formulada, distinguimos pedido y problema, comparamos encuadres, sometimos el memo a evidencia adversa, aceptamos objeciones y defendimos una decisión provisional.

N02 retoma justamente lo que hoy dejamos abierto: dónde termina el sistema relevante y qué relaciones necesitamos incluir para no intervenir sobre una parte aislada.`,
  },
];

const videoSources = {
  road: {
    label: "Colegas recorriendo un espacio de trabajo",
    source: "Pexels",
    creator: "Tiger Lily",
    url: "https://www.pexels.com/video/workmates-walking-in-office-corridor-7147176/",
  },
  structure: {
    label: "Persona caminando por un corredor de arquitectura mínima",
    source: "Pexels",
    creator: "cottonbro studio",
    url: "https://www.pexels.com/video/person-walking-on-a-white-corridor-5971048/",
  },
  wires: {
    label: "Flujo dinámico de conexiones y datos",
    source: "Pexels",
    creator: "Chandresh Uike",
    url: "https://www.pexels.com/video/futuristic-digital-data-flow-background-34127955/",
  },
  lights: {
    label: "Manos revisando documentos de trabajo",
    source: "Pexels",
    creator: "Kaboompics.com",
    url: "https://www.pexels.com/video/person-looking-through-papers-on-work-desk-7710457/",
  },
  hotel: {
    label: "Recepción y atención de una huésped en un hotel",
    source: "Pexels",
    creator: "Mikhail Nilov",
    url: "https://www.pexels.com/video/a-receptionist-assisting-a-client-in-the-hotel-7820474/",
  },
};

const mediaVersion = "20260915-3";

function BackgroundVideo({ name }) {
  const videoRef = useRef(null);
  const [playing, setPlaying] = useState(false);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return undefined;
    video.muted = true;
    const start = () => video.play().then(() => setPlaying(true)).catch(() => setPlaying(false));
    start();
    const resumeWhenVisible = () => {
      if (document.visibilityState === "visible" && video.paused) start();
    };
    document.addEventListener("visibilitychange", resumeWhenVisible);
    return () => document.removeEventListener("visibilitychange", resumeWhenVisible);
  }, [name]);

  const toggle = () => {
    const video = videoRef.current;
    if (!video) return;
    if (video.paused) video.play().then(() => setPlaying(true)).catch(() => setPlaying(false));
    else {
      video.pause();
      setPlaying(false);
    }
  };

  return <>
    <video
      ref={videoRef}
      className="background-video"
      autoPlay
      muted
      loop
      playsInline
      preload="auto"
      poster={`./media/${name}.png?v=${mediaVersion}`}
      onCanPlay={() => videoRef.current?.play().catch(() => setPlaying(false))}
      onPlaying={() => setPlaying(true)}
      onPause={() => setPlaying(false)}
    >
      <source src={`./media/${name}.mp4?v=${mediaVersion}`} type="video/mp4" />
    </video>
    <button className="video-toggle" type="button" onClick={toggle}>{playing ? "Pausar video" : "Reproducir video"}</button>
  </>;
}

function usePresentationKeys({ next, previous, first, last, openNotes, toggleFullscreen }) {
  useEffect(() => {
    const onKey = (event) => {
      if (["ArrowRight", "PageDown", " "].includes(event.key)) { event.preventDefault(); next(); }
      if (["ArrowLeft", "PageUp"].includes(event.key)) { event.preventDefault(); previous(); }
      if (event.key === "Home") first();
      if (event.key === "End") last();
      if (event.key.toLowerCase() === "n") openNotes();
      if (event.key.toLowerCase() === "f") toggleFullscreen();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [next, previous, first, last, openNotes, toggleFullscreen]);
}

function SlideBody({ slide }) {
  if (slide.layout === "opening") return <div className="opening-layout"><h1>{slide.title}</h1><p className="main-prompt">{slide.prompt}</p><p className="aside">{slide.aside}</p></div>;
  if (slide.layout === "decision") return <><h1>{slide.title}</h1><div className="decision-grid">{slide.options.map((item) => <div key={item}><strong>{item}</strong><span>una razón</span></div>)}</div><p className="main-prompt">{slide.prompt}</p></>;
  if (slide.layout === "definitions") return <><h1>{slide.title}</h1><div className="definition-grid">{slide.items.map(([title, body], index) => <div key={title}><span>{String(index + 1).padStart(2, "0")}</span><h2>{title}</h2><p>{body}</p></div>)}</div><p className="main-prompt">{slide.prompt}</p></>;
  if (slide.layout === "comparison") return <><h1>{slide.title}</h1><p className="subtitle">{slide.subtitle}</p><div className="comparison-grid">{slide.items.map(([label, claim, action]) => <div key={label}><span>{label}</span><h2>{claim}</h2><p>{action}</p></div>)}</div><p className="main-prompt">{slide.prompt}</p></>;
  if (slide.layout === "questions") return <><h1>{slide.title}</h1><ol className="question-list">{slide.items.map((item, index) => <li key={item}><span>{String(index + 1).padStart(2, "0")}</span><strong>{item}</strong></li>)}</ol><p className="aside">{slide.aside}</p></>;
  if (slide.layout === "sequence") return <><h1>{slide.title}</h1><div className="word-sequence">{slide.items.map((item, index) => <div key={item}><span>{String(index + 1).padStart(2, "0")}</span><strong>{item}</strong></div>)}</div><p className="main-prompt">{slide.prompt}</p></>;
  if (slide.layout === "evidence") return <><h1>{slide.title}</h1><p className="subtitle">{slide.subtitle}</p><ol className="evidence-list">{slide.items.map((item, index) => <li key={item}><span>{String(index + 1).padStart(2, "0")}</span><strong>{item}</strong></li>)}</ol><p className="main-prompt">{slide.prompt}</p></>;
  if (slide.layout === "reflection") return <><h1>{slide.title}</h1><div className="reflection-grid">{slide.items.map(([label, body], index) => <div key={label} className={index === 1 ? "current" : ""}><span>{label}</span><strong>{body}</strong></div>)}</div><p className="main-prompt">{slide.prompt}</p></>;
  return null;
}

function App() {
  const query = new URLSearchParams(location.search);
  const presenterMode = query.get("presenter") === "1";
  const initial = Math.min(Math.max(Number(query.get("slide")) || 1, 1), slides.length) - 1;
  const [index, setIndex] = useState(initial);
  const rootRef = useRef(null);
  const channelRef = useRef(null);
  const indexRef = useRef(initial);
  const slide = slides[index];
  const notesHref = `${location.pathname}?slide=${index + 1}&presenter=1`;

  const controls = useMemo(() => ({
    next: () => setIndex((value) => Math.min(value + 1, slides.length - 1)),
    previous: () => setIndex((value) => Math.max(value - 1, 0)),
    first: () => setIndex(0),
    last: () => setIndex(slides.length - 1),
    openNotes: () => window.open(notesHref, "metsi-n01-speaker-notes", "noopener")?.focus(),
    toggleFullscreen: () => document.fullscreenElement ? document.exitFullscreen() : rootRef.current?.requestFullscreen(),
  }), [index, notesHref]);
  usePresentationKeys(controls);

  useEffect(() => {
    if (!("BroadcastChannel" in window)) return undefined;
    const channel = new BroadcastChannel("metsi-n01-presentation");
    channelRef.current = channel;
    channel.onmessage = ({ data }) => {
      if (data?.type === "slide" && Number.isInteger(data.index)) {
        setIndex(Math.min(Math.max(data.index, 0), slides.length - 1));
      }
      if (data?.type === "request-slide") {
        channel.postMessage({ type: "slide", index: indexRef.current });
      }
    };
    if (presenterMode) channel.postMessage({ type: "request-slide" });
    return () => channel.close();
  }, [presenterMode]);

  useEffect(() => {
    indexRef.current = index;
    const params = new URLSearchParams(location.search);
    params.set("slide", String(index + 1));
    if (presenterMode) params.set("presenter", "1");
    else params.delete("presenter");
    history.replaceState(null, "", `${location.pathname}?${params}${location.hash}`);
    localStorage.setItem("metsi-n01-slide", String(index));
    channelRef.current?.postMessage({ type: "slide", index });
  }, [index, presenterMode]);

  useEffect(() => {
    if (!presenterMode) window.name = "metsi-n01-presentation";
  }, [presenterMode]);

  useEffect(() => {
    const onStorage = (event) => {
      if (event.key === "metsi-n01-slide") {
        const nextIndex = Number(event.newValue);
        if (Number.isInteger(nextIndex)) setIndex(Math.min(Math.max(nextIndex, 0), slides.length - 1));
      }
    };
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  if (presenterMode) {
    const source = videoSources[slide.video];
    return <main className="notes-window">
      <header>
        <div><span>NOTAS DE ORADOR · METSI N01</span><b>{String(index + 1).padStart(2, "0")} / {String(slides.length).padStart(2, "0")}</b></div>
        <h1>{slide.title}</h1>
      </header>
      <article>{slide.notes.split("\n\n").map((paragraph) => <p key={paragraph}>{paragraph}</p>)}</article>
      <aside><span>FONDO VISUAL</span><a href={source.url} target="_blank" rel="noreferrer">{source.label} · {source.creator} · {source.source}</a></aside>
      <nav aria-label="Navegación desde las notas">
        <button onClick={controls.previous} disabled={index === 0}>← Anterior</button>
        <a href={`${location.pathname}?slide=${index + 1}`} target="metsi-n01-presentation">Abrir presentación ↗</a>
        <button onClick={controls.next} disabled={index === slides.length - 1}>Siguiente →</button>
      </nav>
    </main>;
  }

  return <main ref={rootRef} className="presentation">
    <section className={`stage tone-${slide.tone}`} aria-label={`Diapositiva ${index + 1} de ${slides.length}`}>
      <BackgroundVideo key={slide.video} name={slide.video} />
      <div className="veil" />
      <header className="slide-header"><span>{String(index + 1).padStart(2, "0")}</span><i /><b>METSI · N01</b><em>{slide.stage}</em><hr /></header>
      <article className={`slide-copy layout-${slide.layout}`}><SlideBody slide={slide} /></article>
      {slide.duration && <div className="duration">{slide.duration}</div>}
      <footer><span>{String(index + 1).padStart(2, "0")}</span><p>Diego Carralbal · METSI · FCE UBA</p></footer>
      <nav className="controls" aria-label="Navegación de la presentación">
        <button onClick={controls.previous} disabled={index === 0} aria-label="Diapositiva anterior">←</button>
        <a href={notesHref} target="metsi-n01-speaker-notes" rel="noopener" aria-label="Abrir notas de orador en otra pestaña" title="Abrir notas de orador en otra pestaña">Notas ↗</a>
        <button onClick={controls.toggleFullscreen} aria-label="Pantalla completa">□</button>
        <button onClick={controls.next} disabled={index === slides.length - 1} aria-label="Diapositiva siguiente">→</button>
      </nav>
    </section>
  </main>;
}

createRoot(document.getElementById("root")).render(<App />);
