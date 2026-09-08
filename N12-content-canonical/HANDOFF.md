# Handoff autosuficiente · METSI N12 · contenido canónico v1

## Estado

N12 quedó desarrollado y auditado únicamente como contenido. No existe PDF, HTML, CSS, fotografía, portada, infografía ni plan de maqueta dentro de este paquete.

La única fuente textual autorizada para esta ronda es:

`N12-content-canonical/source/N12_eventos_estados_comandos_evidencia_y_autoridad-content-canonical-v1.md`

## Función curricular

N12 continúa el Bloque C y responde cómo distinguir lo que se pidió, lo que ocurrió, lo que se considera vigente, qué evidencia lo sostiene y quién tenía autoridad para decidir. Recibe de N11 afirmaciones auditadas y entrega a N13 transiciones preparadas para estudiar demoras, duplicación, concurrencia, consistencia, idempotencia y reconciliación.

El artefacto acumulativo es HH-12, mapa de transición verificable. Sus nueve campos conectan propósito, estado previo, comando, autoridad, reglas, evento, proyecciones, evidencia, tiempo, excepción y reparación.

## Qué quedó resuelto

- Historia de apertura sobre una inscripción universitaria confirmada por la interfaz y rechazada por la autoridad académica.
- Distinción precisa entre comando, evento, estado, consulta, evidencia, permiso, autoridad y transición.
- Tratamiento de tiempo del fenómeno, registro y conocimiento, correlación, semántica, proyecciones, rectificación, retractación y compensación.
- Tres aplicaciones sucesivas a Hotel Horizonte, incluida una transición defendible para “entregable”.
- Caso de transferencia hospitalario y contraejemplo de eventos genéricos sin significado.
- Integración de inteligencia artificial como capacidad técnica que no adquiere autoridad por sí sola.
- Método operativo de nueve campos, prueba de coherencia, matriz de autoridad, invariantes y prueba de reparación.
- Cinco píldoras, glosario, seis preguntas, seis referentes y Referencias base.
- Fronteras explícitas con N11 y N13.

## Métricas verificadas

- 7.835 palabras totales.
- 6.997 palabras sustantivas según las exclusiones del estándar METSI.
- 274 bloques fuente identificados y trazables.
- Catorce entradas en Referencias base, trece URLs y catorce anclajes explícitos en el cuerpo.
- Cero secuencias compartidas de veinticuatro palabras o más con N01 a N11, excluido el aparato bibliográfico.
- Auditoría humana de profundidad: 38/40, sin dimensiones por debajo de tres.
- SHA-256 de la fuente: `ce69f661943c34cf0e812685b6b61bfb7c7baff0b2cb66fa4b636ff27630769a`.

## Verificación

Ejecutar desde la raíz del repositorio:

```bash
python3 N12-content-canonical/validate_n12_content.py
```

El resultado esperado es `overall: pass`. El validador reconstruye además `source-manifest.json` y `provenance/integrity-report.json`.

## Incertidumbres y decisiones diferidas

No queda una incertidumbre conceptual abierta que impida la revisión autoral. La traducción visual de HH-12, la selección fotográfica, el volumen final de páginas y cualquier ajuste de lectura propio de la maqueta pertenecen a una etapa posterior y no fueron anticipados.

## Próxima decisión

La siguiente etapa válida es la revisión autoral del contenido. Recién después de su aprobación corresponde congelar la fuente como `content-final`, incorporarla al manifiesto del Bloque C y comenzar N13. La composición de N12 debe permanecer fuera de alcance hasta que N11 a N16 cierren su auditoría transversal de contenido.
