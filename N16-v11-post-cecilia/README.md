# N16 · revisión post-Cecilia, versión publicada

Esta carpeta es la fuente editable única de la revisión publicada de N16. El PDF visible en el sitio es `site/pdf/publicados/N16-METSI-lectura-previa-v10-final.pdf` (41 páginas; SHA-256 `d3a1926e5bd2a838c1d7154c543061cf981addd9acf19be2aef04afbebb16020`). Se conserva el nombre de la ruta pública para no romper enlaces anteriores; la revisión vigente es `n16-post-cecilia-20261028`.

## Qué se incorporó

- Un caso ficticio separado de Hotel Horizonte para comprobar contradicciones entre proceso, datos y estados de una constancia. No describe una política real de FCE-UBA.
- Regla A: un episodio de reparación agrupa varios intentos sobre el mismo objeto y propósito, sin borrar fallos ni contar dos veces las esperas.
- Regla P1: una observación activa impide mostrar «Resuelto»; una decisión firmada requiere además entrega válida al titular.
- Los casos de prueba C-103 y C-107; C-107 registra observaciones secuenciales, no dos activas simultáneas. La constancia anterior no habilita una nueva comunicación ni cierra su reparación.
- Dos láminas aprobadas por el usuario, páginas 28–29, con paleta METSI monocroma y acento volt.

`N16/index.html` es el interior editable; las hojas de estilo, imágenes y SVG se resuelven dentro de esta carpeta. `protected-covers/definitive/N16.pdf` guarda sólo la primera página aprobada. La portada definitiva se toma de ese archivo al ensamblar, no del marcador impreso del HTML.

`modelo/` contiene el BPMN V11, las reglas relacionales y las pruebas de casos. `qa/` conserva los resultados automáticos. El PDF final pasó el control digital de 41 páginas, 316 bloques fuente conservados, 21 destinos de índice, 34 enlaces internos, 83 externos, geometría y color. La inspección visual se hizo sobre las 41 páginas; las páginas 4, 5, 27–31 y 40–41 se examinaron además individualmente. No hay aún prueba con docentes, importación en un modelador independiente, auditoría de lector de pantalla ni preprensa; no atribuirle esas validaciones.

Antes de modificar o reemplazar N16: comparar fuente y PDF, ejecutar de nuevo pruebas y control visual, actualizar foliación y enlaces del sitio, publicar y verificar el SHA remoto. No generar otra serie de copias privadas permanentes: los renders intermedios son descartables.
