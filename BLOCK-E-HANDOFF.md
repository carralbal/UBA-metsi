# METSI · Handoff autosuficiente del Bloque E

## Estado

N21, N22, N23, N24 y N25 están completos en contenido canónico y en versión editorial v1. Los cinco PDF finales tienen 28 páginas A4 y resultado global PASS. N00 a N20 no se modificaron. El bloque no fue publicado ni enviado a la rama remota.

## Recorrido académico

1. N21 distingue proyecto, producto, servicio y plataforma por horizonte, valor, ownership y criterio de cierre.
2. N22 convierte iniciativas en hipótesis refutables con evidencia, umbrales y salvaguardas.
3. N23 desplaza el corte desde componentes terminados hacia capacidad observable y aprendizaje.
4. N24 trata la prioridad como renuncia explícita bajo límites, obligaciones y distribución de consecuencias.
5. N25 integra flujo, colas, tamaño de lote, espera y feedback sin reducir el problema a velocidad.

Cada lectura conserva una tesis propia, un episodio de Hotel Horizonte, tres movimientos, un instrumento utilizable, transferencia, contraejemplo, errores frecuentes, consecuencias, límites, síntesis, cinco píldoras, glosario, seis preguntas, seis referentes y doce referencias base.

## Paquetes y reproducción

- Fuente canónica: `N21-content-canonical` a `N25-content-canonical`.
- Paquete editorial: `N21-v1-editorial` a `N25-v1-editorial`.
- Generación de contenido: `build_block_e_content.py`.
- Composición: `build_block_c_editorial.py --start 21 --end 25`.
- Exportación: `export_block_c_pdfs.py --start 21 --end 25`.
- Finalización: `finalize_block_c_pdfs.py --start 21 --end 25`.
- Auditoría de contenido: `audit_block_e_content.py`.
- Auditoría de PDF: `audit_block_e_pdfs.py`.
- Planes de contacto: `qa-contact-sheets/N21-contact-sheet.jpg` a `N25-contact-sheet.jpg`.

## Evidencia de cierre

| Documento | PDF final | Páginas | Bloques trazados | Enlaces bibliográficos | Placas fotográficas | SHA256 |
|---|---|---:|---:|---:|---:|---|
| N21 | `N21-v1-editorial/output/N21-METSI-lectura-previa-v1-final.pdf` | 28 | 251/251 | 2/2 | 1, 5, 22, 28 | `a3362a86e58b2b6eb4a30f70fa45f60fda987e99859063daafb9c3672cc611d5` |
| N22 | `N22-v1-editorial/output/N22-METSI-lectura-previa-v1-final.pdf` | 28 | 251/251 | 6/6 | 1, 5, 22, 28 | `238ba3eb5d7c8100740d380275693862740358a8972d0f39873998cf47af958c` |
| N23 | `N23-v1-editorial/output/N23-METSI-lectura-previa-v1-final.pdf` | 28 | 251/251 | 4/4 | 1, 5, 22, 28 | `c798eb375ddf328c2f0cd12eff32fa84efbec7cd8ff00dd2290eced2600499b1` |
| N24 | `N24-v1-editorial/output/N24-METSI-lectura-previa-v1-final.pdf` | 28 | 251/251 | 6/6 | 1, 5, 22, 28 | `9207845179ffb28141055e5e3a6bf3bc2738dcc5ca90cc1bd38959c8c41ab167` |
| N25 | `N25-v1-editorial/output/N25-METSI-lectura-previa-v1-final.pdf` | 28 | 251/251 | 5/5 | 1, 5, 22, 28 | `5eb1541257b4a909f9566cbf85828d39138b19153b28f788aad60f084fed2704` |

## Validaciones realizadas

- Profundidad y arquitectura canónica: PASS, 40/40 en cada lectura.
- Solapamiento transversal: PASS; máximo 0,2135 con ngramas de doce palabras, explicado por la arquitectura común.
- Correspondencia fuente a HTML y PDF: PASS, sin pérdidas canónicas.
- A4, 28 páginas, idioma `es-AR`, estructura etiquetada y metadatos: PASS.
- Portada, dos pausas internas y cierre de fósforos a página completa: PASS.
- Primera pausa después de página 4 y cierre estable en página 28: PASS.
- Títulos, cortes, colisiones, páginas vacías, folios, pies, enlaces y textos alternativos: PASS.
- Auditoría visual completa de 140 páginas mediante planes de contacto: PASS.
- Referencias temporales contrastadas con fuentes primarias vigentes al 7 de septiembre de 2026: The Kanban Guide de mayo de 2025, The Standard for Program Management, quinta edición, e ISO/IEC 20000-1:2018, confirmada en 2023.

## Incertidumbres declaradas

No se dispone de derecho local verificable para doce de los treinta retratos de referentes. Esos espacios muestran un monograma y quedan deliberadamente pendientes. Esta incertidumbre no afecta contenido, bibliografía, accesibilidad ni composición. No se detectaron otras incertidumbres materiales desde los archivos.

## Próximo estado autorizado

El bloque queda listo para revisión del autor. Publicar, sustituir retratos o cambiar contenido requiere una instrucción posterior explícita.
