# N32 y N33 · cotejo post-Cecilia y corrección editorial directa

Fecha: 28/10/2026. Alcance: edición digital para lectura; **no** certificación académica integral, accesibilidad humana ni preprensa.

| N | PDF canónico de ruta estable | Páginas | SHA anterior | SHA corregido local |
| --- | --- | ---: | --- | --- |
| N32 | `site/pdf/publicados/N32-METSI-lectura-previa-v10-final.pdf` | 43 | `9ee583076e157ad9a7e9d4aeed1c9c49ab14011fefbc67807f417ceed6eddb93` | `8b25e4892dae856eb6fa117264b804db375a6dba8eae99deeb50e9d33e793dc7` |
| N33 | `site/pdf/publicados/N33-METSI-lectura-previa-v10-final.pdf` | 40 | `6aeeaaae976191b39a3b5b0266f88ec386906d0a32d25abb7a783bf1483e67f3` | `342fa85bd06b7820f28fe3918914cac0386fc85ed731fbb062e021e5de170073` |

## Fuente fiel y revisión focal

- **N32**: `work/UBA-metsi-publication/output/source-recovery-20261020/N32-art-v2-working/N32/`; QA histórico `pedagogy/N32/QA-DIGITAL-v2c-20261024.md` documenta 266/266 bloques fuente conservados, 43/43 páginas visuales, 34 destinos, 57 enlaces internos y 90 URI. Cotejo focal de pp. 24,27,39,41: una prueba sobre 100 casos detecta 90 correctos y 10 erróneos; la revisión humana corrige ocho errores pero altera dos aciertos, por lo que quedan 96 correctos y 4 erróneos, con 200 minutos de revisión. Los denominadores se mantienen claros; HH-32 pide evidencia de caso normal, difícil y variante. La mención de «Moral Crumple Zones» de p. 24 es enlace integrado en la fuente, no fragmento perdido. Una frase repetida en p. 27 funciona como cita destacada. No se agregó otra consigna.
- **N33**: `work/UBA-metsi-publication/output/source-recovery-20261020/N33-art-v3-working/N33/`; QA histórico `pedagogy/N33/QA-DIGITAL-v3b-20261024.md` documenta 257/257 bloques, 40/40 páginas visuales, 34 destinos, 60 enlaces internos y 96 URI. Cotejo focal de pp. 27,36,38: inventario de doce campos para operación, cambio y retiro, con responsable, umbral, evidencia y reversión. La preparación conserva un solo producto. No se encontró motivo para ampliar contenido.

## Corrección exacta sobre los PDF finales

En ambos documentos, p. 3 «Referentes» tenía una franja gris heredada. Se anuló únicamente la operación de relleno del rectángulo `[0,2336,794,1123]`, sin cambiar textos, retratos restantes, enlaces ni la página completa. En las fuentes fieles, `revision-local.css` imponía a Mario Bunge `transform:scale(2.7)!important` y `object-position:100% 50%`, dejando apenas los ojos, borrosos. El JPG fuente de N32/N33 es idéntico al de N28 (SHA `433a305d568566455ea922b51521279c2cbb4529c70e368d77f6e7545b185e25`). Se sustituyeron sólo los píxeles del XObject Mario `/X64` usando el encuadre ya publicado en N28: N32 conserva 366×367 RGB/Flate; N33 se remuestreó a sus dimensiones originales 321×319 con Lanczos. Se preservó la máscara circular original de cada PDF.

`scripts/normalize_n32_n33_referentes_20261028.py` exige SHA previo y estructura esperada; verificó texto, anotaciones y geometría en **43/43** y **40/40**, streams de todas las otras páginas idénticos y árbol de estructura etiquetada. Las dos p. 3 se renderizaron a 1800 px y se abrieron: fondo `paper` uniforme, rostro completo, otros cinco retratos y pies íntegros. El delta reproducible de fuente está en `pedagogy/source-overrides/referentes-paper-n32-n33.css`; no se editó el checkout histórico con trabajo preexistente. No se creó ni conservó PDF candidato privado.

Se mantiene la ruta pública estable y se cambian las claves de caché a `n32-editorial-20261028` y `n33-editorial-20261028` en portada, atlas, crónicas y manifiesto. **Publicación remota y SHA se documentarán sólo después de Pages.**

## Límites

El cambio directo y localizado no equivale a regeneración integral desde una fuente única. Faltan cotejo docente completo, ensayo de carga y clase, prueba humana de lector de pantalla, verificación de imágenes/derechos y preprensa; esta revisión focal no constituye aprobación académica definitiva.
