import fs from "node:fs";
import fsp from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";

const runtimeRequire = createRequire(
  "/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json",
);
const PptxGenJS = runtimeRequire("pptxgenjs");
const JSZip = runtimeRequire("jszip");

const root = process.cwd();
const mediaDir = path.join(root, ".class-deck-build", "N01", "v4-media");
const outputDir = path.join(root, "pedagogy", "presentations", "N01");
const outputPath = path.join(outputDir, "N01-METSI-material-de-clase-v4-video-pilot.pptx");

const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Diego Carralbal";
pptx.company = "FCE · UBA";
pptx.subject = "Material docente con video de fondo y notas de orador en voz natural";
pptx.title = "METSI · N01 · Del pedido al problema profesional";
pptx.lang = "es-AR";
pptx.theme = {
  headFontFace: "Didot",
  bodyFontFace: "Avenir",
  lang: "es-AR",
};
pptx.defineLayout({ name: "METSI_WIDE", width: 13.333333, height: 7.5 });
pptx.layout = "METSI_WIDE";

const C = {
  ink: "171817",
  paper: "F8F8F5",
  volt: "CFFF00",
  soft: "D9DBD8",
  muted: "A9ACA8",
  white: "FFFFFF",
};
const SANS = "Avenir";
const SERIF = "Didot";
const W = 13.333333;
const H = 7.5;

function dataUri(filePath) {
  const ext = path.extname(filePath).slice(1).toLowerCase();
  const mime = ext === "jpg" || ext === "jpeg" ? "image/jpeg" : "image/png";
  return `data:${mime};base64,${fs.readFileSync(filePath).toString("base64")}`;
}

const media = Object.fromEntries(
  ["road", "wires", "structure", "lights", "hotel"].map((name) => [name, {
    video: path.join(mediaDir, `${name}.mp4`),
    poster: dataUri(path.join(mediaDir, `${name}.png`)),
  }]),
);

function addBackground(slide, key, darkness = 42) {
  const asset = media[key];
  slide.addMedia({
    type: "video",
    path: asset.video,
    cover: asset.poster,
    x: 0,
    y: 0,
    w: W,
    h: H,
    objectName: `Fondo de video · ${key}`,
  });
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 0,
    w: W,
    h: H,
    line: { color: C.ink, transparency: 100 },
    fill: { color: C.ink, transparency: 100 - darkness },
  });
}

function addText(slide, text, x, y, w, h, options = {}) {
  slide.addText(text, {
    x, y, w, h,
    fontFace: options.fontFace ?? SANS,
    fontSize: options.fontSize ?? 22,
    color: options.color ?? C.white,
    bold: options.bold ?? false,
    italic: options.italic ?? false,
    align: options.align ?? "left",
    valign: options.valign ?? "top",
    margin: options.margin ?? 0,
    breakLine: false,
    fit: "shrink",
    paraSpaceAfterPt: options.paraSpaceAfterPt ?? 0,
    charSpacing: options.charSpacing,
    isTextBox: true,
    lineSpacingMultiple: options.lineSpacingMultiple,
    transparency: options.transparency,
  });
}

function addKicker(slide, number, stage) {
  slide.addShape(pptx.ShapeType.arc, {
    x: 0.62, y: 0.5, w: 0.5, h: 0.5,
    adjustPoint: 0.25,
    rotate: 45,
    fill: { color: C.ink, transparency: 100 },
    line: { color: C.white, transparency: 15, width: 1 },
  });
  addText(slide, String(number).padStart(2, "0"), 0.67, 0.67, 0.4, 0.15, {
    fontSize: 10.5, bold: true, align: "center", valign: "mid",
  });
  slide.addShape(pptx.ShapeType.parallelogram, {
    x: 1.25, y: 0.63, w: 0.68, h: 0.12,
    line: { color: C.volt, transparency: 100 },
    fill: { color: C.volt },
  });
  addText(slide, `METSI · N01   ${stage}`, 2.08, 0.59, 4.6, 0.22, {
    fontSize: 11, bold: true, color: C.white, charSpacing: 1.7,
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 6.6, y: 0.69, w: 5.9, h: 0,
    line: { color: C.white, transparency: 62, width: 0.8 },
  });
}

