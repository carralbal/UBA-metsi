"""Verify scope and source preservation; not a test of student comprehension."""
from pathlib import Path
import hashlib, json, re, subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'pedagogy/pedagogical-review-20260926'
BASE = 'b26f9a1'
titles = json.loads((OUT/'titles.json').read_text())
documents = json.loads((ROOT/'course-manifest.json').read_text())['documents']
records = []
for d in documents:
    if d['code'] == 'N00':
        continue
    path = d['canonical_source']
    old = subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT,text=True)
    new = (ROOT/path).read_text()
    def section(text, heading):
        match = re.search(r'^## '+re.escape(heading)+r'\n(.*?)(?=^## |\Z)',text,re.M|re.S)
        return match[1].strip() if match else ''
    old_refs, new_refs = section(old,'Referencias base'),section(new,'Referencias base')
    assert old_refs == new_refs, (d['code'],'bibliography changed')
    assert section(old,'Referentes') == section(new,'Referentes'), (d['code'],'referents changed')
    assert new.count('## Para orientar la lectura\n') == 1
    assert re.search(r'^#{2,3} Ejemplo resuelto',new,re.M)
    assert new.splitlines()[0] == '# '+d['code']+' · '+titles[d['code']]['title']
    records.append(dict(
        code=d['code'], source=path,
        source_sha256=hashlib.sha256(new.encode()).hexdigest(),
        bibliography_unchanged=True, referents_unchanged=True,
        orientation_present=True, worked_example_present=True,
        previous_summary_words=len(section(old,'Síntesis').split()),
        current_summary_words=len(section(new,'Síntesis').split()),
        word_delta=len(new.split())-len(old.split()),
        title=titles[d['code']]['title'],
    ))
assert len(records)==36
report=dict(baseline_commit=BASE,scope='36 readings; N00 remains a guide',
            limitation='Structural checks do not certify pedagogy or PDF layout.',
            documents=records)
(OUT/'source-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(readings=len(records),bibliographies_preserved=36,
    summary_words_before=sum(d['previous_summary_words'] for d in records),
    summary_words_after=sum(d['current_summary_words'] for d in records),
    total_word_delta=sum(d['word_delta'] for d in records)),ensure_ascii=False))
