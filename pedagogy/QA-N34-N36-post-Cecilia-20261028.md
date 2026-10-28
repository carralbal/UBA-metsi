# N34–N36 · cotejo post-Cecilia y corrección editorial directa

Fecha: 28/10/2026. Alcance: edición digital para pantalla; **no** aprobación docente integral, lector de pantalla humano ni preprensa.

| N | PDF canónico de ruta estable | Páginas | SHA anterior | SHA corregido local |
| --- | --- | ---: | --- | --- |
| N34 | `site/pdf/publicados/N34-METSI-lectura-previa-v10-final.pdf` | 39 | `aed35d5fd6bd43d7f2ab3eff4a57b8cc379cf3d91dbc9aeb93006142b903dc66` | `543951a22de1dc3a93e6ebea8f2686d59f08ee7228e7f42c77ed3f9ee95bef70` |
| N35 | `site/pdf/publicados/N35-METSI-lectura-previa-v10-final.pdf` | 40 | `6a9d52f9c6b16c538e52896bc3381b6ce148e3f6120216b5fb413243a79c26d2` | `3eade973d02eb5a6275f4ebf45c6849289274da27f081540479f4cd394344ca1` |
| N36 | `site/pdf/publicados/N36-METSI-lectura-previa-v10-final.pdf` | 41 | `31cb648d61dfb78a635b5d34947960629e05f28d662296b7b64a8b4eb2484a18` | `1c6980394675993aea8a51b736f2f23ddb6c2ae96130608c81f55ee9bc781f33` |

## Fuente fiel y sustancia curricular

- **N34**: fuente `work/UBA-metsi-publication/output/source-recovery-20261020/N34-art-v5-working/`; recibos `pedagogy/N34/QA-DIGITAL-v5b-20261024.md` y `PUBLICACION-DIGITAL-v5b-20261024.md`. La revisión anterior de 39/39 páginas y 258/258 bloques se conserva. Cotejo focal: p. 23 contiene expediente de doce campos, incluyendo origen pedido u oportunidad, prefactibilidad, autoridad, compra, requisito→modelo→aceptación, operación y revisión; p. 25 fuerza a reconstruir una decisión bajo cambio de condición; p. 26 propone un expediente trabajado. No agregar otra ficha que repita los mismos campos.
- **N35**: fuente `N35-art-v2-working/N35/`, recibos `pedagogy/N35/QA-DIGITAL-v2c-20261024.md`, `COTEJO-SEMANTICO-LAMINA-P23-20261024.md`, `PUBLICACION-DIGITAL-v2c-20261024.md`. El recibo de publicación **posterior** al QA privado confirma que la lámina p. 23 sí pasó cotejo semántico y fue publicada: expone una falta de autoridad disponible, no inventa una atribución de la recepción tercerizada. En p. 26 hay doce campos de audiencia, evidencia, objeción y transferencia; p. 28 compara dos mensajes con el mismo límite, y p. 36 pide dos explicaciones con la misma restricción material. Las 40 páginas y 272 bloques históricos se conservan. Un ensayo docente con tiempo sigue pendiente, pero no invalida el cotejo ya hecho.
- **N36**: fuente `N36-art-v4-working/N36/`, recibos `pedagogy/N36/QA-DIGITAL-v4c-20261024.md`, `COTEJO-SEMANTICO-LAMINAS-P23-P36-20261024.md`, `PUBLICACION-DIGITAL-v4c-20261024.md`. El recibo posterior al QA privado confirma cotejo semántico y publicación de ambas láminas. P. 23 no atribuye causalidad al mejor turno: distingue información compartida y coordinación anticipada como mecanismos a observar; p. 36 separa reconstruir, contrastar, decidir, practicar y volver a observar, con un solo producto. P. 27 distingue evidencia disponible antes de la decisión y conocimiento posterior. Las 41 páginas y 286 bloques históricos se conservan. No pegar el guion docente D-1/O-1 como capítulo.

## Corrección exacta en el PDF final

Las tres p. 3 «Referentes» exhibían la misma franja gris de centro en `paper`, un relleno heredado del rectángulo `[0,2336,794,1123]`. `scripts/normalize_n34_n36_referentes_20261028.py` exige SHA y estructura esperada y anula **sólo** esa operación de relleno en cada PDF final; no recompone la página ni crea copia privada retenida. Verificó texto, anotaciones, geometría y estructura etiquetada en **39/39**, **40/40**, **41/41** páginas, y que los streams de las demás páginas no cambiasen. Las tres p. 3 se renderizaron a 1800 px y se inspeccionaron: fondo uniforme, seis retratos y pie de página íntegros. Los deltas de fuente se registran en `pedagogy/source-overrides/referentes-paper-n34-n36.css`; no se editó el checkout histórico con trabajo preexistente.

Se mantienen rutas públicas; cambiaron sólo claves de caché a `n34-editorial-20261028`, `n35-editorial-20261028`, `n36-editorial-20261028` en portada, manifiesto, atlas y crónicas. Commit `11e5060e8530d2fd7f58c9dbca43f37d306e6b0c` en `origin/main`; Pages run `40758508820` terminó `completed/success`. `AUDITORIA-REMOTA-SHA-37-N-POST-N34-N36-20261028.json` comprobó **37/37 PDF byte idénticos**, incluidos N34–N36; `AUDITORIA-ENLACES-SITIO-37-N-POST-N34-N36-20261028.json` comprobó **37/37 rutas** de la portada. Los nueve PNG efímeros de QA N34–N36 se retiraron después del SHA. No quedó PDF candidato privado.

## Límites

Esto no equivale a una regeneración integral autocontenida, ni a revisión docente de todo N00–N36. Faltan ensayo de carga/tiempo del cuatrimestre, lector de pantalla humano y preflight de imprenta. El cotejo puntual de láminas de N35/N36 está cerrado según sus recibos; el desempeño de esas láminas en una clase real aún no está probado.
