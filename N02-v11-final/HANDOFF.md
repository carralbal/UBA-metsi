# Handoff autosuficiente, N02 v11

## Estado

N02 v11 está compuesto, exportado y validado como candidato de revisión. No se declara cerrado hasta recibir aprobación explícita. N00, N01 y N02 v8, v9 y v10 permanecen preservados.

## Entrega principal

- PDF: `output/N02-METSI-lectura-previa-v11-final.pdf`
- Fuente: `source/N02_el_sistema_no_cabe_en_una_aplicacion-v11.md`
- Editables: `index.html`, `magazine.css`, `diagrams/N02-mapa-decision.svg`
- Informe: `INFORME-CORRECCION-v11.md`
- Cambios: `CHANGELOG.md`
- QA: `qa-report.json`, `integrity-report.json`, `qa/N02-contact-sheet.jpg`, `visual-audit.md`
- Trazabilidad: `manifest.json`, `source-manifest.json`, `page-spread-plan.json`, `provenance/`

## Reproducción

```bash
python3 build_collection.py --start 2 --end 2
python3 export_pdfs.py 2
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 finalize_and_qa.py 2
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 validate_n02_v11.py
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 render_contact_sheets.py 2
```

La exportación usa Google Chrome local. La validación usa pypdf, Poppler y Pillow.

## Decisiones editoriales de v11

- Se eliminaron las capitulares problemáticas de las páginas 10, 17 y 23. El texto conserva orden de lectura natural y ninguna inicial queda aislada.
- El corte entre las páginas 21 y 22 fue recompaginado. Toda continuación de párrafo tiene al menos cuatro líneas y quedan al menos dos líneas en la página de origen.
- Las preguntas 3, 4 y 6 usan registro académico impersonal. La página 25 incorpora una instrucción de entrega diferenciada de la lista.
- La tapa conserva el sistema visual y presenta el eyebrow en dos líneas independientes: `LECTURA PREVIA` y `EDICIÓN 2026`.
- La ruta queda explicitada como 16 PRUEBA, 17 TRANSFERENCIA y 18 PRUEBA.
- Se mantienen seis preguntas. La URL canónica de IS2020 coincide con N01. La raya del título oficial de ISO permanece por ser puntuación bibliográfica.

## Controles cerrados

- El PDF tiene 27 páginas A4 y 22 secciones numeradas.
- Todas las 17 entradas de Referencias base tienen anclaje en el cuerpo.
- Las 15 URLs distintas están presentes en texto y como anotaciones clickeables.
- El PDF conserva estructura etiquetada, idioma `es-AR`, folio y pie enlazado en las 27 páginas.
- No hay títulos huérfanos, páginas ordinarias por debajo de media ocupación ni continuaciones de párrafo de menos de cuatro líneas.
- La estructura de listas coincide exactamente con v10. El glosario mantiene tres columnas legibles y no presenta colisiones.
- La validación automática y la inspección visual de las 27 páginas resultan PASS.

## Identidad del artefacto

- SHA256: `4fd477899af5cf26f6ce901467d5610164a1c3cde3c50c4d7f2fad64ebea9b43`
- Tamaño: 28.136.987 bytes.
- Modificación: 2026-09-02 18:45:04 -03.
- Es un archivo nuevo generado como v11, no una copia renombrada de v10.

## Incertidumbre

No quedan incertidumbres técnicas abiertas en los archivos. La decisión pendiente es editorial: aprobar N02 v11 como versión final o devolver observaciones puntuales.
