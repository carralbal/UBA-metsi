"""Install the 36 verified readings using the existing stable public URLs."""
from pathlib import Path
import hashlib, html, json, re, shutil, subprocess, tempfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'pedagogy/pedagogical-review-20260926'
STAMP = 'revision-pedagogica-20260926'
def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

plan = json.loads((REVIEW/'release-plan.json').read_text())
titles = json.loads((REVIEW/'titles.json').read_text())
manifest = json.loads((ROOT/'course-manifest.json').read_text())
public = json.loads((ROOT/'site/course-manifest.json').read_text())
collection = json.loads((ROOT/'collection-manifest.json').read_text())
homepage = (ROOT/'site/index.html').read_text()
assert len(plan) == 36 and all(e['rendered'] and e['visual_review'] for e in plan)
archive = ROOT/'archive/pedagogical-review-20260926'
archive.mkdir(parents=True, exist_ok=True)
if not (archive/'course-manifest.json').exists():
    save(archive/'course-manifest.json', manifest)
    save(archive/'public-catalogue.json', public)
    shutil.copy2(ROOT/'site/index.html', archive/'homepage.html')
    (archive/'README.md').write_text('# Edición anterior\n\nLos PDF y sus fuentes se conservan en los paquetes versionados indicados en course-manifest.json. La portada del sitio y el catálogo anteriores se guardan aquí como referencia histórica.\n')
installed = []
for e in plan:
    code = e['code']
    package = ROOT/e['package']
    pdf = ROOT/e['output']
    qa = json.loads((package/'pdf-audit.json').read_text())
    assert sha(pdf) == qa['sha256'] == e['pdf_sha256']
    assert sha(ROOT/e['source']) == e['source_sha256'] == qa['source_sha256']
    assert not qa['empty_pages'] and not qa['out_of_bounds'] and not qa['overlap_candidates']
    item = next(x for x in manifest['documents'] if x['code']==code)
    reading = next(x for x in public['readings'] if x['code']==code)
    assert (ROOT/item['pdf']).is_file(), 'previous package must be preserved'
    target = ROOT/item['public_pdf']
    assert target.is_file()
    shutil.copy2(pdf, target)
    count = len(qa['pages'])
    title = titles[code]['title']
    subtitle = titles[code]['subtitle']
    relative = str(target.relative_to(ROOT/'site'))
    url = relative+'?v='+STAMP
    reading.update(pages=count, pdf=url, revision=STAMP, title=title, subtitle=subtitle)
    homepage = re.sub(r'href="'+re.escape(relative)+r'(?:\?[^"]*)?"', f'href="{url}"', homepage)
    homepage = re.sub(r'('+code+r' · )\d+( páginas)', rf'\g<1>{count}\2', homepage)
    homepage, changed = re.subn(r'(<article>[^\n]*?<p>'+code+r' · \d+ páginas</p><h3>).*?(</h3>)', lambda m:m[1]+html.escape(title)+m[2], homepage)
    assert changed == 1, (code, changed)
    homepage = re.sub(r'(src="covers/thumbs/'+code+r'\.webp)(?:\?[^"]*)?"', rf'\1?v={STAMP}"', homepage)
    item.update(title=title, subtitle=subtitle, pdf=e['output'], canonical_source=e['source'],
                canonical_sha256=e['source_sha256'], source_version=STAMP, pages=count,
                bytes=pdf.stat().st_size, sha256=sha(pdf), editorial_revision=STAMP,
                qa_report=e['package']+'/pdf-audit.json', qa_status='PASS',
                qa_validator='scripts/audit_plain_language_pdfs.py', tag=STAMP+'-'+code.lower())
    entry = next((x for x in collection if x['number']==int(code[1:])), None)
    if entry is not None:
        entry.update(title=code+' · '+title, subtitle=subtitle, source=e['source'],
                     source_words=len((ROOT/e['source']).read_text().split()))
    with tempfile.TemporaryDirectory(prefix='metsi-cover-') as tmp:
        preview = Path(tmp)/code
        subprocess.run(['pdftoppm','-f','1','-l','1','-singlefile','-scale-to','1600','-png',str(pdf),str(preview)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with Image.open(preview.with_suffix('.png')) as image:
            image = image.convert('RGB')
            image.save(ROOT/'site/covers'/f'{code}.png', optimize=True)
            image.thumbnail((480,680))
            image.save(ROOT/'site/covers/thumbs'/f'{code}.webp', quality=87, method=6)
    installed.append(dict(code=code, public=url, title=title, sha256=sha(pdf), source_sha256=e['source_sha256']))
    print(code, 'installed', flush=True)
manifest['updated_at']='2026-09-26'
public['editorial_revision']=STAMP
save(ROOT/'course-manifest.json', manifest)
save(ROOT/'site/course-manifest.json', public)
save(ROOT/'collection-manifest.json', collection)
(ROOT/'site/index.html').write_text(homepage)
save(REVIEW/'publication-manifest.json', dict(status='LOCAL_READY_NOT_YET_PUBLISHED', revision=STAMP, documents=installed))
