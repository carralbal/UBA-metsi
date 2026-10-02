import {chromium} from '/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const [stage, number, selector] = process.argv.slice(2);
const browser = await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless:true});
try {
  const page = await browser.newPage();
  await page.emulateMedia({media:'print'});
  await page.goto(pathToFileURL(path.join(stage, `N${number}`, 'index.html')).href, {waitUntil:'networkidle'});
  console.log(JSON.stringify(await page.evaluate((selector) => {
    const el = document.querySelector(selector);
    if (!el) return {error:'not found'};
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return {class:el.className, height:cs.height, minHeight:cs.minHeight, display:cs.display,
      fontSize:cs.fontSize, lineHeight:cs.lineHeight, columns:cs.columnCount,
      stylesheets:[...document.styleSheets].map(sheet=>({href:sheet.href, rules:(()=>{try{return sheet.cssRules.length}catch{return -1}})()})),
      breakBefore:cs.breakBefore, breakAfter:cs.breakAfter, breakInside:cs.breakInside,
      gridRows:cs.gridTemplateRows, rectHeight:r.height, padding:cs.padding,
      children:[...el.children].map(child=>({class:child.className, height:getComputedStyle(child).height,
        rectHeight:child.getBoundingClientRect().height}))};
  }, selector), null, 2));
} finally {await browser.close();}
