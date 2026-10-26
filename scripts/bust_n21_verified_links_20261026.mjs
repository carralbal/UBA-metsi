// The N21 binary was already current; make every public route fetch that verified blob.
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..');
const files = ['site/index.html', 'site/course-manifest.json',
  'site/covers/atlas-data.js', 'site/covers/cronicas/articles.json'];
const oldUrl = 'N21-METSI-lectura-previa-v10-final.pdf?v=fullbleed-editorial-20261007';
const newUrl = 'N21-METSI-lectura-previa-v10-final.pdf?v=n21-verified-20261026';
for (const relative of files) {
  const target = path.join(root, relative);
  const before = fs.readFileSync(target, 'utf8');
  const count = before.split(oldUrl).length - 1;
  if (count < 1) throw new Error(`${relative}: expected N21 link`);
  let after = before.replaceAll(oldUrl, newUrl);
  if (relative === 'site/course-manifest.json')
    after = after.replace('"revision": "fullbleed-editorial-20261007",\n      "subtitle": "Proyecto, producto, servicio y plataforma: responsabilidades que continúan"',
      '"revision": "n21-verified-20261026",\n      "subtitle": "Proyecto, producto, servicio y plataforma: responsabilidades que continúan"');
  fs.writeFileSync(target, after);
  process.stdout.write(`${relative}: ${count} N21 links\n`);
}
