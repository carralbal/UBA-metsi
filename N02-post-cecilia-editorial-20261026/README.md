# N02 · fuente editable de la revisión del 26-10-2026

`index.html`, las hojas CSS, `assets/` y `diagrams/` constituyen la fuente editable del interior publicado. Se conservaron los 237 bloques de contenido identificados en la recuperación académica. La portada pública aprobada no se recrea aquí: se toma sin cambios del PDF previamente publicado durante el ensamblado.

Cambios de esta edición: se incorpora la lectura visual de registro/trabajo real/resultado tras la escena de la valija; se integra una pausa ink después de la primera aplicación hotelera; y se elimina de la apertura la caja paper sobre ink. El acabado a sangre extiende las páginas fotográficas y la apertura sin modificar la prosa extraíble. El PDF público y su SHA-256 figuran en `audits/N02-N14-N21-post-cecilia-release-20261026.json`.

La fuente está preparada para Chrome/Chromium en media `print` y escala histórica `0.961344`, seguida del ensamblado de la portada y el acabado a sangre. `contents-reconciliation.json` registra el cotejo del índice.

## Corrección semántica del 28-10-2026

En la página física 6, el estado «Equipaje embarcado» se describía como un dato correcto, aunque el episodio sólo acreditaba un escaneo en rampa. Se corrigieron los dos párrafos de la escena y el epígrafe «Tres vistas» en este `index.html`: el escaneo es real, la conclusión de embarque no está demostrada y el traslado posterior no quedó registrado. La revisión no modifica el ejercicio HH-02 ni otra sección. La sustitución mecánica reproducible está en `scripts/correct_n02_valija_semantics_20261028.py`; el render y ensamblado conservador están en los scripts homónimos de `scripts/`. Se preserva el nombre público estable del PDF y se renueva sólo la clave de caché.
