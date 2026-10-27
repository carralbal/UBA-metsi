# Recibo QA · N17 post-Cecilia · 27/10/2026

## Estado

**Edición digital publicada y verificada contra el archivo remoto.** No es una aprobación académica ni una prueba de imprenta.

## Evidencia de integridad

- Fuente pública fiel: 316 IDs. Fuente final: 325 IDs; los 316 originales conservan su texto y nueve bloques nuevos hacen visible prefactibilidad y práctica. La versión privada que sustituía el caso hospitalario no se promovió.
- Render HTML: 325 bloques visibles, ninguna imagen faltante. 45 páginas A4 ensambladas sin hojas en blanco retiradas. Portada idéntica al flujo de contenido del PDF público anterior.
- PDF final: `site/pdf/publicados/N17-METSI-lectura-previa-v10-final.pdf`, 25.757.376 bytes, SHA-256 `dc53ea612e32ec35771703d2054f88fb81719b2aa5141fff4ef811ddad5bccfa`.
- Publicación: commit `c4df1c9a2c1a126dd8d492b691795a2d383521e7`; GitHub Pages run `40599660159` terminó en `success`. La URL pública respondió HTTP 200, devolvió 25.757.376 bytes y el SHA-256 descargado coincidió exactamente con el PDF final local: `https://carralbal.github.io/UBA-metsi/pdf/publicados/N17-METSI-lectura-previa-v10-final.pdf?v=n17-prefact-post-cecilia-20261027`.
- `PdfReader(strict=True)` abre 45 páginas, 26 destinos de índice y 27 anotaciones en el índice; 26/26 números de página se cotejaron con sus destinos. `/StructTreeRoot` preservado. `pdfplumber` no detectó caracteres fuera de los bordes ni fuentes menores a 5 pt. Avisos no fatales de trailer/FontBBox no impidieron abrir ni renderizar el PDF.
- Cinco planchas finales se abrieron y cubren 45/45 páginas; se ampliaron la nueva p. 32, el caso hospitalario p. 33 y la preparación p. 43. La banda gris vertical decorativa de Referentes fue retirada; fotografía interior observada en blanco y negro. Acabado a borde aplicado en pp. 4, 5, 26 y 45.

## Límite pendiente

Ensayar carga de 120 minutos con docentes y alumnos, revisión académica, accesibilidad humana y preprensa antes de llamarlo edición definitiva en esos sentidos.
