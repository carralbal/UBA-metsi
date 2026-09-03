# Handoff autosuficiente, N03 v8 final

## Estado

N03 quedó sincronizado con su contenido canónico final, compuesto y auditado. La fuente histórica v7 y sus artefactos de 34 páginas no forman parte de esta entrega. El PDF v8 es un artefacto nuevo generado desde la fuente canónica y no una copia renombrada.

## Entrega principal

- PDF final: `output/N03-METSI-lectura-previa-v8-final.pdf`
- PDF bruto reproducible: `output/N03-METSI-lectura-previa-v8.pdf`
- Fuente empaquetada: `source/N03_fronteras_retroalimentacion_y_efectos-content-final.md`
- Fuente canónica: `../N03-content-final/source/N03_fronteras_retroalimentacion_y_efectos-content-final.md`
- Editables: `index.html`, `magazine.css`, `diagrams/N03-mapa-decision.svg`
- Auditoría: `validation-v8.json`, `qa-report.json`, `integrity-report.json`, `qa/N03-contact-sheet.jpg`, `visual-audit.md`
- Validador: `../validate_n03_v8.py`

## Contenido integrado

- 11 secciones numeradas y Referencias base como aparato SIN NUM.
- Tres movimientos: delimitar el recorte, observar el retorno de los efectos y decidir cuándo revisar la frontera.
- Entrada desde N02, continuidad HH-03 en los tres movimientos y salida explícita hacia N04.
- 9.034 palabras canónicas totales y 7.631 sustantivas entre Tesis y Síntesis.
- 11 referencias ancladas, siete URLs externas activas e íntegras.
- Cinco píldoras, 13 términos de glosario y seis preguntas de preparación.

## Decisiones de composición

- La página 4 es la Pregunta profesional en fondo oscuro completo.
- Hay exactamente dos pausas fotográficas internas a página completa. La primera ocupa la página 5 y la segunda la 19.
- Las secciones extensas se componen como artículos de dos columnas, con cortes específicos para impedir títulos huérfanos.
- La página 28 reserva la preparación en una grilla de dos columnas y la 29 presenta Referencias base en dos columnas minimalistas.
- La tapa, las dos pausas y el cierre llegan a sangre.
- Las cuatro voces de Hotel Horizonte usan retratos distintos, del mismo tamaño y sin duplicaciones.
- La tapa utiliza una fotografía cinematográfica producida para N03, con una protagonista argentina o latinoamericana, reflejos que materializan la noción de frontera y espacio negativo compatible con la composición estable.
- La comparación visual contra el commit anterior confirma que sólo cambió la página 1. Las páginas 2 a 30 son idénticas píxel por píxel a 72 dpi.
- La última página conserva la secuencia canónica de fósforos con estructura editorial completa y sin frase.

## Reproducción

```bash
python3 build_collection.py --start 3 --end 3
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 export_pdfs.py 3
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 finalize_and_qa.py 3
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 validate_n03_v8.py
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 render_contact_sheets.py 3
```

## Controles cerrados

- 30 páginas A4; ninguna página ordinaria queda por debajo del 50 % de llenado. El mínimo es 51,65 %.
- Cero títulos o subtítulos huérfanos en 64 encabezados verificados.
- Los 320 bloques elegibles de la fuente aparecen exactamente una vez en el HTML.
- Cero páginas eliminadas y cero rellenos visuales automáticos.
- Tapa accesible: `LECTURA PREVIA` y `EDICIÓN 2026` se extraen como cadenas completas.
- Seis referentes y cuatro voces distintas de Hotel Horizonte.
- PDF etiquetado, idioma `es-AR`, folio y pie en las 30 páginas y texto alternativo en el cierre.
- Las siete URLs coinciden entre fuente y anotaciones y conservan enteros `eur-lex`, `NIST.AI.600-1` y `NIST.AI.700-2`.
- La única raya larga pertenece al título oficial de ISO/IEC/IEEE 15288:2023.

## Identidad del artefacto

- Fuente SHA256: `6930c5a6cf7c98ad2f60ebf662334a7f491827260e460c939c51b7c9acef6854`.
- Fotografía de tapa SHA256: `9acbcc9aad15ee729692dcff9d22f4a15250e28d76c4b1058b3a528501154960`.
- PDF SHA256: `08ba8b04dec1372b24e13382f90ff85d8ba6cb68d068402ac15fbbdf1cd71f61`.
- Tamaño: 14.191.265 bytes.

## Incertidumbre

No quedan incertidumbres técnicas abiertas. La aprobación editorial final corresponde al autor.
