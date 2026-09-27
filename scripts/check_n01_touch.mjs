import { chromium } from '/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
const base = process.argv[2] || 'http://127.0.0.1:8772/pdf/presentaciones/N01/';
const browser = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
const errors = [];
try {
  const context = await browser.newContext({ viewport: {width:390,height:844}, isMobile:true, hasTouch:true, reducedMotion:'reduce' });
  const page = await context.newPage();
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(`${base}?slide=1`, {waitUntil:'domcontentloaded'});
  const next = page.getByRole('button', {name:'Diapositiva siguiente',exact:true});
  const prev = page.getByRole('button', {name:'Diapositiva anterior',exact:true});
  await next.waitFor();
  assert(await prev.isDisabled());
  const box = await next.boundingBox();
  assert(box.width >= 44 && box.height >= 44);
  const cdp = await context.newCDPSession(page);
  async function swipe(x1,y1,x2,y2) {
    await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:x1,y:y1}]});
    for(let i=1;i<=6;i++) {
      await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:x1+(x2-x1)*i/6,y:y1+(y2-y1)*i/6}]});
      await page.waitForTimeout(20);
    }
    await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
    await page.waitForTimeout(120);
  }
  const slide = () => new URL(page.url()).searchParams.get('slide');
  await swipe(300,410,90,415); assert.equal(slide(),'2');
  await swipe(90,410,300,415); assert.equal(slide(),'1');
  await swipe(180,420,200,422); assert.equal(slide(),'1');
  await swipe(4,410,190,415); assert.equal(slide(),'1');
  for(let i=2;i<=10;i++) { await next.click(); await page.waitForTimeout(40); assert.equal(slide(),String(i)); }
  assert(await next.isDisabled());
  for(let i=9;i>=1;i--) { await prev.click(); await page.waitForTimeout(40); assert.equal(slide(),String(i)); }
  await page.screenshot({path:'/tmp/n01-mobile-touch.png'});
  await page.setViewportSize({width:320,height:568});
  await page.goto(`${base}?slide=4`,{waitUntil:'domcontentloaded'});
  await next.waitFor();
  await swipe(180,360,180,190); assert.equal(slide(),'4');
  const scrolling = await page.locator('.slide-copy').evaluate(el=>({top:el.scrollTop,overflow:el.scrollHeight>el.clientHeight}));
  assert(scrolling.overflow && scrolling.top>0,JSON.stringify(scrolling));
  await page.screenshot({path:'/tmp/n01-small-touch.png'});
  await page.setViewportSize({width:844,height:390});
  await page.screenshot({path:'/tmp/n01-landscape-touch.png'});
  assert(await next.isVisible());
  await context.close();
  const desktop = await browser.newContext({viewport:{width:1440,height:900},reducedMotion:'reduce'});
  const desk = await desktop.newPage();
  await desk.goto(`${base}?slide=1`,{waitUntil:'domcontentloaded'});
  await desk.locator('.stage').waitFor();
  assert(!(await desk.locator('.touch-navigation').isVisible()));
  await desk.keyboard.press('ArrowRight'); await desk.waitForTimeout(80);
  assert.equal(new URL(desk.url()).searchParams.get('slide'),'2');
  await desk.keyboard.press('ArrowLeft'); await desk.waitForTimeout(80);
  assert.equal(new URL(desk.url()).searchParams.get('slide'),'1');
  const popupPromise = desktop.waitForEvent('page');
  await desk.keyboard.press('n');
  const notes = await popupPromise;
  await notes.waitForLoadState('domcontentloaded');
  await notes.locator('.notes-window').waitFor();
  assert.equal(await notes.locator('.touch-navigation').count(),0);
  assert.equal(errors.length,0,errors.join('\n'));
  console.log(JSON.stringify({ok:true,base,checks:['touch swipe both directions','small/edge gesture ignored','all ten slides and boundaries','48px controls','vertical scrolling without changing slide','portrait/landscape','desktop arrows','separate notes tab','no mobile controls on desktop','no runtime errors']}));
} finally { await browser.close(); }
