import { access, readFile, writeFile } from 'node:fs/promises';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';

const repo = resolve(import.meta.dirname, '..');
const directory = join(repo, 'site/covers/referentes');
const portraits = JSON.parse(await readFile(join(directory, 'manifest.json'), 'utf8'));
const temporary = await mkdtemp(join(tmpdir(), 'metsi-referentes-'));

try {
  for (const portrait of portraits) {
    const output = join(directory, `${portrait.id}.webp`);
    if (process.argv.includes('--missing-only')) {
      try { await access(output); console.log(`${portrait.name}: already present`); continue; } catch {}
    }
    let input;
    if (portrait.local_source) {
      input = join(repo, portrait.local_source);
    } else {
      const query = new URL('https://commons.wikimedia.org/w/api.php');
      query.search = new URLSearchParams({
        action: 'query',
        titles: `File:${portrait.commons_file}`,
        prop: 'imageinfo',
        iiprop: 'url|extmetadata',
        iiurlwidth: '960',
        format: 'json',
      });
      const response = await fetch(query, { headers: { 'User-Agent': 'METSI/1.0 (educational editorial portraits)' } });
      if (!response.ok) throw new Error(`${portrait.name}: Wikimedia API ${response.status}`);
      const payload = await response.json();
      const page = Object.values(payload.query.pages)[0];
      const image = page.imageinfo?.[0];
      if (!image) throw new Error(`${portrait.name}: no Wikimedia image`);
      const actualLicense = image.extmetadata?.LicenseShortName?.value;
      if (actualLicense !== portrait.license && !(portrait.license === 'Free Art License 1.3' && actualLicense === 'FAL')) {
        throw new Error(`${portrait.name}: expected ${portrait.license}, found ${actualLicense}`);
      }
      const photo = await fetch(image.thumburl || image.url, { headers: { 'User-Agent': 'METSI/1.0 (educational editorial portraits)' } });
      if (!photo.ok) throw new Error(`${portrait.name}: image ${photo.status}`);
      input = join(temporary, `${portrait.id}.source`);
      await writeFile(input, new Uint8Array(await photo.arrayBuffer()));
    }
    const intermediate = join(temporary, `${portrait.id}.png`);
    const processed = spawnSync('ffmpeg', [
      '-hide_banner', '-loglevel', 'error', '-y', '-i', input,
      '-vf', `${portrait.crop ? `${portrait.crop},` : ''}scale=420:420:force_original_aspect_ratio=increase,crop=420:420,format=gray`,
      '-frames:v', '1', intermediate,
    ], { encoding: 'utf8' });
    if (processed.status !== 0) throw new Error(`${portrait.name}: ${processed.stderr}`);
    const encoded = spawnSync('cwebp', ['-quiet', '-q', '78', intermediate, '-o', output], { encoding: 'utf8' });
    if (encoded.status !== 0) throw new Error(`${portrait.name}: ${encoded.stderr}`);
    console.log(`${portrait.name}: ${output}`);
  }
} finally {
  await rm(temporary, { recursive: true, force: true });
}
