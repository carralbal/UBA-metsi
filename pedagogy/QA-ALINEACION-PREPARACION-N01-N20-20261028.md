# QA · consignas públicas y preparación docente N01–N20

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
| N11 | Una página sobre una afirmación externa: alcance, medición, población, origen, incertidumbre, uso permitido y uso excesivo. | Se quitó el expediente exhaustivo y las dos respuestas obligatorias; sensibilidad y procedencia profunda se trabajan en clase. |
| N12 | Una hoja/esquema de una transición elegida con pedido, aceptación, comprobación, resultado mostrado, rechazo y reparación. | RF, RNF, pruebas y tres tiempos pasan al taller; no se exige segunda entrega ni dos respuestas extras. |
| N13 | Una operación multisistema (HH-13 u otra) con respuesta perdida, repetición, conflicto y vista antigua; ficha y secuencia comprobable. | Se quitó el expediente completo previo, conservando protección, reconciliación y reparación; la simulación HH-13 no es segunda entrega. |
| N14 | **AS-IS y TO-BE antes de clase** del mismo caso, habitual y aviso fallido, dos medidas comparables y consecuencia de revisión. | Se corrigió el error que posponía el TO-BE. BPMN detallado se desarrolla en clase; constancias es opción válida sin exigir después HH-14. **Carga alta por medir.** |
| N15 | Tres preguntas, cuatro familias y alternativa no gráfica; cartera mínima, opción descartada, evidencia, omisión, mantenimiento y prueba. | Se quitó la prueba obligatoria con otra persona y dos respuestas extras; la cartera elegida se ensaya en taller. |
| N16 | Tres vistas vinculadas, caso habitual y difícil, diferencia, evidencia, tratamiento, prueba de cierre y revisión. | Se corrigió la guía que pedía demasiado poco; el taller transforma **el caso elegido**, no obliga a producir otro HH-16. **Carga por medir.** |
| N17 | Una decisión y dos lógicas, caso ordinario/adverso, compromiso razonable/prematuro; **si elige constancias**, prefactibilidad técnica/operativa/económica con salida de freno. | Se quitó el mapa exhaustivo y las dos respuestas extras; la cartera de métodos se ensambla en clase. La prefactibilidad no se presenta como presupuesto real. |
| N18 | Un expediente de elemento conocido con hecho/interpretación/vacío, conservar/adaptar/migrar/retirar, caso ordinario/excepción/ausencia y prueba de revisión. | Se quitó el informe arqueológico adicional y dos respuestas extras; dependencia y memoria se profundizan en taller. |
| N19 | Una capacidad, cuatro alternativas mínimo (una sin automatización), dos episodios iguales, excluyente, supuestos, salida y recomendación; p. 37 añade pesos 100 %, notas probadas, costos omitidos, autoridad y salida. | Se reconoció que la ponderación **sí pertenece a la preparación pública**: una sola matriz/expediente, con notas pendientes cuando no hay evidencia. Taller revisa criterios previos contra ofertas ficticias. **Carga alta por medir.** |
| N20 | Una ficha HH-20 de decisión próxima, dos hitos, no avance, contingencia, evidencia de transferencia y apoyo temporal que se retira. | Se quitó la estrategia completa y dos respuestas extras antes de clase; tailoring y puertas se desarrollan en taller. |

## Verificaciones y límites

- Para N05–N20 se releyó el texto extraído de la sección «Preguntas de
  preparación» de **cada PDF de `site/course-manifest.json`**, no de copias
  históricas. N13, N15, N18, N19 y N20 se contrastaron también con el producto de apertura;
  para N01–N04 se contrastaron apertura y cierre, porque la consigna puede
  estar repartida en varias páginas.
- `python3 pedagogy/validate_pedagogy.py`: **PASS 36/36**, sin problemas
  estructurales. N01–N20 conservan ocho actividades, 120 minutos planificados,
  diez pantallas y ocho criterios de rúbrica por paquete. Esos 120 minutos son
  una suma de diseño, **no una clase ensayada con reloj**.
- `git diff --check`: sin errores de espacio.
- No se cambió contenido sustantivo del PDF ni se añadió una preparación a N00.
- Falta aplicar el mismo contraste semántico a **N21–N36**, revisar las
  dependencias entre paquetes y ensayar la carga real con docentes/estudiantes.
