#!/usr/bin/env python3
"""Compose complete revised readings, never splice new maps into old prose."""
from pathlib import Path
import argparse
import hashlib
import html
import json
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build_collection as first
import build_block_c_editorial as later

EDITION = ROOT / 'pedagogy/plain-language-edition'
MAPS = ROOT / 'editorial-standard/approved-infographics/collection-legible-2026-09'
VERSIONS = {1:19, 2:16, 3:11, 4:10, 5:11, 6:11, 7:11, 8:11, 9:11, 10:10}
ORIGINAL_CLASSES = first.section_classes

def classes(number, index, title):
    # Do not let an instrument named HH-xx become a second Hotel photo feature.
    result = ['reading-section', 'edition-section']
    if index == 1: result.append('edition-question')
    elif index == 2: result.append('opening-story')
    if title.startswith('Hotel Horizonte'): result.append('hotel-case')
    if title == 'Tesis': result.append('thesis-standard')
    if title == 'Referencias base': result.append('references')
    if title == 'Preguntas de preparación': result.append('questions')
    if title == 'Glosario esencial': result.append('glossary-two-column')
    if title == 'Cinco píldoras para recordar': result.append('pill-summary')
    if index != 1: result.append('two-column')
    return result

def core(number, index, title):
    return index <= 4 or title.startswith(('Movimiento', 'Hotel Horizonte', 'Instrumento', 'Producto mínimo')) or title in {'Síntesis', 'Preguntas de preparación'}

