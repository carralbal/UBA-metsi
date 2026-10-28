# N00 · recibo de revisión post-Cecilia · 28/10/2026

## Alcance

La lectura N00 conserva las 55 páginas digitales A4 del PDF público previo: 49 páginas de cuerpo y las seis páginas aprobadas del mapa de aprendizaje. La portada y las seis páginas del mapa son idénticas píxel a píxel a la versión publicada anterior. El texto nuevo distingue dos puertas de entrada a METSI: un pedido de solución y una oportunidad observada sin encargo. Ambas conducen a investigar antes de decidir; no se crea una segunda entrega.

La fuente editable recuperada contiene 391 bloques identificados. Se restauró un párrafo del PDF público que faltaba en esa fuente, se eliminó una hoja vacía introducida por un contenedor HTML vacío, se recompuso el PDF con el ensamblador semántico anterior y se reinsertó el mapa aprobado. Se corrigieron cuatro números impresos del índice, el orden de lectura de las siete preguntas al pasar de página y una barra negra que sobresalía de un recuadro. Los cambios no sustituyen el caso longitudinal ni el mapa visual.

## Puertas de control de la candidata

- `QA-POST-CECILIA-20261028.json`: PASS. SHA-256 de la candidata `53ef97cb0f147b215aaf7c73639e7bde7d7c907720ac00be7e8a844803828336`.
- 55/55 páginas A4; portada y mapa (páginas físicas 1 y 14–19) idénticos visualmente al público; etiquetas de página conservadas.
- Estructura etiquetada, idioma `es-AR`, 98 entradas de índice PDF, 36 destinos con nombre, 120 enlaces y cero errores de navegación.
- Ensamblado del cuerpo: `PASS_MACHINE_CHECKS_PENDING_VISUAL_REVIEW`; cero imágenes faltantes, cero bloques ocultos, cero pérdida de roles semánticos respecto de la fuente renderizada.
- Índice visible contrastado con sus destinos; siete preguntas en secuencia 1–7. Revisión visual de las 55 páginas en cinco planchas y de las páginas cambiadas de apertura, índice y preguntas/producto a mayor escala.
- No se afirma aprobación del equipo docente, preprensa ni aptitud para imprimir: esta es una revisión digital del contenido post-Cecilia.

## Reproducción y estado

Fuente editable de trabajo: `N00/index.html`, `N00/magazine.css`, `N00/revision-local.css`, `standard-v7.css`, `corrections.css`, `N00/assets/`, `N00/diagrams/`. La portada y el mapa tienen fuente/versiones previas rastreadas en Git; `baseline.py` recupera el PDF público anterior desde el commit inmutable `1b9a546d5442bb9d674fb8147e2a1174db6a6aec` y comprueba su SHA-256. Las rutinas `scripts/render_n00_post_cecilia_20261027.mjs`, `assemble_proper.py`, `assemble_pdf_patched.py`, `insert_route_patched.py`, `restore_outlines.py` reconstruyen la candidata. El ensamblador requiere además el finalizador editorial del paquete de recuperación de fuentes de octubre. Las correcciones de paginación del índice son parte explícita del renderizador y se comprueban al compilar.

**Estado al escribir este recibo:** candidata validada localmente; publicación y cotejo remoto pendientes. No confundir el nombre histórico del enlace estable `v4-recorrido` con la fecha de esta revisión de contenido.
