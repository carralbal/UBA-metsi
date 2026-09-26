# Revisión de mapas de decisión · N01–N36

Edición del 26 de septiembre de 2026. Alcance: legibilidad y distribución de los mapas aprobados, con integración de la redacción aprobada de N25. No constituye una nueva reescritura integral de las otras 35 lecturas.

## Resultado

- 36 documentos controlados; 34 mapas ampliados y recompuestos como gráficos vectoriales.
- N06 y N34 conservan sus PDF: sus versiones publicadas no contienen el mapa SVG objeto de esta revisión. N00, guía de la colección, queda fuera del reemplazo.
- N01–N10: nueva composición de las nueve lecturas con mapa, manteniendo exactamente los bloques de texto de origen. Se controlan también portadas, fotografías y referentes.
- N11–N36: reemplazo de la página de mapa; los contenidos de las demás páginas se comparan con el original. Excepción: N25 incorpora su versión completa de redacción previamente aprobada.
- N15: retirada de una página accidental sin texto ni imágenes, que contenía únicamente una línea desbordada. El original permanece recuperable en `N15/previous.pdf`.
- Cada carpeta conserva el PDF anterior y el nuevo, el contacto visual y los resultados de control. Los cambios no afectan presentaciones PPTX.

## Evidencia

`release-plan.json` identifica cada archivo público y su original mediante SHA-256. `assembly-report.json` registra la preservación de páginas. `qa-report.json` contiene control de texto, límites de página y tipografía; `visual-approval.json` vincula la revisión visual con los archivos finales. `publication-manifest.json` registra los reemplazos locales; el despliegue se confirma mediante GitHub Pages.

Los SVG editables, fuentes conceptuales, descripciones alternativas y controles geométricos se encuentran en `editorial-standard/approved-infographics/collection-legible-2026-09/`. Se conservan también los cuatro mapas aprobados como referencias de esta edición.

## Reproducción

Ejecutar, desde la raíz del repositorio, `scripts/build_legible_collection.py`, `scripts/render_legible_collection.mjs`, `scripts/prepare_map_release.py`, `scripts/render_map_readings.mjs`, `scripts/assemble_map_release.py` y `scripts/audit_map_release.py`. El render utiliza Chrome y Playwright; la auditoría utiliza pypdf, pdfplumber, Pillow y Poppler. Los intérpretes deben contar con esas dependencias. Revisar visualmente los resultados antes de actualizar la aprobación. `scripts/publish_map_release.py` instala sólo archivos cuyos hashes coincidan con la aprobación y cuyas auditorías no tengan incidencias pendientes.

Los directorios de imágenes temporales de cada página y los PDF intermedios de render no se versionan.
