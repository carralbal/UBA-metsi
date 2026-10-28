# Recibo QA · N10 post-Cecilia · 27/10/2026

## Estado

Versión digital candidata, comprobada localmente; **la publicación y el cotejo remoto todavía deben registrarse aquí**. No es aprobación académica docente ni prueba de imprenta.

## Fuente fiel y cambio curricular

- Base: PDF que el sitio servía antes de esta revisión, `site/pdf/N10-METSI-lectura-previa-v10-final.pdf`, 37 A4, SHA-256 `27d3542f7b19e946522204f21c92d44b16942e0ea70bfe8b57f87264330564c2`.
- Fuente final: `N10-v12-post-cecilia/N10/index.html`, procedente de `output/source-recovery-20261024/N10-imac-source-private/working/N10/index-v2-private.html`, que generó el PDF público de 37 páginas. **No** se usó como reemplazo el borrador anterior de 38 páginas `N10-bridge-v3`, aunque informó siete cambios y mostró cómo evitar la hoja huérfana. Esto preserva la revisión editorial del 24/10.
- Se trasplantaron las siete sustituciones identificadas por IDs `N10-s08-b046`–`b050`, `N10-s13-b001`, `N10-s16-b001`: la transferencia hospitalaria ficticia comienza con una señal observada sin pedido de herramienta, contrasta explicaciones, mantiene autoridad clínica y no aprueba IA. El caso no representa un hospital real ni fija umbrales clínicos.
- El ejemplo HH-10 resuelto conserva la rama reactiva y agrega **la misma ficha** si Lucía detecta una señal sin encargo. No crea una entrega; contrasta PMS a tiempo frente a correcciones de turno, hace explícita una condición de no iniciar, autoriza sólo investigación acotada y reserva prefactibilidad para la puerta siguiente. Las pistas son didácticas, no hechos empíricos del hotel.
- Los 274 bloques de fuente originales siguieron visibles; ningún ID se retiró. Se conservó el caso HH, referencias, fotografías y diagramas ya publicados.

## Verificación local

- Render del paquete editable independiente: 37 A4, 274 bloques visibles, ocho hojas CSS y cero imágenes faltantes. Texto normalizado idéntico página por página al render usado para el ensamblado.
- PDF final local `N10-post-cecilia-from-current-20261027/fullbleed-v1/N10-METSI-fullbleed-editorial-A4.pdf`: 37 A4, 21.047.262 bytes, SHA-256 `6bf82a6b99e137467c8f2ac71bb92dd548e410da2bcb7895cf5bc323b3e2a5fc`.
- La tapa pública fue preservada por corriente de dibujo, texto, cajas y píxeles idénticos según el ensamblador. Navegación: 20 destinos nombrados, 21 enlaces internos, 149 URL, cero errores. Texto buscable y árbol de estructura etiquetada preservados por el acabado digital a borde de pp. 4, 5, 21 y 37.
- Planchas de contacto de 37/37 páginas inspeccionadas; pp. 26 (transferencia) y 28 (HH-10) abiertas ampliadas. No se observaron solapes o cortes. `pdfplumber`: cero caracteres fuera de A4, cero caracteres de menos de 5 pt. Advertencia no fatal `FontBBox` durante el acabado; PDF abierto y renderizado.
- La comparación de texto con el PDF público anterior conserva 37/37 páginas. Las diferencias sustantivas se concentran en pp. 26, 28, 32 y 35; cambios mínimos en otras hojas son de extracción/maquetación, no se detectó pérdida de contenido en los 274 bloques reconciliados.

## Pendiente

Publicar PDF y fuente, verificar GitHub Pages y cotejar SHA de descarga remota. Ensayar con docentes la lectura N01→N10 y el tiempo de la misma ficha; no declarar aprobación académica, validación humana de accesibilidad o aptitud de imprenta por este control.
