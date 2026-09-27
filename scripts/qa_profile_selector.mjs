import { chromium } from '/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const base = process.argv[2] || 'http://127.0.0.1:8772/';
const output = '/private/tmp/metsi-profile-qa';
fs.mkdirSync(output, {recursive:true});
const browser = await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
const results = [];
try {
 for (const [width,height] of [[1440,1000],[1024,768],[901,800],[768,900],[390,844],[320,568],[844,390]]) {
  const page = await browser.newPage({viewport:{width,height},reducedMotion:'reduce'});
  const errors = []; page.on('pageerror', e=>errors.push(e.message));
  await page.goto(base, {waitUntil:'networkidle'});
  const dialog = page.locator('#profile-dialog');
  assert(!(await dialog.textContent()).includes('↗'),'Emoji-capable arrows in dialog');
  assert.equal(await dialog.locator('.profile-arrow').count(),4);
  assert.equal(await dialog.locator('.profile-entry-accent').evaluate(e=>getComputedStyle(e).backgroundColor),'rgb(207, 255, 0)');
  assert.equal(await dialog.locator('.profile-choice-number').first().evaluate(e=>getComputedStyle(e).color),'rgb(207, 255, 0)');
  assert(await dialog.evaluate(d=>d.open));
  assert.equal(await page.evaluate(()=>document.activeElement.id),'profile-dialog-title');
  await page.keyboard.press('Escape');
  assert(await dialog.evaluate(d=>d.open),'Escape dismissed required choice');
  await page.mouse.click(2,2);
  assert(await dialog.evaluate(d=>d.open),'Backdrop dismissed required choice');
  for(let i=0;i<6;i++) {await page.keyboard.press('Tab');assert(await page.evaluate(()=>document.querySelector('#profile-dialog').contains(document.activeElement)),'Focus escaped');}
  const overflow = await dialog.evaluate(d=>d.scrollWidth>d.clientWidth+1);
  assert(!overflow,`Dialog overflow at ${width}`);
  await page.locator('#profile-dialog-title').focus();
  await page.screenshot({path:`${output}/dialog-${width}-${height}.png`});
  const original = await page.locator('#hero-title').innerHTML();
  const image = await page.locator('.hero').evaluate(e=>getComputedStyle(e).backgroundImage);
  for(const key of ['student','teacher','authority','visitor']) {
    if(!(await dialog.evaluate(d=>d.open))) await page.locator('[data-profile-switch]').click();
    await page.locator(`[data-profile-choice="${key}"]`).click();
    await page.waitForFunction(()=>!document.querySelector('#profile-dialog').open);
    assert.equal(await page.locator('body').getAttribute('data-audience'),key);
    assert.equal(await page.evaluate(()=>localStorage.getItem('metsi.audience.v1')),key);
    assert.equal(await page.locator('#hero-title').innerHTML(),original);
    assert.equal(await page.locator('.hero').evaluate(e=>getComputedStyle(e).backgroundImage),image);
    assert.equal(await page.locator('.profile-route li').count(),3);
    assert.equal(await page.locator('.cover-library>article').count(),36);
    assert.equal(await page.locator('body').evaluate(e=>e.style.position),'');
    assert(!(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1)),`Page overflow ${width} ${key}`);
    const links = await page.locator('.profile-route a,.hero-actions a').evaluateAll(els=>els.map(e=>e.getAttribute('href')));
    for(const href of links) {
      if(href.startsWith('#')) assert.equal(await page.locator(href).count(),1,href);
      else { const response=await page.request.get(new URL(href,base).href); assert.equal(response.status(),200,href); }
    }
    await page.reload({waitUntil:'networkidle'});
    assert(!(await dialog.evaluate(d=>d.open)),`Asked again for ${key}`);
    assert.equal(await page.locator('body').getAttribute('data-audience'),key);
  }
  if(width<=900) {
    const header = await page.locator('.site-header').evaluate(e=>[...e.children].filter(c=>getComputedStyle(c).display!=='none'&&c.tagName!=='NAV').map(c=>{const r=c.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom}}));
    for(let a=0;a<header.length;a++)for(let b=a+1;b<header.length;b++)assert(!(header[a].left<header[b].right&&header[a].right>header[b].left&&header[a].top<header[b].bottom&&header[a].bottom>header[b].top),'Header overlaps');
    await page.locator('[data-menu-toggle]').click();
    assert.equal(await page.locator('[data-menu-toggle]').getAttribute('aria-expanded'),'true');
    await page.locator('[data-profile-switch]').click();
    assert.equal(await page.locator('[data-menu-toggle]').getAttribute('aria-expanded'),'false');
    await page.locator('[data-profile-choice="student"]').click();
  }
  await page.locator('#atlas-practicas').scrollIntoViewIfNeeded();
  await page.waitForTimeout(100);
  const before = await page.evaluate(()=>scrollY);
  await page.locator('[data-profile-switch]').click();
  await page.locator('[data-profile-choice="teacher"]').click();
  assert(Math.abs((await page.evaluate(()=>scrollY))-before)<2,'Scroll not restored');
  const positions=[];
  for(let block=1;block<=8;block++) {
    await page.locator(`[data-practice-block="${block}"]`).click();
    positions.push(await page.locator('.practice-radial').evaluate(e=>e.getBoundingClientRect().top+scrollY));
  }
  assert(positions.every(p=>Math.abs(p-positions[0])<2),'Radial moved');
  await page.evaluate(()=>scrollTo({top:0,behavior:'instant'}));
  await page.screenshot({path:`${output}/home-${width}-${height}.png`});
  assert.deepEqual(errors,[]);
  results.push({width,height,profiles:4,mandatoryChoice:true,persistence:true,homePreserved:true,overflow:false,radialStable:true,errors});
  await page.close();
 }
 // Missing/blocked/corrupt storage must never prevent a choice or lock the user out.
 for(const mode of ['blocked','invalid']) {
  const page=await browser.newPage({viewport:{width:390,height:844}});
  await page.addInitScript(mode=>{
    if(mode==='blocked') Object.defineProperty(window,'localStorage',{get(){throw new DOMException('Unavailable','SecurityError')}});
    else localStorage.setItem('metsi.audience.v1','unknown-profile');
  },mode);
  await page.goto(base,{waitUntil:'networkidle'});
  assert(await page.locator('#profile-dialog').evaluate(d=>d.open));
  await page.locator('[data-profile-choice="visitor"]').click();
  await page.waitForFunction(()=>!document.querySelector('#profile-dialog').open);
  assert.equal(await page.locator('body').getAttribute('data-audience'),'visitor');
  await page.close();
 }
 // Graceful fallback: this preference is not authentication, so no-JS stays readable.
 const fallback=await browser.newPage({javaScriptEnabled:false});
 await fallback.goto(base);
 assert(await fallback.locator('#hero-title').isVisible());
 assert(!(await fallback.locator('#profile-dialog').isVisible()));
 await fallback.close();
 fs.writeFileSync(`${output}/results.json`,JSON.stringify({base,results,storageFallback:true,noJsReadable:true},null,2));
 console.log(JSON.stringify({results,storageFallback:true,noJsReadable:true}));
} finally { await browser.close(); }
