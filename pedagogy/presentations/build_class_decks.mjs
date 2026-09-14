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
  const manifest = JSON.parse(await fs.readFile(path.join(workspaceDir, "course-manifest.json"), "utf8"));
  const record = manifest.documents.find((item) => item.code === n);
  if (!record) throw new Error(`No se encontró ${n} en course-manifest.json`);
  if (record.canonical_source) return path.join(workspaceDir, record.canonical_source);

  const packageDir = path.dirname(path.dirname(path.join(workspaceDir, record.pdf)));
  const sourceDir = path.join(packageDir, "source");
  const candidates = (await fs.readdir(sourceDir))
    .filter((file) => file.endsWith(".md"))
    .map((file) => path.join(sourceDir, file));
  const preferred = candidates.filter((file) => /-v2\.md$/.test(file));
  if (preferred.length === 1) return preferred[0];
  if (candidates.length !== 1) {
    throw new Error(`${n}: no se pudo resolver una fuente canónica única en ${path.relative(workspaceDir, sourceDir)}`);
  }
  return candidates[0];
}

function workshopSteps(md) {
  const matches = [...md.matchAll(/^###\s+(\d+)\.\s+(.+?),\s+(\d+)\s+minutos\s*$/gm)];
  const steps = matches.map((match, index) => {
    const end = matches[index + 1]?.index ?? md.indexOf("\n## ", match.index + match[0].length);
    const raw = md.slice(match.index + match[0].length, end >= 0 ? end : undefined).trim();
    const body = cleanMd(raw.replace(/^[-*]\s+/gm, "").replace(/\n+/g, " "));
    return { number: Number(match[1]), title: cleanMd(match[2]), minutes: Number(match[3]), body };
  });
  if (steps.length !== 8) throw new Error(`Se esperaban 8 momentos de taller y se encontraron ${steps.length}`);
  return steps;
}

function compactInstruction(value, maximum = 290) {
  if (value.length <= maximum) return value;
  const clipped = value.slice(0, maximum);
  const sentence = clipped.lastIndexOf(". ");
  const space = clipped.lastIndexOf(" ");
  return `${clipped.slice(0, sentence > maximum * 0.55 ? sentence + 1 : space)}…`;
}

function blockFor(n) {
  const number = Number(n.slice(1));
  if (number <= 4) return "BLOQUE A · ENCUADRE";
  if (number <= 10) return "BLOQUE B · INVESTIGACIÓN";
  if (number <= 16) return "BLOQUE C · MODELADO";
  if (number <= 20) return "BLOQUE D · ESTRATEGIA";
  if (number <= 25) return "BLOQUE E · PRODUCTO Y FLUJO";
  if (number <= 30) return "BLOQUE F · OPERACIÓN";
  if (number <= 33) return "BLOQUE G · IA";
  return "BLOQUE H · INTEGRACIÓN";
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
  addText(slide, `${blockFor(n)}  ·  ${stage}`, 760, 37, 355, 22, { size: 11, bold: true, color: C.muted, align: "right" });
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
  const { n, h1, question, workshopResult } = context;
  addFrame(slide, n, row.number, row.number === 10 ? "CIERRE" : "ENCUENTRO");
  const activity = row.number >= 2 && row.number <= 9 ? context.steps[row.number - 2] : null;
  const title = activity?.title ?? titleCase(row.visible);
  const instruction = activity ? compactInstruction(activity.body) : "";

  if (row.number === 1) {
    addText(slide, "PREGUNTA PROFESIONAL", 74, 118, 500, 28, { size: 15, bold: true, color: C.muted });
    addText(slide, h1.replace(/^N\d+\s*·\s*/, ""), 760, 118, 385, 42, { size: 15, bold: true, color: C.muted, align: "right" });
    addText(slide, question || title, 74, 170, 1040, 280, { font: FONT_SERIF, size: 46 });
    addRect(slide, 74, 514, 88, 10, C.volt);
    addText(slide, "Respondé antes de explicar. La primera posición queda registrada para revisarla al cierre.", 74, 548, 910, 74, { size: 22, color: C.muted });
    return;
  }

  addText(slide, title, 74, 112, 920, 84, { font: FONT_SERIF, size: 40 });
  if (activity) {
    addRect(slide, 1050, 126, 130, 54, C.gray, C.line, true);
    addText(slide, `${activity.minutes} MIN`, 1050, 139, 130, 26, { size: 15, bold: true, align: "center" });
  }

  if (row.number === 2) {
    addText(slide, instruction, 74, 205, 1080, 82, { size: 20, color: C.muted });
    addRect(slide, 74, 305, 1130, 218, C.gray);
    const prompts = ["POSICIÓN", "RAZÓN", "EVIDENCIA FALTANTE"];
    prompts.forEach((prompt, index) => {
      const left = 112 + index * 355;
      addText(slide, prompt, left, 340, 300, 28, { size: 15, bold: true, color: C.muted });
      addRect(slide, left, 390, 295, 2, index === 2 ? C.volt : C.ink);
      addText(slide, index === 0 ? "Una frase antes de debatir." : "Una relación que otra persona pueda revisar.", left, 416, 292, 70, { size: 19 });
    });
    return;
  }

  if (row.number === 3) {
    addText(slide, instruction, 74, 205, 1080, 72, { size: 20, color: C.muted });
    const labels = splitLabels(row.visible);
    const shown = labels.length >= 3 ? labels.slice(0, 3) : ["Primera lectura", "Tensión", "Decisión"];
    shown.forEach((label, i) => {
      const left = 74 + i * 380;
      addText(slide, `0${i + 1}`, left, 306, 70, 30, { size: 16, bold: true, color: C.muted });
      addRect(slide, left, 346, 330, 3, i === 1 ? C.volt : C.ink);
      addText(slide, label, left, 372, 330, 90, { font: FONT_SERIF, size: 28 });
      addText(slide, "¿Qué diferencia cambia la decisión?", left, 480, 320, 58, { size: 18, color: C.muted });
    });
    return;
  }

  if (row.number === 4) {
    addText(slide, instruction, 74, 205, 1080, 76, { size: 20, color: C.muted });
    addText(slide, "A", 88, 330, 60, 60, { font: FONT_SERIF, size: 46 });
    addText(slide, "Lo que el artefacto afirma", 150, 330, 410, 80, { size: 27, bold: true });
    addRect(slide, 634, 296, 2, 276, C.line);
    addText(slide, "B", 690, 330, 60, 60, { font: FONT_SERIF, size: 46 });
    addText(slide, "Lo que la evidencia permite afirmar", 752, 330, 410, 80, { size: 27, bold: true });
    addText(slide, "La diferencia debe conducir a una revisión observable.", 150, 488, 980, 62, { font: FONT_SERIF, size: 29, color: C.muted, align: "center" });
    return;
  }

  if (row.number === 5) {
    addText(slide, instruction, 74, 205, 1080, 68, { size: 20, color: C.muted });
    const labels = splitLabels(row.visible);
    const items = labels.length >= 3 ? labels : ["Qué se intenta sostener", "Qué evidencia existe", "Qué falta distinguir", "Qué decisión cambia"];
    items.slice(0, 4).forEach((label, i) => {
      const top = 300 + i * 72;
      addText(slide, String(i + 1).padStart(2, "0"), 88, top, 70, 34, { size: 16, bold: true, color: C.muted });
      addText(slide, label, 170, top - 4, 930, 42, { size: 24, bold: i === 0 });
      addRect(slide, 170, top + 42, 930, 1, C.line);
    });
    return;
  }

  if (row.number === 6) {
    addRect(slide, 74, 222, 1130, 354, C.gray);
    addText(slide, "TRABAJO DE EQUIPO", 104, 248, 300, 24, { size: 15, bold: true, color: C.muted });
    addText(slide, cleanMd(row.visible), 104, 294, 820, 60, { font: FONT_SERIF, size: 34 });
    addText(slide, instruction, 104, 382, 850, 142, { size: 21 });
    addText(slide, "TIEMPO", 1010, 258, 120, 24, { size: 14, bold: true, color: C.muted, align: "center" });
    addText(slide, `${activity.minutes}\nminutos`, 1008, 308, 125, 76, { font: FONT_SERIF, size: 24, align: "center" });
    return;
  }

  if (row.number === 7) {
    addText(slide, "EVIDENCIA NUEVA", 74, 235, 1090, 64, { size: 48, bold: true });
    addRect(slide, 74, 324, 112, 12, C.volt);
    addText(slide, instruction, 74, 370, 1050, 150, { font: FONT_SERIF, size: 30 });
    addText(slide, "Localicen qué cambia, qué se sostiene y qué todavía falta probar.", 74, 542, 1050, 52, { size: 20, color: C.muted });
    return;
  }

  if (row.number === 8) {
    addText(slide, instruction, 74, 205, 1080, 70, { size: 20, color: C.muted });
    const items = ["Citar el punto observado", "Nombrar la relación débil", "Proponer una prueba", "Evitar resolver por el otro equipo"];
    items.forEach((item, i) => {
      const left = 74 + (i % 2) * 565;
      const top = 315 + Math.floor(i / 2) * 130;
      addText(slide, String(i + 1).padStart(2, "0"), left, top, 56, 30, { size: 15, bold: true, color: C.muted });
      addText(slide, item, left + 64, top - 6, 450, 74, { size: 27, bold: true });
      addRect(slide, left + 64, top + 78, 420, 2, i === 2 ? C.volt : C.line);
    });
    return;
  }

  if (row.number === 9) {
    addText(slide, instruction, 74, 205, 1080, 68, { size: 20, color: C.muted });
    const items = ["Qué sostenemos", "Qué evidencia usamos", "Qué decidimos", "Qué podría hacernos revisar"];
    items.forEach((item, i) => {
      addText(slide, `0${i + 1}`, 80, 300 + i * 72, 65, 32, { size: 16, bold: true, color: C.muted });
      addText(slide, item, 165, 293 + i * 72, 840, 48, { font: FONT_SERIF, size: 27 });
      addRect(slide, 1015, 314 + i * 72, 130, 3, i === 3 ? C.volt : C.ink);
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
  const activity = row.number >= 2 && row.number <= 9 ? context.steps[row.number - 2] : null;
  const activityNote = activity
    ? `CONSIGNA VISIBLE Y TIEMPO\n${activity.title} · ${activity.minutes} minutos\n${activity.body}`
    : "";
  return [
    `PROPÓSITO DE LA PANTALLA\n${row.visible}`,
    activityNote,
    `FACILITACIÓN SINCRÓNICA\n${row.note}\nSeñal para avanzar: ${row.advance}`,
    `USO ASINCRÓNICO\n${context.prepPurpose}\nPresentar esta pantalla como una estación de trabajo. Pedir evidencia visible antes de habilitar la siguiente y abrir una devolución breve entre pares. No convertirla en explicación grabada del texto ya leído.`,
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
  const steps = workshopSteps(taller);
  const probes = listItems(guion, "Preguntas de sondeo");
  const context = { n, h1, question, workshopResult, prepPurpose, probes, steps };

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
