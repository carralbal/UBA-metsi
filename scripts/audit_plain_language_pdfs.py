#!/usr/bin/env python3
"""Geometric/coverage checks on each complete revised PDF; not a prose score."""
from pathlib import Path
import argparse, collections, hashlib, json, re, subprocess, unicodedata
import pdfplumber
from pypdf import PdfReader, PdfWriter
from PIL import Image, ImageDraw
from concurrent.futures import ThreadPoolExecutor

ROOT=Path(__file__).resolve().parents[1]
EDITION=ROOT/'pedagogy/plain-language-edition'

def words(text):
    text=unicodedata.normalize('NFKD',text).casefold()
    return re.findall(r'[a-z0-9]+', ''.join(c for c in text if not unicodedata.combining(c)))

def audit(e):
    path=ROOT/e['output']
    reader=PdfReader(path)
    if reader.metadata and reader.metadata.get('/Creator',''):
        writer=PdfWriter(clone_from=reader)
        writer.metadata=None
        title=(ROOT/e['source']).read_text().splitlines()[0].removeprefix('# ')
        writer.add_metadata({'/Title':title,'/Author':'Diego Carralbal','/Subject':'Metodología del Estudio de Sistemas de Información · FCE UBA'})
        # Local HTML paths are not useful public PDF navigation targets.
        for page in writer.pages:
            for ann in page.get('/Annots',[]):
                annotation=ann.get_object();action=annotation.get('/A')
                if action and str(action.get('/URI','')).startswith('file:'):
                    del annotation['/A']
        temporary=path.with_suffix('.clean.pdf')
        writer.write(temporary)
        temporary.replace(path)
    dom=json.loads((ROOT/e['package']/'render-report.json').read_text())
    source_manifest=json.loads((ROOT/e['package']/'source-manifest.json').read_text())
    canonical_blocks=source_manifest.get('eligible_blocks',source_manifest.get('blocks',[]))
    expected=collections.Counter(words(' '.join(b['text'] for b in canonical_blocks)))
    actual=collections.Counter()
    pages=[]
    with pdfplumber.open(path) as pdf:
        for i,p in enumerate(pdf.pages,1):
            actual.update(words(''.join(c['text'] for c in p.chars)))
            # Words rather than text-stream joins preserve spaces at line ends.
            text=p.extract_text(x_tolerance=2,y_tolerance=2) or ''
            out=[c for c in p.chars if c['text'].strip() and (c['x0']<-.75 or c['x1']>p.width+.75 or c['top']<-.75 or c['bottom']>p.height+.75)]
            # Flag genuinely superposed glyphs on different baselines. Adjacent
            # kerning/accents on a common baseline are deliberately excluded.
            buckets=collections.defaultdict(list)
            overlaps=[]
            for c in p.chars:
                if not c['text'].strip():continue
                bx,by=int(c['x0']//12),int(c['top']//12)
                for xx in range(bx-1,bx+2):
                    for yy in range(by-2,by+2):
                        for d in buckets[xx,yy]:
                            if abs(c['bottom']-d['bottom'])<2:continue
                            ix=min(c['x1'],d['x1'])-max(c['x0'],d['x0'])
                            iy=min(c['bottom'],d['bottom'])-max(c['top'],d['top'])
                            if ix>min(c['width'],d['width'])*.65 and iy>min(c['height'],d['height'])*.55:
                                overlaps.append([c['text'],d['text'],round(c['top'],1)])
                buckets[bx,by].append(c)
            pages.append(dict(page=i,words=len(words(text)),images=len(p.images),out_of_bounds=len(out),overlap_candidates=len(overlaps),examples=overlaps[:8],opening=text[:130]))
    # PDF logical reading order is immaterial for multiset completeness.
    pdftext='\n'.join(p.extract_text() or '' for p in PdfReader(path).pages)
    actual=collections.Counter(words(pdftext))
    missing=expected-actual
    meaningful={w:c for w,c in missing.items() if len(w)>2}
    total=sum(expected.values())
    report=dict(code=e['code'],source_sha256=e['source_sha256'],pages=pages,source_words=total,pdf_words=sum(actual.values()),missing_word_occurrences=sum(missing.values()),missing_meaningful=meaningful,coverage=round(1-sum(missing.values())/max(1,total),5),empty_pages=[p['page']for p in pages if p['words']==0 and p['images']==0],out_of_bounds=sum(p['out_of_bounds'] for p in pages),overlap_candidates=sum(p['overlap_candidates'] for p in pages),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    (ROOT/e['package']/'pdf-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    qa=EDITION/'qa'/e['code'];qa.mkdir(parents=True,exist_ok=True)
    subprocess.run(['pdftoppm','-scale-to','330','-png',str(path),str(qa/'page')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    images=sorted(qa.glob('page-*.png'),key=lambda p:int(p.stem.rsplit('-',1)[1]))[:len(pages)]
    sheet=Image.new('RGB',(5*250,((len(images)+4)//5)*365),'#dddcd6');draw=ImageDraw.Draw(sheet)
    for i,image_path in enumerate(images):
        im=Image.open(image_path).convert('RGB');im.thumbnail((240,330));x=i%5*250;y=i//5*365
        sheet.paste(im,(x+(250-im.width)//2,y+23));draw.text((x+8,y+5),f'{e["code"]} · {i+1:02d}',fill='black')
    sheet.save(qa/'contact.jpg',quality=92)
    print(json.dumps({k:v for k,v in report.items() if k not in {'pages','missing_meaningful','source_sha256','sha256'}},ensure_ascii=False),flush=True)
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('numbers',nargs='*',type=int);args=parser.parse_args()
    plan=json.loads((EDITION/'release-plan.json').read_text())
    selected=[e for e in plan if not args.numbers or int(e['code'][1:]) in args.numbers]
    with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(audit,selected))