function addFooter(slide, number) {
  slide.addShape(pptx.ShapeType.line, {
    x: 0.62, y: 7.12, w: 12.08, h: 0,
    line: { color: C.white, transparency: 58, width: 0.7 },
  });
  addText(slide, String(number).padStart(2, "0"), 0.62, 7.2, 0.5, 0.12, { fontSize: 8.5, color: C.soft });
  addText(slide, "Diego Carralbal · METSI · FCE UBA", 9.55, 7.18, 3.15, 0.14, {
    fontSize: 8.5, color: C.soft, align: "right",
  });
}

function baseSlide(number, stage, video, darkness = 42) {
  const slide = pptx.addSlide();
  slide.background = { color: C.ink };
  addBackground(slide, video, darkness);
  addKicker(slide, number, stage);
  addFooter(slide, number);
  return slide;
}

function addVoltRule(slide, x, y, w = 0.8) {
  slide.addShape(pptx.ShapeType.line, {
    x, y, w, h: 0,
    line: { color: C.volt, width: 3 },
  });
}

function addNotes(slide, text) {
  slide.addNotes(text.replace(/\n{3,}/g, "\n\n").trim());
}

async function normalizePackage(filePath) {
  const zip = await JSZip.loadAsync(await fsp.readFile(filePath));
  const contentTypesPart = zip.file("[Content_Types].xml");
  let contentTypes = await contentTypesPart.async("string");
  contentTypes = contentTypes.replace(
    /<Override PartName="\/ppt\/slideMasters\/slideMaster(?:[2-9]|10)\.xml" ContentType="application\/vnd\.openxmlformats-officedocument\.presentationml\.slideMaster\+xml"\/>/g,
    "",
  );
  zip.file("[Content_Types].xml", contentTypes);
  for (let index = 1; index <= 10; index += 1) {
    const partName = `ppt/slides/slide${index}.xml`;
    const slidePart = zip.file(partName);
    let xml = await slidePart.async("string");
    xml = xml.replace(/<a:hlinkClick r:id="" action="ppaction:\/\/media"\/>/g, '<a:hlinkClick action="ppaction://media"/>');
    zip.file(partName, xml);
  }
  const normalized = await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" });
  await fsp.writeFile(filePath, normalized);
}

// 01 · Apertura
{
  const slide = baseSlide(1, "APERTURA", "road", 46);
  addText(slide, "La solución llega formulada.\nEl problema, todavía no.", 0.68, 1.45, 8.15, 2.15, {
    fontFace: SERIF, fontSize: 43, lineSpacingMultiple: 0.9,
  });
  addVoltRule(slide, 0.72, 4.06, 1.08);
  addText(slide, "¿Qué necesitamos comprender antes de comprometernos con una solución?", 0.72, 4.35, 7.1, 1.0, {
    fontSize: 20, color: C.paper,
  });
  addText(slide, "Hoy no venimos a repetir N01.\nVenimos a ponerlo a trabajar.", 8.95, 5.22, 3.2, 0.8, {
    fontFace: SERIF, fontSize: 20, italic: true, align: "right",
  });
  addNotes(slide, `Quiero empezar sin explicar nada. Imaginen que somos el equipo que recibió un pedido muy claro: comprar un nuevo PMS para el Hotel Horizonte. La solución ya viene nombrada, incluso parece urgente. La pregunta es qué necesitamos comprender antes de comprometernos con ella. Tómense unos segundos y elijan una palabra para nombrar el problema. Puede ser una falla, una demora, una descoordinación, una promesa comercial o algo distinto. No busco todavía la palabra correcta. Me interesa que escuchemos la diversidad de encuadres que aparece incluso cuando todos leímos el mismo material. Voy a registrar esas palabras porque al final vamos a volver a ellas. Si nuestras palabras cambian, también cambia lo que consideramos evidencia, la acción que parece razonable y quién debería poder decidir.`);
}

