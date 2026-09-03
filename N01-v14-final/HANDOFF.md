# Handoff autosuficiente, N01 v14 final

## Estado

N01 v14 está compuesto, exportado y validado. Las versiones v8 a v13, sus fuentes y sus paquetes permanecen intactos. La revisión vive en la rama `n01-v14-final`.

## Entrega principal

- PDF final: `output/N01-METSI-lectura-previa-v14-final.pdf`
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
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 validate_n01_v14.py
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 render_contact_sheets.py 1
```

La exportación requiere Google Chrome local. La validación integral usa Poppler para medir ocupación, controlar la tapa y comparar las 29 páginas contra v13. También compara el campo visual de la tapa contra v12.

## Controles cerrados

- Veintinueve páginas A4 y 28 secciones sin títulos huérfanos.
- Eyebrow de tapa codificado como dos cadenas PDF completas y consecutivas, una por línea, con tracking tipográfico.
- Densidad de tapa idéntica a v12 en el campo original y fondo extendido hasta el trim box sin modificar la composición.
- Once URLs exactas, clickeables y con guiones preservados.
- Las páginas 2 a 29 son píxel por píxel idénticas a v13.
- Los tres ajustes ya aprobados de v12 permanecen intactos.

## Incertidumbres

No quedan incertidumbres técnicas o editoriales abiertas desde los archivos. La publicación fuera del repositorio local no forma parte de esta pasada.
