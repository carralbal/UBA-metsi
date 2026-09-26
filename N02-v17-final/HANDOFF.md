# Handoff autosuficiente, N02 v14 final

## Estado

N02 quedó sincronizado con su contenido canónico final y recompaginado como PDF auditable. La v13 se conservó intacta como referencia visual. La v14 incorpora únicamente el contenido canónico aprobado y los ajustes de composición necesarios para integrarlo sin regresiones. La identidad consignada abajo corresponde al PDF vigente después de la auditoría transversal de tapas del 4 de septiembre de 2026; esta actualización documental no constituye una nueva aprobación autoral.

## Entrega principal

- PDF final: `output/N02-METSI-lectura-previa-v14-final.pdf`
- Fuente empaquetada: `source/N02_el_sistema_no_cabe_en_una_aplicacion-content-final.md`
- Fuente canónica: `../N02-content-final/source/N02_el_sistema_no_cabe_en_una_aplicacion-content-final.md`
- Editables: `index.html`, `magazine.css`, `diagrams/N02-mapa-decision.svg`
- Auditoría: `validation-v14.json`, `qa-report.json`, `integrity-report.json`, `qa/N02-contact-sheet.jpg`, `visual-audit.md`
- Validador: `../validate_n02_v14.py`
- Auditoría familiar portable: `../BLOCK-01-cover-final/audit.json`
- Línea de base portable de interiores: `../BLOCK-01-cover-final/baseline-interior-hashes.json`
- Plancha familiar: `../BLOCK-01-cover-final/contact-sheet-N00-N10.jpg`

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
python3 export_pdfs.py 2
python3 finalize_and_qa.py 2
python3 validate_n02_v14.py
python3 render_contact_sheets.py 2
```

## Controles cerrados

- 29 páginas A4; ninguna página ordinaria queda por debajo del 60 % de llenado.
- Cero títulos huérfanos; cada una de las 24 secciones abre con cuerpo en la misma página.
- Cero páginas vacías eliminadas y cero rellenos visuales automáticos.
- Tapa accesible: `LECTURA PREVIA` y `EDICIÓN 2026` se extraen como cadenas completas.
- Portada nativa en blanco y negro, sin conversión cromática por CSS, con rango tonal validado y texto alternativo semántico asociado a una estructura `Figure` válida.
- Tapa, pausas y cierre llegan a sangre.
- Seis referentes y cuatro voces distintas de Hotel Horizonte.
- Cinco píldoras, 19 términos de glosario, seis preguntas y 17 referencias.
- PDF etiquetado, idioma `es-AR`, folio y pie en las 29 páginas, texto alternativo en el cierre.
- La única raya de inciso es parte del título oficial de ISO/IEC/IEEE 15288:2023.

## Identidad del artefacto

- Fuente SHA256: `6f6bfde594de374a8873fe212ac3c326b50b1186d61268a540a9303a77b1f138`.
- Portada: `assets/cover-source-premium-bw-v1.png`, desplegada como `assets/cover.png`; SHA256 `72a08234f87ad623c3092b3c06684551619fb881f625c2829543ccf0c2b10501`.
- Texto alternativo de portada: «Tres profesionales de un hotel porteño trabajan en recepción, un corredor operativo y un espacio reflejado detrás de un vidrio».
- PDF SHA256: `35f7d39ac0981d11be568db17b9a422737e18005b583a281b326de8e069fe6a3`.
- Tamaño: 25.335.126 bytes.
- Fecha de modificación: 2026-09-04 07:57:39 ART.
- Auditoría familiar: PASS, 11 de 11 documentos; 328 de 328 páginas interiores idénticas a la línea de base; 11 de 11 conjuntos de URLs idénticos; 11 de 11 portadas con `Figure` y texto alternativo válidos.
- Es un PDF nuevo generado desde la fuente canónica, no una copia renombrada.

## Incertidumbre

No quedan incertidumbres técnicas abiertas. El estado editorial continúa siendo «cerrado» y la aprobación final sigue correspondiendo al autor; esta actualización de identidad y auditoría no agrega una aprobación autoral nueva.
