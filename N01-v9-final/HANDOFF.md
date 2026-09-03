# Handoff autosuficiente, N01 v9 final

## Estado

N01 v9 está compuesto, exportado y validado. La versión v8 aprobada permanece intacta en `N01-v8-final/` y su fuente sigue en `N01/source/N01_metodologia_sin_recetas-v8.md`. La revisión vive en la rama `n01-v9-review` y se identifica con la etiqueta `n01-v9-final-validated`.

## Entrega principal

- PDF final: `output/N01-METSI-lectura-previa-v9-final.pdf`
- Fuente editorial empaquetada: `source/N01_metodologia_sin_recetas-v9.md`
- HTML editable: `index.html`
- CSS de composición: `magazine.css`
- Diagrama editable: `diagrams/N01-mapa-decision.svg`
- Manifiesto de construcción: `manifest.json`
- Manifiesto de fuente: `source-manifest.json`
- Trazabilidad de imágenes: `provenance/image-manifest.json`
- Auditoría de profundidad: `provenance/content-depth-audit.json`
- Invariantes protegidos: `provenance/regression-lock.json`
- QA técnico: `qa-report.json`
- QA integral: `integrity-report.json`
- Hoja de contacto final: `qa/N01-contact-sheet.jpg`
- Plan de páginas: `page-spread-plan.json`
- Auditoría visual: `visual-audit.md`
- Registro de cambios: `CHANGELOG.md`

## Reproducción

Desde la raíz del repositorio:

```bash
python3 build_collection.py --start 1 --end 1
python3 export_pdfs.py 1
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 finalize_and_qa.py 1
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 validate_n01_v9.py
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 render_contact_sheets.py 1
```

La exportación requiere Google Chrome local. La validación y el render usan las dependencias PDF empaquetadas por Codex.

## Controles cerrados

- Treinta páginas A4 y cierre de fósforos en la 30.
- Veintiocho secciones numeradas, en el orden revisado, sin títulos huérfanos.
- Seis tramos visibles en los marcadores.
- Tapa en tres líneas y sin colisión entre pull quote y círculo.
- Página 24 con epígrafe completo y orden de extracción correcto.
- Diagrama central legible y sin truncamiento.
- Glosario completo, exclusivo y en cuatro columnas en la página 28.
- Quince referencias completas, ancladas y con enlaces corregidos.
- Seis referentes alineados uno a uno con el aparato.
- Seis voces y seis retratos distintos para Hotel Horizonte.
- Registro impersonal sin “usted”.
- Folio y vínculo de pie en las treinta páginas.
- Cierre con leyenda, texto alternativo y sin frase superpuesta.
- Fuente y paquete v8 sin modificaciones.

## Incertidumbres

No quedan incertidumbres técnicas o editoriales abiertas desde los archivos. La única decisión externa pendiente es la publicación o promoción de esta versión fuera del repositorio local.
