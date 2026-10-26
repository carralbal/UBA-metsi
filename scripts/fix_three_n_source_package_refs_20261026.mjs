// Make the archived editable source packages self-contained without changing paint.
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..');
for (const code of ['N02', 'N14']) {
  const folder = path.join(root, `${code}-post-cecilia-editorial-20261026`);
  const target = path.join(folder, 'index.html');
  const before = fs.readFileSync(target, 'utf8');
  let after = before;
  for (const name of ['corrections.css', 'standard-v7.css']) {
    const needle = `href="../${name}"`;
    if (!after.includes(needle)) throw new Error(`${code}: missing ${needle}`);
    after = after.replace(needle, `href="${name}"`);
  }
  const pdf = code === 'N02'
    ? '../site/pdf/N02-METSI-lectura-previa-v16-final.pdf'
    : '../site/pdf/publicados/N14-METSI-lectura-previa-v10-final.pdf';
  after = after.replaceAll(`../protected-covers/definitive/${code}.pdf`, pdf);
  fs.writeFileSync(target, after);
  process.stdout.write(`${code}: local styles and public locked-cover reference resolved\n`);
}
