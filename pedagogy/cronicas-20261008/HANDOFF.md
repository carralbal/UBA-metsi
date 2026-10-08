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
   - **Despliegue sin permiso de workflow**: el primer intento de `git push` fue rechazado porque el token GitHub de esta cuenta no tiene scope `workflow`; el commit intentaba modificar `.github/workflows/deploy-pages.yml` para añadir `site/cronicas` al artefacto. Se revirtió ese cambio antes del push exitoso y se trasladó la sección a `site/covers/cronicas`, dentro de `site/covers`, carpeta que el workflow existente **ya** copia a Pages con `lfs: true`. El commit publicado no cambia el workflow.
6. **Generador**. `scripts/build_cronicas.py` produce las páginas, índice, metadatos y una compilación local de 37 páginas en `../../output/pdf/METSI-cronicas-N00-N36.pdf` relativa al repo (raíz del proyecto ChatGPT). Tiene fallback para los PDF de pilotos ya publicados si el archivo fuente externo no existe en un clon nuevo. **No publicar la compilación de 107 MB**: supera el límite de 100 MB por archivo de GitHub. Publicar sólo los 37 individuales; la compilación es prueba local y no está enlazada.
7. **QA automatizada realizada**: 37 archivos N??.pdf, una página A4 cada uno; 37 titulares únicos; 27 casos locales/LATAM; 81 hipervínculos PDF; todos enlazan a fuente y lectura; ningún PDF contiene la cadena “Hotel Horizonte”; índice con 37 tarjetas; compilación local con 37 páginas; `node --check site/metsi.js` sin errores; render de contacto de las 37 páginas revisado. Se inspeccionaron visualmente N00, N25, N31 a tamaño de página, y después se renderizaron y revisaron en contacto los siete casos globales nuevos N11/N18/N20/N23/N24/N29/N34. No se observaron desbordes en estos siete. Fotos piloto N00/N02/N25 verificadas prácticamente neutras (diferencia RGB media 0,21/0/0,36).

## Publicación y verificación final

- Commit de producto en `main`: **`ac6ebe1c1be9b8302d81d680aa40382cedebb0bb`**. Push exitoso a `https://github.com/carralbal/UBA-metsi.git` el 8 de octubre de 2026.
- Workflow de Pages del commit: `https://github.com/carralbal/UBA-metsi/actions/runs/37794322828`, estado **success**; checkout con LFS y ensamblado completados.
- Índice público `https://carralbal.github.io/UBA-metsi/covers/cronicas/`: **HTTP 200, `text/html`**.
- Los 37 enlaces públicos `.../covers/cronicas/pdf/N00.pdf` a `N36.pdf`: verificados uno por uno mediante HEAD, **37/37 HTTP 200, `application/pdf`**. N00, N25 y N36 se descargaron completos para comprobar tamaño de PDF real (2,86 MB, 3,18 MB y 3,46 MB respectivamente; no punteros LFS).
- Home público `https://carralbal.github.io/UBA-metsi/`: su HTML ya contiene el enlace “Explorar las crónicas” en la biblioteca y el enlace directo a la crónica N00. El JS `site/metsi.js` agrega los vínculos N01–N36; se verificó sintácticamente con `node --check` y la estructura de tarjetas permite la inserción.
- La validación local final verificó 37 PDF A4 de una página, 37 titulares únicos, 27 casos Argentina/LATAM, 81 hipervínculos totales dentro de PDF, ninguna mención a Hotel Horizonte, 37 tarjetas en el índice y 37 rutas existentes a las lecturas N originales.

## En proceso

- **Nada pendiente de implementación o publicación para esta solicitud.** El usuario dijo que validará directamente sobre el resultado final; su revisión editorial puede originar una siguiente iteración. Si algún título/caso/foto no lo convence, modificar `articles.py` o las imágenes, ejecutar el generador y publicar un nuevo commit.
- Este handoff final se completó **después del despliegue verificado**. El commit de producto publicó los artículos; una actualización documental posterior deja asentado el estado final para cualquier chat nuevo.

