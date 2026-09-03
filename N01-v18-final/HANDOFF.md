# Handoff autosuficiente, N01 v18 final

## Estado

N01 v18 está compuesto, exportado y validado contra la fuente canónica final del Bloque 1. La sincronización incorpora HH-01 y su continuidad con N02. Las versiones v8 a v17 permanecen congeladas.

## Entregables

- PDF final: `output/N01-METSI-lectura-previa-v18-final.pdf`
- Fuente canónica empaquetada: `source/N01_metodologia_sin_recetas-content-final.md`
- HTML editable: `index.html`
- Hoja de estilos: `magazine.css`
- Informe de integridad: `integrity-report.json`
- Informe PDF: `qa-report.json`
- Auditoría visual: `visual-audit.md`
- Hoja de contacto: `qa/N01-contact-sheet.jpg`

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
- Seis voces y seis retratos distintos, sin duplicaciones.
- Glosario completo: quince entradas, tres columnas, 9,7 pt.
- Cierre: fósforos, folio, pie, leyenda y texto alternativo.

## Integridad

- Fuente canónica SHA256: `831af339cc5400bf95edb04b5b70bbacbc0857e12a2001bd77bd67bb27bd09c4`.
- PDF final SHA256: `c4699ae37c263815b942c810bb6f606cd129ae1e2ab1c9dc1daf3cef2b867e0a`.
- PDF final: 24.719.327 bytes.
- Fecha de modificación: 2026-09-03 12:37:07 ART.

## Incertidumbres

No quedan incertidumbres editoriales abiertas en esta versión. El PDF no contiene estructura etiquetada PDF/UA, una limitación conocida del motor de exportación que no altera el contenido, la capa de texto ni los textos alternativos registrados.
