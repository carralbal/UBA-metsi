# Changelog breve, N01 v15

- Tapa, scrim inferior: se eliminó el corte horizontal que aclaraba la franja del pie. El último tramo oscuro del degradado se prolonga ahora hasta el borde inferior sin repetir su franja inicial.
- Tapa, composición: foto, encuadre, título, kicker, cita, marcas, eyebrow, folio y pie permanecen en la misma posición y con la misma geometría de v14.

## Verificaciones de regresión

- PDF A4 de 29 páginas.
- Fuente académica byte por byte idéntica a v12.
- Once URLs verificadas en texto y anotaciones; todos los guiones permanecen intactos.
- Ninguna página ocupa menos de la mitad del campo útil. Mínimo medido: 52,9 % en la página de cierre.
- Comparación raster completa contra v14: sólo cambió la página 1. Las páginas 2 a 29 son idénticas.
- El salto horizontal medido en el pie bajó de 30,853 a 0,322 niveles de luminancia.
- QA integral: todos los controles PASS.
- SHA256: `9837fb05e82fc7b6d000bf3105e8420044970906cf637c75a7868968de2c5c01`.
