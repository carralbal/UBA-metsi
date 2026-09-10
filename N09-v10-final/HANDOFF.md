# Handoff autosuficiente · N09 v9 final

## Estado

N09 queda compuesto, exportado y auditado como PDF final desde la fuente canónica aprobada. El contenido, la estructura, la accesibilidad, la procedencia de imágenes, los enlaces y la compaginación quedan cerrados técnicamente. La auditoría técnica consolidada de las tapas N00 a N10 cerró con resultado `PASS` para los once documentos, 328 páginas interiores y once conjuntos de URL.

## Entregable principal

`output/N09-METSI-lectura-previa-v9-final.pdf`

- 28 páginas A4.
- 20.792.745 bytes.
- Fecha de modificación: 4 de septiembre de 2026, 07:58:03, hora de Buenos Aires.
- SHA-256: `3cf21741a5b0ca81f924562171e38f45377acc1e4629e069719f8126879167aa`.

## Fuente autoritativa

`source/N09_experiencia_accesibilidad_y_adopcion-content-final.md`

Es byte a byte idéntica a `N09-content-final`, con SHA-256 `8e81a6462d515a955a1575dd36b91a12df500939f871df616934aa32bb018845`. El informe canónico registra 7.912 palabras totales y 6.637 palabras sustantivas desde Tesis hasta Síntesis.

## Qué quedó cerrado

- 324 bloques fuente renderizados una vez y en orden canónico;
- catorce secciones numeradas, catorce referencias y catorce anclajes;
- tapa a sangre con fotografía concebida nativamente en blanco y negro, amplia gama tonal y sombreado localizado;
- eyebrow extraíble como dos cadenas consecutivas;
- Contenido completo y seis referentes distintos con procedencia y derechos documentados;
- página 4 oscura completa, sin borde blanco;
- exactamente dos pausas internas a página completa, en páginas 5 y 15;
- siete activos de ImageGen únicos, con dimensión, huella, descripción y uso efectivo concordantes;
- inventario visual portable consolidado con los diecinueve activos renderizados y las dos fuentes de apoyo de la infografía, todos con huella, origen y derechos o herencia trazable;
- infografía editable del mapa de recorrido accesible integrada una sola vez en la página 18, con ocho campos canónicos;
- cuatro voces distintas de Hotel Horizonte con retratos de tratamiento uniforme;
- cinco píldoras, nueve términos de glosario y seis preguntas de preparación;
- doce URL externas completas, impresas y clicables sólo en Referencias base;
- ninguna página ordinaria por debajo del 55 % de llenado, con mínimo real de 60,05 %;
- Referencias base en dos columnas minimalistas, sin fotografía ni barra ornamental;
- cierre canónico con fósforos, folio, línea de pie, epígrafe y texto alternativo, sin frase grande;
- PDF etiquetado y marcado en `es-AR`, con folio y pie enlazado en sus 28 páginas;
- N08 preservado con SHA-256 `8513d10b826cf9f69d9f8948a941a9013c1c57968bc9a08bfdc9686e8c788f36`.

## Archivos de control

- `validation-v9.json`: gate determinista completo, con todas las rutas internas expresadas de forma relativa al paquete.
- `qa-report.json`: control técnico del PDF.
- `visual-audit.md`: revisión visual página por página y por sistema.
- `qa/N09-contact-sheet.jpg`: vista de las 28 páginas.
- `page-spread-plan.json`: plan exhaustivo de compaginación.
- `assets/image-manifest.json`: inventario de las siete fotografías originales de ImageGen.
- `image-manifest.json`: inventario consolidado de todos los visuales renderizados y sus fuentes de apoyo.
- `image-rights-manifest.json`: identidad, procedencia y derechos de los seis referentes.
- `provenance/accessibility-image-map.md`: bloqueo entre activo, uso y descripción factual.
- `infographic-work-layer/`: SVG editable, raster de revisión, manifiesto semántico, texto alternativo y QA.
- `provenance/regression-lock.json`: huellas y cantidades cerradas.

## Reproducción

Desde la raíz del repositorio:

```bash
python3 build_collection.py --start 9 --end 9
python3 export_pdfs.py 9 9
python3 finalize_and_qa.py 9 9
python3 render_contact_sheets.py 9 9
python3 validate_n09_v9.py --expected-pages 28
```

El último comando debe terminar con código cero y `status: PASS`. El validador es de sólo lectura y no fija el SHA del PDF como condición previa: comprueba las propiedades del artefacto resultante y reporta su huella.

El validador tiene SHA-256 `e1a81a4362834b5d66f64e02cfaafc3159572871dde2f36c81741c316b1e9e56`. Su informe portable tiene SHA-256 `73961ea90ee0357e773047d3ec63d9f44497b1bdef1fcaf734f2aacca5cdb8c8` y no contiene rutas absolutas del entorno de construcción.

## Incertidumbre residual

No queda incertidumbre técnica de contenido, estructura, imágenes, enlaces, accesibilidad, compaginación ni pertenencia de la tapa a la familia N00 a N10. La publicación remota de N09 requiere autorización expresa.
