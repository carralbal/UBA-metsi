# Estado vigente de METSI

Actualizado: 10 de septiembre de 2026.

Este archivo prevalece sobre auditorías anteriores cuando exista una diferencia de estado.

## Colección pública

La biblioteca de `site` conserva las rutas públicas estables de N00 a N36. N00 a N10 mantienen sus versiones aprobadas. N11 a N36 no se reemplazan todavía por los paquetes v6 porque la puerta exhaustiva de publicación no los habilitó como conjunto.

## Paquetes N11 a N36 v6

Los paquetes `N11-v6-editorial` a `N36-v6-editorial` se conservan completos como línea de reconstrucción recuperable. Incluyen fuentes, composición, activos, manifiestos, auditorías determinísticas y un PDF final de cada N.

No deben confundirse con una nueva aprobación externa. Una verificación posterior a su construcción detectó páginas ordinarias con densidad inferior al criterio editorial y una discordancia entre etiquetas declaradas y SVG en varias infografías. N26 presenta además un falso positivo probable del detector de marcadores sobre la cadena `todo:`. Esos hallazgos no se corrigen en este cierre porque el autor dispuso primero preservar decisiones y versiones, y después intervenir contenido y PDF.

## Infografías

La serie de `editorial-standard/infographic-rebuild-candidates-v3` y su catálogo `output/pdf/METSI-catalogo-infografias-N00-N36-revision-v3.pdf` están aprobados provisionalmente.

La aprobación acepta por ahora proximidades y solapamientos puntuales de texto con cajas. Esa deuda queda abierta. La serie todavía no está integrada en los PDF v6.

## Ampliación curricular

La distribución de PMI, PMBOK, Scrum, Kanban, UI, UX, diseño, DevOps, DORA, APIs, Git, GitHub, BPM, BPMN y autores argentinos y latinoamericanos está aprobada en `decisions/2026-09-10-infografias-y-ampliacion-curricular.md`.

El contenido nuevo todavía no fue escrito ni incorporado a los Markdown canónicos. Los PDF públicos y los paquetes v6 no contienen aún esta ampliación.

## Próxima secuencia autorizada

1. Preparar las fichas de intervención por N.
2. Revisar las fuentes canónicas sin tocar PDF.
3. Auditar contenido, continuidad y bibliografía.
4. Resolver la deuda geométrica de las infografías e integrarlas.
5. Recompaginar y superar la puerta exhaustiva.
6. Recién entonces sustituir los PDF de la biblioteca.

## Condición de recuperación

El repositorio debe contener este estado, las decisiones, los seis skills METSI, los generadores, validadores, catálogos, paquetes v6 y PDF finales. Los renders, cachés y PDF crudos permanecen excluidos por ser regenerables.
