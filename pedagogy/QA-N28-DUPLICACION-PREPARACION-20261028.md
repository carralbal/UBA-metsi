# N28 · corrección editorial puntual de la preparación

Fecha: 28/10/2026. Alcance: PDF canónico digital, p. 35 únicamente.

## Defecto y causa

La última oración del producto para el encuentro aparecía dos veces: una dentro
de la consigna y otra como eco tipográfico ampliado debajo. La segunda era
redundante y aparecía además con palabras pegadas. Se verificó visualmente en el
PDF publicado. El HTML fiel recuperado en
`work/UBA-metsi-publication/output/source-recovery-20261020/N28-art-v7b/working/N28/index.html`
contiene la oración una sola vez; el eco surgió en el PDF ensamblado.

## Corrección y comprobación local

- PDF estable: `site/pdf/publicados/N28-METSI-lectura-previa-v10-final.pdf`.
- SHA previo en Git: `4bd945eb9ccf76ec8c1f7bbf47d725e1b24791df0547a32dc74b98f1df979b3e`.
- SHA corregido: `3fae7a187dac8f58d61278849b60e67495b48f0a8b47a2b6d1396a7cf4cf4692`.
- Receta determinista: `scripts/fix_n28_duplicate_prompt_20261028.py`. Parte del blob
  previo de Git, quita sólo las tres líneas del eco y sus dos reglas decorativas;
  conserva la consigna en su caja original. No mantiene copia PDF privada.
- 38 páginas A4, árbol de etiquetas estructurales y cantidad de anotaciones
  por página preservados. Texto extraído idéntico en las otras 37 páginas; en la
  p. 35 la frase aparece una vez. Render final de p. 35 revisado: folio 23,
  encabezado, siete preguntas, consigna, recuadro y pie permanecen legibles.
- Se cambió la clave de caché a `n28-prompt-20261028` en manifiesto, portada,
  atlas y colección de crónicas, sin cambiar la ruta pública estable.

El script de corrección conserva la fuente de esta edición como PDF+delta; una
regeneración integral desde HTML requiere verificar que el ensamblado no vuelva
a crear un eco duplicado. Esto **no certifica preprensa ni accesibilidad con
lector de pantalla humano**.
