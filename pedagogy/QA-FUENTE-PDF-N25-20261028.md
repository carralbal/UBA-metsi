# N25 · reproducción exacta de la edición digital sin HTML nuevo

## Resultado

N25 no tiene un HTML único aceptado que recomponga fielmente sus 33 páginas;
las reconstrucciones v2–v5 se descartaron. Su **fuente real es una cadena de
operaciones PDF-level** sobre el PDF de 33 páginas anterior, más tres capas
tipográficas de 16–19 KB.

`scripts/rebuild_n25_from_git_history_20261028.py` reconstruyó esa cadena en
un directorio temporal que se elimina automáticamente:

1. PDF original del objeto histórico Git LFS SHA-256
   `5994f0f2465c5f39582723ef4b74cf2531000fe2b25e8b3e87291d974c526518`
   (puntero en el commit anterior a `310a557`; objeto local validado: 9.203.022
   bytes).
2. Desaturación de las fotos de pp. 7 y 18, sin reescribir sus JPEG; barra
   volt recolocada en p. 18.
3. Capas editoriales originales para pp. 9, 20 y 28, conservadas en
   `N25-pdf-source/overlays/` (53.714 bytes en total).
4. PDF v7 resultante, SHA-256
   `19cd382b9ea34ef09878dbc0e4ccfa4502740e809e524b9015df360e8adeb241`,
   idéntico al documento aceptado/publicado el 24/10.
5. Normalización de p. 3 con el script ya publicado
   `scripts/normalize_n22_n23_n25_referentes_20261028.py`.

**Salida exacta:** 33 A4, SHA-256
`8b3380ea04f9ac019157cbe9e5677343860a87a7b87a9423c107061bd9b1232e`,
idéntica byte por byte al PDF canónico actual
`site/pdf/publicados/N25-METSI-lectura-previa-v10-final.pdf`. El reconstruido
pasó los controles de texto, anotaciones, estructura, geometría y streams de
las páginas ajenas a p. 3 definidos en la normalización. **No se conservó
ninguna copia privada de libro** después de esta prueba.

## Dependencia y límite

El PDF original existe como objeto LFS en el Git histórico y estaba en la
caché local en la prueba. Una clonación nueva necesita acceso a ese objeto
LFS; la cuota LFS actual puede impedir recuperarlo desde cero. La receta y
las tres capas pequeñas sí están en Git normal. No se debe sustituir el PDF
final desde HTML v2–v5 ni tratar la receta como autorización para imprenta.
La inspección editorial y estructural original está registrada en
`work/UBA-metsi-publication/pedagogy/N25/QA-DIGITAL-v7-20261024.md`; su SHA
final anterior a la normalización está actualizado arriba.
