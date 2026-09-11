# N13 · Rúbrica y evidencias

## Escala

- `0`: ausente o certeza inventada;
- `1`: falla identificada sin garantía ni consecuencia;
- `2`: solución técnica con identidad, invariante o reparación incompletas;
- `3`: robusta, explícita, convergente y reparable.

## Rúbrica del expediente de convergencia

| Criterio | Pregunta de evaluación | Evidencia de nivel 3 |
|---|---|---|
| Ambigüedad | ¿Conserva no saber como estado legítimo? | Distingue timeout, rechazo, éxito y consulta posterior. |
| Identidad | ¿La intención sobrevive a reintentos? | Utiliza clave estable y alcance declarado. |
| Idempotencia | ¿Protege un efecto de negocio? | Prueba repetición y reconoce consecuencias laterales. |
| Concurrencia | ¿Representa intenciones válidas incompatibles? | Protege el invariante sin inventar orden. |
| Consistencia | ¿Declara observador, ventana e invariante? | Coordina sólo donde la consecuencia lo exige. |
| Reconciliación | ¿Explica la divergencia antes de corregir? | Clasifica causa, evidencia, autoridad y decisión. |
| Compensación | ¿Reconoce daño residual? | Separa restauración técnica de reparación completa. |
| Operación | ¿Incluye presupuestos y escalamiento? | Limita reintentos, demoras y automatización de recuperación. |

## Evidencia de aprendizaje

El expediente final debe mostrar al menos dos revisiones producidas por la red o la perturbación: una sobre identidad, invariante o consistencia y otra sobre reconciliación, compensación o escalamiento.

## Conexión acumulativa

El handoff, la cola o la excepción identificados al cierre se conservan para N14. Allí se reconstruye el servicio completo mediante BPMN y evidencia de proceso real.

