# Handoff autosuficiente · N05 v9 final

## Estado real

N05 está compuesto desde su contenido canónico, exportado y cerrado técnicamente. La auditoría consolidada de tapas del Bloque 01 lo verificó dentro de la familia N00 a N10 sin modificar el interior.

Este handoff no atribuye una aprobación autoral que no esté documentada. Registra el estado verificable de los archivos.

## Entrega principal

- PDF final: `output/N05-METSI-lectura-previa-v9-final.pdf`.
- PDF bruto reproducible: `output/N05-METSI-lectura-previa-v9.pdf`.
- Páginas: 28, todas A4.
- Tamaño exacto: 15.880.141 bytes.
- Fecha de modificación: 2026-09-04 07:57:49, hora de Buenos Aires.
- SHA-256 del PDF final: `cf6088c205637cf3cfb2902e5f5804c880f6f1c9509317df4b8d3b2334ccc516`.

## Fuente y tapa vigentes

- Fuente empaquetada: `source/N05_actores_afectados_poder_y_perspectivas-content-final.md`.
- Fuente canónica: `../N05-content-final/source/N05_actores_afectados_poder_y_perspectivas-content-final.md`.
- SHA-256 de la fuente: `46a9ecb180b96c6ff71790750e3e6d606ef7c0a1f061a0682ad29ad99dfcbf2b`.
- Maestro de tapa vigente: `assets/cover-source-premium-bw-v2.png`.
- Archivo desplegado: `assets/cover.png`.
- SHA-256 de ambos archivos de tapa: `0054cb5c5a9547134d476ff6bb02dd1d31e6757caa2fbcd32c77d648a180ccb8`.
- Procedencia vigente: `provenance/cover-image-premium-bw-v2.md`.

La tapa v2 es un activo original generado para METSI y concebido en blanco y negro. Representa a cuatro profesionales argentinos y latinoamericanos alrededor de una silla vacía. La composición usa un gradiente oscuro localizado en la base, sin velo global ni conversión monocromática por CSS.

## Contenido y composición cerrados

- 11 secciones numeradas, Referentes y Referencias base como aparatos `SIN NUM.`.
- Ruta de lectura monótona y continuidad explícita entre N04, N05 y N06.
- HH-05 como hilo conductor.
- 279 bloques fuente renderizados exactamente una vez.
- Diez referencias ancladas y ocho URLs externas completas y clicables.
- Seis referentes con retratos distintos y cajas visuales uniformes.
- Mapa Actor, Decisión, Consecuencia editable y auditado.
- Cinco píldoras, glosario de 17 entradas y seis preguntas de preparación.
- Pregunta profesional oscura en la página 4 y dos pausas fotográficas internas a sangre en las páginas 5 y 19.
- Cierre canónico con fósforos a sangre, folio, línea de pie, epígrafe y texto alternativo, sin frase superpuesta.

## Verificación final

- Validador individual: `validation-v9.json`, estado `PASS`, 32 de 32 controles.
- QA técnico: `qa-report.json`, PDF etiquetado, marcado y con idioma `es-AR`.
- Cero títulos o subtítulos huérfanos en 52 controles.
- Ninguna página ordinaria por debajo del 50 % de llenado; mínimo registrado: 50,16 %.
- Páginas 2 a 28 idénticas píxel por píxel a la línea de base bloqueada.
- Auditoría de tapas: `../BLOCK-01-cover-final/audit.json`, estado global `PASS`, 11 de 11 documentos, 328 páginas interiores idénticas y 11 de 11 conjuntos de URLs preservados.
- En N05, la tapa llega a sangre, no presenta halo perimetral, conserva una escala amplia de grises y su figura semántica contiene el texto alternativo exacto.

## Archivos de control

- `validation-v9.json`
- `qa-report.json`
- `integrity-report.json`
- `visual-audit.md`
- `qa/N05-contact-sheet.jpg`
- `page-spread-plan.json`
- `provenance/cover-image-premium-bw-v2.md`
- `provenance/editorial-image-provenance.md`
- `provenance/referent-portrait-sources.md`
- `provenance/regression-lock.json`

## Reproducción

Desde la raíz del repositorio:

```bash
python3 build_collection.py --start 5 --end 5
python3 export_pdfs.py 5
python3 finalize_and_qa.py 5
python3 validate_n05_v9.py
```

## Incertidumbre residual

No quedan incertidumbres técnicas abiertas desde los archivos. Cualquier aprobación o cambio autoral posterior debe quedar documentado de forma explícita y limitarse al punto solicitado.
