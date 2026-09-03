# METSI N00: handoff editorial final

Fecha: 2026-08-29, America/Argentina/Buenos_Aires

## Estado entregado

La revisión se realizó únicamente sobre el directorio original. No se abrió, consultó ni contactó la tarea inestable anterior y no se buscó, abrió ni modificó la copia de respaldo separada. Sólo se regeneró N00; N01–N10 permanecieron sin regenerar.

- PDF final: `N00/output/N00-METSI-lectura-previa-final.pdf`
- PDF bruto: `N00/output/N00-METSI-lectura-previa.pdf`
- Fuente canónica: `../metsi_content/lecturas_fuente_v8/N00_como_leer_metsi.md`
- Generador: `build_collection.py`
- Finalización y QA: `finalize_and_qa.py`
- Páginas: 43, todas A4
- Integridad fuente a HTML: PASS, 388 de 388 bloques
- QA final: PASS
- Encabezados faltantes: ninguno
- Fuentes prohibidas: ninguna
- Cierre: cero palabras y cero enlaces
- SHA-256 final: `1befe3dee3185cb41e9679ec7c60cf57ef4d53f4e9ee219d9f4377b6489a75de`

## Cambios editoriales cerrados

1. El bloque «Tu primera versión» es un espacio de escritura, no una pieza de contenido. Se eliminó cualquier fill saturado o aspecto de placeholder y quedó como papel blanco cálido, borde gris fino, regla volt superior y etiqueta mínima. Está en la página 31.
2. La portada ocupa el A4 completo, sin borde blanco.
3. La página 4 es una portadilla oscura a sangre completa, sin borde blanco.
4. La fotografía de la orquesta que antes cerraba N00 se movió inmediatamente después de la página 4. Ahora es la página 5 y lleva la frase: «Antes de intervenir, hay que aprender a escuchar lo que la representación todavía no explica.»
5. Se incorporó una segunda pausa fotográfica interna en la página 23, antes de la Parte II, con la frase: «Leer no es atravesar páginas. Es llegar con una posición que otras miradas puedan poner a prueba.»
6. La página final volvió a la secuencia canónica de fósforos. Es la página 43, ocupa la página completa y no contiene frase, caption, folio, firma ni enlace.
7. Referencias base quedó en la página 42, sobre fondo blanco, en dos columnas, sin barra volt/negra lateral.
8. Las seis fichas actuales de personajes de Hotel Horizonte tienen retratos de idénticas dimensiones y una retícula común. Esta regla subsume el pedido anterior referido a cinco fotografías.
9. La fotografía académica genérica fue reemplazada por una escena editorial generada que representa de manera verosímil a estudiantes argentinos/latinoamericanos. El archivo versionado es `N00/image-curation/selected/editorial-04-latam-v2.png`; el anterior no fue sobrescrito.
10. La fotografía de pasillo de la sección sobre IA fue reemplazada por una escena pertinente: dos estudiantes y un docente latinoamericanos revisando fuentes junto a una computadora. El archivo versionado es `N00/image-curation/selected/editorial-06-ai-latam-v2.png`; el anterior no fue sobrescrito.
11. Camila Duarte recibió un retrato nuevo y claramente diferenciado del de Mariela Benítez. El archivo versionado es `assets/hotel-portraits/camila-duarte-v2.png`; no existe reutilización del rostro de Mariela.
12. «Anatomía de una lectura N» ya no queda como título huérfano: comienza con su primer párrafo en la misma página.
13. «Preguntas de preparación» conserva una única tarjeta y quedó compuesta en dos columnas editoriales reales, numeradas 1–4 y 5–7, sin salto de página ni columnas internas duplicadas.
14. Las portadillas oscuras de Parte I, Parte II y Parte III ocupan los cuatro bordes del A4; no conservan bandas blancas de pie o laterales.
15. El área «Tu primera versión» de la página 31 quedó identificada explícitamente como campo de escritura. Ahora incluye una instrucción breve, cuatro renglones funcionales y menor altura; ya no se percibe como un bloque blanco vacío o un placeholder.
16. Las 36 descripciones del «Índice comentado de los 36 Núcleos» quedaron normalizadas al voseo rioplatense: `situá`, `mostrá`, `convertí`, `seleccioná`, `compará`, etc. No quedaron imperativos de tuteo en esa serie.

## Secuencia de control visual

