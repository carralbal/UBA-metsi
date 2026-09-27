import { chromium } from '/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs';
import assert from 'node:assert/strict';
const base=process.argv[2]||'http://127.0.0.1:8768/';
const out='/private/tmp/metsi-site-alignment-browser';
fs.mkdirSync(out,{recursive:true});
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
const results=[];
for (const width of [1440,768,390]) {
 const page=await browser.newPage({viewport:{width,height:950},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base,{waitUntil:'networkidle'});
 await page.evaluate(()=>document.fonts.ready);
 const expected=await page.evaluate(()=>window.METSI_ATLAS);
 assert.equal(expected.items.length,41);
 assert.equal(await page.locator('.cover-library>article').count(),36);
 assert.equal(await page.locator('.nucleus a').count(),0);
 assert.deepEqual(await page.locator('.block summary strong').allTextContents(),expected.blocks.map(b=>b.title));
 assert.deepEqual(await page.locator('.program-units span').allTextContents(),expected.blocks.map(b=>b.title));
 await page.locator('.practice-radial').scrollIntoViewIfNeeded();
 // Let the entrance animation finish before measuring block-to-block shifts.
 await page.waitForTimeout(1000);
 let count=0,positions=[];
 for(let b=1;b<=8;b++) {
   await page.locator('[data-practice-block="'+b+'"]').click();
   const rect=await page.locator('.practice-radial').evaluate(el=>{const r=el.getBoundingClientRect();return {x:r.x,y:r.y+scrollY,width:r.width}});
   positions.push(rect);
   for(const item of expected.items.filter(x=>x.block===b)){
     await page.locator('[data-practice-id="'+item.id+'"]').click();
     const refs=await page.locator('[data-practice-documents] a').evaluateAll(a=>a.map(x=>x.getAttribute('href')));
     assert.deepEqual(refs,item.refs.map(r=>r.href));count+=refs.length;
     const overflow=await page.locator('.practice-sheet').evaluate(el=>el.scrollWidth>el.clientWidth+2);
     assert(!overflow, 'Panel overflow '+width+' '+item.id);
   }
 }
 assert(positions.every(p=>Math.abs(p.y-positions[0].y)<2&&Math.abs(p.x-positions[0].x)<2),'Radial moved at '+width+': '+JSON.stringify(positions));
 assert.equal(await page.locator('.reading-reference-grid li').count(),36);
 await page.locator('.reference-index details').first().locator('summary').click();
 assert.equal(await page.locator('.reference-index details').first().locator('li').count(),24);
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2);
 assert(!overflow,'Horizontal overflow '+width);
 if(width<900){await page.locator('[data-menu-toggle]').click();assert.equal(await page.locator('[data-menu-toggle]').getAttribute('aria-expanded'),'true');await page.keyboard.press('Escape');}
 await page.locator('[data-practice-block="6"]').click();
 await page.mouse.move(0,0);
 await page.waitForTimeout(250);
 await page.locator('.practice-radial-layout').screenshot({path:out+'/atlas-'+width+'.png'});
 await page.locator('#referentes').screenshot({path:out+'/references-'+width+'.png'});
 await page.screenshot({path:out+'/page-'+width+'.png',fullPage:true});
 assert.deepEqual(errors,[]);
 results.push({width,practices:41,verifiedDestinations:count,radialStable:true,noHorizontalOverflow:true,errors});
 await page.close();
}
await browser.close();
fs.writeFileSync('pedagogy/site-alignment-20260927/browser-qa.json',JSON.stringify({base,results},null,2));
console.log(JSON.stringify(results));
