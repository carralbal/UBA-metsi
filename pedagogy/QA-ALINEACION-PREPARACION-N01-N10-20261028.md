# QA · consignas públicas y preparación docente N01–N10

**Corte: 28/10/2026.** Se contrastaron las consignas de preparación de los PDF
canónicos indicados en `site/course-manifest.json` con los paquetes de
`pedagogy/Nxx/`. Esta revisión corrige carga oculta de trabajo previo; **no
modifica los PDF públicos ni certifica los tiempos reales de lectura o taller**.

## Regla de alineación

La lectura pública define qué lleva el estudiante al encuentro. La guía docente
puede aclarar ese producto, pero no añadir otro informe, un mapa exhaustivo o
una extensión obligatoria. El taller de 120 minutos puede transformar la
preparación breve en un artefacto más profundo. El portfolio reúne las evidencias
producidas en clase y no constituye automáticamente otra tarea asincrónica.

| N | Preparación que indica el PDF canónico | Corrección del paquete docente |
|---|---|---|
| N01 | Memo HH-01 y dos respuestas; el PDF no fija tiempo numérico. | La cifra de 20–30 minutos se identifica como hipótesis docente sin validar, no como tiempo prometido por la lectura. |
| N02 | Dos respuestas y **un** mapa HH-02 del episodio, con hipótesis y límite. | Se eliminó el segundo mapa y la nota separada; la frontera rival se construye en taller. |
| N03 | Dos respuestas integradas en **un** brief HH-03 con cuatro límites, efecto a contrastar y condición de revisión. | Se quitó la exigencia de otro informe/nota; la cadena causal más extensa se trabaja en clase. |
| N04 | Dos respuestas con **dos registros AED breves**, integrados. | Se quitó el dossier adicional de ocho campos y la nota; el dossier profundo se ensambla en taller. |
| N05 | Dos preguntas escritas; una aplica **un** mapa ADC a una decisión HH-05, actor ausente y evidencia. | Se quitó la cartografía exhaustiva previa y el texto adicional de la silla vacía. |
| N06 | Dos respuestas, hasta **300 palabras en total**; una contiene un registro HH-06 pequeño. | Se quitó el tablero previo de tres incertidumbres; la cartera se construye en clase. |
| N07 | Dos respuestas y un protocolo HH-07 corto: apertura, episodio, dos repreguntas, rival y conservación de fuente. | Se quitó la prueba y ampliación obligatoria antes de clase; se hacen en taller. |
| N08 | Dos respuestas y una ficha HH-08 breve de observación, interpretación, pregunta, función y decisión. | Se quitó el blueprint detallado previo; se construye con la escena observada en clase. |
| N09 | Dos respuestas y una ficha HH-09 de una transición, barrera, carga, rival y evidencia decisiva. | Se quitó el recorrido/blueprint completo previo; se ensambla en clase. |
| N10 | Dos preguntas y ficha HH-10 breve: hechos, hipótesis, dudas, acción autorizada/prohibida y hallazgo de revisión. | Se quitaron dos encuadres completos previos; el contraste de encuadres se produce en taller. |

## Verificaciones y límites

- Para N05–N10 se releyó el texto extraído de la sección «Preguntas de
  preparación» de **cada PDF de `site/course-manifest.json`**, no de copias
  históricas. Para N01–N04 se contrastaron además apertura y cierre, porque la
  consigna puede estar repartida en varias páginas.
- `python3 pedagogy/validate_pedagogy.py`: **PASS 36/36**, sin problemas
  estructurales. N01–N10 conservan ocho actividades, 120 minutos planificados,
  diez pantallas y ocho criterios de rúbrica por paquete. Esos 120 minutos son
  una suma de diseño, **no una clase ensayada con reloj**.
- `git diff --check`: sin errores de espacio.
- No se cambió contenido sustantivo del PDF ni se añadió una preparación a N00.
- Falta aplicar el mismo contraste semántico a **N11–N36**, revisar las
  dependencias entre paquetes y ensayar la carga real con docentes/estudiantes.
