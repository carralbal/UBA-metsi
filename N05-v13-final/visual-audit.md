# Auditoría visual · N05 v9 final

## Resultado

**PASS.** La tapa v2 vigente fue verificada individualmente y como parte de la familia N00 a N10. El interior permanece bloqueado.

## Tapa vigente

- Maestro: `assets/cover-source-premium-bw-v2.png`.
- Desplegado: `assets/cover.png`.
- SHA-256 común: `0054cb5c5a9547134d476ff6bb02dd1d31e6757caa2fbcd32c77d648a180ccb8`.
- Procedencia: `provenance/cover-image-premium-bw-v2.md`.
- Fotografía original en blanco y negro, sin `grayscale()` ni desaturación efectiva en CSS.
- Cuatro profesionales argentinos y latinoamericanos deliberan alrededor de una silla vacía.
- Sangrado completo y cero halo claro en los cuatro bordes.
- Texto alternativo de la figura de tapa: “Silla vacía frente a una mesa de decisión donde cuatro profesionales argentinos y latinoamericanos examinan documentos y distribuyen autoridad”.
- La figura tiene una ruta semántica válida en la estructura del PDF.

## Escala tonal de la tapa compuesta

| Métrica | Resultado |
|---|---:|
| Luminancia media | 86,25 |
| Percentil 5 | 9,00 |
| Percentil 95 | 192,21 |
| Amplitud entre percentiles | 183,21 |
| Desvío estándar | 56,82 |
| Píxeles en tonos medios | 51,85 % |
| Píxeles por debajo de 32 | 16,08 % |

La tapa conserva una escala amplia de grises. El gradiente oscuro se limita a la base para sostener la legibilidad y no cubre la fotografía con una tela uniforme.

## Documento completo

- 28 páginas A4.
- Pausas internas a sangre en las páginas 5 y 19.
- Seis retratos de referentes distintos y de tamaño visual uniforme.
- Cuerpo sin colisiones, desbordes ni títulos huérfanos.
- Ninguna página ordinaria por debajo del 50 % de llenado; mínimo 50,16 %.
- Diez referencias ancladas y ocho URLs íntegras.
- Cierre con fósforos a sangre, folio, línea de pie, epígrafe y texto alternativo.

## Regresión y familia

- Páginas 2 a 28: identidad píxel por píxel contra la línea de base bloqueada.
- URLs: conjunto idéntico a la línea de base.
- Auditoría consolidada: `../BLOCK-01-cover-final/audit.json`, `PASS` en 11 de 11 documentos.
- La familia usa 11 fuentes de tapa distintas y supera el control de similitud perceptual.

## Evidencia

- `qa/N05-contact-sheet.jpg`
- `validation-v9.json`
- `qa-report.json`
- `provenance/cover-image-premium-bw-v2.md`
- `../BLOCK-01-cover-final/contact-sheet-N00-N10.jpg`
