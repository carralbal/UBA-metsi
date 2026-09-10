# Continuidad y recuperación del proyecto METSI

Este archivo define qué debe conservar Git para reconstruir el proyecto sin depender de una conversación de Codex.

## Fuente de verdad

- Repositorio público: `https://github.com/carralbal/UBA-metsi`.
- Rama publicada: `main`.
- Fuentes canónicas: carpetas `N00`, `N01`, `N02`, `N03-content-final` a `N05-content-final` y `N11-content-canonical` a `N36-content-canonical`, junto con los planes y auditorías por bloque.
- Paquetes editoriales vigentes de reconstrucción: `N11-v6-editorial` a `N36-v6-editorial`.
- Sitio publicable: `site`.
- Sistema editorial y skills recuperables: `editorial-standard`.
- Decisiones autorales que condicionan trabajo futuro: `decisions`.

## Elementos que deben quedar versionados

- Markdown canónico, planes, matrices, decisiones y auditorías determinísticas.
- Generadores, validadores y scripts de publicación.
- HTML, CSS, JSON, SVG, textos alternativos y manifiestos de procedencia.
- Activos editoriales autorizados y sus metadatos.
- Un PDF final por versión editorial conservada.
- Catálogos de revisión necesarios para interpretar una aprobación del autor.
- Copia completa y verificable de los seis skills METSI.

## Elementos regenerables que no se versionan

- `__pycache__`, archivos `pyc`, temporales y cachés.
- Páginas rasterizadas, contactos de control y renders intermedios cuando existe el PDF final y el procedimiento para regenerarlos.
- PDF crudos anteriores a la normalización final cuando ya se conserva el PDF final correspondiente.

## Recuperación

1. Clonar el repositorio y ejecutar `git lfs pull`.
2. Ejecutar `python3 sync_metsi_skills.py --apply` para restaurar los seis skills activos desde `editorial-standard`.
3. Ejecutar `python3 sync_metsi_skills.py` para comprobar la sincronización.
4. Ejecutar `python3 editorial-standard/metsi-publish-course/scripts/verify_publishable.py .` desde la raíz.
5. Ejecutar `python3 site/validate_site.py --check-only --require-sources` para verificar la publicación local.

La ausencia del chat no debe implicar pérdida de decisiones, fuentes, herramientas ni entregables. Una decisión que sólo exista en la conversación todavía no forma parte del estado recuperable.
