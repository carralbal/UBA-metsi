# Handoff autosuficiente · METSI N13 · contenido canónico v1

## Estado

N13 quedó desarrollado y auditado sólo como contenido. La revisión de lenguaje llano cerró en la versión v2. No hay cambios en PDF, HTML, CSS, imágenes ni decisiones de maqueta.

Fuente autorizada:

`N13-content-canonical/source/N13_demoras_concurrencia_consistencia_idempotencia_y_reconciliacion-content-canonical-v2.md`

## Función y artefacto

N13 recibe HH-12 y entrega HH-13, expediente de convergencia. Sus diez campos documentan intención estable, efecto protegido, fronteras, tiempos, invariante, garantía observable, idempotencia, conflicto, estado ambiguo, reconciliación y reparación.

## Métricas

- 6.772 palabras totales y 6.018 sustantivas.
- 241 bloques con identificador y hash.
- Doce referencias y diez URLs, todas las entradas ancladas en el cuerpo.
- Diecinueve unidades conceptuales de 150 palabras o más.
- Cero coincidencias de veinticuatro palabras con N01 a N12.
- Auditoría humana: 39/40.
- SHA-256: `d5b0a1d77030d279299883f31f183ca71cf2b14e045a97c54edcc4f560fc96a8`.

## Verificación

```bash
python3 validate_block_c_content.py N13-content-canonical
```

Resultado esperado: `overall: pass`.

## Frontera siguiente

N14 utilizará las transiciones y divergencias de HH-13 para reconstruir procesos end-to-end, handoffs, colas y excepciones. No debe volver a desarrollar idempotencia ni consistencia distribuida.
