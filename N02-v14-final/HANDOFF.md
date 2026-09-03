# Handoff autosuficiente, N02 v14 final

## Estado

N02 quedó sincronizado con su contenido canónico final y recompaginado como PDF auditable. La v13 se conservó intacta como referencia visual. La v14 incorpora únicamente el contenido canónico aprobado y los ajustes de composición necesarios para integrarlo sin regresiones.

## Entrega principal

- PDF final: `output/N02-METSI-lectura-previa-v14-final.pdf`
- Fuente empaquetada: `source/N02_el_sistema_no_cabe_en_una_aplicacion-content-final.md`
- Fuente canónica: `../N02-content-final/source/N02_el_sistema_no_cabe_en_una_aplicacion-content-final.md`
- Editables: `index.html`, `magazine.css`, `diagrams/N02-mapa-decision.svg`
- Auditoría: `validation-v14.json`, `qa-report.json`, `integrity-report.json`, `qa/N02-contact-sheet.jpg`, `visual-audit.md`
- Validador: `../validate_n02_v14.py`

## Contenido integrado

- 24 secciones numeradas y dos aparatos SIN NUM.
- Entrada de HH-01: el memo revisable se transforma en el sistema relevante de HH-02.
- Tres aplicaciones de HH-02, incluida la frontera lista para ser revisada.
- Salida hacia N03: relaciones con verbos, tres mecanismos rivales, evidencia discriminante y condición de revisión.
- 17 referencias, todas ancladas; 15 URLs externas activas e íntegras.

## Decisiones de composición

- Las secciones ya aprobadas mantienen su familia visual mediante un mapa estable por título.
- Los nuevos puentes de entrada y salida se componen en dos columnas y no heredan la portadilla fotográfica de caso.
- La primera aplicación de HH-02 conserva las cuatro voces del hotel sin crear una portadilla adicional.
- La sección 11 usa dos columnas y una banda fotográfica de 34 mm. Esta única adaptación permite cerrar en 29 páginas sin tocar tamaño de cuerpo ni interlineado.
- Se preservan dos pausas internas a página completa, la primera inmediatamente después de la página 4, y el cierre con fósforos.

## Reproducción

```bash
python3 build_collection.py --start 2 --end 2
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 export_pdfs.py 2
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 finalize_and_qa.py 2
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 validate_n02_v14.py
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 render_contact_sheets.py 2
```

## Controles cerrados

- 29 páginas A4; ninguna página ordinaria queda por debajo del 60 % de llenado.
- Cero títulos huérfanos; cada una de las 24 secciones abre con cuerpo en la misma página.
- Cero páginas vacías eliminadas y cero rellenos visuales automáticos.
- Tapa accesible: `LECTURA PREVIA` y `EDICIÓN 2026` se extraen como cadenas completas.
- Tapa, pausas y cierre llegan a sangre.
- Seis referentes y cuatro voces distintas de Hotel Horizonte.
- Cinco píldoras, 19 términos de glosario, seis preguntas y 17 referencias.
- PDF etiquetado, idioma `es-AR`, folio y pie en las 29 páginas, texto alternativo en el cierre.
- La única raya de inciso es parte del título oficial de ISO/IEC/IEEE 15288:2023.

## Identidad del artefacto

- Fuente SHA256: `6f6bfde594de374a8873fe212ac3c326b50b1186d61268a540a9303a77b1f138`.
- PDF SHA256: `fbe7afb20087cabac599f28f8bae3f51cee90e21933960476b874854e4f61052`.
- Tamaño: 28.030.274 bytes.
- Es un PDF nuevo generado desde la fuente canónica, no una copia renombrada.

## Incertidumbre

No quedan incertidumbres técnicas abiertas. La aprobación editorial final corresponde al autor.
