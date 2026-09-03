# Handoff autosuficiente, N02 v13

## Estado

N02 v13 está compuesto, exportado y validado como candidato de revisión. La corrección se limitó a la compaginación de las páginas 24 y 25. No se modificó ninguna palabra de la fuente v12.

## Entrega principal

- PDF: `output/N02-METSI-lectura-previa-v13-final.pdf`
- Fuente: `source/N02_el_sistema_no_cabe_en_una_aplicacion-v13.md`
- Editables: `index.html`, `magazine.css`, `diagrams/N02-mapa-decision.svg`
- Informe: `INFORME-CORRECCION-v13.md`
- QA: `qa-report.json`, `integrity-report.json`, `qa/N02-contact-sheet.jpg`, `visual-audit.md`
- Validador: `../validate_n02_v13.py`

## Reproducción

```bash
python3 build_collection.py --start 2 --end 2
python3 export_pdfs.py 2 2
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 finalize_and_qa.py 2 2
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 validate_n02_v13.py
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 render_contact_sheets.py 2
```

## Decisión de maqueta

- Se usaron las dos palancas solicitadas.
- El generador divide las 19 entradas del glosario después de la entrada 13. Las seis entradas finales pasan completas a la página 25 y se componen en tres columnas.
- Las preguntas siguen en dos columnas y su margen entre ítems pasa a 13 mm. La separación visible medida es 38,14; 37,46; 38,14 y 37,46 puntos.
- La sección de preguntas deja de imponer una altura mínima. El panel gris termina 12,72 puntos después de la consigna.

## Controles cerrados

- Página 24: 92,54 % de llenado. Página 25: 74,15 %. Ninguna página baja del 50 % de ocupación rasterizada.
- La fuente v13 es byte a byte idéntica a v12. Ambas tienen SHA256 `71ff4a73dd4dc64c7e27b2c0a4410cba0926cf1588e63d588663ea087d9141a6`.
- El inventario de palabras extraído del PDF es idéntico. La similitud secuencial es 0,998708; la única permutación proviene del nuevo flujo visual en tres columnas.
- Cambios visuales detectados exclusivamente en las páginas 24 y 25.
- Se conservan 27 páginas A4, 22 secciones, 53 viñetas, seis preguntas, 17 referencias ancladas y 15 URLs externas íntegras.
- La ruta, el índice, la tapa, el eyebrow accesible, las capitulares eliminadas, las viudas controladas, los folios, los pies y el cierre permanecen intactos.

## Identidad del artefacto

- SHA256 PDF: `9c2698a1bd611cd7e51447f67c172ae5983f24ea0b3b40efcf9882bb4494386a`
- Tamaño: 28.141.675 bytes.
- Modificación: 2026-09-02 22:37:25 -03.
- Es un PDF nuevo generado desde la fuente y no una copia renombrada de v12.

## Incertidumbre

No quedan incertidumbres técnicas abiertas. La aprobación editorial de v13 corresponde al autor.
