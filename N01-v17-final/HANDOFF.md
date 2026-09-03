# Handoff autosuficiente, N01 v17 final

## Estado

N01 v17 está compuesto, exportado y validado. Sólo cambia la construcción del scrim superior de tapa y el reflujo necesario para eliminar la viuda de la página 11. El contenido académico, la estructura, los recursos y los paquetes v8 a v16 permanecen intactos. La revisión vive en la rama `n01-v17-final`.

## Entrega principal

- PDF final: `output/N01-METSI-lectura-previa-v17-final.pdf`
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
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 validate_n01_v17.py
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 render_contact_sheets.py 1
```

La exportación requiere Google Chrome local. La validación integral usa Poppler, pypdf y pdfplumber para controlar geometría, orden de stream, ocupación, enlaces, viudas y colisiones.

## Cambios cerrados

- Tapa: el scrim superior llega de lado a lado y mantiene el desvanecimiento vertical. En la franja despejada superior, el salto máximo entre píxeles contiguos bajó de 7 en v16 a 3 en v17. En la antigua coordenada de costura, los saltos medidos son 0, 0, 1 y 0.
- Contraste: eyebrow 5,33:1, por encima de 4,5:1. El logotipo permanece legible sobre un único campo continuo. Kicker, título, cita, círculo, folio y pie no cambiaron.
- Página 10: termina después de “desplaza riesgo”, sin dos líneas sueltas del párrafo siguiente.
- Página 11: “Estas distinciones…” aparece completo en cuatro líneas antes de la Sección 08.
- Página 12: “Un ejemplo completo…” y su primer párrafo aparecen juntos; no se generó una viuda secundaria.

## Controles de regresión

- Veintinueve páginas A4 y 28 secciones con título y cuerpo en la misma página.
- Cero párrafos fuente divididos entre páginas.
- Fuente académica byte por byte idéntica e inventario PDF de 9091 palabras idéntico a v16.
- Once URLs exactas y clickeables, con guiones preservados.
- Quince entradas del glosario a 9,7 pt; viñetas separadas 7,47 pt de los corondeles.
- Todas las páginas superan la mitad del campo útil. Mínimo: 52,9 %.
- Página de cierre, fósforos, folio, pie, leyenda y texto alternativo preservados.

## Archivo final

- Tamaño: 24834084 bytes.
- Fecha de modificación: 2026-09-02 09:54:36 -0300.
- SHA256: `53c47d6f481cf473b4dbdbae3098540f062e4267fb0a3d1927fd2a34816803c2`.
- No es una copia renombrada de v16: v16 mide 24827706 bytes y tiene SHA256 `c7f0508bb9f7f152a2637412c7b8e3f164f367b88aae1c81f484d02756d44855`.

## Incertidumbres

No quedan incertidumbres técnicas o editoriales abiertas desde los archivos. La publicación fuera del repositorio local no forma parte de esta pasada.
