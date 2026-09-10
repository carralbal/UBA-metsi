# METSI · prepublicación v8 de N11 a N36

Fecha: 10 de septiembre de 2026.

## Estado

El sitio candidato contiene los PDF editoriales v8 de N11 a N36 bajo las mismas rutas estables que utiliza actualmente la biblioteca. El cambio existe sólo en la rama `academic-depth-revision-n11-n36`; no fue promovido a `main` ni desplegado en GitHub Pages.

## Identidad de la entrega

- Rango: N11 a N36.
- Versión fuente: `v8-editorial`.
- Contrato de rutas: `stable-v1-filename`.
- Huella de la entrega: `395cff062a73b68c5e964867145e1cdf8bf656530a79eab0a96c2716941b3dd9`.
- PDF sustituidos en el candidato: 26.
- Tapas regeneradas: 26, todas con la misma huella que las tapas aprobadas anteriores.
- Referencias locales comprobadas: 162.
- Archivos protegidos de N00 a N10: 22, sin cambios.

## Compuerta de sitio

Resultado: `PASS`.

La verificación confirmó:

- manifiestos parseables y concordantes;
- fuentes canónicas y paquetes v8 con hashes coincidentes;
- 37 descargas PDF exactas, desde N00 hasta N36;
- conteos de páginas concordantes con la biblioteca;
- títulos, rutas estables y tapas correctas;
- todos los Núcleos y los ocho bloques curriculares presentes;
- imágenes con texto alternativo;
- navegación por teclado, diseño adaptable y movimiento reducido;
- metadatos sociales completos;
- ausencia de marcadores, enlaces rotos y rutas fuera del sitio.

## Próxima operación

La promoción a `main` deberá conservar exactamente esta huella de entrega, ejecutar nuevamente `site/validate_site.py --check-only --require-sources`, desplegar GitHub Pages y comprobar la URL pública y una muestra de descargas en producción.
