import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { chromium } from '/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const site = path.join(repo, 'site');
const route = path.join(site, 'covers', 'recorrido', 'index.html');
const home = path.join(site, 'index.html');
const browser = await chromium.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  headless: true,
});
const results = [];

try {
  for (const width of [320, 390, 768, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 900 }, deviceScaleFactor: 1 });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(pathToFileURL(route).href);
    assert.equal(await page.locator('.station').count(), 8);
    assert.equal(await page.locator('.n-button').count(), 36);
    assert.equal(await page.locator('.guide-code').textContent(), 'N00');
    await page.locator('[data-reading="N25"]').click();
    assert.equal(await page.locator('[data-reading="N25"]').getAttribute('aria-pressed'), 'true');
    assert.match(await page.locator('#metsi-etapa-e .readout').textContent(), /empezar menos cosas/);
    const measured = await page.evaluate(() => {
      const root = document.getElementById('metsi-viaje-vertical');
      const colors = [...root.querySelectorAll('*')]
        .filter(element => element.textContent.trim() && element.children.length === 0)
        .map(element => getComputedStyle(element).color);
      return {
        scrollWidth: document.documentElement.scrollWidth,
        viewport: innerWidth,
        forbiddenTextColors: colors.filter(color => ['rgb(92, 121, 0)', 'rgb(113, 144, 0)', 'rgb(207, 255, 0)'].includes(color)),
      };
    });
    assert(measured.scrollWidth <= measured.viewport + 1, `Horizontal overflow at ${width}px`);
    assert.equal(measured.forbiddenTextColors.length, 0, `Green text at ${width}px`);
    assert.deepEqual(errors, [], `Browser errors at ${width}px`);
    if (width === 390 || width === 1440) {
      await page.screenshot({ path: `/private/tmp/metsi-learning-route-${width}.png`, fullPage: true });
    }
    results.push({ width, stations: 8, readings: 36, noHorizontalOverflow: true, noGreenText: true, interaction: 'pass', errors });
    await page.close();
  }
  const source = fs.readFileSync(home, 'utf8');
  assert.match(source, /class="journey-learning-link" href="covers\/recorrido\//);
  assert.match(source, /class="guide-route-link" href="covers\/recorrido\//);
  assert(fs.existsSync(path.join(site, 'covers', 'recorrido', 'mapa.svg')));
  const report = { status: 'pass', results, homepageLinks: 2, pdfChanged: false };
  fs.writeFileSync(path.join(site, 'covers', 'recorrido', 'qa-report.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(report));
} finally {
  await browser.close();
}
