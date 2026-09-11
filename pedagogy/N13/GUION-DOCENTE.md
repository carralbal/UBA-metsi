# N13 · Guion visual y notas docentes

## Función del soporte visual

El soporte administra información parcial. No muestra una línea temporal omnisciente mientras los equipos deciden.

| Pantalla | Qué se ve | Nota de orador | Señal para avanzar |
|---:|---|---|---|
| 1 | Pregunta profesional de N13 | Pedir decisión ante timeout y grado de conocimiento. | Se distingue ambigüedad de fracaso. |
| 2 | Reglas de la red | Cada estación sólo usa mensajes recibidos. | Los estados locales pueden divergir. |
| 3 | Cinco garantías | Separar envío, entrega, proceso, respuesta y efecto. | El grupo nombra qué ocurrió realmente. |
| 4 | Invariante de la última habitación | Evitar la solución por reloj global implícito. | Se protege el efecto crítico. |
| 5 | Clave de intención | Repetir mensajes y observar efectos. | Se distingue deduplicación de idempotencia. |
| 6 | Matriz de consistencia | Pedir observador, ventana, invariante y consecuencia. | La garantía deja de ser universal. |
| 7 | Tres registros divergentes | Exigir explicación antes de elegir fuente. | La reconciliación conserva historia. |
| 8 | Compensación y daño | Preguntar qué no puede deshacerse técnicamente. | Aparece reparación organizacional. |
| 9 | Prueba de perturbación | Introducir fallas durante la propia recuperación. | Hay presupuesto y escalamiento. |
| 10 | Puente a N14 | Seguir el caso más allá de los sistemas. | Surgen handoff, cola y excepción. |

## Preguntas de sondeo

- ¿Qué sabe quien inició la operación?
- ¿La ausencia de respuesta prueba ausencia de efecto?
- ¿Cuál es la identidad estable de la intención?
- ¿Qué invariante merece coordinación?
- ¿Qué observador puede tolerar demora?
- ¿Qué diferencia debe explicarse antes de corregir?
- ¿Qué daño no revierte una compensación técnica?

## Errores esperables

### Timeout tratado como rechazo

Intervención: ofrecer dos historias compatibles con la misma ausencia de respuesta.

### Identificador nuevo en cada reintento

Intervención: separar identidad de solicitud técnica e identidad de intención.

### Exactamente una vez sin alcance

Intervención: pedir qué efecto y qué frontera protege la garantía.

### Consistencia total por defecto

Intervención: comparar costo de coordinación con consecuencia protegida.

### Reconciliación por sobrescritura

Intervención: exigir explicación, autoridad, evidencia y reparación.

## Decisiones de facilitación

- Si alguien observa toda la red, restringirlo a su estación durante la decisión.
- Si la actividad se vuelve programación, volver a intención, efecto e invariante.
- Si la compensación parece borrar el episodio, introducir una consecuencia humana ya ocurrida.
- Si falta tiempo, reducir defensas, no la carrera concurrente ni la perturbación.

