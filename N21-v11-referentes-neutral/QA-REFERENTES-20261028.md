# N21 · corrección de fondo en Referentes · 28/10/2026

## Hallazgo y alcance

La página 3 del PDF público tenía una franja gris vertical en la columna central,
originada por `linear-gradient` de `.authors-page` en el CSS heredado. N02 ya se
había normalizado a fondo paper. El mismo muestreo de p. 3 detectó fondos
centrales distintos de paper en otras lecturas; **este recibo sólo cierra N21**.

## Corrección reproducible

- Entrada: `site/pdf/publicados/N21-METSI-lectura-previa-v10-final.pdf`, 40 A4,
  SHA-256 `a32fb3327cc3081e7c0a655424390f63b715bb38a5ea78f8587f32d0f7d965ec`.
- Fuente editable: `index.html` y `edition.css` de este directorio; 253/253 IDs
  presentes. CSS corregido: fondo paper uniforme en `.authors-page`.
- Finalización del PDF: `scripts/normalize_n21_referentes_background_20261028.py`
  convierte en no-pintada **una** operación de fondo no semántica, con guarda
  de SHA, patrón y rectángulo. No refluyen texto ni páginas.
- Salida: mismo PDF público estable, SHA-256
  `fb21c41abcffb3e1fe4bb0a16b25f81ec8139141e73e61208e3b7c9a0ae68e45`.

## Comprobaciones realizadas

- 40/40 páginas y texto extraído idéntico en las 40.
- Raster a escala 0,35: **sólo la p. 3 cambia**. Se abrió la p. 3 a escala 1,6:
  fondo uniforme y ningún recorte/solape visible.
- 79/79 anotaciones equivalentes, 24/24 destinos declarados, árbol de
  estructura conservado y 9/9 descripciones `/Alt` presentes.
- Metadatos de título/autor/asunto inalterados.
- El índice p. 2, ejemplo numérico p. 18, pausa fotográfica p. 25,
  preparación p. 38 y referencias p. 39 se abrieron también a escala 1,6;
  sin colisiones visibles. La p. 25 conserva fotografía B/N a sangre.
- Se leyó el texto de las 40 páginas. El instrumento HH-21 y su única
  consigna p. 38 son coherentes; no surgió otra corrección de contenido.

No equivale a certificación de lector de pantalla, revisión docente real ni
arte de imprenta. La bibliografía antigua se usa como tradición teórica; la
referencia de Blank/Dorf 2020 se comprobó con Wiley y no es una edición nueva
de contenido, aunque la reimpresión sea de 2020.
