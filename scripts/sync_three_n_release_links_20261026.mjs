// Mechanical cache and N14 page-reference update after one added interior page.
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..');
const files = ['site/index.html', 'site/covers/atlas-data.js', 'site/covers/cronicas/articles.json'];
const old02 = 'N02-METSI-lectura-previa-v16-final.pdf?v=n02-digital-20261023';
const new02 = 'N02-METSI-lectura-previa-v16-final.pdf?v=n02-editorial-20261026';
const old14 = 'N14-METSI-lectura-previa-v10-final.pdf?v=n14-digital-20261024';
const new14 = 'N14-METSI-lectura-previa-v10-final.pdf?v=n14-editorial-20261026';
const receipt = {};
for (const relative of files) {
  const target = path.join(root, relative);
  const before = fs.readFileSync(target, 'utf8');
  const count02 = before.split(old02).length - 1;
  const count14 = before.split(old14).length - 1;
  if (count02 < 1 || count14 < 1) throw new Error(`${relative}: expected both N02 and N14 URLs`);
  let after = before.replaceAll(old02, new02).replaceAll(old14, new14);
  if (relative === 'site/index.html') {
    after = after.replaceAll('N14-METSI-lectura-previa-v10-final.pdf?v=n14-editorial-20261026#page=48',
      'N14-METSI-lectura-previa-v10-final.pdf?v=n14-editorial-20261026#page=49');
    after = after.replaceAll('Bibliografía de N14, página 48', 'Bibliografía de N14, página 49');
    after = after.replace('N14 · De un área a otra: dónde se frena el trabajo</a><small>Referencias base · pág. 48',
      'N14 · De un área a otra: dónde se frena el trabajo</a><small>Referencias base · pág. 49');
    after = after.replace('N14 · 49 páginas', 'N14 · 50 páginas');
    if (!after.includes('N14 · 50 páginas') || after.includes('Bibliografía de N14, página 48'))
      throw new Error('N14 visible page references not updated');
  }
  if (relative === 'site/covers/atlas-data.js') {
    after = after.replace('N14-METSI-lectura-previa-v10-final.pdf?v=n14-editorial-20261026#page=30',
      'N14-METSI-lectura-previa-v10-final.pdf?v=n14-editorial-20261026#page=31');
  }
  fs.writeFileSync(target, after);
  receipt[relative] = {n02_urls: count02, n14_urls: count14};
}
process.stdout.write(JSON.stringify(receipt) + '\n');
