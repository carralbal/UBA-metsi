# Recibo QA · N14 post-Cecilia · 27/10/2026

## Estado

**Versión digital publicada y cotejada byte a byte con GitHub Pages.** No es aprobación académica ni prueba de imprenta.

## Integridad y contenido

- Fuente pública anterior: 307 IDs. Fuente final: 314 IDs; los 307 anteriores conservan su texto y siete nuevos dan el ejemplo AS-IS/TO-BE y la práctica. El caso hospitalario público no fue reemplazado.
- La misma ficha visual de seis personajes aparecía cuatro veces en N14. Se dejó una primera aparición y se retiraron las otras tres; cada aplicación conserva su prosa distinta. La operación no toca bloques con ID.
- Caso ficticio: línea de base dirigida 24/60 consultas y 16/24 vinculadas al estado prematuro; no se atribuye causalidad ni se inventa un resultado TO-BE. `Requiere acción` exige aviso entregado, no sólo generado. La infografía privada incompleta no se integró.
- Paquete editable: `index.html`, nueve CSS en total y 25 recursos usados. Reimpresión desde el paquete: 314 bloques visibles, cero imágenes faltantes, 46/46 páginas con texto normalizado idéntico a la etapa HTML candidata.

## PDF

- PDF candidato: `N14-post-cecilia-20261027/fullbleed-v6/N14-METSI-fullbleed-editorial-A4.pdf`, 46 páginas A4, SHA-256 `b6564dee1e73d27514431e0b802bafedb635a8c0318ff49c2b52737c9453a5b8`.
- Ensamblado: `PASS_MACHINE_CHECKS_PENDING_VISUAL_REVIEW`; portada preservada (stream, texto, cajas y píxeles idénticos). 31 destinos, 49 enlaces internos y 88 enlaces URL, cero errores de navegación. Las 31 etiquetas del índice coinciden con sus destinos reales. `/StructTreeRoot` preservado y `PdfReader(strict=True)` abre las 46 páginas.
- Acabado de pantalla a borde en pp. 4, 5, 20 y 46; texto buscable anterior y posterior idéntico por página. `pdfplumber`: cero caracteres fuera de página y cero fuentes menores a 5 pt. Dos avisos `FontBBox` no fatales durante el acabado; el archivo abre y renderiza.
- Cinco planchas de contacto cubren visualmente 46/46 páginas; se abrieron las cinco. Se abrió además p. 14 ampliada tras quitar un panel repetido y p. 33 ampliada con el nuevo caso; no se observaron cortes, solapamientos ni pies invadidos. Fotografía interior en blanco y negro. El ejemplo comienza en página nueva y cabe completo.

## Publicación y pendiente

- Commit de contenido `52720a2c913d8f72db2277a65fc9a1892d7c8131`, empujado a `main` desde el worktree de release. GitHub Pages run `40603655860` terminó con `success` para ese mismo commit.
- PDF público: `https://carralbal.github.io/UBA-metsi/pdf/publicados/N14-METSI-lectura-previa-v10-final.pdf?v=n14-asis-tobe-post-cecilia-20261027-verified`.
- Copia remota descargada después del despliegue: 20.570.725 bytes, 46 páginas A4, SHA-256 `b6564dee1e73d27514431e0b802bafedb635a8c0318ff49c2b52737c9453a5b8`, idéntico al PDF local. Una descarga anterior al fin del despliegue devolvía el blob previo; no se usó como evidencia de cierre.
- Sigue pendiente ensayar la carga de 120 minutos con docentes y contrastar la modelización formal de N16. Validación humana de accesibilidad y preprensa quedan fuera de este recibo. La infografía privada AS-IS/TO-BE de N14 no se publicó porque omite la rama de baja y la respuesta de la persona.
