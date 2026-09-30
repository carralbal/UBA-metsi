# Recuperación editorial de las lecturas N01–N36

Estado: recuperación editorial instalada localmente y validada para publicación.

## Cierre de la serie recuperada

Se recompusieron los interiores de N01–N36 con la redacción clara aprobada y
la arquitectura visual de revista: aperturas oscuras, fotografía editorial,
casos, infografías, cambios de retícula y cierres diferenciados. Se conservaron
**exactamente las 36 tapas aprobadas**: el primer folio de cada PDF nuevo se
copió del PDF público anterior y una comparación raster confirmó igualdad en
los 36 casos. No se rediseñó ni sustituyó ninguna tapa.

La auditoría de contenido encontró cero comienzos o finales de bloques fuente
faltantes; la de geometría no detectó texto superpuesto ni fuera de página. El
control de enlaces y tamaño del sitio pasó en una copia limpia del paquete. Los
PDF reemplazados y sus SHA-256 figuran en `install-receipt.json`; el estado
anterior se conserva en el commit `7551d2ce` y en la etiqueta
`pre-editorial-recovery-20260929`. La fuente canónica de la prosa sigue en
`pedagogy/plain-language-edition/`; la recuperación visual se reproduce con
`scripts/prepare_editorial_recovery.py`, `render_editorial_recovery.mjs`,
`lock_editorial_recovery_covers.py` y `recovery.css`. El HTML intermedio tiene
una tapa obsoleta y **nunca** debe publicarse directamente: el bloqueo de tapa
es obligatorio. Las notas de avance siguientes documentan las pruebas previas
al cierre; sus estados «sin publicar» son históricos.

## Corrección de regresión de tapas

Las tres primeras pruebas compartidas eran inválidas: el HTML de la edición de
lectura clara conservaba fotografías de tapa anteriores a las portadas aprobadas
y la recuperación de CSS las volvió a mostrar. N25 permitió confirmar un cambio
real de foto, encuadre y diagramación, no un mero efecto de paginación.

La tapa publicada de cada N es ahora una entrada inmutable del ensamblado de
prueba. El render del HTML se guarda como `interior-stage.pdf`, nunca como PDF
presentable; `scripts/lock_editorial_recovery_covers.py` incorpora la primera
página exacta del PDF público correspondiente y conserva del render sólo las
páginas interiores. Se regeneraron los 36 PDF de prueba desde cero y se repitió
el ensamblado. `scripts/verify_editorial_cover_lock.py` rasteriza la
primera página de ambos PDF a la misma resolución y exige igualdad binaria de
la imagen resultante. Las 36 comparaciones pasaron; el informe está en
`approved-cover-verification.json`. Se sustituyeron las pruebas N03, N12 y N25
que tenían tapas incorrectas. La tapa aprobada todavía debe quedar representada
en la fuente editorial editable antes de una publicación definitiva; el bloqueo
por página PDF protege las pruebas actuales, pero no sustituye esa tarea. Nada
de esto aprueba todavía sus páginas interiores ni modifica el sitio público.

## Avance del 29 de septiembre

Se recompusieron copias locales de N01–N36 con la redacción clara actual y la
gramática magazine: clases editoriales por sección, fotos de apertura y pausas,
referentes, familias de infografías y composición diferenciada. La causa de la
pérdida de diseño quedó localizada en el generador de la edición llana y su CSS,
no en la calidad del texto nuevo.

El primer control automatizado confirma que los 36 documentos abren, sus imágenes
cargan y sus bloques de contenido son visibles. Se corrigieron desbordes de
preguntas y glosarios, referencias huérfanas y varios párrafos aislados en N03,
N10, N12, N14, N17, N18 y N29. Hay tres PDF de revisión en `previews/` (N03,
N12 y N25). La auditoría de densidad sigue señalando páginas que requieren
criterio visual; no se aprueba la publicación por una métrica automática.

No se reemplazaron los PDF del sitio ni se cambió ningún video. Antes de publicar
faltan la revisión visual final de la colección, la confirmación de integridad de
las frases fragmentadas por saltos de página y un respaldo de la edición pública.

### Control posterior de la maqueta (29 de septiembre, segunda pasada)

