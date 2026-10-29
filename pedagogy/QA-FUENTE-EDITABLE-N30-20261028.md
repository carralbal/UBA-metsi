# N30 · fuente editable recuperada, sin duplicar el PDF final

## Qué se preservó

La fuente del interior aceptado v27 (HTML, cuatro hojas de estilo locales y los
recursos que no coincidían con el paquete anterior) se incorporó a
`N30-v27-recovered-source/`. `scripts/materialize_n30_recovered_source_20261028.py`
documenta la procedencia del checkout histórico. De los 23 recursos de imagen o
diagrama citados por el HTML, 21 son byte idénticos a `N30-v14-editorial` y se
reutilizan; sólo se copiaron el retrato Bunge y el mapa actualizado. Se añadió
un SVG citado por CSS. No se copió otra vez el PDF público ni las fotografías
que ya estaban en Git.

El HTML conserva el campo `data-cover-sha256` del recurso de portada original
como dato de procedencia, aunque para vista local `data-cover-pdf` y el objeto
apuntan al PDF público completo. No usar aquel hash como comprobación del PDF
público actual; el SHA correcto figura abajo.

`scripts/verify_n30_recovered_source_20261028.mjs` abrió el HTML en Chrome:
324/324 bloques de fuente, 23 imágenes cargadas, cinco estilos cargados y
cero solicitudes fallidas. La portada de lectura enlaza al PDF público estable
como recurso de referencia, sin crear un segundo PDF.

## Límite explícito

El PDF digital final de N30 es el archivo canónico de 39 A4 en
`site/pdf/publicados/N30-METSI-lectura-previa-v10-final.pdf`, SHA-256
`3fd62b76ae56949e28b089c6b728094cef6e24b4eebed00e83b3a2a6fe9685db`.
El HTML recuperado v27 es una **fuente del interior**, no un generador
autónomo byte-exacto del PDF final: el ensamblaje v28 agregó portada,
etiquetado y pp. 26–27, y luego se normalizó la p. 3 de Referentes. El recibo
histórico `pedagogy/N30/QA-CANDIDATA-DIGITAL-v28-Y-PUBLICACION-PENDIENTE-20261023.md`
describe esa cadena, pero su estado de publicación/LFS es obsoleto. No
recompilar N30 desde este HTML y sobrescribir el PDF público sin reconstruir y
verificar la cadena completa. No se modificó el PDF final en este corte.

## Reproducción exacta del arte digital desde Git

El commit `a04f8e2ce7849f4d7647a2f1f01a9a1fed354ced` conserva como blob Git
normal el PDF v28 de 39 páginas, SHA-256
`a838b7b1f85b77bde2127a9b1fd5d0d219d4f5d6fc8be2b1521564c3f5a0cc22`.
`scripts/rebuild_n30_from_git_history_20261028.py` lo extrae sólo a un
directorio temporal, aplica la normalización aprobada de p. 3 con
`scripts/normalize_n30_n31_referentes_20261028.py` y exige el SHA final del
PDF canónico. Si coincide, la cadena **PDF v28 → PDF final** es reproducible
byte por byte sin depender del checkout histórico ni guardar copias privadas.

Esto no convierte el HTML interior v27 en ensamblador autónomo de la v28. La
fuente semántica y editorial queda preservada, y el arte final queda
reconstruible desde Git; cerrar además la cadena HTML → v28 exigiría portar el
ensamblador histórico de portada/etiquetado y contrastar toda su salida.
