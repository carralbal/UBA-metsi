# Handoff autosuficiente, N02 v10

## Estado

N02 v10 está compuesto, exportado y validado como candidato de revisión. No se declara cerrado hasta recibir aprobación explícita. N02 v8 y v9 permanecen preservados; N00 y N01 no fueron modificados.

## Entrega principal

- PDF: `output/N02-METSI-lectura-previa-v10-final.pdf`
- Fuente: `source/N02_el_sistema_no_cabe_en_una_aplicacion-v10.md`
- Editables: `index.html`, `magazine.css`, `diagrams/N02-mapa-decision.svg`
- Cambios: `CHANGELOG.md`
- QA: `qa-report.json`, `integrity-report.json`, `qa/N02-contact-sheet.jpg`, `visual-audit.md`
- Trazabilidad: `manifest.json`, `source-manifest.json`, `page-spread-plan.json`, `provenance/`

## Reproducción

```bash
python3 build_collection.py --start 2 --end 2
python3 export_pdfs.py 2
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 finalize_and_qa.py 2
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 validate_n02_v10.py
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 render_contact_sheets.py 2
```

La exportación usa Google Chrome local. La validación usa pypdf, Poppler y Pillow.

## Decisiones editoriales de v10

- La sexta ficha de Referentes ya no representa a una institución: corresponde a Elham Tabassi y se vincula con el AI RMF 1.0 de 2023.
- Checkland y Poulter coinciden en la ficha, el cuerpo y Referencias base.
- El cuerpo no contiene rayas de inciso; las rayas que permanecen pertenecen a títulos bibliográficos o rangos de páginas.
- El caso HH-02 conserva la fotografía, el contenido y la tabla, pero corrige el epígrafe y el orden de lectura.
- Síntesis se compone en dos columnas anchas; el glosario usa tres columnas legibles; Referencias base permanece minimalista, a dos columnas y en página propia.
- El final conserva 27 páginas, dos pausas internas y la secuencia canónica de fósforos como última página.

## Controles cerrados

- Todas las 17 entradas de Referencias base tienen anclaje en el cuerpo.
- Las 15 URLs distintas están presentes en texto y como anotaciones clickeables.
- El PDF tiene `/StructTreeRoot`, `/MarkInfo` marcado e idioma `es-AR`.
- El orden de lectura coloca el título de HH-02 antes de su epígrafe, la tabla antes de las voces y el título de las píldoras antes de sus cinco ítems.
- Todas las páginas son A4, tienen folio y pie enlazado; la página final tiene leyenda y texto alternativo estructural.
- La validación automática y la inspección visual de las 27 páginas resultan PASS.

## Incertidumbre

No quedan incertidumbres técnicas abiertas en los archivos. La única decisión pendiente es editorial: aprobar N02 v10 como versión final o devolver observaciones puntuales.