- Página 1: portada a sangre.
- Página 4: portadilla oscura de Parte I a sangre.
- Página 5: primera pausa fotográfica, orquesta y frase.
- Página 21: seis retratos de igual tamaño.
- Página 22: índice comentado de los 36 Núcleos.
- Página 23: segunda pausa fotográfica, aula y frase.
- Página 24: portadilla de Parte II.
- Página 25: «Anatomía de una lectura N» comienza junto con su desarrollo, sin título aislado.
- Página 31: ejercicio de Martina y área de escritura neutra.
- Página 34: «Preguntas de preparación» en dos columnas completas y sin salto.
- Página 36: portadilla de Parte III a sangre completa.
- Página 37: fotografía nueva y pertinente para la sección de IA.
- Página 42: Referencias base en doble columna minimalista.
- Página 43: fósforos, imagen única a página completa.

La plancha de contacto revisada está en `qa-contact-sheets/N00-contact-sheet.jpg`.

## Invariantes incorporadas para próximos documentos N

La skill reutilizable `metsi-compose-document` y sus referencias editoriales ahora establecen:

- exactamente dos pausas fotográficas internas a página completa, cada una con una frase breve, contundente, reflexiva y vinculada con el argumento;
- primera pausa después de la apertura canónica/página 4 y segunda pausa en una transición conceptual posterior;
- cierre adicional e invariable con la imagen canónica de fósforos, a página completa y sin texto ni folio;
- áreas de escritura blancas o blanco cálido, con borde neutro fino y regla volt discreta; nunca colores de depuración, fills saturados ni gradientes decorativos.
- toda foto explícitamente definida como pausa, hero, fondo, apertura, cierre o página completa debe tocar los cuatro bordes del A4; no se aceptan márgenes, bandas ni filetes blancos accidentales;
- una fotografía editorial autónoma se considera pausa y siempre ocupa una página completa a sangre; sólo pueden permanecer insertos los retratos, la evidencia documental, los detalles instructivos o las imágenes que formen parte semántica del argumento circundante;
- títulos, consignas, llamados a la acción e instrucciones dirigidas al estudiante usan castellano rioplatense argentino y voseo consistente; no se mezclan `situá`, `mostrá`, `seleccioná` o `compará` con formas de tuteo como `sitúa`, `muestra`, `selecciona` o `compara`;
- en escenas académicas, estudiantiles o laborales situadas localmente, la imagen debe resultar verosímil para Argentina o Latinoamérica por el conjunto de personas, arquitectura, mobiliario, vestuario y contexto; no se valida ni se rechaza una imagen por tono de piel aislado;
- toda fotografía de portada se concibe y produce originalmente en blanco y negro, con iluminación, vestuario, materiales, contraste y separación tonal diseñados para monocromo; no se admite usar una fotografía concebida en color y convertirla después mediante desaturación o filtro de escala de grises;
- los retratos de personajes recurrentes deben conservar identidad propia y diferenciarse en estructura facial, edad aparente, peinado, encuadre y presencia; se rechazan duplicados o parecidos de parentesco no previsto por la historia;
- cualquier elemento ya aprobado queda cerrado: una corrección puntual debe superar comparación visual contra la versión anterior y no puede alterar páginas fuera del alcance solicitado.

Estas invariantes quedaron incorporadas en las skills reutilizables `metsi-compose-document` y `metsi-find-images`, además de la referencia `premium-magazine-system.md`.

## Procedencia de imágenes generadas en esta revisión

Las tres imágenes nuevas se produjeron con la herramienta integrada de generación de imágenes y se conservaron como activos versionados, sin reemplazar físicamente los archivos anteriores. Sus hashes están registrados en `N00/image-curation/image-manifest.json` y en el generador:

- `editorial-04-latam-v2.png`: grupo de estudiantes argentinos/latinoamericanos en trabajo colaborativo;
- `editorial-06-ai-latam-v2.png`: revisión humana de fuentes y resultado de IA;
- `camila-duarte-v2.png`: retrato documental nuevo de Camila Duarte.

La fuente N00 también explicita estas reglas para que el propio documento funcione como contrato editorial de la colección.

## Reproducción exacta

Desde `work/METSI-N02-v8` o ajustando las rutas equivalentes:

```bash
python3 build_collection.py --start 0 --end 0
python3 export_pdfs.py 0
python3 finalize_and_qa.py 0
python3 render_contact_sheets.py 0
```

No ejecutar el rango completo salvo autorización expresa, porque eso regeneraría N01–N10.

## Incertidumbre residual

El PDF sigue sin etiquetas estructurales de accesibilidad. La línea de base aprobada también carecía de ellas. Corregir esa limitación requiere cambiar el pipeline de exportación/finalización y no forma parte de esta revisión editorial.

La condición «argentino o latinoamericano» es una dirección de representación contextual, no una identidad verificable a partir de una fotografía ni un atributo que deba inferirse de un rostro. El control aplicado evalúa la plausibilidad editorial del conjunto y documenta esa limitación.
