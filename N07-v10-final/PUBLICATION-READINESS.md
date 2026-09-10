# Preparación de publicación · N07 v9 final

## Estado

**READY.** El paquete dispone de una cadena verificable para todas las imágenes renderizadas, la fuente editable de la tapa y la infografía. El PDF y el paquete autocontenido aprobaron el gate técnico final. Sólo falta la autorización expresa del autor para publicar N07 en el repositorio público.

## Cobertura verificada

- tapa original de curso, con fuente y render conservados dentro de `assets/`;
- cuatro fotografías editoriales y dos pausas internas generadas para METSI, nativamente en blanco y negro, con manifiesto y SHA-256;
- seis retratos de referentes distintos, con identidad, fuente, crédito, licencia o base de reutilización, transformación exacta y hash derivado;
- cuatro retratos canónicos y distintos del caso Hotel Horizonte;
- infografía original editable, con doce nodos, catorce relaciones, manifiesto semántico, texto alternativo y QA;
- cierre canónico de fósforos preservado byte a byte;
- cero rutas privadas o absolutas en los manifiestos de publicación;
- activos no seleccionados fuera de la composición y del manifiesto de uso.

## Gate reproducible aprobado

El build final comprobó la identidad de los 371 bloques canónicos, la presencia exacta de los activos declarados, los hashes de tapa, fotografías, retratos, infografía y cierre, y la ausencia de rutas locales privadas. Una segunda construcción reprodujo sin diferencias el HTML, el CSS, los manifiestos, el texto, los enlaces y las 31 páginas rasterizadas.

La publicación pública no se ejecuta con este cierre técnico. Requiere una autorización expresa y específica para N07.
