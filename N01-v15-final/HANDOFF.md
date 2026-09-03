# Handoff autosuficiente, N01 v15 final

## Estado

N01 v15 está compuesto, exportado y validado. Las versiones v8 a v14, sus fuentes y sus paquetes permanecen intactos. La revisión vive en la rama `n01-v15-final`.

## Entrega principal

- PDF final: `output/N01-METSI-lectura-previa-v15-final.pdf`
- Fuente editorial sin cambios: `source/N01_metodologia_sin_recetas-v12.md`
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
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 validate_n01_v15.py
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 render_contact_sheets.py 1
```

La exportación requiere Google Chrome local. La validación integral usa Poppler para medir ocupación, controlar la continuidad del scrim y comparar las 29 páginas contra v14.

## Controles cerrados

- Veintinueve páginas A4 y 28 secciones sin títulos huérfanos.
- Eyebrow de tapa codificado como dos cadenas PDF completas y consecutivas, una por línea, con tracking tipográfico.
- Scrim de tapa continuo hasta el borde inferior, sin franja repetida ni salto claro.
- Once URLs exactas, clickeables y con guiones preservados.
- Las páginas 2 a 29 son píxel por píxel idénticas a v14.
- Los tres ajustes ya aprobados de v12 permanecen intactos.

## Incertidumbres

No quedan incertidumbres técnicas o editoriales abiertas desde los archivos. La publicación fuera del repositorio local no forma parte de esta pasada.
