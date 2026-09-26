# Handoff autosuficiente · N04 v9 final

## Estado real

N04 está compuesto desde su contenido canónico, exportado y cerrado técnicamente. La única diferencia visual contra N04 v8 está en la portada. Las páginas 2 a 32 permanecen idénticas píxel por píxel a la línea de base.

Este handoff no atribuye una aprobación autoral que no esté documentada. Registra el estado verificable de los archivos.

## Entrega principal

- PDF final: `output/N04-METSI-lectura-previa-v9-final.pdf`.
- PDF bruto reproducible: `output/N04-METSI-lectura-previa-v9.pdf`.
- Páginas: 32, todas A4.
- Tamaño exacto: 27.477.637 bytes.
- Fecha de modificación: 2026-09-04 09:13:43, hora de Buenos Aires.
- SHA-256 del PDF final: `b6b4df7df6c92e4ed76cce15d89a0802f9c7c0b6529f16ed8cdeef1b9af23ccb`.

## Fuente y tapa vigentes

- Fuente empaquetada: `source/N04_hechos_sintomas_relatos_hipotesis_y_decisiones-content-final.md`.
- Fuente canónica: `../N04-content-final/source/N04_hechos_sintomas_relatos_hipotesis_y_decisiones-content-final.md`.
- SHA-256 de la fuente: `4e86351bcd6865c81bbdb8a5e72352e55042b5d9e16f71949737c610e6d13320`.
- Maestro de tapa vigente: `assets/cover-source-premium-bw-v3.png`.
- Archivo desplegado: `assets/cover.png`.
- SHA-256 de ambos archivos de tapa: `ac947baf49208e1eba7c1d5842c88e27e5761b2d0be86a8f7660a1afd7532925`.
- Procedencia vigente: `provenance/cover-image-premium-bw-v3.md`.

La v3 es una derivación tonal reproducible de `assets/cover-source-premium-bw-v2.png`, fotografía original concebida en blanco y negro. Sólo abre luminancia y contraste del mismo raster. No recorta, reencuadra, escala, agrega, elimina ni desplaza elementos, y no depende de conversión monocromática por CSS.

## Contenido y composición cerrados

- 11 secciones numeradas, Referentes y Referencias base como aparatos `SIN NUM.`.
- Ruta monótona con continuidad explícita entre N03, N04 y N05.
- HH-04 como hilo conductor y cuatro voces de Hotel Horizonte con retratos distintos.
- 437 bloques fuente renderizados exactamente una vez.
- Diez referencias ancladas y ocho URLs externas completas y clicables.
- Cinco píldoras, glosario de 16 entradas y seis preguntas de preparación.
- Pregunta profesional oscura en la página 4 y dos pausas fotográficas internas a sangre en las páginas 5 y 22.
- Cierre canónico con fósforos a sangre, folio, línea de pie, epígrafe y texto alternativo, sin frase superpuesta.

## Verificación final

- Validador individual: `validation-v9.json`, estado `PASS`, 32 de 32 controles.
- QA técnico: `qa-report.json`, PDF etiquetado, marcado y con idioma `es-AR`.
- Cero títulos o subtítulos huérfanos en 79 controles.
- Ninguna página ordinaria por debajo del 50 % de llenado; mínimo registrado: 50,26 %.
- Páginas 2 a 32 idénticas píxel por píxel a N04 v8.
- Auditoría de tapas: `../BLOCK-01-cover-final/audit.json`, estado global `PASS`, 11 de 11 documentos, 328 páginas interiores idénticas y 11 de 11 conjuntos de URLs preservados.
- En N04, la tapa llega a sangre, no presenta halo perimetral, conserva una escala amplia de grises y su figura semántica contiene el texto alternativo exacto.

## Archivos de control

- `validation-v9.json`
- `qa-report.json`
- `integrity-report.json`
- `visual-audit.md`
- `qa/N04-contact-sheet.jpg`
- `qa/N04-cover-v9.png`
- `page-spread-plan.json`
- `provenance/cover-image-premium-bw-v3.md`
- `provenance/cover-regression-v8-v9.json`
- `provenance/regression-lock.json`

## Reproducción

Desde la raíz del repositorio:

```bash
python3 build_collection.py --start 4 --end 4
python3 export_pdfs.py 4
python3 finalize_and_qa.py 4
python3 validate_n04_v9.py
```

## Incertidumbre residual

No quedan incertidumbres técnicas abiertas desde los archivos. Cualquier aprobación o cambio autoral posterior debe quedar documentado de forma explícita y limitarse al punto solicitado.
