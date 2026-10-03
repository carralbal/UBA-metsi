import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.METSI_PLAYWRIGHT_PATH || 'playwright');

const root = path.resolve(import.meta.dirname, '..');
const output = path.resolve(import.meta.dirname, 'output');
const webSource = fs.readFileSync(path.join(root, 'site/covers/recorrido/index.html'), 'utf8');
const findObject = (name, next) => {
  const re = new RegExp(`const ${name} = ([\\s\\S]*?);\\s*const ${next} =`);
  const match = webSource.match(re);
  if (!match) throw new Error(`No se encontró ${name} en el recorrido aprobado`);
  return vm.runInNewContext(`(${match[1]})`);
};
const readings = findObject('readings', 'stages');
const stages = findObject('stages', 'diagrams');
const diagrams = findObject('diagrams', 'host');
if (Object.keys(readings).length !== 36 || stages.length !== 8) throw new Error('El recorrido no tiene N01–N36 y A–H completos');
fs.mkdirSync(output, { recursive: true });

const esc = value => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const folio = index => `12${'ABCDEF'[index]}`;
const footer = index => `<footer><span>${folio(index)} · N00 / MAPA DE APRENDIZAJE</span><span>Diego Carralbal, 2026 · METSI · FCE UBA</span></footer>`;
const stageBlock = stage => `<section class="station ${stage.ns.length <= 3 ? 'short' : ''}" aria-label="Estación ${stage.letter}: ${stage.name}">
  <div class="stage-header"><div class="stage-marker">${stage.letter}</div><div class="stage-heading"><p class="range">${stage.range} · ESTACIÓN ${stage.letter}</p><h2>${esc(stage.name)}</h2><p class="change">${esc(stage.change)}</p></div><div class="diagram">${diagrams[stage.id]}</div></div>
  <div class="readings">${stage.ns.map(n => `<article class="reading"><b>${n}</b><div><h3>${esc(readings[n][0])}</h3><p>${esc(readings[n][1])}</p></div></article>`).join('')}</div>
  <div class="outcome"><span>LO QUE DEJA</span><p>${esc(stage.outcome)}</p></div>
</section>`;

const opening = `<section class="sheet opening">
  <div class="topline"><i></i><span>METSI · N00 · MAPA DE APRENDIZAJE</span></div>
  <h1>Un recorrido que cambia<br>cómo decidís.</h1>
  <p class="opening-deck">De entender qué pasa a comprobar si el cambio sirve y aprender de sus resultados.</p>
  <div class="guide"><strong>N00</strong><div><span>ANTES DE LAS LECTURAS</span><h2>Preparar el viaje.</h2><p>Cómo vamos a aprender y cuál es el hotel que usaremos como ejemplo. Es la guía, no una lectura más.</p></div></div>
  <div class="route-overview"><div class="route-label">OCHO ESTACIONES · UNA CAPACIDAD ACUMULATIVA</div>
    ${stages.map((s,i) => `<div class="route-step"><span class="route-dot ${i===0?'first':''}">${s.letter}</span><span class="route-range">${s.range}</span><h3>${esc(s.name)}</h3><p>${esc(s.change)}</p></div>`).join('')}
  </div><p class="opening-note">Las páginas siguientes despliegan cada tramo. Cada lectura agrega una pregunta o una práctica que prepara la siguiente decisión.</p>
  ${footer(0)}
</section>`;

const pair = (left, right, index) => `<section class="sheet pair">
  <header><span>METSI · N00</span><span>EL RECORRIDO · ${left.letter}–${right.letter}</span></header>
  <div class="pair-title"><span>${String(index).padStart(2,'0')} / 04</span><h1>${['Entender antes de resolver.','Representar para decidir.','Entregar y sostener.','Gobernar y aprender.'][index-1]}</h1></div>
  <div class="pair-body">${stageBlock(left)}${stageBlock(right)}</div>
  ${footer(index)}
</section>`;

const close = `<section class="sheet close">
  <div class="topline"><i></i><span>METSI · N00 · DEL PEDIDO AL APRENDIZAJE</span></div>
  <h1>El viaje no termina<br>en la entrega.</h1>
  <p class="close-deck">Cada estación deja una capacidad que modifica la siguiente. N36 devuelve lo aprendido al comienzo: la próxima pregunta ya no es la misma.</p>
  <div class="five-moves"><div class="flowline" aria-hidden="true"></div>
    <div class="move"><b>01</b><h2>Entender</h2><p>A–B · Una pregunta contrastada con pruebas y un problema investigable.</p></div>
    <div class="move"><b>02</b><h2>Representar</h2><p>C · Estados, flujos y contradicciones visibles.</p></div>
    <div class="move"><b>03</b><h2>Cambiar</h2><p>D–E · Una estrategia revisable y un corte útil, probado y terminado.</p></div>
    <div class="move"><b>04</b><h2>Sostener</h2><p>F–G · Servicio recuperable e IA con control humano.</p></div>
    <div class="move"><b>05</b><h2>Aprender</h2><p>H · Criterios que otras personas pueden usar y revisar.</p></div>
  </div>
  <div class="return"><span>N36 → PRÓXIMO RECORRIDO</span><p>Lo aprendido cambia la próxima pregunta, no sólo la respuesta anterior.</p></div>
  ${footer(5)}
</section>`;