def build(number):
    source = EDITION / f'N{number:02d}.md'
    assert source.is_file(), source
    first.section_classes = classes
    first.prioritized_contents_core = core
    first.apply_n01_pagination_groups = lambda body, title: body
    first.split_n02_glossary_for_print = lambda body: body
    first.split_n08_glossary_for_print = lambda body: body
    first.keep_n08_observation_instrument_together = lambda body: body
    if number <= 10:
        old = ROOT / f'N{number:02d}-v{VERSIONS[number]}-final'
        out = ROOT / f'N{number:02d}-v{VERSIONS[number]+1}-final'
        if not out.exists():
            shutil.copytree(old, out, ignore=shutil.ignore_patterns('output', 'source'))
        first.SOURCE_PATH_OVERRIDES[number] = source
        first.OUTPUT_ROOT_OVERRIDES[number] = out
        first.PACKAGE_VERSION_LABELS[number] = f'v{VERSIONS[number]+1}-final'
        first.build_document(number)
    else:
        out = ROOT / f'N{number:02d}-v13-editorial'
        later.SOURCES[number] = source
        later.PACKAGE_VERSION = 13
        later.BASELINE_VERSION = 10
        # New h2 headings are real editorial units, not unrecognized additions
        # to the short question opener from the old edition.
        later.coalesce_editorial_sections = lambda n, sections: sections
        later.MOVEMENT_EDITORIAL_CLOSES = set()
        later.DEFERRED_INFOGRAPHIC_DOCS = set()
        later.LANDSCAPE_INFOGRAPHICS = set()
        later.build(number)

    content = (out / 'index.html').read_text()
    content = content.replace('<body ', '<body id="plain-edition" ', 1)
    content = re.sub(r'\bdocument-n\d+\b', 'plain-edition', content, count=1)
    # Historical per-document selectors encode the old text lengths. Retain
    # cover/referent styling, but use one flow layout for the revised body.
    if 'plain-edition' not in content:
        content = content.replace('<body class="', '<body class="plain-edition ', 1)
    content = content.replace('METODOLOGÍA DE SISTEMAS DE INFORMACIÓN', 'METODOLOGÍA DEL ESTUDIO DE SISTEMAS DE INFORMACIÓN')
    # Always display the source title, including N04/N05 whose old cover helper
    # hardcodes an earlier editorial title.
    title, sections = first.parse_source(source)
    clean_title = re.sub(r'^N\d+\s*[·—-]\s*', '', title)
    content = re.sub(r'(<h1\b[^>]*>).*?(</h1>)', lambda m:m[1]+html.escape(clean_title)+m[2], content, count=1, flags=re.S)

    map_dir = MAPS / f'N{number:02d}'
    if map_dir.exists():
        target = out / 'diagrams' / f'N{number:02d}-mapa-legible.svg'
        shutil.copy2(map_dir / target.name, target)
        alt = html.escape((map_dir / 'alt-text.md').read_text().strip(), quote=True)
        plate = f'<figure class="edition-map"><img src="diagrams/{target.name}" alt="{alt}"></figure>'
        if number >= 11:
            content, count = re.subn(r'<section class="approved-infographic-page[^\"]*">.*?</section>', plate, content, count=1, flags=re.S)
            assert count == 1, (number, 'missing map')
        else:
            figures = [m for m in re.finditer(r'<figure\b[^>]*>.*?</figure>', content, re.S) if re.search(r'<img[^>]+src="[^\"]+\.svg"', m[0])]
            assert len(figures) == 1, (number, len(figures))
            match = figures[0]
            content = content[:match.start()] + plate + content[match.end():]
    # The already-legible N06/N34 original diagrams stay unchanged.
    if number in {6, 34}:
        content = re.sub(r'(<figure\b[^>]*class=")([^\"]*)("[^>]*>\s*<img[^>]*src="[^\"]+\.svg")', r'\1\2 edition-map\3', content)
    if number == 34:
        content = re.sub(r'<section class="approved-infographic-page[^\"]*">.*?(<img src="diagrams/[^>]+>).*?</section>', r'<figure class="edition-map">\1</figure>', content, count=1, flags=re.S)
    if number == 6 and 'edition-map' not in content:
        alt = html.escape((out/'diagrams/alt-text.md').read_text().strip(), quote=True)
        content = content.replace('</main>', f'<figure class="edition-map"><img src="diagrams/N06-mapa-decision.svg" alt="{alt}"></figure></main>', 1)
    # The map occupies its own page AFTER the complete thesis, never between
    # a heading and the paragraph that explains it.
    plate_matches = list(re.finditer(r'<figure class="[^\"]*edition-map[^\"]*"[^>]*>.*?</figure>', content, re.S))
    assert len(plate_matches) == 1, (number, 'one complete decision map required')
    plate_markup = plate_matches[0][0]
    if number == 6:
        plate_markup = (EDITION/'N06-map.html').read_text().strip()
    content = content[:plate_matches[0].start()] + content[plate_matches[0].end():]
    thesis_match = next(m for m in re.finditer(r'<section class="[^\"]*reading-section[^\"]*"[^>]*>.*?</section>', content, re.S) if re.search(r'<h2[^>]*>Tesis</h2>', m[0]))
    content = content[:thesis_match.end()] + plate_markup + content[thesis_match.end():]
    content = content.replace('<div class="block-c-fullbleed-anchor" aria-hidden="true"></div>', '')
    def route_label(match):
        fragment=match[0]
        heading=re.search(r'<h2[^>]*>(.*?)</h2>',fragment,re.S)
        if not heading:return fragment
        label=html.unescape(re.sub('<[^>]+>','',heading[1]))
        route=('PROBLEMA' if label in {'Pregunta profesional','Tesis'} or label.startswith('Hotel Horizonte') else
               'DISTINCIONES' if label.startswith('Movimiento 1') else
               'DECISIONES' if label.startswith(('Movimiento 2','Instrumento')) else
               'PRUEBA' if label.startswith('Movimiento 3') else
               'PREPARACIÓN' if label in {'Síntesis','Glosario esencial','Preguntas de preparación','Cinco píldoras para recordar'} else 'DESARROLLO')
        return re.sub(r'(<div class="section-marker">.*?</div>)',lambda marker:re.sub(r'<em>[^<]*</em>',f'<em>{route}</em>',marker[0],count=1),fragment,count=1,flags=re.S)
    content=re.sub(r'<section class="[^\"]*reading-section[^\"]*"[^>]*>.*?</section>',route_label,content,flags=re.S)
    content = content.replace('</head>', '<link rel="stylesheet" href="edition.css"></head>', 1)
    (out / 'index.html').write_text(content)
    shutil.copy2(EDITION / 'edition.css', out / 'edition.css')
    # Actual source coverage, independent of the builder's historical audit flag.
    manifest = json.loads((out / 'source-manifest.json').read_text())
    ids = re.findall(r'data-source-id="([^\"]+)"', content)
    entries = manifest.get('eligible_blocks', manifest.get('blocks', []))
    source_ids = [entry['source_id'] for entry in entries]
    assert not set(source_ids)-set(ids), (number, 'missing source blocks')
    assert len(ids) == len(set(ids)), (number, 'duplicate source blocks')
    result = dict(code=f'N{number:02d}', package=str(out.relative_to(ROOT)), html=str((out/'index.html').relative_to(ROOT)), source=str(source.relative_to(ROOT)), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), source_blocks=len(source_ids), output=str((out/'output'/f'N{number:02d}-METSI-lectura-previa.pdf').relative_to(ROOT)), rendered=False, visual_review=False, published=False)
    (out/'edition-manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('numbers', nargs='*', type=int)
    args = parser.parse_args()
    plan_file = EDITION/'release-plan.json'
    plans = {r['code']:r for r in json.loads(plan_file.read_text())} if plan_file.exists() else {}
    for n in args.numbers or [i for i in range(1,37) if i != 25]:
        result = build(n)
        plans[result['code']] = result
        plan_file.write_text(json.dumps(sorted(plans.values(), key=lambda r:r['code']), ensure_ascii=False, indent=2)+'\n')
