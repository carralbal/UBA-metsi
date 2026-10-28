# N16 · cierre interno del ajuste de clase post-Cecilia

Fecha: 28/10/2026. Alcance: paquete docente **candidato**, no PDF del estudiante ni clase efectivamente probada.

## Qué cambió

La lectura pública N16 ya integraba en pp. 25–29 una decisión HH-16, la contraprueba ficticia de constancias C-103/C-107 y dos vistas conceptuales de identidad/historia y decisión/comunicación. El taller anterior dedicaba 120 minutos casi por completo a clasificar contradicciones y no hacía producir/corregir un proceso, datos y condiciones de estado. Se **sustituyó** esa secuencia por una de 120 minutos con ocho checkpoints: pregunta de R-73, demostración mínima, construcción de proceso, C-103, cruce datos/estado con C-107, transferencia a HH-16 y corrección ajena. La única entrega conservada es HH-16; la constancia es un borrador de aula.

Se actualizaron juntos `PREPARACION-ASINCRONICA.md`, `TALLER-SINCRONICO.md`, `GUION-DOCENTE.md` y `RUBRICA-Y-EVIDENCIAS.md`. Hay alternativa de tabla estructurada al diagrama, sin licencia obligatoria. La rúbrica pide evidencia que otro ayudante pueda reconstruir sin explicación oral. Las notas docentes distinguen modelo conceptual de ER validado, caso ficticio de política institucional y control XSD de importación independiente.

## Control ejecutado

`pedagogy/validate_pedagogy.py` dio **PASS para 36/36 paquetes**, incluido N16: 8 checkpoints, 120 minutos, 10 pantallas descritas, 8 criterios de rúbrica y ningún marcador pendiente. `git diff --check` sin error. Esta validación comprueba estructura y suma de tiempos planeados; **no** demuestra que una clase real termine en 120 minutos, que el deck antiguo represente la nueva secuencia ni que la corrección ciega funcione.

## Puertas abiertas

1. Actualizar la PPT de aula N16 antes de usarla: el guion enumera sus diez pantallas nuevas, pero el archivo anterior sigue ligado a la secuencia vieja.
2. Importar el BPMN A/P1 en un modelador independiente y probar las dos contrapruebas; el XSD y las pruebas de reglas existentes no equivalen a esa importación.
3. Ensayar con ayudantes y cronómetro la ficha HH-16, registrar cuándo se exceden 120 minutos y quitar pasos si ocurre, sin sumar otra entrega.
4. Corregir una ficha sin defensa oral del equipo productor y documentar si la decisión y la contraprueba se pueden reconstruir.

La revisión pertenece al **paquete docente** de N16 y no cambia el PDF público ya cotejado por SHA en la colección de 37.