// 02 · Decisión inicial
{
  const slide = baseSlide(2, "DECISIÓN INICIAL", "structure", 52);
  addText(slide, "¿Comprar el PMS ahora?", 0.72, 1.25, 7.3, 0.72, { fontFace: SERIF, fontSize: 38 });
  addText(slide, "SÍ", 0.72, 2.55, 2.25, 0.8, { fontFace: SERIF, fontSize: 48 });
  addText(slide, "NO", 4.12, 2.55, 2.25, 0.8, { fontFace: SERIF, fontSize: 48 });
  addText(slide, "TODAVÍA NO", 7.3, 2.55, 4.4, 0.8, { fontFace: SERIF, fontSize: 48 });
  [0.72, 4.12, 7.3].forEach((x, i) => addVoltRule(slide, x, 3.55, i === 2 ? 1.65 : 0.7));
  addText(slide, "una razón", 0.72, 3.85, 2.3, 0.3, { fontSize: 15, color: C.soft });
  addText(slide, "una razón", 4.12, 3.85, 2.3, 0.3, { fontSize: 15, color: C.soft });
  addText(slide, "una razón", 7.3, 3.85, 2.3, 0.3, { fontSize: 15, color: C.soft });
  addText(slide, "+ una evidencia que falta", 0.72, 5.35, 7.0, 0.45, { fontSize: 22, bold: true });
  addText(slide, "10 MIN", 11.42, 5.35, 1.2, 0.35, { fontSize: 13, color: C.volt, bold: true, align: "right" });
  addNotes(slide, `Ahora sí, cada persona va a tomar una posición. La pregunta es concreta: ¿compraríamos el PMS ahora? Sólo hay tres respuestas posibles: sí, no o todavía no. Escriban su elección, una razón y una evidencia que hoy les falta. Una opción sin razón es apenas una preferencia; una razón sin evidencia faltante corre el riesgo de convertirse en una conclusión cerrada. Tienen dos minutos en silencio. Después voy a relevar la distribución, pero no vamos a debatir todavía cuál respuesta es correcta. Lo que quiero conservar es el punto de partida. Si eligieron “todavía no”, no alcanza con decir que falta información: nombren una observación posible, de qué fuente podría venir y qué decisión cambiaría. Si eligieron “sí” o “no”, hagan el mismo esfuerzo. Toda decisión profesional necesita mostrar qué la sostiene y qué podría revisarla.`);
}

// 03 · Pedido, problema, solución
{
  const slide = baseSlide(3, "COMPARAR ENCUADRES", "wires", 56);
  addText(slide, "Tres palabras que suelen mezclarse", 0.72, 1.15, 7.5, 0.6, { fontFace: SERIF, fontSize: 34 });
  const cols = [
    ["01", "PEDIDO", "Lo que alguien solicita"],
    ["02", "PROBLEMA", "La situación que todavía debemos explicar"],
    ["03", "SOLUCIÓN", "Una intervención posible, no un destino"],
  ];
  cols.forEach(([n, title, desc], index) => {
    const x = 0.72 + index * 4.15;
    addText(slide, n, x, 2.35, 0.42, 0.22, { fontSize: 10, bold: true, color: C.volt });
    addText(slide, title, x, 2.78, 3.55, 0.45, { fontFace: SERIF, fontSize: 29 });
    addVoltRule(slide, x, 3.48, 0.72);
    addText(slide, desc, x, 3.76, 3.45, 0.82, { fontSize: 17, color: C.soft });
  });
  addText(slide, "¿Qué diferencia cambiaría una decisión?", 0.72, 5.75, 10.8, 0.5, {
    fontFace: SERIF, fontSize: 25, italic: true,
  });
  addNotes(slide, `Vamos a comparar las palabras que aparecieron. Un pedido es lo que alguien solicita; un problema es la situación que todavía necesitamos comprender; una solución es una intervención posible. Las tres cosas pueden estar relacionadas, pero no son equivalentes. Si alguien pide un nuevo PMS, eso demuestra que existe un pedido. No demuestra todavía que el software actual sea la causa dominante. En grupos de cuatro, compartan el campo de HH-01 que les resultó más difícil y busquen dos diferencias entre sus versiones que podrían cambiar una decisión. No vale cerrar la conversación diciendo que falta toda la información. Elijan una diferencia concreta: qué actor queda fuera, qué propósito cambia, qué evidencia se considera suficiente o quién tiene autoridad. Quince minutos. Cuando volvamos, no me cuenten todo el memo. Tráiganme una diferencia y la consecuencia práctica que tendría.`);
}

