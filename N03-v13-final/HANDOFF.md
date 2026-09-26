# Handoff autosuficiente · N03 v9 final

## Estado real

N03 está compuesto desde su contenido canónico, exportado y cerrado técnicamente. El PDF final es un artefacto generado desde la fuente editable, no una copia renombrada. La auditoría consolidada de tapas del Bloque 01 lo verificó dentro de la familia N00 a N10 sin modificar el interior.

Este handoff no atribuye una aprobación autoral que no esté documentada. Registra el estado verificable de los archivos.

## Entrega principal

- PDF final: `output/N03-METSI-lectura-previa-v9-final.pdf`
- PDF bruto reproducible: `output/N03-METSI-lectura-previa-v9.pdf`
- Páginas: 30, todas A4.
- Tamaño exacto: 15.142.425 bytes.
- Fecha de modificación: 2026-09-04 07:57:42, hora de Buenos Aires.
- SHA-256 del PDF final: `08154728ce84f956c88f65a46d08018fda8ec933ca820380f9fb1166cc3512ef`.

## Fuente y tapa vigentes

- Fuente empaquetada: `source/N03_fronteras_retroalimentacion_y_efectos-content-final.md`.
- Fuente canónica: `../N03-content-final/source/N03_fronteras_retroalimentacion_y_efectos-content-final.md`.
- SHA-256 de la fuente: `6930c5a6cf7c98ad2f60ebf662334a7f491827260e460c939c51b7c9acef6854`.
- Maestro de tapa: `assets/cover-source-premium-bw-v3.png`.
- Archivo desplegado: `assets/cover.png`.
- SHA-256 de ambos archivos de tapa: `06976e01da816e65e8becdc825c62bd6b166e90654f23b74f9cd2b900cb0be94`.
- Procedencia: `provenance/cover-image-premium-bw-v3.md`.

La tapa v3 es un activo original generado para METSI y concebido en blanco y negro. La composición usa oscurecimiento localizado detrás de los textos, sin conversión monocromática por CSS.

## Contenido y composición cerrados

- 11 secciones numeradas y Referencias base como aparato `SIN NUM.`.
- Tres movimientos: delimitar el recorte, observar el retorno de los efectos y decidir cuándo revisar la frontera.
- Entrada desde N02, continuidad HH-03 en los tres movimientos y salida explícita hacia N04.
- 9.034 palabras canónicas y 7.631 sustantivas entre Tesis y Síntesis.
- 320 bloques fuente renderizados exactamente una vez.
- 11 referencias ancladas y siete URLs externas completas y clicables.
- Cinco píldoras, 13 términos de glosario y seis preguntas de preparación.
- Pregunta profesional oscura en la página 4 y dos pausas fotográficas internas a sangre en las páginas 5 y 19.
- Cuatro voces distintas de Hotel Horizonte, con retratos del mismo tamaño.
- Cierre canónico con fósforos a sangre, folio, línea de pie, epígrafe y texto alternativo, sin frase superpuesta.

## Verificación final

- Validador individual: `validation-v9.json`, estado `PASS`, 31 de 31 controles.
- QA técnico: `qa-report.json`, PDF etiquetado, marcado y con idioma `es-AR`.
- Cero títulos o subtítulos huérfanos en 64 controles.
- Ninguna página ordinaria por debajo del 50 % de llenado; mínimo registrado: 51,65 %.
- Las páginas 2 a 30 son idénticas píxel por píxel a la línea de base bloqueada.
- Auditoría de tapas: `../BLOCK-01-cover-final/audit.json`, estado global `PASS`, 11 de 11 documentos, 328 páginas interiores idénticas y 11 de 11 conjuntos de URLs preservados.
- En N03, la tapa llega a sangre, no presenta halo perimetral, conserva una escala amplia de grises y su figura semántica contiene el texto alternativo exacto.

## Archivos de control

- `validation-v9.json`
- `qa-report.json`
- `integrity-report.json`
- `visual-audit.md`
- `qa/N03-contact-sheet.jpg`
- `provenance/cover-change-regression.json`
- `provenance/version-v9-regression.json`
- `provenance/regression-lock.json`

## Reproducción

Desde la raíz del repositorio:

```bash
python3 build_collection.py --start 3 --end 3
python3 export_pdfs.py 3
python3 finalize_and_qa.py 3
python3 validate_n03_v9.py
python3 render_contact_sheets.py 3
```

## Incertidumbre residual

No quedan incertidumbres técnicas abiertas desde los archivos. Cualquier aprobación o cambio autoral posterior debe quedar documentado de forma explícita y limitarse al punto solicitado.
