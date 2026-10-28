# Recibo QA · N01 post-Cecilia · 27/10/2026

## Estado

**Versión digital lista para publicación; falta cotejo remoto de GitHub Pages.** No equivale a aprobación académica del equipo docente/Cecilia ni a preprensa.

## Procedencia y reconciliación

- Fuente fiel del PDF público vigente antes de la intervención: `site/pdf/N01-METSI-lectura-previa-v19-final.pdf`, 36 páginas, SHA-256 `580bf3499b39b2d4d58cd378e233749983e9eea402ebc1df03c0f0b54a8bd73c`.
- Ensayo privado de doble origen: `../UBA-metsi-publication/output/source-recovery-20261019/N01-regeneration-pilot/candidate-working/N01/index.html`. No se publicó el ensayo por ser más reciente: se comparó página a página con el PDF público y se conservaron todos los pasajes no afectados.
- Paquete editable final: `N01-v22-post-cecilia/N01/index.html`, seis hojas de estilo cargadas y 223 bloques con ID. Los 223 IDs previos se conservan; cambia el texto de ocho páginas (4, 10, 13, 26, 28, 29, 31, 34). Los cambios expresan pedido **o** oportunidad detectada sin pedido, el mismo HH-01 con campo `Origen`, preguntas de preparación y un caso de transferencia ficticio de turnos de salud. El resto del texto académico público permanece igual normalizando espaciado y diferencias de extracción tipográfica.
- El caso de salud es **didáctico, no una noticia ni un dato empírico**. La cifra 24 % y los diez episodios son supuestos declarados para enseñar a investigar antes de comprar.
- La sección de referencias volvió a p. 35, como en el PDF público; el índice se sincronizó con ese destino. No se retiró ninguna referencia.

## Maquetación y verificación local

- PDF final local: `N01-post-cecilia-20261027/fullbleed-v3/N01-METSI-fullbleed-editorial-A4.pdf`, 36 páginas A4, 29.974.691 bytes, SHA-256 `53be797ea45234a654a29dbf445173cbbe23355a2a98948a6c72103cc28f6821`.
- La tapa pública se conservó por stream, texto, cajas y píxeles idénticos. 32 destinos internos y 41 enlaces internos preservados, 88 URL; sin errores de navegación. El aparato de referencias está completo en p. 35.
- Se eliminó la caja `paper` de la apertura `ink` p. 4: la guía de producto ahora es tipografía clara sobre el mismo fondo con regla lima. Las pp. 4, 5, 18 y 36 tienen acabado digital a borde. No se cambió el texto buscable al aplicar el acabado; el árbol de estructura etiquetada permanece.
- Planchas de contacto de las 36 páginas inspeccionadas; se abrieron además pp. 4, 27, 28, 34 y 35 ampliadas y las cuatro páginas con acabado. No se observaron cortes ni solapamientos. `pdfplumber`: cero caracteres fuera de página y cero caracteres de tamaño menor a 5 pt. Las seis imágenes de referentes de p. 3 están presentes. Una advertencia no fatal `FontBBox` ocurrió durante el acabado; el PDF abre, conserva texto y renderiza.
- El paquete editable se reimprimió de forma independiente: 36/36 páginas y texto normalizado idéntico al HTML ensayado, 223 bloques visibles, cero imágenes faltantes.

## Pendiente

Publicar, esperar Pages y comparar la descarga remota en bytes/SHA; probar con docentes la carga real de N01→N10 y comprobar que la segunda puerta no agrega una entrega al cuatrimestre. La validación humana de accesibilidad y la preprensa no forman parte de este recibo.
