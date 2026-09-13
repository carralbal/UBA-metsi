# METSI · Auditoría visual y semántica de N34 y guardas N00–N36

Fecha: 12 de septiembre de 2026  
Estado: candidato local, no publicado

## Alcance y conclusión

N34 se utilizó como caso diagnóstico. Los seis problemas señalados son reales. Cuatro provienen de decisiones compartidas por el generador N11–N36 y, por lo tanto, requieren una reconstrucción transversal. Dos exigen control documento por documento porque dependen de la semántica de cada tapa y de la densidad de cada infografía.

El contenido académico de N34 no presenta pérdida ni baja densidad: conserva 236 bloques fuente, 8.100 palabras según el manifiesto académico y 7.300 palabras sustantivas. El problema observado era editorial, no una ausencia de argumento.

## Resultado de N34 v9

| Control | Diagnóstico | Corrección aplicada | Estado |
|---|---|---|---|
| Infografía legible | La lámina estaba encajada dentro de la tesis y su cuerpo quedaba por debajo de una escala razonable. | Se separó como lámina A4 completa. La tesis comparte página con el puente conceptual. | PASS visual |
| Tapa sin sesgo semántico | La imagen anterior convertía “gobierno” en edificio estatal, bandera y escena institucional. | Nueva fotografía concebida originalmente en blanco y negro: profesional con expediente en corredor operativo de hotel, sin símbolos partidarios ni gubernamentales. | PASS visual |
| Referentes regionales y retratos | N34 no tenía una voz argentina o latinoamericana; David Snowden aparecía en plano general. | Se incorporó a Paulo Freire en argumento, Referentes y bibliografía. Snowden se recortó a plano de retrato sin inventar una imagen. | PASS |
| Contraste del marcador | Volt sobre blanco producía un círculo débil y una función cromática confusa. | Círculo papel, número negro y borde negro. Volt queda reservado a acentos. | PASS |
| Ancla Hotel Horizonte | El archivo compartido era pequeño, monocromo y se pixelaba al escalar. | Nueva ancla canónica de mayor resolución, con diagonal preservada y color natural desaturado. | PASS visual |
| Personajes Hotel Horizonte | Había escalas de rostro diferentes y descripciones genéricas. | Se normalizaron encuadres y se escribieron posiciones específicas para el problema de N34. | PASS visual y semántico |

## Auditoría determinística del candidato

- PDF A4, etiquetado y con 27 páginas.
- 236 de 236 bloques fuente presentes, sin faltantes ni bloques inesperados.
- Fuente canónica v3: SHA-256 `9e4734540c7eb6c3a1d3d03a63f30bd53086466f4db974fef0acb2c13f23785a`.
- PDF final: SHA-256 `c312447195b707a30ba2c07c7e58edc4ab4db11fbdc5b453b8c47761e1d5dff4`.
- Tamaño del PDF: 21.073.884 bytes.
- La única página con menos de la mitad según extracción de texto es la pregunta profesional, que es una portada argumental deliberada a página completa. Su fondo y composición ocupan toda la página. No hay páginas ordinarias involuntariamente vacías.

## Qué es transversal y qué no

### Defectos transversales confirmados en N11–N36

1. El marcador de sección heredaba la combinación volt sobre papel. La corrección debe regenerar los 26 PDFs.
2. El ancla inclinada de Hotel Horizonte utilizaba el mismo archivo de baja resolución. La nueva ancla debe reemplazarse en los 26 PDFs.
3. El panel de seis personajes reutilizaba encuadres sin normalización suficiente. La escala debe auditarse y normalizarse en los 26 PDFs.
4. Las posiciones de los personajes eran demasiado genéricas. Deben redactarse para el conflicto específico de cada N, no copiarse como ficha fija.
5. Los seis Referentes de N11 a N33 no incluyen una voz argentina o latinoamericana, aunque la distribución aprobada sí incorporó autores regionales dentro del cuerpo. La presencia en el argumento no reemplaza la visibilidad editorial de Referentes.

### Controles que requieren auditoría individual N00–N36

1. Tapa: la imagen no debe derivarse literalmente de una palabra ambigua del título. Se revisará el brief visual de cada N contra el argumento completo, buscando sesgos políticos, institucionales, clínicos, policiales o tecnológicos no intencionales.
2. Infografía: no alcanza con validar el SVG aislado. Se medirá la escala final embebida en el PDF. Una lámina densa debe recibir una página completa o dividirse semánticamente; nunca reducirse hasta resultar ilegible.
3. Referentes: cada retrato debe ser primer plano o plano corto coherente y conservar una fuente y derechos verificables. Un recorte documental es admisible; inventar o atribuir un rostro no lo es.
4. Hotel Horizonte: además del encuadre común, cada documento debe explicar qué sostiene, cuestiona, observa o autoriza cada personaje frente al tema de ese N.

## Guardas para la próxima reconstrucción

- Infografía: auditoría sobre el PDF final al 100 %, no sobre el archivo SVG. Texto principal visualmente equivalente a 7 pt o más; si no se alcanza, se rediseña o divide.
- Tapa: brief construido desde la pregunta profesional y la tensión, con lista explícita de símbolos prohibidos por sesgo.
- Referentes: seis fotografías válidas, plano corto consistente y al menos una voz argentina o latinoamericana cuando exista una contribución académica pertinente, sin cuotas ornamentales.
- Marcador: papel, negro y volt con funciones separadas; nunca volt como texto pequeño sobre blanco.
- Hotel: ancla canónica a color desaturado, resolución suficiente, oblicua consistente, seis encuadres homologados y seis posiciones específicas.
- Regresión: revisión visual de tapa, Referentes, pregunta profesional, Hotel, infografía, píldoras, glosario, preguntas y referencias en cada PDF regenerado.

## Nombre de la materia en el sitio

No aparece la expresión “Metodología del Estudio de los Sistemas de Información”. El sitio local publicado utiliza “Metodología de los Sistemas de Información” en la descripción, el eyebrow y el pie. Los PDFs utilizan “Metodología de Sistemas de Información”. Debe decidirse una única forma oficial y aplicarla de manera consistente; la diferencia actual es el artículo “los”.

