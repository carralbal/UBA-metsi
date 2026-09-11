# Continuidad y recuperación del proyecto METSI

Este archivo define qué debe conservar Git para reconstruir el proyecto sin depender de una conversación de Codex.

## Fuente de verdad

- Repositorio público: `https://github.com/carralbal/UBA-metsi`.
- Rama publicada: `main`.
- Fuentes canónicas: carpetas `N00`, `N01`, `N02-content-final` a `N10-content-final` y `N11-content-canonical` a `N36-content-canonical`, junto con los planes y auditorías por bloque.
- Paquetes editoriales vigentes del bloque inicial: `N00-v3-final`, `N01-v18-final`, `N02-v15-final`, `N03-v10-final`, `N04-v9-final`, `N05-v10-final`, `N06-v10-final`, `N07-v10-final`, `N08-v10-final`, `N09-v10-final` y `N10-v9-final`.
- Paquetes editoriales vigentes de N11 a N36: `N11-v8-editorial` a `N36-v8-editorial`.
- Sitio publicable: `site`.
- Sistema editorial y skills recuperables: `editorial-standard`.
- Decisiones autorales que condicionan trabajo futuro: `decisions`.
- Sistema de producción pedagógica y paquetes de encuentro: `pedagogy`. Los bloques A, B, C y D, N01 a N20, están completos y auditados; las auditorías `pedagogy/AUDIT-BLOCK-A.md` a `pedagogy/AUDIT-BLOCK-D.md` conservan la evidencia de cierre.
- Selección académica vigente para la próxima reconstrucción de N11 a N36: `academic-content-revision-manifest-n11-n36.json`, acompañada por `ACADEMIC-CONTENT-AUDIT-N11-N36.md`.

Los paquetes `N11-v8-editorial` a `N36-v8-editorial` son la versión pública. Superaron la auditoría visual, la validación de PDF y la puerta de publicación. N00 a N10 permanecen protegidos por hash y no fueron alterados por esta promoción.

## Elementos que deben quedar versionados

- Markdown canónico, planes, matrices, decisiones y auditorías determinísticas.
- Generadores, validadores y scripts de publicación.
- HTML, CSS, JSON, SVG, textos alternativos y manifiestos de procedencia.
- Activos editoriales autorizados y sus metadatos.
- Un PDF final por versión editorial conservada.
- Catálogos de revisión necesarios para interpretar una aprobación del autor.
- Copia completa y verificable de los seis skills METSI.
- Plan maestro, preparación asincrónica, talleres, guiones docentes y rúbricas de la etapa pedagógica.

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
6. Ejecutar `python3 scripts/audit_academic_content_revision.py` para comprobar la revisión académica seleccionada de N11 a N36 antes de cualquier nueva composición.

El cierre integrado de N00 a N36 se reproduce con `python3 scripts/build_block01_completion.py`, se sella con `python3 scripts/audit_integrated_collection.py` y se publica localmente con `python3 scripts/sync_block01_integrated_release.py`.

La ausencia del chat no debe implicar pérdida de decisiones, fuentes, herramientas ni entregables. Una decisión que sólo exista en la conversación todavía no forma parte del estado recuperable.
