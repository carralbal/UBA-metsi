# Handoff autosuficiente · N07 contenido final

## Estado

N07 queda cerrado en etapa de contenido y listo para revisión autoral o composición posterior. La fuente v8 se conserva como antecedente inalterado. El paquete final pasa los controles deterministas y la auditoría humana de profundidad.

## Fuente autoritativa

`source/N07_entrevistar_no_es_pedir_requisitos-content-final.md`

Cuando se autorice la composición, esta fuente debe sustituir a la v8 como entrada. La v8 conserva sólo valor de procedencia.

## Qué está cerrado

- pregunta profesional, historia, tesis y continuidad N06, N07 y N08;
- arquitectura de tres movimientos;
- diferencia entre relevar una solución declarada y producir evidencia situada;
- preguntas episódicas, preguntas inductivas, familias de preguntas y sondas;
- incidente crítico, memoria reconstructiva y sesgo retrospectivo;
- diseño de la situación de entrevista, poder de información y variación;
- poder, seguridad psicológica, consentimiento, confidencialidad y reciprocidad;
- protocolo de entrevista y registro analizable;
- cadena de inferencia desde fragmento fuente hasta implicación de decisión;
- codificación reflexiva, explicaciones rivales, caso negativo y triangulación;
- tres aplicaciones HH-07, desde la pregunta hasta la afirmación defendible;
- uso responsable de transcripción, síntesis y codificación con IA en 2026;
- transferencia a órdenes de mantenimiento industrial;
- pase explícito a N08 para contrastar relatos con trabajo realizado;
- errores, consecuencias, límites, síntesis, cinco píldoras, glosario y seis preguntas;
- once referencias completas y ancladas;
- español rioplatense académico e impersonal, con voseo sólo en preguntas literales de entrevista.

## Decisiones curriculares

- N07 recibe de N06 una misión de evidencia ya delimitada. No vuelve a enseñar valor de información, cartera, muestreo general, criterio de parada ni riesgo residual.
- N07 transforma esa misión en preguntas, episodios, fragmentos fuente, interpretaciones y afirmaciones contrastables.
- N07 entrega a N08 episodios narrados, explicaciones rivales, rastros esperados y preguntas de observación. No enseña todavía el método de observación directa.
- La indagación contextual se utiliza para marcar la frontera: entrevistar con un artefacto como ancla no equivale a observar la actividad mientras ocurre.
- Se retiró el término `outcome` del cuerpo porque su formulación canónica corresponde a N10. N07 usa resultado esperado.
- Las preguntas literales conservan formas argentinas como `Llevame`, `Contame` y `recordás`; la voz expositiva permanece impersonal.

## Producto operativo de N07

La pieza profesional central es una cadena de evidencia con seis niveles:

1. fragmento fuente;
2. reconstrucción del episodio;
3. código descriptivo;
4. patrón;
5. mecanismo propuesto;
6. implicación de decisión.

El protocolo incluye propósito, selección, consentimiento, preguntas nucleares, sondas, temas sensibles, cierre y plan de registro y análisis. La consigna final exige aplicar ese protocolo a HH-07.

## Qué no existe todavía

No existen dentro de este paquete PDF, HTML, CSS, fotografías, infografías, estructura etiquetada, folios, pies ni decisiones de paginación. Su ausencia es deliberada y responde al encargo de trabajar sólo contenido.

## Cómo verificar

Desde la raíz del repositorio:

```bash
python3 N07-content-final/validate_n07_content.py
```

El comando debe terminar con código cero y escribir:

- `provenance/integrity-report.json`
- `source-manifest.json`

El informe esperado contiene `overall: pass`, más de 6.000 palabras sustantivas, once referencias ancladas, cinco píldoras, seis preguntas, tres aplicaciones HH-07, continuidad explícita con N06 y N08 y ninguna anticipación del término reservado para N10.

## Procedencia

La fuente histórica v8 permanece en `work/metsi_content/lecturas_fuente_v8/N07_entrevistar_no_es_pedir_requisitos.md`. Su SHA-256 esperado es `5df32a7ec4da3fb9db17b31622818e159d624f9e8376a2ca72ee2dbbddec8e54`. El validador no la modifica ni la utiliza como autoridad de composición.

## Incertidumbre residual

No existe incertidumbre abierta sobre contenido, secuencia, referencias ni frontera con N06 y N08. La etapa de contenido no permite validar paginación, viudas, densidad por página, orden de lectura del PDF, accesibilidad del artefacto, textos alternativos ni comportamiento de enlaces anotados. Esos controles quedan diferidos hasta una autorización explícita de composición.

## Condición para avanzar

N03, N04, N05, N06 y N07 quedan disponibles como contenidos canónicos. La composición de N07 permanece bloqueada. La continuación natural es N08, usando las discrepancias y preguntas de observación que entrega HH-07 y respetando la frontera curricular documentada aquí.
