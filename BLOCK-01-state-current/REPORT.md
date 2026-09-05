# Estado consolidado y autoridad vigente · METSI N00 a N10

Fecha de auditoría: 2026-09-04T22:36:26-03:00.

## Dictamen

El estado técnico consolidado es **PASS**. No hay una deuda de contenido oculta en N01 a N10: las diez fuentes empaquetadas coinciden byte por byte con las fuentes canónicas, los diez controles de QA de PDF informan PASS y los diez controles de integridad informan PASS.

La distinción de autoridad de N00 quedó resuelta. N00 v2 fue aprobado por el autor, tiene 27 de 27 controles técnicos aprobados y pasa a ser la versión autoritativa. El N00 anterior permanece intacto como baseline histórico. Esta aprobación no implica publicación externa.

Esta auditoría no modificó fuentes, HTML, CSS ni PDF.

## Jerarquía de autoridad

1. **N00 v2 aprobado y autoritativo:** `N00-v2-candidate/output/N00-METSI-lectura-previa-v2-candidate-final.pdf`, 43 páginas, SHA-256 `c5e3237214b701a9721dc77d8c3d03756a7959910a19054967a7bc531c14c497`. Estado: PASS técnico, aprobación autoral registrada, publicación externa todavía no autorizada.
2. **N00 anterior:** `N00/output/N00-METSI-lectura-previa-final.pdf`, 45 páginas, SHA-256 `1b4a1ab42665246349ed240659585a2e33766fe72157032bfbefc03cc7127f64`. Estado: baseline histórico preservado sin cambios.
3. **Contenido N01 a N10:** `BLOCK-01-content-final/` es la autoridad canónica y congelada.
4. **PDF N01 a N10:** las versiones de la tabla siguiente son los finales vigentes y contienen una copia exacta de su fuente canónica.
5. **Tapas:** todo texto originalmente diseñado en volt permanece en volt. Se prohíbe resolver legibilidad con una tela oscura global. Cualquier apoyo debe ser tonal, localizado y sujeto a revisión de la tapa completa.

## Procedencia fotográfica de N00 v2

El manifiesto de imágenes quedó cerrado y verificable. Distingue los activos usados de los reemplazados y no seleccionados; registra autor, página fuente, licencia, dimensiones y hash. Los 7 activos vigentes coinciden exactamente con las referencias del HTML y con los archivos renderizados. Estado: **PASS**.

## Evidencia N01 a N10

| Documento | Páginas A4 | Palabras sustantivas | Profundidad | Fuente exacta | QA PDF | Integridad | SHA PDF |
|---|---:|---:|---:|---|---|---|---|
| N01 | 29 | 6,426 | 40/40 | Sí | PASS | PASS | `668acc44383a…` |
| N02 | 29 | 6,145 | 40/40 | Sí | PASS | PASS | `35f7d39ac098…` |
| N03 | 30 | 7,631 | 38/40 | Sí | PASS | PASS | `08154728ce84…` |
| N04 | 32 | 8,695 | 38/40 | Sí | PASS | PASS | `b6b4df7df6c9…` |
| N05 | 28 | 6,793 | 38/40 | Sí | PASS | PASS | `cf6088c20563…` |
| N06 | 28 | 7,069 | 38/40 | Sí | PASS | PASS | `c05782e7ad61…` |
| N07 | 31 | 8,474 | 38/40 | Sí | PASS | PASS | `c7b36bffcd3d…` |
| N08 | 28 | 6,356 | 39/40 | Sí | PASS | PASS | `8513d10b826c…` |
| N09 | 28 | 6,637 | 39/40 | Sí | PASS | PASS | `3cf21741a5b0…` |
| N10 | 31 | 7,180 | 39/40 | Sí | PASS | PASS | `cd5511c6bc94…` |

Totales canónicos: 86,198 palabras, 71,406 sustantivas, 123 referencias y 85 URL.

## Tapas N00 a N10

La auditoría comparativa vigente informa PASS: once páginas A4, once fotografías a sangre, once renders monocromos, once eyebrows extraíbles y conservación de la copia original en volt. La plancha de revisión sigue siendo `BLOCK-01-cover-review-current/contact-sheet-N00-N10-current.jpg`.

## Informes históricos que no abren trabajo nuevo

- `N01/audit/INFORME-AUDITORIA-N01-N10-v2.md` documenta el estado previo a la remediación.
- `N01/audit/MATRIZ-REMEDIACION-N01-N10.md` es una matriz histórica previa al cierre canónico.
- `BLOCK-01-FINAL-HANDOFF.md` conserva valor como cierre de baseline, pero antecede al candidato aislado N00 v2. No autoriza su promoción.

## Gates reproducidos

- PASS: `canonical_content_audit_n01_n10`
- PASS: `ten_final_packages_found`
- PASS: `all_packaged_sources_match_canonical_bytes`
- PASS: `all_final_pdf_qa_pass`
- PASS: `all_final_pdf_integrity_pass`
- PASS: `all_final_pdf_pages_a4`
- PASS: `all_final_pdf_files_directly_confirmed`
- PASS: `approved_n00_unchanged_and_passes`
- PASS: `n00_v2_candidate_technical_pass`
- PASS: `n00_v2_image_provenance_pass`
- PASS: `n00_v2_author_approval_recorded`
- PASS: `cover_system_current_rule_pass`

## Únicos pendientes reales

- Revisar visualmente la serie de tapas N00 a N10 a tamaño útil y registrar cualquier observación concreta.
- Publicar N00 v2 sólo después de una autorización explícita de publicación; su aprobación editorial ya está registrada.
- Publicar N07 a N10 sólo después de una autorización explícita de publicación; esta auditoría no publica.
- Tratar la percepción del texto volt en prueba de impresión como revisión autoral, no como permiso para aplicar velos oscuros globales.

## Incertidumbres explícitas

- Esta pasada no afirma certificación PDF/UA formal; se apoya en los controles de accesibilidad del repositorio.
- No se consultó el sitio público en vivo; aquí no se cambia ni se recertifica el estado de publicación.
- La aprobación de N00 v2 no permite inferir autorización de publicación externa.

## Reproducción

Con las dependencias declaradas en `requirements-qa.txt`:

```bash
python3 BLOCK-01-content-final/validate_block01_content.py
python3 BLOCK-01-state-current/validate_block01_state.py
```

## Próxima decisión correcta

No corresponde reabrir N01 a N10 ni tocar sus interiores. N00 v2 ya está aprobado. La próxima tarea editorial es la revisión visual de las once tapas. Cualquier publicación de N00 v2 o de N07 a N10 permanece como una acción separada y requiere autorización explícita.
