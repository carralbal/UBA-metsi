# METSI · Handoff autosuficiente de los bloques G y H

## Estado

N31 a N36 están completos en contenido canónico y versión editorial v1. Los seis PDF finales tienen 30 páginas A4 y resultado global PASS. N00 a N30 no fueron modificados. La biblioteca del sitio contiene las 37 lecturas, desde N00 hasta N36, y pasó su validación local integral.

## Recorrido académico

1. N31 distingue reglas, predicción, generación y agencia para decidir cuándo la IA es pertinente.
2. N32 evalúa tareas, cobertura, severidad, desigualdad, robustez y supervisión antes de asignar autonomía.
3. N33 convierte principios de IA en gobierno vivo mediante inventario, ownership, datos, proveedores, cambios, monitoreo, incidentes, reparación y retiro.
4. N34 reconstruye una cadena íntegra desde el problema y la evidencia hasta la operación y el gobierno.
5. N35 trabaja la defensa y transferencia de criterios sin copiar soluciones ni ocultar incertidumbre.
6. N36 cierra el recorrido con práctica reflexiva capaz de aprender de decisiones, errores, sorpresas y asistencia de IA.

Cada lectura conserva una tesis propia, un episodio de Hotel Horizonte, tres movimientos, doce unidades conceptuales, un instrumento utilizable, transferencia, contraejemplo, errores frecuentes, consecuencias, límites, síntesis, cinco píldoras, glosario, seis preguntas, seis referentes y doce referencias base.

## Paquetes y reproducción

- Fuente canónica: `N31-content-canonical` a `N36-content-canonical`.
- Paquete editorial: `N31-v1-editorial` a `N36-v1-editorial`.
- Generación de contenido: `build_blocks_g_h_content.py`.
- Composición: `build_block_c_editorial.py --start 31 --end 36`.
- Exportación: `export_block_c_pdfs.py --start 31 --end 36`.
- Finalización: `finalize_block_c_pdfs.py --start 31 --end 36`.
- Auditoría de contenido: `audit_blocks_g_h_content.py`.
- Auditoría de PDF: `audit_blocks_g_h_pdfs.py`.
- Validación de biblioteca: `site/validate_site.py`.

## Evidencia de cierre

| Documento | Páginas | Bloques trazados | Enlaces bibliográficos | Placas fotográficas | SHA256 |
|---|---:|---:|---:|---:|---|
| N31 | 30 | 255/255 | 8/8 | 1, 5, 24, 30 | `e808179b2eda6b91dda1f64de13b62f984cd6c32039bb8b30ee0f3c42d9889e4` |
| N32 | 30 | 255/255 | 9/9 | 1, 5, 24, 30 | `ee31424cd5d96670ac4772875f5de7aa46a7e8be1063df4373b1c16b3d9e7945` |
| N33 | 30 | 255/255 | 11/11 | 1, 5, 24, 30 | `edfb8f9250b1a4c7d9188ff47e133bc2a873ee1da316a9e571e0ca2f783272f9` |
| N34 | 30 | 255/255 | 6/6 | 1, 5, 24, 30 | `044dba68b3ef48d792fe8c41d9fd609eb51c02de15f6f44927946ded4d02aed7` |
| N35 | 30 | 255/255 | 3/3 | 1, 5, 24, 30 | `9021b96590eb3b7aba980bcea78cb3e6b2cd15700b3392240319c2f28327fb8d` |
| N36 | 30 | 255/255 | 3/3 | 1, 5, 24, 30 | `9aa0402c8b8d6b475d88619018e0ab64633d9361fea9d2b863d5217acf1f3abb` |

## Validaciones realizadas

- Arquitectura, profundidad, referencias ancladas y registro: PASS en las seis lecturas.
- Solapamiento transversal: PASS; máximo 0,2172 con ngramas de doce palabras.
- Correspondencia entre fuente, HTML y PDF: PASS, 255 de 255 bloques por documento y cero pérdidas canónicas.
- A4, 30 páginas, idioma `es-AR`, PDF etiquetado, metadatos y enlaces: PASS.
- Tapa, dos pausas y cierre con fósforos a página completa: PASS.
- Eyebrow, folios, pies, títulos, cortes, páginas vacías y fondos: PASS.
- Biblioteca local: PASS, 37 PDF, 37 tapas, 36 Núcleos y ocho bloques, sin enlaces locales rotos.
- Revisión visual de escritorio y móvil: PASS, sin desborde horizontal ni imágenes ausentes.

## Incertidumbre explícita

Los retratos sin una fuente local con derechos verificables se mantienen como monograma. Las referencias normativas y técnicas dependientes del tiempo están fechadas; el TEVV-Athlon de NIST se identifica expresamente como borrador inicial de 2026. No se detectaron otras incertidumbres materiales desde los archivos.
