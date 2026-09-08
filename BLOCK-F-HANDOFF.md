# METSI · Handoff autosuficiente del Bloque F

## Estado

N26, N27, N28, N29 y N30 están completos en contenido canónico y en versión editorial v1. Los cinco PDF finales tienen 28 páginas A4 y resultado global PASS. N00 a N25 no se modificaron. El bloque no fue publicado ni enviado a la rama remota.

## Recorrido académico

1. N26 amplía la arquitectura hacia un ecosistema de servicios, plataformas y terceros, con ownership, confianza, degradación y salida.
2. N27 convierte las dependencias en contratos sintácticos, semánticos, temporales y operacionales verificables.
3. N28 organiza evidencia de calidad según riesgo y vuelve discutibles los atributos en tensión.
4. N29 gobierna integración, artefactos, infraestructura, aprobación, despliegue progresivo y recuperación.
5. N30 conecta telemetría, señales de negocio y experiencia, SLI, SLO, incidentes y aprendizaje.

Cada lectura conserva una tesis propia, un episodio de Hotel Horizonte, tres movimientos, un instrumento utilizable, transferencia, contraejemplo, errores frecuentes, consecuencias, límites, síntesis, cinco píldoras, glosario, seis preguntas, seis referentes y doce referencias base.

## Paquetes y reproducción

- Fuente canónica: `N26-content-canonical` a `N30-content-canonical`.
- Paquete editorial: `N26-v1-editorial` a `N30-v1-editorial`.
- Generación de contenido: `build_block_f_content.py`.
- Composición: `build_block_c_editorial.py --start 26 --end 30`.
- Exportación: `export_block_c_pdfs.py --start 26 --end 30`.
- Finalización: `finalize_block_c_pdfs.py --start 26 --end 30`.
- Auditoría de contenido: `audit_block_f_content.py`.
- Auditoría de PDF: `audit_block_f_pdfs.py`.
- Planes de contacto: `qa-contact-sheets/N26-contact-sheet.jpg` a `N30-contact-sheet.jpg`.

## Evidencia de cierre

| Documento | PDF final | Páginas | Bloques trazados | Enlaces bibliográficos | Placas fotográficas | SHA256 |
|---|---|---:|---:|---:|---:|---|
| N26 | `N26-v1-editorial/output/N26-METSI-lectura-previa-v1-final.pdf` | 28 | 251/251 | 6/6 | 1, 5, 22, 28 | `ee745833778d8635c51ec45a12e58c5d94a50e710d136b3d81f75ffbf63ac550` |
| N27 | `N27-v1-editorial/output/N27-METSI-lectura-previa-v1-final.pdf` | 28 | 251/251 | 8/8 | 1, 5, 22, 28 | `92a694256db16ead71e9bfe566561b963e6eca75d1e3dab29a8d1ae49aa165d2` |
| N28 | `N28-v1-editorial/output/N28-METSI-lectura-previa-v1-final.pdf` | 28 | 251/251 | 8/8 | 1, 5, 22, 28 | `951ad7fc5bbaab488a26e118f9033c923cb103d25b051dbcbe30fc714019bb83` |
| N29 | `N29-v1-editorial/output/N29-METSI-lectura-previa-v1-final.pdf` | 28 | 251/251 | 9/9 | 1, 5, 22, 28 | `5ae987a85d8c135d454be948fc5ac6f30ec589de55673b6455aead00bba4e783` |
| N30 | `N30-v1-editorial/output/N30-METSI-lectura-previa-v1-final.pdf` | 28 | 251/251 | 7/7 | 1, 5, 22, 28 | `80d3516ac0a2352ef173eb0fded01168d772d08d3d88f0682c2eaf7edb681667` |

## Validaciones realizadas

- Profundidad y arquitectura canónica: PASS, 40/40 en cada lectura.
- Solapamiento transversal: PASS; máximo 0,2099 con ngramas de doce palabras, explicado por la arquitectura común.
- Correspondencia fuente a HTML y PDF: PASS, 251 de 251 bloques por documento y cero pérdidas canónicas.
- A4, 28 páginas, idioma `es-AR`, estructura etiquetada y metadatos: PASS.
- Portada, dos pausas internas y cierre de fósforos a página completa: PASS.
- Primera pausa después de página 4 y cierre estable en página 28: PASS.
- Títulos, cortes, páginas vacías, folios, pies, enlaces y textos alternativos: PASS.
- Auditoría visual completa de 140 páginas mediante planes de contacto: PASS.
- Referencias temporales contrastadas con fuentes primarias vigentes al 8 de septiembre de 2026.

## Incertidumbres declaradas

No se dispone de derecho local verificable para varios retratos institucionales o colectivos. Esos espacios muestran un monograma y quedan deliberadamente pendientes. Esta incertidumbre no afecta contenido, bibliografía, accesibilidad ni composición. No se detectaron otras incertidumbres materiales desde los archivos.

## Próximo estado autorizado

El bloque queda listo para revisión del autor. Publicar, sustituir retratos o cambiar contenido requiere una instrucción posterior explícita.
