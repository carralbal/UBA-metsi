# Auditoría visual final de N01 v15

Resultado: **PASS**.

Se inspeccionaron las 29 páginas en hoja de contacto y la tapa en resolución de 180 dpi y en Preview.

- Tapa: el scrim oscuro llega de forma continua a los cuatro bordes. El corte horizontal del pie desapareció; su salto de luminancia pasó de 30,853 en v14 a 0,322 en v15.
- Densidad: el último valor oscuro del degradado se prolonga hasta el borde inferior. No se estiró la foto ni se agregó una banda opaca sobre el texto.
- Eyebrow: Vista Previa selecciona «LECTURA PREVIA» y «EDICIÓN 2026» como líneas completas, consecutivas y sin caracteres intercalados. El PDF contiene exactamente dos runs de texto, uno por línea.
- Composición: logotipo, bloque N01, paralelogramo volt, círculo, cita, kicker, título de tres líneas y pie conservan posición y tamaño.
- Páginas 2 a 29: comparación raster píxel por píxel idéntica a v14.
- URLs: las once conservan destino y texto exactos; `eur-lex`, `wp-content` y `bodies-of-knowledge/software-engineering` permanecen enteros.
- Cierre: fósforos, folio, pie, leyenda y texto alternativo preservados.

Activos: `qa/N01-contact-sheet.jpg`, `qa-report.json` e `integrity-report.json`.
