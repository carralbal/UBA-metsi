# Handoff autosuficiente, N01 v16 final

## Estado

N01 v16 está compuesto, exportado y validado. El contenido académico y los paquetes v8 a v15 permanecen intactos. La revisión vive en la rama `n01-v16-final`.

## Entrega principal

- PDF final: `output/N01-METSI-lectura-previa-v16-final.pdf`
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
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 validate_n01_v16.py
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 render_contact_sheets.py 1
```

La exportación requiere Google Chrome local. La validación integral usa Poppler, pypdf y pdfplumber para controlar geometría, orden de stream, ocupación, enlaces, viudas y colisiones.

## Controles cerrados

- Veintinueve páginas A4 y 28 secciones con título y cuerpo en la misma página.
- Cero transiciones de cuerpo con restos de una a tres líneas.
- Palabras iniciales `En`, `No` y `La` completas y posteriores a sus títulos en el stream.
- Quince viñetas del glosario separadas al menos 7,47 pt de los corondeles.
- Eyebrow de tapa con contraste 5,41:1 y dos cadenas PDF completas, consecutivas y no entrelazadas.
- Imagen y scrims de tapa extendidos al trim, sin marco ni halo.
- Once URLs exactas y clickeables, con guiones preservados.
- Guarda académica, estructural y visual completa en PASS.

## Incertidumbres

No quedan incertidumbres técnicas o editoriales abiertas desde los archivos. La publicación fuera del repositorio local no forma parte de esta pasada.
