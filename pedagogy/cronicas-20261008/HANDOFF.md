# Handoff completo · Crónicas METSI N00–N36 · 2026-10-08

## Objetivo exacto del usuario

Corregir la fotografía en color del segundo piloto (N25) y producir **37 artículos periodísticos de una carilla**, uno por cada N00–N36, con títulos hook como los pilotos. Después, integrarlos de manera clara en el sitio existente, sin rediseñar ni reemplazar los documentos N, y publicar en producción en `https://carralbal.github.io/UBA-metsi/`. El usuario pidió explícitamente no detenerse ni solicitar validación previa: validará sobre los 37 PDF y la web final.

### Criterios editoriales vinculantes

- No mencionar Hotel Horizonte en las crónicas; usar casos reales distintos de hotelería.
- Investigar noticias/casos en internet; citar las fuentes primarias dentro de cada PDF, con fragmentos breves entrecomillados de referentes o fuentes recientes.
- Cada pieza debe tener escena/hook, contexto real, al menos un párrafo que explique el concepto del N correspondiente y cierre que haga pensar.
- Aproximadamente 70% de los casos de Argentina o LATAM; alternar algunos globales.
- Fotos siempre con apariencia blanco y negro, no color. Identificarlas como **ilustrativas**: no documentan los sucesos relatados.
- Formato profesional y periodístico, ameno, no académico. Visual de METSI, pero serie complementaria, no competidora de las revistas N.
- Preservar intactas la web principal y las 37 lecturas N, salvo enlaces y una entrada puntual a las crónicas en la sección 10 Colección.
- Al cerrar cada tarea: informar qué quedó cerrado, qué sigue en proceso y qué falta. Este archivo debe permitir retomar sin perder contexto.

## Lo cerrado hasta ahora

1. **Foto N25 corregida**. Se sustituyó la foto color del piloto `output/pdf/METSI-cronicas-N25-piloto.pdf` por una versión editorial neutra B&N generada a partir de la imagen original Pexels. Archivo integrado: `site/covers/cronicas/images/N25-bw.png`; PDF final: `site/covers/cronicas/pdf/N25.pdf`. A muestreo de 50×50 píxeles, desviación RGB media 0,36 (neutra). La foto mantiene crédito Pexels en el PDF.
2. **37 historias terminadas**. Texto y metadatos fuente en `pedagogy/cronicas-20261008/articles.py`. N02 y N25 son los pilotos previamente aprobados en redacción/títulos, con sólo la foto N25 cambiada. El resto N00–N36 está escrito y generado. Se reemplazó N36, antes repetido con N08, por un caso Ceibal/ANEP 2026. Hay **27/37 casos de Argentina o América Latina (73%)** y 10 globales (Europa, EE.UU., África y Asia). N11/N18/N20/N23/N24/N29/N34 pasaron a fuentes primarias verificadas de UK, NYC, UK, Sudáfrica, Singapur e India para alcanzar la alternancia pedida. Son escenas editoriales, no entrevistas testimoniales inventadas.
3. **PDFs maquetados**. `site/covers/cronicas/pdf/N00.pdf` … `N36.pdf`, una página A4 cada uno. Estilo papel/ink/volt sobrio, Didot/Baskerville/Avenir, titulares de dos líneas, fotografía panorámica ilustrativa y cuerpo en tres columnas. Los PDFs no editan ni sustituyen ningún documento N. N00 usa foto arquitectónica B&N derivada de imagen aprobada del N00; N09 y N10 usan otras fotografías editoriales B&N existentes de sus lecturas. Otras fotos provienen de las imágenes aprobadas de portada N correspondientes.
4. **Índice estático**. `site/covers/cronicas/index.html`, `style.css` y `articles.json` muestran las 37 historias agrupadas por bloques A–H, con acceso tanto a la crónica como a la lectura larga. El texto aclara que son puerta de entrada y que las fotos no documentan los hechos.
5. **Integración mínima en el sitio**. `site/index.html` tiene una entrada visual a Crónicas en la sección 10 Colección y enlace a N00. `site/metsi.js` añade un enlace “Leer la crónica” a cada tarjeta N01–N36 (sin quitar descarga de PDF), y `site/metsi.css` incorpora sólo el estilo específico. Se actualizaron las cadenas de caché del CSS y JS para que el navegador vea el cambio.
   - **Despliegue sin permiso de workflow**: el primer intento de `git push` fue rechazado porque el token GitHub de esta cuenta no tiene scope `workflow`; el commit intentaba modificar `.github/workflows/deploy-pages.yml` para añadir `site/cronicas` al artefacto. Se revirtió ese cambio localmente y se trasladó la nueva sección a `site/covers/cronicas`, dentro de `site/covers`, carpeta que el workflow existente **ya** copia a Pages con `lfs: true`. Se deben enmendar los commits locales antes de reintentar push para que el historial enviado no contenga cambios de workflow.
