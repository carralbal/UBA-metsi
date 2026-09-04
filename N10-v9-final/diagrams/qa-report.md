# QA de infografía · N10 HH-10

**Estado:** PASS
**Fecha:** 2026-09-04
**Anclaje de integración:** `N10-s08-b001`
**Fuente canónica:** `N10-content-final/source/N10_construir_el_problema_y_outcomes-content-final.md`
**SHA-256 de la fuente:** `f272051348f0f2bf459e384cd66d433ae2881ac1d4d1d38200664a4c0e3f29c3`

## Contrato semántico

- Una afirmación central: los nueve campos se controlan mutuamente y sólo autorizan un compromiso proporcional.
- Tres bandas explícitas y no intercambiables: situar el cambio, sostener el argumento, limitar y reabrir.
- Nueve campos canónicos presentes una vez cada uno.
- Puerta final con cuatro salidas: aprobar, devolver, dividir y reformular.
- Catorce nodos únicos, dieciséis relaciones únicas y veintiún bloques fuente trazados.
- Todos los `source_id` del manifiesto existen en la fuente renderizable de N10.
- No se incorporaron conceptos decorativos ni se reescribió el manuscrito.

## Validación determinista

Comando ejecutado:

`python3 scripts/validate_infographic.py N10-HH10-encuadre-puerta-decision.svg --manifest content-manifest.json`

Resultado:

`RESULT: PASS (0 warning(s))`

Control semántico adicional:

`SEMANTIC PASS · 82 elementos de texto visibles · 14 nodos · 16 relaciones · 21 bloques fuente`

## Validación visual

- PNG renderizado desde el SVG a 3600 × 2200 px, exactamente 2× respecto del viewBox de 1800 × 1100.
- Inspección visual realizada a resolución completa y en reducción equivalente a página.
- Sin texto truncado, guionado mecánico ni elipsis.
- Sin colisiones visibles entre texto, objetos, puertos o conectores.
- Las rutas se dibujan detrás de los nodos y tienen extremos inequívocos.
- La ruta de revisión queda separada del rótulo de la tercera banda.
- Tipografía mínima: 14 px; no se redujo texto para resolver espacio.
- Contraste corregido en la puerta oscura; pregunta, condición y criterio proporcional son legibles.
- Uso activo del lienzo, sin regiones muertas relevantes.
- Paleta cálida, técnica y contenida; las diferencias no dependen sólo del color.
- Densidad, jerarquía y terminación contrastadas con el benchmark `hotel-horizonte-system.png`.

## Accesibilidad y formato

- SVG válido, editable, con `viewBox`, `role="img"`, `<title>` y `<desc>`.
- Texto alternativo largo y versión breve disponibles en `alt-text.md`.
- `review.html` usa la versión raster 2× y declara `lang="es-AR"`.
- No hay `foreignObject`, caracteres de guionado prohibidos ni CSS de partición de palabras.

## Huellas SHA-256

| Archivo | SHA-256 |
|---|---|
| `N10-HH10-encuadre-puerta-decision.svg` | `8eae98d3624777f9b0d631852fb75584504ccf22fd550c1ef41a995f75f1c707` |
| `N10-HH10-encuadre-puerta-decision@2x.png` | `52aef14350b41c3cebf8907824e15ba6acf791e808c1670be649ef1ddaef633f` |
| `review.html` | `f994263e7f9da032bfc827407ea4828b2ea25132faef3598027ffe0c8caaf8b0` |
| `content-manifest.json` | `7971428b5e3f11c8c1117513fabe33c407e4497e884a3a2bb70b1be2586ecf4a` |
| `alt-text.md` | `db29124a7c1ef5d013b32eafd7768f7e305592000644231d2413f25b0f6f5134` |

## Límite de esta entrega

La infografía queda aprobada como activo y fue integrada después en el HTML y el PDF de N10 mediante el anclaje canónico declarado.
