import { chromium } from '/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const source = path.join(root, 'N14-v11-post-cecilia/index.html');
const output = process.argv[2];
if (!output || !path.isAbsolute(output)) throw new Error('Supply absolute temporary PDF path');

const browser = await chromium.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  headless: true,
});
try {
  const page = await browser.newPage();
  await page.emulateMedia({ media: 'print' });
  await page.goto(pathToFileURL(source).href, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const check = await page.evaluate(() => ({
    missingImages: [...document.images].filter(i => !i.complete || !i.naturalWidth).map(i => i.getAttribute('src')),
    hiddenBlocks: [...document.querySelectorAll('[data-source-id]')]
      .filter(e => getComputedStyle(e).display === 'none' || e.getBoundingClientRect().height === 0)
      .map(e => e.dataset.sourceId),
    sourceBlockCount: document.querySelectorAll('[data-source-id]').length,
    preparation: [...document.querySelectorAll('[data-source-id="N14-s26-b007"], [data-source-id="N14-add-asis-tobe-prep"]')]
      .map(e => e.textContent.trim()),
  }));
  if (check.missingImages.length || check.hiddenBlocks.length || check.sourceBlockCount !== 314 || check.preparation.length !== 2) {
    throw new Error(JSON.stringify(check));
  }
  await page.pdf({ path: output, printBackground: true, preferCSSPageSize: true, tagged: true, scale: 0.961344 });
  process.stdout.write(JSON.stringify({ output, ...check }) + '\n');
} finally {
  await browser.close();
}
