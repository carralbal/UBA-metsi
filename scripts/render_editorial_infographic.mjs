import {chromium} from '/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const [folder, variant = ''] = process.argv.slice(2);
if (!folder) throw new Error('Usage: render_editorial_infographic.mjs FOLDER');
const suffix = variant ? `-${variant}` : '';
const browser = await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless:true});
try {
  const viewport = variant === 'print' ? {width:1200,height:1650} : variant === 'inline' ? {width:1200,height:900} : {width:1800,height:1100};
  const page = await browser.newPage({viewport, deviceScaleFactor:1});
  await page.goto(pathToFileURL(path.join(folder,`review${suffix}.html`)).href, {waitUntil:'load'});
  await page.locator('img').screenshot({path:path.join(folder,`cartera-evidencia${suffix}.png`),timeout:60000});
} finally {
  await browser.close();
}
