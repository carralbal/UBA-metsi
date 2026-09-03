# Handoff autosuficiente, N01 v10 final

## Estado

N01 v10 está compuesto, exportado y validado. Las versiones v8 y v9, sus fuentes y sus paquetes permanecen intactos. La revisión vive en la rama `n01-v10-final`.

## Entrega principal

- PDF final: `output/N01-METSI-lectura-previa-v10-final.pdf`
- Fuente editorial: `source/N01_metodologia_sin_recetas-v10.md`
- HTML y CSS editables: `index.html`, `magazine.css`
- Diagrama editable: `diagrams/N01-mapa-decision.svg`
- Registro de cambios: `CHANGELOG.md`
- QA técnico e integral: `qa-report.json`, `integrity-report.json`
- Hoja de contacto: `qa/N01-contact-sheet.jpg`
- Trazabilidad: `manifest.json`, `source-manifest.json`, `provenance/`

## Reproducción

Desde la raíz del repositorio:

```bash
python3 build_collection.py --start 1 --end 1
python3 export_pdfs.py 1
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 finalize_and_qa.py 1
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 validate_n01_v10.py
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 render_contact_sheets.py 1
```

La exportación requiere Google Chrome local. Las dependencias PDF empaquetadas por Codex se usan para finalizar, validar y renderizar.

## Controles cerrados

- Veintinueve páginas A4, 28 secciones sin títulos huérfanos y cierre canónico en la 29.
- Once URLs verificadas individualmente, con guiones preservados y destinos exactos.
- Secciones 23, 24 y 25 en dos columnas anchas.
- Glosario completo en cuatro columnas a 9,15 puntos.
- Seis voces y seis citas preservadas; sólo se actualizó el epígrafe.
- Definición única y accionable del criterio de revisabilidad.
- Ruta corregida: 01 a 04 PROBLEMA, 05 a 08 DISTINCIONES, 09 a 17 DECISIONES, 18 a 20 PRUEBA, 21 a 24 TRANSFERENCIA y 25 a 28 PREPARACIÓN.
- Folio, pie y enlace del autor en las 29 páginas.
- Activos, retratos, referencias, PMBOK, numeración y sistema visual de v9 preservados.

## Incertidumbres

No quedan incertidumbres técnicas o editoriales abiertas desde los archivos. La publicación fuera del repositorio local no forma parte de esta pasada.
