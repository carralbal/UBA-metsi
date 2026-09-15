# Backlog de cierre y puesta en marcha de METSI

Actualizado el 14 de septiembre de 2026.

Este backlog comienza después del cierre editorial de las lecturas N00 a N36. Distingue lo que ya existe de la pasada de diseño, prueba y publicación que todavía debe realizarse.

## P0. Reconstrucción visual y semántica de las lecturas N00–N36

**Estado:** completado. N11 a N36 v9 fueron reconstruidos, auditados, integrados en `main` y publicados en GitHub Pages el 14 de septiembre de 2026.

### Trabajo realizado

- Se auditó la escala efectiva de las infografías dentro de cada PDF.
- Se revisaron tapas, marcadores, ancla de Hotel Horizonte, personajes, Referentes y presencia regional.
- Se ejecutó la regresión integrada de los treinta y siete documentos.
- Se publicó la colección vigente con fuentes canónicas, PDFs, manifiestos y auditorías trazables.

### Criterio de cierre

Los treinta y siete PDFs pasan la auditoría visual al 100 %, conservan todos sus bloques canónicos y ninguna decisión compartida del generador introduce monotonía, pérdida de legibilidad o una lectura semántica ajena al argumento.

El diagnóstico y las guardas se conservan en [`audits/2026-09-12-N34-visual-semantic-audit-and-collection-gates.md`](audits/2026-09-12-N34-visual-semantic-audit-and-collection-gates.md).

## P1. Material docente para encuentros sincrónicos y asincrónicos

### Estado

Paquete docente v3 construido y auditado nuevamente el 14 de septiembre de 2026. Existen treinta y seis paquetes pedagógicos, uno por cada N, y treinta y seis presentaciones editables. En conjunto contienen 360 pantallas y 360 notas de orador, además de preparación asincrónica, taller sincrónico, guion docente y rúbrica por cada Núcleo.

### Trabajo realizado

- [x] Se revisó la estructura de las 360 pantallas y las 360 notas.
- [x] Se separó la capa visible para estudiantes de la capa de facilitación.
- [x] Cada presentación usa la pregunta profesional canónica y las ocho actividades específicas de su N.
- [x] Cada encuentro declara propósito, tiempos, consignas, agrupamiento, materiales, evidencia, perturbación, puesta en común y salida.
- [x] Cada N incluye preparación y recorrido asincrónico equivalente.
- [x] Las dinámicas se vinculan con el objeto de aprendizaje y con Hotel Horizonte.
- [ ] Realizar una prueba piloto con ayudantes y registrar ajustes de uso real.

### Entregables

- Presentación final por N, con capa visible para estudiantes.
- Notas de orador completas para profesor y ayudantes.
- Guía de facilitación sincrónica.
- Recorrido asincrónico equivalente.
- Ficha de materiales, tiempos, agrupamientos y evidencias de salida.
- Auditoría transversal de carga, variedad, accesibilidad y continuidad.

### Criterio de cierre

Cada encuentro puede ser facilitado por otra persona del equipo docente sin depender de explicaciones orales del autor, y reserva más tiempo para producir, contrastar y revisar que para exponer conceptos ya leídos.

El criterio técnico está cumplido. La prueba piloto con ayudantes queda como validación situada previa a declarar versión de cohorte.

## P2. Sistema de trabajo estudiantil para Hotel Horizonte

**Estado:** sistema candidato construido el 12 de septiembre de 2026 y revalidado el 14 de septiembre de 2026. Pendiente de prueba piloto con el equipo docente.

### Decisión pedagógica recomendada

Hotel Horizonte debe trabajarse como un caso longitudinal y no como treinta y seis ejercicios aislados.

- Equipos estables de tres o cuatro estudiantes durante el curso para conservar memoria, distribuir roles y sostener decisiones complejas.
- Parejas dentro de cada equipo para microtareas breves, entrevistas simuladas, revisión cruzada y contraste de artefactos.
- Registro individual obligatorio al cierre de cada tramo para hacer visible qué sostuvo o cambió cada estudiante y con qué evidencia.
- Rotación de roles dentro del equipo para evitar especializaciones rígidas y asegurar participación: facilitación, evidencia, modelado, objeción y documentación.

### Régimen de entregas recomendado

No solicitar una entrega extensa después de cada N. Mantener un dossier vivo y versionado de Hotel Horizonte con microartefactos recuperables y ocho hitos formales, uno al cierre de cada bloque.

1. Bloque A: encuadre, frontera y afirmaciones iniciales.
2. Bloque B: actores, episodios, observación, experiencia y problem frame.
3. Bloque C: evidencia, estados, tiempos, procesos y coherencia entre modelos.
4. Bloque D: alternativas, restricciones y estrategia metodológica situada.
5. Bloque E: producto, hipótesis, cortes, priorización y flujo.
6. Bloque F: ecosistema, contratos, calidad, despliegue e incidentes.
7. Bloque G: pertinencia, evaluación y gobierno de IA.
8. Bloque H: dossier integrado, defensa, transferencia y reflexión final.

Cada hito conserva versiones anteriores, objeciones recibidas, decisiones revisadas, evidencia adversa y asuntos abiertos. La evaluación combina producto grupal, contribución individual y capacidad de revisar.

### Documentos por construir

- [x] Dossier maestro editable del caso.
- [x] Cuaderno de trabajo del equipo.
- [x] Registro individual de revisión.
- [x] Plantillas específicas para los ocho hitos.
- [x] Protocolo de revisión entre pares.
- [x] Rúbrica acumulativa y reglas de recuperación.
- [x] Guía docente para introducir episodios, evidencia nueva y perturbaciones sin convertir el caso en una receta.

Los materiales están en [`pedagogy/hotel-horizonte/`](pedagogy/hotel-horizonte/).

### Criterio de cierre

El sistema permite reconstruir cómo evolucionó una decisión desde N01 hasta N36, qué aportó cada integrante, qué evidencia produjo cambios y qué tensiones permanecen abiertas.

## P3. Programa y navegación de carralbal.github.io

### Programa de la materia

- Reconciliar las versiones existentes del programa y declarar una única fuente canónica.
- Tomar como candidato principal `metsi_content/03_programa_formal_propuesto.md`, contrastándolo con `UBA-metsi-contenidos/01-programa-general.md` y `UBA-metsi-contenidos/arquitectura/03_programa_formal_propuesto.md`.
- Revisar coherencia entre programa, ocho bloques, N00 a N36, carga, evaluación, bibliografía y perfil profesional.
- Publicar el programa nuevo en `https://carralbal.github.io/` con versión descargable y fecha de vigencia.

### Menú adaptable

- Mantener la navegación completa en pantallas amplias.
- Reemplazarla por un menú hamburguesa en anchos pequeños.
- Incluir apertura y cierre accesibles, foco de teclado, `aria-expanded`, cierre con Escape y área táctil suficiente.
- Verificar que no tape títulos, acciones ni anclas y que funcione en celular vertical, celular horizontal y tableta.

### Criterio de cierre

El sitio publica el programa canónico vigente, permite localizarlo desde la navegación principal y conserva una experiencia completa y accesible en escritorio y dispositivos móviles.

## Orden de ejecución recomendado

1. Diseñar y aprobar el sistema de trabajo estudiantil de Hotel Horizonte, porque define los artefactos que las clases deben producir.
2. Revisar y terminar los materiales docentes N01 a N36 contra ese sistema.
3. Consolidar el programa canónico y publicarlo en el sitio personal.
4. Implementar y auditar el menú adaptable.
5. Ejecutar una prueba piloto integral con ayudantes y registrar ajustes antes de la primera cohorte.
