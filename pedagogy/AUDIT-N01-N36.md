# Auditoría transversal del sistema pedagógico N01 a N36

Fecha: 11 de septiembre de 2026.

## Dictamen

`PASS`. El recorrido pedagógico N01 a N36 está completo, ejecutable, versionado y listo para revisión de ayudantes y autoridades académicas.

Este dictamen alcanza la arquitectura de encuentros y materiales docentes. No sustituye la evaluación institucional ni afirma que una implementación futura será idéntica en todos los cursos. Declara que el sistema entregado satisface sus puertas explícitas y conserva evidencia suficiente para ser revisado.

## Integridad cuantitativa

| Control | Resultado |
|---|---:|
| Núcleos planificados | 36 |
| Paquetes completos | 36 |
| Piezas operativas | 144 |
| Actividades sincrónicas | 288 |
| Duración total diseñada | 4.320 minutos |
| Pantallas docentes especificadas | 360 |
| Criterios observables mínimos | 288 |
| Secuencias de taller distintas | 36 de 36 |
| Marcadores `TODO`, `TBD` o `XXX` | 0 |
| Problemas informados por el validador | 0 |

## Coherencia pedagógica

- Cada N comienza con producción asincrónica y evita pedir un resumen de lectura.
- Los encuentros utilizan la lectura como insumo y reservan el tiempo compartido para decidir, producir, perturbar, objetar y revisar.
- Cada taller tiene ocho actividades y ciento veinte minutos, pero la dinámica cambia según el objeto de aprendizaje.
- Cada guion docente tiene diez pantallas con función, nota de orador y señal para avanzar.
- Cada rúbrica evalúa razonamiento, evidencia, autoridad, límites y revisión, no prolijidad formal aislada.
- Cada Núcleo produce al menos un artefacto recuperable en el portfolio.

## Continuidad conceptual

El recorrido avanza desde el encuadre del problema hacia investigación, modelado, estrategia, producto, operación, IA, integración y reflexión. Los puentes no son frases administrativas: el producto de una N se convierte en restricción, evidencia o punto de partida de la siguiente.

Hotel Horizonte funciona como caso longitudinal en los treinta y seis paquetes. Cambia de pregunta y de presión en cada bloque: promesa, frontera, actores, episodios, datos, procesos, estrategia, flujo, contratos, calidad, operación, IA, gobierno, defensa y aprendizaje. No reemplaza los casos de transferencia, que comprueban si el criterio viaja sin copiar la solución.

## Profundidad y actualidad

- PMI y PMBOK se comparan por función de gobierno y anticipación, especialmente en N17 y N20.
- Scrum y Kanban se utilizan para aprendizaje, cadencia, compromiso y flujo, con límites explícitos.
- UX, accesibilidad y diseño se trabajan como evidencia de experiencia y no como cosmética.
- BPMN aparece como instrumento de coordinación y prueba de instancias en N14.
- APIs se estudian como contratos parciales dentro de acuerdos sintácticos, semánticos, temporales y operacionales en N27.
- Git y GitHub conservan procedencia y organizan colaboración dentro del gobierno de liberación en N29.
- DevOps y DORA se conectan con entrega, estabilidad, recuperación, retrabajo e incidentes en N29 y N30.
- La IA se aborda desde tarea, alternativa, autonomía, desigualdad, supervisión, gobierno, contestación, reparación y retiro en N31 a N36.
- Las ampliaciones curriculares y la incorporación de perspectivas argentinas y latinoamericanas permanecen documentadas en las fuentes editoriales y sus auditorías; los talleres las activan mediante dominios locales, obligaciones públicas y transferencia situada.

## Diversidad de aprendizaje

La auditoría confirmó treinta y seis secuencias diferentes. Se utilizan, entre otras, reconstrucción de episodios, observación, simulación de red, caminata BPMN, feria de modelos, prueba de retiro, arqueología de legado, consejo de cartera, flujo con fichas, apagón de proveedor, laboratorio de contratos, tribunal de calidad, trazabilidad Git, sala de incidentes, saturación de supervisión, audiencia de contestación, red team, defensa ante audiencias y clínica de doble bucle.

## Riesgos controlados

- No hay exposición docente extensa como actividad dominante.
- Ningún paquete puede resolverse copiando definiciones del PDF.
- Las perturbaciones obligan a cambiar o defender una decisión con evidencia.
- Las aprobaciones conservan riesgo residual, autoridad y condición de revisión.
- La IA no reemplaza verificación ni responsabilidad.
- Los instrumentos comunes no convierten las experiencias en plantillas mecánicas.

## Evidencia automática y recuperación

La puerta `python3 pedagogy/validate_pedagogy.py` cerró en `PASS`. También cerraron `python3 -m py_compile pedagogy/validate_pedagogy.py`, `git diff --check` y la búsqueda de marcadores pendientes y entidades HTML residuales.

El repositorio conserva plan maestro, cuatro piezas por N, auditorías por bloque, auditoría transversal y validador. El sistema puede reconstruirse sin depender de esta conversación.
