# N14 · Preparación asincrónica

## Propósito

Llegar con un servicio seguido de punta a punta, desde la promesa hasta el cierre real, incluyendo esperas, handoffs, colas, excepciones y reparación.

## Producción requerida

Elegí HH-14 o un servicio conocido y construí dos recorridos: una instancia ordinaria y una excepcional. Para cada una declará:

- promesa, población, evento inicial, outcome y cierre;
- trabajo, espera y tiempo calendario;
- handoffs de trabajo, información y responsabilidad;
- colas visibles e invisibles y regla de prioridad;
- retrabajo, demanda de falla y reparación;
- trabajo prescripto, ejecutado y experimentado;
- evidencia que falta si sólo se observan aplicaciones;
- hipótesis de intervención y efecto rival.

Representá el núcleo en BPMN con pools o lanes pertinentes, eventos, actividades, gateways, flujos de secuencia y mensajes. Incorporá al menos una excepción y su retorno o compensación.

## Criterios de entrada

- El proceso no se confunde con área ni aplicación.
- El handoff transfiere responsabilidad, no sólo datos.
- Toda cola tiene política explícita o inferida.
- La excepción puede revelar una variante estable.
- BPMN se usa para coordinación y no como prueba de ejecución real.
