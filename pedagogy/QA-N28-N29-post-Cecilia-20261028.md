# N28 y N29 · cotejo post-Cecilia y corrección editorial directa

Fecha: 28/10/2026. Alcance: lectura digital en pantalla; **no** certificación docente integral ni preprensa.

| Lectura | PDF público estable | Páginas | SHA-256 previo | SHA-256 corregido |
| --- | --- | ---: | --- | --- |
| N28 | `site/pdf/publicados/N28-METSI-lectura-previa-v10-final.pdf` | 38 | `e5ce7ee145f935cb5cae8932beae49db25ac3cb8b96cafbb4cc0d9f8afb20006` | `4bd945eb9ccf76ec8c1f7bbf47d725e1b24791df0547a32dc74b98f1df979b3e` |
| N29 | `site/pdf/publicados/N29-METSI-lectura-previa-v10-final.pdf` | 39 | `fb12efc5e00fe20a60656f57a517a65c65e8325d97cf2bfa10a22b0bba901a5c` | `61343dbe70308840bb334c5e1a84a794e0345be1c9826bda4bfda103af2bf71b` |

Los SHA previos coinciden con los recibos históricos de `work/UBA-metsi-publication/pedagogy/N28/QA-DIGITAL-v7b-20261024.md` y `N29/QA-DIGITAL-v4g-20261024.md`. Las fuentes fieles de esas ediciones están en `output/source-recovery-20261020/N28-art-v7b/working/N28/` y `N29-art-v4/working/N29/`. No usar un paquete `v10` como sustituto sin cotejo de identidad.

## Revisión curricular focal

- **N28**: barrido visual de 38/38 páginas y lectura de pp. 23–25, 33 y 35. La evaluación de calidad está anclada en doce preguntas sobre evidencia, oráculo, excepciones, decisiones y responsabilidad. La muestra didáctica de 20 episodios seleccionados no se presenta como estimación de los 200 casos mensuales. El producto de preparación es único; no se añade otra entrega.
- **N29**: barrido visual de 39/39 páginas y lectura de pp. 25–27, 35 y 37. El instrumento muestra un plan de cambio con ramas de reversión compatible y corrección hacia adelante. Los doce registros ficticios se distribuyen 9+2+1 y se usan para ensayar contingencias, no para proclamar desempeño. La preparación integra plan, árbol de decisión y registro sin convertirlos en tres trabajos separados.
- Estos cotejos confirman cobertura metodológica de prueba de servicio y despliegue/recuperación, pero **no** equivalen a aprobación académica integral. El ensayo docente debe comprobar legibilidad, carga horaria y continuidad N28→N29→N30.

## Correcciones incorporadas directamente a los PDF finales

En la p. 3 de ambos PDF se anuló sólo el relleno gris vertical no semántico, preservando retratos, texto, trazos y pie. Las páginas corregidas se renderizaron y revisaron visualmente. También se eliminó una coma huérfana al inicio del bloque de edición bibliográfica: en N28, «Fourth Edition» de Len Bass; en N29, «Second Edition» de Kent Beck. Las páginas 3 finales se renderizaron de nuevo y se revisaron visualmente. No queda copia candidata privada.

Los scripts de normalización tienen guardas de SHA y verifican antes de reemplazar el PDF canónico: número de páginas, geometría y anotaciones de **todas** las páginas; texto idéntico en todas salvo la supresión prevista de la coma en p. 3. La corrección del fondo conserva todo el texto. Se conservaron 38 y 39 páginas. Los deltas para una futura regeneración fiel desde fuente están en `pedagogy/source-overrides/referentes-paper-n28-n29.css` y `referentes-editions-n28-n29.md`.

Se actualizó la clave de caché de N28 y N29 en la portada, el atlas, crónicas y el manifiesto, manteniendo la misma ruta estable del PDF. Commit `0dcb158c0b1ed164fdccbc90aa2a1d12e25f73e7` en Git `main`; [Pages run 40750994662](https://github.com/carralbal/UBA-metsi/actions/runs/40750994662) terminó `success`. La auditoría `AUDITORIA-REMOTA-SHA-37-N-POST-N28-N29-20261028.json` del workspace confirmó **37/37 PDF byte idénticos** entre repo y Pages, incluyendo N28 SHA `4bd945eb9ccf76ec8c1f7bbf47d725e1b24791df0547a32dc74b98f1df979b3e` y N29 SHA `61343dbe70308840bb334c5e1a84a794e0345be1c9826bda4bfda103af2bf71b`. La auditoría paralela de portada confirmó 37/37 enlaces y las dos claves nuevas aparecen en el HTML remoto. Esto prueba publicación, no aval docente.

## Límites y siguientes controles

No se rehízo la edición completa desde HTML/activos: el acabado de la cubierta y la estructura accesible requieren el ensamble exacto de origen. Los deltas están documentados, pero la reproducción integral desde una sola fuente sigue pendiente. Tampoco se hizo lectura docente completa, prueba con lector de pantalla humano ni preprensa. Los renders temporales de QA se eliminan tras la comprobación remota.
