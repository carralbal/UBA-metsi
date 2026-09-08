# Auditoría de profundidad · METSI N13

## Dictamen

**APTO COMO CONTENIDO CANÓNICO V1.** N13 supera el estándar de profundidad y puede pasar a revisión autoral. No se habilita todavía diseño ni PDF.

## Función curricular

N13 recibe transiciones verificables de N12 y estudia cómo sostenerlas bajo demora, repetición, concurrencia y falla parcial. Su avance exclusivo es convertir consistencia, idempotencia y reconciliación en decisiones vinculadas con invariantes, consecuencias y autoridad. Entrega HH-13 a N14 sin anticipar el análisis de procesos end-to-end.

## Evidencia de profundidad

- Apertura extensa sobre una beca pagada dos veces que todavía aparece pendiente.
- Tres lentes integrados: transacciones y recuperación, orden causal y modelos de consistencia, coordinación selectiva y sagas.
- Diecinueve unidades conceptuales centrales; todas superan 150 palabras.
- Tres aplicaciones a Hotel Horizonte, transferencia hospitalaria y contraejemplo de distribución innecesaria.
- HH-13 con diez campos más prueba de perturbación.
- Fuentes fundacionales y cinco entradas de 2022 a 2026 utilizadas en el argumento.

## Auditoría humana, 39/40

| Dimensión | Puntaje | Evidencia |
|---|---:|---|
| Precisión conceptual | 4 | Distingue entrega, efecto, intención, deduplicación, idempotencia, consistencia, convergencia y reconciliación. |
| Explicación por mecanismos | 4 | Reconstruye cómo respuestas perdidas, reintentos y concurrencia producen efectos incompatibles. |
| Progresión accesible a técnica | 4 | Avanza desde una beca duplicada hasta causalidad, invariantes, sagas y pruebas de perturbación. |
| Ejemplos y contraejemplos | 4 | Incluye beca, pagos, reservas, medicación, biblioteca y tres pasadas del caso longitudinal. |
| Literatura y actualidad | 4 | Integra Lamport, Gray, Helland, Vogels, Kleppmann y Bailis con guías 2022 a 2026. |
| Hotel Horizonte | 4 | Convierte una doble asignación en política verificable de convergencia. |
| Transferencia y condiciones de borde | 4 | El caso hospitalario y la biblioteca prueban consecuencias opuestas. |
| Singularidad | 4 | No redefine N12 ni invade proceso end-to-end de N14. |
| Legibilidad | 3 | La densidad técnica exige lectura activa, pero se sostiene mediante historia y ejemplos. |
| Utilidad decisional | 4 | Permite elegir coordinación, idempotencia, estado ambiguo y reconciliación por riesgo. |

No hay dimensiones inferiores a tres. El total supera 35/40.

## Red team

Una lectura superficial podría concluir que timeout significa falla, que idempotencia garantiza exactamente una vez o que consistencia eventual autoriza cualquier demora. El texto refuta las tres ideas mediante mecanismos y pruebas.

El contraejemplo de la biblioteca limita la tesis: distribuir puede fabricar el problema que luego pretende resolver. La decisión profesional que mejora es localizar el efecto protegido y elegir una garantía observable, no una etiqueta arquitectónica.

## Resultado

N13 contiene 6.018 palabras sustantivas, doce referencias completamente ancladas y cero coincidencias de veinticuatro palabras con N01 a N12. El validador pasa todos sus controles.
