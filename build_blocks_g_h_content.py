#!/usr/bin/env python3
"""Build the canonical METSI content packages for Blocks G and H, N31 through N36."""

from __future__ import annotations

import json
from pathlib import Path

import build_block_d_content as base


ROOT = Path(__file__).resolve().parent


def unit(title: str, definition: str, contrast: str, example: str, boundary: str) -> list[str]:
    example = example[:1].upper() + example[1:]
    mechanism = (
        f"{title} se operacionaliza delimitando propósito, población, entradas, autoridad, "
        "acción, consecuencia y condición de revisión. El recorrido se contrasta con una "
        "alternativa más simple y con un escenario adverso antes de ampliar compromiso."
    )
    evidence = (
        "La evidencia integra una prueba previa, resultados desagregados y el episodio "
        f"siguiente: {example} También conserva las decisiones humanas y automáticas que "
        "produjeron ese resultado."
    )
    return [title, definition, contrast, mechanism, evidence, example, boundary]


def make_doc(*, block: str, slug: str, title: str, question: str, opening_title: str,
             opening: list[str], hotel: str, advance: str, defer: str,
             rows: list[tuple[str, str, str, str, str]], instrument_title: str,
             fields: list[str], transfer_title: str, transfer: list[str],
             counter_title: str, counter: list[str], errors: list[str],
             referents: list[list[str]], references: list[str]) -> dict:
    units = [unit(*row) for row in rows]
    doc = base.compact_doc(
        slug=slug, title=title, question=question, opening_title=opening_title,
        opening=opening, hotel=hotel, advance=advance, defer=defer, units=units,
        instrument_title=instrument_title, instrument_fields=fields,
        transfer_title=transfer_title, transfer=transfer,
        counter_title=counter_title, counter=counter, errors=errors,
        referents=referents, references=references,
    )
    movement_titles = {
        "G": [
            "Movimiento 1 · Distinguir capacidad, propósito y consecuencia",
            "Movimiento 2 · Evaluar exposición, evidencia y control humano",
            "Movimiento 3 · Gobernar cambio, incidentes y retiro",
        ],
        "H": [
            "Movimiento 1 · Reconstruir la cadena de decisiones",
            "Movimiento 2 · Defender y transferir capacidad",
            "Movimiento 3 · Aprender de la acción y de sus consecuencias",
        ],
    }[block]
    doc["movements"] = [[movement_titles[i], units[i * 4:(i + 1) * 4]] for i in range(3)]
    doc["consequences"] = (
        advance
        + " La competencia profesional aparece cuando la elección conserva trazabilidad, "
          "expone sus límites y puede ser discutida por quienes deciden, operan y reciben sus consecuencias."
    )
    doc["limits"] = (
        "Ningún modelo, expediente o marco elimina incertidumbre, conflicto ni asimetrías de poder. "
        "La evidencia disponible puede ser incompleta, los incentivos pueden desplazar daño y la "
        "autoridad formal puede carecer de capacidad real. La lectura exige declarar esas restricciones, "
        "limitar exposición, preservar reparación y fijar una revisión verificable."
    )
    return doc


