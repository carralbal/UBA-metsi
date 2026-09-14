# Cierre de publicación: programa, navegación móvil y portada web

Fecha: 2026-09-14
Alcance: sitio público METSI en `carralbal.github.io/UBA-metsi/`

## Programa de la materia

- Se consolidó la fuente canónica en `programa/programa-metsi-2026.md`.
- La fuente conserva literalmente el programa formal aprobado en el proyecto de contenido.
- SHA-256 de la fuente: `4e28d0f1f6ffcf15d8f50c7cd7efada0bc018fa0a6a6c3db4cb10bca18103c22`.
- Se creó una versión web accesible y responsive en `site/programa.html` y se integró una síntesis navegable en el home público.
- Se generó el PDF A4 en `site/programa/programa-metsi-2026.pdf`.
- PDF: 7 páginas, 19.600 bytes.
- SHA-256 del PDF: `7304eaac105a3ec77926c2321c709a339783bddbdf54b67d73ce559d2a81e4cf`.
- La página web y el PDF incluyen identificación, encuadre, fundamentación, propósitos, objetivos, resultados de aprendizaje, ocho unidades curriculares, estrategia de enseñanza, actividades, evaluación y bibliografía.

## Menú móvil

- Se incorporó un botón hamburguesa semántico con `aria-controls`, `aria-expanded` y etiqueta dinámica.
- El panel se abre y cierra por activación, se cierra al elegir un vínculo, al tocar fuera y con la tecla Escape.
- Al cerrar con Escape, el foco vuelve al botón.
- Los vínculos del programa y de la colección quedan disponibles también dentro del menú móvil.
- La prueba visual y funcional no detectó desbordamiento horizontal de elementos.

## Imagen de fondo del home

- Se usa `site/covers/hero-metsi-bw-v1.webp`, fotografía arquitectónica en blanco y negro de 1.672 × 941 px.
- La imagen ocupa el fondo completo del hero.
- Se eliminó el degradado. Solo se conserva un velo negro uniforme para asegurar contraste tipográfico.
- El encuadre cambia por breakpoint para proteger las zonas de lectura: 50 % en escritorio, 56 % en tableta y 62 % en móvil.
- Opacidad del velo: 0,34 en escritorio y tableta, 0,48 en móvil.

## Prueba responsive

| Escenario | Viewport CSS | Resultado |
|---|---:|---|
| Escritorio | 1440 × 900 | Fondo visible, texto y mapa sin superposición, menú de escritorio visible |
| Tableta | 768 × 1024 | Fondo visible, bloques apilados sin colisión, hamburguesa operativa |
| Móvil | 390 × 844 | Fondo visible, texto legible, botones a ancho disponible, sin scroll horizontal |

## Guarda de regresión

`site/validate_site.py --check-only` terminó en `PASS` con 33 de 33 controles verdaderos.

- 37 lecturas PDF y 37 tapas verificadas sin modificar sus hashes aprobados.
- 36 núcleos y 8 bloques curriculares presentes.
- 169 referencias locales comprobadas, 0 rotas.
- Fuente y PDF del programa presentes y coherentes.
- Navegación del programa accesible.
- Menú hamburguesa implementado.
- Imagen de fondo y breakpoints declarados.

La publicación conserva el flujo de GitHub Pages vigente. El programa descargable se incluye dentro del árbol `covers`, que el despliegue copia de manera recursiva, y la versión web resumida forma parte de `index.html`.
