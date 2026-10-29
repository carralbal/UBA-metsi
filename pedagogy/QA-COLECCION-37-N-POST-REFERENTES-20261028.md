# METSI · barrido de la colección digital N00–N36

**28/10/2026. Resultado técnico para pantalla; no es aprobación académica,
certificación PDF/UA ni preprensa.**

Se auditó el manifiesto completo: **37 PDF y 1.435 páginas A4**. La auditoría
geométrica buscó palabras fuera de hoja, colisiones y folios interiores
sospechosamente vacíos. Marcó sólo N32 p. 9: el extractor interpreta como
solapados dos pares de número/rótulo. Se abrió a 1400 px y son legibles y
separados; no se cambió una composición válida por una alerta automática.

La auditoría estructural encontró **37/37** con árbol de etiquetas, bandera
`/Marked`, idioma de documento y anotaciones de enlace. Esto no demuestra
orden de lectura correcto, alt útil, contraste ni experiencia con VoiceOver.

Las 37 páginas 3 de Referentes recibieron fondo paper uniforme; los controles
por lote preservaron texto, enlaces, geometría y etiquetas. Los informes
anteriores `AUDITORIA-REMOTA-SHA-37-N-HEAD-93e7a34-20261028.json` y
`AUDITORIA-ENLACES-SITIO-37-N-HEAD-93e7a34-20261028.json` comprobaron 37/37
PDF byte idénticos y 37/37 enlaces/revisiones. Después de ese corte sólo
cambiaron N11 y N21, en la página 3 de Referentes: su [QA puntual](QA-LEGIBILIDAD-N11-N21-20261028.md)
acredita las guardas internas y los dos SHA públicos exactos tras Pages run
`40790739864` `success`. Los otros 35 PDF no cambiaron entre ambos cortes.

Una nueva auditoría de tamaño de lectura sobre las 37 piezas encuentra texto
interior modal de 11 pt redondeados en N01–N36 salvo N11 (10,5) y N21 (11,5);
N00 usa 10 pt. Las páginas compactas bajo 10 pt son mapas o aparatos de
referencia puntuales en N00, N02, N11 y N29. Esto es triage, no juicio de
lecturabilidad humana. El [informe detallado](../AUDITORIA-TIPO-LECTURA-37-N-POST-LEGIBILIDAD-20261028.json)
se genera con `scripts/audit_37_reading_type_20261028.py`.

No quedaron PDF nuevos privados persistentes. Los renders y PDFs temporales
se eliminaron después de comprobar el resultado público.
