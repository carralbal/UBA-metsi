"""Build traceable atlas and bibliography data from the published readings."""
from pathlib import Path
from html import escape
import json, re, unicodedata, hashlib
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "pedagogy/site-alignment-20260927"
def norm(s):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower())

catalog = json.loads((ROOT/"site/course-manifest.json").read_text())
docs = {d["code"]: d for d in json.loads((ROOT/"course-manifest.json").read_text())["documents"] if d["code"] != "N00"}
texts, pages = {}, {}
for code, d in docs.items():
    texts[code] = (ROOT/d["canonical_source"]).read_text()
    assert hashlib.sha256((ROOT/d["canonical_source"]).read_bytes()).hexdigest() == d["canonical_sha256"], code
    path = ROOT/d["public_pdf"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == d["sha256"], code
    cache = Path("/private/tmp") / ("metsi-text-" + d["sha256"] + ".json")
    if cache.exists():
        pages[code] = json.loads(cache.read_text())
    else:
        pages[code] = [p.extract_text() for p in PdfReader(path).pages]
        cache.write_text(json.dumps(pages[code]))

def reference(number, fragment):
    code = f"N{number:02}"
    headings = re.findall(r"^#{2,3} (.+)$", texts[code], re.M)
    matches = [h for h in headings if h.startswith(fragment)]
    assert len(matches) == 1, (code, fragment, matches)
    heading = matches[0]
    found = [i+1 for i,p in enumerate(pages[code]) if i >= 3 and norm(heading) in norm(p)]
    assert found, (code, heading, "heading not found in published PDF")
    page = found[0]
    d = docs[code]
    return {"code": code, "section": heading, "page": page, "title": d["title"],
            "href": d["public_pdf"].removeprefix("site/") + "?v=" + d["editorial_revision"] + f"#page={page}"}

items = []
for row in json.loads((QA/"atlas-selection.json").read_text()):
    ident, label, block, band, status, description, refs, *note = row
    items.append(dict(id=ident,label=label,block=block,band=band,status=status,description=description,
                      refs=[reference(n,fragment) for n,fragment in refs],
                      referenceLabel=note[0] if note else "Dónde empezar · sección y página"))
blocks = [
    ("Comprender", "Comprender el sistema", "N01—N04", "Entendé qué produce el resultado antes de elegir una solución."),
    ("Investigar", "Investigar el problema", "N05—N10", "Escuchá a las personas y comprobá qué está pasando."),
    ("Modelar", "Modelar para decidir", "N11—N16", "Usá datos y modelos para responder preguntas concretas."),
    ("Decidir", "Decidir cómo intervenir", "N17—N20", "Compará alternativas y acordá cómo avanzar y cuándo revisar."),
    ("Entregar", "Entregar valor y aprender", "N21—N25", "Probá cambios pequeños, comprobá resultados y mejorá el flujo."),
    ("Operar", "Operar y mejorar el servicio", "N26—N30", "Prepará el uso real, los acuerdos con terceros y la respuesta ante fallas."),
    ("Gobernar", "Gobernar el uso de IA", "N31—N33", "Definí qué puede hacer la IA, quién controla y cuándo detenerla."),
    ("Integrar", "Integrar y compartir lo aprendido", "N34—N36", "Conectá las decisiones y explicá qué aprendiste y qué falta comprobar.")
]
payload = dict(items=items, blocks=[dict(label=b[0],title=b[1],range=b[2],claim=b[3]) for b in blocks])
(ROOT/"site/covers/atlas-data.js").write_text("window.METSI_ATLAS = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n")
(QA/"atlas-verification.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n")
print(f"Verified {len(items)} practices, {sum(len(x['refs']) for x in items)} exact PDF destinations.")

# Compare the program's common bibliography with the actual reading bibliographies.
program = (ROOT/"programa/programa-metsi-2026.md").read_text()
biblios = {c:t.split("## Referencias base")[-1] for c,t in texts.items()}
records = []
for line in program.split("## Referentes y bibliografía")[1].split("## Revisión y actualización")[0].splitlines():
    if not line.startswith("- "): continue
    title = re.search(r"[“\"]([^”\"]+)[”\"]", line) or re.search(r"\*([^*]+)\*", line)
    if not title: continue
    key = norm(title[1].split(":")[0].split(",")[0])
    author = norm(line[2:].split("(")[0].split(",")[0])
    year = re.search(r"\((\d{4})\)", line)[1]
    matches = {}
    for code,bib in biblios.items():
        entries = [l.removeprefix("- ") for l in bib.splitlines()
                   if l.startswith("- ") and key in norm(l)
                   and norm(l[2:]).startswith(author) and f"({year})" in l]
        if entries: matches[code] = entries
    records.append({"program_entry":line[2:],"readings":matches})
(QA/"bibliography-comparison.json").write_text(json.dumps(records,ensure_ascii=False,indent=2)+"\n")
for r in records:
    print(re.search(r"\*([^*]+)",r["program_entry"])[1], ":", ",".join(r["readings"]) or "NO EXACT WORK MATCH")

def compact_codes(codes):
    groups = []
    for code in codes:
        n = int(code[1:])
        if groups and n == groups[-1][-1] + 1: groups[-1].append(n)
        else: groups.append([n])
    return ", ".join(f"N{g[0]:02}" if len(g)==1 else f"N{g[0]:02}–N{g[-1]:02}" for g in groups)

# Static bibliography stays available without JavaScript.
html = ['<!-- BEGIN ALIGNED REFERENCES -->', '<div class="reference-index">',
        '<details><summary>Obras del programa y dónde encontrarlas</summary>',
        '<p>Selección general compartida con el programa. Los enlaces identifican la obra y el año citados; cada lectura puede agregar otras ediciones y fuentes.</p>', '<ol>']
for r in records:
    assert r['readings'], r['program_entry']
    entry = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escape(r['program_entry']))
    links = []
    for code in r['readings']:
        ref = reference(int(code[1:]), 'Referencias base')
        links.append(f'<a href="{escape(ref["href"])}" target="_blank" rel="noopener" aria-label="Bibliografía de {code}, página {ref["page"]} (nueva pestaña)">{code}</a>')
    html.append(f'<li><p>{entry}</p><p class="reference-locations">En las lecturas: {" · ".join(links)}</p></li>')
