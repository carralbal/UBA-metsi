# Handoff autosuficiente · N06 v9 final

## Estado real

N06 está compuesto desde su contenido canónico, exportado y cerrado técnicamente. La revisión comparada de tapas N00 a N10 ya no está pendiente: la auditoría consolidada del Bloque 01 verificó la familia completa sin modificar el interior.

Este handoff no atribuye una aprobación autoral que no esté documentada. Registra el estado verificable de los archivos.

## Entrega principal

- PDF final: `output/N06-METSI-lectura-previa-v9-final.pdf`.
- PDF bruto reproducible: `output/N06-METSI-lectura-previa-v9.pdf`.
- Páginas: 28, todas A4.
- Tamaño exacto: 19.518.092 bytes.
- Fecha de modificación: 2026-09-04 08:58:06, hora de Buenos Aires.
- SHA-256 del PDF final: `c05782e7ad61b544994032c4eb6a740ff52ab34573b9a45d36960f5dd03bfd6a`.

## Fuente y tapa vigentes

- Fuente empaquetada: `source/N06_discovery_como_reduccion_de_incertidumbre-content-final.md`.
- Fuente canónica: `../N06-content-final/source/N06_discovery_como_reduccion_de_incertidumbre-content-final.md`.
- SHA-256 de la fuente: `837172826ad62ec7d7b841208202f91adbadf73d5286387fdf304c636b10e9fd`.
- Maestro de tapa vigente: `assets/cover-source-premium-bw-v1.png`.
- Archivo desplegado: `assets/cover.png`.
- SHA-256 de ambos archivos de tapa: `0780b6f86663444d876fb56f3d880b3a7256a44809e9ee569b10087603aa1fd0`.
- Procedencia vigente: `provenance/cover-image-premium-bw-v1.md`.

La tapa v1 es un activo original generado para METSI y concebido en blanco y negro. La escena profesional está situada en Argentina, conserva una escala tonal amplia y no usa filtros globales de contraste, brillo, `grayscale()` o desaturación. El oscurecimiento es localizado para sostener la legibilidad.

## Contenido y composición cerrados

- Contenido canónico preservado sin pérdidas ni duplicados.
- 348 bloques fuente renderizados exactamente una vez.
- Índice completo, ruta monótona y seis referentes distintos.
- Diez referencias ancladas y cinco URLs externas completas y clicables.
- Cinco píldoras, nueve entradas de glosario y seis preguntas de preparación.
- Nota `SIN NUM.` contenida en la columna izquierda de Contenido, sin invadir el epígrafe ni el pie.
- Pregunta profesional oscura en la página 4 y dos pausas fotográficas internas a sangre en las páginas 5 y 13.
- Referencias base en dos columnas minimalistas, sin barra lateral ni fotografía ornamental.
- Cierre canónico con fósforos a sangre, folio, línea de pie, epígrafe y texto alternativo, sin frase superpuesta.

## Verificación final

- Validador individual: `validation-v9.json`, estado `PASS`, 40 de 40 controles.
- QA técnico: `qa-report.json`, PDF etiquetado, marcado y con idioma `es-AR`.
- Cero títulos o subtítulos huérfanos en 52 controles.
- Ninguna página ordinaria por debajo del umbral editorial; mínimo registrado: 65,87 %.
- Páginas 2 a 28 idénticas píxel por píxel a la línea de base bloqueada.
- Auditoría de tapas: `../BLOCK-01-cover-final/audit.json`, estado global `PASS`, 11 de 11 documentos, 328 páginas interiores idénticas y 11 de 11 conjuntos de URLs preservados.
- En N06, la tapa llega a sangre, no presenta halo perimetral, conserva una escala amplia de grises y su figura semántica contiene el texto alternativo exacto.
- La segunda construcción preserva HTML, CSS, manifiestos, texto extraído, enlaces y 28 páginas rasterizadas; el identificador binario interno del PDF puede variar sin alterar contenido o apariencia.

## Archivos de control

- `validation-v9.json`
- `qa-report.json`
- `integrity-report.json`
- `visual-audit.md`
- `qa/N06-contact-sheet.jpg`
- `page-spread-plan.json`
- `provenance/cover-image-premium-bw-v1.md`
- `provenance/editorial-image-provenance.md`
- `provenance/referent-portrait-sources.md`
- `provenance/regression-lock.json`

## Reproducción

Desde la raíz del repositorio:

```bash
python3 build_collection.py --start 6 --end 6
python3 export_pdfs.py 6
python3 finalize_and_qa.py 6
python3 validate_n06_v9.py
```

## Incertidumbre residual

No quedan incertidumbres técnicas abiertas desde los archivos. Cualquier aprobación o cambio autoral posterior debe quedar documentado de forma explícita y limitarse al punto solicitado.
