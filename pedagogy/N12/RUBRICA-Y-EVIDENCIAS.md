# N12 · Rúbrica y evidencias

## Escala

- `0`: ausente o confundido;
- `1`: transición nominal sin evidencia ni autoridad;
- `2`: secuencia útil con tiempo, aceptación, invariante o reparación todavía imprecisos;
- `3`: semántica, especificada, refutable, autorizada y reparable.

## Rúbrica del mapa de transición

| Criterio | Pregunta de evaluación | Evidencia de nivel 3 |
|---|---|---|
| Distinción | ¿Separa comando, evento, estado, consulta y evidencia? | Cada elemento admite la prueba y el rechazo correspondientes. |
| Semántica y RF/RNF | ¿Los nombres expresan hechos y los requisitos se pueden refutar? | Un RF impide aceptación prematura; un RNF exige consulta usable; cada uno tiene prueba distinta. |
| Tiempo | ¿Distingue ocurrencia, registro y conocimiento? | Declara orden probado, demora y ambigüedad. |
| Correlación | ¿Las piezas pertenecen al mismo episodio? | Conserva identidad y vínculo entre sistemas. |
| Autoridad | ¿Distingue permiso técnico y legitimidad? | Asigna decisión, propuesta, veto y escalamiento. |
| Estado | ¿La proyección declara reglas y eventos conocidos? | Puede explicar divergencias sin fingir verdad eterna. |
| Invariante y aceptación | ¿La transición protege una condición relevante? | Se prueba en éxito, rechazo, duplicado y corrección; «recibido» no basta para aceptar. |
| Reparación | ¿Conserva consecuencias e historia? | Declara corrección, compensación, responsable y evidencia. |

## Evidencia de aprendizaje

El **único mapa HH-12** debe mostrar dos correcciones respecto de la clasificación inicial: una sobre intención/ocurrencia/estado y otra sobre tiempo/autoridad/reparación. Incluye RF, RNF y pruebas asociadas que otro equipo pueda intentar hacer fallar; no se califica por cantidad de requisitos.

## Conexión acumulativa

La falla parcial o concurrencia identificada al cierre se conserva para N13. Allí se diseñan idempotencia, consistencia y reconciliación según consecuencias.