## Falta / próximos pasos posibles, no bloqueantes

1. Esperar la evaluación del usuario sobre los 37 artículos y la integración. No pedirle otra validación para declarar esta entrega terminada: pidió comprobar sobre producción, y producción ya está verificada.
2. Si se decide mejorar la serie, respetar el criterio de 70% casos Argentina/LATAM, foto B&N ilustrativa, fuente primaria enlazada, título hook y una página exacta. No tocar el diseño ni el contenido de los documentos N sin un pedido nuevo.
3. Opcional: una comprobación visual en Safari móvil y escritorio del índice público. La navegación y los archivos fueron probados automáticamente, no se realizó una captura visual de navegador en producción.
4. La compilación local de 37 páginas está en `../../output/pdf/METSI-cronicas-N00-N36.pdf` relativa al repo; no está publicada porque pesa ~112 MB. No confundirla con los 37 PDF individuales publicados.

## Referencias y precauciones

- Proyecto real Git: `work/UBA-metsi-publication` bajo este proyecto ChatGPT. Rama `main`; remoto `https://github.com/carralbal/UBA-metsi.git`. Sitio servido desde `site/` por Pages. `sources/` de este proyecto es read-only; no se tocó.
- Los pilotos fuente externos de esta tarea, si siguen presentes: `output/pdf/METSI-cronicas-N02-piloto.pdf` y `output/pdf/METSI-cronicas-N25-piloto.pdf` en la raíz del proyecto ChatGPT. Ya están copiados a `site/cronicas/pdf/` para la entrega.
- Para N00 se utilizó una imagen generada B&N a partir de `N00-v2-candidate/assets/editorial-05.jpg`; archivo de serie `site/covers/cronicas/images/N00-bw.png`. Para N25 se utilizó edición B&N de la fotografía Pexels ya empleada en el piloto. No confundir fotografías ilustrativas con evidencia del caso.
- La mayoría de las fuentes son gubernamentales y primarias. Dos pilotos previamente aprobados tratan Horizon (UK) y la unidad de alta hospitalaria de St Thomas' (UK). N33 utiliza informe NIST 2026. Las URLs de las 37 fuentes están en `articles.py` y se incluyen como enlaces en los PDF.
- La única relación bidireccional necesaria: lectura larga ↔ crónica. Desde `site/covers/cronicas/index.html` cada tarjeta enlaza a ambas; desde la colección principal el JS inserta el enlace de crónica en cada tarjeta; N00 tiene enlace HTML directo.
- El CSS/JS del sitio usa cache bust `?v=cronicas-20261008` en `site/index.html`; no reutilizar versión vieja tras publicación.

## Ajuste del índice solicitado el 2026-10-08 (continuación)

### Pedido y diagnóstico exactos

El usuario validó la serie de 37 crónicas, pero señaló tres defectos en `https://carralbal.github.io/UBA-metsi/covers/cronicas/`: (1) el vínculo «Volver a la colección» debía verse durante todo el desplazamiento; (2) N00 exhibía un rectángulo gris sin contenido a la derecha; (3) cada tarjeta debía mostrar la fotografía de su artículo. El gris no era una imagen fallida: era el fondo de la grilla de tres columnas, expuesto porque N00 era su único ítem y ocupaba sólo la primera columna.

### Cerrado en el commit de producto `d70e0f48c999ab044e74ef64f4c81dff12fa8ee2`

