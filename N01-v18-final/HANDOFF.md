# Handoff autosuficiente, N01 v18 final

## Estado

N01 v18 está compuesto, exportado y validado contra la fuente canónica final del Bloque 1. La sincronización incorpora HH-01 y su continuidad con N02. Las versiones v8 a v17 permanecen congeladas. La identidad consignada abajo corresponde al PDF vigente después de la auditoría transversal de tapas del 4 de septiembre de 2026; esta actualización documental no constituye una nueva aprobación autoral.

## Entregables

- PDF final: `output/N01-METSI-lectura-previa-v18-final.pdf`
- Fuente canónica empaquetada: `source/N01_metodologia_sin_recetas-content-final.md`
- HTML editable: `index.html`
- Hoja de estilos: `magazine.css`
- Informe de integridad: `integrity-report.json`
- Informe PDF: `qa-report.json`
- Auditoría visual: `visual-audit.md`
- Hoja de contacto: `qa/N01-contact-sheet.jpg`
- Auditoría familiar portable: `../BLOCK-01-cover-final/audit.json`
- Línea de base portable de interiores: `../BLOCK-01-cover-final/baseline-interior-hashes.json`
- Plancha familiar: `../BLOCK-01-cover-final/contact-sheet-N00-N10.jpg`

## Cambio editorial

La Sección 21 conserva la apertura visual de Hotel Horizonte y agrega el memo HH-01 completo. La página usa tres columnas para el desarrollo y una nota inferior para la declaración de autorización y los siete campos. El contenido no invade la nota, no se superpone y termina dentro de la página 24. La consigna de la página 28 solicita completar la ficha breve de HH-01.

## Verificación ejecutada

```text
python3 validate_n01_v18.py
```

Resultado: `PASS`.

- 29 páginas A4.
- 29 folios y 29 enlaces de pie.
- 28 secciones con encabezado y cuerpo juntos.
- Ningún párrafo fuente cruza una página.
- Ninguna página queda por debajo del 50 % de ocupación. El mínimo medido es 52,9 % en la página de cierre.
- Las once URLs externas están presentes, son clicables y conservan sus guiones.
- Las quince referencias conservan anclaje en el cuerpo.
- Tapa, tracking del eyebrow, sangrado y scrims conservan la geometría aprobada.
- Portada nativa en blanco y negro, sin conversión cromática por CSS, con rango tonal validado y texto alternativo semántico asociado a una estructura `Figure` válida.
- Seis voces y seis retratos distintos, sin duplicaciones.
- Glosario completo: quince entradas, tres columnas, 9,7 pt.
- Cierre: fósforos, folio, pie, leyenda y texto alternativo.

## Integridad

- Fuente canónica SHA256: `831af339cc5400bf95edb04b5b70bbacbc0857e12a2001bd77bd67bb27bd09c4`.
- Portada: `assets/cover-source-premium-bw-v1.png`, desplegada como `assets/cover.png`; SHA256 `12a34ac7c675693add178d00f248eab710ea6154fa8ee5e4547f6e0ee6503679`.
- Texto alternativo de portada: «Ruta serrana argentina que avanza entre curvas, roca y niebla hasta perderse en la distancia».
- PDF final SHA256: `668acc44383a86dbfec31620f47b9e511c1097ff1df7b846903942f8760d57fe`.
- PDF final: 26.886.102 bytes.
- Fecha de modificación: 2026-09-04 08:19:50 ART.
- Auditoría familiar: PASS, 11 de 11 documentos; 328 de 328 páginas interiores idénticas a la línea de base; 11 de 11 conjuntos de URLs idénticos; 11 de 11 portadas con `Figure` y texto alternativo válidos.

## Incertidumbres

No quedan incertidumbres técnicas abiertas en esta versión. El PDF está etiquetado, marcado y declara idioma `es-AR`. El estado editorial continúa siendo «cerrado»; la actualización de identidad y auditoría no agrega una aprobación autoral nueva.
