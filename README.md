# METSI · Metodología de los Sistemas de Información

Repositorio de preservación editorial del material de lectura previa de METSI, Facultad de Ciencias Económicas, Universidad de Buenos Aires.

## Documentos finales vigentes

| Documento | Estado | PDF final | Auditoría y handoff |
|---|---|---|---|
| N00 | aprobado | [`N00-METSI-lectura-previa-final.pdf`](N00/output/N00-METSI-lectura-previa-final.pdf) | [`N00-EDITORIAL-STANDARD-HANDOFF-2026-08-29.md`](N00-EDITORIAL-STANDARD-HANDOFF-2026-08-29.md) |
| N01 | cerrado | [`N01-METSI-lectura-previa-v18-final.pdf`](N01-v18-final/output/N01-METSI-lectura-previa-v18-final.pdf) | [`N01-v18-final/HANDOFF.md`](N01-v18-final/HANDOFF.md) |
| N02 | cerrado | [`N02-METSI-lectura-previa-v15-final.pdf`](N02-v15-final/output/N02-METSI-lectura-previa-v15-final.pdf) | [`N02-v15-final/HANDOFF.md`](N02-v15-final/HANDOFF.md) |
| N03 | final auditable | [`N03-METSI-lectura-previa-v10-final.pdf`](N03-v10-final/output/N03-METSI-lectura-previa-v10-final.pdf) | [`N03-v10-final/HANDOFF.md`](N03-v10-final/HANDOFF.md) |
| N04 | final auditable | [`N04-METSI-lectura-previa-v9-final.pdf`](N04-v9-final/output/N04-METSI-lectura-previa-v9-final.pdf) | [`N04-v9-final/HANDOFF.md`](N04-v9-final/HANDOFF.md) |
| N05 | final aprobado | [`N05-METSI-lectura-previa-v10-final.pdf`](N05-v10-final/output/N05-METSI-lectura-previa-v10-final.pdf) | [`N05-v10-final/HANDOFF.md`](N05-v10-final/HANDOFF.md) |
| N06 | final auditable | [`N06-METSI-lectura-previa-v10-final.pdf`](N06-v10-final/output/N06-METSI-lectura-previa-v10-final.pdf) | [`N06-v10-final/HANDOFF.md`](N06-v10-final/HANDOFF.md) |
| N07 | final auditable | [`N07-METSI-lectura-previa-v10-final.pdf`](N07-v10-final/output/N07-METSI-lectura-previa-v10-final.pdf) | [`N07-v10-final/HANDOFF.md`](N07-v10-final/HANDOFF.md) |
| N08 | final auditable | [`N08-METSI-lectura-previa-v10-final.pdf`](N08-v10-final/output/N08-METSI-lectura-previa-v10-final.pdf) | [`N08-v10-final/HANDOFF.md`](N08-v10-final/HANDOFF.md) |
| N09 | final auditable | [`N09-METSI-lectura-previa-v10-final.pdf`](N09-v10-final/output/N09-METSI-lectura-previa-v10-final.pdf) | [`N09-v10-final/HANDOFF.md`](N09-v10-final/HANDOFF.md) |
| N10 | final auditable | [`N10-METSI-lectura-previa-v9-final.pdf`](N10-v9-final/output/N10-METSI-lectura-previa-v9-final.pdf) | [`N10-v9-final/HANDOFF.md`](N10-v9-final/HANDOFF.md) |

N00 a N10 integran el primer tramo editorial cerrado. N11 a N36 están publicados en sus paquetes v8, con fuentes canónicas, activos, diagramas y evidencia de QA preservados.

La revisión transversal de tapas, contraste, sangrado, texto alternativo,
unicidad y preservación exacta de interiores se conserva en
[`BLOCK-01-cover-final/`](BLOCK-01-cover-final/).

## Fuentes y reproducción

El repositorio conserva las fuentes canónicas, HTML y CSS editables, activos gráficos, infografías, manifiestos, informes de integridad, validadores, planchas de contacto y scripts de exportación. Cada versión final mantiene su propio handoff y su evidencia de QA.

Las dependencias Python de auditoría están fijadas en [`requirements-qa.txt`](requirements-qa.txt). La rasterización requiere Poppler. La finalización tipográfica usa Avenir y Didot: en macOS se resuelven desde el sistema y en otros entornos pueden declararse mediante `METSI_AVENIR_FONT` y `METSI_DIDOT_FONT`, siempre con archivos cuyo uso esté autorizado.

Las etiquetas Git `n01-v18-final`, `n02-v14-final`, `n03-v9-final`, `n04-v9-final`, `n05-v9-public`, `n06-v9-public`, `n07-v9-package-final`, `n08-v9-package-final`, `n09-v9-package-final` y `n10-v9-package-final`, junto con las etiquetas de contenido canónico, permiten recuperar estados aprobados sin depender de nombres ambiguos.

## Estándar editorial y skills

[`editorial-standard/`](editorial-standard/) contiene la copia versionada de las skills METSI activas:

- composición de documentos;
- generación integral de courseware;
- curaduría de imágenes;
- infografías deterministas;
- infografías editoriales de referencia;
- publicación del curso.

La regla de tapa vigente exige fotografía concebida originalmente en blanco y negro. No admite una imagen pensada en color y convertida después mediante desaturación o filtro.

## Publicación

La rama `main` y GitHub Pages publican la colección completa N00 a N36. N00 a N10 permanecen protegidos por hash y N11 a N36 corresponden al candidato editorial v8 promovido el 10 de septiembre de 2026. El historial completo, incluidas las versiones intermedias, permanece en el repositorio para trazabilidad.

## Producción pedagógica

[`pedagogy/`](pedagogy/) desarrolla el recorrido posterior a las lecturas: preparación asincrónica, talleres sincrónicos, guiones visuales con notas docentes, dinámicas, rúbricas y evidencia acumulativa. El plan maestro cubre N01 a N36 y los bloques A, B, C y D, N01 a N20, ya cuentan con paquetes ejecutables completos.

No se incorpora una licencia abierta. La disponibilidad pública del repositorio no constituye por sí sola una autorización de reutilización.