DOCS = {
31: make_doc(
 block="G", slug="reglas_prediccion_generacion_y_agencia",
 title="Reglas, predicción, generación y agencia: cuándo la IA es pertinente",
 question="¿Cómo distinguir capacidades de inteligencia artificial y decidir si aportan valor frente a una regla, una búsqueda o un proceso mejor diseñado?",
 opening_title="El agente resolvió la reserva y creó una promesa que nadie había autorizado",
 opening=[
  "Hotel Horizonte prueba un agente que recibe mensajes, consulta disponibilidad y propone compensaciones. En la demostración responde con fluidez y resuelve una reserva duplicada. Al día siguiente concede una mejora que Comercial nunca ofreció y modifica un dato que Recepción no puede revertir.",
  "La discusión inicial pregunta si el modelo es suficientemente potente. La pregunta profesional es anterior: qué tarea se intenta resolver, qué clase de capacidad requiere, qué consecuencia puede producir y por qué una solución más simple no alcanza.",
  "Reglas, predicción, generación y agencia no son grados de una misma tecnología. Organizan relaciones distintas entre entradas, inferencias, acciones y autoridad. Mezclarlas impide elegir pruebas y controles proporcionales.",
  "El equipo descompone el recorrido. Una regla valida requisitos, un modelo estima cancelación, un generador redacta una respuesta y un agente elige herramientas y actúa. Cada componente recibe límites, evidencia y una vía de salida diferentes.",
  "La pertinencia no se demuestra con una demo. Se sostiene comparando alternativas, conociendo el costo del error y explicando qué juicio permanece en manos humanas.",
  "N31 abre el Bloque G. Recibe de N30 señales e incidentes operativos y los usa para decidir si incorporar inteligencia artificial sin delegar el juicio."
 ],
 hotel="HH-31 construye un expediente de pertinencia para el ingreso del huésped. Separa reglas deterministas, predicciones, generación de lenguaje y acciones con herramientas. Para cada capacidad registra propósito, población, alternativa sin IA, autoridad, daño posible, evidencia, supervisión y condición de no uso.",
 advance="N31 distingue reglas, predicción, generación y agencia, y convierte la pregunta por la inteligencia artificial en una decisión situada de pertinencia.",
 defer="N32 evaluará tareas, cobertura, severidad, desigualdad, robustez y supervisión real antes de asignar autonomía. N31 no decide todavía si el desempeño observado resulta suficiente.",
 rows=[
  ("Regla determinista","Una regla produce una salida especificada cuando se cumplen condiciones explícitas.","No aprende una relación estadística ni necesita lenguaje generativo.","el validador de identidad rechaza un documento vencido","Las reglas también contienen errores de política y necesitan owner y versión."),
  ("Predicción","Una predicción estima una variable desconocida a partir de patrones y datos.","No explica causalidad ni prescribe por sí sola una acción.","un modelo estima probabilidad de cancelación","La probabilidad pierde sentido fuera de la población y ventana evaluadas."),
  ("Generación","Un sistema generativo produce contenido nuevo condicionado por instrucciones y contexto.","Fluidez y plausibilidad no equivalen a verdad ni autorización.","el asistente redacta una respuesta al huésped","Toda afirmación material necesita fuente, límite y revisión proporcional."),
  ("Agencia","Un sistema agente selecciona pasos, usa herramientas y modifica estados para perseguir un objetivo.","No es sólo una conversación más larga ni automatización tradicional.","el agente consulta inventario y ofrece una alternativa","Más capacidad de actuar aumenta superficie de error y exige permisos mínimos."),
  ("Tarea y propósito","La unidad de diseño es una tarea situada con propósito y consecuencia definidos.","No es el puesto completo ni una lista genérica de casos de uso.","Recepción clasifica una solicitud antes de decidir","Una tarea mal recortada puede trasladar trabajo o responsabilidad."),
  ("Alternativa sin IA","La comparación incluye regla, búsqueda, mejora de datos, rediseño de proceso y no intervención.","No se compara un prototipo con el problema sin ninguna alternativa.","un buscador de políticas reemplaza respuestas generadas","La opción simple puede ser preferible aun cuando produzca menos novedad."),
  ("Valor incremental","El valor incremental es la mejora atribuible a la IA frente a una baseline practicable.","No coincide con entusiasmo, adopción ni precisión aislada.","el tiempo de resolución baja sin aumentar reparaciones","Una mejora promedio no compensa daño grave o desigual."),
  ("Consecuencia de decisión","La consecuencia conecta una salida del sistema con una acción que afecta recursos, derechos o experiencia.","Un texto informativo no tiene el mismo riesgo que una acción ejecutada.","una recomendación termina reasignando una habitación accesible","El efecto depende de autoridad, interfaz e incentivos, no sólo del modelo."),
  ("Incertidumbre y calibración","La incertidumbre expresa cuánto respaldo existe para una salida y cómo cambia según contexto.","Una cifra de confianza no garantiza calibración ni comprensión humana.","el modelo reconoce baja certeza ante una política excepcional","La incertidumbre útil debe cambiar una decisión o un escalamiento."),
  ("Control humano significativo","El control humano requiere información, tiempo, autoridad y una alternativa real para intervenir.","No se satisface agregando una aprobación automática o decorativa.","Recepción puede rechazar la sugerencia y reparar el estado","Una persona puede quedar como fusible si carga responsabilidad sin capacidad."),
  ("Fundamentación y procedencia","La fundamentación vincula una respuesta con fuentes vigentes y permite rastrear transformaciones.","Recuperar documentos no vuelve correcta una inferencia.","el asistente cita la política y su fecha de vigencia","La fuente puede ser incompleta, contradictoria o inaplicable al caso."),
  ("Condición de no uso","La condición de no uso define cuándo la IA no debe iniciarse o debe retirarse.","No es resistencia genérica ni un descargo posterior.","el hotel prohíbe compensaciones automáticas sin autoridad","No usar IA también exige sostener una alternativa operacional."),
 ],
 instrument_title="Instrumento HH-31: expediente de pertinencia de IA",
 fields=["Problema y tarea","Población","Capacidad requerida","Alternativa sin IA","Baseline","Consecuencia","Autoridad","Datos y fuentes","Incertidumbre","Control humano","Evidencia de valor","No uso y revisión"],
 transfer_title="Caso de transferencia: orientación académica", transfer=[
  "Una facultad considera un asistente para responder consultas sobre correlatividades. Parte del problema es búsqueda de normativa vigente; otra parte requiere interpretar trayectorias y excepciones.",
  "El expediente separa recuperación de fuentes, generación de explicación y decisiones que sólo puede tomar una autoridad académica. La IA ayuda a localizar y redactar, pero no crea equivalencias ni concede excepciones.",
  "La transferencia muestra que pertinencia significa asignar capacidades diferentes dentro de un mismo recorrido, no elegir entre usar IA o rechazarla por completo."
 ],
 counter_title="Contraejemplo: IA para una regla estable", counter=[
  "Un equipo usa un modelo generativo para decidir si una fecha cae dentro de un plazo reglamentario.",
  "La tarea admite una regla verificable. El modelo agrega variabilidad, costo y opacidad sin aportar valor incremental.",
  "La decisión madura consiste en no usar IA y reservarla para incertidumbres que justifiquen sus capacidades."
 ],
 errors=["Empezar por la herramienta","Llamar IA a toda automatización","Confundir predicción con decisión","Confundir fluidez con conocimiento","Dar herramientas sin permisos mínimos","Omitir la baseline","Medir adopción como valor","Agregar aprobación decorativa","Usar recuperación como garantía","Ocultar incertidumbre","Ignorar poblaciones afectadas","No diseñar una salida"],
 referents=[["OECD","Actualiza una definición funcional de sistema de inteligencia artificial."],["NIST","Organiza gobierno, mapeo, medición y manejo del riesgo de IA."],["UNESCO","Propone competencias técnicas, éticas, humanas y de diseño de sistemas."],["Stuart Russell y Peter Norvig","Distinguen agentes, objetivos, entornos y racionalidad limitada."],["Judea Pearl","Separa asociación, intervención y explicación causal."],["Virginia Dignum","Vincula inteligencia artificial responsable con diseño, uso y gobierno."]],
 references=["OECD (2024). Explanatory Memorandum on the Updated OECD Definition of an AI System. https://oecd.ai/en/ai-publications/explanatory-memorandum-on-the-updated-oecd-definition-of-an-ai-system","NIST (2023). Artificial Intelligence Risk Management Framework 1.0. https://doi.org/10.6028/NIST.AI.100-1","NIST (2024). Generative Artificial Intelligence Profile. https://doi.org/10.6028/NIST.AI.600-1","UNESCO (2024). AI Competency Framework for Students. https://www.unesco.org/en/articles/ai-competency-framework-students","UNESCO (2023). Guidance for Generative AI in Education and Research. https://www.unesco.org/en/articles/guidance-generative-ai-education-and-research","Russell, S. y Norvig, P. (2021). Artificial Intelligence: A Modern Approach, Fourth Edition. Pearson.","Pearl, J. y Mackenzie, D. (2018). The Book of Why. Basic Books.","Dignum, V. (2019). Responsible Artificial Intelligence. Springer.","ISO/IEC (2023). ISO/IEC 42001:2023 Artificial Intelligence Management System. https://www.iso.org/standard/42001","European Union (2024). Artificial Intelligence Act. https://eur-lex.europa.eu/eli/reg/2024/1689/oj","Amershi, S. et al. (2019). Guidelines for Human AI Interaction. https://doi.org/10.1145/3290605.3300233","Shneiderman, B. (2022). Human Centered AI. Oxford University Press."]
),
32: make_doc(
 block="G", slug="evaluar_tareas_cobertura_severidad_desigualdad_robustez_y_supervision",
 title="Evaluar tareas, cobertura, severidad, desigualdad, robustez y supervisión",
 question="¿Qué evidencia permite asignar autonomía a una capacidad de IA sin ocultar fallas graves detrás de un buen promedio?",
 opening_title="El promedio era alto y las habitaciones accesibles fallaban",
 opening=[
  "El asistente de Hotel Horizonte alcanza noventa y dos por ciento de respuestas consideradas correctas. La cifra habilita un piloto amplio. Una semana después, el equipo descubre que las consultas sobre accesibilidad eran escasas en el conjunto de prueba y concentraban casi todos los errores graves.",
  "La evaluación había medido desempeño medio, no cobertura del uso ni severidad de consecuencias. Tampoco había probado cambios de temporada, instrucciones adversas, capacidad de supervisión ni tiempo disponible para reparar.",
  "Evaluar un sistema de IA exige definir unidad de análisis, población, baseline, criterio, umbral y decisión asociada. La prueba debe representar el sistema sociotécnico completo, incluyendo personas, interfaces, datos y operación.",
  "El equipo reconstruye casos, separa error inocuo de daño material, desagrega resultados y mide al conjunto humano y automático. La autonomía deja de ser una etiqueta y se convierte en una exposición graduada.",
  "La prueba anterior al despliegue no alcanza. El comportamiento cambia con entradas, modelos, proveedores, incentivos y aprendizaje de usuarios; la evaluación continúa durante la operación.",
  "N32 recibe de N31 una capacidad considerada pertinente y pregunta si la evidencia disponible justifica su alcance, su nivel de autonomía y sus protecciones."
 ],
 hotel="HH-32 evalúa clasificación, redacción y acción por separado. Construye un conjunto con casos ordinarios, extremos y adversos, desagrega por tipo de necesidad, pondera severidad, compara baseline humana y simple, y ensaya la supervisión bajo carga. La autonomía sólo aumenta cuando desempeño, cobertura y reparación cumplen umbrales explícitos.",
 advance="N32 evalúa tareas, cobertura, severidad, desigualdad, robustez y supervisión real antes de asignar autonomía a una capacidad de inteligencia artificial.",
 defer="N33 convertirá esa evidencia en gobierno vivo del ciclo de vida. N32 no diseña todavía inventario institucional, ownership, control de cambios, incidentes ni retiro.",
 rows=[
  ("Unidad de evaluación","La unidad de evaluación combina tarea, población, contexto, salida y consecuencia.","No es el modelo aislado ni un benchmark genérico.","cada respuesta del asistente se vincula con la decisión posterior","Cambiar la unidad puede invertir la conclusión sobre desempeño."),
  ("Cobertura","La cobertura expresa qué proporción y diversidad del uso previsto está representada.","No coincide con cantidad total de casos.","el conjunto incluye excepciones de accesibilidad y temporadas altas","Casos raros pueden dominar el riesgo aunque pesen poco en el promedio."),
  ("Baseline","La baseline representa la mejor alternativa practicable sin el cambio evaluado.","No es ausencia de solución ni desempeño humano idealizado.","se compara con búsqueda guiada y atención actual","Una baseline degradada puede inflar artificialmente el valor incremental."),
  ("Validez de constructo","La validez pregunta si la medida representa la capacidad que se pretende juzgar.","Exactitud superficial puede no medir utilidad ni seguridad.","una rúbrica distingue respuesta completa de respuesta persuasiva","La métrica puede premiar conducta contraria al propósito."),
  ("Severidad","La severidad clasifica consecuencias por daño, alcance, reversibilidad y población.","No equivale a frecuencia ni confianza del modelo.","negar una habitación accesible pesa más que un error de estilo","Baja frecuencia no vuelve tolerable un daño irreversible."),
  ("Desempeño desagregado","El desempeño desagregado muestra diferencias entre grupos, contextos y clases de caso.","Un promedio global puede ocultar desigualdad sistemática.","se comparan consultas por idioma, canal y necesidad","Categorías demasiado amplias pueden volver invisible la población relevante."),
  ("Robustez","La robustez es capacidad de sostener comportamiento aceptable ante variación esperable.","No significa inmunidad a todo cambio.","se modifican redacción, orden y datos irrelevantes de la consulta","Una prueba limitada no anticipa todas las distribuciones futuras."),
  ("Prueba adversa","La prueba adversa busca activamente modos de falla, abuso y evasión.","No es creatividad sin modelo de amenaza.","se intenta obtener descuentos o datos mediante instrucciones maliciosas","Publicar ataques sin control también puede ampliar exposición."),
  ("Confiabilidad y repetibilidad","La confiabilidad estudia variación entre ejecuciones y condiciones equivalentes.","Una única respuesta correcta no caracteriza un sistema no determinista.","se repite la misma tarea con versiones y temperaturas controladas","La repetibilidad total puede ser innecesaria si la consecuencia permanece estable."),
  ("Desempeño del equipo humano IA","La evaluación sociotécnica mide el resultado del conjunto y no sólo de sus componentes.","Una mejor recomendación puede empeorar la decisión si induce confianza excesiva.","se observa cuándo Recepción acepta, corrige o ignora sugerencias","La intervención humana puede sumar sesgo, demora o automatización complaciente."),
  ("Supervisión real","La supervisión real combina competencia, atención, tiempo, autoridad y alternativa.","No se prueba con una casilla de aprobación.","el turno nocturno detecta y revierte una compensación improcedente","La carga puede convertir revisión nominal en aceptación automática."),
  ("Evaluación en operación","La evaluación en operación repite pruebas y observa consecuencias después del despliegue.","No es sólo monitoreo técnico ni auditoría anual.","cambios de temporada disparan nuevas muestras y umbrales","Medir sin capacidad de limitar o retirar no gobierna el riesgo."),
 ],
 instrument_title="Instrumento HH-32: expediente de evaluación y autonomía",
 fields=["Tarea y población","Decisión habilitada","Baseline","Conjunto y cobertura","Métrica y validez","Severidad","Desagregación","Robustez","Prueba adversa","Equipo humano IA","Umbral de autonomía","Evaluación continua"],
 transfer_title="Caso de transferencia: priorización hospitalaria", transfer=["Un hospital evalúa una herramienta que ordena estudios pendientes. El promedio de concordancia es alto, pero los casos urgentes y las poblaciones con datos incompletos requieren otra lectura.","El expediente pondera severidad, cobertura, desempeño desagregado y capacidad del equipo para detectar fallas bajo carga. La herramienta prioriza sólo dentro de límites y nunca elimina revisión clínica.","La transferencia muestra que la autonomía se diseña por tarea y consecuencia, no por prestigio del modelo."],
 counter_title="Contraejemplo: ganar el benchmark", counter=["Un proveedor exhibe una mejora de dos puntos en un conjunto público y pide automatizar decisiones.","El conjunto no representa la población local, no incluye consecuencias ni mide supervisión. La comparación no puede sostener la decisión solicitada.","La evidencia vale por la relación que establece entre uso, riesgo y autoridad, no por el ranking."],
 errors=["Evaluar sólo el modelo","Usar un promedio único","Confundir volumen con cobertura","Omitir baseline","Medir lo fácil","Tratar frecuencia como severidad","No desagregar","Probar sólo el camino feliz","Ignorar variabilidad","Evaluar humanos y máquina por separado","Simular supervisión sin carga","Cerrar evaluación al desplegar"],
 referents=[["NIST","Desarrolla medición, evaluación, verificación y validación de sistemas de IA."],["Joy Buolamwini y Timnit Gebru","Mostraron desigualdades ocultas por agregación en sistemas de clasificación."],["Batya Friedman y David Hendry","Vinculan diseño con valores y actores afectados."],["Madeleine Clare Elish","Explica zonas de deformación moral en sistemas autónomos."],["Ben Shneiderman","Propone control humano confiable y verificable."],["ISO/IEC","Estandariza conceptos de sesgo, robustez y gestión de riesgo."]],
 references=["NIST (2023). Artificial Intelligence Risk Management Framework 1.0. https://doi.org/10.6028/NIST.AI.100-1","NIST (2024). Generative Artificial Intelligence Profile. https://doi.org/10.6028/NIST.AI.600-1","NIST (2026). ARIA 0.1 Pilot Evaluation Report, NIST AI 800-4. https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-4.pdf","NIST (2026). TEVV-Athlon Framework, Initial Public Draft. https://www.nist.gov/artificial-intelligence/ai-research/tevv-athlon-framework-evaluating-ai-systems","Buolamwini, J. y Gebru, T. (2018). Gender Shades. Proceedings of Machine Learning Research, 81, 1-15. http://proceedings.mlr.press/v81/buolamwini18a.html","Friedman, B. y Hendry, D. G. (2019). Value Sensitive Design. MIT Press.","Elish, M. C. (2019). Moral Crumple Zones. Engaging Science, Technology, and Society, 5, 40-60. https://doi.org/10.17351/ests2019.260","Shneiderman, B. (2022). Human Centered AI. Oxford University Press.","ISO/IEC (2023). ISO/IEC 23894:2023 Artificial Intelligence Risk Management. https://www.iso.org/standard/77304.html","ISO/IEC (2024). ISO/IEC TR 24027:2021 Bias in AI Systems and AI Aided Decision Making. https://www.iso.org/standard/77607.html","Amershi, S. et al. (2019). Guidelines for Human AI Interaction. https://doi.org/10.1145/3290605.3300233","Raji, I. D. et al. (2020). Closing the AI Accountability Gap. https://doi.org/10.1145/3351095.3372873"]
),
33: make_doc(
 block="G", slug="gobierno_vivo_de_inteligencia_artificial",
 title="Gobierno vivo de IA: inventario, ownership, datos, proveedores, cambios, incidentes, reparación y retiro",
 question="¿Cómo gobernar sistemas de inteligencia artificial que cambian durante su uso y dependen de datos, modelos y proveedores distribuidos?",
 opening_title="El modelo cambió sin que cambiara el proyecto",
 opening=["Hotel Horizonte aprueba un asistente con alcance limitado. Dos meses después, el proveedor cambia el modelo base, Comercial agrega una fuente y Operaciones amplía permisos. Ningún cambio parece mayor por separado, pero el sistema ahora responde y actúa de otra manera.","El acta de aprobación conserva la versión inicial. El inventario sólo lista el nombre comercial y el contrato. Cuando aparece un incidente, nadie puede reconstruir qué configuración, datos, herramientas y responsables estaban activos.","Gobernar IA es mantener una representación vigente del sistema sociotécnico y de sus dependencias. Requiere inventario, ownership, procedencia, control de cambios, monitoreo, incidentes, reparación y retiro.","El equipo crea un registro vivo por uso y no sólo por proveedor. Vincula cada capacidad con población, fuentes, versión, permisos, evaluación, owner, incidentes y condición de salida.","La política deja de ser una declaración general. Se convierte en decisiones ejecutables y auditables a lo largo del ciclo de vida.","N33 cierra el Bloque G. Recibe de N31 la pertinencia y de N32 la evidencia de evaluación, y las transforma en gobierno institucional capaz de sostener, limitar y retirar."],
 hotel="HH-33 registra el asistente como una composición de modelo, instrucciones, recuperación, herramientas, interfaz y trabajo humano. Cada cambio material activa evaluación proporcional. Incidentes preservan evidencia, informan a afectados, habilitan reparación y modifican controles. El retiro incluye datos, accesos, conocimiento y continuidad.",
 advance="N33 diseña gobierno vivo mediante inventario, ownership, datos, proveedores, cambios, monitoreo, incidentes, reparación y retiro.",
 defer="N34 integrará el recorrido completo desde problema y evidencia hasta operación y gobierno. N33 cierra el gobierno de IA sin reconstruir todavía la cadena total de la materia.",
 rows=[
  ("Inventario de sistemas de IA","El inventario registra usos, componentes, poblaciones y consecuencias con vigencia.","No es una lista de licencias ni de modelos adquiridos.","cada asistente se identifica por tarea, versión y permisos","Lo no inventariado no puede evaluarse, gobernarse ni retirarse con seguridad."),
  ("Frontera del sistema","La frontera incluye modelo, datos, instrucciones, herramientas, interfaz, personas y proceso.","No coincide con la API del proveedor.","el registro abarca la decisión de Recepción y sus fuentes","Una frontera estrecha desplaza responsabilidad fuera del análisis."),
  ("Ownership y accountability","El ownership reúne autoridad y recursos para limitar, cambiar y reparar.","Accountability no es atribuir culpa después del daño.","una responsable puede suspender ofertas automáticas","Responsabilidad sin capacidad real crea un fusible humano."),
  ("Clasificación de riesgo","La clasificación vincula uso y consecuencia con obligaciones proporcionales.","No se deriva sólo del tipo de modelo.","responder preguntas y modificar reservas reciben niveles distintos","La clase debe revisarse cuando cambia propósito, población o autonomía."),
  ("Procedencia de datos y modelos","La procedencia reconstruye origen, transformación, permiso, versión y uso.","No se satisface con nombrar una fuente o proveedor.","cada fragmento recuperado conserva documento y vigencia","Procedencia conocida no demuestra calidad, licitud ni pertinencia."),
  ("Gobierno de proveedores","El gobierno de proveedores asigna evidencia, avisos, acceso, auditoría y salida.","Comprar un servicio no terceriza la responsabilidad por su uso.","el contrato exige notificación de cambios materiales","El poder contractual puede limitar controles y debe figurar como riesgo."),
  ("Control de cambios","El control de cambios identifica modificaciones materiales y su evaluación necesaria.","No todo cambio requiere el mismo proceso ni toda actualización es menor.","una nueva herramienta dispara pruebas de permisos y consecuencias","El versionado incompleto vuelve irreproducible un incidente."),
  ("Monitoreo de IA desplegada","El monitoreo combina desempeño, distribución, uso, deriva y consecuencias.","No es observar latencia y disponibilidad solamente.","se sigue corrección por población y frecuencia de escalamiento","Una métrica sin umbral ni autoridad sólo documenta degradación."),
  ("Incidente de IA","Un incidente involucra daño, falla o pérdida de control vinculada con el sistema.","No exige caída técnica ni conducta maliciosa.","una respuesta inventada provoca una compensación improcedente","La clasificación inicial no debe impedir contención ni preservación de evidencia."),
  ("Contestabilidad y reparación","La contestabilidad permite comprender, objetar y obtener revisión efectiva.","No es un formulario sin plazo ni autoridad.","el huésped corrige una decisión y recupera la reserva","Revisar sin reparar deja intacta la consecuencia material."),
  ("Retiro y salida","El retiro elimina o desactiva capacidad sin perder continuidad, evidencia ni derechos.","No equivale a dejar de pagar una licencia.","se revocan accesos y se preservan registros necesarios","Dependencia del proveedor puede volver inviable una salida prometida."),
  ("Sistema de gestión de IA","Un sistema de gestión integra política, roles, procesos, evidencia y mejora continua.","No es una certificación ni un comité aislado.","el hotel revisa inventario, incidentes y cambios en una cadencia común","Formalizar puede crear burocracia si no modifica decisiones reales."),
 ],
 instrument_title="Instrumento HH-33: registro vivo de gobierno de IA",
 fields=["Uso y propósito","Frontera","Población y consecuencia","Owner","Riesgo","Datos y modelos","Proveedor","Versión y cambio","Evaluación","Monitoreo","Incidente y reparación","Retiro"],
 transfer_title="Caso de transferencia: selección de personal", transfer=["Una organización incorpora un asistente para ordenar candidaturas y resumir antecedentes. El proveedor actualiza el modelo y Recursos Humanos agrega nuevos criterios sin registrar el cambio.","El registro separa apoyo administrativo de decisión laboral, documenta población y fuentes, exige evaluación desagregada, derecho de revisión y salida practicable.","La transferencia muestra que una política general no gobierna un sistema mutable; lo hace una red de decisiones vigentes."],
 counter_title="Contraejemplo: el código de ética en la intranet", counter=["Una empresa publica principios de transparencia, equidad y control humano y considera resuelto el gobierno.","No conoce cuántos sistemas usa, quién puede detenerlos ni qué cambió desde su aprobación. Ante un incidente, los principios no indican una acción.","Los valores se vuelven gobierno cuando se traducen en inventario, autoridad, evidencia, reparación y retiro."],
 errors=["Inventariar proveedores y no usos","Recortar la frontera al modelo","Nombrar owner sin autoridad","Clasificar una sola vez","Confundir procedencia con calidad","Tercerizar responsabilidad","Aceptar cambios silenciosos","Monitorear sólo disponibilidad","Ocultar incidentes no técnicos","Ofrecer revisión sin reparación","Retirar sin continuidad","Certificar sin aprender"],
 referents=[["NIST","Organiza funciones continuas de gobierno, mapeo, medición y manejo."],["ISO/IEC","Define requisitos de un sistema de gestión de inteligencia artificial."],["European Union","Establece obligaciones diferenciadas por rol y riesgo en la cadena de valor."],["Inioluwa Deborah Raji","Propone auditoría interna con documentación y accountability."],["Margaret Mitchell y colegas","Desarrollaron model cards para transparencia situada."],["Timnit Gebru y colegas","Desarrollaron datasheets para documentar conjuntos de datos."]],
 references=["NIST (2023). Artificial Intelligence Risk Management Framework 1.0. https://doi.org/10.6028/NIST.AI.100-1","NIST (2024). Generative Artificial Intelligence Profile. https://doi.org/10.6028/NIST.AI.600-1","ISO/IEC (2023). ISO/IEC 42001:2023 Artificial Intelligence Management System. https://www.iso.org/standard/42001","ISO/IEC (2023). ISO/IEC 23894:2023 Artificial Intelligence Risk Management. https://www.iso.org/standard/77304.html","European Union (2024). Artificial Intelligence Act. https://eur-lex.europa.eu/eli/reg/2024/1689/oj","European Commission (2025). General Purpose AI Code of Practice. https://digital-strategy.ec.europa.eu/en/policies/contents-code-gpai","Raji, I. D. et al. (2020). Closing the AI Accountability Gap. https://doi.org/10.1145/3351095.3372873","Mitchell, M. et al. (2019). Model Cards for Model Reporting. https://doi.org/10.1145/3287560.3287596","Gebru, T. et al. (2021). Datasheets for Datasets. Communications of the ACM, 64(12), 86-92. https://doi.org/10.1145/3458723","OECD (2023). Advancing Accountability in AI. https://doi.org/10.1787/2448f04b-en","NIST (2026). ARIA 0.1 Pilot Evaluation Report, NIST AI 800-4. https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-4.pdf","Crawford, K. (2021). Atlas of AI. Yale University Press."]
),
34: make_doc(
 block="H", slug="reconstruir_la_cadena_completa_del_problema_al_gobierno",
 title="Reconstruir la cadena completa: del problema y la evidencia a la operación y el gobierno",
 question="¿Cómo demostrar que una intervención conserva coherencia desde el problema inicial hasta sus decisiones, su operación y su gobierno?",
 opening_title="Cada entregable era correcto y la intervención no cerraba",
 opening=["Hotel Horizonte reúne mapas, entrevistas, modelos, contratos, pruebas, tableros y registros de IA. Cada pieza supera su revisión local. Al intentar defender la intervención completa, aparecen saltos: una métrica no responde a la tesis, un control no cubre el daño principal y una decisión operativa no tiene fuente.","El problema no es falta de documentación. Es falta de cadena. Una intervención profesional debe permitir recorrer problema, evidencia, explicación, alternativa, decisión, realización, operación, consecuencia y revisión.","Integrar no significa resumir treinta lecturas ni unir archivos. Significa demostrar coherencia y localizar contradicciones sin borrarlas.","El equipo construye una matriz de trazabilidad argumental. Cada afirmación relevante tiene evidencia, objeción, decisión, owner, señal y condición de revisión.","La cadena también conserva ausencias. Lo que todavía no se sabe aparece como riesgo o próxima prueba, no como espacio rellenado por confianza.","N34 abre el Bloque H. Recibe los instrumentos acumulados de N01 a N33 y los convierte en un expediente defendible de intervención completa."],
 hotel="HH-34 recompone el caso desde la promesa de ingreso. Vincula episodios y actores con la tesis, modelos y alternativas; conecta estrategia con contratos, calidad y operación; y une gobierno de IA con señales e incidentes. Las contradicciones se convierten en preguntas de integración y no en defectos que deban ocultarse.",
 advance="N34 reconstruye la cadena completa desde problema y evidencia hasta operación y gobierno, y convierte un conjunto de artefactos en una intervención trazable.",
 defer="N35 tomará esta cadena y la adaptará a audiencias, objeciones y contextos de transferencia. N34 no diseña todavía la defensa comunicacional ni la apropiación por terceros.",
 rows=[
  ("Cadena de intervención","La cadena relaciona situación, explicación, decisión, acción, consecuencia y revisión.","No es un cronograma ni un listado de entregables.","la promesa del huésped conecta todas las piezas","Una cadena demasiado lineal puede ocultar retroalimentación y conflicto."),
  ("Trazabilidad argumental","La trazabilidad permite seguir una afirmación hasta evidencia, autoridad y uso.","No busca rastrear cada frase ni acumular enlaces.","la tesis se vincula con episodios y decisiones","Trazabilidad formal sin lectura crítica puede legitimar una premisa débil."),
  ("Coherencia vertical","La coherencia vertical alinea problema, outcome, medida y decisión.","No significa que todos los niveles usen la misma métrica.","la demora observada se conecta con una capacidad y un SLO","Optimizar una capa puede contradecir el propósito superior."),
  ("Coherencia horizontal","La coherencia horizontal verifica compatibilidad entre procesos, datos, tecnología y organización.","No equivale a uniformidad entre áreas.","contrato, operación y reparación usan el mismo estado","Diferencias legítimas deben conservar traducciones y no borrarse."),
  ("Registro de supuestos","El registro identifica premisas que sostienen decisiones y sus pruebas.","No es una lista genérica de riesgos.","la disponibilidad de Recepción se prueba en turno nocturno","Un supuesto puede volverse falso sin producir una alerta inmediata."),
  ("Registro de decisiones","El registro conserva alternativas, razones, autoridad, fecha y consecuencia.","No es la minuta completa de una reunión.","se documenta por qué se limita autonomía del agente","Registrar no reemplaza revisar ni reparar una decisión fallida."),
  ("Arquitectura de evidencia","La arquitectura de evidencia define qué fuentes sostienen qué decisiones y con qué vigencia.","No es un repositorio único ni una jerarquía automática de métodos.","entrevistas, trazas y pruebas se triangulan","Más evidencia puede aumentar contradicción y exigir mejor juicio."),
  ("Contradicción productiva","Una contradicción productiva revela fronteras, supuestos o perspectivas incompatibles.","No es un error que deba promediarse ni una opinión equivalente a cualquier dato.","Comercial y Recepción definen liberada de manera distinta","Conservar toda contradicción sin decisión paraliza la intervención."),
  ("Puerta de integración","La puerta comprueba suficiencia conjunta antes de ampliar compromiso.","No es una aprobación por acumulación de firmas.","el piloto avanza sólo si contrato, contingencia y señal cierran","La puerta debe tener autoridad y alternativas reales."),
  ("Expediente mínimo defendible","El expediente mínimo contiene lo necesario para reconstruir y cuestionar la intervención.","No es el documento más corto ni una carpeta exhaustiva.","una audiencia ajena puede seguir la cadena","Reducir demasiado puede ocultar voces y decisiones materiales."),
  ("Prueba de extremo a extremo","La prueba sigue una promesa a través de fronteras y consecuencias.","No se reduce a integración técnica ni camino feliz.","una reserva adversa atraviesa canal, hotel y reparación","Un caso no representa toda la población y debe combinarse con cobertura."),
  ("Cierre con incertidumbre","El cierre declara qué se sabe, qué permanece abierto y quién seguirá observando.","No equivale a certeza total ni a terminar documentos.","la operación acepta señales y preguntas pendientes","Cerrar demasiado pronto congela riesgo; no cerrar nunca diluye responsabilidad."),
 ],
 instrument_title="Instrumento HH-34: expediente integrado de intervención",
 fields=["Promesa y población","Problema","Evidencia","Explicaciones rivales","Outcome","Alternativas","Decisiones","Realización","Operación","Gobierno","Contradicciones","Cierre y revisión"],
 transfer_title="Caso de transferencia: inscripción universitaria", transfer=["Una universidad rediseña inscripción, correlatividades, pagos y soporte. Equipos diferentes presentan soluciones localmente correctas.","HH-34 conecta experiencia estudiantil, reglas académicas, datos, infraestructura, atención e incidentes. La prueba de extremo a extremo revela una excepción que ningún entregable aislado contenía.","La transferencia muestra que integrar es sostener una promesa común a través de fronteras de autoridad."],
 counter_title="Contraejemplo: el portfolio de entregables", counter=["Un equipo presenta todos los artefactos solicitados y los ordena por fecha.","No puede explicar qué decisión habilitó cada uno ni qué contradicción resolvió. El volumen documenta actividad y no intervención.","Un expediente integrado vale porque permite reconstruir el juicio, no porque conserva todo lo producido."],
 errors=["Confundir integración con resumen","Ordenar sólo por cronología","Trazar sin cuestionar","Alinear métricas y olvidar personas","Borrar contradicciones","Registrar todas las reuniones","Acumular evidencia sin decisión","Aprobar por firmas","Probar sólo componentes","Cerrar sin owner","Reabrir todo el curso","Presentar una única explicación"],
 referents=[["Peter Checkland y John Poulter","Conectan indagación, modelos y acción en situaciones problemáticas."],["Donald Schön","Explica reflexión profesional en problemas indeterminados."],["Stephen Toulmin","Estructura afirmaciones, evidencia, garantías y refutaciones."],["ISO/IEC/IEEE","Organiza procesos de ciclo de vida y trazabilidad de información."],["SEBoK","Integra decisiones, requisitos, verificación, validación y ciclo de vida."],["Project Management Institute","Vincula éxito con valor, accountability y adaptación."]],
 references=["Checkland, P. y Poulter, J. (2007). Learning for Action. Wiley. ISBN 978-0-470-02554-3.","Schön, D. A. (1983). The Reflective Practitioner. Basic Books.","Toulmin, S. (2003). The Uses of Argument, Updated Edition. Cambridge University Press.","ISO/IEC/IEEE (2023). ISO/IEC/IEEE 15288:2023 System Life Cycle Processes. https://www.iso.org/standard/81702.html","ISO/IEC/IEEE (2018). ISO/IEC/IEEE 29148:2018 Requirements Engineering. https://www.iso.org/standard/72089.html","SEBoK (2026). Systems Engineering and Management. https://sebokwiki.org/wiki/Systems_Engineering_and_Management","Project Management Institute (2025). PMBOK Guide, Eighth Edition. https://www.pmi.org/standards/pmbok","Project Management Institute (2025). Maximizing Project Success. https://www.pmi.org/-/media/pmi/documents/public/pdf/learning/thought-leadership/project_success_2025_final.pdf","Argyris, C. y Schön, D. A. (1996). Organizational Learning II. Addison-Wesley.","Rittel, H. W. J. y Webber, M. M. (1973). Dilemmas in a General Theory of Planning. Policy Sciences, 4, 155-169.","NIST (2023). Artificial Intelligence Risk Management Framework 1.0. https://doi.org/10.6028/NIST.AI.100-1","Senge, P. M. (2006). The Fifth Discipline, Revised Edition. Currency."]
),
35: make_doc(
 block="H", slug="comunicar_defender_y_transferir_criterios",
 title="Comunicar, defender y transferir criterios sin copiar soluciones",
 question="¿Cómo lograr que audiencias distintas comprendan, cuestionen y usen una intervención sin reducirla a un relato persuasivo ni copiar su forma?",
 opening_title="La misma presentación convenció al comité y confundió a Operaciones",
 opening=["El equipo de Hotel Horizonte presenta la intervención con una única secuencia de diapositivas. Dirección escucha demasiado detalle técnico, Tecnología recibe conclusiones sin evidencia y Recepción no encuentra qué debe hacer ante una excepción.","La propuesta era la misma, pero la decisión de cada audiencia era distinta. Comunicar profesionalmente no consiste en simplificar un contenido fijo. Consiste en conservar la cadena de evidencia mientras cambia foco, lenguaje, forma y profundidad.","Defender tampoco significa neutralizar objeciones. Una objeción puede revelar evidencia faltante, una autoridad ausente o un costo desplazado.","El equipo diseña cuatro recorridos conectados por el mismo expediente. Cada uno declara decisión solicitada, afirmaciones, fuentes, incertidumbre, consecuencias y próximo paso.","La transferencia se prueba cuando otra persona puede aplicar criterios en un caso nuevo sin copiar la solución del hotel.","N35 recibe de N34 una cadena integrada y la convierte en capacidad de comunicación, defensa, apropiación y transferencia."],
 hotel="HH-35 prepara una defensa ejecutiva, una revisión técnica, un handoff operativo y una explicación accesible para huéspedes afectados. Todas comparten tesis, evidencia y límites. Un registro de objeciones modifica el expediente cuando aparece una explicación rival mejor.",
 advance="N35 comunica según audiencia, responde objeciones y transfiere criterios sin copiar soluciones ni perder trazabilidad.",
 defer="N36 utilizará defensa, resultado y sorpresa para construir práctica reflexiva continua. N35 no convierte todavía la experiencia en un sistema personal y colectivo de aprendizaje.",
 rows=[
  ("Audiencia y decisión","Una audiencia se define por la decisión que debe tomar, su conocimiento y su exposición.","No es un segmento demográfico ni un nivel de jerarquía.","Dirección decide inversión y Recepción decide contingencia","Adaptar no autoriza ocultar consecuencias relevantes."),
  ("Tesis comunicable","La tesis expresa una afirmación central, su mecanismo y su alcance.","No es un eslogan ni una lista de beneficios.","la propuesta conecta menor espera con reglas y reparación","Una tesis breve puede seguir siendo falsa o incompleta."),
  ("Afirmación, evidencia y garantía","Un argumento conecta una afirmación con evidencia mediante una razón explícita.","La fuente no habla por sí sola ni la autoridad reemplaza la garantía.","un episodio y una traza sostienen la explicación","La misma evidencia puede admitir interpretaciones rivales."),
  ("Narrativa ejecutiva","La narrativa ejecutiva organiza contexto, decisión, valor, riesgo y compromiso.","No elimina complejidad ni promete certeza.","el comité ve alternativas y condición de salida","Resumir puede silenciar poblaciones o dependencias críticas."),
  ("Defensa técnica","La defensa técnica expone arquitectura, contratos, pruebas, límites y operación.","No es una exhibición de herramientas ni cantidad de detalle.","Tecnología puede reproducir una prueba adversa","Precisión técnica sin conexión con outcome es insuficiente."),
  ("Handoff operativo","El handoff transfiere capacidad para observar, decidir, actuar y reparar.","No es entregar manuales al final.","el turno nocturno resuelve sin llamar al proyecto","La autonomía requiere recursos y autoridad, no sólo conocimiento."),
  ("Comunicación con personas afectadas","La comunicación afectada explica consecuencia, opciones, revisión y reparación.","No es marketing ni descargo legal ilegible.","el huésped entiende por qué cambió su reserva","Transparencia excesivamente técnica también puede ocultar."),
  ("Objeción","Una objeción cuestiona afirmación, evidencia, garantía, consecuencia o autoridad.","No es resistencia que deba vencerse.","Operaciones muestra que la contingencia no funciona bajo carga","No toda objeción tiene el mismo respaldo y debe evaluarse."),
  ("Incertidumbre comunicada","Comunicar incertidumbre distingue desconocimiento, variabilidad y desacuerdo.","No es debilitar una propuesta ni agregar una advertencia genérica.","se declara qué dato cambiaría la recomendación","Ocultar incertidumbre produce confianza frágil; exagerarla impide decidir."),
  ("Evidencia visual","La evidencia visual organiza relaciones, cantidades o secuencias que necesitan verse.","No es decoración ni sustituto de explicación.","un mapa conecta actores, estados y reparación","Un gráfico puede naturalizar escalas, omisiones o causalidades falsas."),
  ("Transferencia por criterios","La transferencia conserva preguntas, mecanismos y límites al cambiar contexto.","No copia soluciones, roles ni métricas del caso original.","otro hotel usa criterios y diseña una contingencia distinta","Abstraer demasiado produce consejos genéricos sin poder de decisión."),
  ("Teach back","Teach back verifica apropiación pidiendo reconstruir y usar el criterio.","No es repetir una definición ni aprobar una exposición.","un equipo nuevo explica cuándo no usar el agente","Una buena explicación no garantiza capacidad bajo presión y necesita práctica."),
 ],
 instrument_title="Instrumento HH-35: matriz de defensa y transferencia",
 fields=["Audiencia","Decisión","Tesis","Evidencia","Garantía","Objeción principal","Incertidumbre","Consecuencia","Forma visual","Acción esperada","Teach back","Criterio transferible"],
 transfer_title="Caso de transferencia: guardia hospitalaria", transfer=["Un hospital recibe el expediente del Hotel Horizonte y no copia su agente ni sus métricas. Utiliza criterios de tarea, severidad, supervisión y reparación para evaluar apoyo a la guardia.","La defensa se adapta a conducción clínica, tecnología, profesionales y pacientes, pero conserva fuentes, límites y autoridad.","La transferencia ocurre cuando el nuevo equipo produce una solución diferente con una cadena de juicio reconocible."],
 counter_title="Contraejemplo: adaptar el logo", counter=["Una consultora replica la presentación del hotel, cambia nombres y conserva la misma secuencia de solución.","El contexto tiene otra población, autoridad y daño. La forma viaja, pero el criterio no.","Transferir exige reconstruir el problema con las preguntas aprendidas y aceptar que la respuesta cambie."],
 errors=["Usar una presentación para todos","Confundir brevedad con claridad","Citar sin garantía","Vender certeza","Mostrar detalle sin decisión","Entregar manuales sin práctica","Hablar por personas afectadas","Tratar objeción como resistencia","Ocultar incertidumbre","Decorar con gráficos","Copiar soluciones","Evaluar por repetición"],
 referents=[["Stephen Toulmin","Ofrece una anatomía práctica de argumentos y refutaciones."],["Edward Tufte","Vincula representación visual con integridad de evidencia."],["Donald Schön","Sitúa la conversación reflexiva dentro de la práctica profesional."],["Chris Argyris","Analiza rutinas defensivas y aprendizaje organizacional."],["Paulo Freire","Concibe comunicación y aprendizaje como diálogo situado."],["Etienne Wenger","Explica aprendizaje, participación y comunidades de práctica."]],
 references=["Toulmin, S. (2003). The Uses of Argument, Updated Edition. Cambridge University Press.","Tufte, E. R. (2001). The Visual Display of Quantitative Information, Second Edition. Graphics Press.","Schön, D. A. (1983). The Reflective Practitioner. Basic Books.","Argyris, C. (1991). Teaching Smart People How to Learn. Harvard Business Review, 69(3), 99-109.","Freire, P. (2005). Pedagogy of the Oppressed, 30th Anniversary Edition. Continuum.","Wenger, E. (1998). Communities of Practice. Cambridge University Press.","Heath, C. y Heath, D. (2007). Made to Stick. Random House.","Norman, D. A. (2013). The Design of Everyday Things, Revised and Expanded Edition. Basic Books.","ISO (2010). ISO 9241-210:2010 Human Centred Design for Interactive Systems. https://www.iso.org/standard/52075.html","W3C (2023). Web Content Accessibility Guidelines 2.2. https://www.w3.org/TR/WCAG22/","Project Management Institute (2025). Maximizing Project Success. https://www.pmi.org/-/media/pmi/documents/public/pdf/learning/thought-leadership/project_success_2025_final.pdf","Checkland, P. y Poulter, J. (2007). Learning for Action. Wiley. ISBN 978-0-470-02554-3."]
),
36: make_doc(
 block="H", slug="practica_reflexiva_y_aprendizaje_profesional",
 title="Práctica reflexiva: aprender de decisiones, errores, sorpresas y asistencia de IA",
 question="¿Cómo convertir la experiencia de intervenir en una capacidad profesional que aprende sin reescribir el pasado ni delegar la reflexión?",
 opening_title="La intervención funcionó y eso no cerró el aprendizaje",
 opening=["Hotel Horizonte reduce la espera y mejora la reparación. La solución cumple sus objetivos. Meses después, una nueva temporada altera el patrón de reservas y una práctica manual que parecía transitoria se vuelve central.","El éxito inicial no vuelve correctas todas las explicaciones. La sorpresa obliga a comparar lo esperado con lo ocurrido, revisar supuestos y reconocer decisiones que produjeron consecuencias no anticipadas.","La reflexión profesional no es una confesión ni una lista de lecciones aprendidas. Reconstruye episodios, distingue resultado de razonamiento y modifica teorías de acción.","El equipo conserva un diario de decisiones, realiza revisiones posteriores y prueba cambios. También utiliza IA para explorar hipótesis y criticar borradores, pero registra fuentes, desacuerdos y decisiones propias.","Aprender implica cambiar no sólo una respuesta, sino también las reglas con que se define un problema y se distribuye autoridad.","N36 cierra el curso. Integra decisiones, errores, sorpresas y asistencia de IA en una práctica capaz de seguir aprendiendo después de la materia."],
 hotel="HH-36 compara la promesa, la evidencia esperada y los resultados de la intervención. Identifica sorpresas, reconstruye teorías en uso, separa corrección local de cambio de marco y convierte cada aprendizaje en una práctica verificable. El cierre deja un sistema personal y colectivo de revisión.",
 advance="N36 cierra el curso con una práctica reflexiva capaz de aprender de decisiones, errores, sorpresas y asistencia de inteligencia artificial sin delegar el juicio.",
 defer="N36 no clausura una doctrina. Deja un método de aprendizaje profesional: reconstruir situaciones, contrastar explicaciones, intervenir con límites, observar consecuencias y revisar criterios junto con otras personas.",
 rows=[
  ("Reflexión en la acción","La reflexión en la acción examina y modifica el encuadre mientras se interviene.","No es improvisación sin registro ni aplicación automática de teoría.","Recepción adapta una contingencia ante una excepción inédita","La presión puede reducir contraste y exige límites previos."),
  ("Reflexión sobre la acción","La reflexión sobre la acción reconstruye después un episodio y su razonamiento.","No es evaluar sólo el resultado ni justificar retrospectivamente.","el equipo compara decisión, expectativa y consecuencia","La memoria es selectiva y necesita trazas y voces múltiples."),
  ("Sorpresa","La sorpresa es una diferencia significativa entre lo esperado y lo observado.","No todo desvío es error ni todo error produce aprendizaje.","la práctica manual explica un éxito atribuido al software","Normalizar la sorpresa impide revisar el marco."),
  ("Teoría declarada y teoría en uso","La teoría declarada expresa lo que se dice hacer; la teoría en uso se infiere de acciones.","La diferencia no equivale automáticamente a hipocresía.","el protocolo promete revisión y el turno evita escalar","Observar conducta sin contexto puede atribuir intención incorrecta."),
  ("Aprendizaje de bucle simple","El bucle simple corrige acciones para alcanzar objetivos y reglas vigentes.","No cuestiona necesariamente el objetivo ni su distribución.","se ajusta un umbral para reducir falsas alertas","Corregir puede estabilizar un sistema injusto."),
  ("Aprendizaje de doble bucle","El doble bucle revisa supuestos, objetivos, reglas y autoridad.","No consiste en discutir todo desde cero.","se redefine éxito para incluir reparación y accesibilidad","Cambiar el marco requiere legitimidad y puede encontrar resistencia."),
  ("Diario de decisiones","El diario conserva contexto, alternativas, evidencia, confianza y revisión.","No es una bitácora de actividad ni vigilancia individual.","una decisión de autonomía registra qué la haría retroceder","Registrar demasiado puede volver invisible lo importante."),
  ("Revisión posterior","La revisión posterior estudia condiciones y mecanismos para mejorar capacidad.","No es una búsqueda de culpable ni una cronología ornamental.","un incidente modifica contrato, entrenamiento y señal","Seguridad psicológica no elimina accountability ni reparación."),
  ("Práctica deliberada","La práctica deliberada ejercita una capacidad específica con feedback y dificultad creciente.","Repetir tareas habituales no garantiza aprendizaje.","el equipo ensaya objeciones y escenarios adversos","La práctica sin conexión con trabajo real puede volverse ritual."),
  ("Portfolio de aprendizaje","El portfolio selecciona evidencia de cambio de juicio y capacidad.","No es una colección exhaustiva de entregables.","se comparan versiones y razones de una decisión","Curar sólo éxitos elimina la evidencia más formativa."),
  ("IA como interlocutora crítica","La IA puede proponer rivales, simular objeciones y ayudar a explorar.","No es fuente automática, evaluadora neutral ni sustituta de reflexión.","un modelo critica el expediente y el estudiante verifica cada objeción","La fluidez puede reforzar marcos dominantes e inventar respaldo."),
  ("Sistema de aprendizaje profesional","El sistema integra registro, conversación, prueba, feedback y revisión continua.","No depende de motivación individual ni de un curso permanente.","la comunidad revisa casos y actualiza criterios","Sin tiempo, seguridad y autoridad, el aprendizaje queda declarado."),
 ],
 instrument_title="Instrumento HH-36: sistema personal y colectivo de práctica reflexiva",
 fields=["Episodio","Expectativa","Decisión","Evidencia disponible","Resultado","Sorpresa","Teoría en uso","Explicación rival","Bucle de aprendizaje","Cambio practicable","Asistencia de IA","Próxima revisión"],
 transfer_title="Caso de transferencia: primera experiencia profesional", transfer=["Una persona egresada recibe un pedido ambiguo en su primer trabajo. No posee la solución de Hotel Horizonte, pero reconoce actores, evidencia, fronteras, alternativas y condiciones de revisión.","Registra una decisión provisional, solicita contraste y usa IA para explorar objeciones sin delegar fuentes ni autoridad. Después compara lo esperado con el resultado y actualiza su criterio.","La transferencia final no es recordar treinta y seis respuestas. Es poder construir una intervención defendible y seguir aprendiendo de ella."],
 counter_title="Contraejemplo: la lista de lecciones aprendidas", counter=["Al cerrar un proyecto, el equipo enumera comunicar más, probar antes y mejorar coordinación.","Las frases no nombran episodios, mecanismos, responsables ni cambios observables. Pueden repetirse después de cualquier proyecto y no modifican práctica.","Una lección existe cuando cambia una decisión, una prueba o una capacidad y queda una señal para revisarla."],
 errors=["Confundir reflexión con opinión","Juzgar sólo resultados","Explicar toda sorpresa como excepción","Reescribir lo que se sabía","Corregir sin revisar objetivos","Cuestionar todo sin decidir","Registrar actividad y no razones","Buscar culpables","Practicar sin feedback","Mostrar sólo éxitos","Delegar crítica a la IA","Declarar aprendizaje sin capacidad"],
 referents=[["Donald Schön","Fundó una teoría de práctica reflexiva para problemas indeterminados."],["Chris Argyris y Donald Schön","Distinguen aprendizaje de bucle simple y doble."],["John Dewey","Vincula experiencia, investigación y reflexión."],["David Kolb","Modela aprendizaje experiencial como ciclo de transformación."],["Amy Edmondson","Estudia seguridad psicológica, voz y aprendizaje en equipos."],["Jack Mezirow","Analiza transformación de marcos de referencia mediante reflexión crítica."]],
 references=["Schön, D. A. (1983). The Reflective Practitioner. Basic Books.","Argyris, C. y Schön, D. A. (1996). Organizational Learning II. Addison-Wesley.","Dewey, J. (1938). Experience and Education. Macmillan.","Kolb, D. A. (1984). Experiential Learning. Prentice Hall.","Edmondson, A. C. (1999). Psychological Safety and Learning Behavior in Work Teams. Administrative Science Quarterly, 44(2), 350-383. https://doi.org/10.2307/2666999","Mezirow, J. (1991). Transformative Dimensions of Adult Learning. Jossey-Bass.","Senge, P. M. (2006). The Fifth Discipline, Revised Edition. Currency.","Freire, P. (2005). Pedagogy of the Oppressed, 30th Anniversary Edition. Continuum.","NIST (2023). Artificial Intelligence Risk Management Framework 1.0. https://doi.org/10.6028/NIST.AI.100-1","UNESCO (2024). AI Competency Framework for Students. https://www.unesco.org/en/articles/ai-competency-framework-students","Moon, J. A. (2004). A Handbook of Reflective and Experiential Learning. Routledge.","Wenger, E. (1998). Communities of Practice. Cambridge University Press."]
),
}


