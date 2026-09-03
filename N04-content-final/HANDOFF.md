# Handoff autosuficiente · N04 contenido final

## Estado

N04 queda cerrado en etapa de contenido y listo para revisión autoral o posterior composición. El manuscrito es nuevo, conserva la fuente v7 como antecedente inalterado y pasa los controles deterministas y la auditoría humana de profundidad.

## Fuente autoritativa

`source/N04_hechos_sintomas_relatos_hipotesis_y_decisiones-content-final.md`

No debe volver a utilizarse la fuente v7 como entrada de composición cuando se autorice el PDF. La fuente v7 sólo conserva valor de procedencia.

## Qué está cerrado

- pregunta profesional, historia, tesis y continuidad N03, N04 y N05;
- arquitectura de tres movimientos;
- HH-04 como hilo conductor;
- taxonomía de afirmaciones y rastros;
- modelo argumental, procedencia, triangulación, calidad de datos y causalidad;
- hipótesis rivales, pruebas discriminantes y suficiencia;
- Registro AED y condiciones de revisión;
- tratamiento de IA, contenido sintético y C2PA;
- transferencia, errores, límites, síntesis, cinco píldoras, glosario y seis preguntas;
- diez referencias completas con anclaje en el cuerpo;
- español rioplatense académico e impersonal.

## Qué no existe todavía

No existen dentro de este paquete PDF, HTML, CSS, fotografías, infografías, retratos, estructura etiquetada, folios, pies ni decisiones de paginación. Su ausencia es deliberada y responde al encargo de trabajar sólo contenido.

## Cómo verificar

Desde la raíz del repositorio:

```bash
python3 N04-content-final/validate_n04_content.py
```

El comando debe terminar con código cero y escribir:

- `provenance/integrity-report.json`
- `source-manifest.json`

El informe esperado contiene `overall: pass`, 10.108 palabras totales, 8.695 palabras sustantivas, diez referencias, cinco píldoras y seis preguntas. Si cambia la fuente, se debe ejecutar otra vez antes de versionar.

## Condición para avanzar

N03 y N04 están listos como contenido canónico. La composición de cualquiera de los dos documentos queda bloqueada hasta una autorización explícita posterior. La continuación natural del bloque es N05, tomando como entrada la fuente final de N04 y conservando su frontera curricular.