1. `site/covers/cronicas/style.css`: encabezado `.top` ahora es `position: sticky`, con `top: 0`, z-index y fondo opaco paper. La navegación de regreso permanece visible al recorrer la colección. N00 se diseñó como `article.card.feature` de ancho completo, texto a la izquierda y foto a la derecha en desktop; se apila en móvil. Así desaparece la zona gris de la grilla vacía.
2. `scripts/build_cronicas.py`: el índice ahora incorpora un enlace fotográfico por tarjeta, con imagen local, alt, tamaño intrínseco y carga diferida salvo N00. `--index-only` permite regenerar únicamente índice/miniaturas sin tocar los PDF. La selección usa exactamente la fuente visual aprobada para cada artículo: N00, N02 y N25 utilizan sus imágenes especiales; N09/N10 usan las fotos editoriales de sus lecturas; el resto las fotos B&N de sus portadas. Se generan 37 recortes WebP de 840×525, gris neutro, en `site/covers/cronicas/images/cards/`.
3. `site/covers/cronicas/index.html` regenerado con 37 fotos, sus enlaces a la crónica/lectura y `style.css?v=cards-20261008` para evitar caché vieja. Se modificaron sólo estas 40 rutas (índice, CSS, generador y 37 WebP); ningún PDF ni la web principal se editó.
4. QA local: 37 tarjetas, 37 fotos existentes, 37 enlaces a PDF existentes, N00 marcado como una sola tarjeta destacada, CSS con llaves equilibradas, `git diff --check` correcto. Las miniaturas se inspeccionaron en dos planchas de contacto; no hay cuadros vacíos ni imágenes color. La desviación media máxima entre canales RGB de las miniaturas WebP fue 0,0242/255. Total de miniaturas: ~1,2 MB. Se confirmó que el commit no incluye PDF ni archivos ajenos.
5. Remoto validado: cuenta GitHub `carralbal`, repositorio público `carralbal/UBA-metsi`, rama `main`, remoto `https://github.com/carralbal/UBA-metsi.git`. Push de `d70e0f4` exitoso.

### Publicación comprobada: cerrado

- Despliegue de Pages de `d70e0f4`: `https://github.com/carralbal/UBA-metsi/actions/runs/37800634956`, estado **completed/success**. Checkout, ensamblado, subida del artefacto y Deploy terminaron correctamente.
- URL pública final: `https://carralbal.github.io/UBA-metsi/covers/cronicas/`. La página viva contiene **37 tarjetas, 37 referencias a imágenes distintas `images/cards/N??.webp`, una única `card feature` N00** y la versión CSS `cards-20261008`.
- CSS público: HTTP 200 `text/css` y contiene `.top{position:sticky;top:0` y `.card.feature{grid-column:1/-1`. Esto verifica la publicación de las reglas, aunque no se hizo captura visual de un navegador en producción.
- Muestras públicas N00, N02, N25 y N36: todas HTTP 200 `image/webp`, con tamaños reales de 37.948, 42.876, 47.826 y 45.702 bytes. El índice en vivo mostró las 37 rutas; las 37 imágenes existen en el artefacto local publicado por `cp -R site/covers`.
- Ninguna lectura N ni PDF de crónica fue reeditado para este ajuste. El índice y sus archivos nuevos están publicados; no queda ningún trabajo de implementación abierto.

### En proceso

Nada. El usuario revisará directamente la versión pública y podrá pedir ajustes nuevos.

### Falta / sólo si hay una nueva iteración

1. Recoger la opinión del usuario sobre el diseño de tarjetas y fotos. No cambiar títulos, artículos ni PDF sin un pedido nuevo.
2. Si se regenera el índice, usar el Python del runtime con Pillow/ReportLab/pypdf y ejecutar `scripts/build_cronicas.py --index-only`; esta opción conserva los PDF. Revisar que N02/N25 sigan usando sus fotos piloto especiales y que N00 abarque toda la fila.
3. Opcional no bloqueante: inspección visual en navegador móvil/escritorio. La estructura, las fotos y el CSS se verificaron local y públicamente; no hay captura de navegador en esta continuación.

### Precaución sobre la puerta de publicación heredada

