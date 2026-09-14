import { chromium } from "/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs";
import { pathToFileURL } from "node:url";
import path from "node:path";

const source = path.resolve(process.argv[2]);
const browser = await chromium.launch({
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  headless: true,
});
const page = await browser.newPage({ viewport: { width: 1200, height: 1600 } });
await page.emulateMedia({ media: "print" });
await page.goto(pathToFileURL(source).href, { waitUntil: "load" });
const result = await page.locator(".block-c-pause").evaluateAll((nodes) => nodes.map((node, index) => {
  const style = getComputedStyle(node);
  const rect = node.getBoundingClientRect();
  const quote = node.querySelector("p");
  const quoteStyle = quote ? getComputedStyle(quote) : null;
  const quoteRect = quote ? quote.getBoundingClientRect() : null;
  return {
    index: index + 1,
    page: style.page,
    display: style.display,
    position: style.position,
    width: style.width,
    height: style.height,
    breakBefore: style.breakBefore,
    breakAfter: style.breakAfter,
    breakInside: style.breakInside,
    rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
    quote: quoteStyle && quoteRect ? {
      position: quoteStyle.position,
      left: quoteStyle.left,
      right: quoteStyle.right,
      bottom: quoteStyle.bottom,
      fontSize: quoteStyle.fontSize,
      rect: { x: quoteRect.x, y: quoteRect.y, width: quoteRect.width, height: quoteRect.height },
    } : null,
  };
}));
console.log(JSON.stringify(result, null, 2));
await browser.close();
