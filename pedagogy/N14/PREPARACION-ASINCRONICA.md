# N14 · Preparación asincrónica

## Propósito

Llegar con **un mismo servicio** seguido de punta a punta, desde la promesa hasta el cierre real, incluyendo esperas, handoffs, colas, excepciones y reparación. La aplicación de constancias N14 p. 33 demuestra AS-IS/TO-BE con la misma unidad y medidas; no reemplaza HH-14 ni crea una segunda entrega.

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

Conservá un **AS-IS** de ese mismo proceso: población, inicio, cierre y dos medidas observables. El **TO-BE** se construirá en clase con la misma unidad; por ahora no atribuyas a ese diseño una mejora medida. Traé una hipótesis rival: ¿qué tarea podría simplemente trasladarse a otra persona?

## Criterios de entrada

- El proceso no se confunde con área ni aplicación.
- El handoff transfiere responsabilidad, no sólo datos.
- Toda cola tiene política explícita o inferida.
- La excepción puede revelar una variante estable.
- BPMN se usa para coordinación y no como prueba de ejecución real.
- AS-IS y TO-BE deben poder compararse en la misma población, frontera y medidas.
- Un proceso propuesto no es un resultado observado.