Se intentó la verificación global `verify_publishable.py` de la skill sobre toda la carpeta de trabajo, pero reporta decenas de archivos **preexistentes, no incluidos en este commit**: PDF locales de impresión >100 MiB y symlinks en carpetas temporales o `node_modules`. No borrar ni mover esos trabajos del usuario sólo para hacer pasar el escaneo global. La carga publicada se limita a `site/` mediante el workflow existente; se inspeccionó el staged diff y se verificaron las 40 rutas nuevas/modificadas. El gate global no es una señal de fallo de estas miniaturas.

## Nueva ronda editorial: piloto narrativo N02 · 2026-10-08

### Pedido y alcance exactos

El usuario aprobó **la estética visual** de cada crónica, pero rechazó su escritura: poco profunda, telegráfica, sin un hilo conductor atrapante ni placer de lectura. Pidió volver a empezar con **un solo piloto**, elegido por Codex, escrito «con tinta de periodista y contador de historias». La tarea actual es únicamente el texto para que él evalúe el rumbo; **no autoriza aún** a reescribir los 37 PDF ni a publicar esta versión.

### Decisión editorial y fundamento

Se eligió N02, sobre el escándalo Horizon del correo británico, porque el usuario había elegido explícitamente su hook «Avisaron que el sistema fallaba. Los acusaron a ellos». Se conserva el título. Se usó la historia documentada de Lee Castleton: llamadas de enero de 2004, auditoría de marzo, litigio de 2007, consecuencias para la familia, hallazgos generales sobre Horizon en 2019, informe de la investigación pública en 2025 y litigio aún activo en 2026. El texto evita una afirmación no probada: **el fallo general de 2019 no demuestra por sí solo qué originó cada discrepancia concreta en la sucursal de Castleton**. Esa cautela es parte del argumento central sobre investigación y juicio profesional, no una nota técnica que deba omitirse.

### Cerrado en esta ronda

1. Se leyó el PDF N02 actualmente publicado (`site/covers/cronicas/pdf/N02.pdf`) para comparar. Tiene una primera escena genérica, cita institucional y explicación conceptual correcta, pero demasiados saltos y poca vida narrativa. No se modificó.
2. Se verificaron fuentes primarias oficiales: declaración de Anne Chambers ante la investigación (llamados del 14, 21 y 28 de enero de 2004); expediente de la auditoría y litigio; informe oficial Volume 1 de 2025 (deuda y afectación de Millie Castleton); fallo de 2019; palabras de Sir Wyn Williams de julio de 2025; ficha judicial del nuevo litigio de 2026. Las URLs y la precisión factual están al pie del nuevo piloto.
3. Se redactó un piloto completo con escena cronológica, escalada de la cifra hasta la quiebra, consecuencia familiar, giro interpretativo, concepto explícito de N02 y analogía cercana con inscripción universitaria. El cierre es una pregunta que retoma el conflicto, no un resumen en tono de manual. Texto íntegro guardado en `pedagogy/cronicas-20261008/N02-piloto-reescritura.md` para revisión y posible producción posterior. El artículo tiene unas 570 palabras antes de las fuentes (el archivo completo, con fuentes y nota de estado, tiene 731 palabras).
4. No se tocaron `articles.py`, el generador, el sitio, los PDF ni ningún archivo de producción. No hubo commit ni push por este piloto.

### En proceso

- Presentar el texto N02 completo en la respuesta de chat, con enlaces a fuentes oficiales cerca de los hechos, y recoger evaluación editorial del usuario. Como el usuario pidió una prueba, no debe darse por aprobada ni publicar en esta ronda.

### Falta / ruta de continuación exacta

