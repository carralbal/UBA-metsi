import {chromium} from '/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const stage=process.argv[2];
const numbers=process.argv.slice(3).map(Number);
if(!stage || numbers.some(n=>!Number.isInteger(n) || n<1 || n>36)) {
  throw new Error('Usage: render_editorial_recovery.mjs STAGE [N...]');
}
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
try {
  const page=await browser.newPage();
  await page.emulateMedia({media:'print'});
  for(const number of numbers.length?numbers:Array.from({length:36},(_,i)=>i+1)) {
    const folder=path.join(stage,`N${String(number).padStart(2,'0')}`);
    await page.goto(pathToFileURL(path.join(folder,'index.html')).href,{waitUntil:'networkidle'});
    await page.evaluate(()=>document.fonts.ready);
    const check=await page.evaluate(()=>({
      missingImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.getAttribute('src')),
      hiddenSourceBlocks:[...document.querySelectorAll('[data-source-id]')]
        .filter(el=>getComputedStyle(el).display==='none'||el.getBoundingClientRect().height===0)
        .map(el=>el.dataset.sourceId),
      sourceBlockCount:document.querySelectorAll('[data-source-id]').length,
    }));
    if(check.missingImages.length||check.hiddenSourceBlocks.length) {
      throw new Error(JSON.stringify({number,...check}));
    }
    // This print is only an interior-layout stage. Its source HTML carries an
    // obsolete cover; the approved published cover is locked in a separate,
    // verified assembly step before any candidate may be reviewed.
    const pdf=path.join(folder,'interior-stage.pdf');
    await page.pdf({path:pdf,printBackground:true,preferCSSPageSize:true,tagged:true});
    await fs.writeFile(path.join(folder,'render-check.json'),JSON.stringify(check,null,2)+'\n');
    console.log(`N${String(number).padStart(2,'0')} staged: ${check.sourceBlockCount} visible blocks`);
  }
} finally {await browser.close();}
