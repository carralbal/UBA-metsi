# Preparación de publicación · N06 v9 final

## Estado

**READY.** La composición corregida dispone de una cadena verificable para sus once imágenes renderizadas y para la fuente editable de la tapa. El PDF y el paquete autocontenido aprobaron el gate técnico final. Sólo falta la autorización expresa del autor para publicar N06 en el repositorio público.

## Cobertura verificada

- tapa original de curso, con fuente y render conservados dentro de `assets/`;
- tres fotografías editoriales realmente usadas, con autor, página fuente, licencia y SHA-256;
- seis retratos Commons distintos, con identidad, autor o crédito, licencia, hash fuente, transformación exacta y hash derivado;
- cierre canónico de fósforos preservado byte a byte;
- cero rutas privadas o absolutas en `image-manifest.json` y en las tres notas de procedencia;
- `hotel-horizonte.png` excluido porque N06 no lo referencia;
- los activos de retratos no seleccionados quedan fuera de la composición y del manifiesto de uso.

## Gate reproducible aprobado

El build final comprobó que el HTML referencia exactamente `cover.png`, `editorial-03.jpg`, `editorial-06.jpg`, `editorial-07.jpg`, los seis retratos declarados y `matches-close.png`; que sus hashes coinciden con `image-manifest.json`; que no aparece `hotel-horizonte.png`; y que no existen rutas privadas absolutas ni URI locales. Una segunda construcción reprodujo sin diferencias el HTML, el CSS, los manifiestos, el texto, los enlaces y las 28 páginas rasterizadas.

La nota de Donald A. Schön documenta la limitación de origen del registro Commons y la licencia Free Art License explícita. No queda marcada como bloqueo.
