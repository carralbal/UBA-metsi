# Recibo QA · N19 post-Cecilia · 27/10/2026

## Alcance y decisión

**Aprobado técnicamente para publicación digital, pendiente de verificación remota.** No se declara validación académica ni preprensa. La variante privada v17 de 37 páginas fue rechazada porque perdía contenido del PDF público; se construyó una fusión desde la fuente fiel pública, no desde ese PDF incompleto.

## Integridad curricular

- 301/301 `data-source-id` públicos permanecen con el mismo texto. Se agregaron 10 bloques para el caso de compra y uno para la preparación, total 312 visibles.
- El caso público de alertas/tutorías queda intacto; la compra se suma tras él. Hay una consecuencia de carga: la lectura pasa de 38 a 40 páginas. La ruta de núcleo deberá contrastarse con alumnos/docentes; no es evidencia de que entre cómodamente en 120 minutos.
- La comparación económica didáctica es aritméticamente consistente: Alfa USD 7.400 en costos conocidos del primer año; Beta USD 2.700 pero excluida por historial; Gamma USD 8.400. Evaluación ponderada sobre 5: Alfa 3,75; Gamma 4,35. Recomendación condicional, sin adjudicación.

## Integridad editorial y técnica local

- PDF final: `site/pdf/publicados/N19-METSI-lectura-previa-v10-final.pdf`, 23.265.872 bytes, SHA-256 `0f5414faa83c9a2f622995af420f09f43d3e8ff48cc833d1728981aba60f6054`.
- 40 páginas A4, abiertas con `PdfReader(strict=True)`; 21 destinos y 21 números de índice cotejados con las páginas efectivas; 22 anotaciones en el índice. Etiquetado `/StructTreeRoot` conservado. Cero caracteres fuera del área de página y ninguno inferior a 5 pt en páginas con texto. La portada es una imagen sin caracteres extraíbles, por diseño.
- El flujo de la portada final es idéntico al de la portada pública anterior (`sha256` de contenido `9a02650f3130800f26d4829463100c933ee9189e9914dde4ea6afecfcb6e99fc`). Acabado de borde aplicado a pp. 4, 5, 27 y 40.
- Se abrieron cuatro planchas que cubren visualmente 40/40 páginas; se ampliaron pp. 23–26 con el caso agregado. Fotos monocromas, sin caja paper en apertura ink. Se eliminó la franja gris decorativa de Referentes. Render HTML: 312 bloques visibles, sin imágenes faltantes.
- La biblioteca emitió un aviso no fatal de `FontBBox` en la inspección; `pypdf` estricto, `pdfplumber` y el render visual pudieron abrir el documento. No se observó desborde por ese aviso.

## Pendientes externos

Verificar GitHub Pages, HTTP, bytes y SHA remoto tras el push. Obtener revisión académica, ensayo de carga de lectura, accesibilidad humana y prueba de impresión antes de llamar la edición «definitiva» para todo uso.
