# Presentaciones de clase METSI

Cada N cuenta con una presentación editable de diez pantallas. El contenido visible coordina el trabajo de estudiantes y evita repetir la lectura previa. Las pantallas 02 a 09 corresponden, una por una, a las ocho actividades reales del taller de esa N, con su tiempo y su consigna. Las notas de orador contienen la intervención docente, la señal para avanzar, preguntas de sondeo y una adaptación para modalidad asincrónica.

## Sistema visual

- formato panorámico 16:9;
- paleta METSI: papel, tinta, gris y volt;
- Didot para títulos y Avenir para navegación y cuerpo;
- una función pedagógica por pantalla;
- sin fotografías decorativas ni colores ajenos a la colección.

## Generación

El generador toma como fuente los cuatro archivos del paquete pedagógico de cada N, la pregunta profesional de la fuente canónica de lectura y el `course-manifest.json` que identifica la versión publicada. Así evita desacoplar la clase de la lectura vigente.

```sh
node pedagogy/presentations/build_class_decks.mjs --only N01 --revision v3
```

Sin `--only`, genera N01 a N36. También admite `--start` y `--end` para procesar un tramo continuo.

La auditoría estructural comprueba las diez pantallas y las diez notas de cada archivo. Con `--render-root` también renderiza las 360 diapositivas y crea una lámina de revisión por N.

```sh
python pedagogy/presentations/audit_class_decks.py --revision v3 --render-root /tmp/metsi-class-decks-v3
```

El índice de archivos está en [`INDEX.md`](INDEX.md) y el resultado de la última auditoría en [`AUDIT-N01-N36.md`](AUDIT-N01-N36.md).
