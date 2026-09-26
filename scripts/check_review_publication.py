"""Gate only the authorized delivery, excluding unrelated local work."""
from pathlib import Path
import hashlib, json, os, subprocess, tempfile

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT/'pedagogy/pedagogical-review-20260926'
gate = Path('/Users/diegocarralbal/.codex/skills/metsi-publish-course/scripts/verify_publishable.py')
release = json.loads((REVIEW/'publication-manifest.json').read_text())
manifest = json.loads((ROOT/'course-manifest.json').read_text())
assert len(release['documents']) == 36
for item in release['documents']:
    document = next(d for d in manifest['documents'] if d['code']==item['code'])
    for filename in [document['pdf'], document['public_pdf']]:
        assert hashlib.sha256((ROOT/filename).read_bytes()).hexdigest() == item['sha256'], filename
files = set(subprocess.check_output(['git','diff','--cached','--name-only','--diff-filter=ACM'], cwd=ROOT, text=True).splitlines())
files.update(subprocess.check_output(['git','ls-files','site','.github/workflows'], cwd=ROOT, text=True).splitlines())
files.update(['course-manifest.json'])
with tempfile.TemporaryDirectory(prefix='metsi-publication-gate-') as directory:
    dest = Path(directory)
    for name in files:
        source = ROOT/name
        assert not source.is_symlink(), name
        target = dest/name
        target.parent.mkdir(parents=True, exist_ok=True)
        os.link(source, target)
    run = subprocess.run([os.sys.executable, str(gate), directory], capture_output=True, text=True)
    report = json.loads(run.stdout)
    (REVIEW/'publication-gate.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(report, ensure_ascii=False))
    raise SystemExit(run.returncode)