6. **Generador**. `scripts/build_cronicas.py` produce las páginas, índice, metadatos y una compilación local de 37 páginas en `../../output/pdf/METSI-cronicas-N00-N36.pdf` relativa al repo (raíz del proyecto ChatGPT). Tiene fallback para los PDF de pilotos ya publicados si el archivo fuente externo no existe en un clon nuevo. **No publicar la compilación de 107 MB**: supera el límite de 100 MB por archivo de GitHub. Publicar sólo los 37 individuales; la compilación es prueba local y no está enlazada.
7. **QA automatizada realizada**: 37 archivos N??.pdf, una página A4 cada uno; 37 titulares únicos; 27 casos locales/LATAM; 81 hipervínculos PDF; todos enlazan a fuente y lectura; ningún PDF contiene la cadena “Hotel Horizonte”; índice con 37 tarjetas; compilación local con 37 páginas; `node --check site/metsi.js` sin errores; render de contacto de las 37 páginas revisado. Se inspeccionaron visualmente N00, N25, N31 a tamaño de página, y después se renderizaron y revisaron en contacto los siete casos globales nuevos N11/N18/N20/N23/N24/N29/N34. No se observaron desbordes en estos siete. Fotos piloto N00/N02/N25 verificadas prácticamente neutras (diferencia RGB media 0,21/0/0,36).

## Estado en proceso

- Revisar un último pase de regresión visual/navegación local y preparar publicación. El repositorio tiene **muchísimos archivos untracked preexistentes** que no pertenecen a esta tarea; NO incluirlos en el commit. Etapa de git/push todavía no realizada al escribir este handoff.
- Las citas complementarias de N04, N12 y N36 están enlazadas como segunda fuente en el pie de su PDF. Los datos y URLs exactos figuran en `articles.py`.
- Puede ser útil añadir un manifiesto editorial breve sobre imágenes y fuentes, aunque los PDF y `articles.json` ya guardan su procedencia inmediata.

## Falta para terminar esta solicitud

1. El generador ya se ejecutó luego de los cambios editoriales. Si se modifica `articles.py` o `build_cronicas.py` nuevamente, volver a ejecutarlo con `/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/build_cronicas.py` desde la raíz del repo.
2. Confirmar que la página local `site/covers/cronicas/` abre sus 37 PDF y que `site/index.html#biblioteca` llega al índice. Verificar en navegador móvil/escritorio si está disponible, o al menos HTML/JS/archivos localmente.
3. `git add` **sólo**: la restauración de `.github/workflows/deploy-pages.yml` (para que el diff final frente al remoto sea cero), `pedagogy/cronicas-20261008/articles.py`, `pedagogy/cronicas-20261008/HANDOFF.md`, `scripts/build_cronicas.py`, `site/index.html`, `site/metsi.css`, `site/metsi.js`, `site/covers/cronicas/index.html`, `site/covers/cronicas/style.css`, `site/covers/cronicas/articles.json`, `site/covers/cronicas/images/N00-bw.png`, `site/covers/cronicas/images/N02-bw.jpg`, `site/covers/cronicas/images/N25-bw.png`, `site/covers/cronicas/pdf/N00.pdf` … `N36.pdf`. Stagear también la eliminación de `site/cronicas` del commit local inicial. La compilación grande ya está fuera del repo, en `../../output/pdf/`; no stagear archivos no relacionados.
4. **Enmendar el commit local 3112092, no crear otro**: `git commit --amend --no-edit` después de stagear estos cambios. Luego verificar `git diff origin/main..HEAD -- .github/workflows/deploy-pages.yml` vacío y publicar `main` en `origin` (autorización expresa del usuario). Comprobar GitHub Pages y URLs públicas `.../covers/cronicas/`, `.../covers/cronicas/pdf/N00.pdf`, `.../covers/cronicas/pdf/N25.pdf`, `.../covers/cronicas/pdf/N36.pdf`. No afirmar que está publicado hasta que respondan 200.
5. Actualizar este handoff con hash, hora, URL verificadas y resultado. En el cierre al usuario: enlace directo al índice y mención de 37 artículos y foto N25 corregida, con estado cerrado/en proceso/falta.

## Referencias y precauciones

- Proyecto real Git: `work/UBA-metsi-publication` bajo este proyecto ChatGPT. Rama `main`; remoto `https://github.com/carralbal/UBA-metsi.git`. Sitio servido desde `site/` por Pages. `sources/` de este proyecto es read-only; no se tocó.
- Los pilotos fuente externos de esta tarea, si siguen presentes: `output/pdf/METSI-cronicas-N02-piloto.pdf` y `output/pdf/METSI-cronicas-N25-piloto.pdf` en la raíz del proyecto ChatGPT. Ya están copiados a `site/cronicas/pdf/` para la entrega.
- Para N00 se utilizó una imagen generada B&N a partir de `N00-v2-candidate/assets/editorial-05.jpg`; archivo de serie `site/covers/cronicas/images/N00-bw.png`. Para N25 se utilizó edición B&N de la fotografía Pexels ya empleada en el piloto. No confundir fotografías ilustrativas con evidencia del caso.
- La mayoría de las fuentes son gubernamentales y primarias. Dos pilotos previamente aprobados tratan Horizon (UK) y la unidad de alta hospitalaria de St Thomas' (UK). N33 utiliza informe NIST 2026. Las URLs de las 37 fuentes están en `articles.py` y se incluyen como enlaces en los PDF.
- La única relación bidireccional necesaria: lectura larga ↔ crónica. Desde `site/covers/cronicas/index.html` cada tarjeta enlaza a ambas; desde la colección principal el JS inserta el enlace de crónica en cada tarjeta; N00 tiene enlace HTML directo.
- El CSS/JS del sitio usa cache bust `?v=cronicas-20261008` en `site/index.html`; no reutilizar versión vieja tras publicación.
