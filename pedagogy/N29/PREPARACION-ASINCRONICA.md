# N29 · Preparación asincrónica

## Propósito

Llegar con una cadena de cambio trazable desde una decisión hasta despliegue, exposición, recuperación y cierre.

## Producción requerida

Reconstruí una liberación HH-29 con:

- issue o decisión de origen;
- rama y commits en Git;
- pull request en GitHub con revisión y evidencia;
- integración continua y artefacto inmutable;
- configuración e infraestructura versionadas;
- aprobación basada en riesgo y segregación de funciones;
- despliegue progresivo, bandera y señales;
- rollback, rollforward, datos, terceros y cierre operacional.

## Prueba de recuperación

Suponé que el código puede volver, pero una migración de datos y una acción de un tercero no. Indicá qué parte del rollback era ficticia y cómo se repara. Respondé además dos preguntas de preparación de N29.

## Criterios de entrada

- Git conserva historia, no justificación suficiente.
- GitHub organiza una práctica, no reemplaza gobierno.
- Desplegar no equivale a liberar.
- El artefacto aprobado no se reconstruye.
- Recuperar incluye datos, configuración y operación.
