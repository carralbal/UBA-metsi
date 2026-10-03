import {chromium} from '/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';

const url = pathToFileURL(resolve('site/index.html')).href;
const widths = [320, 390, 650, 768, 900, 1024, 1280, 1440, 2048, 2790];
const visual = process.argv.includes('--visual');
const browser = await chromium.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  headless: true,
});
const failures = [];
let checked = 0;

try {
  for (const width of widths) {
    const page = await browser.newPage({viewport: {width, height: 900}, reducedMotion: 'reduce'});
    await page.goto(url, {waitUntil: 'load'});
    await page.locator('[data-profile-choice="student"]').click();
    await page.waitForFunction(() => !document.getElementById('profile-dialog').open && document.body.style.position !== 'fixed');
    await page.waitForFunction(() => document.querySelectorAll('[data-practice-block]').length === 8);
    for (let block = 1; block <= 8; block++) {
      await page.evaluate((number) => {
        document.querySelector(`[data-practice-block="${number}"]`).click();
      }, block);
      const ids = await page.locator('.practice-node[data-practice-id]').evaluateAll(
        (nodes) => [...new Set(nodes.map((node) => node.dataset.practiceId))]
      );
      for (const id of ids) {
        const problem = await page.evaluate((practiceId) => {
          document.querySelector(`.practice-node[data-practice-id="${CSS.escape(practiceId)}"]`).click();
          const root = document.querySelector('[data-practice-detail]');
          const sheet = root.closest('.practice-sheet').getBoundingClientRect();
          const title = root.querySelector('[data-practice-title]');
          const description = root.querySelector('[data-practice-description]');
          const references = root.querySelector('[data-practice-documents]');
          const textRects = (element) => {
            const range = document.createRange();
            range.selectNodeContents(element);
            return [...range.getClientRects()];
          };
          const titleRects = textRects(title);
          const descriptionRects = textRects(description);
          const referenceRects = textRects(references);
          const intersects = (a, b) => a.some((one) => b.some((two) =>
            Math.min(one.right, two.right) - Math.max(one.left, two.left) > 2 &&
            Math.min(one.bottom, two.bottom) - Math.max(one.top, two.top) > 2
          ));
          const overflow = [...titleRects, ...descriptionRects, ...referenceRects].some((rect) =>
            rect.left < sheet.left - 1 || rect.right > sheet.right + 1
          );
          return {
            label: title.textContent,
            titleDescription: intersects(titleRects, descriptionRects),
            titleReferences: intersects(titleRects, referenceRects),
            descriptionReferences: intersects(descriptionRects, referenceRects),
            overflow,
          };
        }, id);
        checked++;
        if (problem.titleDescription || problem.titleReferences || problem.descriptionReferences || problem.overflow) {
          failures.push({width, block, id, ...problem});
        }
        if (visual && [390, 1440].includes(width) && problem.label === 'Pensamiento sistémico') {
          await page.locator('.practice-atlas').screenshot({path: `/private/tmp/metsi-atlas-${width}.png`});
        }
      }
    }
    await page.close();
  }
} finally {
  await browser.close();
}

console.log(`Atlas: ${checked} estados comprobados en ${widths.length} anchos; ${failures.length} defectos.`);
for (const failure of failures) console.log(JSON.stringify(failure));
if (failures.length) process.exitCode = 1;
