# Handoff autosuficiente · N07 v9 final

## Estado

N07 queda compuesto, exportado y auditado como PDF final desde su contenido canónico aprobado. El contenido, los enlaces, la estructura, la accesibilidad y la compaginación quedan cerrados técnicamente. La auditoría técnica consolidada de las tapas N00 a N10 cerró con resultado `PASS` para los once documentos, 328 páginas interiores y once conjuntos de URL.

## Entregable principal

`output/N07-METSI-lectura-previa-v9-final.pdf`

- 31 páginas A4.
- 20.825.394 bytes.
- Fecha de modificación: 4 de septiembre de 2026, 07:57:56, hora de Buenos Aires.
- SHA-256: `c7b36bffcd3da4d1955f3563f7836dc9fad28d5cb0fa5ed7129bba1f2b075bd9`.

## Fuente autoritativa

`source/N07_entrevistar_no_es_pedir_requisitos-content-final.md`

Es byte a byte idéntica a la fuente de `N07-content-final`, con SHA-256 `4e0416a028109761f0a9f498315946a62a147355c759054a733dd82902f639b6`.

## Qué quedó cerrado

- contenido canónico preservado sin pérdidas, duplicados ni reescrituras;
- 371 bloques fuente renderizados una vez y en el orden original;
- tapa a sangre con fotografía concebida nativamente en blanco y negro, gama amplia de grises y capa tonal localizada, sin halo ni costura;
- margen medido de 27,029 pt entre el título y la cita de tapa, por encima del mínimo de seguridad de 12 pt;
- eyebrow extraíble como `LECTURA PREVIA` y `EDICIÓN 2026`;
- índice completo y seis referentes distintos, con retratos uniformes y procedencia documentada;
- exactamente dos pausas internas a página completa, en las páginas 5 y 13;
- primera pausa inmediatamente después de la página 4;
- infografía de cadena de evidencia con doce nodos y catorce relaciones, ampliada a 160 × 97,8 mm y con rótulo mínimo equivalente a 7,56 pt;
- corrección de los tres riesgos de reflujo detectados: `Sondas útiles` junto a su lista en la página 17, ítems 9 y 10 juntos en la página 27, y encabezado de Cinco píldoras anterior a sus cinco ítems en el orden de extracción de la página 28;
- 11 referencias ancladas y 5 URL externas completas, impresas y clicables;
- 5 píldoras, 13 entradas de glosario y 6 preguntas de preparación;
- cuatro voces de Hotel Horizonte con retratos distintos y de igual tratamiento;
- ningún título o subtítulo huérfano;
- ninguna página ordinaria por debajo del umbral editorial, con mínimo medido de 57,89 % en la página 30;
- Referencias base en dos columnas minimalistas, sin barra lateral ni fotografía ornamental;
- cierre canónico con fósforos, folio, línea de pie, epígrafe, texto alternativo y sin frase agregada;
- PDF etiquetado con idioma `es-AR` y pie enlazado en sus 31 páginas;
- segunda construcción con HTML, CSS, manifiestos, texto extraído, enlaces y 31 páginas rasterizadas idénticos a la primera. El identificador binario interno del PDF puede variar entre exportaciones sin alterar contenido ni apariencia.

## Archivos de control

- `validation-v9.json`: resumen de la auditoría determinista integral.
- `qa-report.json`: control técnico del PDF.
- `visual-audit.md`: auditoría visual final.
- `qa/N07-contact-sheet.jpg`: vista completa del documento.
- `page-spread-plan.json`: ubicación de aparatos, pausas, infografía y cierre.
- `infographic-evidence-chain/`: fuente editable, manifiesto semántico, texto alternativo y QA de la infografía.
- `provenance/`: procedencia de tapa, imágenes, retratos y bloqueo de regresión.

## Cómo reproducir y verificar

Desde la raíz del repositorio:

```bash
python3 build_collection.py --start 7 --end 7
python3 export_pdfs.py 7 7
python3 finalize_and_qa.py 7
python3 validate_n07_v9.py
```

El último comando debe terminar con código cero, `status: PASS` y 40 controles aprobados.

## Incertidumbre residual

No queda incertidumbre técnica de contenido, estructura, enlaces, accesibilidad, compaginación ni pertenencia de la tapa a la familia N00 a N10. La publicación remota de N07 requiere autorización expresa.
