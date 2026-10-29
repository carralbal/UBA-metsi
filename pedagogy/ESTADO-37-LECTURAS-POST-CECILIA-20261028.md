# METSI · estado único de las 37 lecturas post-Cecilia

**Corte: 28/10/2026. Edición digital para pantalla.** Esta tabla existe para
evitar una segunda colección de «copias privadas» y distinguir contenido
incorporado, decisión de conservar y asuntos aún dependientes del equipo.
El PDF en la ruta del [manifiesto](../site/course-manifest.json) es siempre el
arte digital canónico; un PDF de prueba no lo sustituye.

## Semáforo real, no cosmético

- **37/37 publicadas:** 1.435 A4. La auditoría en HEAD `93e7a34` confirmó
  37/37 PDF por SHA y 37/37 enlaces. Después sólo se alteraron N11 y N21:
  commit `70b3e93`, Pages `40790739864` `success` y SHA remoto idéntico a Git
  para ambos. Los commits posteriores de fuente/QA no tocaron `site/`.
- **10/37 con ajuste focal post-Cecilia:** nueve integraciones N00, N01, N08,
  N10, N12, N14, N16, N17, N19, más corrección conceptual N02. **27/37
  conservadas** porque su contenido ya cubría el punto correspondiente o
  agregar una página duplicaría material. «Conservar» no equivale a aval de
  docentes ni autoridades.
- **36/36 paquetes de clase pasaron validación estructural**; ocho paquetes
  focales ya reflejan lo nuevo. Además, la preparación de **N01–N10** se
  contrastó con las consignas de sus PDF canónicos para eliminar trabajo previo
  oculto. Falta el mismo contraste N11–N36. No se ensayó aún una clase con reloj
  ni se sincronizaron sus decks v4.
- **No hay PDF privado canónico.** Se usaron archivos temporales para QA y se
  eliminaron. N11 y N21 tienen p. 3 de Referentes más legible; N25 y N30
  cuentan con receta comprobada que reproduce exactamente su PDF final.

| Lectura | Decisión de contenido post-Cecilia | Aula focal | Observación que importa |
|---|---|---|---|
| N00 | Integrado: dos puertas de entrada | — | Pedido reactivo y oportunidad proactiva. |
| N01 | Integrado: dos orígenes HH-01 | Sí | No dar por supuesta la solución. |
| N02 | Corregido: hecho observado/inferencia | — | La valija es escena ficticia; no presentar inferencia como hecho. |
| N03 | Conservar | — | Consecuencias de mover un límite. |
| N04 | Conservar | — | Evidencia, supuestos y alternativas. |
| N05 | Conservar | — | Personas, voces y autoridad. |
| N06 | Conservar | — | Investigación que cambia la decisión. |
| N07 | Conservar | — | Entrevista sin inducir. |
| N08 | Integrado: señal proactiva | Sí | Oportunidad sin encargo explícito. |
| N09 | Conservar | — | UX y traspaso hacia prueba en servicio. |
| N10 | Integrado: puerta de no iniciar | Sí | No toda señal justifica un proyecto. |
| N11 | Conservar contenido | — | Referentes p. 3 legibles; fuente fiel consolidada en Git. |
| N12 | Integrado: RF, RNF, aceptación | Sí | Entregable reconocible y comprobable. |
| N13 | Conservar | — | Reintentos y excepciones. |
| N14 | Integrado: AS-IS/TO-BE | Sí | Una sola galería de seis personajes; medidas comparables. |
| N15 | Conservar | — | Elegir las vistas necesarias. |
| N16 | Integrado: proceso, datos, estados | Sí | Dos láminas aprobadas ya en PDF final pp. 28–29. |
| N17 | Integrado: prefactibilidad | Sí | Decidir si avanzar antes de comprometer recursos. |
| N18 | Conservar | — | Restricciones del legado. |
| N19 | Integrado: adquisición | Sí | Criterios antes de ofertas. |
| N20 | Conservar | — | Plan, EDT, decisiones y riesgos. |
| N21 | Conservar contenido | — | Referentes p. 3 legibles; cuerpo 11,5 pt modal. |
| N22 | Conservar | — | Experimento y protección de personas. |
| N23 | Conservar | — | Corte pequeño pero útil de punta a punta. |
| N24 | Conservar | — | Capacidad y variación. |
| N25 | Conservar | — | Flujo y espera; PDF final reproducido byte por byte. |
| N26 | Conservar | — | Ecosistema y ITIL 4 citado; no afirma COBIT. |
| N27 | Conservar | — | Contrato e interfaces entre actores. |
| N28 | Conservar | — | Pruebas del servicio real. |
| N29 | Conservar | — | Despliegue y recuperación. |
| N30 | Conservar | — | Observabilidad; PDF final reproducido byte por byte. |
| N31 | Conservar | — | Pertinencia de IA y control humano. |
| N32 | Conservar | — | Pruebas de IA y daños posibles. |
| N33 | Conservar | — | Gobierno, corrección y retiro de IA. |
| N34 | Conservar | — | Volver al problema y al resultado buscado. |
| N35 | Conservar | — | Explicar y defender decisiones. |
| N36 | Conservar | — | Aprendizaje y próxima iteración. |

## Evidencia y límites

- [QA de colección](QA-COLECCION-37-N-POST-REFERENTES-20261028.md): geometría
  1.435/1.435, fondos de Referentes y accesibilidad estructural. La lectura
  humana con VoiceOver y la preprensa siguen pendientes. [Auditoría de tamaño
  de lectura](../AUDITORIA-TIPO-LECTURA-37-N-POST-LEGIBILIDAD-20261028.json)
  para 37/37 en JSON.
- [Legibilidad N11/N21](QA-LEGIBILIDAD-N11-N21-20261028.md): sólo p. 3
  recompuesta, contenido/otras páginas preservados y SHA remoto comprobado.
- [Fuente N25](QA-FUENTE-PDF-N25-20261028.md): reconstrucción exacta desde
  objeto LFS histórico + tres overlays pequeños; una clonación nueva depende
  de poder descargar aquel LFS.
- [Fuente N30](QA-FUENTE-EDITABLE-N30-20261028.md): HTML interior preservado,
  PDF final reproducible desde blob normal de Git v28 + normalización p. 3.
- [Programa propuesto](../programa/programa-metsi-2026.md) y portada: reflejan
  los métodos nuevos, pero no cuentan con aprobación institucional.
- [Auditoría de carga](AUDITORIA-CARGA-37-LECTURAS-20261028.md): 36
  preparaciones, sólo siete lecturas con tiempo numérico entre N01 y N36,
  y calendario de 46 encuentros posible pero aún sin prueba de aula. Cierre curricular
  digital no equivale a viabilidad de cuatrimestre.
- [Alineación de preparación N01–N10](QA-ALINEACION-PREPARACION-N01-N10-20261028.md):
  cada consigna pública se cruzó con el paquete docente; se quitaron entregas
  adicionales en la preparación, manteniendo la profundización en clase.

## Por validar con el equipo docente

Completar la alineación de preparación N11–N36 antes de dar por cerrada la carga
asincrónica. Ensayar con reloj los ocho paquetes focales y los puentes N06, N09→N28,
N17→N20, N19→N26→N27, N21→N30, N29→N30, N34→N36. Confirmar si una clase
de 120 minutos funciona y si la carga real cabe en el cuatrimestre. Actualizar
los decks si se usarán, probar BPMN en un modelador independiente, hacer
prueba humana de accesibilidad y, si habrá impresión, un preflight aparte.
El programa, las lecturas y la PPTX interna todavía no equivalen al aval de
Cecilia, el equipo ni las autoridades.
