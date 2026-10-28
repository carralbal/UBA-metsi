# N15 y N16 · corrección de referentes en la edición final

Fecha: 28/10/2026. Alcance: PDF digital; no preprensa ni evaluación humana con lector de pantalla.

| N | PDF canónico | Páginas | SHA anterior | SHA local corregido |
| --- | --- | ---: | --- | --- |
| N15 | `site/pdf/publicados/N15-METSI-lectura-previa-v10-final.pdf` | 48 | `a4977a3ea477a05640f45413d9ec06d27f8978c75fc6ecb3b19db6c4605bf1f5` | `10d831f4d326d96adb1cb59a7b8c5e226c81dd0d028cac798aa64d1e53b00869` |
| N16 | `site/pdf/publicados/N16-METSI-lectura-previa-v10-final.pdf` | 41 | `d3a1926e5bd2a838c1d7154c543061cf981addd9acf19be2aef04afbebb16020` | `cdfa170d4f3c55183e69d37abe3dbff452ede32ec6cf5c191d456d2d7a9f54fc` |

## Sustancia ya cerrada y límites

- **N15**: `work/UBA-metsi-publication/pedagogy/N15/QA-DIGITAL-v3-20261024.md` y `PUBLICACION-DIGITAL-v3-20261024.md` registran 48/48 páginas inspeccionadas, 313/313 bloques fieles, 27/27 folios del índice, 44 enlaces internos, 88 externos y 91 marcadores; Pages y SHA remoto comprobados para la edición previa. El cotejo post-Cecilia focal de pp. 33, 44 y 46 confirma que se eligen representaciones según decisión y omisiones. La producción básica de modelos con propósito se trabaja en N16; no ampliar N15 como catálogo de diagramas.
- **N16**: el paquete `N16-v11-post-cecilia/README.md` y su registro de QA documentan 41 A4, 316 identificadores conservados, un caso C-107 con siete familias y 25 movimientos inválidos rechazados, y las dos láminas aprobadas en pp. 28–29. El BPMN superó controles estructurales y XSD OMG anterior, pero no importación independiente en una herramienta ni ensayo docente. No sustituir esta edición por la v6 histórica.

## Cambio exacto y control

Las dos p. 3 «Referentes» contenían el mismo relleno gris `[0,2336,794,1123]` que rompía el fondo `paper` y una coma aislada antes de «Revised Edition». `scripts/normalize_n15_n16_referentes_20261028.py` exige SHA y geometría esperados; anula sólo ese relleno y quita sólo el glifo. Se aplicó **sobre cada PDF canónico**, sin mantener PDF privado. Verificó texto esperado, anotaciones, geometría y árbol de etiquetas en 48/48 y 41/41 páginas; fuera de la p. 3 los streams son idénticos. Ambas p. 3 se renderizaron a 1800 px y revisaron visualmente: papel uniforme, seis retratos, texto y pie íntegros. Deltas para futura recomposición: `pedagogy/source-overrides/referentes-paper-n15-n16.css` y `referentes-editions-n15-n16.md`.

Actualizar claves de caché en sitio a `n15-editorial-20261028` y `n16-editorial-20261028`, sin cambiar rutas. Al publicar, anexar commit, Pages run, SHA remoto 37/37 y chequeo de enlaces 37/37 antes de retirar renders temporales.

Pendientes de otra puerta: tiempo/carga de clase, prueba de lectura accesible humana, preflight de imprenta. El control de p. 3 no equivale a repetir la auditoría académica de todas las páginas.
