#!/usr/bin/env python3
"""Render every page and verify map geometry, body extraction and typography."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
import json,subprocess,tempfile,unicodedata,re,statistics
from PIL import Image,ImageDraw,ImageChops
from pypdf import PdfReader
import pdfplumber
from build_legible_collection import ROOT,OUT,PACKAGES,write_json
RELEASE=ROOT/'pedagogy/readability-pilots/collection-map-release-2026-09'
def norm(s):return ''.join(c for c in unicodedata.normalize('NFKC',s).lower() if c.isalnum())
class Source(HTMLParser):
    def __init__(self):super().__init__();self.active=[];self.blocks={}
    def handle_starttag(self,t,a):
        at=dict(a)
        if 'data-source-id' in at:self.active.append([t,at['data-source-id'],[]])
    def handle_data(self,s):
        for x in self.active:x[2].append(s)
    def handle_endtag(self,t):
        if self.active and self.active[-1][0]==t:
            _,id,parts=self.active.pop();self.blocks[id]=''.join(parts)
def audit(e):
    folder=RELEASE/e['code'];pdf=folder/'reading.pdf';r=PdfReader(pdf)
    pages=folder/'qa-pages';pages.mkdir(exist_ok=True)
    subprocess.run(['pdftoppm','-scale-to','300','-png',str(pdf),str(pages/'page')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    paths=sorted((p for p in pages.glob('page-*.png') if int(p.stem.split('-')[-1])<=len(r.pages)),key=lambda p:int(p.stem.split('-')[-1]))
    assert len(paths)==len(r.pages)
    sheet=Image.new('RGB',(5*235,((len(paths)+4)//5)*330),'#dddcd6');d=ImageDraw.Draw(sheet)
    for i,p in enumerate(paths):
        im=Image.open(p).convert('RGB');im.thumbnail((225,300));x=i%5*235;y=i//5*330
        sheet.paste(im,(x+(235-im.width)//2,y+22));d.text((x+8,y+5),f'{e["code"]} · {i+1:02d}',fill='black')
    sheet.save(folder/'contact.jpg',quality=90)
    report=dict(code=e['code'],pages=len(paths),map_pages=[],source_missing=[],empty_pages=[],overflows=[])
    full=''.join(p.extract_text() or '' for p in r.pages);allnorm=norm(full)
    if e['mode']=='html-reflow':
        s=Source();s.feed((ROOT/PACKAGES[e['number']]/'index.html').read_text())
        report['eligible_source_blocks']=len(s.blocks)
        baseline_text=norm(''.join(p.extract_text() or '' for p in PdfReader(ROOT/e['baseline']).pages))
        # Running labels can interrupt an otherwise intact extracted paragraph.
        # Keep extraction warnings separate from actual source-integrity checks.
        raw_missing=[{'id':id,'text':t[:180],'also_in_baseline':norm(t) not in baseline_text} for id,t in s.blocks.items() if norm(t) and norm(t) not in allnorm]
        clean=lambda s:s.replace('distinciones','').replace('decisiones','').replace('problema','').replace('preparación','').replace('transferencia','').replace('prueba','')
        report['extraction_warnings']=raw_missing
        report['source_missing']=[x for x in raw_missing if not x['also_in_baseline'] and clean(norm(s.blocks[x['id']])) not in clean(allnorm)]
    with pdfplumber.open(pdf) as p:
        for i,page in enumerate(p.pages):
            t=r.pages[i].extract_text() or ''
            if not t.strip() and not page.images:report['empty_pages'].append(i+1)
            chars=[c for c in page.chars if c['text'].strip()]
            outside=[c for c in chars if c['x0'] < -1 or c['x1']>page.width+1 or c['top'] < -1 or c['bottom']>page.height+1]
            if outside:report['overflows'].append(dict(page=i+1,count=len(outside),text=''.join(c['text'] for c in outside)))
            if 'MAPA DE DECISIÓN' in t:
                sizes=[c['size'] for c in chars]
                report['map_pages'].append(dict(page=i+1,minimum_pt=round(min(sizes),2),median_pt=round(statistics.median(sizes),2)))
                subprocess.run(['pdftoppm','-f',str(i+1),'-l',str(i+1),'-singlefile','-scale-to','1600','-png',str(pdf),str(folder/'map-final')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    # Full-bleed pages must match the locked baseline in the reflowed documents.
    if e['mode']=='html-reflow':
        old=PdfReader(ROOT/e['baseline']);newtexts=[norm(p.extract_text() or '') for p in r.pages]
        matches=[]
        for i,p in enumerate(old.pages):
            text=norm(p.extract_text() or '')
            candidates=[j for j,t in enumerate(newtexts) if t==text]
            if len(candidates)==1:
                j=candidates[0]
                # Raster comparison uses the exact same engine and resolution.
                with tempfile.TemporaryDirectory(prefix='metsi-regression-') as tmp:
                    out=Path(tmp)/'old'
                    subprocess.run(['pdftoppm','-f',str(i+1),'-l',str(i+1),'-singlefile','-scale-to','300','-png',str(ROOT/e['baseline']),str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                    a=Image.open(out.with_suffix('.png')).convert('RGB');b=Image.open(paths[j]).convert('RGB')
                    identical=a.size==b.size and ImageChops.difference(a,b).getbbox() is None
                matches.append(dict(old_page=i+1,new_page=j+1,pixel_identical=identical))
        report['unchanged_page_comparisons']=matches
    write_json(folder/'qa-report.json',report)
    print(e['code'],'pages',len(paths),'missing',len(report['source_missing']),'outside',len(report['overflows']),flush=True)
    return report
def main():
    plan=json.loads((RELEASE/'release-plan.json').read_text())
    with ThreadPoolExecutor(max_workers=3) as pool:reports=list(pool.map(audit,plan))
    write_json(RELEASE/'qa-report.json',reports)
    for start in range(0,36,6):
        batch=reports[start:start+6];sheet=Image.new('RGB',(1500,2*780),'#dddcd6');d=ImageDraw.Draw(sheet)
        for i,e in enumerate(batch):
            file=RELEASE/e['code']/'map-final.png'
            if not file.exists():continue
            im=Image.open(file);im.thumbnail((490,745));x=(i%3)*500;y=(i//3)*780
            sheet.paste(im,(x+(500-im.width)//2,y+25));d.text((x+10,y+5),e['code'],fill='black')
        sheet.save(RELEASE/f'maps-{start+1:02d}-{min(start+6,36):02d}.jpg',quality=93)
if __name__=='__main__':main()
