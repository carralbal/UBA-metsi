import { chromium } from '/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const source = path.resolve(root, '../UBA-metsi-publication/output/source-recovery-20261020/N11-public-recovery-v1-private-20261022/index-v76-private.html');
const override = path.join(root, 'pedagogy/source-overrides/referentes-legibles-n11-20261028.css');
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
  await page.addStyleTag({ path: override });
  await page.evaluate(() => document.fonts.ready);
  const check = await page.evaluate(() => ({
    sourceBlockCount: document.querySelectorAll('[data-source-id]').length,
    missingImages: [...document.images]
      .filter(img => !img.complete || !img.naturalWidth)
      .map(img => img.getAttribute('src')),
    referents: document.querySelectorAll('.authors-page .contributor').length,
    font: getComputedStyle(document.querySelector('.authors-page .contributor p')).fontSize,
  }));
  if (check.sourceBlockCount !== 384 || check.missingImages.length || check.referents !== 6) {
    throw new Error(JSON.stringify(check));
  }
  await page.pdf({
    path: output,
    printBackground: true,
    preferCSSPageSize: true,
    tagged: true,
    outline: true,
    scale: 0.961344,
  });
  process.stdout.write(JSON.stringify({ output, ...check }) + '\n');
} finally {
  await browser.close();
}
