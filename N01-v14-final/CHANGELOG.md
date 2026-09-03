# Changelog breve, N01 v14

- Tapa, eyebrow: cada línea se consolidó como una cadena PDF real, con tracking tipográfico mediante espaciado de caracteres. Vista Previa devuelve «LECTURA PREVIA» y «EDICIÓN 2026» completas, consecutivas y sin intercalado.
- Tapa, fondo: se recuperó la densidad visual exacta de v12 en todo el campo aprobado y se extendió únicamente el patrón oscuro hasta el borde derecho. La composición, el oscurecimiento y la posición de todos los elementos permanecen intactos.

## Verificaciones de regresión

- PDF A4 de 29 páginas.
- Fuente académica byte por byte idéntica a v12.
- Once URLs verificadas en texto y anotaciones; todos los guiones permanecen intactos.
- Ninguna página ocupa menos de la mitad del campo útil. Mínimo medido: 52,9 % en la página de cierre.
- Comparación raster completa contra v13: sólo cambió la página 1. Las páginas 2 a 29 son idénticas.
- Comparación de tapa contra v12: el campo original es idéntico; sólo cambia la franja que antes dejaba una costura en el borde derecho.
- QA integral: todos los controles PASS.
- SHA256: `9e7eb615f4172a4962e77bfc8ce8dcb346be2a3d9ab836f1356952639ccf99da`.
