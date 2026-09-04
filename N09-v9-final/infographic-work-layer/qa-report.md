# QA · N09 · Mapa de recorrido accesible

**Resultado:** PASS
**Fecha:** 2026-09-04
**Estado:** activo de revisión validado e integrado al PDF final.

## Contrato semántico

- Fuente: `N09-content-final/source/N09_experiencia_accesibilidad_y_adopcion-content-final.md`.
- Anclaje editorial: `N09-s07-b035`, “Instrumento de decisión: mapa de recorrido accesible”.
- Topología: blueprint de servicio y atlas de evidencia, no flujo genérico de cajas repetidas.
- La franja superior conserva las cuatro transiciones explícitas del texto canónico.
- La ampliación conserva los ocho campos enumerados por la fuente. “Alternativa y reparación” se mantiene como el octavo campo compuesto, tal como aparece en la enumeración canónica.
- El riel distributivo conserva tiempo, esfuerzo, asistencia y error.
- La puerta de decisión conserva las cinco salidas del protocolo: continuar, modificar, limitar, investigar o retirar.
- No se incorporaron afirmaciones externas ni se reescribió la fuente para construir el gráfico.

## QA determinista

- Validador oficial de la skill: `RESULT: PASS (0 warning(s))`.
- Manifiesto contra SVG: 18 nodos y 15 relaciones, todos con ID presente.
- Accesibilidad estructural: `role="img"`, `title`, `desc` y `aria-label` exacto para cada nodo del manifiesto.
- Orden de pintura: los conectores aparecen antes que los paneles, nodos y etiquetas.
- Geometría en Chromium a 1800 × 1100: 0 recortes y 0 colisiones visibles entre conectores y texto con una reserva de 14 px.
- Legibilidad: tamaños SVG de 28, 29, 30, 32 y 56 px. El mínimo equivale a 7,06 pt al ancho final de 160 mm.
- Fuentes: Avenir o Avenir Next para texto; Didot o Bodoni 72 para título. No aparecen Arial, Helvetica, Inter ni Times New Roman.
- Raster de revisión: PNG RGB de 3600 × 2200, exactamente 2× el SVG.
- Página de revisión: sin desborde horizontal a 1920, 768 y 390 px. En los tres anchos cargan el SVG 1800 × 1100 y el PNG 3600 × 2200.
- Integración preparada: `diagrams/N09-mapa-decision.svg` coincide byte a byte con el SVG editable.

## QA visual

- Jerarquía clara entre recorrido, ampliación, planos de evidencia, carga distribuida y decisión.
- El volt se reserva para la transición ampliada, puertos críticos y marcas de orientación.
- La paleta queda limitada a papel, blanco, grises, negro y volt.
- Los tres planos se distinguen por masa tonal, geometría y rótulo lateral sin depender sólo del color.
- No hay texto truncado, superpuesto ni fuera del marco.
- Los recorridos de evidencia y revisión usan carriles propios; cuando atraviesan un panel quedan ocultos detrás de su masa y reaparecen en puertos explícitos.
- La densidad, los bordes, el contraste y la variación geométrica se revisaron contra la referencia dorada de la skill.

## Integridad y hashes SHA-256

| Archivo | SHA-256 |
| --- | --- |
| `n09-accessible-service-blueprint.svg` | `719fc5ce84aadc321e240a6dfdf468634a5da7997e47fbe9600cd4311ff8884d` |
| `n09-accessible-service-blueprint.png` | `bf9bef41c52a302d5ac03e1784283692deff777211fbc24e9fa38d716a80c4e9` |
| `content-manifest.json` | `7306e681430afc10c9c417e9292ad77bea6445b7fc0ecf7920c899fc97092b45` |
| `alt-text.md` | `1311a0efcc306283c95b2247a2cbd1bbfec8a67a00becfce4d8419c1a1f8fbc6` |
| `review.html` | `a4d0c47ea7203e9ea1313d3ef49bff259d4fd8f82085a3eb147058683f90762a` |
| `../diagrams/N09-mapa-decision.svg` | `719fc5ce84aadc321e240a6dfdf468634a5da7997e47fbe9600cd4311ff8884d` |
| `../diagrams/N09-mapa-decision.json` | `041f528249caca808b92d087c62f4f9ba119955dd05770540718ae0691f3b552` |

## Límite de esta entrega

El paquete queda listo para revisión visual y posterior integración. No se modificaron el generador, las fotografías, los PDF ni otros paquetes.