1. Si el usuario pide ajustes, revisar el texto del piloto preservando los hechos verificados, su cautela causal y el hook aprobado; evitar hacerlo más corto hasta que vuelva a sonar a telegrama. Preguntar sólo si un giro estilístico depende de una preferencia material que no se pueda inferir.
2. Si aprueba el tono, definir la longitud definitiva compatible con una carilla y luego adaptar el contenido de N02 al PDF **sin cambiar su estética aprobada**. Antes de remaquetar 37 piezas, producir una prueba real y comprobar que el texto entra sin reducir tipografía a tamaño ilegible ni cortar contenido. Posteriormente escalar el método a N00–N36 con casos ya documentados y el balance de ~70% Argentina/LATAM, citando fuentes primarias; revisar cada texto y render.
3. No modificar las lecturas largas N00–N36 ni sus portadas: esta ronda concierne sólo a las crónicas periodísticas complementarias. No publicar el piloto sin una instrucción nueva y explícita de hacerlo.

## Reescritura integral y fotografías propias de la serie · 2026-10-08

### Pedido vigente y alcance

Tras aprobar el piloto N02, el usuario pidió rehacer **todas** las crónicas N00–N36 con más profundidad y un hilo narrativo periodístico. Exigió que la imagen de cada ficha del índice sea la misma que la del PDF correspondiente, y que **no** se reutilicen las imágenes habituales de Hotel Horizonte ni las portadas de las lecturas N. La estética base de la crónica y del índice ya estaba aprobada; no se rediseñó el sitio principal ni se tocaron las 37 lecturas largas.

### Cerrado y verificable en el árbol de trabajo

1. `pedagogy/cronicas-20261008/narratives.py`: 37 historias completas, aproximadamente 318–567 palabras cada una, con apertura de escena, secuencia causal, caso documentado, concepto explícito de la N y cierre que retoma la pregunta. N02 conserva el texto del piloto aprobado de Lee Castleton/Horizon. El balance de casos es 27/37 Argentina o América Latina (73%). Las fuentes primarias de los casos siguen en `articles.py`; se contrastaron adicionalmente los pasajes de N25, N28, N32 y N34 con las fuentes oficiales. Ninguna historia menciona Hotel Horizonte ni presenta fotografías ilustrativas como registro del caso.
2. `scripts/curate_cronica_photos.py` y tres manifiestos `image-candidates.json`, `image-selection.json`, `image-manifest.json`: búsqueda documentada de 209 candidatas; selección final de **37 fotografías distintas** de Unsplash con URL, creador, licencia y hash. Copias locales monocromáticas en `site/covers/cronicas/images/story/N00.jpg` a `N36.jpg`. Son fotografías editoriales específicas de esta serie; no proceden del hotel ni de las tapas N. Los créditos y la aclaración de que son ilustrativas constan en cada PDF. No se generaron fotografías de personas o casos ficticios.
3. `scripts/build_cronicas.py`: cada PDF N00–N36 usa su `images/story/N??.jpg` y la tarjeta web deriva su WebP `images/cards/N??.webp` **del mismo archivo**. El índice se regeneró con las 37 tarjetas y una versión de caché `narrativas-20261008` en imágenes/PDF. El enlace desde el sitio principal también usa la versión nueva en `site/index.html` y `site/metsi.js`.
4. Se conservó el lenguaje visual paper/ink/Volt, Didot/Baskerville/Avenir, foto panorámica, líneas finas y mucho aire. Para no volver al tono telegráfico ni hacer la letra ilegible, cada artículo ocupa **dos A4**: apertura/foto/primer desarrollo en la primera página y continuación/cierre editorial en la segunda. Son 74 páginas en total. La compilación local, no enlazada públicamente, está en `../../output/pdf/METSI-cronicas-N00-N36.pdf` relativa al repo y pesa ~26 MB.
5. `scripts/verify_cronicas.py` verificó **37 artículos, 74 páginas A4, 37 pares fotografía PDF/tarjeta, 0 fallos**: presencia de todo el texto en el PDF, título, ausencia de Hotel Horizonte, imagen derivada de la fuente exacta, 37 rutas y enlaces, licencias, fuente y lectura original. Renderizó las 74 páginas y siete planchas de contacto en `/private/tmp/metsi-cronicas-final-qa/`; se revisaron las siete sin desborde visible. El render inicial reveló un espaciado de caracteres acumulado en la continuación; se corrigió en `tracked()` y N02 volvió a revisarse a página completa, limpio.
6. El índice conserva la cabecera de regreso siempre visible, la tarjeta N00 destacada y la estética de la ronda previa. Las nuevas fotos están ya en la zona visual de cada tarjeta; no hay rectángulos de relleno vacíos.

