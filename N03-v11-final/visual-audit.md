# Auditoría visual · N03 v9 final

## Resultado

**PASS.** La tapa vigente fue verificada individualmente y como parte de la familia N00 a N10. El interior permanece bloqueado.

## Tapa vigente

- Maestro: `assets/cover-source-premium-bw-v3.png`.
- Desplegado: `assets/cover.png`.
- SHA-256 común: `06976e01da816e65e8becdc825c62bd6b166e90654f23b74f9cd2b900cb0be94`.
- Procedencia: `provenance/cover-image-premium-bw-v3.md`.
- Fotografía original en blanco y negro, sin `grayscale()` ni desaturación efectiva en CSS.
- Sangrado completo y cero halo claro en los cuatro bordes.
- Texto alternativo de la figura de tapa: “Trabajadora hotelera argentina observa un corredor operativo desde un umbral de vidrio, con carros y puertas que prolongan el circuito hacia el fondo”.
- La figura tiene una ruta semántica válida en la estructura del PDF.

## Escala tonal de la tapa compuesta

| Métrica | Resultado |
|---|---:|
| Luminancia media | 123,55 |
| Percentil 5 | 16,72 |
| Percentil 95 | 215,53 |
| Amplitud entre percentiles | 198,82 |
| Desvío estándar | 57,83 |
| Píxeles en tonos medios | 71,83 % |
| Píxeles por debajo de 32 | 10,20 % |

La tapa conserva sombras, grises medios y altas luces. El oscurecimiento está localizado detrás de la información editorial y no funciona como velo negro uniforme.

## Documento completo

- 30 páginas A4.
- Pregunta profesional en fondo oscuro completo en la página 4.
- Pausas internas a sangre en las páginas 5 y 19.
- Cuerpo sin colisiones, desbordes ni títulos huérfanos.
- Ninguna página ordinaria por debajo del 50 % de llenado; mínimo 51,65 %.
- Referencias base en dos columnas minimalistas y siete URLs íntegras.
- Cierre con fósforos a sangre, folio, línea de pie, epígrafe y texto alternativo.

## Regresión y familia

- Páginas 2 a 30: identidad píxel por píxel contra la línea de base bloqueada.
- URLs: conjunto idéntico a la línea de base.
- Auditoría consolidada: `../BLOCK-01-cover-final/audit.json`, `PASS` en 11 de 11 documentos.
- La familia usa 11 fuentes de tapa distintas y supera el control de similitud perceptual.

## Evidencia

- `qa/N03-contact-sheet.jpg`
- `qa/N03-cover-v9.png`
- `validation-v9.json`
- `qa-report.json`
- `provenance/cover-change-regression.json`
- `provenance/version-v9-regression.json`
- `../BLOCK-01-cover-final/contact-sheet-N00-N10.jpg`
