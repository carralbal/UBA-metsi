# Informe de corrección, N02 v11 a v12

## Resultado

La versión v12 resuelve los tres defectos indicados y pasa la guarda integral de regresión.

## Defecto 1. Ruta de lectura

Se eligió la salida A. En la fuente v12 se intercambiaron, sin reescritura, los bloques completos de Comprobación y Caso de transferencia. En `build_collection.py` se corrigió el mapeo de ruta de N02: 16 y 17 son PRUEBA, 18 es TRANSFERENCIA y 19 a 22 son PREPARACIÓN. El índice se regeneró con 17 Comprobación y 18 Caso de transferencia.

Criterio: **PASS**. Las 22 etiquetas forman seis tramos contiguos en el orden anunciado: cuatro PROBLEMA, seis DISTINCIONES, cinco DECISIONES, dos PRUEBA, una TRANSFERENCIA y cuatro PREPARACIÓN. Ninguna etiqueta reaparece.

## Defecto 2. Entrada de glosario huérfana

En el CSS de N02 dentro de `build_collection.py` se extendió la protección `break-inside` y `page-break-inside` al bloque completo del glosario, además de conservarla en cada entrada. La misma protección cubre las listas de píldoras y preguntas.

Criterio: **PASS**. Las 19 entradas del glosario quedan completas en p24. La medición pedida devuelve 387 caracteres en negrita de 8,8 puntos en p24 y cero en p25. P25 abre directamente con la sección 22.

## Defecto 3. Huecos en preguntas

En el CSS de preguntas de N02 dentro de `build_collection.py` se eliminó la grilla de tres filas de altura fija. La lista usa flujo de dos columnas balanceadas, con preguntas 1 a 3 a la izquierda y 4 a 6 a la derecha. Cada ítem conserva altura propia y margen inferior uniforme.

Criterio: **PASS**. Los cuatro espacios entre preguntas consecutivas miden 15,04 puntos, aproximadamente un interlineado y por debajo del máximo de dos interlineados.

## Diff contra v11

**PASS**. La v12 se reconstruye exactamente a partir de la v11 intercambiando los dos bloques autorizados. El inventario palabra por palabra es idéntico: 7.701 tokens en ambas versiones, sin adiciones, eliminaciones ni sustituciones. El HTML conserva 104 elementos de lista y la guarda visual de 53 viñetas.

La comparación visual detecta cambios sólo en p2 y p22 a p25. P1 y p3 a p21, además de p26 y p27, son idénticas a v11.

## Guarda de regresión

- **PASS, capitulares:** no existen glifos grandes aislados. Las tres aperturas copiables permanecen completas.
- **PASS, viudas:** la única continuación de texto queda entre p6 y p7, con ocho líneas en p7. El corte p23 a p24 de v11 desaparece como consecuencia directa del orden autorizado y no produce pérdida ni viuda.
- **PASS, registro:** cero voseo, cero segunda persona, cero `usted`; seis preguntas impersonales.
- **PASS, consigna:** conserva barra volt y la frase `dos de las seis preguntas`.
- **PASS, tapa:** eyebrow en dos líneas, sangrado, contraste y componentes intactos. P1 es visualmente idéntica a v11.
- **PASS, maqueta:** 27 páginas, 22 secciones con título y cuerpo juntos, índice 01 a 22 y dos entradas SIN NUM.
- **PASS, listas:** estructura idéntica a v11; 53 viñetas preservadas y cero colisiones visuales.
- **PASS, ocupación:** mínimo medido de 52,9 % en el cierre intencional; entre las páginas ordinarias, mínimo de 54,5 % en p15. P18 queda en 55,8 %, p25 en 69,6 % y p26 en 57,3 %.
- **PASS, URLs:** 15 enlaces de Referencias base y LinkedIn en las 27 páginas. Texto y anotaciones coinciden; todos los segmentos con guión permanecen enteros.
- **PASS, Checkland:** ISBN 978-0-470-02554-3 íntegro y sin URL de Wiley.
- **PASS, puntuación:** una sola raya, exclusivamente en el título oficial ISO. Ninguna en el cuerpo.
- **PASS, limpieza:** sin TBD, lorem, XXX ni corchetes de producción.
- **PASS, activos:** las 21 imágenes tienen hashes idénticos a v11.

## Llenado de las 27 páginas

P1 a p27: 89,6; 82,5; 68,7; 89,6; 89,6; 87,1; 87,5; 76,9; 84,3; 86,9; 83,7; 81,2; 87,5; 79,5; 54,5; 89,6; 74,8; 55,8; 87,7; 85,8; 87,7; 86,9; 85,4; 83,9; 69,6; 57,3; 52,9 %.

## Archivo entregado

- Nombre: `N02-METSI-lectura-previa-v12-final.pdf`.
- Tamaño: 28.141.291 bytes.
- Modificación: 2026-09-02 20:57:35 -03.
- SHA256: `f71e9af144610cc12cd30b2c52f99437a58e35dc08d5564f9bb7da1e291b6cb0`.
- Es una exportación nueva desde la fuente v12. No es una copia renombrada de v11.
