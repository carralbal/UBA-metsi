# Changelog breve, N01 v16

- Viudas y huérfanas: el generador aplica `orphans: 2` y `widows: 5`, con resguardos de bloque para los párrafos que Chromium no resolvía de manera estable. Las 28 transiciones fueron auditadas y no queda ningún resto de una a tres líneas al inicio de página.
- Orden de lectura: se desactivaron las capitulares flotantes de N01. En las páginas 10, 17 y 26, las cabeceras y los títulos preceden al cuerpo, y las palabras `En`, `No` y `La` se extraen completas.
- Glosario: las quince viñetas pasaron a posición interior, con tratamiento uniforme en las tres columnas. La distancia mínima medida respecto de los corondeles es 7,47 pt.
- Tapa: se agregó un refuerzo local del scrim sólo en la esquina superior izquierda. El contraste del eyebrow subió de 3,50:1 a 5,41:1; la geometría de todos los elementos de tapa quedó sin cambios.
- Arrastre del reflujo: el subtítulo “Ejemplo: una misma práctica, dos calidades metodológicas” se agrupa con su primer párrafo para impedir una huérfana secundaria.

## Verificación final

- PDF A4 de 29 páginas.
- Fuente académica byte por byte idéntica a v11 y v12.
- 49 controles integrales en estado PASS.
- Once URLs exactas en texto y anotaciones, con todos sus guiones preservados.
- Ninguna página ocupa menos de la mitad del campo útil. Mínimo medido: 52,9 %.
- SHA256: `c7f0508bb9f7f152a2637412c7b8e3f164f367b88aae1c81f484d02756d44855`.
