# Handoff autosuficiente · N04 v9 final

## Estado

N04 queda compuesto, exportado y auditado como PDF final candidato. La única diferencia visual contra N04 v8 está en la portada: se sustituyó la fotografía concebida en color por una fotografía nueva concebida desde el inicio en blanco y negro. El resultado usa el contenido canónico aprobado y no modifica N00, N01, N02 ni N03.

## Entregable principal

`output/N04-METSI-lectura-previa-v9-final.pdf`

- 32 páginas A4.
- 28.938.926 bytes al ejecutar la validación final.
- SHA-256: `b3f9d19b25589cba735adcc2d1ec611218e50af54cae5075c71294b8003a58e7`.

## Fuente autoritativa

`source/N04_hechos_sintomas_relatos_hipotesis_y_decisiones-content-final.md`

Es byte a byte idéntica a la fuente de `N04-content-final`, con SHA-256 `4e86351bcd6865c81bbdb8a5e72352e55042b5d9e16f71949737c610e6d13320`.

## Qué quedó cerrado

- tapa fotográfica premium, cinematográfica, con representación argentina o latinoamericana y concebida nativamente en blanco y negro;
- archivo fuente de tapa nuevo, sin reutilización ni edición de la imagen v8;
- regla CSS de N04 sin `grayscale()` ni `saturate(0)`, porque la monocromía pertenece al original fotográfico;
- eyebrow en dos cadenas legibles: `LECTURA PREVIA` y `EDICIÓN 2026`;
- índice completo y ordenado;
- seis referentes con identidades y obras diferenciadas;
- once secciones, ruta monótona y continuidad N03, N04 y N05;
- HH-04 como hilo conductor y cuatro voces de Hotel Horizonte con retratos distintos;
- dos pausas a página completa, en páginas 5 y 22;
- 437 bloques fuente renderizados una vez, sin pérdidas ni duplicados;
- diez referencias ancladas y ocho URL externas completas y clicables;
- glosario de 16 entradas, cinco píldoras y seis preguntas;
- ninguna página ordinaria por debajo del 50 %;
- cierre con fósforos, folio, línea de pie, epígrafe y texto alternativo.
- auditoría determinista final: 31 controles aprobados sobre 31.

## Archivos de control

- `validation-v9.json`: auditoría determinista integral.
- `qa-report.json`: control técnico del PDF.
- `visual-audit.md`: auditoría visual de 39 sobre 40.
- `qa/N04-contact-sheet.jpg`: vista completa de las 32 páginas.
- `qa/N04-cover-v9.png`: tapa renderizada.
- `page-spread-plan.json`: plan de páginas.
- `provenance/cover-image-premium-bw-v2.md`: prompt, criterio y procedencia de tapa.
- `provenance/cover-regression-v8-v9.json`: comparación raster que prueba que sólo cambió la tapa.
- `provenance/regression-lock.json`: valores que no deben cambiar en una ronda posterior.

## Cómo reproducir y verificar

Desde la raíz del repositorio:

```bash
python3 build_collection.py --start 4 --end 4
python3 export_pdfs.py 4
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 finalize_and_qa.py 4
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 validate_n04_v9.py
```

El último comando debe terminar con código cero y `status: PASS`. La comparación raster contra v8 debe arrojar una diferencia visible en la página 1 y diferencia absoluta media cero en las páginas 2 a 32.

## Incertidumbre residual

No queda una incertidumbre técnica o editorial abierta desde los archivos. La aprobación autoral final del PDF continúa siendo una decisión del autor; cualquier cambio posterior debe tratar esta versión como línea de base y limitarse al punto solicitado.
