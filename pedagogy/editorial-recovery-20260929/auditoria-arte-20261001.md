# Cierre de dirección de arte · N01–N36 · 1 de octubre de 2026

## Alcance y criterio

Se revisaron las 36 lecturas completas como interiores de revista, comparando las vistas de todas las páginas con la edición previa. El criterio no fue declarar aprobado un documento por conservar clases CSS o por tener una fotografía: se evaluaron aperturas ink, cambios de escala, pausas, diagramas, caso Hotel Horizonte, jerarquía, secuencias de páginas y cierres. Las tapas aprobadas se preservan píxel a píxel.

La auditoría inicial detectó tramos excesivamente continuos de texto y pérdidas puntuales de recursos editoriales. Se probaron intervenciones locales y se descartaron las que empeoraban la lectura —por ejemplo, repetir una imagen en N24 o mantener una pausa que dejaba media página vacía en N32—. El cierre se hizo sobre los PDF completos, no sobre fragmentos de HTML.

## Resultado por documento

| N | Decisión editorial final |
| --- | --- |
| 01 | Se recupera el elenco visual del caso y una página interior diferenciada. |
| 02 | Se conserva: reparto de voces, fotografía, mapas y cierres mantienen un ritmo deliberado. |
| 03 | Se introduce una pausa editorial en el argumento central. |
| 04 | Se incorpora una comparación visual de tres afirmaciones sin alterar la redacción. |
| 05 | Se conserva: la página breve de glosario cumple una función de consulta. |
| 06 | Se incorporan una taxonomía legible y un mapa de evidencias, no una lámina de rótulos diminutos. |
| 07 | Se conserva la secuencia editorial ya resuelta. |
| 08 | Se introduce una pausa tipográfica en el tramo central. |
| 09 | Se conserva: el cierre breve de glosario no se rellena artificialmente. |
| 10 | Se introduce una pausa editorial en el argumento central. |
| 11 | Se conserva: la síntesis breve final es una composición intencional. |
| 12 | Se conserva: la página de cinco ideas es una pieza de recapitulación. |
| 13–15 | Se conservan las aperturas, diagramas y variación de páginas existentes. |
| 16 | Se ajusta la secuencia central para interrumpir el bloque continuo de texto. |
| 17 | Se compone la decisión final como una doble página intencional, eliminando la continuación huérfana. |
| 18 | Se ajusta la pausa del tramo central. |
| 19–22 | Se conservan las composiciones editoriales revisadas página por página. |
| 23 | Se recupera la pausa fotográfica de consecuencias. |
| 24–26 | Se conservan, sin duplicar fotografía ni confundir páginas de síntesis con fallas. |
| 27 | Se introduce una pausa editorial en el tramo central. |
| 28–29 | Se conservan sus infografías y el ritmo interior ya recuperado. |
| 30 | Se incorpora una comparación visual de telemetría y se convierte el cierre aislado en interludio tipográfico ink. |
| 31 | Se conserva. |
| 32 | Se reequilibra la secuencia: se descarta la versión que creaba una hoja semivacía. |
| 33–36 | Se conservan tras revisar sus páginas completas, recursos y cierres. |

Por tanto, **13 PDF cambian** (N01, N03, N04, N06, N08, N10, N16, N17, N18, N23, N27, N30 y N32) y **23 quedan idénticos byte a byte**. Idéntico no significa aprobado sin inspección: en esos 23 se verificó el interior y se eligió no introducir decoración o cortes sin una mejora clara. Esta pasada no reescribe la redacción académica aprobada ni rediseña las tapas.

## Control de salida

- 36 tapas comparadas por imagen renderizada: idénticas píxel a píxel a las aprobadas.
- 9.872 bloques de origen verificados en los candidatos: ninguno ausente ni cambiado.
- 36 PDF completos revisados con control geométrico: sin texto fuera de página ni superposiciones detectadas.
- Las páginas de baja densidad detectadas automáticamente se inspeccionaron a tamaño de lectura; las síntesis y glosarios breves se conservaron cuando su brevedad era funcional.
- Los HTML de los 36 candidatos se regeneraron desde el constructor y coincidieron byte a byte con la versión de revisión.
- Los enlaces a bibliografía y al atlas se recalcularon con la paginación final al instalar los PDF locales. La publicación se confirma aparte, después de comprobar el sitio en línea.

El commit público anterior es el respaldo recuperable de los PDF previos. El registro de instalación `art-pass-20261001.json` conserva hash anterior y nuevo, paginación y archivos reemplazados.
