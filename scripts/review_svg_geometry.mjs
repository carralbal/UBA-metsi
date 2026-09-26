import { chromium } from '/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import { pathToFileURL } from 'node:url';
import path from 'node:path';
import fs from 'node:fs/promises';

const file = path.resolve(process.argv[2]);
const browser = await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless:true});
try {
  const page = await browser.newPage({viewport:{width:1200,height:1620},deviceScaleFactor:1.5});
  await page.goto(pathToFileURL(file).href);
  await page.evaluate(()=>document.fonts.ready);
  const result = await page.evaluate(()=>{
    const svg = document.querySelector('svg');
    const box = svg.viewBox.baseVal;
    const labels = [...svg.querySelectorAll('text')].map(t=>{
      const b=t.getBBox();
      return {text:t.textContent,x:b.x,y:b.y,width:b.width,height:b.height,size:parseFloat(getComputedStyle(t).fontSize)};
    });
    const overlaps=[];
    for(let i=0;i<labels.length;i++) for(let j=i+1;j<labels.length;j++){
      const a=labels[i], b=labels[j];
      if(Math.min(a.x+a.width,b.x+b.width)-Math.max(a.x,b.x)>1 && Math.min(a.y+a.height,b.y+b.height)-Math.max(a.y,b.y)>1) overlaps.push([a.text,b.text]);
    }
    return {labels:labels.length,minFontPx:Math.min(...labels.map(l=>l.size)),overlaps,outside:labels.filter(l=>l.x<0||l.y<0||l.x+l.width>box.width||l.y+l.height>box.height),geometry:labels};
  });
  await page.locator('svg').screenshot({path:file.replace(/\.svg$/, '-preview.png')});
  await fs.writeFile(file.replace(/\.svg$/, '-geometry.json'),JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify({...result,geometry:undefined}));
} finally {await browser.close();}
