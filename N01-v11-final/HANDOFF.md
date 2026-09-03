# Handoff autosuficiente, N01 v11 final

## Estado

N01 v11 está compuesto, exportado y validado. Las versiones v8, v9 y v10, sus fuentes y sus paquetes permanecen intactos. La revisión vive en la rama `n01-v11-final`.

## Entrega principal

- PDF final: `output/N01-METSI-lectura-previa-v11-final.pdf`
- Fuente editorial: `source/N01_metodologia_sin_recetas-v11.md`
- HTML y CSS editables: `index.html`, `magazine.css`
- Registro de cambios: `CHANGELOG.md`
- QA técnico e integral: `qa-report.json`, `integrity-report.json`
- Hoja de contacto: `qa/N01-contact-sheet.jpg`
- Trazabilidad: `manifest.json`, `source-manifest.json`, `provenance/`

## Reproducción

```bash
python3 build_collection.py --start 1 --end 1
python3 export_pdfs.py 1
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 finalize_and_qa.py 1
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 validate_n01_v11.py
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 render_contact_sheets.py 1
```

La exportación requiere Google Chrome local. La validación integral también usa Poppler para medir la ocupación de cada página.

## Controles cerrados

- Veintinueve páginas A4 y 28 secciones sin títulos huérfanos.
- Último párrafo de la Síntesis completo en la página 27.
- Glosario completo en tres columnas a 9,7 puntos.
- Once URLs exactas, clickeables y con guiones preservados.
- Tapa visualmente idéntica a v10 y metadato superior izquierdo en dos runs ordenados.
- Página 28, sistema visual, citas, revisabilidad, ruta y cierre canónico preservados.
- Ninguna página por debajo del 50 % de ocupación.

## Incertidumbres

No quedan incertidumbres técnicas o editoriales abiertas desde los archivos. La publicación fuera del repositorio local no forma parte de esta pasada.
