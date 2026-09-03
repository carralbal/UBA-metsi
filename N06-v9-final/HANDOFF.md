# Handoff autosuficiente · N06 v9 final

## Estado

N06 queda compuesto, exportado y auditado como PDF final candidato desde su contenido canónico aprobado. El contenido, los enlaces, la estructura, la accesibilidad y la compaginación quedan cerrados técnicamente. La comparación autoral de las diez tapas N01 a N10 permanece como una revisión visual conjunta posterior y no habilita cambios en el cuerpo.

## Entregable principal

`output/N06-METSI-lectura-previa-v9-final.pdf`

- 28 páginas A4.
- 20.392.785 bytes.
- Fecha de modificación: 03 de septiembre de 2026, 20:46:22, hora de Buenos Aires.
- SHA-256: `7cd9de77fdb634f90f8f47a083a2f9e77cadc042621ae01b7b9f5fae09df7955`.

## Fuente autoritativa

`source/N06_discovery_como_reduccion_de_incertidumbre-content-final.md`

Es byte a byte idéntica a la fuente de `N06-content-final`, con SHA-256 `837172826ad62ec7d7b841208202f91adbadf73d5286387fdf304c636b10e9fd`.

## Qué quedó cerrado

- contenido canónico preservado sin pérdidas ni duplicados;
- tapa a sangre con fotografía concebida nativamente en blanco y negro, rango tonal amplio y overlay extendido hasta los cuatro bordes, sin costura inferior;
- eyebrow extraíble como `LECTURA PREVIA` y `EDICIÓN 2026`;
- índice completo y seis referentes distintos;
- nota `SIN NUM.` contenida en la columna izquierda de Contenido, sin invadir el epígrafe fotográfico ni el pie;
- exactamente dos pausas internas a página completa, en las páginas 5 y 13;
- primera pausa inmediatamente después de la página 4;
- 348 bloques fuente renderizados una vez;
- 10 referencias ancladas y 5 URL externas completas y clicables;
- 5 píldoras, 9 entradas de glosario y 6 preguntas de preparación;
- ningún título o subtítulo huérfano;
- ninguna página ordinaria por debajo del umbral editorial, con mínimo medido de 65,87 %;
- Referencias base en dos columnas minimalistas, sin barra lateral ni fotografía ornamental;
- cierre canónico con fósforos, folio, línea de pie, epígrafe, texto alternativo y sin frase agregada;
- PDF etiquetado con idioma `es-AR`.
- segunda construcción con HTML, CSS, manifiestos, texto extraído, enlaces y 28 páginas rasterizadas idénticos a la primera; el identificador binario interno del PDF puede variar entre exportaciones sin alterar contenido ni apariencia.

## Archivos de control

- `validation-v9.json`: auditoría determinista integral.
- `qa-report.json`: control técnico del PDF.
- `visual-audit.md`: auditoría visual final.
- `qa/N06-contact-sheet.jpg`: vista completa del documento.
- `page-spread-plan.json`: ubicación de aparatos, pausas y cierre.
- `provenance/`: procedencia de tapa, imágenes, retratos y bloqueo de regresión.

## Cómo reproducir y verificar

Desde la raíz del repositorio:

```bash
python3 build_collection.py --start 6 --end 6
python3 export_pdfs.py 6 6
python3 finalize_and_qa.py 6
python3 validate_n06_v9.py
```

El último comando debe terminar con código cero y `status: PASS`.

## Incertidumbre residual

No queda una incertidumbre de contenido, estructura, enlaces, accesibilidad o compaginación. Sólo queda abierta la decisión autoral comparada sobre el tono de las tapas N00 a N10. Hasta esa revisión, esta tapa se conserva como candidato funcional y no se modifica por separado.