html.extend(['</ol></details>', '<details><summary>Bibliografía específica de las 36 lecturas</summary>', '<p>Cada enlace abre Referencias base en el PDF publicado. No incluye la guía N00.</p>', '<ol class="reading-reference-grid">'])
for code in docs:
    ref = reference(int(code[1:]), 'Referencias base')
    html.append(f'<li><a href="{escape(ref["href"])}" target="_blank" rel="noopener">{code} · {escape(ref["title"])}</a><small>Referencias base · pág. {ref["page"]}</small></li>')
html.extend(['</ol></details>', '</div>', '<!-- END ALIGNED REFERENCES -->'])
home = (ROOT/'site/index.html').read_text()
section = '\n'.join(html)
if '<!-- BEGIN ALIGNED REFERENCES -->' in home:
    home = re.sub(r'<!-- BEGIN ALIGNED REFERENCES -->[\s\S]*?<!-- END ALIGNED REFERENCES -->', lambda _: section, home)
else:
    home = home.replace('      <div class="reference-actions">', section+'\n      <div class="reference-actions">')
(ROOT/'site/index.html').write_text(home)

for code, block in zip(catalog['blocks'], payload['blocks']):
    code['title'] = block['title']
(ROOT/'site/course-manifest.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')

# The same source-derived concordance is printed in the program.
program = re.sub(r'\nLecturas que citan esta obra y año: [^\n]+\n', '\n', program)
for r in records:
    needle = '- ' + r['program_entry']
    program = program.replace(needle, needle + '\n\nLecturas que citan esta obra y año: '+compact_codes(r['readings'])+'.')
(ROOT/'programa/programa-metsi-2026.md').write_text(program)