// 04 · Dos HH-01
{
  const slide = baseSlide(4, "DOS VERSIONES", "lights", 58);
  addText(slide, "No gana el memo más prolijo", 0.72, 1.05, 8.0, 0.65, { fontFace: SERIF, fontSize: 36 });
  addText(slide, "Gana la diferencia que vuelve visible una consecuencia.", 0.72, 1.76, 8.2, 0.38, { fontSize: 18, color: C.soft });
  [0.72, 6.85].forEach((x, index) => {
    slide.addShape(pptx.ShapeType.rect, {
      x, y: 2.55, w: 5.75, h: 2.4,
      line: { color: C.white, transparency: 45, width: 1 },
      fill: { color: C.ink, transparency: 35 },
    });
    addText(slide, `HH-01 · ${index === 0 ? "A" : "B"}`, x + 0.28, 2.82, 1.4, 0.25, { fontSize: 12, bold: true, color: C.volt });
    addText(slide, index === 0 ? "“El problema es el sistema actual.”" : "“La promesa comercial no llega a operación.”", x + 0.28, 3.32, 5.05, 0.82, {
      fontFace: SERIF, fontSize: 25,
    });
    addText(slide, index === 0 ? "Próxima acción: reemplazar" : "Próxima acción: reconstruir el episodio", x + 0.28, 4.42, 5.05, 0.3, {
      fontSize: 15, color: C.soft,
    });
  });
  addText(slide, "¿Qué evidencia permitiría distinguirlos?", 0.72, 5.62, 8.8, 0.5, { fontFace: SERIF, fontSize: 25, italic: true });
  addNotes(slide, `Miren estas dos versiones. Las dos pueden estar bien escritas y las dos pueden parecer razonables. La primera convierte al sistema actual en el problema y habilita una acción de reemplazo. La segunda ubica la tensión entre una promesa comercial y la capacidad real de operación, y habilita una investigación del episodio. No vamos a elegir la más linda ni la que usa palabras más técnicas. Vamos a preguntar qué diferencia cambia una decisión y qué evidencia permitiría distinguirlas. Si el PMS respondió a tiempo, la primera explicación pierde fuerza. Si Comercial publicó una condición que Operaciones nunca validó, la segunda gana fuerza. Esto no significa que ya tengamos la verdad. Significa que el encuadre dejó de ser una opinión suelta y empezó a producir preguntas observables. Ese es el trabajo que vamos a hacer con nuestros propios memos.`);
}

// 05 · Prueba metodológica
{
  const slide = baseSlide(5, "CLÍNICA CONCEPTUAL", "structure", 55);
  addText(slide, "Una prueba en cuatro preguntas", 0.72, 1.05, 8.2, 0.65, { fontFace: SERIF, fontSize: 36 });
  const questions = [
    "¿Qué incertidumbre reducimos?",
    "¿Antes de qué decisión?",
    "¿Mediante qué evidencia?",
    "¿Qué resultado cambiaría el camino?",
  ];
  questions.forEach((question, index) => {
    const y = 2.05 + index * 0.92;
    addText(slide, `0${index + 1}`, 0.78, y + 0.1, 0.45, 0.2, { fontSize: 10, bold: true, color: C.volt });
    addText(slide, question, 1.55, y, 8.9, 0.5, { fontFace: SERIF, fontSize: 26 });
    slide.addShape(pptx.ShapeType.line, { x: 1.55, y: y + 0.63, w: 9.45, h: 0, line: { color: C.white, transparency: 70, width: 0.6 } });
  });
  addText(slide, "Si una actividad no responde estas preguntas, quizá produce movimiento, pero todavía no produce aprendizaje útil.", 8.95, 5.4, 3.2, 0.78, {
    fontSize: 16, color: C.soft, align: "right",
  });
  addNotes(slide, `Voy a detenerme sólo en dos confusiones que suelen aparecer. La primera es tomar el pedido como prueba del problema. La segunda es tomar una actividad como evidencia de aprendizaje. Para revisar ambas vamos a usar cuatro preguntas. ¿Qué incertidumbre reducimos? ¿Antes de qué decisión? ¿Mediante qué evidencia? ¿Qué resultado cambiaría el camino? Si no podemos responderlas, quizás estamos haciendo cosas, pero todavía no sabemos qué aprendemos ni para qué sirve. Apliquen la prueba a una acción de su memo. Por ejemplo, entrevistar a Recepción no es valioso por sí mismo. Se vuelve metodológicamente útil si busca distinguir entre una falla técnica y una regla operativa, antes de decidir un reemplazo, mediante evidencia del episodio, y si existe un resultado que nos haría abandonar la explicación inicial. Tienen doce minutos para probar y ajustar.`);
}

