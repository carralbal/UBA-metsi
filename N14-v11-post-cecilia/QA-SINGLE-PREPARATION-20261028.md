# N14 · recibo de una sola consigna de preparación · 28/10/2026

La inspección del PDF publicado encontró dos párrafos «Para el encuentro» en p. 44: una consigna general anterior y otra nueva de AS-IS/TO-BE. Esa duplicación podía interpretarse como dos entregas. Se corrigió **directamente la fuente canónica** `N14-v11-post-cecilia/index.html`: el bloque antiguo `N14-s26-b007` ahora explica la comparación con la misma unidad y la prueba adversa; `N14-add-asis-tobe-prep` queda como **única consigna/producto**. No se alteraron las seis preguntas ni el ejemplo resuelto.

## Pruebas antes de promoción

- La fuente conserva **314/314 IDs** únicos, siete hojas CSS directas y los recursos usados; Chrome no informó imágenes faltantes ni bloques ocultos.
- Render, ensamblado con portada pública y acabado a sangre dieron **46/46 A4**. El ensamblador devolvió `PASS_MACHINE_CHECKS_PENDING_VISUAL_REVIEW`, sin páginas blancas eliminadas ni errores de navegación. El árbol de estructura etiquetada siguió presente y el stream de portada es idéntico al del PDF público previo.
- El texto extraíble difiere del PDF previo **sólo en p. 44**. A escala de render de 0,7, la comparación raster de las **46 páginas** detectó diferencia únicamente en p. 44 (promedio 3,775/255); las otras 45 quedaron visualmente idénticas a esa escala. En p. 44 se cuenta una sola aparición de «Para el encuentro,» y cero caracteres fuera de la caja A4 según `pdfplumber`.
- La p. 44 se abrió y revisó a 120 dpi: no hay texto superpuesto, cortado o fuera del panel; se ve una sola consigna destacada. El párrafo explicativo es previo y no pide un segundo producto.
- PDF final SHA-256 **`bcefa2904fefdf85864401726dcb6ffbf66a2a24cfae8511adab1ca9606d1afa`**, 20.568.659 bytes. La ruta pública estable es `site/pdf/publicados/N14-METSI-lectura-previa-v10-final.pdf` y los enlaces de `site/index.html`, atlas, crónicas y `site/course-manifest.json` usan `n14-single-preparation-20261028` (14 apariciones en cuatro archivos). `jq`, `node --check` y `git diff --check` pasaron.

## Límite

Esta es una corrección editorial puntual de la versión digital. No constituye aprobación académica integral, prueba de clase, accesibilidad con lector de pantalla ni preprensa. La comprobación remota de Pages y SHA se registra en el handoff después de desplegar; no se anticipa aquí como realizada.
