# N27 · Rúbrica y evidencias

## Escala

- `0`: documentación de endpoint;
- `1`: sintaxis sin acuerdo completo;
- `2`: contrato útil con operación o evolución incompleta;
- `3`: acuerdo verificable, temporal, reparable y evolutivo.

## Rúbrica del contrato

| Criterio | Pregunta de evaluación | Evidencia de nivel 3 |
|---|---|---|
| Sintaxis | ¿Formato y cardinalidad se prueban? | Incluye esquema y prueba incompatible. |
| Semántica | ¿Estados y campos significan lo mismo? | Declara definición, autoridad e invariante. |
| Tiempo | ¿Orden, vigencia y latencia están acordados? | Define ventanas y conducta ante demora. |
| Operación | ¿El acuerdo funciona fuera del desarrollo? | Incluye monitoreo, soporte y escalamiento. |
| Error | ¿La falla permite decidir y reparar? | Usa correlación, estado y acción explícita. |
| Idempotencia | ¿El reintento conserva invariantes? | Prueba duplicación o limita el efecto. |
| Seguridad | ¿Datos y permisos acompañan al contrato? | Declara protección, minimización y autoridad. |
| Evolución | ¿Versionar incluye migrar y retirar? | Prueba convivencia, compatibilidad y cierre. |

## Evidencia de aprendizaje

El contrato debe detectar una incompatibilidad semántica y temporal aunque ambos sistemas acepten el mismo mensaje.

## Conexión acumulativa

N28 convertirá sus garantías en reclamos de calidad sustentados por evidencia proporcional al riesgo.