### En proceso al escribir esta sección

- Preparar un commit acotado a esta serie, publicarlo en `main` y verificar GitHub Pages. El árbol compartido contiene **muchos archivos sin seguimiento de tareas anteriores** (auditorías de preimpresión, videos, pilotos de lecturas); no incluirlos ni borrarlos. Sólo stage de rutas de crónicas, handoff y versiones de enlaces de la web principal.

### Falta para cerrar la entrega

1. Ejecutar comprobación sintáctica de `site/metsi.js`, `git diff --check`, verificar exactamente los staged paths, commit y push a `origin/main`.
2. Esperar el workflow de Pages, comprobar el índice público y muestras de PDF/WebP con HTTP 200 y archivos reales. Si Pages falla, no afirmar publicación.
3. Registrar aquí commit, workflow y URLs verificadas. Avisar de forma transparente que el formato creció a dos páginas por artículo para sostener profundidad y lectura cómoda.

### Reproducción exacta en un nuevo chat

Usar el Python de runtime `/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3` (el `python3` del sistema no tiene Pillow). Desde `work/UBA-metsi-publication`, ejecutar `scripts/build_cronicas.py` y luego `scripts/verify_cronicas.py` con ese intérprete. No ejecutar de nuevo la etapa de curación salvo que se cambien fotos: los 37 originales y sus metadatos ya están preservados. El verificador deja PNGs y contactos en `/private/tmp/metsi-cronicas-final-qa/`. La fuente narrativa es `narratives.py`; `articles.py` sigue siendo la ficha de título, caso y URL primaria. Para publicar, stage selectivo: scripts de crónicas, carpeta `pedagogy/cronicas-20261008/`, `site/covers/cronicas/index.html`, `images/cards/`, `images/story/`, `pdf/`, `site/index.html` y `site/metsi.js`; no stage global.

### Publicación y verificación final de esta ronda · cerrado

