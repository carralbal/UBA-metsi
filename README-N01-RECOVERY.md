# METSI N01 recovery repository

Este repositorio local preserva y reconstruye N01 a partir del directorio de
trabajo original. No incorpora ni consulta copias de respaldo.

## Alcance versionado

- `N00/`: estándar editorial aprobado y referencia de regresión.
- `N01/`: paquete completo de N01, incluyendo fuentes, recursos y PDFs.
- `build_collection.py`: constructor activo de la colección.
- `editorial-standard/`: instantánea autocontenida de las reglas aplicadas.

Los demás documentos N permanecen fuera del seguimiento Git y no se modifican
en esta recuperación.

## Política de preservación

El PDF N01 vigente al iniciar el trabajo se conserva sin sobrescritura. Las
nuevas versiones se generan con nombres distintos hasta obtener aprobación.