// 06 · Reconstrucción
{
  const slide = baseSlide(6, "RECONSTRUIR HH-01", "hotel", 58);
  addText(slide, "Una versión común,\nsin borrar el desacuerdo", 0.72, 1.08, 6.5, 1.25, { fontFace: SERIF, fontSize: 36 });
  const fields = ["pedido", "propósito", "incertidumbre", "evidencia", "actores", "autoridad", "próxima decisión"];
  fields.forEach((field, index) => {
    const row = index % 4;
    const col = index < 4 ? 0 : 1;
    const x = 7.45 + col * 2.55;
    const y = 1.26 + row * 1.05;
    addText(slide, String(index + 1).padStart(2, "0"), x, y, 0.35, 0.18, { fontSize: 9.5, bold: true, color: C.volt });
    addText(slide, field.toUpperCase(), x + 0.55, y - 0.03, 2.0, 0.24, { fontSize: 11.5, bold: true, charSpacing: 1 });
    slide.addShape(pptx.ShapeType.line, { x: x + 0.55, y: y + 0.35, w: 1.88, h: 0, line: { color: C.white, transparency: 55, width: 0.8 } });
  });
  addText(slide, "Producto: una segunda versión de HH-01 que otra persona pueda objetar y revisar.", 0.72, 5.35, 6.1, 0.8, { fontSize: 18, color: C.soft });
  addText(slide, "23 MIN", 11.42, 5.48, 1.2, 0.28, { fontSize: 13, color: C.volt, bold: true, align: "right" });
  addNotes(slide, `Ahora cada equipo va a construir una segunda versión común de HH-01. No buscamos que todos piensen igual. Buscamos que el desacuerdo quede ubicado en un campo que podamos revisar. Revisen pedido, propósito, incertidumbre, evidencia, actores, autoridad y próxima decisión. El memo no es un diagnóstico definitivo ni un plan completo. Es una forma de declarar qué creemos comprender, qué sigue abierto y qué acción pequeña queda autorizada. Conserven al menos un desacuerdo relevante y nombren a un actor que podría cuestionar el propósito que formularon. Mientras trabajan, háganse una pregunta incómoda: ¿qué evidencia adversa estaríamos dispuestos a aceptar? Si la respuesta es “ninguna”, el memo está defendiendo una conclusión previa. Tienen veintitrés minutos. El producto es una versión que otra persona pueda objetar y revisar, no una pieza cerrada.`);
}

