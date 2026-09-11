# N27 · Preparación asincrónica

## Propósito

Llegar con un contrato verificable que no reduzca una integración a formato y endpoint.

## Producción requerida

Elegí una frontera HH-27 y construí una ficha con:

- contrato sintáctico de una API;
- significado compartido de estados y campos;
- orden, latencia, vigencia y expiración;
- precondiciones, poscondiciones e invariantes;
- autoridad, soporte, observabilidad y reparación;
- errores, reintentos e idempotencia;
- seguridad, datos y compatibilidad de versiones;
- pruebas de contrato y migración.

## Prueba de compatibilidad engañosa

Hacé que dos sistemas acepten el mismo JSON, pero interpreten `disponible` de manera distinta y fuera de tiempo. Explicá qué prueba detecta cada ruptura. Respondé además dos preguntas de preparación de N27.

## Criterios de entrada

- Una API es un contrato parcial.
- Sintaxis válida no garantiza significado común.
- Tiempo y orden forman parte del acuerdo.
- Un error debe orientar una reparación.
- Versionar exige transición y retiro.
