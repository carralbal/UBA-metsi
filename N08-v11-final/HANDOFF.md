# Handoff autosuficiente · N08 v9 final

## Estado

N08 queda compuesto, exportado y auditado como PDF final desde la fuente canónica aprobada. El contenido, la estructura, la accesibilidad, los enlaces y la compaginación quedan cerrados técnicamente. La auditoría técnica consolidada de las tapas N00 a N10 cerró con resultado `PASS` para los once documentos, 328 páginas interiores y once conjuntos de URL.

## Entregable principal

`output/N08-METSI-lectura-previa-v9-final.pdf`

- 28 páginas A4.
- 19.397.092 bytes.
- Fecha de modificación: 4 de septiembre de 2026, 07:57:59, hora de Buenos Aires.
- SHA-256: `8513d10b826cf9f69d9f8948a941a9013c1c57968bc9a08bfdc9686e8c788f36`.

## Fuente autoritativa

`source/N08_observar_el_trabajo_invisible-content-final.md`

Es byte a byte idéntica a `N08-content-final`, con SHA-256 `328d2858fbe170bee35f17ada425fdb78b0e34a395bc4992ed33fb5b2910b8b9`.

## Qué quedó cerrado

- 256 bloques fuente renderizados una vez y en orden canónico;
- tapa a sangre con fotografía concebida nativamente en blanco y negro, amplia gama tonal y sombreado localizado;
- eyebrow extraíble como dos cadenas consecutivas;
- índice completo y seis referentes distintos con procedencia y derechos documentados;
- exactamente dos pausas internas a página completa, en páginas 5 y 17;
- infografía editable de siete capas integrada en la sección 06;
- instrumento de observación conservado junto con su título, introducción y tabla;
- fotografía de aplicación con rostros completos, epígrafe unido y encuadre editorial;
- cuatro voces distintas de Hotel Horizonte con retratos iguales en tamaño;
- glosario repartido en once y cinco entradas completas, sin entrada aislada;
- doce referencias ancladas y seis URL externas completas, impresas y clicables;
- ninguna página ordinaria por debajo del 55 por ciento de llenado;
- Referencias base en dos columnas minimalistas, sin fotografía ni barra ornamental;
- cierre canónico con fósforos, folio, línea de pie, epígrafe, texto alternativo y sin frase grande;
- PDF etiquetado en `es-AR`, con folio y pie enlazado en sus 28 páginas;
- N07 preservado con SHA-256 `c7b36bffcd3da4d1955f3563f7836dc9fad28d5cb0fa5ed7129bba1f2b075bd9`.
- segunda construcción con HTML, CSS, manifiesto fuente y plancha de contacto idénticos a la primera; la marca temporal interna explica la variación binaria del PDF.

## Archivos de control

- `validation-v9.json`: síntesis del gate determinista.
- `qa-report.json`: control técnico del PDF.
- `visual-audit.md`: revisión visual completa.
- `qa/N08-contact-sheet.jpg`: vista de las 28 páginas.
- `page-spread-plan.json`: plan exhaustivo de compaginación.
- `image-manifest.json`: inventario portable de 21 activos.
- `infographic-work-layer/`: fuente editable, manifiesto semántico, alt y QA.
- `provenance/`: procedencia y bloqueo de regresión.

## Reproducción

Desde la raíz del repositorio:

```bash
python3 build_collection.py --start 8 --end 8
python3 export_pdfs.py 8 8
python3 finalize_and_qa.py 8 8
python3 validate_n08_v9.py --expected-pages 28
```

El último comando debe terminar con código cero y `status: PASS`.

## Incertidumbre residual

No queda incertidumbre técnica de contenido, estructura, imágenes, enlaces, accesibilidad, compaginación ni pertenencia de la tapa a la familia N00 a N10. La publicación remota de N08 requiere autorización expresa.
