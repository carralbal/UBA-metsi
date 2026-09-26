#!/usr/bin/env python3
"""Check source fidelity, full-document visual regression and effective map type."""
from pathlib import Path
import json
import subprocess
import tempfile
from collections import Counter

from PIL import Image, ImageChops, ImageDraw
from pypdf import PdfReader
import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / 'N25-v11-editorial'
NEW = ROOT / 'N25-v12-editorial'
OUT = ROOT / 'pedagogy/readability-pilots/N25'


def main():
    before = OLD / 'output/N25-METSI-lectura-previa-v11.pdf'
    after = NEW / 'output/N25-METSI-lectura-previa-v12.pdf'
    readers = [PdfReader(p) for p in (before, after)]
    count = len(readers[1].pages)
    assert len(readers[0].pages) == count, 'Unexpected pagination change'
    map_pages = [i for i,p in enumerate(readers[1].pages) if '46 días para un cambio.' in (p.extract_text() or '')]
    assert len(map_pages) == 1
    map_index = map_pages[0]
    sources = [json.loads((p/'source-manifest.json').read_text()) for p in (OLD, NEW)]
    assert sources[0]['eligible_blocks'] == sources[1]['eligible_blocks'], 'Source text changed'
    integrity = json.loads((NEW/'integrity-report.json').read_text())
    assert integrity['status'] == 'PASS'
    changed = []
    sheet = Image.new('RGB',(5*310,5*448),'#d8d8d5')
    draw = ImageDraw.Draw(sheet)
    with tempfile.TemporaryDirectory(prefix='metsi-n25-regression-') as temp:
        for label,pdf in [('before',before),('after',after)]:
            subprocess.run(['pdftoppm','-r','80','-png',str(pdf),str(Path(temp)/label)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        old_images=sorted(Path(temp).glob('before-*.png'))
        new_images=sorted(Path(temp).glob('after-*.png'))
        for i,(a,b) in enumerate(zip(old_images,new_images)):
            with Image.open(a) as ia, Image.open(b) as ib:
                if ia.size != ib.size or ImageChops.difference(ia.convert('RGB'),ib.convert('RGB')).getbbox():
                    changed.append(i+1)
                thumb=ib.convert('RGB');thumb.thumbnail((290,410))
                x=(i%5)*310+10;y=(i//5)*448+26
                sheet.paste(thumb,(x,y));draw.text((x,y-18),str(i+1),fill='#191919')
        sheet.save(OUT/'N25-v12-control-paginas.png')
    assert changed == [map_index+1], f'Unexpected changed pages: {changed}'
    with pdfplumber.open(after) as pdf:
        page=pdf.pages[map_index]
        sizes=Counter(round(float(c['size']),2) for c in page.chars if c['text'].strip())
        assert min(sizes) >= 9.8, sizes
        clipped=[c['text'] for c in page.chars if c['x0']<0 or c['x1']>page.width or c['top']<0 or c['bottom']>page.height]
        assert not clipped
    report=dict(status='PASS',pages=count,map_page=map_index+1,changed_pages=changed,unchanged_pages=count-1,source_blocks=integrity['source_block_count'],source_text_equal=True,effective_font_sizes_pt=dict(sorted(sizes.items())),clipped_characters=clipped,publication='LOCAL_ONLY')
    (OUT/'N25-v12-integracion-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__': main()
