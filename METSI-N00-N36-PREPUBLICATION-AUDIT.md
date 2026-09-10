# METSI · Auditoría integral previa a publicación N00 a N36

Fecha: 9 de septiembre de 2026.

## Dictamen ejecutivo

**PASS editorial y académico para revisión externa. PENDIENTE de publicación técnica de la nueva serie N11 a N36.**

La colección completa puede entregarse a ayudantes y jefatura como versión candidata final. N00 a N10 permanecen cerradas y no fueron modificadas. N11 a N36 fueron reconstruidas con el estándar aprobado de N00 a N10 y superaron los controles finales. El sitio público todavía sirve los PDF anteriores de N11 a N36, por lo que no debe presentarse la publicación web como actualizada hasta ejecutar y verificar la promoción.

## Autoridad de cada tramo

| Tramo | Estado local | Evidencia | Acción pendiente |
|---|---|---|---|
| N00 | v2 aprobada, 43 páginas | 27 controles técnicos, procedencia de imágenes y aprobación autoral | ninguna editorial |
| N01 a N10 | cerradas y congeladas | fuentes exactas, QA de PDF, integridad, tapas y regresión interior en `PASS` | ninguna editorial |
| N11 a N36 | reconstrucción v6 cerrada | 26 auditorías determinísticas, 26 integridades y 26 infografías en `PASS` | promover al sitio cuando se autorice |

## Alcance global

- Documentos: 37, N00 más 36 Núcleos.
- Bloques curriculares: ocho.
- Páginas de los PDF candidatos: 1.047, compuestas por 337 páginas en N00 a N10 y 710 en N11 a N36.
- Contenido N01 a N10: 86.198 palabras canónicas.
- Contenido N11 a N36: 209.560 palabras de fuente y 6.607 bloques canónicos.
- Tapas N00 a N10: once de once aprobadas.
- Referentes N11 a N36: 156, seis por lectura.
- Manifiesto central: N00 a N36 completos, en orden y sin códigos duplicados.

## Evaluación académica

**Acorde con la materia.** El conjunto enseña a transformar pedidos ambiguos en intervenciones defendibles. La progresión se concentra en representación, evidencia, decisión, realización, operación, gobierno y aprendizaje. Ingeniería de Software, gestión, experiencia, regulación e IA aparecen como tradiciones o dominios con los que la metodología dialoga, no como sustitutos del problema metodológico.

**Profundidad suficiente.** Las lecturas no se reducen a definiciones ni recetas. Presentan mecanismos, tensiones, criterios de aceptación, evidencia rival, consecuencias, límites y condiciones de revisión. El volumen se distribuye en unidades autónomas, con recuperación y preparación, en lugar de condensarse en un manual único.

**Actualidad.** La colección incorpora prácticas profesionales y debates vigentes, incluida la operación distribuida, accesibilidad, observabilidad, dependencia de terceros, gobierno de IA, supervisión humana y reparación. La actualización no desplaza las bases de pensamiento sistémico, acción situada, reflexión profesional y aprendizaje organizacional.

**Solapamiento controlado.** Los conceptos compartidos con otras materias se reinterpretan desde la pregunta metodológica: qué se afirma, qué evidencia lo sostiene, quién puede decidir, qué consecuencia se acepta y qué haría revisar el curso de acción. Ese criterio evita duplicar una materia de requisitos, arquitectura, producto, proyectos, datos o inteligencia artificial.

## Hilo conductor

**PASS.** N00 explica el contrato de lectura. N01 a N10 construyen el problema antes de recetar una solución. N11 a N20 convierten evidencia y estrategia en decisiones situadas. N21 a N30 gobiernan capacidades y sostienen la promesa en operación. N31 a N36 incorporan IA, integran el expediente, defienden criterios, transfieren aprendizaje y revisan la práctica.

Hotel Horizonte proporciona continuidad empírica. Los seis roles, la promesa, las restricciones y las decisiones acumuladas permiten que una distinción nueva modifique un caso ya conocido en vez de inaugurar un ejemplo aislado en cada documento.

## Evaluación editorial y estética

**PASS para el candidato local.** N00 a N10 conservan el sistema aprobado. N11 a N36 recuperan ese contrato: Contenido sobrio, Referentes completos, Hotel Horizonte canónico, Tesis, Síntesis, cinco píldoras lineales, Glosario, Preguntas sin fotografía, Referencias base y cierre estable.

Las imágenes interiores ya no son exclusivamente monocromas. El blanco y negro se reserva para tapas, contenido, referentes y anclas estables. Algunas escenas documentales interiores usan color original desaturado y controlado. Las infografías sólo emplean papel, blanco, tinta, grises y volt, sin azul, bronce, dorado ni masas negras dominantes.

## Evaluación pedagógica

**PASS.** Cada lectura plantea una pregunta profesional, ofrece distinciones para trabajarla, prueba esas distinciones en Hotel Horizonte, explicita límites y deja una preparación verificable para el encuentro. El dispositivo alterna lectura, recuperación, aplicación y discusión. La dificultad aumenta por acumulación de capacidades, no por vocabulario innecesario ni por compresión visual.

El conjunto es apto para revisión por un equipo docente porque permite discutir contenido y decisiones pedagógicas sin que fallas de maqueta, imágenes rotas o inconsistencias recurrentes contaminen la evaluación.

## Evidencia técnica vigente

1. `BLOCK-01-state-current/REPORT.md` certifica N00 a N10 y distingue el N00 v2 autoritativo.
2. `N11-N36-FINAL-EDITORIAL-AUDIT.md` consolida la reconstrucción v6.
3. `BLOCK-E-N21-N25-CROSS-AUDIT.md`, `BLOCK-F-N26-N30-CROSS-AUDIT.md`, `BLOCK-G-N31-N33-CROSS-AUDIT.md` y `BLOCK-H-N34-N36-CROSS-AUDIT.md` documentan continuidad y diversidad por bloque.
4. `audit_editorial_rebuild.py --start 11 --end 36 --version 6` termina sin fallas.
5. Los 26 `integrity-report.json` de v6 informan `PASS`, sin identificadores faltantes ni inesperados.
6. Las 26 infografías aprobadas poseen manifiesto, texto alternativo y validación geométrica con cero advertencias.

## Estado del sitio

El sitio contiene 37 descargas y su versión publicada pasa su propio validador, pero N11 a N36 todavía apuntan a la reconstrucción anterior v3 mediante rutas públicas estables. La versión v6 no fue sincronizada ni publicada durante esta auditoría. El próximo gate debe reemplazar PDF y miniaturas, actualizar manifiestos y hashes, validar las 37 descargas y comprobar el despliegue remoto.

## Conclusión

La versión local de N00 a N36 está en condiciones de pasar a revisión académica externa. No quedan brechas editoriales abiertas conocidas en N11 a N36. El único trabajo pendiente es operativo: empaquetar, versionar y publicar la nueva serie sin reabrir N00 a N10 ni alterar el contenido canónico.
