import { chromium } from '/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const source = path.join(root, 'N30-v27-recovered-source/N30/index.html');
const browser = await chromium.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  headless: true,
});
try {
  const page = await browser.newPage();
  const failedRequests = [];
  page.on('requestfailed', request => failedRequests.push({url: request.url(), error: request.failure()}));
  await page.goto(pathToFileURL(source).href, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const result = await page.evaluate(() => ({
    sourceBlocks: document.querySelectorAll('[data-source-id]').length,
    images: document.images.length,
    missingImages: [...document.images].filter(image => !image.complete || !image.naturalWidth).map(image => image.src),
    stylesheets: [...document.styleSheets].filter(sheet => sheet.href).length,
    coverReference: document.querySelector('[data-cover-pdf]')?.getAttribute('data-cover-pdf'),
  }));
  if (result.sourceBlocks !== 324 || result.missingImages.length || result.stylesheets !== 5 || failedRequests.length) {
    throw new Error(JSON.stringify({ ...result, failedRequests }));
  }
  process.stdout.write(JSON.stringify({ ...result, failedRequests }) + '\n');
} finally {
  await browser.close();
}
