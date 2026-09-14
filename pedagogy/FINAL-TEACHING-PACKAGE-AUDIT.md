# Cierre del paquete docente METSI N01 a N36

Fecha: 14 de septiembre de 2026.

Resultado técnico y pedagógico: **PASS**.

## Alcance

- 36 paquetes pedagógicos ejecutables.
- 144 documentos troncales, cuatro por N: preparación asincrónica, taller sincrónico, guion docente y rúbrica con evidencias.
- 36 presentaciones editables v3.
- 360 pantallas visibles para estudiantes.
- 360 bloques de notas de orador.
- 288 actividades de taller, ocho por N y 120 minutos por secuencia completa.
- Sistema longitudinal de Hotel Horizonte con nueve documentos troncales, ocho hitos formales, cuaderno de equipo, bitácora individual, revisión entre pares y rúbrica acumulativa.

## Qué corrige la versión v3

Las versiones anteriores tenían una estructura técnicamente completa, pero las presentaciones podían leerse como plantillas genéricas. La v3 vincula cada archivo con la fuente canónica vigente y con las ocho actividades reales de su taller. Por eso cada encuentro presenta su pregunta profesional, sus consignas, su duración, su evidencia nueva, su producción y su cierre específico.

La capa visible evita resumir la lectura. Organiza trabajo, decisiones y revisión. La capa docente incorpora propósito, intervención sincrónica, señal para avanzar, preguntas de sondeo, adaptación asincrónica y resultado esperado.

## Controles ejecutados

- `validate_pedagogy.py`: PASS en N01 a N36.
- `validate_hotel_horizonte.py`: PASS en los nueve documentos y ocho hitos del caso.
- `audit_class_decks.py --revision v3`: PASS en 36 de 36 presentaciones.
- Integridad de archivos: 10 diapositivas y 10 notas por N.
- Consignas reales: presentes en las pantallas 02 a 09 y en sus notas.
- Paleta y tipografías: papel, tinta, gris y volt; Didot y Avenir.
- Revisión visual transversal: muestras de los ocho bloques y cierre N36, sin desbordes, colisiones ni texto fuera de página.

## Estado de uso

El paquete queda listo para revisión por jefatura de cátedra y ayudantes. La única actividad que no puede sustituirse con una auditoría de archivos es la prueba piloto situada con el equipo docente. Esa prueba no bloquea la entrega del candidato, pero debe registrar tiempos reales, dudas recurrentes y ajustes de facilitación antes de declarar una versión de cohorte.
