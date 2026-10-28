import {chromium} from '/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const input = path.join(root, 'N02-post-cecilia-editorial-20261026/index.html');
const output = process.argv[2];
if (!output) throw new Error('Pass one temporary output PDF path');

const browser = await chromium.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  headless: true,
});
try {
  const page = await browser.newPage();
  await page.emulateMedia({media: 'print'});
  await page.goto(pathToFileURL(input).href, {waitUntil: 'networkidle'});
  await page.evaluate(() => document.fonts.ready);
  const check = await page.evaluate(() => ({
    sourceBlocks: document.querySelectorAll('[data-source-id]').length,
    missingImages: [...document.images].filter(i => !i.complete || !i.naturalWidth).map(i => i.getAttribute('src')),
    semanticFix: document.body.textContent.includes('La aplicación llamó «embarcado» a ese paso'),
  }));
  if (check.missingImages.length || !check.semanticFix || check.sourceBlocks !== 237) {
    throw new Error(JSON.stringify(check));
  }
  await page.pdf({path: output, printBackground: true, preferCSSPageSize: true, tagged: true, scale: 0.961344});
  process.stdout.write(JSON.stringify({output, ...check}) + '\n');
} finally {
  await browser.close();
}
