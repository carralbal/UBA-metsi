# Handoff autosuficiente · N05 v9 final

## Estado

N05 queda compuesto, exportado, auditado y aprobado por el autor como PDF final. Usa el contenido canónico aprobado y no modifica N00, N01, N02, N03 ni N04.

## Entregable principal

`output/N05-METSI-lectura-previa-v9-final.pdf`

- 28 páginas A4.
- 15.201.083 bytes.
- Fecha de modificación: 3 de septiembre de 2026, 16:40:42, hora de Buenos Aires.
- SHA-256: `3b507eea1ddc0c7981ea90747039c1137a0149d233accb2d40ae86184b64d34f`.

## Fuente autoritativa

`source/N05_actores_afectados_poder_y_perspectivas-content-final.md`

Es byte a byte idéntica a la fuente de `N05-content-final`, con SHA-256 `46a9ecb180b96c6ff71790750e3e6d606ef7c0a1f061a0682ad29ad99dfcbf2b`.

## Qué quedó cerrado

- tapa fotográfica premium, cinematográfica y concebida nativamente en blanco y negro;
- composición a sangre, sin halo ni margen blanco;
- eyebrow en dos cadenas legibles: `LECTURA PREVIA` y `EDICIÓN 2026`;
- índice completo y ordenado;
- seis referentes con retratos distintos y cajas visuales idénticas de 25 mm por 25 mm;
- once secciones y ruta de lectura monótona;
- continuidad explícita N04, N05 y N06, con HH-05 como hilo conductor;
- mapa Actor, Decisión, Consecuencia editable y auditado;
- exactamente dos pausas visuales internas a página completa, en las páginas 5 y 19;
- 279 bloques fuente renderizados una vez, sin pérdidas ni duplicados;
- diez referencias ancladas y ocho URL externas completas y clicables;
- cinco píldoras, glosario de 17 entradas y seis preguntas de preparación;
- ningún título o subtítulo huérfano;
- ninguna página ordinaria por debajo del 50 % de llenado; mínimo: 50,16 % en Referencias base;
- cierre con fósforos, folio, línea de pie, epígrafe, texto alternativo y sin frase agregada;
- PDF etiquetado con idioma `es-AR`.

## Archivos de control

- `validation-v9.json`: auditoría determinista integral.
- `qa-report.json`: control técnico del PDF.
- `visual-audit.md`: auditoría visual final.
- `qa/N05-contact-sheet.jpg`: vista completa de las 28 páginas.
- `page-spread-plan.json`: plan y ubicación de aparatos, secciones y pausas.
- `provenance/cover-image-premium-bw-v1.md`: procedencia y dirección de tapa.
- `provenance/editorial-image-provenance.md`: trazabilidad de fotografías internas.
- `provenance/referent-portrait-sources.md`: procedencia de los seis retratos.
- `provenance/regression-lock.json`: valores que no deben cambiar en rondas posteriores.

## Cómo reproducir y verificar

Desde la raíz del repositorio:

```bash
python3 build_collection.py --start 5 --end 5
python3 export_pdfs.py 5
python3 finalize_and_qa.py 5
python3 validate_n05_v9.py
```

El último comando debe terminar con código cero y `status: PASS`.

## Incertidumbre residual

No queda una incertidumbre técnica, editorial ni autoral abierta sobre N05. La futura revisión comparada de tapas N00 a N10 podrá proponer un cambio exclusivo de cubierta. Hasta entonces, esta versión es la línea de base cerrada y ningún otro elemento puede modificarse.
