# N10 · corrección editorial de legibilidad · 28/10/2026

## Alcance exacto

Sólo se amplió el cuerpo de la historia de apertura de **página física 6**, de
9,5 pt efectivos (redondeo a medio punto) a 10,5 pt, ajustando la fuente CSS
editable `N10-v12-post-cecilia/N10/private-n10-art-v2.css` a 10,8 pt antes
del factor de render. No se cambió texto, orden, caso ni capacidad curricular.
N21 sigue siendo mayor (11,5 pt medidos); esta corrección no pretende igualar
todo el sistema tipográfico.

## Prueba privada y regresión

- PDF anterior: `site/pdf/N10-METSI-lectura-previa-v10-final.pdf`, SHA-256
  `6bf82a6b99e137467c8f2ac71bb92dd548e410da2bcb7895cf5bc323b3e2a5fc`.
- Candidato privado aprobado **sólo técnicamente**:
  `N10-type-private-20261028/N10-METSI-tipografia-privada-v2.pdf`, 37 A4,
  SHA-256 `fba101047ad61b65463db6fc5473ec7614765a733c0e701e0791adbabc508730`.
- La fuente renderizada retuvo 274/274 bloques, cero imágenes faltantes y
  cero bloques ocultos. Las 36 páginas no tocadas conservaron texto idéntico;
  la p. 6 conservó el mismo multiconjunto de palabras. La página 6 se revisó
  visualmente a 1.600 px sin recorte.
- La regresión de **37/37 páginas** a 50 dpi (`QA-REGRESION-VISUAL-PRIVADA-v4.json`)
  encontró diferencia de píxeles **sólo en p. 6**. Los 20 destinos del índice
  conservan nombres y folios, 170 anotaciones se conservan; la p. 6 mantiene
  `/StructParents=25` y los mismos 22 MCID. El PDF conserva idioma `es-AR` y
  árbol de etiquetas. Esto no equivale a prueba completa con lector de pantalla.
- El ensamblado genérico privado **se descartó** porque, aunque preservó texto,
  degradó las páginas a sangre 4, 5, 21 y 37 ya corregidas en el público.
  Una primera sustitución privada de stream produjo un PDF inválido para
  Poppler y también se descartó. La **v2** registrada arriba usa un stream
  indirecto; Poppler abrió p. 6 y p. 7 y la regresión completa pasó.

## Puertas que esta corrección NO cierra

Este recibo sólo habilita una corrección editorial digital acotada. No valida
el contenido académico de N10, una prueba docente, PDF/UA ni imprenta.
Después de publicar hay que verificar Pages y SHA remoto del nuevo archivo,
repetir el control de enlaces y actualizar inventario/handoff.