base.REFERENCE_NOTES.update({
    "Updated OECD": "distingue sistemas por inferencia, objetivos, salidas e interacción con el entorno",
    "AI Competency": "integra perspectiva humana, ética, técnica y diseño de sistemas",
    "Human AI Interaction": "aporta pautas para expectativa, control, corrección y recuperación",
    "ARIA 0.1": "muestra por qué la evaluación previa necesita observación repetida en despliegue",
    "TEVV-Athlon": "propone una arquitectura borrador para evaluación sociotécnica continua",
    "Gender Shades": "demuestra cómo el promedio puede ocultar desigualdades relevantes",
    "Moral Crumple": "explica cómo la responsabilidad puede deformarse alrededor de personas supervisoras",
    "Closing the AI": "conecta auditoría con documentación, roles y procesos internos",
    "Model Cards": "documenta desempeño, usos previstos y límites de modelos",
    "Datasheets": "documenta motivación, composición, recolección y uso de datos",
    "Advancing Accountability": "organiza elementos de accountability a lo largo del ciclo de vida",
    "Uses of Argument": "estructura afirmación, evidencia, garantía, calificador y refutación",
    "Maximizing Project": "define éxito como valor suficiente para justificar esfuerzo y gasto",
    "Visual Display": "vincula forma gráfica con densidad e integridad de evidencia",
    "Psychological Safety": "explica condiciones para voz, error y aprendizaje en equipos",
    "Transformative Dimensions": "analiza revisión crítica de marcos de referencia",
})


def build(number: int, spec: dict) -> None:
    base.build(number, spec)
    code = f"N{number:02d}"
    block = "G" if number <= 33 else "H"
    package = ROOT / f"{code}-content-canonical"
    (package / "CHANGELOG.md").write_text(
        f"# {code} · Changelog\n\n"
        f"- Creación del contenido canónico v1 para el Bloque {block}.\n"
        f"- Integración de HH-{number:02d}, Hotel Horizonte, transferencia, límites y referencias ancladas.\n",
        encoding="utf-8",
    )


def main() -> None:
    base.DOCS = DOCS
    for number, spec in DOCS.items():
        build(number, spec)
    print(json.dumps({f"N{n:02d}": d["title"] for n, d in DOCS.items()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
