import {chromium} from '/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const root=process.cwd(), edition=path.join(root,'pedagogy/plain-language-edition');
const plan=JSON.parse(await fs.readFile(path.join(edition,'release-plan.json'),'utf8'));
const numbers=process.argv.slice(2).map(Number);
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
try {
  const page=await browser.newPage();
  await page.emulateMedia({media:'print'});
  for(const e of plan.filter(e=>!numbers.length||numbers.includes(Number(e.code.slice(1))))) {
    await fs.copyFile(path.join(edition,'edition.css'),path.join(root,e.package,'edition.css'));
    await page.goto(pathToFileURL(path.join(root,e.html)).href,{waitUntil:'networkidle'});
    await page.evaluate(()=>document.fonts.ready);
    const report=await page.evaluate(()=>({
      missingImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.getAttribute('src')),
      hiddenSourceBlocks:[...document.querySelectorAll('[data-source-id]')].filter(el=>getComputedStyle(el).display==='none'||el.getBoundingClientRect().height===0).map(el=>el.dataset.sourceId),
      sourceBlocks:[...document.querySelectorAll('[data-source-id]')].map(el=>({id:el.dataset.sourceId,text:el.textContent})),
      headings:[...document.querySelectorAll('h2')].map(el=>el.textContent),
    }));
    if(report.missingImages.length||report.hiddenSourceBlocks.length)throw new Error(JSON.stringify({code:e.code,...report}));
    await page.pdf({path:path.join(root,e.output),printBackground:true,preferCSSPageSize:true,tagged:true});
    await fs.writeFile(path.join(root,e.package,'render-report.json'),JSON.stringify(report,null,2)+'\n');
    console.log(e.code+' rendered with '+report.sourceBlocks.length+' visible source blocks');
  }
} finally {await browser.close();}
