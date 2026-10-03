# N00 · Recorrido visual en la guía

La versión v4 incorpora seis páginas nuevas inmediatamente después de la página 12 de N00. Las otras 44 páginas se trasladan sin modificar su contenido gráfico; la portada y la versión v3 quedan intactas como respaldo.

La fuente de las 36 explicaciones, las ocho estaciones y sus microdiagramas es el recorrido aprobado en `site/covers/recorrido/index.html`. `build.mjs` convierte esa fuente en seis páginas A4 editables en HTML y en `N00-recorrido-insert.pdf`. `merge.py` inserta esas páginas en el PDF v3 para producir el PDF completo de 50 páginas. Los folios suplementarios 12A–12F preservan la numeración impresa del documento original.

Para regenerar, instalar Playwright y pypdf, y configurar `METSI_PLAYWRIGHT_PATH` y `METSI_CHROME_PATH` si no están en las ubicaciones estándar. Después ejecutar `node N00-v4-recorrido/build.mjs` y `python3 N00-v4-recorrido/merge.py` desde la raíz del repositorio.

El PDF vigente para la web está en `site/pdf/publicados/N00-METSI-lectura-previa-v4-recorrido.pdf`. La versión anterior sigue en `site/pdf/N00-METSI-lectura-previa-v3-final.pdf`.

## Contrato visual y conceptual

- Claim: el recorrido pasa de comprender el problema a sostener la intervención y aprender del resultado.
- Fuente: la descripción de N00–N36 y las ocho estaciones aprobadas para el recorrido interactivo.
- Topología: trayecto vertical N00 → A–H → N36, con cinco movimientos de síntesis y microdiagramas específicos para cada estación.
- Relaciones: cada tramo produce una capacidad que el siguiente necesita; la salida de H devuelve el aprendizaje a la próxima pregunta.
- Invariantes: tapa v3, fotos, fondos, texto, referentes y 44 páginas originales; volt sólo como acento gráfico, no como color de texto.

## Control

- Inserto: seis páginas A4, con N01–N36 una vez cada una y sin desbordes según la medición del navegador.
- PDF final: 50 páginas.
- Los 44 flujos de contenido originales se compararon byte a byte con la v4 y no presentan diferencias.
- Se inspeccionaron las seis páginas nuevas rasterizadas y su hoja de contacto.
