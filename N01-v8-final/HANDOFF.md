# Handoff autosuficiente, N01 v8 final

## Estado

N01 quedó reconstruido como candidato final independiente. La versión anterior permanece intacta en `N01/` y está preservada desde el commit base `2a9d1b2`. La nueva salida vive en `N01-v8-final/`.

## Entrega principal

- PDF final: `output/N01-METSI-lectura-previa-v8-final.pdf`
- Fuente editorial: `source/N01_metodologia_sin_recetas-v8.md`
- HTML editable: `index.html`
- CSS de composición: `magazine.css`
- Diagrama editable: `diagrams/N01-mapa-decision.svg`
- Manifiesto de construcción: `manifest.json`
- Trazabilidad de imágenes: `provenance/image-manifest.json`
- Auditoría de profundidad: `provenance/content-depth-audit.json`
- Invariantes protegidos: `provenance/regression-lock.json`
- QA técnico: `qa-report.json`
- QA integral: `integrity-report.json`
- Hoja de contacto final: `qa/N01-contact-sheet.jpg`
- Plan de páginas: `page-spread-plan.json`
- Auditoría visual: `visual-audit.md`

## Cambios editoriales consolidados

- Se profundizó N01 hasta 7.696 palabras y 29 secciones, con continuidad explícita hacia N02 a N10.
- Se anclaron las quince entradas de Referencias base en el cuerpo.
- Se incorporaron SWEBOK V4.0a, ISO 15288, ISO 24748, PMBOK 8, NIST AI RMF, NIST GenAI, Reglamento de IA de la Unión Europea, DORA 2025 e IS2020 con función argumental.
- Se preservaron dos pausas fotográficas a página completa y el cierre canónico de fósforos.
- La página 4 se resolvió como apertura oscura a sangre.
- Referencias base quedó en doble columna minimalista, sin barras decorativas.
- Hotel Horizonte presenta seis voces y seis retratos diferentes con marco idéntico.
- Las imágenes nuevas poseen autor, página fuente, licencia, hash, alt y propósito editorial; ninguna se repite en N00 a N10.

## Controles cerrados

- Treinta páginas A4.
- Ningún título fuente ausente del PDF.
- Ninguna tipografía prohibida.
- Folio y vínculo de pie en las treinta páginas.
- Dos pausas visuales exactas.
- Seis referentes y seis voces de Hotel Horizonte.
- Quince referencias completas y ancladas.
- Ocho imágenes editoriales con hashes e identificadores únicos.
- Cierre con fósforos, folio, pie, leyenda, texto alternativo y ausencia de frase superpuesta.
- PDF anterior sin modificaciones.

El resultado de todos los controles es `PASS`. Para repetir la validación integral se ejecuta:

```bash
/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 validate_n01_final.py
```

## Incertidumbres

No quedan incertidumbres técnicas o editoriales abiertas desde los archivos. La única decisión pendiente es externa al artefacto: cuándo promover este candidato a versión oficialmente aprobada de N01 y, si se decide, reemplazar el alias de distribución. Hasta entonces, ambos PDF permanecen separados.
