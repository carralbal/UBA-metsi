# Alineación del sitio con las lecturas · 27 de septiembre de 2026

## Alcance

- Lenguaje más directo en el home y en los 36 resúmenes del mapa.
- Ocho nombres de bloque en infinitivo, compartidos por atlas, detalle, catálogo y programa.
- Atlas: 41 conceptos y 70 enlaces a secciones y páginas verificadas del PDF vigente. OKR y COBIT se identifican como conexiones temáticas, no desarrollos del marco.
- Referentes: selección general de 24 obras del programa con enlaces a las lecturas que citan la obra y el año; acceso separado a Referencias base de las 36 N.
- Programa: nueve páginas, correspondencia A–H / N01–N36, enfoque pedagógico actualizado y concordancia bibliográfica. Se conserva la denominación formal y el carácter de propuesta pendiente de revisión institucional.
- Los 36 PDF y sus fuentes canónicas permanecen sin cambios. Sus hashes se contrastan con el manifiesto de publicación antes de generar el atlas.

## Verificación

- Todas las secciones enlazadas existen en las fuentes y en la página indicada del PDF publicado.
- La concordancia bibliográfica identifica obras y años, no prueba equivalencia entre distintas ediciones ni reemplaza una revisión académica de todas las citas.
- Pruebas de navegador a 1440, 768 y 390 píxeles: ocho bloques, 41 prácticas, 70 enlaces, menú móvil y ausencia de desbordamiento horizontal. Posición del radial estable.
- Programa renderizado y revisado en sus nueve páginas; corregido un título que quedaba aislado al final de página.
- La versión anterior del programa se conserva en archive/programa/pre-alignment-20260927/.

## Regeneración

1. Ejecutar scripts/build_site_alignment.py para comprobar fuentes/PDF y regenerar atlas, concordancia y catálogo.
2. Ejecutar programa/build_programa_pdf.py para sincronizar el programa público, sus páginas, hash y enlaces.
3. Ejecutar scripts/qa_site_alignment.mjs contra la vista previa o la URL pública.

No se modifican el régimen académico ni las condiciones de evaluación. Su aprobación institucional sigue siendo una instancia separada de esta alineación editorial.

## Publicación verificada

- Repositorio: https://github.com/carralbal/UBA-metsi
- Commit de publicación: 6ad14ced859fa40b90b1aaa1ef1d05d136e365b0.
- GitHub Pages: https://github.com/carralbal/UBA-metsi/actions/runs/36345433677 (completado correctamente).
- Sitio: https://carralbal.github.io/UBA-metsi/?v=6ad14ce
- Atlas: https://carralbal.github.io/UBA-metsi/?v=6ad14ce#atlas-practicas
- Programa: https://carralbal.github.io/UBA-metsi/covers/programa/programa-metsi-2026.pdf?v=alineacion-20260927
- Seis archivos públicos contrastados por SHA-256 con la versión local, incluido el PDF del programa. Las 36 lecturas responden HTTP 200 como PDF.
- Navegador público verificado a 1440, 768 y 390 píxeles: las mismas 41 prácticas y 70 destinos, sin errores de ejecución ni desbordamiento horizontal. El control de estabilidad del radial se toma una vez finalizada la animación de entrada, para no confundirla con un desplazamiento por selección.
- Evidencia: live-verification.json y browser-qa.json.