const html = `<!doctype html><html lang="es-AR"><head><meta charset="utf-8"><title>METSI · N00 · Recorrido de aprendizaje</title><style>
@page{size:A4;margin:0}*{box-sizing:border-box}html,body{margin:0;padding:0}body{color:#191919;background:#f8f8f5;font-family:Avenir,'Avenir Next',Arial,sans-serif;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.sheet{position:relative;width:210mm;height:297mm;overflow:hidden;padding:17mm 17mm 16mm;background:#fafaf8;page-break-after:always}.sheet:last-child{page-break-after:auto}
footer{position:absolute;bottom:10mm;left:17mm;right:17mm;display:flex;justify-content:space-between;border-top:.25mm solid #aaa;padding-top:2.3mm;color:#62645f;font-size:7pt;letter-spacing:.015em}
.topline{display:flex;align-items:center;gap:5mm;font-size:8pt;font-weight:700;letter-spacing:.16em}.topline i{display:block;width:15mm;height:2.7mm;background:#cfff00;transform:skew(-25deg)}
h1,h2,h3,p{margin:0}h1,h2{font-weight:400;font-family:Didot,'Bodoni 72',Baskerville,Georgia,serif}h3{font-weight:600}
.opening h1,.close h1{font-size:42pt;line-height:.98;letter-spacing:-.025em;margin:10mm 0 4mm}.opening-deck,.close-deck{font:400 15pt/1.28 Baskerville,Georgia,serif;color:#555852;max-width:155mm}
.guide{display:grid;grid-template-columns:27mm 1fr;gap:7mm;margin-top:11mm;padding:6mm 7mm 6.5mm;background:#202120;color:#f9f9f5}.guide strong{font-size:20pt;letter-spacing:.04em}.guide span{font-size:7pt;font-weight:700;letter-spacing:.12em}.guide h2{font-size:21pt;margin:1mm 0}.guide p{font-size:9pt;line-height:1.35;color:#dfdfda}
.route-overview{position:relative;margin:9mm 0 0 5mm;padding-left:11mm;border-left:.4mm solid #212222}.route-label{margin-left:-6mm;margin-bottom:4mm;font-size:7.2pt;font-weight:700;letter-spacing:.13em}.route-step{position:relative;display:grid;grid-template-columns:20mm 39mm 1fr;align-items:baseline;gap:2mm;min-height:15mm;padding:2mm 0 1.8mm;border-top:.2mm solid #c4c5bd}.route-step:first-of-type{border-top:0}.route-dot{position:absolute;left:-16.8mm;top:2mm;display:grid;place-items:center;width:10.5mm;height:10.5mm;border:.35mm solid #202120;border-radius:50%;background:#fafaf8;font:400 17pt/1 Didot,serif}.route-dot.first{background:#cfff00}.route-range{font-size:7.6pt;font-weight:700;letter-spacing:.06em}.route-step h3{font:400 17pt/1 Didot,serif}.route-step p{font:400 8.7pt/1.25 Baskerville,Georgia,serif;color:#595b56}.opening-note{margin:4mm 0 0 16mm;font:italic 10pt/1.3 Baskerville,Georgia,serif;color:#555852}
.pair header{display:flex;justify-content:space-between;padding-bottom:2.6mm;border-bottom:.35mm solid #343534;font-size:7.2pt;font-weight:700;letter-spacing:.14em}.pair-title{display:flex;align-items:baseline;gap:7mm;margin:5mm 0 4mm}.pair-title span{font-size:7.5pt;font-weight:700;letter-spacing:.12em}.pair-title h1{font-size:27pt;line-height:1}.pair-body{position:relative;border-left:.28mm solid #373936;margin-left:8mm;padding-left:10mm}.station{position:relative;min-height:112mm;padding:2mm 0 4mm;border-bottom:.22mm solid #bfc1ba}.station:last-child{border-bottom:0;padding-top:6mm}.station:before{content:'';position:absolute;left:-10.4mm;top:8mm;width:9.5mm;height:.3mm;background:#373936}.stage-header{display:grid;grid-template-columns:14mm 1fr 54mm;gap:4mm;align-items:start;min-height:34mm}.stage-marker{position:relative;left:-16.6mm;display:grid;place-items:center;width:14mm;height:14mm;border:.3mm solid #202120;border-radius:50%;background:#fafaf8;font:400 25pt/1 Didot,serif}.stage-heading{margin-left:-15mm}.range{font-size:7pt;font-weight:700;letter-spacing:.13em}.stage-heading h2{font-size:23pt;line-height:.98;margin:1.5mm 0}.change{font:italic 9.5pt/1.18 Baskerville,Georgia,serif;color:#5c5e58}.diagram{height:32mm;overflow:hidden}.diagram svg{display:block;width:100%;height:100%}.diagram svg text{font-family:Avenir,Arial,sans-serif;font-size:13px;font-weight:700;fill:#202120}.diagram svg .muted{fill:#62655f;font-weight:400}.diagram svg .line{stroke:#202120;stroke-width:1.5;fill:none}.diagram svg .soft{stroke:#b9bcb4;stroke-width:1.5;fill:none}.diagram svg .dash{stroke:#202120;stroke-width:1.5;stroke-dasharray:3 5;fill:none}.diagram svg .volt{fill:#cfff00}.diagram svg .paper{fill:#fafaf8}.diagram svg .shade{fill:#e5e5de}
.readings{display:grid;grid-template-columns:1fr 1fr;gap:0 7mm;border-top:.2mm solid #bfc1ba;margin-top:2mm}.reading{display:grid;grid-template-columns:11mm 1fr;gap:2mm;padding:2.4mm 0 1.8mm;border-bottom:.18mm solid #d0d2cb;break-inside:avoid}.reading b{font-size:8pt;letter-spacing:.05em}.reading h3{font-size:9.6pt;line-height:1.12;margin-bottom:.5mm}.reading p{font:400 9.2pt/1.19 Baskerville,Georgia,serif;color:#30312e}.outcome{display:flex;gap:4mm;align-items:baseline;margin-top:3mm}.outcome span{white-space:nowrap;font-size:7pt;font-weight:700;letter-spacing:.11em}.outcome p{font:italic 9.2pt/1.2 Baskerville,Georgia,serif;color:#4f514d}.station.short{min-height:105mm}
.close h1{margin-bottom:6mm}.close-deck{max-width:155mm}.five-moves{position:relative;margin:13mm 0 0 7mm;padding-left:13mm}.flowline{position:absolute;top:1mm;bottom:0;left:0;width:.35mm;background:#282a27}.move{position:relative;display:grid;grid-template-columns:16mm 46mm 1fr;align-items:baseline;gap:3mm;min-height:23mm;padding:3.5mm 0;border-top:.2mm solid #c4c5bd}.move:before{content:'';position:absolute;left:-17mm;top:5mm;width:7mm;height:7mm;background:#fafaf8;border:.3mm solid #252625;border-radius:50%}.move:first-of-type:before{background:#cfff00}.move b{font-size:8pt}.move h2{font-size:24pt;line-height:1}.move p{font:400 11pt/1.22 Baskerville,Georgia,serif;color:#4a4d47}.return{margin-top:7mm;background:#202120;color:#f8f8f4;padding:8mm 9mm;border-bottom:2mm solid #cfff00}.return span{font-size:7.5pt;font-weight:700;letter-spacing:.15em}.return p{font:400 20pt/1.08 Didot,serif;margin-top:3mm}
</style></head><body>${opening}${pair(stages[0],stages[1],1)}${pair(stages[2],stages[3],2)}${pair(stages[4],stages[5],3)}${pair(stages[6],stages[7],4)}${close}</body></html>`;

