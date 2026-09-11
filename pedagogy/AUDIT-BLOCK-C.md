# Auditoría pedagógica del Bloque C

Fecha: 10 de septiembre de 2026.

## Alcance

Paquetes N11 a N16 y continuidad acumulativa desde N10. Se revisaron preparación asincrónica, taller sincrónico, guion docente, rúbrica y evidencias.

## Resultado

`PASS`.

- Seis paquetes completos y veinticuatro piezas nuevas.
- Ocho momentos y ciento veinte minutos por encuentro.
- Diez pantallas funcionales por guion docente.
- Ocho criterios observables por rúbrica.
- Hotel Horizonte integrado como caso longitudinal que altera decisiones.
- Intervención docente breve, situada y posterior a una primera producción.
- Perturbación, prueba adversa, revisión y evidencia acumulativa presentes.
- Ninguna secuencia sincrónica duplicada entre N01 y N16.
- Sin marcadores `TODO`, `TBD`, `XXX` ni entidades HTML residuales.

## Progresión comprobada

| N | Operación central | Evidencia que entrega a la N siguiente |
|---|---|---|
| N11 | Auditar afirmación, medida, población, denominador y procedencia | Necesidad de eventos, estados y autoridad verificables |
| N12 | Diseñar una transición con semántica, tiempos, autoridad y reparación | Falla parcial, respuesta perdida o concurrencia |
| N13 | Proteger efectos e invariantes bajo distribución | Handoff, cola o excepción que excede la transición |
| N14 | Reconstruir y ejecutar el servicio completo mediante BPMN | Pregunta que requiere otra representación |
| N15 | Seleccionar una cartera mínima de modelos por pregunta y audiencia | Diferencias entre vistas que exigen interpretación |
| N16 | Clasificar y gobernar contradicciones y ciclos de vida | Incertidumbre que exige elegir una estrategia en N17 |

## Diferenciación conceptual

N11 no repite N04. N04 distingue el estatus epistemológico de afirmaciones y el puente inferencial. N11 agrega constructo, operacionalización, unidad, población, ventana, granularidad, denominador, procedencia técnica y prueba de sensibilidad para decidir si un dato alcanza.

N12 no se limita a una máquina de estados. Relaciona comando, evento, consulta, estado, evidencia, tres tiempos, autoridad institucional, invariantes, corrección y reparación.

N13 trata la incertidumbre introducida por demora, pérdida, duplicación y concurrencia. La consistencia y la idempotencia se eligen por efecto e invariante, no como propiedades universales.

N14 utiliza BPMN como notación de coordinación contrastada contra instancias ejecutadas. Incluye pools o lanes, eventos, actividades, gateways, mensajes, temporizadores, excepciones, compensación y retorno al flujo.

N15 evalúa utilidad y costo total de las representaciones. N16 evita forzar una fuente única y convierte diferencias entre modelos en decisiones gobernables de traducción, corrección, escalamiento, revisión o retiro.

## Variedad de dinámicas

N11 utiliza mesa de operacionalización, autopsia de procedencia y sensibilidad. N12 utiliza coreografía física, reconstrucción temporal y pruebas de transición. N13 utiliza una red con mensajes retenidos, duplicados y reordenados. N14 utiliza caminata de instancia, modelado BPMN y tormenta de excepciones. N15 utiliza feria, subasta de costo y prueba ciega. N16 utiliza recorrido transversal, propagación de cambio y simulacro de retiro.

## Puerta automática

`python3 pedagogy/validate_pedagogy.py` cerró en `PASS` con treinta y seis N planificadas y dieciséis paquetes construidos. Para cada paquete verificó archivos y marcadores, ocho actividades, ciento veinte minutos, diez pantallas, ocho criterios, presencia del caso Hotel Horizonte y ausencia de secuencias idénticas.

