# Handoff autosuficiente, N02 v12

## Estado

N02 v12 está compuesto, exportado y validado como candidato de revisión. No se declara cerrado hasta recibir aprobación explícita. N00, N01 y N02 v8 a v11 permanecen preservados.

## Entrega principal

- PDF: `output/N02-METSI-lectura-previa-v12-final.pdf`
- Fuente: `source/N02_el_sistema_no_cabe_en_una_aplicacion-v12.md`
- Editables: `index.html`, `magazine.css`, `diagrams/N02-mapa-decision.svg`
- Informe: `INFORME-CORRECCION-v12.md`
- QA: `qa-report.json`, `integrity-report.json`, `qa/N02-contact-sheet.jpg`, `visual-audit.md`
- Validador: `../validate_n02_v12.py`

## Reproducción

```bash
python3 build_collection.py --start 2 --end 2
python3 export_pdfs.py 2
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 finalize_and_qa.py 2 2
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 validate_n02_v12.py
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 render_contact_sheets.py 2
```

## Decisiones y cambios

- Se eligió la salida A. Comprobación es ahora la sección 17, PRUEBA; el caso de medicación es la sección 18, TRANSFERENCIA.
- El índice refleja el nuevo orden. La ruta completa es monotónica y no reaparece ninguna etiqueta cerrada.
- Píldoras, glosario y preguntas son bloques de lista protegidos frente a cortes de página.
- El glosario completo queda en la página 24. La página 25 abre con la sección 22, sin entrada huérfana.
- Las preguntas usan flujo de dos columnas determinado por el contenido. El espacio libre entre preguntas es uniforme, 15,04 puntos.

## Controles cerrados

- PDF A4 de 27 páginas, 22 secciones y 27 folios con pie enlazado.
- Diferencia textual exacta contra v11: sólo se intercambiaron dos bloques completos. El inventario de 7.701 palabras es idéntico.
- Cambios visuales limitados a las páginas 2 y 22 a 25. La tapa y las otras 22 páginas son idénticas a v11.
- Glosario: 387 caracteres en negrita de 8,8 puntos en p24 y cero en p25.
- No hay títulos huérfanos. La única continuación de párrafo queda entre p6 y p7 con ocho líneas en p7.
- Se conservan seis preguntas, la consigna de entrega, el registro impersonal, las tres capitulares eliminadas y el eyebrow accesible.
- Las 17 referencias continúan ancladas y las 15 URLs permanecen íntegras, visibles y clickeables.
- Estructura de listas idéntica a v11 y guarda de 53 viñetas preservada, sin colisiones.
- Ninguna página queda por debajo del 50 % de ocupación medido.

## Identidad del artefacto

- SHA256: `f71e9af144610cc12cd30b2c52f99437a58e35dc08d5564f9bb7da1e291b6cb0`
- Tamaño: 28.141.291 bytes.
- Modificación: 2026-09-02 20:57:35 -03.
- Es un archivo nuevo generado desde la fuente v12, no una copia renombrada de v11.

## Incertidumbre

No quedan incertidumbres técnicas abiertas. La decisión pendiente es editorial: aprobar N02 v12 o devolver observaciones puntuales.
