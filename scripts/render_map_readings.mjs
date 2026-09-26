import {chromium} from '/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';import path from 'node:path';import{pathToFileURL}from'node:url';
const root=process.cwd(),dir=path.join(root,'pedagogy/readability-pilots/collection-map-release-2026-09');
const plan=JSON.parse(await fs.readFile(path.join(dir,'release-plan.json'),'utf8'));
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
try{const page=await browser.newPage();for(const e of plan.filter(e=>e.mode==='html-reflow'&&(!process.argv[2]||e.number===Number(process.argv[2])))){
 await page.goto(pathToFileURL(path.join(root,e.html)).href,{waitUntil:'networkidle'});await page.evaluate(()=>document.fonts.ready);
 await page.pdf({path:path.join(root,e.output.replace('reading.pdf','rendered.pdf')),printBackground:true,preferCSSPageSize:true,tagged:true});
 console.log(e.code+' rendered');
}}finally{await browser.close();}
