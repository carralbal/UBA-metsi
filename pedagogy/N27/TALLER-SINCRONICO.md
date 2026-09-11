# N27 · Taller sincrónico

## Resultado del encuentro

Cada equipo entrega y prueba un contrato HH-27 sintáctico, semántico, temporal y operacional.

## Duración base

Ciento veinte minutos.

## Preparación docente

- Preparar mensajes JSON válidos y semánticamente incompatibles.
- Preparar demoras, duplicados y respuestas perdidas.
- Preparar documentación de API sin operación.
- Preparar una versión nueva que elimina un campo.

## Secuencia

### 1. Intercambio ciego, 10 minutos

Un equipo publica mensajes y otro los consume sólo con un esquema. Se registran supuestos inevitables.

### 2. Laboratorio sintáctico, 14 minutos

Se validan tipos, obligatoriedad, cardinalidad y versiones. La prueba debe fallar con un cambio incompatible.

### 3. Juicio semántico, 18 minutos

Housekeeping y Recepción defienden significados distintos de `disponible`. Se acuerdan estados, autoridad e invariantes.

### 4. Reloj de contrato, 16 minutos

Se introducen demora, desorden y expiración. El equipo define ventanas, secuencia y decisión frente a dato tardío.

### 5. Tormenta de errores, 18 minutos

Una respuesta se pierde y el cliente reintenta. Se prueban idempotencia, códigos, correlación y reparación.

### 6. Guardia operacional, 16 minutos

La API responde, pero nadie atiende una inconsistencia nocturna. Se agregan observabilidad, escalamiento y soporte.

### 7. Migración compatible, 20 minutos

Se despliega una versión nueva con consumidores desiguales. Cada equipo diseña convivencia, prueba y retiro seguro.

### 8. Cierre y puente, 8 minutos

Se formula qué evidencia de calidad exigiría N28 antes de confiar en el contrato.

## Evidencias para el portfolio

- esquema y prueba negativa;
- glosario semántico;
- reglas temporales;
- contrato de error;
- modelo operacional;
- plan de migración y reclamo para N28.
