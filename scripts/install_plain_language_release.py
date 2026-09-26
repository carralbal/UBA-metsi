#!/usr/bin/env python3
"""Install only reviewed complete readings and synchronize public catalogues."""
from pathlib import Path
import hashlib, html, json, re, shutil, subprocess, tempfile
from pypdf import PdfReader
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
EDITION=ROOT/'pedagogy/plain-language-edition'
STAMP='lectura-clara-20260926'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def main():
    plan=json.loads((EDITION/'release-plan.json').read_text())
    approval=json.loads((EDITION/'visual-approval.json').read_text())
    assert len(plan)==35 and approval['status']=='PASS'
    inventory=json.loads((EDITION/'inventory.json').read_text())
    originals={d['code']:d for d in inventory['documents']}
    manifest=json.loads((ROOT/'course-manifest.json').read_text())
    public=json.loads((ROOT/'site/course-manifest.json').read_text())
    homepage=(ROOT/'site/index.html').read_text()
    installed=[]
    for e in plan:
        code=e['code'];file=ROOT/e['output']
        qa=json.loads((ROOT/e['package']/'pdf-audit.json').read_text())
        assert sha(file)==qa['sha256']==approval['documents'][code]
        assert not qa['out_of_bounds'] and not qa['overlap_candidates'] and not qa['empty_pages']
        assert qa['coverage']>=.999
        assert sha(ROOT/e['source'])==e['source_sha256']==qa['source_sha256']
        assert not originals[code]['bibliography_entries_missing']
        item=next(x for x in manifest['documents']if x['code']==code)
        reading=next(x for x in public['readings']if x['code']==code)
        target=ROOT/item['public_pdf']
        assert target.is_file() and target.suffix=='.pdf'
        shutil.copy2(file,target)
        count=len(PdfReader(file).pages)
        title=re.sub(r'^# N\d+\s*[·—-]\s*','',(ROOT/e['source']).read_text().splitlines()[0])
        url=str(target.relative_to(ROOT/'site'))+f'?v={STAMP}'
        reading.update(pages=count,pdf=url,revision=STAMP,title=title)
        homepage=re.sub(r'href="'+re.escape(str(target.relative_to(ROOT/'site')))+r'(?:\?[^\"]*)?"',f'href="{url}"',homepage)
        homepage=re.sub(r'('+code+r' · )\d+( páginas)',rf'\g<1>{count}\2',homepage)
        homepage=re.sub(r'(<article>[^\n]*?<p>'+code+r' · \d+ páginas</p><h3>).*?(</h3>)',lambda m:m[1]+html.escape(title)+m[2],homepage)
        homepage=re.sub(r'(src="covers/thumbs/'+code+r'\.webp)(?:\?[^\"]*)?"',rf'\1?v={STAMP}"',homepage)
        item.update(pdf=e['output'],canonical_source=e['source'],canonical_sha256=e['source_sha256'],source_version=STAMP,pages=count,bytes=file.stat().st_size,sha256=sha(file),editorial_revision=STAMP,qa_report=str((ROOT/e['package']/'pdf-audit.json').relative_to(ROOT)),qa_status='PASS',qa_validator='scripts/audit_plain_language_pdfs.py',tag=STAMP+'-'+code.lower())
        with tempfile.TemporaryDirectory(prefix='metsi-cover-') as tmp:
            preview=Path(tmp)/code
            subprocess.run(['pdftoppm','-f','1','-l','1','-singlefile','-scale-to','1600','-png',str(file),str(preview)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            with Image.open(preview.with_suffix('.png')) as image:
                image=image.convert('RGB');image.save(ROOT/'site/covers'/f'{code}.png',optimize=True)
                image.thumbnail((480,680));image.save(ROOT/'site/covers/thumbs'/f'{code}.webp',quality=87,method=6)
        e.update(rendered=True,visual_review=True)
        save(ROOT/e['package']/'edition-manifest.json', e)
        installed.append(dict(code=code,public=url,sha256=sha(file),source_sha256=e['source_sha256']))
        print(code,count,'pages installed',flush=True)
    # N25 is the approved prose model, not a missing rewrite.
    n25=next(x for x in manifest['documents']if x['code']=='N25')
    installed.append(dict(code='N25',public=n25['public_pdf'].removeprefix('site/'),sha256=sha(ROOT/n25['public_pdf']),approved_model_retained=True))
    manifest['updated_at']='2026-09-26';public['editorial_revision']=STAMP
    save(ROOT/'course-manifest.json',manifest);save(ROOT/'site/course-manifest.json',public)
    (ROOT/'site/index.html').write_text(homepage)
    save(EDITION/'release-plan.json',plan)
    save(EDITION/'publication-manifest.json',dict(status='LOCAL_READY_NOT_YET_PUBLISHED',revision=STAMP,documents=sorted(installed,key=lambda d:d['code'])))

if __name__=='__main__':main()
