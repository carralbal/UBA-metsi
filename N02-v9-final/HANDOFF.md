# Handoff autosuficiente, N02 v9

## Estado

N02 v9 está compuesto, exportado y validado como candidato de revisión. N02 v8 permanece intacto y verificable por hash. N00 y N01 no fueron modificados. Esta entrega no declara N02 cerrado: el cierre editorial depende de la aprobación del usuario.

## Entrega principal

- PDF: `output/N02-METSI-lectura-previa-v9-final.pdf`
- Fuente revisada: `source/N02_el_sistema_no_cabe_en_una_aplicacion-v9.md`
- Editables: `index.html`, `magazine.css`, `diagrams/N02-mapa-decision.svg`
- Cambios: `CHANGELOG.md`
- QA: `qa-report.json`, `integrity-report.json`, `qa/N02-contact-sheet.jpg`
- Trazabilidad: `manifest.json`, `source-manifest.json`, `page-spread-plan.json`, `provenance/`

## Reproducción

```bash
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 build_collection.py --start 2 --end 2
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 export_pdfs.py 2
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 finalize_and_qa.py 2
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 validate_n02_v9.py
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 render_contact_sheets.py 2
```

La exportación usa Google Chrome local. La validación usa Poppler, pypdf, pdfplumber y Pillow.

## Cambios controlados respecto de v8

- Se creó una fuente v9 separada. La fuente v8 conserva SHA256 `00a8899601af4a1aade38645479c6f5f2dab63dfdcaa914e0982aca20bdb529b`.
- Se sumaron 56 palabras para anclar seis entradas que no quedaban identificadas de forma inequívoca. No se agregaron secciones, casos ni líneas argumentales.
- Se normalizaron cuatro consignas a voseo y se escribió con palabras el título de las cinco píldoras.
- Se redujeron cuatro pausas fotográficas internas a las dos que fija el estándar actual. Las fotografías descartadas como pausa permanecen preservadas entre los activos.
- Referentes y Referencias base pasaron a criterio SIN NUM.; las 22 secciones argumentales mantienen orden y numeración.
- La composición de referencias pasó a dos columnas minimalistas.
- Se reemplazaron descripciones genéricas por 20 textos alternativos específicos.

## Controles de regresión

- Baseline v8 PDF: 44.670.499 bytes; SHA256 `8b9300ae2f7cbac11fa3ce4b122b0750567f410ad581eabb585507b1e7582313`.
- Candidato v9 PDF: 26.459.061 bytes; SHA256 `fd6e4c556dac35149f4b9496feb262a5c96f1652b38abf4690f084d936319ee5`.
- Veintisiete páginas A4, todas con folio y pie enlazado.
- Veintidós títulos con cuerpo en la misma página.
- Diecisiete referencias ancladas. Dieciséis URLs presentes en texto; quince destinos únicos presentes como anotaciones.
- Seis referentes y cuatro voces de Hotel Horizonte con retratos distintos.
- Seis fotografías editoriales usadas sin repetición y sin reutilizar la imagen de portada.
- Cero páginas vacías, cero fuentes prohibidas y cero marcadores pendientes.

## Incertidumbres

No quedan incertidumbres técnicas abiertas desde los archivos. La selección de la v9 como versión cerrada, o una nueva ronda de observaciones de lectura, es una decisión editorial del usuario.