const htmlPath = path.join(output, 'N00-recorrido-print.html');
const pdfPath = path.join(output, 'N00-recorrido-insert.pdf');
fs.writeFileSync(htmlPath, html);
const browser = await chromium.launch({executablePath:process.env.METSI_CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--no-sandbox']});
try {
  const page = await browser.newPage({viewport:{width:794,height:1123},deviceScaleFactor:1});
  await page.goto(`file://${htmlPath}`,{waitUntil:'load'});
  await page.evaluate(() => document.fonts.ready);
  const bounds = await page.evaluate(() => [...document.querySelectorAll('.sheet')].map(sheet => ({
    height:sheet.scrollHeight, clientHeight:sheet.clientHeight,
    overflows:[...sheet.querySelectorAll('.reading,.guide,.route-step,.move,.return')].filter(el => el.getBoundingClientRect().bottom > sheet.getBoundingClientRect().bottom - 18).map(el => el.className)
  })));
  if (bounds.some(b => b.height > b.clientHeight + 2 || b.overflows.length)) throw new Error(`Desborde de maquetación: ${JSON.stringify(bounds)}`);
  await page.pdf({path:pdfPath,format:'A4',printBackground:true,preferCSSPageSize:true,margin:{top:0,right:0,bottom:0,left:0}});
  fs.writeFileSync(path.join(output, 'layout-check.json'),JSON.stringify(bounds,null,2));
} finally { await browser.close(); }
console.log(pdfPath);
