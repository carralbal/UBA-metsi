# Changelog breve, N01 v13

- Tapa, eyebrow: «LECTURA PREVIA» y «EDICIÓN 2026» se construyen dentro de un único nodo textual, en dos líneas consecutivas, con tracking tipográfico. Preview devuelve ambas cadenas completas y en orden.
- Tapa, fondo: se diagnosticó el caso A. La fotografía ya llegaba a sangre, pero la matriz del patrón oscuro conservaba el ancho de 540 puntos de la caja original. La matriz se escaló junto con la tapa, sin cambiar color ni opacidad, y la costura vertical desapareció.

## Verificaciones de regresión

- PDF A4 de 29 páginas.
- Fuente académica byte por byte idéntica a v12.
- Once URLs verificadas en texto y anotaciones; todos los guiones permanecen intactos.
- Ninguna página ocupa menos de la mitad del campo útil. Mínimo medido: 52,9 % en la página de cierre.
- Comparación raster completa contra v12: sólo cambió la página 1. Las páginas 2 a 29 son idénticas.
- QA integral: todos los controles PASS.
- SHA256: `3cbf2dee6e8f785e91466f8e08509f730419ce71fedd6642c5e15f464ae192e3`.
