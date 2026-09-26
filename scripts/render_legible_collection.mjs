import {chromium} from '/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const root=process.cwd();
const out=path.join(root,'editorial-standard/approved-infographics/collection-legible-2026-09');
const plans=JSON.parse(await fs.readFile(path.join(out,'plan.json'),'utf8'));
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
try {
 const page=await browser.newPage({viewport:{width:1200,height:1620},deviceScaleFactor:1});
 for(const plan of plans){
  const file=path.join(root,plan.svg);const folder=path.dirname(file);
  await page.goto(pathToFileURL(file).href);await page.evaluate(()=>document.fonts.ready);
  const geometry=await page.evaluate(()=>{
   const labels=[...document.querySelectorAll('svg text')].map(t=>{const b=t.getBBox();return {text:t.textContent,x:b.x,y:b.y,w:b.width,h:b.height,size:parseFloat(getComputedStyle(t).fontSize)};});
   const overlaps=[];
   for(let i=0;i<labels.length;i++)for(let j=i+1;j<labels.length;j++){const a=labels[i],b=labels[j];if(Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x)>1&&Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y)>1)overlaps.push([a.text,b.text]);}
   const rowOverflow=[...document.querySelectorAll('[data-row-bottom]')].flatMap(row=>[...row.querySelectorAll('text')].filter(t=>{const b=t.getBBox();return b.y+b.height>Number(row.dataset.rowBottom);}).map(t=>t.textContent));
   return {labels,overlaps,rowOverflow,outside:labels.filter(a=>a.x<0||a.x+a.w>1200||a.y<0||a.y+a.h>1620)};
  });
  await fs.writeFile(path.join(folder,'geometry.json'),JSON.stringify(geometry,null,2));
  await page.screenshot({path:path.join(folder,'preview.png')});
  console.log(`N${plan.number}: ${geometry.overlaps.length} overlaps; ${geometry.outside.length} outside; ${JSON.stringify(geometry.rowOverflow)} row overflow`);
  const alt=(await fs.readFile(path.join(folder,'alt-text.md'),'utf8')).replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;');
  const markup=`<!doctype html><html lang="es-AR"><meta charset="utf-8"><title>METSI N${plan.number} · Mapa de decisión</title><style>@page{size:A4;margin:0}*{box-sizing:border-box}html,body{margin:0;background:#fff}.plate{position:absolute;left:18.5mm;top:18mm;width:173mm;height:233.55mm}.plate img{display:block;width:100%;height:100%}footer{position:absolute;top:280mm;left:18.5mm;right:18.5mm;border-top:.2mm solid #b5b7b0;padding-top:3mm;font:8pt Arial;color:#575a55;display:flex;justify-content:space-between}</style><main class="plate"><img src="${path.basename(file)}" alt="${alt}"></main><footer><span>MAPA DE DECISIÓN</span><span>Diego Carralbal, 2026 · linkedin.com/in/carralbal</span></footer></html>`;
  await fs.writeFile(path.join(folder,'plate.html'),markup);
  await page.goto(pathToFileURL(path.join(folder,'plate.html')).href);await page.evaluate(()=>document.fonts.ready);
  await page.pdf({path:path.join(folder,'plate.pdf'),printBackground:true,preferCSSPageSize:true,tagged:true});
 }
}finally{await browser.close();}
