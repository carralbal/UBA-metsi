# Handoff autosuficiente · N03 contenido final

## Estado

N03 queda cerrado en etapa de contenido y listo para revisión autoral o posterior composición. El manuscrito es nuevo, conserva la fuente v7 como antecedente inalterado y pasa los controles deterministas y la auditoría humana de profundidad.

## Fuente autoritativa

`source/N03_fronteras_retroalimentacion_y_efectos-content-final.md`

No debe volver a utilizarse la fuente v7 como entrada de composición cuando se autorice el PDF. La fuente v7 sólo conserva valor de procedencia.

## Qué está cerrado

- pregunta profesional, historia, tesis y continuidad N02 → N03 → N04;
- arquitectura de tres movimientos;
- HH-03 como hilo conductor;
- cuatro tipos de frontera y sus diferencias;
- mecanismos de retroalimentación, demora, desplazamiento, acumulación y control;
- tabla de explicaciones rivales;
- instrumento de decisión y piloto;
- transferencia, errores, límites, síntesis, cinco píldoras, glosario y seis preguntas;
- once referencias completas con anclaje en el cuerpo;
- español rioplatense académico e impersonal.

## Qué no existe todavía

No existen dentro de este paquete PDF, HTML, CSS, fotografías, infografías, retratos, estructura etiquetada, folios, pies ni decisiones de paginación. Su ausencia es deliberada y responde al encargo de trabajar sólo contenido.

## Cómo verificar

Desde la raíz del repositorio:

```bash
python3 N03-content-final/validate_n03_content.py
```

El comando debe terminar con código cero y escribir:

- `provenance/integrity-report.json`
- `source-manifest.json`

El informe esperado contiene `overall: pass`, 9.034 palabras totales, 7.631 palabras sustantivas, once referencias, cinco píldoras y seis preguntas. Si cambia la fuente, se debe ejecutar otra vez antes de versionar.

## Condición para avanzar

La próxima etapa lógica es repetir este proceso para N04, todavía sin PDF. La composición de N03 queda bloqueada hasta una autorización explícita posterior.
