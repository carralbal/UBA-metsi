# Ediciones bibliográficas de N28 y N29: corrección reproducible

Fuente fiel histórica, sin modificar aquí: `work/UBA-metsi-publication/output/source-recovery-20261020/N28-art-v7b/working/N28/index.html` y `N29-art-v4/working/N29/index.html`. Son las fuentes de las ediciones digitales publicadas el 24/10/2026, no los paquetes `N28-v10-editorial`/`N29-v10-editorial` del checkout de publicación.

Al regenerar, en el bloque `authors-page` de cada fuente, cambiar **sólo** el texto del `small` indicado:

| N | Referente | Actual en la fuente histórica | Corregido para nueva generación |
| --- | --- | --- | --- |
| N28 | Len Bass | `<small>, Fourth Edition. Addison-Wesley · 2021</small>` | `<small>Fourth Edition. Addison-Wesley · 2021</small>` |
| N29 | Kent Beck | `<small>, Second Edition. Addison-Wesley · 2004</small>` | `<small>Second Edition. Addison-Wesley · 2004</small>` |

La coma inicial quedó sola porque `cite` y `small` son bloques separados. El PDF público de cada N fue corregido directamente, sin duplicado privado, mediante `scripts/normalize_n28_n29_referentes_editions_20261028.py`. La normalización del fondo está en `referentes-paper-n28-n29.css`. Para reconstruir integralmente el PDF desde HTML hay que incorporar también la cubierta protegida, la versión exacta de las otras hojas de estilo y el acabado de accesibilidad de los recibos históricos. **Este registro de deltas no sustituye todavía una fuente única autocontenida y regenerada de punta a punta.**