// 07 · Perturbación
{
  const slide = baseSlide(7, "EVIDENCIA NUEVA", "wires", 60);
  addText(slide, "La evidencia debe poder incomodar", 0.72, 1.0, 8.5, 0.64, { fontFace: SERIF, fontSize: 35 });
  addText(slide, "Cada equipo recibe dos piezas.", 0.72, 1.73, 6.1, 0.32, { fontSize: 17, color: C.soft });
  const evidence = [
    "El PMS respondió a tiempo",
    "Recepción no pudo asignar la habitación",
    "Comercial publicó una condición no validada",
    "Una persona abandonó por accesibilidad",
    "El chatbot canceló sin confirmar identidad",
    "La sobreventa aparece sólo en un canal externo",
  ];
  evidence.forEach((item, index) => {
    const col = index % 2;
    const row = Math.floor(index / 2);
    const x = 0.72 + col * 6.15;
    const y = 2.45 + row * 1.05;
    addText(slide, String(index + 1).padStart(2, "0"), x, y + 0.06, 0.42, 0.18, { fontSize: 9.5, bold: true, color: C.volt });
    addText(slide, item, x + 0.55, y, 5.35, 0.56, { fontSize: 17.2, bold: true });
    slide.addShape(pptx.ShapeType.line, { x: x + 0.55, y: y + 0.67, w: 5.16, h: 0, line: { color: C.white, transparency: 70, width: 0.6 } });
  });
  addText(slide, "Registrar: qué cambia · qué se mantiene · qué acción queda autorizada", 0.72, 6.02, 10.9, 0.38, { fontSize: 17, color: C.soft });
  addNotes(slide, `Ahora voy a entregar dos piezas de evidencia a cada equipo. No fueron elegidas para confirmar lo que ustedes ya sostienen. Fueron elegidas para ponerlo a prueba. Puede aparecer que el PMS respondió a tiempo, que Recepción no pudo asignar una habitación declarada limpia, que Comercial publicó una condición no validada, que una persona abandonó por una barrera de accesibilidad, que el chatbot canceló sin confirmar identidad o que la sobreventa ocurre sólo en un canal externo. Lean las dos piezas y registren tres cosas: qué campo de HH-01 cambia, cuál se mantiene y qué nueva acción queda autorizada. No intenten hacer que toda la evidencia encaje a la fuerza. Si una pieza contradice su explicación, esa contradicción es valiosa. Tienen veinte minutos. Al final necesito ver una revisión explícita, incluso si la revisión consiste en sostener el encuadre y explicar por qué esta evidencia todavía no alcanza para cambiarlo.`);
}

// 08 · Objeción
{
  const slide = baseSlide(8, "REVISIÓN CRUZADA", "lights", 60);
  addText(slide, "Objetar no es resolver por otro", 0.72, 1.05, 8.7, 0.62, { fontFace: SERIF, fontSize: 35 });
  const steps = [
    ["01", "CITAR", "el campo cuestionado"],
    ["02", "MOSTRAR", "la relación que no se sostiene"],
    ["03", "PROPONER", "una prueba, no una solución"],
  ];
  steps.forEach(([n, verb, desc], index) => {
    const x = 0.72 + index * 4.16;
    addText(slide, n, x, 2.35, 0.4, 0.18, { fontSize: 10, bold: true, color: C.volt });
    addText(slide, verb, x, 2.82, 3.45, 0.44, { fontFace: SERIF, fontSize: 28 });
    addVoltRule(slide, x, 3.48, 0.7);
    addText(slide, desc, x, 3.82, 3.35, 0.64, { fontSize: 17, color: C.soft });
  });
  addText(slide, "Dos objeciones por memo. Las dos deben poder usarse.", 0.72, 5.55, 9.4, 0.42, { fontSize: 19, bold: true });
  addText(slide, "18 MIN", 11.42, 5.6, 1.2, 0.28, { fontSize: 13, color: C.volt, bold: true, align: "right" });
  addNotes(slide, `Intercambien ahora sus memos con otro equipo. La tarea no es corregir el trabajo ajeno ni imponer una solución. Cada equipo revisor va a formular dos objeciones que puedan usarse. La primera debe señalar una relación entre evidencia y decisión que todavía no se sostiene. La segunda debe detectar una condición de revisión demasiado vaga o imposible de observar. Para que la devolución sea útil, citen el campo cuestionado, expliquen qué relación es débil y propongan una prueba. Por ejemplo: “En evidencia afirman que el PMS falla, pero no muestran el tiempo acordado ni el registro del episodio; proponemos contrastar logs y secuencia operativa”. Eso es distinto de decir “cambien el sistema”. Tienen dieciocho minutos. Cuando reciban las objeciones, no se defiendan enseguida. Primero prueben si permiten mejorar el memo. Una buena revisión no cierra la discusión: hace más precisa la próxima decisión.`);
}

