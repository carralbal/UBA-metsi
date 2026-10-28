# N30 y N31 · cotejo post-Cecilia y corrección editorial directa

Fecha: 28/10/2026. Alcance: edición digital para lectura; **no** certificación académica integral ni preprensa.

| N | PDF canónico de ruta estable | Páginas | SHA previo | SHA corregido local |
| --- | --- | ---: | --- | --- |
| N30 | `site/pdf/publicados/N30-METSI-lectura-previa-v10-final.pdf` | 39 | `a838b7b1f85b77bde2127a9b1fd5d0d219d4f5d6fc8be2b1521564c3f5a0cc22` | `3fd62b76ae56949e28b089c6b728094cef6e24b4eebed00e83b3a2a6fe9685db` |
| N31 | `site/pdf/publicados/N31-METSI-lectura-previa-v10-final.pdf` | 39 | `f9a63e6b9f062ab568611de3cc5ba38589d1a524ef936acfe3f0b357f74dcb01` | `3e9405de8a713052d06103d94adfe54541c4de5edc1b8180542495f91a2cb408` |

Los SHA previos corresponden a los recibos históricos `work/UBA-metsi-publication/pedagogy/N30/PUBLICACION-DIGITAL-v28-20261023.md` y `N31/QA-DIGITAL-v5c-20261024.md`. La fuente fiel N31 está en `output/source-recovery-20261020/N31-art-v5/working/N31/`, cuyo QA documenta 247/247 bloques conservados. La fuente exacta del acabado N30 v28 sigue por identificar; no usar una versión de trabajo más antigua sin cotejo.

## Revisión metodológica focal

- **N30:** lectura de pp. 17–18, 23–25, 34 y 36–37. El ejercicio separa 4/100 observaciones, 4/5 del límite piloto y 4 veces la tasa objetivo; no mezcla las poblaciones. HH-30 enlaza doce componentes desde promesa y población hasta SLI/SLO, presupuesto, señales, alerta, respuesta, reparación y evaluación del aprendizaje. Distingue síntoma de causa, y «alerta recibida» de «servicio reparado». La preparación pide **un** mapa de promesa con señal, autoridad, primera acción y evidencia posterior. Se reabrieron visualmente pp. 23–24: los aparentes espacios faltantes en títulos de la extracción textual son artefactos de esa extracción, no fallas tipográficas visibles. La infografía p. 24 sigue íntegra.
- **N31:** se conserva el cotejo focal de pp. 27, 35 y 37 registrado en el inventario. La ficha de mejora distingue consulta/propuesta/modificación autorizada, compara IA con alternativa realista y cuenta preparación/revisión/reparación/mantenimiento. La idea ADLC y especificaciones para agentes puede usarse como práctica emergente a evaluar, no como ciclo universal. No se añadió una consigna de más.

## Correcciones exactas en los PDF finales

- **Ambos N:** en p. 3 «Referentes» se anuló sólo una operación de relleno gris heredado, no semántica, para obtener el `paper` uniforme del estándar N21. En N30 la operación pintaba `[0,2246,794,1123]`; en N31 `[0,2336,794,1123]`. No se alteraron textos ni anotaciones.
- **N31 retrato:** `revision-local.css` de la fuente fiel tenía `transform:scale(2.7)!important` y `object-position:100% 50%` para Mario Bunge, creando un recorte borroso de los ojos. El JPG fuente N31 es **byte idéntico** al de N28 (SHA `433a305d568566455ea922b51521279c2cbb4529c70e368d77f6e7545b185e25`). Se reemplazó únicamente el flujo de píxeles del XObject N31 Mario por el XObject N28 ya publicado, de igual 366×367 RGB/Flate, manteniendo la máscara circular original de N31 y todas las marcas de accesibilidad. La p. 3 final se renderizó y abrió grande: aparece el rostro completo y legible, con los otros cinco retratos/textos intactos. El override CSS adjunto impide el zoom al regenerar.
- Script reproducible con guardas de SHA, objeto, dimensiones, conteo, texto, anotaciones, geometría y flujos de otras 38 páginas: `scripts/normalize_n30_n31_referentes_20261028.py`. `pdfinfo`/estructura etiquetada y página visual verificadas localmente. No se generó ni conservó PDF candidato privado. Los PNG efímeros de QA se retirarán al verificar publicación remota.

Se mantiene la ruta pública; se actualizaron las claves de caché `n30-editorial-20261028` y `n31-editorial-20261028` en portada, atlas, crónicas y manifiesto del checkout. **No atribuir publicación efectiva a GitHub Pages hasta recibir éxito del run y comprobar SHA remoto 37/37.**

## Límites

La corrección directa del PDF es deliberadamente mínima y auditable, pero no equivale a regenerar las 39 páginas desde una fuente única. La fuente histórica N31 no se editó en su checkout para preservar cambios preexistentes; se registró un override CSS. Quedan pendientes consolidación de fuentes, prueba de carga/tiempo en clase, lectura docente completa, lector de pantalla humano y preprensa. La imagen de N31 ya se usa en otra lectura pública; no se añadió fotografía nueva.
