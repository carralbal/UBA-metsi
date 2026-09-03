# Informe de corrección, N02 v12 a v13

## Cambio aplicado

Se usaron las dos palancas. En `build_collection.py`, el glosario N02 se divide en dos listas de impresión sin alterar su fuente: las primeras 13 entradas quedan en p24 y las seis finales pasan completas a p25 en tres columnas. La separación de preguntas se fijó en 13 mm y la altura mínima rígida del panel se eliminó.

No se usó la salida de emergencia.

## Criterios de aceptación

- **PASS, p25:** 74,15 % de llenado; el contenido termina en y=598,23 pt.
- **PASS, p24:** 92,54 % de llenado.
- **PASS, documento:** las 27 páginas superan el 50 % de ocupación rasterizada; mínimo 52,9 %.
- **PASS, preguntas:** cuatro separaciones de 38,14; 37,46; 38,14 y 37,46 pt.
- **PASS, listas:** p25 continúa con seis entradas completas; ninguna entrada se divide ni queda aislada.
- **PASS, panel:** termina 12,72 pt después del último elemento, por debajo del máximo de 30 pt.

## Diff contra v12

- Fuente v12 y v13: byte a byte idénticas, SHA256 común `71ff4a73dd4dc64c7e27b2c0a4410cba0926cf1588e63d588663ea087d9141a6`.
- Recuento de control provisto: 8.548 palabras en ambas versiones.
- Extracción normalizada del PDF sin pies: 8.514 tokens en ambas; inventario idéntico y similitud secuencial 0,998708. La diferencia de orden se limita a once tokens reubicados por el flujo en columnas, sin altas, bajas ni sustituciones.
- Comparación visual: sólo cambian p24 y p25.

## Guarda de regresión

- **PASS:** ruta monótona y secciones 17 y 18 en el orden aprobado; índice coherente.
- **PASS:** 19 entradas de glosario, con 387 caracteres fuertes en 8,8 pt repartidos 256 en p24 y 131 en p25.
- **PASS:** cero capitulares aisladas, cero letras sueltas y copia íntegra de las tres frases controladas.
- **PASS:** única continuidad de párrafo p6 a p7, con ocho líneas; Síntesis completa en p23.
- **PASS:** registro impersonal, seis preguntas y consigna con «dos de las seis preguntas».
- **PASS:** tapa, eyebrow, contrastes, sangre y composición sin cambios.
- **PASS:** 27 páginas A4, 22 títulos con cuerpo en la misma página, índice 01 a 22, dos SIN NUM. y 53 viñetas.
- **PASS:** las 15 URLs externas y LinkedIn siguen coherentes entre texto y anotaciones. p26 es visualmente idéntica a v12, por lo que se conservan todos los saltos aprobados y todos los guiones.
- **PASS:** ISBN 978-0-470-02554-3 entero y Checkland sin URL de Wiley.
- **PASS:** sin TBD, lorem, XXX ni corchetes; sólo permanece la raya del título oficial ISO/IEC/IEEE 15288:2023.
- **PASS:** revisión de los 27 topes de página, sin nuevas viudas, listas aisladas ni títulos huérfanos.

## Artefacto nuevo

- Archivo: `output/N02-METSI-lectura-previa-v13-final.pdf`
- Tamaño: 28.141.675 bytes.
- Modificación: 2026-09-02 22:37:25 -03.
- SHA256: `9c2698a1bd611cd7e51447f67c172ae5983f24ea0b3b40efcf9882bb4494386a`.
- Confirmación: PDF generado de nuevo desde la fuente, no es una copia renombrada.
