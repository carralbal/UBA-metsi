# Handoff final autosuficiente · METSI N00 a N10

Fecha de cierre técnico: 4 de septiembre de 2026.

## Alcance y autoridad

Este cierre comprende N00 a N10. N11 queda expresamente excluido y no fue
consultado, regenerado, modificado ni incorporado al versionado.

Los PDF indicados en esta tabla son las versiones finales vigentes. Las fuentes
de N01 a N10 están congeladas en `BLOCK-01-content-final/`; la fuente de N00 se
conserva en `N00/source/N00_como_leer_metsi.md`.

| Documento | Páginas | Bytes | SHA-256 | PDF final |
|---|---:|---:|---|---|
| N00 | 45 | 30.648.242 | `1b4a1ab42665246349ed240659585a2e33766fe72157032bfbefc03cc7127f64` | `N00/output/N00-METSI-lectura-previa-final.pdf` |
| N01 | 29 | 26.886.102 | `668acc44383a86dbfec31620f47b9e511c1097ff1df7b846903942f8760d57fe` | `N01-v18-final/output/N01-METSI-lectura-previa-v18-final.pdf` |
| N02 | 29 | 25.335.126 | `35f7d39ac0981d11be568db17b9a422737e18005b583a281b326de8e069fe6a3` | `N02-v14-final/output/N02-METSI-lectura-previa-v14-final.pdf` |
| N03 | 30 | 15.142.425 | `08154728ce84f956c88f65a46d08018fda8ec933ca820380f9fb1166cc3512ef` | `N03-v9-final/output/N03-METSI-lectura-previa-v9-final.pdf` |
| N04 | 32 | 27.477.637 | `b6b4df7df6c92e4ed76cce15d89a0802f9c7c0b6529f16ed8cdeef1b9af23ccb` | `N04-v9-final/output/N04-METSI-lectura-previa-v9-final.pdf` |
| N05 | 28 | 15.880.141 | `cf6088c205637cf3cfb2902e5f5804c880f6f1c9509317df4b8d3b2334ccc516` | `N05-v9-final/output/N05-METSI-lectura-previa-v9-final.pdf` |
| N06 | 28 | 19.518.092 | `c05782e7ad61b544994032c4eb6a740ff52ab34573b9a45d36960f5dd03bfd6a` | `N06-v9-final/output/N06-METSI-lectura-previa-v9-final.pdf` |
| N07 | 31 | 20.825.394 | `c7b36bffcd3da4d1955f3563f7836dc9fad28d5cb0fa5ed7129bba1f2b075bd9` | `N07-v9-final/output/N07-METSI-lectura-previa-v9-final.pdf` |
| N08 | 28 | 19.397.092 | `8513d10b826cf9f69d9f8948a941a9013c1c57968bc9a08bfdc9686e8c788f36` | `N08-v9-final/output/N08-METSI-lectura-previa-v9-final.pdf` |
| N09 | 28 | 20.792.745 | `3cf21741a5b0ca81f924562171e38f45377acc1e4629e069719f8126879167aa` | `N09-v9-final/output/N09-METSI-lectura-previa-v9-final.pdf` |
| N10 | 31 | 21.552.865 | `cd5511c6bc9424c51ae2edd72444c0fe908dfa9f82753d29c93b39236a863f89` | `N10-v9-final/output/N10-METSI-lectura-previa-v9-final.pdf` |

Total: 339 páginas A4.

## Resultado de los gates

- Contenido N01 a N10: PASS. Total de 86.198 palabras, 71.406 sustantivas,
  123 referencias y 85 URLs. No hay párrafos duplicados ni secuencias
  compartidas de veinticuatro palabras o más.
- Validadores individuales: PASS para los diez PDF finales N01 a N10. N00
  conserva su aprobación y QA final documentados.
- Tapas N00 a N10: PASS 11/11. Son once fotografías distintas, concebidas en
  blanco y negro, a sangre, con amplitud tonal y contraste aprobados.
- Accesibilidad de tapa: PASS 11/11. Cada PDF está marcado, declara `es-AR` y
  enlaza el texto alternativo efectivo con una estructura `Figure` válida.
- Regresión interior: PASS 328/328 páginas, con igualdad exacta contra el
  baseline raster canónico.
- Enlaces: PASS 11/11 conjuntos de URL preservados.
- Reconstrucción aislada: PASS para N00 a N10. Las rutas del manifiesto central
  resuelven dentro del repositorio y el generador no requiere archivos de un
  directorio de trabajo anterior.

La evidencia detallada está en `BLOCK-01-cover-final/audit.json`,
`BLOCK-01-cover-final/baseline-interior-hashes.json` y
`BLOCK-01-content-final/provenance/block-integrity-report.json`.

## Reproducción

Dependencias Python: `requirements-qa.txt`. También se requiere Poppler. Avenir
y Didot deben estar disponibles legalmente desde macOS, desde `assets/fonts/`
o mediante `METSI_AVENIR_FONT` y `METSI_DIDOT_FONT`.

```bash
python3 build_collection.py --start 0 --end 10
python3 BLOCK-01-content-final/validate_block01_content.py
python3 BLOCK-01-cover-final/validate_block01_covers.py
```

SHA-256 del generador cerrado:
`f0249529fc10f42c2bcdc757f11c9a4e1ddb93dff1959926a104667c719f3ed6`.

SHA-256 del finalizador y QA:
`1c7950c978fabb1df7e6c678fef85eadab561d49f4ec5e80fcfbb71c69a788b8`.

## Estándar editorial congelado

La copia versionada de las skills y sus referencias está en
`editorial-standard/`. La regla de tapa exige fotografía nativa en blanco y
negro, calidad editorial premium, representación argentina o latinoamericana
cuando aparezcan personas o ámbitos locales, página completa sin bordes blancos,
gama amplia de grises y sombreado localizado. No se admite una capa negra global
que aplaste la imagen.

El contenido y las páginas interiores quedan cerrados. Una revisión futura de
tapas debe limitarse a la página 1 y volver a demostrar igualdad exacta de las
páginas 2 a final.

## Estado de publicación

Este cierre es local. El sitio público vigente llega hasta N06. N07, N08, N09 y
N10 no deben incorporarse a `main` ni al sitio sin autorización explícita del
autor. El tag local previsto para este estado es
`block-01-n00-n10-final-audited`.
