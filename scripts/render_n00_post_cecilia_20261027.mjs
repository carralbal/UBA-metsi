import { chromium } from '/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const folder = path.resolve(process.argv[2] || 'N00-post-cecilia-from-current-20261027');
const printScale = Number(process.argv[3] || '0.961344');
const input = path.join(folder, 'N00/index.html');
const output = path.join(folder, 'N00-post-cecilia-stage.pdf');
const browser = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
try {
  const page = await browser.newPage();
  await page.emulateMedia({ media: 'print' });
  await page.goto(pathToFileURL(input).href, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  // Pagination changed after the two-entrance revision. Keep printed TOC labels
  // aligned with the actual PDF destinations, including the six inserted map pages.
  await page.evaluate(() => {
    const fixes = [
      ['nav-N00-s05-h2', 'p. 10', 'p. 9'],
      ['nav-N00-s20-h2', 'p. 38', 'p. 37'],
      ['nav-N00-s28-h2', 'p. 45', 'p. 44'],
      ['nav-N00-s30-h2', 'p. 46', 'p. 45'],
    ];
    for (const [target, before, after] of fixes) {
      const label = document.querySelector(`[data-nav-page-for="${target}"]`);
      if (!label || label.textContent.trim() !== before) {
        throw new Error(`Unexpected N00 TOC label for ${target}`);
      }
      label.textContent = after;
    }
  });
  const check = await page.evaluate(() => ({
    missingImages: [...document.images].filter(i => !i.complete || !i.naturalWidth).map(i => i.getAttribute('src')),
    hiddenSourceBlocks: [...document.querySelectorAll('[data-source-id]')].filter(e =>
      getComputedStyle(e).display === 'none' || e.getBoundingClientRect().height === 0
    ).map(e => e.dataset.sourceId),
    sourceBlockCount: document.querySelectorAll('[data-source-id]').length,
    stylesheetCount: document.styleSheets.length,
  }));
  if (check.missingImages.length || check.hiddenSourceBlocks.length || check.sourceBlockCount !== 391) {
    throw new Error(JSON.stringify(check));
  }
  await page.pdf({ path: output, printBackground: true, preferCSSPageSize: true, tagged: true, scale: printScale });
  await fs.writeFile(path.join(folder, 'render-check.json'), JSON.stringify(check, null, 2) + '\n');
  process.stdout.write(JSON.stringify({ output, ...check }) + '\n');
} finally {
  await browser.close();
}
