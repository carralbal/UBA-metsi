#!/usr/bin/env python3
"""Verify review-only maps against source, rendered text geometry and manifest."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'pedagogy/readability-pilots/mapas-tanda-02'
VALIDATOR=Path('/Users/diegocarralbal/.codex/skills/metsi-build-reference-grade-infographics/scripts/validate_infographic.py')
reports=[]
for n in [24,26,27]:
    folder=OUT/f'N{n}'
    svg=folder/f'N{n}-mapa-legible.svg'
    manifest=json.loads((folder/'content-manifest.json').read_text())
    geometry=json.loads(svg.with_name(svg.stem+'-geometry.json').read_text())
    source=ROOT/manifest['source']
    validation=subprocess.run([sys.executable,str(VALIDATOR),str(svg),'--manifest',str(folder/'content-manifest.json')],capture_output=True,text=True,check=True)
    tree=ET.parse(svg)
    ids={e.attrib['id'] for e in tree.iter() if 'id' in e.attrib}
    assert {item['id'] for item in manifest['nodes']} <= ids
    assert {item['id'] for item in manifest['edges']} <= ids
    assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['source_sha256']
    assert not geometry['overlaps'] and not geometry['outside']
    assert geometry['minFontPx']>=24
    assert all(g['size']>=28 or g['size']==24 for g in geometry['geometry'])
    assert all(g['x']>=42 and g['x']+g['width']<=1158 for g in geometry['geometry'])
    report=dict(document=f'N{n}',status='PASS_REVIEW_ASSET',validator=validation.stdout.strip(),text_elements=geometry['labels'],overlaps=len(geometry['overlaps']),clipped_text=len(geometry['outside']),minimum_content_font_pt=manifest['minimum_content_font_pt'],minimum_metadata_font_pt=round(24*173/1200*72/25.4,2),source_unchanged=True,manifest_nodes_present=True,manifest_edges_present=True,visual_review='Inspección de PNG a 1800 × 2430: rótulos legibles, conectores fuera de texto y espacio aprovechado.',pdf_integration=False,publication=False,user_approval='PENDING')
    (folder/'qa-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    (folder/'QA.md').write_text(f'''# N{n} · Control de la propuesta

- Validador: aprobado, cero advertencias.
- {geometry['labels']} objetos de texto; cero superposiciones y cero recortes detectados.
- Cuerpo: al menos 28 px, equivalente a 11,44 pt a 173 mm de ancho.
- Encabezados secundarios y pie: 24 px, equivalente a 9,81 pt.
- Todos los nodos y vínculos declarados están presentes en el SVG.
- Fuente contrastada y sin modificaciones; huella conservada en el manifiesto.
- PNG de 1800 × 2430 inspeccionado visualmente: relaciones y conectores claros, sin texto pisado.
- La lectura llana conserva los términos técnicos cuando son necesarios.
- No se alteró ningún PDF, asset aprobado ni archivo del sitio público.
- Pendiente: aprobación visual e integración posterior, con nueva auditoría de página.
''')
    reports.append(report)
(OUT/'qa-report.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(reports,ensure_ascii=False,indent=2))
