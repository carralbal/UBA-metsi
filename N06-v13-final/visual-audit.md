# Auditoría visual · N06 v9 final

## Resultado

**PASS.** La tapa v1 vigente fue verificada individualmente y como parte de la familia N00 a N10. El interior permanece bloqueado.

## Tapa vigente

- Maestro: `assets/cover-source-premium-bw-v1.png`.
- Desplegado: `assets/cover.png`.
- SHA-256 común: `0780b6f86663444d876fb56f3d880b3a7256a44809e9ee569b10087603aa1fd0`.
- Procedencia: `provenance/cover-image-premium-bw-v1.md`.
- Fotografía original en blanco y negro, sin `grayscale()`, desaturación, contraste o brillo global efectivos en CSS.
- Escena profesional argentina, con rango tonal amplio y espacio negativo para la identidad METSI.
- Sangrado completo y cero halo claro en los cuatro bordes.
- Texto alternativo de la figura de tapa: “Profesional argentina observa un muro de evidencias y caminos alternativos en un estudio de Buenos Aires, en una fotografía editorial concebida en blanco y negro con una escala amplia de grises”.
- La figura tiene una ruta semántica válida en la estructura del PDF.

## Escala tonal de la tapa compuesta

| Métrica | Resultado |
|---|---:|
| Luminancia media | 140,64 |
| Percentil 5 | 24,21 |
| Percentil 95 | 238,00 |
| Amplitud entre percentiles | 213,79 |
| Desvío estándar | 65,44 |
| Píxeles en tonos medios | 58,74 % |
| Píxeles por debajo de 32 | 8,40 % |

La tapa preserva más grises y luces que las versiones anteriores sin perder contraste tipográfico. El refuerzo oscuro es localizado y llega al borde sin producir una costura inferior.

## Documento completo

- 28 páginas A4.
- Pausas internas a sangre en las páginas 5 y 13.
- Nota y epígrafe de Contenido sin superposición.
- Cuerpo sin colisiones, desbordes ni títulos huérfanos.
- Ninguna página ordinaria por debajo del umbral editorial; mínimo 65,87 %.
- Diez referencias ancladas y cinco URLs íntegras.
- Cierre con fósforos a sangre, folio, línea de pie, epígrafe y texto alternativo.

## Regresión y familia

- Páginas 2 a 28: identidad píxel por píxel contra la línea de base bloqueada.
- URLs: conjunto idéntico a la línea de base.
- Auditoría consolidada: `../BLOCK-01-cover-final/audit.json`, `PASS` en 11 de 11 documentos.
- La familia usa 11 fuentes de tapa distintas y supera el control de similitud perceptual.

## Evidencia

- `qa/N06-contact-sheet.jpg`
- `validation-v9.json`
- `qa-report.json`
- `provenance/cover-image-premium-bw-v1.md`
- `../BLOCK-01-cover-final/contact-sheet-N00-N10.jpg`
