# Backlog de cierre y puesta en marcha de METSI

Actualizado el 12 de septiembre de 2026.

Este backlog comienza después del cierre editorial de las lecturas N00 a N36. Distingue lo que ya existe de la pasada de diseño, prueba y publicación que todavía debe realizarse.

## P0. Reconstrucción visual y semántica de las lecturas N00–N36

**Estado:** N34 v9 construido como patrón local y no publicado. La colección pública todavía no incorpora estas correcciones.

### Trabajo pendiente

- Auditar la escala efectiva de cada infografía dentro del PDF, no sólo su SVG aislado. Dar página completa o dividir toda lámina cuyo texto no alcance una lectura normal al 100 %.
- Revisar cada tapa contra la pregunta profesional completa y eliminar asociaciones visuales literales o sesgadas producidas por una palabra del título.
- Normalizar los marcadores de sección: círculo papel, número y borde negros, volt reservado a acentos.
- Sustituir en N11–N36 el ancla inclinada de Hotel Horizonte por el archivo canónico de alta resolución y color desaturado.
- Homologar el encuadre de los seis personajes de Hotel Horizonte y escribir una posición específica de cada rol frente al tema de cada N.
- Auditar los seis Referentes de cada documento: retrato corto consistente, fuente verificable y presencia académicamente pertinente de voces argentinas o latinoamericanas.
- Ejecutar la regresión completa de tapa, Contenido, Referentes, pregunta profesional, caso Hotel, infografías, síntesis, píldoras, glosario, preguntas, referencias, enlaces, paginación y densidad.

### Criterio de cierre

Los treinta y siete PDFs pasan la auditoría visual al 100 %, conservan todos sus bloques canónicos y ninguna decisión compartida del generador introduce monotonía, pérdida de legibilidad o una lectura semántica ajena al argumento.

El diagnóstico y las guardas se conservan en [`audits/2026-09-12-N34-visual-semantic-audit-and-collection-gates.md`](audits/2026-09-12-N34-visual-semantic-audit-and-collection-gates.md).

## P1. Material docente para encuentros sincrónicos y asincrónicos

### Estado de partida

Ya existen treinta y seis paquetes pedagógicos, uno por cada N, y treinta y seis presentaciones editables. En conjunto contienen 360 pantallas y 360 notas de orador, además de preparación asincrónica, taller sincrónico, guion docente y rúbrica por cada Núcleo.

### Trabajo pendiente

- Realizar una revisión humana pantalla por pantalla y nota por nota.
- Separar con claridad lo que ve el estudiantado de lo que utiliza quien facilita.
- Asegurar que las presentaciones no resuman la lectura, sino que organicen decisiones, producción, contraste y revisión.
- Incorporar en cada encuentro propósito, tiempo, consigna, agrupamiento, materiales, evidencia disponible, perturbación, puesta en común y condición de salida.
- Preparar una variante asincrónica equivalente, con instrucciones autosuficientes, puntos de intercambio y devolución.
- Diversificar las dinámicas para que el recurso didáctico responda al objeto de aprendizaje de cada N.
- Probar los materiales con ayudantes antes de considerarlos definitivos.

### Entregables

- Presentación final por N, con capa visible para estudiantes.
- Notas de orador completas para profesor y ayudantes.
- Guía de facilitación sincrónica.
- Recorrido asincrónico equivalente.
- Ficha de materiales, tiempos, agrupamientos y evidencias de salida.
- Auditoría transversal de carga, variedad, accesibilidad y continuidad.

### Criterio de cierre

Cada encuentro puede ser facilitado por otra persona del equipo docente sin depender de explicaciones orales del autor, y reserva más tiempo para producir, contrastar y revisar que para exponer conceptos ya leídos.

## P2. Sistema de trabajo estudiantil para Hotel Horizonte

**Estado:** sistema candidato construido el 12 de septiembre de 2026. Pendiente de prueba piloto con el equipo docente.

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
