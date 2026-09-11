# N13 · Preparación asincrónica

## Propósito

Llegar con una transición distribuida analizada bajo respuesta perdida, duplicación, concurrencia y lectura antigua.

## Producción requerida

Tomá la falla identificada en N12 o el episodio de la última habitación de HH-13 y prepará un expediente de convergencia con:

- intención y efecto de negocio protegido;
- sistemas y observadores involucrados;
- respuesta perdida y estado ambiguo;
- duplicado y clave estable de intención;
- comandos concurrentes e invariante en riesgo;
- lectura antigua y ventana tolerable;
- política de coordinación o consistencia;
- reconciliación, compensación y evidencia de cierre;
- presupuesto de tiempo, reintento y escalamiento humano.

## Prueba adversa

Describí un caso en que reintentar empeore el resultado y otro en que coordinar todo reduzca disponibilidad sin proteger una consecuencia relevante. Respondé además dos preguntas de preparación de N13.

## Criterios de entrada

- Un timeout no se interpreta como rechazo.
- La identidad de intención sobrevive a los reintentos.
- Idempotencia protege un efecto definido.
- La consistencia se elige por observador, ventana e invariante.
- Reconciliar explica diferencias antes de corregirlas.

