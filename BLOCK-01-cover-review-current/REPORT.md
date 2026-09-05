# Auditoría comparativa de portadas · N00 a N10

## Alcance

Esta revisión compara la portada del candidato N00 v2 con las versiones finales vigentes de N01 a N10. Es una auditoría de sólo lectura: no se modificó ningún PDF cerrado.

## Conclusión ejecutiva

La serie tiene calidad editorial y funciona como familia. Las once fotografías llegan a sangre, se presentan en blanco y negro y conservan una variación tonal real. No corresponde volver a oscurecer todas las tapas con una capa negra general.

El problema principal no es la luminosidad global de las fotografías. Es el uso del color volt para una frase completa en tamaño pequeño sobre fondos fotográficos. El contraste numérico puede superar un umbral y, aun así, la frase perderse por textura, detalle, distancia de lectura y delgadez del trazo.

La solución de sistema recomendada es:

- reservar el volt para el círculo N, los paralelogramos, reglas y señales breves;
- componer la tesis de tapa en blanco papel cuando la zona sea oscura;
- componerla en tinta casi negra cuando la zona sea clara;
- cuando la fotografía cambie mucho dentro de la misma zona, usar sólo una base tonal local y gradual detrás de la tesis, nunca un velo sobre toda la página;
- conservar intactos título, masthead, fotografía y encuadre salvo que una tapa tenga un problema independiente.

N00 ya aplica esta regla: tesis blanca, fotografía con matices y volt limitado a la firma gráfica.

## Hallazgos de serie

- Las once páginas son A4.
- Los once bloques `LECTURA PREVIA` y `EDICIÓN 2026` se extraen correctamente.
- Ninguna tapa presenta marco blanco uniforme ni pérdida de sangrado.
- Las once composiciones renderizan en monocromo.
- La luminancia media va de 66,28 en N00 a 140,68 en N06. La amplitud confirma que la serie no es uniformemente oscura.
- N00 y N04 son las tapas más densas y oscuras.
- N06 y N10 son las más claras.
- N03, N06, N07, N08 y N09 requieren especial atención perceptiva en la tesis volt porque el fondo tiene detalle o valores medios, aunque el proxy matemático resulte aceptable.
- La diversidad tonal es valiosa. Conviene normalizar la legibilidad de la tipografía, no igualar todas las fotografías.

## Evaluación por portada

| Documento | Imagen y composición | Tono | Tesis actual | Decisión recomendada |
|---|---|---:|---|---|
| N00 | Orquesta y contrabajo. Imagen conceptual fuerte, con profundidad y lectura vertical. | Oscura, con grises recuperados | Blanca | Conservar el candidato. No agregar velo global. |
| N01 | Ruta de montaña. Metáfora clara, fotografía amplia y premium. | Media | Volt | Pasar la tesis a blanco. Mantener el relieve y la niebla sin oscurecerlos. |
| N02 | Recepción hotelera detrás de planos de vidrio. Excelente relación con el argumento. | Media oscura | Volt | Pasar la tesis a blanco; preservar la división espacial y el círculo. |
| N03 | Corredor y trabajo operativo. La frontera queda visible en la propia arquitectura. | Clara media | Volt | Usar tinta oscura o una base local mínima según prueba a tamaño real. No oscurecer el corredor completo. |
| N04 | Retrato profesional y reflejo. Fuerte y cinematográfica. | La más oscura después de N00 | Volt | Tesis blanca. Levantar apenas medios tonos sólo si la revisión de impresión pierde detalle en vestuario y fondo. |
| N05 | Equipo reunido alrededor de una mesa. Buena tensión entre actores. | Media oscura | Volt | Tesis blanca. Mantener la fotografía y el encuadre. |
| N06 | Profesional frente a un muro de trabajo. Conceptualmente precisa. | La más clara | Volt | Prioridad alta: tesis en tinta oscura. El volt se pierde sobre grises claros y papeles. |
| N07 | Conversación cara a cara. Clara relación con entrevista y escucha. | Media | Volt | Tesis blanca sobre la zona inferior; conservar el contraste natural de las figuras. |
| N08 | Trabajo operativo parcialmente oculto por la arquitectura. Muy pertinente. | Media | Volt | Tesis blanca o base local muy leve. No oscurecer el pasillo completo. |
| N09 | Persona y arquitectura institucional. Imagen sobria y profesional. | Media clara | Volt | Probar tinta oscura; si la trama arquitectónica interfiere, aplicar base local mínima. |
| N10 | Infraestructura, ciudad y circulación. Cierre visual amplio del Bloque 1. | Clara | Volt | Tesis blanca sobre la franja inferior ya oscura. Conservar el cielo claro y la profundidad. |

## Lectura estética

La serie evita la apariencia de banco de imágenes genérico porque cada fotografía traduce una operación conceptual distinta: escuchar, avanzar sin receta, reconocer fronteras, separar evidencia, identificar actores, investigar, entrevistar, observar y construir un problema. El masthead y la grilla sostienen continuidad sin volver idénticas las escenas.

El principal riesgo actual es jerárquico: el volt compite entre ser firma gráfica y ser color de lectura. Cuando transporta una frase larga, deja de comportarse como acento y se vuelve texto funcional. Al devolver la tesis a blanco o tinta, el volt recupera potencia y las fotografías conservan sus matices.

## Secuencia de implementación propuesta

1. Crear candidatos de portada solamente para N01 a N10, sin repaginar interiores.
2. Aplicar color contextual a la tesis: blanco o tinta según la zona fotográfica.
3. No modificar fotografía, recorte, masthead, título, círculo, paralelogramos ni pie.
4. Renderizar las diez variantes juntas y revisar primero la plancha, después cada tapa a tamaño completo.
5. Verificar extracción del eyebrow, sangrado, ausencia de halo y conservación exacta de todas las páginas interiores.
6. Someter el paquete comparativo a aprobación autoral antes de reemplazar o publicar ningún PDF.

## Archivos

- `contact-sheet-N00-N10-current.jpg`: comparación visual de las once tapas vigentes.
- `audit.json`: rutas, hashes, páginas y métricas reproducibles.
- `cover-N00.png` a `cover-N10.png`: renders de revisión de la primera página.

## Límite de la métrica

La medición de contraste incluida en `audit.json` es un proxy sobre la zona fotográfica de la tesis. No sustituye la inspección visual a tamaño real. El volt tiene luminancia alta, pero su trazo fino puede perderse sobre texturas y valores medios. Por eso la recomendación editorial es más estricta que el resultado numérico.
