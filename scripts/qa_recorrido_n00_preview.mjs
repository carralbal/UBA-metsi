import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { chromium } = require('/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const previewDir = path.join(root, 'site/covers/preview-recorrido-n00');
const html = path.join(previewDir, 'index.html');
const mode = process.argv[2] || 'qa';
const browser = await chromium.launch({ headless: true, executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });

try {
  if (mode === 'qa') {
    const results = [];
    for (const width of [320, 390, 768, 1440]) {
      const page = await browser.newPage({ viewport: { width, height: 900 }, deviceScaleFactor: 1 });
      await page.goto(pathToFileURL(html).href);
      await page.locator('#tab-b').click();
      const bVisible = await page.locator('#panel-b').isVisible();
      if (width === 390 || width === 1440) {
        await page.screenshot({ path: `/private/tmp/metsi-recorrido-n00-b-${width}.png`, fullPage: true });
      }
      await page.locator('#tab-n00').click();
      const n00Visible = await page.locator('#panel-n00').isVisible();
      const metrics = await page.evaluate(() => ({
        viewport: innerWidth,
        scrollWidth: document.documentElement.scrollWidth,
        n00Copy: document.querySelector('.hero-side p')?.textContent,
        diagramVisible: getComputedStyle(document.querySelector('.route-figure')).display !== 'none',
        overflow: [...document.querySelectorAll('body *')].filter((element) => element.getBoundingClientRect().right > innerWidth + 1).slice(0, 8).map((element) => ({ tag: element.tagName, class: element.className, right: Math.round(element.getBoundingClientRect().right) })),
      }));
      if (width === 320) await page.screenshot({ path: '/private/tmp/metsi-recorrido-n00-320.png', fullPage: true });
      if (metrics.scrollWidth > metrics.viewport + 1 || !bVisible || !n00Visible) {
        throw new Error(`QA failed at ${width}px: ${JSON.stringify({ ...metrics, bVisible, n00Visible })}`);
      }
      if (width === 390 || width === 1440) {
        await page.screenshot({ path: `/private/tmp/metsi-recorrido-n00-${width}.png`, fullPage: true });
      }
      results.push({ width, ...metrics, bVisible, n00Visible });
      await page.close();
    }
    const svgPage = await browser.newPage({ viewport: { width: 1600, height: 650 }, deviceScaleFactor: 2 });
    await svgPage.goto(pathToFileURL(path.join(previewDir, 'mapa.svg')).href);
    await svgPage.screenshot({ path: path.join(previewDir, 'mapa-preview.png') });
    await svgPage.close();
    console.log(JSON.stringify(results, null, 2));
  } else if (mode === 'pdf') {
    const page = await browser.newPage({ viewport: { width: 1588, height: 1123 }, deviceScaleFactor: 1 });
    await page.goto(pathToFileURL(html).href);
    const output = path.join(root, 'output/pdf/piloto-n00-a-b.pdf');
    fs.mkdirSync(path.dirname(output), { recursive: true });
    await page.pdf({ path: output, preferCSSPageSize: true, printBackground: true });
    fs.copyFileSync(output, path.join(previewDir, 'piloto-n00-a-b.pdf'));
    console.log(output);
    await page.close();
  } else {
    throw new Error(`Unknown mode: ${mode}`);
  }
} finally {
  await browser.close();
}
