# N26 y N27 · cotejo post-Cecilia y corrección editorial directa

Fecha: 28/10/2026. Alcance: lectura digital en pantalla; **no** certificación docente integral ni preprensa.

## Versiones que se revisaron

| Lectura | PDF público estable | Páginas | SHA-256 previo | SHA-256 corregido |
| --- | --- | ---: | --- | --- |
| N26 | `site/pdf/publicados/N26-METSI-lectura-previa-v10-final.pdf` | 37 | `7afc9844649c6fb0c539492d74533ea1104de3519181ed02b570504ee54dd1b5` | `51376c2c238cefeb696190964d9e26745987446cc233b1773f630037da935e7d` |
| N27 | `site/pdf/publicados/N27-METSI-lectura-previa-v10-final.pdf` | 38 | `57e6ec1d38753a0b2613322bbc3b9af6d27a931e7a89e53a09d91fab004893ea` | `f86a80e18a873405d16631687b3c5ce7d65799f822c8dab31a7677330d6fbbe1` |

Ambos SHA previos coinciden con los recibos históricos `work/UBA-metsi-publication/pedagogy/N26/QA-DIGITAL-v3b-20261024.md` y `.../N27/QA-DIGITAL-v7b-20261024.md`. Las fuentes fieles de estas ediciones están en el checkout histórico `output/source-recovery-20261020/N26-art-v3/working/N26/` y `N27-art-v7/working/N27/`; no regenerar desde un paquete `v10` sin comprobar identidad. El parche directo de una operación no semántica se reproduce con `scripts/normalize_n26_n27_referentes_background_20261028.py`; el equivalente editable está en `pedagogy/source-overrides/referentes-paper-n26-n27.css`. No se retuvo copia candidata privada.

## Revisión curricular focal

- **N26**: barrido visual de 37/37 páginas y lectura concentrada de pp. 24–25, 27 y 34–35. El instrumento HH-26 hace doce preguntas ligadas a una sola promesa: capacidades antes que aplicaciones, servicios internos y terceros, autoridad, confianza, señales, contingencia, reparación, dependencia compartida y salida. P. 27 propone prueba controlada de demora de identidad y condición de accesibilidad, y separa falla de mapa, acuerdo y capacidad. La preparación p. 34 exige otro servicio, un tercero, una decisión manual, una frontera de confianza y una alternativa limitada. Ya existe sustancia metodológica suficiente para **no** agregar otra consigna. No se presenta como adjudicada la compra condicional de N19.
- **N27**: barrido visual de 38/38 páginas y lectura concentrada de pp. 25–27 y 35–36. HH-27 estructura un contrato de forma, significado, vigencia, condiciones, efectos, invariante, reintento, permisos, evolución y respuesta del turno. La ficha didáctica p. 26 conserva O-042/M-042 y diferencia el mensaje repetido del tardío: 14:02 a 14:19 son 17 minutos; un bloqueo de 14:05 impide restaurar «asignable». P. 27 ensaya simultaneidad, pérdida de respuesta, retraso, consumidor antiguo y permiso revocado sin afectar casos reales. La preparación p. 35 pide una sola ficha y dos pruebas. No falta otro instrumento de contrato.
- Se cotejó en fuente oficial la existencia de [OpenAPI 3.2.0](https://spec.openapis.org/oas/v3.2.0.html), [AsyncAPI 3.1.0](https://www.asyncapi.com/docs/reference/specification/v3.1.0) y el [FinOps Framework 2026](https://www.finops.org/framework/). Su presencia no convierte a la bibliografía completa en aprobada por docentes. Las referencias históricas de base no son, por sí mismas, una indicación de actualidad metodológica.

## Corrección editorial incorporada a los PDF finales

Ambas páginas 3 de «Referentes» tenían la banda gris vertical heredada, inconsistente con la página ya corregida de N21. Se anuló **un único relleno de fondo no semántico** en cada PDF. Antes de sustituir el archivo público se verificó: mismo número de páginas, texto extraído idéntico en todas (37/37 y 38/38), anotaciones idénticas por contenido (101 y 123), 31 y 30 destinos internos conservados, geometría idéntica, árbol estructural presente y flujos de contenido idénticos en todas las páginas salvo p. 3 (36/36 y 37/37). Las pp. 3 corregidas se renderizaron y abrieron a tamaño grande: retratos, textos, reglas y pie siguen intactos; sólo desaparece la banda. El barrido de las demás páginas no detectó un defecto nuevo que justificara recomposición.

Se actualizó la clave de caché de N26 y N27 en la portada, el atlas, crónicas y el manifiesto, manteniendo **la misma ruta estable** del PDF. Los archivos temporales de render se eliminan después de la verificación remota.

## Límites y próximos controles

La revisión focal no equivale a lectura académica completa por docentes ni a prueba de clase cronometrada. N27 pp. 25–27 usa una ficha que continúa entre páginas: legible en la revisión visual, pero conviene observarla con lectores reales. Quedan pendientes lector de pantalla humano y preprensa. El ensayo docente debe probar N19→N26→N27 en un bloque enseñable, no sumar entregables. Verificar publicación de GitHub Pages y SHA remoto de **ambos** PDFs antes de dar por cerrado el cambio en producción.