// 09 · Defensa
{
  const slide = baseSlide(9, "DEFENSA", "hotel", 64);
  addText(slide, "Noventa segundos. Cuatro frases.", 0.72, 1.03, 8.5, 0.66, { fontFace: SERIF, fontSize: 35 });
  const statements = [
    "Queremos sostener…",
    "La siguiente acción autorizada es…",
    "Por ahora no decidimos…",
    "Revisaríamos el encuadre si…",
  ];
  statements.forEach((item, index) => {
    const y = 2.05 + index * 0.9;
    addText(slide, String(index + 1).padStart(2, "0"), 0.78, y + 0.07, 0.42, 0.18, { fontSize: 10, bold: true, color: C.volt });
    addText(slide, item, 1.55, y, 9.7, 0.5, { fontFace: SERIF, fontSize: 25 });
    slide.addShape(pptx.ShapeType.line, { x: 1.55, y: y + 0.6, w: 9.65, h: 0, line: { color: C.white, transparency: 70, width: 0.6 } });
  });
  addText(slide, "La defensa muestra una posición y también su límite.", 7.55, 5.9, 4.0, 0.4, { fontSize: 17, color: C.soft, align: "right" });
  addNotes(slide, `Cada equipo dispone de noventa segundos. No necesitamos una descripción completa del memo. Necesitamos cuatro frases claras. La primera nombra el propósito que quieren sostener. La segunda declara la siguiente acción autorizada. La tercera dice qué decisión permanece deliberadamente cerrada. La cuarta identifica la evidencia que podría cambiar el encuadre. Voy a cuidar el tiempo porque la restricción nos obliga a priorizar. Si escuchamos sólo actividades, voy a preguntar qué decisión habilitan. Si escuchamos una conclusión sin límite, voy a preguntar qué no están autorizando todavía. Defender no significa fingir certeza. Significa mostrar una posición suficientemente sostenida para actuar y suficientemente abierta para ser revisada. Mientras escuchan a los demás, registren una frase que les ayude a mejorar su propio memo. No busquen copiar una respuesta; busquen una forma más precisa de conectar propósito, evidencia, decisión y condición de revisión.`);
}

// 10 · Cierre
{
  const slide = baseSlide(10, "CIERRE Y PUENTE", "road", 53);
  addText(slide, "Lo que cambió deja una huella", 0.72, 1.05, 8.4, 0.64, { fontFace: SERIF, fontSize: 36 });
  const cols = [
    ["ANTES PENSABA", "una idea inicial"],
    ["AHORA SOSTENGO", "una posición revisada"],
    ["TODAVÍA CAMBIARÍA SI", "una evidencia posible"],
  ];
  cols.forEach(([title, desc], index) => {
    const x = 0.72 + index * 4.15;
    addText(slide, title, x, 2.38, 3.55, 0.28, { fontSize: 11.5, bold: true, color: index === 1 ? C.volt : C.white, charSpacing: 1.2 });
    addText(slide, desc, x, 3.03, 3.5, 0.62, { fontFace: SERIF, fontSize: 24 });
    slide.addShape(pptx.ShapeType.line, { x, y: 3.92, w: 3.45, h: 0, line: { color: C.white, transparency: 50, width: 0.8 } });
  });
  addText(slide, "N02 abre la frontera: ¿qué relaciones forman el sistema relevante?", 0.72, 5.32, 9.8, 0.65, { fontFace: SERIF, fontSize: 24, italic: true });
  addNotes(slide, `Para cerrar, vuelvan a la posición que registraron al comienzo. Completen cinco frases: al comienzo pensaba, ahora sostengo, cambié por esta evidencia u objeción, todavía podría cambiar si, y para N02 necesito saber qué relaciones forman el sistema relevante. Háganlo en silencio. No hace falta que el cambio sea total. Puede haber cambiado una palabra, una relación o el límite de una decisión. Lo importante es que podamos reconstruir por qué cambió. Esa huella es evidencia de aprendizaje mucho más valiosa que decir “entendí”. Antes de irnos, quiero que miremos el recorrido completo: recibimos una solución formulada, distinguimos pedido y problema, comparamos encuadres, sometimos el memo a evidencia adversa, aceptamos objeciones y defendimos una decisión provisional. N02 retoma justamente lo que hoy dejamos abierto: dónde termina el sistema relevante y qué relaciones necesitamos incluir para no intervenir sobre una parte aislada.`);
}

await fsp.mkdir(outputDir, { recursive: true });
await pptx.writeFile({ fileName: outputPath, compression: true });
await normalizePackage(outputPath);
console.log(outputPath);
