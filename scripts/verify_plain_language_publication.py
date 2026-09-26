#!/usr/bin/env python3
"""Verify every public PDF against the reviewed release, not just HTTP status."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
EDITION = ROOT / 'pedagogy/plain-language-edition'
BASE = 'https://carralbal.github.io/UBA-metsi/'

def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

def main():
    release = json.loads((EDITION / 'publication-manifest.json').read_text())
    def verify(item):
        url = BASE + item['public']
        url += ('&' if '?' in url else '?') + 'verify=' + release['revision']
        h = hashlib.sha256(); size = 0; signature = b''
        with urllib.request.urlopen(url, timeout=180) as response:
            while chunk := response.read(1024 * 1024):
                if not signature: signature = chunk[:4]
                h.update(chunk); size += len(chunk)
        actual = h.hexdigest()
        assert signature == b'%PDF' and actual == item['sha256'], (item['code'], actual, item['sha256'])
        return dict(code=item['code'], url=url, bytes=size, sha256=actual, status='PASS')
    checks = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for result in as_completed([pool.submit(verify, item) for item in release['documents']]):
            item = result.result(); checks.append(item); print(item['code'], 'public PDF verified', flush=True)
    assert len(checks) == 36
    with urllib.request.urlopen(BASE + 'course-manifest.json?v=' + release['revision'], timeout=60) as response:
        catalogue = json.load(response)
    assert catalogue['editorial_revision'] == release['revision']
    with urllib.request.urlopen(BASE + '?v=' + release['revision'], timeout=60) as response:
        homepage = response.read().decode()
    for item in release['documents']:
        if item['code'] != 'N25': assert item['public'] in homepage, item['code']
    checked_at = datetime.now(timezone.utc).isoformat()
    receipt = dict(status='PASS', revision=release['revision'], checked_at=checked_at,
                   deployed_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                   documents=sorted(checks,key=lambda x:x['code']), catalogue_verified=True, homepage_verified=True)
    save(EDITION / 'public-verification.json', receipt)
    release.update(status='PUBLISHED_AND_VERIFIED', verified_at=checked_at)
    save(EDITION / 'publication-manifest.json', release)
    plan = json.loads((EDITION / 'release-plan.json').read_text())
    for item in plan:
        item['published'] = True
        save(ROOT / item['package'] / 'edition-manifest.json', item)
    save(EDITION / 'release-plan.json', plan)
    inventory = json.loads((EDITION / 'inventory.json').read_text())
    for item in inventory['documents']: item['this_edition_published_and_verified'] = True
    save(EDITION / 'inventory.json', inventory)
    print('PASS: 36 PDFs, catalogue and home verified.', flush=True)

if __name__ == '__main__': main()
