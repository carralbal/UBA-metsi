# N07–N09 · Referentes con paper uniforme en los PDF canónicos

Fecha: 28/10/2026. Alcance: edición digital para pantalla, sin aprobación docente, prueba humana de accesibilidad ni preprensa.

| Lectura | Páginas | SHA anterior | SHA final local |
| --- | ---: | --- | --- |
| N07 | 35 A4 | `5b7aad77ef7b02e4d5bdd077e56fa90f756a433d808b5e5ccd4e150a3f84b4e6` | `2dc7d65ef167f84814d327c13ad5c29ebe1d593d0b28d6c0487b7c7ab2ac3df9` |
| N08 | 34 A4 | `b871223c07c181978b7dda29b23300db75bcd275de15ea157d815a640f0b9322` | `b15c8eabdc3f923eb316dde4646330db0ce3dd55ff85a3b2d9199698301d4a22` |
| N09 | 32 A4 | `df01487035f846cbb2a03f88dc890de390c36b5db4c3664252a134b8f6c5c24a` | `0c9bf5ad6e77438f299ef7c8d351c8d9311d4f177410e66360c1467383ed8f48` |

## Procedencia y sustancia conservada

- N07 tiene QA digital histórico `work/UBA-metsi-publication/pedagogy/N07/QA-DIGITAL-v4-20261024.md`: 35/35 páginas y 276/276 bloques visibles para el SHA anterior. Su fuente recuperada exacta está en `output/source-recovery-20261024/N07-imac-source-private/working/N07/` del checkout histórico. La comparación post-Cecilia se consigna en el inventario: entrevista sin inducir respuesta, contraste con trabajo observado y trazabilidad del problema.
- N08 fue recompuesto tras Cecilia con un caso de entrada proactiva desde la observación, sin tarea extra; `N08-v12-post-cecilia/QA-POST-CECILIA-20261027.md` registra 34/34 páginas y 280 bloques. Su fuente editable versionada `N08-v12-post-cecilia/standard-v7.css` incorpora ahora el fondo uniforme de Referentes para una recompaginación posterior. El contenido de la nueva página 25 no cambió.
- N09 tiene QA digital histórico `work/UBA-metsi-publication/pedagogy/N09/QA-DIGITAL-v2-20261024.md`: 32/32 páginas, 274/274 bloques y fuente fiel en `output/source-recovery-20261024/N09-imac-source-private/working/N09/`. El sitio tenía una etiqueta heredada errónea de «33 páginas»; se corrigió a **32** sin alterar el PDF.

## Cambio delimitado y prueba

La p. 3 de cada PDF mostraba una banda vertical gris heredada `[0,2336,794,1123]`. `scripts/normalize_remaining_referentes_20261028.py`, guardado por SHA exacto, neutralizó **solamente** esa pintura directamente en los PDF finales; no creó copia privada persistente. Se exigieron páginas idénticas en cantidad; texto, anotaciones, geometría y estructura etiquetada conservados en 35/35, 34/34 y 32/32. Todos los streams de las otras páginas son idénticos. Se renderizaron y abrieron las tres p. 3 antes y después: fondo uniforme, retratos, bibliografía y pies íntegros, sin recortes. Para N07/N09 existe `pedagogy/source-overrides/referentes-paper-n07-n09.css` a aplicar a su fuente recuperada sin tocar el checkout histórico con cambios preexistentes.

Claves de caché nuevas en las cinco superficies web: `n07-editorial-20261028`, `n08-editorial-20261028`, `n09-editorial-20261028`.

## Publicación

Pendiente al redactar: commit, run de Pages, 37/37 SHA remotos y 37/37 enlaces. Completar con recibo antes de retirar las seis capturas PNG temporales.
