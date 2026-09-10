# Auditoría de ampliación curricular METSI

Fecha: 10 de septiembre de 2026.

Resultado: **PASS**.

## Alcance

Se auditaron 27 fuentes v2. Veinticinco incorporan la distribución aprobada de gestión, diseño, operación, integración y autores regionales. N35 y N36 se conservaron byte por byte para verificar que Paulo Freire permaneciera integrado sin agregar contenido automático.

Los PDF, el sitio y los paquetes editoriales existentes quedaron fuera de esta intervención y no fueron modificados.

## Resultado cuantitativo

| Medida | Resultado |
|---|---:|
| Fuentes esperadas y encontradas | 27 de 27 |
| Fuentes ampliadas | 25 |
| Fuentes preservadas byte por byte | 2 |
| Palabras en las líneas de base | 218.576 |
| Palabras en las candidatas v2 | 229.138 |
| Incorporación neta | 10.562 |
| Párrafos extensos duplicados entre documentos | 0 |
| PDF modificados | 0 |

## Cobertura aprobada

| Familia | Lecturas | Resultado |
|---|---|---|
| PMI, PMBOK, Scrum y Kanban | N17, N20, N21, N23, N24, N25 | PASS |
| UI, UX y diseño | N06, N08, N09, N15, N28 | PASS |
| BPM y BPMN | N12, N14, N15 | PASS |
| APIs, Git y GitHub | N18, N23, N27, N29 | PASS |
| DevOps y DORA | N23, N25, N29, N30 | PASS |
| Autores argentinos y latinoamericanos | N02, N03, N05, N09, N12, N14, N15, N16, N19, N20, N21, N27, N31, N32, N33, N35, N36 | PASS |

## Juicio de contenido

Las incorporaciones no quedaron como inventarios de marcas ni preparaciones para certificación. Cada núcleo distingue el objeto conceptual, explicita límites, conecta evidencia con decisión y vuelve a Hotel Horizonte como prueba de transferencia. PMBOK, Scrum y Kanban cumplen funciones distintas; UI no se confunde con UX; OpenAPI y AsyncAPI se presentan como partes de contratos más amplios; Git se diferencia de GitHub; BPMN representa coordinación sin fingir ejecución; DORA se utiliza como sistema contextual de preguntas y no como ranking.

Los autores regionales modifican el argumento en lugares específicos. Rolando García interviene sobre construcción y escala del sistema; Etkin y Schvarstein sobre identidad y contradicción organizacional; Scolari sobre interfaz y ecología; Flores sobre compromisos; Varsavsky sobre selección tecnológica; Ricaurte sobre poder y epistemologías de datos; Freire permanece en diálogo y praxis.

## Controles deterministas

- Estructura editorial de contenido completa en las 27 fuentes.
- Hotel Horizonte presente en cada documento controlado.
- Términos y autores ubicados en las lecturas aprobadas.
- Extensión mínima alcanzada según función y contenido preexistente.
- Cero `TBD`, `lorem`, `XXX` o `[TODO]`.
- Cero rayas de inciso agregadas en la nueva redacción.
- Cero párrafos de 220 caracteres o más repetidos entre documentos.
- N35 y N36 idénticos a sus fuentes v1.
- Cero cambios en archivos PDF.

La evidencia completa, con conteos, rutas y SHA-256 por fuente, está en `audits/2026-09-10-curricular-expansion-audit.json`. La reproducción se ejecuta con:

```bash
python3 scripts/audit_curricular_expansion.py --write audits/2026-09-10-curricular-expansion-audit.json
```

## Puerta siguiente

El contenido v2 queda habilitado para integración editorial. Esto no aprueba todavía los PDF. La siguiente puerta debe resolver la deuda geométrica de infografías, recomponer desde fuentes v2, revisar imágenes y comprobar densidad, continuidad, accesibilidad y consistencia página por página antes de publicar.
