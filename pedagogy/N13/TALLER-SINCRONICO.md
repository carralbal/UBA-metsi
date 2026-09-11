# N13 · Taller sincrónico

## Resultado del encuentro

Cada equipo entrega un expediente de convergencia para HH-13 que protege la última habitación, conserva estados ambiguos y define idempotencia, consistencia, reconciliación y reparación.

## Duración base

Ciento veinte minutos.

## Preparación docente

- Preparar sobres de mensajes, respuestas, duplicados y lecturas antiguas.
- Preparar dos estaciones que representen sistemas con relojes y demoras distintas.
- Preparar fichas de intención, efecto, compensación y daño.
- Disponer de un registro común que no revele de antemano el orden causal.

## Secuencia

### 1. Decisión después del timeout, 10 minutos

Cada persona decide si debe reintentar, esperar, consultar o escalar cuando no llega respuesta. Declara qué sabe y qué sólo supone.

### 2. Red de mensajes con pérdida, 16 minutos

Los equipos transportan comandos y eventos entre estaciones. El docente retiene, duplica y reordena sobres. Cada estación sólo conoce lo que recibió y debe registrar su estado local.

### 3. Clínica de garantías, 10 minutos

Se distinguen envío, entrega, procesamiento, respuesta y efecto de negocio mediante incidentes observados en la red.

### 4. Carrera por la última habitación, 22 minutos

Dos equipos reciben intenciones válidas de asignación. Deben proteger el invariante sin asumir reloj global ni éxito de toda coordinación. Registran qué vistas pueden converger después.

### 5. Laboratorio de idempotencia, 18 minutos

Se repite una misma intención con claves estables e inestables. El equipo identifica qué efecto queda protegido y qué consecuencias laterales todavía pueden duplicarse.

### 6. Mesa de reconciliación, 18 minutos

Tres registros difieren. Antes de corregir, el equipo clasifica demora, duplicado, conflicto, lectura antigua o error semántico. Elige fuente, evidencia, autoridad y compensación.

### 7. Prueba de perturbación, 18 minutos

Otro equipo ejecuta pérdida de respuesta, reintento tardío, conflicto concurrente y caída durante compensación. Evalúa convergencia, daño residual y condición de escalamiento.

### 8. Cierre y puente, 8 minutos

Cada persona identifica dónde la transición depende de un handoff, cola o excepción que N14 deberá representar de punta a punta.

## Evidencias para el portfolio

- decisión individual ante timeout;
- registros locales de la red;
- solución para la última habitación;
- prueba de idempotencia;
- acta de reconciliación;
- expediente perturbado y transición hacia N14.