La serie de 36 candidatos volvió a renderizarse tras las correcciones locales.
La comparación del primer folio con cada PDF público pasó en los 36 casos:
ninguna tapa de la prueba cambia respecto de la publicada. La auditoría textual
de todos los candidatos registra **cero comienzos y cero finales de bloques
fuente faltantes**. Se generó además una hoja de contacto de todas las páginas
de cada N para la revisión visual.

Se corrigieron continuaciones casi vacías en N02, N07, N10, N11, N20, N26,
N31 y N32; se reunieron los doce campos de los instrumentos HH-29 y HH-33; se
recompusieron las páginas de cinco ideas en N12, N23, N24, N26 y N27; y se
eliminaron hojas aisladas de traspaso en N34–N36. N15 recibió una pausa
tipográfica deliberada en lugar de una página con sólo dos párrafos pequeños.

Estas pruebas **todavía no están aprobadas ni publicadas**. Queda la revisión
manual final de todas las hojas de contacto y de las páginas individuales que
la auditoría de densidad marca como sospechosas, además de contrastar el ritmo
visual con la edición previa a la reescritura. No debe hacerse la sustitución
en `site/pdf` antes de cerrar ese control.

### Tercera pasada de composición y control

La serie de prueba reúne 1180 páginas, 430 páginas con imagen y 912 objetos de
imagen. La edición pública posterior a la simplificación tenía 342 páginas con
imagen y 687 objetos; la referencia anterior a esa simplificación tenía 441 y
937, respectivamente. La recuperación visual es sustancial, aunque la mera
cantidad no sustituye el juicio editorial.

Se eliminaron continuaciones huérfanas o fragmentadas en N10, N11, N15, N32,
N34, N35 y N36. Los doce campos de HH-34 y HH-36 ya están reunidos en páginas
completas; el mismo tratamiento se había aplicado a HH-29 y HH-33. En N32 y
N36 se recuperó la página fotográfica que había quedado desplazada detrás de
dos párrafos solos. N15 y N35 ahora separan caso, contraejemplo y prueba como
artículos legibles, sin reducir la redacción.

El control automático de geometría de los 36 candidatos no encontró glifos
fuera de página ni superposiciones de texto. El control de integridad textual
continúa en cero bloques fuente con inicio o final faltante. Las 36 tapas se
compararon de nuevo con las publicadas y permanecen idénticas. Siguen en
revisión las páginas de baja ocupación que pueden ser pausas legítimas o cortes
de paginación; el informe de triage está en `geometry-audit.json`. La colección
no se ha reemplazado ni publicado.

## Hallazgo

La pérdida de la estética de revista no es un efecto secundario menor de la nueva paginación. El proceso que incorporó la redacción más clara desactivó deliberadamente parte del sistema editorial:

- `scripts/build_plain_language_release.py` reemplazó las clases de composición por `reading-section edition-section` y asignó `two-column` a casi todas las secciones.
- El mismo proceso quitó la clase `document-nXX` del cuerpo, por lo que dejaron de aplicarse reglas específicas de cada documento en `magazine.css`.
- `pedagogy/plain-language-edition/edition.css` impuso fondo neutro, flujo continuo y dos columnas sobre las secciones, además de ocultar elementos y composiciones anteriores.
- Para N11–N36 se desactivaron cierres editoriales de movimientos y tratamientos de infografías mediante conjuntos vacíos en el generador.

El texto más comprensible debe conservarse. La recuperación tiene que modificar composición y paginación, no volver a la prosa anterior.

## Comparación de los 36 PDF

Referencia: edición en el commit `859e7e4`, anterior a la reescritura pedagógica. Se comparó con la versión PDF pública actual. El inventario de imágenes cuenta páginas que contienen al menos una imagen raster y objetos de imagen PDF; no mide por sí solo calidad, pertinencia ni tamaño visual.

