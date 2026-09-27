# Selector de públicos sobre el home

## Alcance

- Mantiene la fotografía, el título principal, los logos y el contenido académico existente.
- Un diálogo negro translúcido atenúa el fondo y solicita elegir Estudiante, Docente, Autoridad académica o Me interesa la propuesta. Texto blanco, opciones sin cajas y volt sólo en interacción/selección. Versión oscura validada por el usuario antes de publicar.
- La selección cambia la bienvenida, los tres accesos principales, un recorrido recomendado y la perspectiva inicial de la sección Audiencias. No elimina contenido ni altera las lecturas.
- Cambiar perfil permanece disponible en el encabezado, también en móvil.
- La preferencia se conserva únicamente en este navegador (`metsi.audience.v1`). No se envía a un servidor. Si el almacenamiento no está disponible, la elección funciona durante la visita.
- El sitio y los materiales docentes siguen siendo públicos. La preferencia no acredita identidad ni reemplaza autenticación futura.

## Accesibilidad y resiliencia

- Diálogo modal nativo, fondo no interactuable, foco contenido y restauración de foco y desplazamiento al elegir.
- Escape y pulsaciones fuera del panel no omiten la selección, de acuerdo con el pedido.
- Las cuatro opciones se operan con teclado. Sin JavaScript o sin soporte de diálogo, el contenido original sigue siendo legible: no se trata de una barrera de seguridad.
- Respeta movimiento reducido. En pantallas bajas el panel permite desplazarse sin desbordarse lateralmente.
- Ajuste posterior: las flechas se dibujan con trazos CSS, sin glifos que iOS pueda representar como emojis. Marca superior y numeración volt visibles también sin hover. Abarca selector, Cambiar perfil y enlaces del recorrido recomendado.

## Verificación

`scripts/qa_profile_selector.mjs` prueba los cuatro perfiles en 1440×1000, 1024×768, 901×800, 768×900, 390×844, 320×568 y 844×390: persistencia, selección obligatoria, foco, destinos de enlaces, conservación del home, menú móvil, 36 lecturas y estabilidad del atlas. Incluye almacenamiento bloqueado/inválido y JavaScript desactivado.

El verificador general detectó tres enlaces simbólicos de dependencias locales ignoradas en `pedagogy/presentations-web/N01/node_modules/.bin/`. No forman parte del despliegue ni se modificaron. Se verificó un paquete separado con los mismos archivos que ensambla `deploy-pages.yml`: 892 archivos, sin errores, sin enlaces rotos ni credenciales detectadas. No se añadió licencia ni se tocaron PDFs.
