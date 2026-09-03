# Changelog breve, N01 v12

- Páginas 11 y 12: el subtítulo y el párrafo del ejemplo pasan completos a la página 12. Ya no queda una palabra aislada al comienzo de página.
- Página 27: el encabezado y el título de «Cinco píldoras para recordar» preceden a los cinco ítems en la capa de lectura. El aspecto visual permanece idéntico.
- Página 10: se eliminó del SVG y de la capa de texto la etiqueta residual «se apoya en». Las seis cajas y sus descripciones permanecen intactas.
- Tapa: «LECTURA PREVIA» y «EDICIÓN 2026» se construyen como dos elementos de texto completos y consecutivos, con tracking tipográfico. La comparación raster contra v11 da cero píxeles diferentes.

## Verificaciones de regresión

- PDF A4 de 29 páginas.
- Fuente académica byte por byte idéntica a v11.
- Once URLs verificadas en texto, capa de copia y anotaciones clickeables; todos los guiones permanecen intactos.
- Ninguna página ocupa menos de la mitad del campo útil. Mínimo medido: 52,9 % en la página de cierre.
- Comparación raster completa: sólo cambiaron las páginas 11 y 12. Las otras 27 son idénticas a v11.
- QA integral: todos los controles PASS.
- SHA256: `4bafaf254e3b734260b82f720fecebdbd0e76d9462a0fe5988761e7a2cc2a706`.
