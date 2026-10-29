# METSI · legibilidad de Referentes N11/N21 · 28/10/2026

## Hallazgo

La auditoría de tamaño de lectura sobre los 37 PDF finales detectó dos páginas 3
de Referentes sensiblemente menores que la colección: N11 7,3 pt y N21 6,7 pt
como tamaño dominante. No afectaba el cuerpo principal (N21 11,5 pt), pero sí
la lectura de estos seis perfiles en A4. El fondo paper ya estaba normalizado.

## Corrección digital

Se recompuso únicamente la página 3 de cada documento, conservando los seis
retratos, títulos de obra, descripciones y frase de cierre. N11 pasa a 8,2 pt
dominantes y N21 a 8,5 pt dominantes. Los textos pequeños de crédito/metadata
permanecen más discretos. No se agregó ni se eliminó contenido académico.

| Lectura | Antes | Después | Páginas | Streams de otras páginas idénticos | Anotaciones antes/después |
|---|---|---|---:|---:|---:|
| N11 | `ffee9ee8ce8594cf4ab3b231e814c441562106a6d15aab44da300ea45cef12df` | `b74576021042f09a1588dd8d5b37443e4617f1f258da7ca04e84e1c152c1c5f4` | 47 | 46/46 | 178/178 |
| N21 | `fb21c41abcffb3e1fe4bb0a16b25f81ec8139141e73e61208e3b7c9a0ae68e45` | `3d44889f4717d6f54e5ea56248ab8f16b5356e2926145764972a324b23cc77bc` | 40 | 39/39 | 79/79 |

Las dos páginas finales se renderizaron a 1200 px y se inspeccionaron enteras.
No hay corte, superposición ni texto fuera de hoja; ambos PDF conservan
`/StructTreeRoot`, etiquetas, idioma `es-AR` y la cantidad de anotaciones.
N11 tiene igual secuencia MCID y exactamente los mismos caracteres no blancos.
N21 conserva los primeros 44 marcadores de contenido en orden; la fuente
Chromium añade un marcador final no estructural fuera del área visible. El
folio vectorial del PDF publicado se trasplantó sin cambiar su texto.

## Fuente y publicación

N21: CSS editado en `N21-v11-referentes-neutral/edition.css` y proceso con
guardas de SHA/texto/MCID en `scripts/render_n21_readable_referents_20261028.mjs`
 y `scripts/replace_n21_referents_page_20261028.py`. N11: fuente fiel v76
recuperada y **consolidada en este Git** como `N11-v76-recovered-final/index.html`
(384/384 bloques), override de estilo
`pedagogy/source-overrides/referentes-legibles-n11-20261028.css`, y proceso
con guardas equivalente en los scripts `render_n11...` y `replace_n11...`.
La consolidación incluye las 48 hojas CSS necesarias, reutiliza 15 recursos
idénticos ya presentes en `N11-v13-editorial` y añade sólo ocho imágenes
faltantes (~1,4 MB). La fuente consolidada cargó 384 bloques, seis perfiles y
cero imágenes faltantes; volvió a renderizar **47 páginas A4**. Su página 3
y la página 3 del PDF final dan **los mismos píxeles** a 1200 px. Esto verifica
la fidelidad de esa página; no afirma que un render completo futuro sea byte
idéntico a todo el PDF ya publicado, porque hubo intervenciones PDF-level.
Los PDF finales se instalaron en sus rutas públicas estables y las referencias
del sitio llevan una nueva revisión de caché. Sólo Git normal, no LFS.

La aceptación de pantalla no equivale a prueba humana con lector de pantalla
ni habilitación para imprenta. Los PNG/PDF intermedios en `/private/tmp` se
eliminan después de verificar el despliegue; no se conserva una rama de
"copias privadas" de estos documentos.
