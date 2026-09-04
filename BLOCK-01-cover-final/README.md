# Auditoría final de tapas del Bloque 1

Alcance: N00 a N10. N11 queda expresamente excluido. El validador es de sólo
lectura respecto de los paquetes. El baseline canónico está encapsulado en
`baseline-interior-hashes.json`, por lo que la auditoría no depende de copias de
PDF externas ni de rutas propias de una máquina.

Ejecutar desde la raíz del repositorio:

```bash
python3 BLOCK-01-cover-final/validate_block01_covers.py
```

Requiere Python 3 con `numpy`, `Pillow`, `pdfplumber` y `pypdf`, además de
Poppler (`pdftoppm`) disponible en `PATH`.

El gate comprueba páginas y A4, texto alternativo efectivo en la tapa (una
`/Figure` de la página 1 con `/Alt` idéntico al HTML y enlace válido mediante
MCID o MCR más `ParentTree`, u OBJR más `StructParent` y `ParentTree`, dentro de
un PDF marcado y con idioma español). El `/Alt` del XObject de imagen se conserva
sólo como diagnóstico y no produce PASS. También comprueba eyebrow extraíble,
B/N en el activo por dispersión de canales, amplitud tonal de la tapa
PDF ya compuesta, sangrado y halo, cobertura completa del overlay, familias
tipográficas, unicidad exacta
y perceptual de las once fotografías, contrato de `manifest.cover`, ausencia de
conversión CSS efectiva a grises, igualdad del conjunto de URLs y coincidencia
pixel a pixel de las 328 páginas interiores contra las huellas canónicas.

Si se dispone de una copia externa de los once PDF de control, se puede ejecutar
una verificación alternativa. El directorio debe contener `N00.pdf` a `N10.pdf`:

```bash
python3 BLOCK-01-cover-final/validate_block01_covers.py \
  --baseline-dir path/to/baseline \
  --output-dir path/to/audit-output
```

El modo alternativo es explícito y no reemplaza ni reescribe el manifiesto
incluido.

Artefactos generados:

- `baseline-interior-hashes.json`: recuentos, conjuntos URL y SHA-256 del raster
  de cada página interior, 328 en total.
- `audit.json`: evidencia completa, umbrales, hashes y resultado por documento.
- `contact-sheet-N00-N10.jpg`: revisión visual conjunta de las once tapas.

El script devuelve `0` para PASS, `1` si una guarda falla y `2` si la auditoría
no puede ejecutarse. Los renders intermedios se crean en un directorio temporal
y se eliminan al terminar.
