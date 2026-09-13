# Auditoría final de lenguaje llano · N00 a N36

## Resultado

Las 37 fuentes canónicas quedaron revisadas para una lectura más amena, directa y llana, sin retirar profundidad académica. La auditoría automática global informa 37 documentos con señal `BAJA`, ninguno con señal `MEDIA` y ninguno con señal `ALTA`.

Este dictamen reemplaza el `NO PASS` de la auditoría diagnóstica del 12 de septiembre de 2026. Aquella auditoría se conserva como antecedente del problema y no describe el estado actual de las fuentes canónicas.

## Qué se controló

- entrada por una situación, una pregunta o una decisión reconocible;
- explicación previa al término especializado;
- párrafos recorribles y ausencia de bloques de 85 palabras o más;
- percentil 90 de oración no mayor a 30 palabras;
- continuidad entre una N y la siguiente;
- permanencia del caso Hotel Horizonte y sus decisiones cuando corresponde;
- conservación de tesis, conceptos, mecanismos, contraejemplos, instrumentos, límites y bibliografía;
- cinco píldoras, glosario y preguntas de preparación;
- ausencia de marcadores provisorios y de rayas incidentales.

## Excepciones documentadas

N04, N06, N07 y N09 tienen una media de párrafo menor que la referencia general porque contienen listas, tablas o unidades breves deliberadas. En todos ellos el percentil 90, las oraciones, la continuidad y la señal global pasan. N01 conserva su arquitectura introductoria propia, con siete preguntas y sin la secuencia de tres movimientos usada por las N temáticas.

## Guarda de contenido

La intervención se limitó a claridad, segmentación y jerarquía. No se eliminaron conceptos centrales, fuentes, marcos normativos, actores del caso, decisiones, incertidumbres ni consecuencias. Las métricas reproducibles están en `metrics.csv` y `metrics.json`; cada paquete actualizado contiene `source-manifest.json` e `integrity-report.json` con hash de la fuente autorizada.

La comparación reproducible contra la versión canónica anterior, o contra la fuente del último PDF público cuando no existía una versión canónica previa, obtuvo:

| Control | Resultado |
|---|---:|
| Fuentes comparadas | 37 |
| Fuentes que pasan todas las guardas | 37 |
| Relación mínima de palabras | 99,8 % |
| Relación máxima de palabras | 106,4 % |
| Cobertura mínima de los 60 términos sustantivos dominantes | 100 % |
| Bibliografías preservadas | 37 de 37 |
| Personajes de Hotel Horizonte perdidos | 0 |
| Puentes consecutivos faltantes | 0 |

El control también exige conservar las secciones nominales presentes en la base, el número de píldoras y preguntas, al menos el 70 % de la arquitectura de encabezados, el caso Hotel Horizonte, una longitud comparable, ausencia de texto provisorio y la regla de rayas. Los resultados por N están en `content-preservation.csv` y `content-preservation.json`.

La puerta se reproduce con:

```bash
python3 pedagogy/readability/audit_readability.py
python3 pedagogy/readability/audit_content_preservation.py
```

## Frontera

Esta auditoría no modifica PDF, fotografías, infografías, paginación ni sitio. Esos artefactos deben regenerarse después desde estas fuentes cerradas y pasar su propia auditoría editorial.
