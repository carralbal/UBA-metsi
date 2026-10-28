# N04–N06 · normalización de Referentes en los PDF finales

Fecha: 28/10/2026. Alcance: edición digital para pantalla, no imprenta ni certificación de accesibilidad humana.

| N | Ruta estable | Páginas | SHA previo | SHA corregido local |
| --- | --- | ---: | --- | --- |
| N04 | `site/pdf/N04-METSI-lectura-previa-v10-final.pdf` | 34 | `0c8d87866705690a1110219dabb984b254ed9073f9eed02b48750b438a3bd4d9` | `833c22c4f2ad37560b5a4c7c65b3251853c1eaeb40208bff18e609b82c3bd20d` |
| N05 | `site/pdf/N05-METSI-lectura-previa-v11-final.pdf` | 32 | `ac485affa209f66176f92544d39b62646a4d33398fb79d629b8cd55b0a9139e2` | `98ffea9934ec2278fe6eb1c36357b17354df583e5fdec9685f86ce0dbede2a8c` |
| N06 | `site/pdf/N06-METSI-lectura-previa-v11-final.pdf` | 34 | `32f4e9ed7b2e3f7b91d9aadee60c039e0731a682ec12ca714dd436307b91dee9` | `49ff3ee5433c8bf5ff4eda6d6f4d0829341f13b2c1b1588fe907af039db8a997` |

## Sustancia y recibos existentes

- **N04:** `work/UBA-metsi-publication/pedagogy/N04/QA-DIGITAL-v7-20261023.md` y `PUBLICACION-DIGITAL-v7-20261023.md` certifican control visual histórico **34/34**, 309/309 bloques, 15/15 folios y SHA anterior idéntico. Fuente fiel entonces `output/source-recovery-20261020/N04-tail-v5/working/N04/`, no el paquete de nombre similar con menos páginas. Cotejo post-Cecilia de pp. 25, 29, 31 en inventario: procedencia/inferencia/rivales y prueba que debilite hipótesis.
- **N05:** `pedagogy/N05/QA-DIGITAL-v5-20261023.md` y `PUBLICACION-DIGITAL-v5-20261023.md` registran control visual histórico **32/32**, ruta y SHA anterior exactos; fuente `output/source-recovery-20261020/N05-pills-v2/working/N05/`. Cotejo post-Cecilia de pp. 23, 28, 30: objeción, mapa de afectados/decisores y autoridad. No confundir oportunidad detectada con validación de una herramienta preelegida.
- **N06:** `pedagogy/N06/QA-DIGITAL-v3-20261024.md` y `PUBLICACION-DIGITAL-v3-20261024.md` registran control visual **34/34**, 294/294 bloques, 20/20 entradas de índice, 21 enlaces internos, 104 externos y SHA anterior exacto; fuente fiel `output/source-recovery-20261024/N06-imac-source-private/working/N06/`. Cotejo post-Cecilia de pp. 15, 25, 30, 32: seleccionar investigación que cambie firma/postergación/cambio; el ensayo de taller no debe duplicarse en capítulo.

## Cambio acotado y control posterior

Las tres p. 3 presentaban un relleno vertical gris `[0,2336,794,1123]` sobre `paper`. `scripts/normalize_remaining_referentes_20261028.py` exigió SHA y operación exactos; anuló sólo ese relleno **sobre el PDF final**. No hay cambio de texto, anotaciones, geometría o etiquetas en 34/34, 32/32 y 34/34 páginas; fuera de p. 3 los streams son idénticos. Las tres p. 3 se renderizaron y abrieron a 1400 px: fondo uniforme y seis retratos, textos, pies íntegros. El override de fuente para futura recompaginación es `pedagogy/source-overrides/referentes-paper-n04-n06.css`; el checkout histórico con trabajo preexistente no se modificó. No se guardó PDF candidato privado.

Las claves de caché `n04-editorial-20261028`, `n05-editorial-20261028`, `n06-editorial-20261028` quedaron actualizadas en las cinco superficies web existentes. Commit `4416169eacdf6a883d9924d76efe77034cd89df7` subido a `origin/main`; Pages run `40766867726` terminó correctamente. `AUDITORIA-REMOTA-SHA-37-N-POST-N04-N06-20261028.json` descargó los **37/37 PDF** y confirmó SHA idéntico al final local; `AUDITORIA-ENLACES-SITIO-37-N-POST-N04-N06-20261028.json` confirmó **37/37 enlaces** del sitio. Los PNG efímeros se pueden retirar; no hay duplicados PDF privados.

Faltan ensayo docente con tiempo/corrección, accesibilidad humana y preprensa. Este cambio de una pintura no equivale a nueva revisión académica integral, pero tampoco borra los QA visuales históricos.
