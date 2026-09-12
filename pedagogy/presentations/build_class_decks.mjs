import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const workspaceDir = process.cwd();
const skillDir = "/Users/diegocarralbal/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.12148/skills/presentations";
const runtimeNode = "/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node";
const runtimeNodeModules = "/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules";
const runtimePython = "/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3";
process.env.RUNTIME_NODE = runtimeNode;
process.env.RUNTIME_NODE_MODULES = runtimeNodeModules;
const args = process.argv.slice(2);
const onlyIndex = args.indexOf("--only");
const only = onlyIndex >= 0 ? args[onlyIndex + 1]?.toUpperCase() : null;
const revisionIndex = args.indexOf("--revision");
const revision = revisionIndex >= 0 ? args[revisionIndex + 1] : "v1";
const startIndex = args.indexOf("--start");
const startAt = startIndex >= 0 ? args[startIndex + 1]?.toUpperCase() : null;
const endIndex = args.indexOf("--end");
const endAt = endIndex >= 0 ? args[endIndex + 1]?.toUpperCase() : null;

const { finalizePresentation } = await import(
  pathToFileURL(path.join(skillDir, "container_tools/artifact_tool_utils.mjs")).href,
);

const C = {
  paper: "#FAFAF8",
  ink: "#181817",
  gray: "#E4E6E5",
  line: "#AEB1AE",
  muted: "#5B5D59",
  volt: "#CFFF00",
  white: "#FFFFFF",
};
const FONT_SANS = "Avenir";
const FONT_SERIF = "Didot";
const slideSize = { width: 1280, height: 720 };
const expectedSlideSizeEmu = "12192000,6858000";

function cleanMd(value) {
  return value
    .replace(/`([^`]+)`/g, "$1")
    .replace(/\*\*([^*]+)\*\*/g, "$1")
    .replace(/\*([^*]+)\*/g, "$1")
    .replace(/\\\|/g, "|")
    .trim();
}

function section(md, heading) {
  const pattern = new RegExp(`^## ${heading}\\s*$([\\s\\S]*?)(?=^## |\\Z)`, "m");
  return md.match(pattern)?.[1]?.trim() ?? "";
}