- Commit de producto **`6c5ac8de37c630c5b4a9369e7672829f8bb457dd`** en `origin/main` (push correcto con 74 objetos Git LFS: 37 fotos fuente y 37 PDF, 47 MB transferidos). Sólo se incluyeron las 123 rutas de esta entrega; no se tocaron los archivos extraños/sin seguimiento del árbol compartido.
- Workflow de GitHub Pages [37842608728](https://github.com/carralbal/UBA-metsi/actions/runs/37842608728): **completed/success**, pasos Checkout, Assemble publication, Upload artifact y Deploy completos. El índice público `https://carralbal.github.io/UBA-metsi/covers/cronicas/` contiene las 37 rutas `images/cards/N??.webp?v=narrativas-20261008`.
- Comprobación pública exhaustiva: **37/37 PDF HTTP 200** y **37/37 WebP de ficha HTTP 200**. Se descargó además `N02.pdf` completo: HTTP 200, `application/pdf`, 1.256.680 bytes, no puntero LFS. La fotografía N02 WebP se descargó como `image/webp`, 76.892 bytes. La equivalencia entre cada imagen del PDF y la fuente de su tarjeta ya fue probada por `verify_cronicas.py` con 0 fallos.
- `node --check site/metsi.js`, `git diff --check` y `git diff --cached --check` terminaron sin errores antes del commit. La generación final produjo 37 PDF y la compilación de 74 páginas.

### En proceso tras la entrega

Nada de implementación pendiente. La serie pública queda disponible para la revisión editorial del usuario. Cualquier cambio posterior de estilo, longitud, caso, foto o diagramación es **nueva iteración** y debe preservar la correspondencia 1:1 PDF/ficha y la procedencia de fotos, sin volver a usar portadas N/Hotel Horizonte.

### Falta / opcional, no bloqueante

Una inspección visual de Safari móvil en producción podría confirmar el comportamiento del índice sticky; no es necesaria para validar esta entrega porque el CSS del índice no cambió en esta ronda y el despliegue/archivos fueron verificados. Si el usuario prefiere volver a una sola carilla por crónica, habrá que condensar texto o cambiar formato; hacerlo sin bajar legibilidad requiere una decisión editorial explícita. La elección vigente son dos páginas por artículo para conservar narrativa y tamaño de letra.

## Crónicas integradas en el home y grilla sin huecos · 2026-10-08

### Pedido y diagnóstico

El usuario mostró un hueco gris enorme junto a N04 en la colección de crónicas y pidió dos cambios: eliminar **todos** esos espacios grises y hacer visible la colección completa en la página principal, **por encima** de los documentos N, sin obligar a entrar en `/covers/cronicas/`. La zona gris no era una foto fallida: la grilla tenía tres columnas, cuatro tarjetas en A, y pintaba las dos celdas vacías con `--line`. Los bloques D/F de cinco tarjetas podían producir otro hueco.

### Cerrado en el árbol local

1. `site/covers/cronicas/style.css`: grilla de seis pistas con tarjetas normales de dos, última tarjeta sola a ancho completo con texto/foto en composición horizontal, y dos tarjetas finales a media anchura cada una. El fondo de la grilla ahora es paper, no gris. Las reglas residuales de escritorio se limitan a `min-width:851px`; en tableta se recompone en dos columnas y en móvil en una. El N00 sigue siendo destacado. El enlace sticky «Volver a la colección» ahora apunta directamente a `/#cronicas` del sitio principal.
2. `site/index.html`: la sección 10 empieza con introducción conjunta y muestra **las 37 crónicas en línea**, ordenadas N00, A–H; recién después aparece el bloque `id=lecturas` con guía N00 y las 36 tapas N. El antiguo banner de salida hacia la página separada se eliminó. La navegación principal incorpora «Crónicas» (`#cronicas`) y «Lecturas» (`#lecturas`); el CTA de descargar apunta a las lecturas. Fotos, títulos, bajadas y dos enlaces por ficha son visibles sin salir del home.
3. `site/metsi.css`: nuevo componente editorial `chronicles-home` con portada visual N00, grupos, tarjetas con foto y fondos paper/ink/Volt. Usa también seis pistas y reglas para llenar la última fila en escritorio, dos columnas en tablet y una en móvil. Las imágenes `loading=lazy` en el home evitan cargar las 37 fotografías al iniciar la página.
4. `scripts/build_cronicas.py`: una sola función `card_sections()` genera tanto el índice legado como el bloque del home, con rutas relativas correctas; `static_home_collection()` reemplaza sólo el contenido entre `<!-- BEGIN home chronicles cards -->` y `<!-- END home chronicles cards -->`. `--index-only` regenera ambas vistas **sin reescribir los 37 PDF ni las 37 fotografías**. Jerarquía semántica del home: título de sección h2, Crónicas h3, grupos h4, tarjetas h5.
5. `scripts/verify_cronicas.py` ahora verifica además 37 fichas y 37 fotos/PDF en el home, anclas distintas para crónicas/lecturas, orden correcto y ausencia del banner antiguo. La verificación previa de 37 PDF A4 de dos páginas, contenido íntegro y coincidencia visual entre fotografía de PDF y tarjeta sigue vigente.

### QA local hecha / límites

- El generador `--index-only` terminó correctamente; no hay PDF ni WebP modificados en el diff. `lxml` parseó el home: **37 fichas**, grupos `[1,4,6,6,5,4,5,3,3]`, `#cronicas` antes de `#lecturas`. Las llaves CSS están equilibradas; `git diff --check` correcto.
- La puerta global de publicación aplicada al árbol completo falla por PDFs/ZIP >100 MiB y symlinks **preexistentes, ajenos a este cambio y fuera del artefacto de Pages**. Para verificar el objeto que realmente se publica, se hizo una copia temporal copy-on-write de `site/` con manifest y workflow en `/private/tmp/metsi-site-gate-dR8wpN`; `verify_publishable.py` devolvió **ok:true, 373 archivos, 580.594.766 bytes, 0 errores**. Único aviso: no hay licencia general del repositorio, coherente con no conceder reutilización automáticamente. No se borró ni incluyó material ajeno para sortear el escaneo.
- Se intentó abrir una vista local mediante el navegador integrado, pero su comprobación de seguridad administrativa no autorizó `http://127.0.0.1:8765`; se cerró el servidor de prueba y **no se intentó sortear esa política**. La inspección visual final debe hacerse sobre la URL pública si el navegador lo permite; en lo local se verificó estructura, reglas de grilla y archivos.
- No se modificaron textos de crónicas, PDFs N, imágenes fuente ni tapas N. Hay numerosos archivos sin seguimiento de tareas previas; no incluirlos ni borrarlos.

### En proceso

- Terminar la última ejecución de `scripts/verify_cronicas.py`, revisar el diff acotado, commit, push a `origin/main`, esperar Pages y comprobar que el home público contenga las 37 fichas antes de dar por cerrado.

### Falta / continuación exacta

1. Publicar sólo `scripts/build_cronicas.py`, `scripts/verify_cronicas.py`, `site/covers/cronicas/index.html`, `site/covers/cronicas/style.css`, `site/index.html`, `site/metsi.css` y este handoff. No stage global.
2. Después del despliegue, abrir `https://carralbal.github.io/UBA-metsi/#cronicas`, comprobar presencia de N00–N36 y que `#lecturas` quede después; revisar también `https://carralbal.github.io/UBA-metsi/covers/cronicas/` para asegurar que N04 ya no deje una gran zona gris. Registrar commit/run y HTTP aquí.
3. Si un navegador público permite inspección visual, verificar desktop y móvil. Si no, no afirmar una captura visual; sí se puede cerrar con QA estructural, CSS comprobado y despliegue exitoso.

### Publicación y estado final de esta ronda · 2026-10-08

- **Cerrado:** commit de producto `fe3cdff4acf3db1db5ebdb72817445a4f210743d` publicado en `origin/main`. El workflow [Deploy GitHub Pages 37850045682](https://github.com/carralbal/UBA-metsi/actions/runs/37850045682) terminó `success` con Deploy completo. El home público respondió correctamente al descargarlo y contiene exactamente **37 rutas de fotos de crónicas**. En el HTML publicado, `id="cronicas"` aparece antes de `id="lecturas"` (líneas 629 y 690 de la descarga de control) y se carga la versión nueva de CSS `cronicas-inline-20261008`. El verificador integral local terminó en **37 artículos, 74 páginas, 37 pares foto/PDF, cero fallos**. La colección independiente sigue enlazada, pero ya no es un paso obligatorio para encontrar las crónicas.
- **En proceso:** nada de implementación ni publicación. Esta adenda deja constancia del resultado posterior al commit de producto.
- **Falta / límite explícito:** no existe captura visual nueva del sitio. El navegador integrado rechazó tanto la URL local como la pública porque no pudo verificar su política administrativa; no se intentó sortearla. Una revisión visual de escritorio y móvil por el usuario sigue siendo deseable, sobre todo para confirmar ritmo y composición, aunque el CSS, el HTML público y Pages se verificaron. No cambiar historias, PDFs ni fotos como parte de esa revisión salvo pedido nuevo.
