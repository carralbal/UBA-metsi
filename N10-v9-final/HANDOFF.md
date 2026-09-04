# Handoff autosuficiente · N10 v9 final

## Estado

N10 queda compuesto, exportado y auditado como PDF final desde la fuente canónica aprobada. El contenido, la estructura, la accesibilidad, las imágenes, los enlaces y la compaginación quedan cerrados técnicamente. La auditoría técnica consolidada de las tapas N00 a N10 cerró con resultado `PASS` para los once documentos, 328 páginas interiores y once conjuntos de URL.

## Entregable principal

`output/N10-METSI-lectura-previa-v9-final.pdf`

- 31 páginas A4.
- 21.552.865 bytes.
- Fecha de modificación: 4 de septiembre de 2026, 08:48:04, hora de Buenos Aires.
- SHA-256: `cd5511c6bc9424c51ae2edd72444c0fe908dfa9f82753d29c93b39236a863f89`.

## Fuente autoritativa

`source/N10_construir_el_problema_y_outcomes-content-final.md`

Es byte a byte idéntica a la fuente de `N10-content-final`, con SHA-256 `f272051348f0f2bf459e384cd66d433ae2881ac1d4d1d38200664a4c0e3f29c3`.

## Qué quedó cerrado

- 261 bloques fuente renderizados una vez y en orden canónico;
- quince secciones numeradas con la ruta problema, distinciones, decisiones, prueba, transferencia y preparación;
- tapa a sangre con fotografía concebida nativamente en blanco y negro, amplia gama tonal y sombreado localizado;
- eyebrow extraíble como dos cadenas consecutivas;
- Contenido completo, con fotografía editorial propia y sin activos repetidos;
- seis referentes distintos con procedencia, crédito y derechos documentados;
- exactamente dos pausas internas a página completa, en las páginas 5 y 20;
- cinco fotografías editoriales asignadas una sola vez a Contenido, mecanismos rivales, recorrido, output frente a outcome y prueba reversible;
- banda de Hotel Horizonte con imagen real, texto alternativo exacto y epígrafe visible completo;
- cuatro voces distintas de Hotel Horizonte con retratos uniformes;
- infografía editable de nueve campos, tres bandas y cuatro salidas, integrada una sola vez en la sección 08;
- cinco píldoras, ocho entradas de glosario, seis preguntas y trece referencias ancladas;
- ocho URL externas exactas, impresas y anotadas en Referencias base;
- ninguna página ordinaria por debajo del 55 por ciento de llenado, con mínimo de 0,57 en la página 30;
- Referencias base en dos columnas minimalistas, sin fotografía;
- página 4 con fondo oscuro completo;
- cierre canónico con fósforos, folio, línea de pie, epígrafe, texto alternativo y sin frase grande;
- PDF etiquetado en `es-AR`, con folio y pie enlazado en sus 31 páginas.

## Archivos de control

- `validation-v9.json`: resultado del gate determinista de solo lectura.
- `qa-report.json`: control técnico del PDF.
- `visual-audit.md`: revisión visual completa.
- `qa/N10-contact-sheet.jpg`: vista de las 31 páginas.
- `page-spread-plan.json`: plan exhaustivo de compaginación.
- `image-manifest.json`: inventario portable de 22 activos y fuentes visuales.
- `assets/image-manifest.json`: procedencia, prompts, dimensiones, tonos y huellas de las ocho fotografías ImageGen.
- `image-rights-manifest.json`: derechos y créditos de los seis retratos de referentes.
- `infographic-work-layer/`: fuente editable, manifiesto semántico, texto alternativo y QA de la infografía.
- `provenance/`: notas de procedencia y bloqueo de regresión.

## Reproducción

Desde la raíz del repositorio:

```bash
python3 build_collection.py --start 10 --end 10
python3 export_pdfs.py 10 10
python3 finalize_and_qa.py 10 10
python3 validate_n10_v9.py --expected-pages 31
```

El último comando debe terminar con código cero y `status: PASS`.

## Publicación

El paquete queda preparado localmente. La publicación remota de N10 requiere autorización expresa.

## Incertidumbre residual

No queda incertidumbre técnica de contenido, estructura, imágenes, enlaces, accesibilidad, compaginación ni pertenencia de la tapa a la familia N00 a N10.
