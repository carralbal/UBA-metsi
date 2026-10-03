import { chromium } from '/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

const url = pathToFileURL(resolve('site/index.html')).href;
const widths = [320, 390, 650, 768, 1024, 1440, 2048];
const browser = await chromium.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  headless: true,
});
const failures = [];

try {
  for (const width of widths) {
    const page = await browser.newPage({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
    await page.goto(url, { waitUntil: 'load' });
    await page.locator('[data-profile-choice="student"]').click();
    await page.waitForFunction(() => !document.getElementById('profile-dialog').open);
    const result = await page.locator('#referentes').evaluate(async (section) => {
      const imgs = [...section.querySelectorAll('.reference-portraits img')];
      imgs.forEach((img) => { img.loading = 'eager'; });
      await Promise.race([
        Promise.all(imgs.map((img) => img.decode().catch(() => {}))),
        new Promise((done) => setTimeout(done, 5000)),
      ]);
      const broken = imgs.filter((img) => img.naturalWidth === 0).map((img) => img.alt);
      const overlap = [];
      for (const li of section.querySelectorAll('.reference-ledger li')) {
        const photo = li.querySelector('.reference-portraits');
        const copy = li.querySelector('.reference-copy');
        if (!photo || !copy) continue;
        const a = photo.getBoundingClientRect();
        const b = copy.getBoundingClientRect();
        if (Math.min(a.right, b.right) - Math.max(a.left, b.left) > 2 &&
            Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 2) {
          overlap.push(copy.querySelector('b')?.textContent);
        }
      }
      const viewportOverflow = section.scrollWidth > document.documentElement.clientWidth + 1;
      return { broken, overlap, viewportOverflow, imageCount: imgs.length };
    });
    if (result.broken.length || result.overlap.length || result.viewportOverflow || result.imageCount !== 11) {
      failures.push({ width, ...result });
    }
    if ([390, 1440].includes(width)) {
      await page.locator('.reference-ledger').screenshot({ path: `/private/tmp/metsi-referentes-${width}.png` });
    }
    await page.close();
  }
} finally {
  await browser.close();
}

console.log(`Referentes: ${widths.length} anchos comprobados; ${failures.length} defectos.`);
for (const failure of failures) console.log(JSON.stringify(failure));
if (failures.length) process.exitCode = 1;
