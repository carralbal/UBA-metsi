# Handoff autosuficiente, N01 v12 final

## Estado

N01 v12 está compuesto, exportado y validado. Las versiones v8 a v11, sus fuentes y sus paquetes permanecen intactos. La revisión vive en la rama `n01-v12-final`.

## Entrega principal

- PDF final: `output/N01-METSI-lectura-previa-v12-final.pdf`
- Fuente editorial: `source/N01_metodologia_sin_recetas-v12.md`
- HTML y CSS editables: `index.html`, `magazine.css`
- Registro de cambios: `CHANGELOG.md`
- QA técnico e integral: `qa-report.json`, `integrity-report.json`
- Hoja de contacto: `qa/N01-contact-sheet.jpg`
- Trazabilidad: `manifest.json`, `source-manifest.json`, `provenance/`

## Reproducción

```bash
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 build_collection.py --start 1 --end 1
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 export_pdfs.py 1
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 finalize_and_qa.py 1
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 validate_n01_v12.py
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 render_contact_sheets.py 1
```

La exportación requiere Google Chrome local. La validación integral usa Poppler para medir ocupación y comparar las 29 páginas contra v11.

## Controles cerrados

- Veintinueve páginas A4 y 28 secciones sin títulos huérfanos.
- El ejemplo de la Sección 08 comienza completo en la página 12.
- El orden de lectura de la Sección 26 es encabezado, título y cinco ítems.
- La etiqueta residual de la infografía no existe en el SVG ni en el texto del PDF.
- La tapa conserva dos cadenas completas, consecutivas y visualmente idénticas a v11.
- Once URLs exactas, clickeables y con guiones preservados.
- Las 27 páginas no afectadas son píxel por píxel idénticas a v11.

## Incertidumbres

No quedan incertidumbres técnicas o editoriales abiertas desde los archivos. La publicación fuera del repositorio local no forma parte de esta pasada.
