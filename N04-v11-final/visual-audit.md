# Auditoría visual · N04 v9 final

## Resultado

**PASS.** La tapa v3 vigente fue verificada individualmente y como parte de la familia N00 a N10. El interior permanece bloqueado.

## Tapa vigente y procedencia

- Maestro: `assets/cover-source-premium-bw-v3.png`.
- Desplegado: `assets/cover.png`.
- SHA-256 común: `ac947baf49208e1eba7c1d5842c88e27e5761b2d0be86a8f7660a1afd7532925`.
- Procedencia: `provenance/cover-image-premium-bw-v3.md`.
- Cadena correcta: v3 deriva tonalmente de la fotografía v2, concebida desde el inicio en blanco y negro.
- Transformación documentada: luminancia monocromática, `Brightness 1.35` y `Contrast 1.05`, sin cambio geométrico y con diferencia nula frente a la receta reproducible.
- La composición no aplica `grayscale()` ni desaturación efectiva por CSS.
- Sangrado completo y cero halo claro en los cuatro bordes.
- Texto alternativo de la figura de tapa: “Analista de sistemas argentina en un hotel de Buenos Aires, observada entre reflejos y rastros documentales que sugieren evidencia, hipótesis rivales y decisiones”.
- La figura tiene una ruta semántica válida en la estructura del PDF.

## Escala tonal de la tapa compuesta

| Métrica | Resultado |
|---|---:|
| Luminancia media | 67,27 |
| Percentil 5 | 9,00 |
| Percentil 95 | 162,00 |
| Amplitud entre percentiles | 153,00 |
| Desvío estándar | 47,47 |
| Píxeles en tonos medios | 43,56 % |
| Píxeles por debajo de 32 | 21,57 % |

La composición conserva información en sombras, tonos medios y luces. Los refuerzos de contraste son localizados y no producen una tela negra uniforme.

## Documento completo

- 32 páginas A4.
- Pausas internas a sangre en las páginas 5 y 22.
- Cuerpo sin colisiones, desbordes ni títulos huérfanos.
- Ninguna página ordinaria por debajo del 50 % de llenado; mínimo 50,26 %.
- Diez referencias ancladas y ocho URLs íntegras.
- Cierre con fósforos a sangre, folio, línea de pie, epígrafe y texto alternativo.

## Regresión y familia

- Página 1: cambio intencional respecto de N04 v8.
- Páginas 2 a 32: identidad píxel por píxel contra N04 v8 y la línea de base bloqueada.
- URLs: conjunto idéntico a la línea de base.
- Auditoría consolidada: `../BLOCK-01-cover-final/audit.json`, `PASS` en 11 de 11 documentos.
- La familia usa 11 fuentes de tapa distintas y supera el control de similitud perceptual.

## Evidencia

- `qa/N04-contact-sheet.jpg`
- `qa/N04-cover-v9.png`
- `validation-v9.json`
- `qa-report.json`
- `provenance/cover-regression-v8-v9.json`
- `../BLOCK-01-cover-final/contact-sheet-N00-N10.jpg`
