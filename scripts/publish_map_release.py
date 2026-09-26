#!/usr/bin/env python3
"""Install audited replacements locally. Git publication remains a separate step."""
import json,re,shutil
from pathlib import Path
from pypdf import PdfReader
from build_legible_collection import ROOT,OUT,write_json,sha
RELEASE=ROOT/'pedagogy/readability-pilots/collection-map-release-2026-09'
STAMP='mapas-20260926'

def main():
    plan=json.loads((RELEASE/'release-plan.json').read_text())
    audit={r['code']:r for r in json.loads((RELEASE/'qa-report.json').read_text())}
    approval=json.loads((RELEASE/'visual-approval.json').read_text())
    assert approval['status']=='PASS' and len(approval['documents'])==36
    for e in plan:
        qa=audit[e['code']]
        assert not qa['empty_pages'] and not qa['overflows'] and not qa['source_missing'],e['code']
        source=ROOT/e['output'];assert sha(source)==approval['documents'][e['code']]
        target=ROOT/'site'/e['public']
        assert sha(target) in (e['baseline_sha256'],sha(source)),(e['code'],'Public file changed since archive')
        if e['mode']!='audited-preserved':
            geometry=json.loads((OUT/e['code']/'geometry.json').read_text())
            assert not geometry['overlaps'] and not geometry['outside'] and not geometry.get('rowOverflow',[])
            shutil.copy2(source,target)
    smpath=ROOT/'site/course-manifest.json';sm=json.loads(smpath.read_text())
    manifestpath=ROOT/'course-manifest.json';manifest=json.loads(manifestpath.read_text())
    entries={e['code']:e for e in plan};homepage=(ROOT/'site/index.html').read_text()
    for reading in sm['readings']:
        if reading['code']=='N00':continue
        e=entries[reading['code']];source=ROOT/e['output'];count=len(PdfReader(source).pages)
        reading['pages']=count;reading['pdf']=e['public']+f'?v={STAMP}';reading['revision']=STAMP
        homepage=re.sub(r'('+re.escape(e['code'])+r' · )\d+( páginas)',rf'\g<1>{count}\2',homepage)
        homepage=re.sub(r'href="'+re.escape(e['public'])+r'(?:\?[^"]*)?"','href="'+reading['pdf']+'"',homepage)
        item=next(d for d in manifest['documents'] if d['code']==e['code'])
        item.update(pdf=e['output'],public_pdf='site/'+e['public'],pages=count,bytes=source.stat().st_size,sha256=sha(source),editorial_revision=STAMP,qa_report=str((RELEASE/'qa-report.json').relative_to(ROOT)),qa_status='PASS')
        if e['number']==25:
            canonical=ROOT/'pedagogy/readability-pilots/N25/N25-lectura-pedagogica-v1.md'
            item.update(canonical_source=str(canonical.relative_to(ROOT)),canonical_sha256=sha(canonical),source_version='readability-approved-v1')
    sm['editorial_revision']=STAMP;manifest['updated_at']='2026-09-26'
    write_json(smpath,sm);write_json(manifestpath,manifest)
    (ROOT/'site/index.html').write_text(homepage)
    write_json(RELEASE/'publication-manifest.json',dict(status='LOCAL_READY',revision=STAMP,documents=[dict(code=e['code'],public=e['public'],sha256=sha(ROOT/'site'/e['public'])) for e in plan]))
    print('36 entries updated; 34 PDFs replaced; N00, N06 and N34 preserved.')
if __name__=='__main__':main()