function firstParagraph(md, heading) {
  return section(md, heading)
    .split(/\n\s*\n/)
    .map((item) => cleanMd(item.replace(/^#+\s*/, "")))
    .find(Boolean) ?? "";
}

function tableRows(md) {
  const lines = md.split("\n");
  const start = lines.findIndex((line) => /^\|\s*Pantalla\s*\|/.test(line));
  const rows = [];
  for (const line of lines.slice(start + 2)) {
    if (!line.startsWith("|")) break;
    const cells = line.slice(1, -1).split("|").map(cleanMd);
    if (cells.length >= 4 && /^\d+$/.test(cells[0])) {
      rows.push({ number: Number(cells[0]), visible: cells[1], note: cells[2], advance: cells[3] });
    }
  }
  if (rows.length !== 10) throw new Error(`Se esperaban 10 pantallas y se encontraron ${rows.length}`);
  return rows;
}

async function findCanonicalSource(n) {
  const entries = await fs.readdir(workspaceDir, { withFileTypes: true });
  const candidates = [];
  for (const entry of entries) {
    if (!entry.isDirectory() || !entry.name.startsWith(`${n}-`)) continue;
    const sourceDir = path.join(workspaceDir, entry.name, "source");
    try {
      for (const file of await fs.readdir(sourceDir)) {
        if (file.endsWith(".md") && /content|canonical|final/i.test(file)) {
          candidates.push(path.join(sourceDir, file));
        }
      }
    } catch {}
  }
  const preferred = candidates.sort((a, b) => {
    const score = (p) => (p.includes("v8-editorial") ? 30 : 0) + (p.includes("v18-final") ? 20 : 0) + (p.includes("content-final") ? 10 : 0);
    return score(b) - score(a) || a.localeCompare(b);
  })[0];
  if (!preferred) throw new Error(`No se encontró fuente canónica para ${n}`);
  return preferred;
}

function addRect(slide, left, top, width, height, fill, line = "none", radius = false) {
  return slide.shapes.add({
    geometry: radius ? "roundRect" : "rect",
    position: { left, top, width, height },
    fill,
    line: line === "none" ? { fill: "none", width: 0 } : { fill: line, width: 1 },
  });
}

function addText(slide, text, left, top, width, height, options = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position: { left, top, width, height },
    fill: "none",
    line: { fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    typeface: options.font ?? FONT_SANS,
    fontSize: options.size ?? 24,
    bold: options.bold ?? false,
    italic: options.italic ?? false,
    color: options.color ?? C.ink,
    autoFit: options.autoFit ?? "shrinkText",
    horizontalAlignment: options.align ?? "left",
    verticalAlignment: options.valign ?? "top",
  };
  return shape;
}

function addFrame(slide, n, number, stage = "ENCUENTRO") {
  slide.background.fill = C.paper;
  addRect(slide, 0, 0, 18, 720, C.volt);
  addText(slide, `${n}  ·  METSI`, 54, 34, 250, 28, { size: 16, bold: true, color: C.muted });
  addText(slide, String(number).padStart(2, "0"), 1140, 31, 70, 32, { size: 18, bold: true, align: "right" });
  addText(slide, stage, 960, 37, 155, 22, { size: 11, bold: true, color: C.muted, align: "right" });
  addRect(slide, 54, 82, 1160, 2, C.ink);
  addRect(slide, 54, 681, 1160, 1, C.line);
  addText(slide, "Metodología de Sistemas de Información · FCE UBA", 54, 688, 560, 20, { size: 11, color: C.muted });
}

function splitLabels(value) {
  const afterColon = value.includes(":") ? value.split(":").slice(1).join(":") : value;
  return afterColon
    .split(/,|\sy\s|\so\s|\//)
    .map((item) => item.trim())
    .filter(Boolean)
    .slice(0, 4);
}

function titleCase(value) {
  const text = value.replace(/^Pregunta profesional de N\d+$/i, "Pregunta profesional");
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function renderSlide(slide, row, context) {
  const { n, question, workshopResult } = context;
  addFrame(slide, n, row.number, row.number === 10 ? "CIERRE" : "ENCUENTRO");
  const title = titleCase(row.visible);

  if (row.number === 1) {
    addText(slide, "PREGUNTA PROFESIONAL", 74, 118, 500, 28, { size: 15, bold: true, color: C.muted });
    addText(slide, question || title, 74, 160, 1040, 290, { font: FONT_SERIF, size: 48 });
    addRect(slide, 74, 514, 88, 10, C.volt);
    addText(slide, "Respondé antes de explicar. La primera posición queda registrada para revisarla al cierre.", 74, 548, 910, 74, { size: 22, color: C.muted });
    return;
  }

  addText(slide, title, 74, 118, 1080, 88, { font: FONT_SERIF, size: 42 });

  if (row.number === 2) {
    addRect(slide, 74, 240, 1130, 250, C.gray);
    const prompts = ["POSICIÓN", "RAZÓN", "EVIDENCIA FALTANTE"];
    prompts.forEach((prompt, index) => {
      const left = 112 + index * 355;
      addText(slide, prompt, left, 280, 300, 28, { size: 15, bold: true, color: C.muted });
      addRect(slide, left, 332, 295, 2, index === 2 ? C.volt : C.ink);
      addText(slide, index === 0 ? "Tomá una posición antes de escuchar la explicación." : "Dejala escrita en una frase verificable.", left, 362, 292, 82, { size: 20 });
    });
    return;
  }

  if (row.number === 3) {
    const labels = splitLabels(row.visible);
    const shown = labels.length >= 3 ? labels.slice(0, 3) : ["Primera lectura", "Tensión", "Decisión"];
    shown.forEach((label, i) => {
      const left = 74 + i * 380;
      addText(slide, `0${i + 1}`, left, 246, 70, 30, { size: 16, bold: true, color: C.muted });
      addRect(slide, left, 286, 330, 3, i === 1 ? C.volt : C.ink);
      addText(slide, label, left, 312, 330, 105, { font: FONT_SERIF, size: 30 });
      addText(slide, "¿Qué cambia si esta distinción se formula de otro modo?", left, 448, 320, 80, { size: 18, color: C.muted });
    });
    return;
  }

  if (row.number === 4) {
    addText(slide, "A", 88, 260, 60, 60, { font: FONT_SERIF, size: 46 });
    addText(slide, "Primera evidencia o formulación", 150, 260, 410, 80, { size: 28, bold: true });
    addRect(slide, 634, 226, 2, 330, C.line);
    addText(slide, "B", 690, 260, 60, 60, { font: FONT_SERIF, size: 46 });
    addText(slide, "Evidencia o formulación contrastante", 752, 260, 410, 80, { size: 28, bold: true });
    addText(slide, "¿Qué diferencia modifica una decisión concreta?", 150, 430, 980, 62, { font: FONT_SERIF, size: 32, color: C.muted, align: "center" });
    return;
  }

  if (row.number === 5) {
    const labels = splitLabels(row.visible);
    const items = labels.length >= 3 ? labels : ["Qué se intenta sostener", "Qué evidencia existe", "Qué falta distinguir", "Qué decisión cambia"];
    items.slice(0, 4).forEach((label, i) => {
      const top = 230 + i * 90;
      addText(slide, String(i + 1).padStart(2, "0"), 88, top, 70, 34, { size: 16, bold: true, color: C.muted });
      addText(slide, label, 170, top - 4, 930, 48, { size: 27, bold: i === 0 });
      addRect(slide, 170, top + 48, 930, 1, C.line);
    });
    return;
  }

  if (row.number === 6) {
    addRect(slide, 74, 222, 1130, 338, C.gray);
    addText(slide, "TRABAJO DE EQUIPO", 104, 248, 300, 24, { size: 15, bold: true, color: C.muted });
    addText(slide, "Artefacto en construcción", 104, 294, 820, 70, { font: FONT_SERIF, size: 36 });
    addText(slide, "Dejen visible la hipótesis, la evidencia usada, la decisión que habilita y la condición que podría revisarla.", 104, 410, 880, 100, { size: 23 });
    addText(slide, "TIEMPO", 1010, 258, 120, 24, { size: 14, bold: true, color: C.muted, align: "center" });
    addText(slide, "en pantalla", 1008, 308, 125, 60, { font: FONT_SERIF, size: 26, align: "center" });
    return;
  }

  if (row.number === 7) {
    addText(slide, "EVIDENCIA NUEVA", 74, 245, 1090, 70, { size: 54, bold: true });
    addRect(slide, 74, 340, 112, 12, C.volt);
    addText(slide, "No la usen para defender la primera respuesta. Úsenla para localizar qué parte del razonamiento debe cambiar y qué parte todavía se sostiene.", 74, 390, 1020, 150, { font: FONT_SERIF, size: 33 });
    return;
  }

  if (row.number === 8) {
    const items = ["Citar el punto observado", "Nombrar la relación débil", "Proponer una prueba", "Evitar resolver por el otro equipo"];
    items.forEach((item, i) => {
      const left = 74 + (i % 2) * 565;
      const top = 235 + Math.floor(i / 2) * 160;
      addText(slide, String(i + 1).padStart(2, "0"), left, top, 56, 30, { size: 15, bold: true, color: C.muted });
      addText(slide, item, left + 64, top - 6, 450, 74, { size: 27, bold: true });
      addRect(slide, left + 64, top + 78, 420, 2, i === 2 ? C.volt : C.line);
    });
    return;
  }

  if (row.number === 9) {
    const items = ["Qué sostenemos", "Qué evidencia usamos", "Qué decidimos", "Qué podría hacernos revisar"];
    items.forEach((item, i) => {
      addText(slide, `0${i + 1}`, 80, 224 + i * 92, 65, 36, { size: 18, bold: true, color: C.muted });
      addText(slide, item, 165, 217 + i * 92, 840, 54, { font: FONT_SERIF, size: 30 });
      addRect(slide, 1015, 238 + i * 92, 130, 3, i === 3 ? C.volt : C.ink);
    });
    return;
  }

  addText(slide, "ANTES PENSABA", 74, 230, 340, 28, { size: 15, bold: true, color: C.muted });
  addText(slide, "AHORA SOSTENGO", 470, 230, 340, 28, { size: 15, bold: true, color: C.muted });
  addText(slide, "TODAVÍA REVISARÍA SI", 866, 230, 340, 28, { size: 15, bold: true, color: C.muted });
  [74, 470, 866].forEach((left, i) => addRect(slide, left, 278, 338, 230, i === 1 ? C.gray : C.white, C.line));
  addText(slide, workshopResult, 74, 548, 1080, 70, { size: 19, color: C.muted });
}

function listItems(md, heading) {
  return section(md, heading)
    .split("\n")
    .filter((line) => /^- /.test(line.trim()))
    .map((line) => cleanMd(line.trim().slice(2)));
}

function buildNotes(row, context) {
  const probes = Array.from({ length: Math.min(3, context.probes.length) }, (_, offset) => {
    const index = (row.number - 1 + offset) % context.probes.length;
    return `• ${context.probes[index]}`;
  }).join("\n");
  return [
    `PROPÓSITO DE LA PANTALLA\n${row.visible}`,
    `FACILITACIÓN SINCRÓNICA\n${row.note}\nSeñal para avanzar: ${row.advance}`,
    `USO ASINCRÓNICO\nPresentar la pantalla como consigna de pausa. Pedir una respuesta breve o una marca sobre el artefacto antes de habilitar la pantalla siguiente. No convertirla en explicación grabada del texto ya leído.`,
    probes ? `PREGUNTAS DE SONDEO POSIBLES\n${probes}` : "",
    `RESULTADO DEL ENCUENTRO\n${context.workshopResult}`,
  ].filter(Boolean).join("\n\n");
}

async function buildDeck(n) {
  const pedagogyDir = path.join(workspaceDir, "pedagogy", n);
  const guionPath = path.join(pedagogyDir, "GUION-DOCENTE.md");
  const tallerPath = path.join(pedagogyDir, "TALLER-SINCRONICO.md");
  const prepPath = path.join(pedagogyDir, "PREPARACION-ASINCRONICA.md");
  const [guion, taller, prep] = await Promise.all([
    fs.readFile(guionPath, "utf8"),
    fs.readFile(tallerPath, "utf8"),
    fs.readFile(prepPath, "utf8"),
  ]);
  const sourcePath = await findCanonicalSource(n);
  const source = await fs.readFile(sourcePath, "utf8");
  const h1 = source.match(/^#\s+(.+)$/m)?.[1] ?? n;
  const question = firstParagraph(source, "Pregunta profesional");
  const workshopResult = firstParagraph(taller, "Resultado del encuentro");
  const prepPurpose = firstParagraph(prep, "Propósito");
  const rows = tableRows(guion);
  const probes = listItems(guion, "Preguntas de sondeo");
  const context = { n, h1, question, workshopResult, prepPurpose, probes };

  const presentation = Presentation.create({ slideSize });
  presentation.title = `${n} · METSI · Material de clase`;
  presentation.subject = "Soporte visual con notas de orador para encuentros sincrónicos y asincrónicos";
  for (const row of rows) {
    const slide = presentation.slides.add();
    renderSlide(slide, row, context);
    slide.speakerNotes.textFrame.setText(buildNotes(row, context));
    slide.speakerNotes.setVisible(true);
  }

  const privateDir = path.join(workspaceDir, ".class-deck-build", n);
  const outputDir = path.join(workspaceDir, "pedagogy", "presentations", n);
  await fs.mkdir(privateDir, { recursive: true });
  await fs.mkdir(outputDir, { recursive: true });
  const finalPath = path.join(outputDir, `${n}-METSI-material-de-clase-${revision}.pptx`);
  const candidatePath = path.join(privateDir, `candidate-${revision}.pptx`);
  await (await PresentationFile.exportPptx(presentation)).save(candidatePath);

  await finalizePresentation({
    explicitTotalSlideCount: 10,
    workspaceDir,
    candidatePath,
    finalPath,
    pythonExecutable: runtimePython,
    integrityValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_package_integrity.py"),
    layoutValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_layout_geometry.py"),
    layoutArgs: [
      "--expected-slide-size-emu", expectedSlideSizeEmu,
      "--validate-heading-fit",
    ],
    requiredNativeTableOwnerSlides: [],
    requiredNativeChartOwnerSlides: [],
    fontPolicy: {
      basis: "design",
      families: [FONT_SANS, FONT_SERIF],
    },
    verifyArtifactToolImport: true,
    receiptPath: path.join(privateDir, `${path.basename(finalPath)}.validation.json`),
  });
  return finalPath;
}

const documents = Array.from({ length: 36 }, (_, index) => `N${String(index + 1).padStart(2, "0")}`)
  .filter((n) => !only || n === only)
  .filter((n) => !startAt || n >= startAt)
  .filter((n) => !endAt || n <= endAt);
if (!documents.length) throw new Error(`Documento no reconocido: ${only}`);

for (const n of documents) {
  const finalPath = await buildDeck(n);
  console.log(`${n}\t${path.relative(workspaceDir, finalPath)}`);
}
