# Handoff autosuficiente · Bloque 1 · contenido final

## Estado

El contenido de N01 a N10 está cerrado, validado y congelado. La autoridad textual de cada documento es exclusivamente el archivo indicado abajo. No usar PDF, HTML, borradores previos ni copias de trabajo como fuente de recomposición.

## Fuentes canónicas

| Documento | Fuente autorizada |
|---|---|
| N01 | `N01-content-final/source/N01_metodologia_sin_recetas-content-final.md` |
| N02 | `N02-content-final/source/N02_el_sistema_no_cabe_en_una_aplicacion-content-final.md` |
| N03 | `N03-content-final/source/N03_fronteras_retroalimentacion_y_efectos-content-final.md` |
| N04 | `N04-content-final/source/N04_hechos_sintomas_relatos_hipotesis_y_decisiones-content-final.md` |
| N05 | `N05-content-final/source/N05_actores_afectados_poder_y_perspectivas-content-final.md` |
| N06 | `N06-content-final/source/N06_discovery_como_reduccion_de_incertidumbre-content-final.md` |
| N07 | `N07-content-final/source/N07_entrevistar_no_es_pedir_requisitos-content-final.md` |
| N08 | `N08-content-final/source/N08_observar_el_trabajo_invisible-content-final.md` |
| N09 | `N09-content-final/source/N09_experiencia_accesibilidad_y_adopcion-content-final.md` |
| N10 | `N10-content-final/source/N10_construir_el_problema_y_outcomes-content-final.md` |

## Qué quedó resuelto

- Diez lecturas canónicas, todas por encima del piso de 6.000 palabras sustantivas.
- Diez artefactos consecutivos, HH-01 a HH-10.
- Nueve traspasos adyacentes explícitos y bidireccionales.
- Funciones y bloques alineados con el mapa curricular de N00.
- Cierre de Bloque 1 en N10 y frontera no redundante con N11.
- Cero párrafos sustantivos duplicados entre documentos.
- Cero secuencias compartidas de veinticuatro palabras o más.
- 123 referencias y 85 URLs registradas por los validadores individuales.

## Validación

Ejecutar desde la raíz del repositorio:

```bash
python3 BLOCK-01-content-final/validate_block01_content.py
```

El resultado esperado es `overall: pass`. El script verifica los informes individuales, los hashes de integridad, los pisos de profundidad, la secuencia HH, los traspasos, la división de bloques, el cierre N10, el límite N04/N11, las repeticiones transversales y la ausencia de artefactos de composición dentro de este paquete.

Cada documento conserva además su propio `HANDOFF.md`, `CONTENT-AUDIT.md`, `source-manifest.json` e informe de integridad.

## Regla para las próximas etapas

Toda composición debe tomar texto sólo de estas fuentes y registrar cualquier cambio textual como una nueva ronda de contenido. No corregir texto incidentalmente durante la maqueta.

N01 y N02 requieren una futura recompaginación porque sus PDF aprobados anteceden a este cierre de continuidad. N03 a N10 todavía no tienen un PDF final autorizado y pueden entrar en composición usando directamente estas fuentes.

La etapa siguiente de contenido comienza en N11, fuera del alcance de este cierre. La etapa siguiente de producción visual puede comenzar por actualizar N01 y N02 o por componer N03, pero no debe mezclar ambas tareas en una misma pasada.