| N | Páginas antes → ahora | Páginas con imagen antes → ahora | Objetos de imagen antes → ahora |
|---|---:|---:|---:|
| 01 | 37 → 35 | 12 → 9 | 22 → 14 |
| 02 | 36 → 34 | 11 → 9 | 19 → 17 |
| 03 | 35 → 32 | 7 → 6 | 15 → 14 |
| 04 | 39 → 34 | 8 → 7 | 16 → 15 |
| 05 | 33 → 30 | 8 → 7 | 13 → 12 |
| 06 | 31 → 33 | 6 → 5 | 11 → 10 |
| 07 | 37 → 36 | 9 → 9 | 18 → 17 |
| 08 | 33 → 33 | 9 → 9 | 19 → 18 |
| 09 | 35 → 34 | 9 → 9 | 18 → 17 |
| 10 | 37 → 37 | 11 → 10 | 19 → 18 |
| 11 | 42 → 41 | 20 → 11 | 50 → 21 |
| 12 | 38 → 39 | 20 → 11 | 50 → 21 |
| 13 | 28 → 36 | 11 → 10 | 21 → 20 |
| 14 | 41 → 41 | 20 → 11 | 50 → 21 |
| 15 | 37 → 38 | 19 → 10 | 49 → 20 |
| 16 | 31 → 37 | 12 → 11 | 22 → 21 |
| 17 | 34 → 41 | 14 → 11 | 29 → 21 |
| 18 | 29 → 38 | 12 → 11 | 23 → 22 |
| 19 | 29 → 38 | 12 → 11 | 23 → 22 |
| 20 | 33 → 38 | 13 → 10 | 29 → 21 |
| 21 | 33 → 39 | 13 → 10 | 28 → 20 |
| 22 | 34 → 36 | 13 → 10 | 29 → 21 |
| 23 | 35 → 32 | 13 → 9 | 28 → 19 |
| 24 | 29 → 34 | 12 → 10 | 22 → 20 |
| 25 | 25 → 32 | 12 → 11 | 23 → 22 |
| 26 | 26 → 36 | 12 → 11 | 23 → 22 |
| 27 | 28 → 35 | 11 → 10 | 22 → 21 |
| 28 | 29 → 36 | 11 → 10 | 22 → 21 |
| 29 | 33 → 38 | 13 → 10 | 29 → 21 |
| 30 | 29 → 38 | 11 → 10 | 22 → 21 |
| 31 | 32 → 36 | 12 → 8 | 28 → 18 |
| 32 | 33 → 37 | 12 → 8 | 28 → 18 |
| 33 | 33 → 37 | 13 → 8 | 29 → 18 |
| 34 | 33 → 34 | 14 → 10 | 30 → 21 |
| 35 | 31 → 35 | 13 → 10 | 29 → 21 |
| 36 | 30 → 37 | 13 → 10 | 29 → 21 |
| **Total** | **1188 → 1297** | **441 → 342** | **937 → 687** |

El resultado tiene 109 páginas más y 99 páginas con imágenes menos. La mayor caída visual se concentra en N11, N12, N14 y N15 (nueve páginas con imagen menos en cada uno), pero el cambio estructural de estilos afecta la colección completa.

## Prueba controlada con N25

Se generó una copia local con la redacción actual y el CSS magazine anterior. Volvieron de inmediato la apertura negra, la pausa a sangre y las composiciones diferenciadas. Pasó de 32 a 28 páginas y recuperó el mismo número de páginas con imágenes y objetos de imagen que la edición anterior (12 y 23). Los 286 bloques `data-source-id` del HTML se encontraron completos en el texto extraído del PDF de prueba; la diferencia en el conteo bruto de palabras proviene, al menos en parte, del material repetido por las distintas paginaciones. Sin embargo, el contacto visual muestra espacios excesivos heredados de reglas pensadas para la longitud anterior. Este experimento confirma la causa, no constituye todavía una corrección publicable.

## Criterio de recuperación

1. Conservar los textos actuales, tapas, referentes y decisiones visuales aprobadas.
2. Recuperar las clases y familias editoriales por sección, sin imponer dos columnas universalmente.
3. Restaurar las pausas, cierres, infografías e imágenes cuya función seguía vigente; verificar que no se pierda ningún bloque de texto.
4. Rehacer el plan de páginas y dobles páginas para la longitud nueva, evitando tanto el texto continuo como los vacíos accidentales.
5. Revisar cada PDF página por página, con controles de sangrado, superposición, corte de párrafos, legibilidad e integridad textual, antes de sustituir la versión pública.

No se deben publicar los PDF restaurados sólo por superar una comparación de cantidad de imágenes o páginas.
