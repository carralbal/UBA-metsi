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

La ampliación quedó escrita en fuentes Markdown v2 de 25 lecturas y auditada junto con N35 y N36, que se preservaron byte por byte. La evidencia reproducible está en `audits/2026-09-10-curricular-expansion-audit.json` y su ejecutor en `scripts/audit_curricular_expansion.py`. Resultado: `PASS`, 27 fuentes presentes, 229.138 palabras totales, 10.562 palabras incorporadas, estructura completa, anclajes temáticos presentes, continuidad de Hotel Horizonte, cero párrafos extensos duplicados y cero cambios de PDF.

Las fuentes anteriores se conservan como línea de base. Los PDF públicos y los paquetes v6 todavía no contienen la ampliación.

## Próxima secuencia autorizada

1. Resolver la deuda geométrica puntual de las infografías aprobadas.
2. Integrar las fuentes v2 y las infografías en nuevos paquetes editoriales, sin sobrescribir las líneas de base.
3. Recompaginar y superar la puerta exhaustiva de contenido, estructura, imágenes, densidad y accesibilidad.
4. Sustituir los PDF de la biblioteca únicamente cuando el conjunto nuevo cierre en `PASS`.

## Condición de recuperación

El repositorio debe contener este estado, las decisiones, los seis skills METSI, los generadores, validadores, catálogos, paquetes v6 y PDF finales. Los renders, cachés y PDF crudos permanecen excluidos por ser regenerables.
