# N18 y N20 · cierre de franja gris en Referentes

Fecha: 28/10/2026. Alcance: PDF final digital; no supone aprobación docente ni prueba de imprenta.

| N | Páginas | Rectángulo heredado | SHA anterior | SHA final local |
| --- | ---: | --- | --- | --- |
| N18 | 38 A4 | `[0,2336,794,1145]` | `9c47c87654d1b34d9a354884e22e51c768c16de7260118073c6392f522b47331` | `9eec2458feca035d7d35f2c0d2d3657fbec713ba1396fb2e74c839a9e8e395db` |
| N20 | 42 A4 | `[0,2246,794,1123]` | `39ed5d0b3e1303445348255cbd2fde9e5f82626791d07914ad8cff66accb4bbb` | `4bdaabbcd899ee2c98babf29cbfdd567f15e121c31bd20a470b36df54b32613c` |

## Procedencia, cambio y QA

N18 se basa en la revisión digital fiel `N18-art-v4-working/N18/` (303/303 bloques, 38/38 páginas visuales), controlada en `work/UBA-metsi-publication/pedagogy/N18/QA-DIGITAL-v4-20261024.md`. N20 se basa en la edición fiel v21, fuente `output/source-recovery-20261024/N20-imac-source-private/working/N20/` (238 bloques, 42/42 páginas visuales), controlada en `pedagogy/N20/QA-DIGITAL-v21-20261024.md`. Esas fuentes históricas no se tocaron; la regla CSS de futura recompaginación quedó en `pedagogy/source-overrides/referentes-paper-n18-n20.css` del repo de liberación.

Las dos p. 3 tenían una banda gris de dimensiones **distintas**. `scripts/normalize_remaining_referentes_20261028.py` exigió SHA y rectángulo específicos para cada archivo y anuló sólo esa pintura **sobre el PDF final canónico**, sin retener PDF candidato privado. Las 38/38 y 42/42 páginas conservaron texto, anotaciones, geometría y estructura etiquetada; todos los streams fuera de p. 3 son idénticos. Se renderizaron y abrieron ambas páginas antes y después a 1200/1400 px: fondo paper uniforme, seis retratos, bibliografía y pies visibles; en N18 la banda anterior también cubría parte del pie y ahora no lo hace.

N20 redujo el peso binario al reescribir el contenedor PDF. Por eso se comparó adicionalmente, en memoria contra el blob anterior de Git, **cada imagen extraída de todas las páginas**: N18 28/28 y N20 29/29 con nombre y SHA idénticos. La reducción de bytes no significa que falte una fotografía.

Actualizar claves de caché `n18-editorial-20261028`, `n20-editorial-20261028` en el manifiesto y enlaces. Tras el despliegue completar aquí commit/run, cotejo 37/37 SHA y 37/37 rutas/revisiones. Eliminar sólo los cuatro PNG efímeros cuando el cotejo remoto termine. Esto cierra la **franja de Referentes en 37/37**, no el aval académico integral, la accesibilidad asistida ni la preprensa.
