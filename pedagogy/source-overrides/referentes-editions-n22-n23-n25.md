# Fuente editorial · edición sin coma inicial en N22, N23 y N25

En la p. 3 de cada PDF, un bloque de edición bibliográfica independiente comienza con `, Second Edition`; la coma queda huérfana al inicio de línea. La corrección canónica del 28/10/2026 elimina sólo ese glifo inicial, sin reescribir el crédito ni la bibliografía. Al consolidar fuentes, quitar esa coma del texto del `<small>` correspondiente:

- N22, Judea Pearl, *Causality*, «Second Edition. Cambridge University Press · 2009».
- N23, Grady Booch, *The Unified Modeling Language User Guide*, «Second Edition. Addison-Wesley · 2005».
- N25, Kent Beck, *Extreme Programming Explained*, «Second Edition. Addison-Wesley · 2004».

Las fuentes fieles históricas de N22/N23 están documentadas en sus QA; N25 sólo tiene un parche PDF localizado y **no** una fuente HTML única demostrada que regenere el PDF vigente. No usar versiones antiguas de HTML para sobrescribirlo. Script guardado: `scripts/normalize_n22_n23_n25_referentes_20261028.py`.
