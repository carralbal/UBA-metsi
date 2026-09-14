#!/usr/bin/env python3
"""Amplía las tesis N01–N36 según el estándar pedagógico de N00."""
from __future__ import annotations
import argparse, hashlib, json, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Cada especificación agrega mecanismo, ejemplo, límite, caso longitudinal y
# consecuencia. Las tres familias de redacción evitan convertir la colección
# en una plantilla verbal repetitiva.
SPECS: dict[int, tuple[str,str,str,str,str]] = {
  1:("separar el pedido de la situación, construir explicaciones rivales y buscar evidencia capaz de debilitarlas antes de comprometer una solución",
     "una facultad pide un chatbot; observar consultas y abandonos puede revelar que hace falta información accesible o un cambio de proceso, no necesariamente conversación automática",
     "usar la complejidad como excusa para no decidir: una reparación urgente puede hacerse mientras la explicación completa permanece abierta",
     "«integrar todo» se desarma en episodios, actores y consecuencias; Recepción, Housekeeping, Comercial y Tecnología no describen el mismo problema",
     "cambiar la pregunta de qué solución implementar por qué intervención puede justificarse y revisarse; ese criterio orienta el resto de la colección"),
  2:("elegir la frontera según la pregunta e incluir reglas, conversaciones, terceros, excepciones y reparaciones capaces de cambiar el resultado",
     "una transferencia rechazada puede originarse en la pantalla, un límite antifraude, una demora de identidad o una regla diferente entre canales",
     "afirmar que todo está conectado y producir un inventario infinito que no cambia hipótesis, riesgos ni decisiones",
     "una reserva confirmada falla aunque el PMS responda: la promesa atraviesa Comercial, Housekeeping, cerraduras, Recepción y reparación",
     "declarar para qué se dibuja una frontera y qué evidencia obligaría a moverla; N03 examinará relaciones y retroalimentaciones"),
  3:("describir qué cambia, en qué dirección, con qué demora y qué circuitos refuerzan o compensan el efecto observado",
     "agregar personal reduce una cola, pero el apuro puede aumentar errores que regresan como retrabajo y eliminan la mejora inicial",
     "atribuir cualquier sorpresa a la complejidad cuando una regla mal configurada explica de manera directa todos los fallos",
     "la llegada anticipada reordena Housekeeping, demora otras habitaciones y crea compensaciones que retroalimentan la presión operativa",
     "intervenir sobre una relación explicada y observar efectos previstos y no previstos; N04 separará hechos, síntomas e hipótesis"),
  4:("distinguir observación, diferencia relevante, relato situado e hipótesis causal, y declarar qué evidencia autoriza cada afirmación",
     "que el abandono sea doce por ciento no prueba que la interfaz sea difícil: hacen falta recorridos, poblaciones y cambios simultáneos",
     "exigir evidencia perfecta antes de contener un error urgente, confundiendo una acción prudente con una explicación ya demostrada",
     "«habitación liberada» es un registro, no prueba de alojamiento; áreas y cerraduras usan estados con alcances diferentes",
     "unir afirmación, observación y decisión sin borrar perspectivas; N05 incorporará poder, afectados y autoridad"),
  5:("distinguir lo que cada actor declara, puede hacer, controla y debe soportar, incluyendo a quienes no participan de la aprobación",
     "automatizar turnos beneficia a Dirección y puede excluir a personas sin conectividad mientras soporte absorbe nuevas excepciones",
     "tratar toda diferencia como conflicto irreconciliable o creer que escuchar obliga a satisfacer simultáneamente todas las preferencias",
     "Camila promete, Elena acepta riesgo, Lucía repara y Mariela sostiene la operación; el huésped y el turno nocturno también son afectados",
     "diseñar participación, autoridad, objeción y reparación; N06 convertirá dudas relevantes en una estrategia de discovery"),
  6:("identificar la incertidumbre que más puede cambiar la decisión y elegir entrevista, observación, medición o prueba según esa necesidad",
     "antes de construir un portal conviene saber si el problema es carga duplicada, reglas contradictorias o falta de autoridad para aprobar",
     "acumular talleres y hallazgos sin una puerta que indique cuándo avanzar, cambiar o detener la inversión",
     "investigar llegada anticipada exige probar estados, excepciones y reparación en dos pisos, no preguntar si gustaría una app",
     "administrar aprendizaje como inversión con pregunta, método, población y decisión; N07 y N08 profundizarán entrevista y observación"),
  7:("reconstruir episodios y separar lo ocurrido de la interpretación, recordando que el testimonio produce hipótesis pero rara vez las verifica solo",
     "preguntar por la última demora revela señal, momento y decisión; preguntar si necesita una alerta induce una solución",
     "descartar todo relato por subjetivo, perdiendo reglas informales, temores y criterios que ningún registro técnico conserva",
     "Lucía dice que Housekeeping avisa tarde y Mariela que Recepción cambia prioridades; horarios y casos permiten examinar ambas versiones",
     "terminar con mejores distinciones y próximos pasos, no con una lista de pedidos; N08 observará el trabajo que el relato no captura"),
  8:("elegir episodios, registrar secuencias y separar descripción de interpretación para hacer visible coordinación, atajos, esperas y reparación",
     "la aprobación formal tiene tres pasos, pero una observación descubre capturas por mensajería, planillas paralelas y llamadas para destrabar códigos",
     "observar un día extraordinario y presentarlo como funcionamiento habitual, sin declarar período, participantes ni efecto de la propia presencia",
     "seguir un turno muestra cómo Lucía combina pantallas, llamadas y notas porque un estado correcto puede llegar tarde para su decisión",
     "conectar conducta, contexto y consecuencia sin atribuir motivos apresurados; N09 evaluará experiencia, acceso y adopción"),
  9:("tratar experiencia, accesibilidad y adopción como relaciones entre personas, tareas y condiciones, no como capas visuales agregadas al final",
     "un formulario con buen contraste sigue excluyendo si pide un dato desconocido o expira antes de que la persona pueda conseguirlo",
     "explicar baja adopción como resistencia al cambio y evitar revisar capacitación, incentivos, pérdida de autonomía o fallos legítimos de la práctica",
     "la llegada termina cuando el huésped se aloja o recibe reparación comprensible, no cuando completa correctamente una pantalla",
     "definir población, tarea crítica, barrera y criterio de éxito; N10 formulará outcomes verificables sin confundirlos con métricas de interfaz"),
 10:("conectar población, resultado, contexto, evidencia y guardas para comparar alternativas sin quedar atados a la primera solución propuesta",
     "«reducir tiempo hasta una reparación confirmada» orienta mejor que «digitalizar reclamos» y no decide todavía entre app, integración o cambio de regla",
     "mejorar un promedio cerrando casos difíciles o excluyendo poblaciones y presentar el indicador como prueba de mejora del sistema",
     "el outcome es completar la llegada o recibir reparación bajo condiciones acordadas, no simplemente integrar el PMS",
     "cerrar el primer bloque con un problema y un resultado examinables; N11 evaluará cuándo los datos alcanzan para sostener afirmaciones"),
 11:("reconstruir definición, población, período, procedencia y transformación para saber si un valor representa el fenómeno pertinente a la decisión",
     "un 97 por ciento de check-in no prueba satisfacción si el denominador excluye cancelaciones, derivaciones y reparaciones",
     "descartar un dato imperfecto que sí alcanza para detener una prueba riesgosa, aunque no permita estimar una tasa anual",
     "el tablero es reproducible pero declara disponibilidad antes de que Recepción pueda entregar; precisión y validez no son lo mismo",
     "conservar la ruta del fenómeno al dato y del dato a la decisión; N12 distinguirá eventos, estados, comandos y autoridad"),
 12:("separar lo que ocurrió, la condición vigente y la intención de producir un cambio, además de quién tiene autoridad para declarar cada cosa",
     "«aprobar pago» es comando, «pago aprobado» evento y «cuenta al día» estado; un reintento duplicado puede producir consecuencias reales",
     "construir una taxonomía perfecta que no evita contradicciones ni mejora ninguna decisión, trazabilidad o reparación",
     "limpiar no equivale a preparada y preparada no garantiza asignable; Housekeeping, cerraduras y Recepción aportan autoridades distintas",
     "modelar lenguaje junto con tiempo y responsabilidad; N13 mostrará demoras, concurrencia, idempotencia y reconciliación"),
 13:("declarar qué divergencia entre fuentes puede tolerarse, durante cuánto tiempo y qué mecanismo detecta, reconcilia o compensa consecuencias incorrectas",
     "una compra aprobada en un servicio y pendiente en otro puede esperar, salvo que la diferencia libere mercadería o cobre dos veces",
     "exigir consistencia instantánea para todo o aceptar cualquier demora bajo la etiqueta vacía de consistencia eventual",
     "PMS, Housekeeping y cerradura conservan versiones diferentes; Lucía necesita decidir y Federico reconstruir tiempos sin borrar el episodio",
     "preguntar qué decisión depende de cada estado y cómo se recupera; N14 recorrerá handoffs, colas y excepciones"),
 14:("seguir la capacidad completa desde el pedido hasta el resultado y localizar esperas, pérdidas de información y decisiones sin responsable",
     "seis áreas cumplen sus tiempos internos y el caso llega tarde porque los días de cola no pertenecen a ningún indicador local",
     "dibujar el caso feliz con cajas y flechas sin representar devoluciones, urgencias, trabajos incompletos ni criterios de aceptación",
     "la llegada atraviesa reserva, preparación, asignación, acceso y reparación; ninguna área tiene éxito si el huésped espera",
     "medir flujo desde una promesa compartida sin borrar responsabilidades; N15 comparará modelos según la decisión que ayudan a tomar"),
 15:("seleccionar qué aspecto representar según pregunta, audiencia, costo de mantenimiento y aquello que el modelo deja deliberadamente afuera",
     "experiencia muestra barreras, BPMN eventos y responsabilidades, C4 relaciones de software; superponerlos no produce automáticamente una mejor explicación",
     "usar UML, BPMN o una plantilla porque es estándar, aunque su precisión no sirva a la conversación o decisión presente",
     "Lucía sigue el episodio, Federico los contratos y Elena autoridad y riesgo; los modelos comparten objetos pero no escala",
     "justificar utilidad y límite de cada representación; N16 gobernará versiones, vínculos y contradicciones durante el ciclo de vida"),
 16:("conservar propósito, vigencia, responsable y vínculos entre modelos sin exigir que perspectivas legítimamente distintas digan lo mismo",
     "«cliente» puede significar quien paga en un catálogo y quien recibe el servicio en un mapa de experiencia; combinar métricas vuelve crítica la diferencia",
     "centralizar archivos y llamarlo fuente única de verdad, o aceptar contradicciones que activan acciones incompatibles como simple riqueza interpretativa",
     "Comercial, Recepción y Housekeeping usan «disponible» para decisiones diferentes y deben declarar cuándo cada sentido vale",
     "tratar modelos como activos vivos; N17 elegirá lógicas de intervención según incertidumbre, reversibilidad y consecuencia"),
 17:("asignar a cada tramo una lógica explícita: anticipar obligaciones, iterar representaciones, entregar capacidad, adaptar con señales o experimentar hipótesis",
     "una migración planifica respaldos, itera interfaz, libera incrementos y prueba un mensaje; la combinación vale si cada tramo espera evidencia distinta",
     "llamar ágil a cualquier cambio tardío o predictivo a cualquier plan, sin distinguir aprendizaje, compromiso ni criterio de revisión",
     "contratos requieren anticipación, estados iteración, dos pisos un incremento y la llegada anticipada un experimento limitado",
     "componer una estrategia situada en vez de elegir identidad metodológica; N18 incorporará legado, regulación y memoria documental"),
  18:("examinar qué capacidad, derecho, riesgo o memoria sostiene cada tecnología, norma o documento antes de conservarlo, sustituirlo o retirarlo",
     "una planilla duplica trabajo pero registra excepciones que el sistema nuevo ignora; eliminarla sin capturar ese conocimiento debilita la operación",
     "usar cumplimiento para clausurar toda alternativa o tratar documentación como burocracia hasta que un incidente exige explicar decisiones y versiones",
     "registros de llaves, contratos de canal y procedimientos de emergencia se revisan por la protección que conservan, no por su antigüedad",
     "modernizar con hipótesis de retiro, prueba y reversión; N19 comparará configurar, integrar, construir y no automatizar"),
 19:("comparar configurar, integrar, construir y conservar trabajo humano según capacidad, costo total, control, dependencia y posibilidad de cambio",
     "una regla común puede configurarse, una coordinación exigir API, una diferencia justificar desarrollo y un caso raro conservar revisión humana",
     "construir para evitar adaptar el trabajo o comprar para trasladar al proveedor la responsabilidad por integración, operación y gobierno",
     "la llegada anticipada admite PMS, integración, servicio propio o circuito asistido; cada alternativa debe preservar estados y reparación",
     "convertir preferencia tecnológica en decisión trazable; N20 organizará pruebas, hitos y condiciones de salida"),
 20:("unir preguntas, incertidumbres, decisiones, evidencia, hitos y puertas para saber por qué se avanza y qué señal obliga a revisar",
     "antes de contratar todo se demuestra una llegada operable con datos reales, excepciones reparables y riesgo dentro del límite acordado",
     "cambiar el plan ante cada dificultad sin conservar rumbo, evidencia ni autoridad, confundiendo flexibilidad con ausencia de compromiso",
     "contratos, prueba de estados, slice de dos pisos y expansión comercial tienen puertas distintas; terminar tareas no abre por sí solo ninguna",
     "hacer visible la lógica entre trabajo y decisión; N21 distinguirá proyecto, producto, servicio y plataforma"),
 21:("distinguir el cambio temporal del proyecto, el aprendizaje de producto, la capacidad continua del servicio y la habilitación común de plataforma",
     "migrar identidad es proyecto, mejorar inscripción producto, garantizar atención servicio y ofrecer pagos reutilizables plataforma",
     "declarar éxito al entregar software sin responsable de operación, adopción, incidentes y evolución, o sostener un producto sin condición de retiro",
     "instalar componentes puede ser proyecto, pero la llegada es servicio, la promesa aprende como producto y ciertas capacidades actúan como plataforma",
     "asignar horizonte, métricas y responsabilidad; N22 tratará toda iniciativa como hipótesis revisable"),
 22:("explicitar cómo entregables y cambios de práctica producirían un resultado, qué supuestos median y qué observación podría refutar la apuesta",
     "un portal prueba entrega; resolver sin derivación prueba capacidad; comparar llamadas y problemas pendientes ayuda a evaluar el efecto esperado",
     "interpretar cualquier resultado como confirmación o exigir un experimento aleatorio incluso cuando otra evidencia proporcional alcanza",
     "automatizar confirmaciones supone mejorar la llegada sin aumentar promesas incumplibles; velocidad con más compensaciones debilita la hipótesis",
     "gobernar inversión por evidencia y no por inercia; N23 construirá slices completos que produzcan aprendizaje"),
 23:("cortar una capacidad completa para una población pequeña, atravesando interfaz, reglas, datos, operación y reparación, y confrontar una incertidumbre decisiva",
     "todas las pantallas terminadas no alojan a nadie; una llegada completa en dos pisos demuestra menos volumen pero mucha más capacidad",
     "llamar MVP a una versión precaria que traslada trabajo o daño y sólo funciona durante una demostración controlada",
     "Lucía confirma, Mariela prepara, Federico conecta y Ricardo observa excepciones; una feature flag limita población y permite detener",
     "vincular terminado con capacidad y evidencia; N24 hará visible qué se posterga y quién asume la espera"),
 24:("decidir qué recibe capacidad ahora, qué espera y qué no se hará, declarando criterio, restricción, costo de demora y población afectada",
     "una obligación próxima y una mejora de conversión parecen ambas valiosas, pero fecha, reversibilidad y daño cambian el orden razonable",
     "usar una fórmula de puntaje como autoridad neutral o mantener tantas prioridades que el WIP impide terminar cualquiera",
     "accesibilidad, eventos y canales externos compiten por capacidad; Elena, Camila y Lucía deben hacer explícitas renuncias y revisiones",
     "convertir postergación en decisión visible; N25 examinará WIP, colas, lote, espera y feedback"),
 25:("observar llegada, espera, trabajo en curso, terminación y retorno de información para entender el flujo real más allá de reuniones y tableros",
     "iniciar diez casos aumenta sensación de actividad pero alarga cada entrega; limitar WIP permite terminar, aprender y liberar capacidad",
     "copiar ceremonias de Scrum o columnas de Kanban sin políticas explícitas, criterios de terminado ni respuesta a bloqueos",
     "reservas, habitaciones y reparaciones fluyen con relojes distintos; un límite visible evita prometer más llegadas de las que pueden completarse",
     "gestionar identidad y espera de cada caso; N26 ampliará el flujo hacia servicios, plataformas y terceros"),
 26:("mapear capacidades, dependencias, contratos y responsabilidades entre servicios internos, plataformas y proveedores que producen una misma promesa",
     "un pago depende de identidad, red, antifraude y banco; que cada componente esté disponible no garantiza completar la operación",
     "dibujar un ecosistema como catálogo de logos sin mostrar qué capacidad se pierde, quién responde y cómo se opera una degradación",
     "PMS, channel manager, cerraduras y mensajería participan de la llegada; Recepción necesita una salida aunque un tercero falle",
     "gobernar el servicio por dependencia y consecuencia; N27 precisará contratos sintácticos, semánticos, temporales y operacionales"),
 27:("distinguir forma del mensaje, significado, expectativas de tiempo y obligaciones de operación para que una integración conserve el propósito del servicio",
     "dos APIs aceptan el mismo campo «disponible», pero una informa limpieza y otra posibilidad efectiva de asignación",
     "considerar exitosa una integración porque responde 200 o porque GitHub muestra una versión desplegada, sin probar significado ni recuperación",
     "PMS y cerraduras intercambian estados correctos en sintaxis pero incompatibles para la decisión de Lucía; el contrato debe incluir tiempo y reparación",
     "hacer verificable la promesa entre equipos y terceros; N28 graduará evidencia de calidad según riesgo"),
 28:("seleccionar atributos y evidencia según consecuencias, poblaciones y tensiones, reconociendo que velocidad, seguridad, accesibilidad y costo pueden competir",
     "una función rápida en promedio puede ser inaceptable si falla en el caso crítico o deja sin alternativa a una población pequeña",
     "declarar calidad total mediante una única cobertura, encuesta o checklist y ocultar qué riesgo o escenario quedó sin examinar",
     "la llegada debe ser usable, segura, accesible y reparable; probar el caso feliz no cubre cerradura caída ni habitación adaptada",
     "argumentar suficiencia de prueba, no acumular controles; N29 gobernará integración, despliegue, aprobación y recuperación"),
 29:("conectar cambio de código, integración, infraestructura, autorización, despliegue y recuperación mediante evidencia y responsabilidades observables",
     "CI puede verificar cada cambio y CD dejarlo listo, pero producción sólo se actualiza cuando riesgos, datos y operación cumplen la puerta acordada",
     "confundir automatización del pipeline con gobierno completo o convertir toda aprobación en espera manual sin criterio",
     "Federico despliega una regla, Ricardo protege continuidad y Elena acepta expansión; rollback técnico no basta si ya hubo huéspedes afectados",
     "hacer cada cambio trazable y recuperable en lo técnico y operativo; N30 observará señales e incidentes"),
 30:("relacionar señales técnicas y de negocio con SLI, SLO, alertas, episodios e impacto para detectar no sólo fallos sino promesas degradadas",
     "latencia normal convive con abandonos porque una regla devuelve respuestas correctas pero inútiles; la señal de negocio completa el diagnóstico",
     "medir todo sin hipótesis ni responsable, crear paneles que nadie usa o convertir un SLO en garantía absoluta fuera de su población",
     "servidores saludables no prueban una llegada saludable; tiempos, reasignaciones, compensaciones y excepciones revelan la experiencia operativa",
     "usar observabilidad para decidir y aprender, no para decorar; N31 evaluará cuándo la IA agrega una capacidad pertinente"),
 31:("separar reglas, predicción, generación y agencia, y comparar cada alternativa con una solución más simple según error, supervisión y reversibilidad",
     "clasificar texto puede requerir reglas o modelo; redactar una respuesta admite generación; ejecutar una acción agrega autoridad y riesgo distintos",
     "usar IA por novedad en una decisión determinista o llamarla asistente cuando actúa sin confirmación y produce consecuencias reales",
     "un modelo puede sugerir reparación, pero Lucía conserva autoridad y evidencia; automatizar compensaciones exige límites mucho más estrictos",
     "elegir IA por pertinencia y no por moda; N32 diseñará evaluación de tareas, cobertura, severidad y desigualdad"),
 32:("evaluar tareas y poblaciones reales con criterios de cobertura, severidad, robustez y supervisión, no sólo con promedios de laboratorio",
     "un modelo acierta 95 por ciento pero concentra errores graves en casos accesibles; el promedio oculta la desigualdad relevante",
     "optimizar un benchmark desconectado del uso o probar sólo ejemplos fáciles que el equipo ya conoce y puede corregir",
     "la asistencia se evalúa con llegadas y excepciones reales, comparando daño, tiempo de reparación y capacidad humana de detectar el error",
     "vincular evaluación con una decisión de uso y expansión; N33 sostendrá gobierno vivo durante cambios e incidentes"),
 33:("mantener inventario, responsable, finalidad, datos, proveedores, cambios, incidentes, reparación y retiro durante todo el ciclo de vida de IA",
     "un modelo aprobado cambia cuando se actualizan datos, prompt, proveedor o integración; cada modificación puede reabrir la evaluación",
     "tratar la revisión inicial como permiso permanente o documentar políticas sin capacidad para detener, reparar y retirar el sistema",
     "Elena autoriza alcance, Federico registra versiones, Lucía supervisa y los incidentes conservan reparación para huéspedes concretos",
     "hacer del gobierno una práctica operativa y no un expediente; N34 reconstruirá la cadena completa de intervención"),
 34:("recorrer en ambos sentidos problema, explicación, evidencia, alternativa, decisión, realización, operación y gobierno para probar coherencia sin borrar contradicciones",
     "desde una promesa puede seguirse cada decisión hasta su consecuencia y, desde un incidente, volver a la evidencia y al encuadre que lo habilitaron",
     "reunir entregables correctos en un archivo y llamarlo intervención coherente aunque usen poblaciones, conceptos o versiones incompatibles",
     "cada rol conserva artefactos válidos en su marco, pero el expediente sólo sirve si explica la llegada completa y sus desacuerdos",
     "hacer auditable la cadena y sus puertas; N35 enseñará a comunicarla, defenderla y transferir criterio"),
 35:("comunicar problema, evidencia, alternativas, decisión, límites y condición de revisión de modo que otra persona pueda comprender y objetar el razonamiento",
     "una recomendación ejecutiva puede ser breve si enlaza anexos y evidencia; una defensa técnica puede ser detallada sin perder la decisión central",
     "copiar una solución como plantilla sin transferir criterios o usar jerga y volumen para ocultar supuestos débiles",
     "Lucía, Federico y Elena necesitan versiones distintas del relato, pero todas deben conservar promesa, población, riesgo y reparación",
     "transferir capacidad de juicio y no dependencia del autor; N36 cerrará con práctica reflexiva y aprendizaje sobre decisiones"),
 36:("reconstruir qué se esperaba, qué ocurrió, qué sorprendió, qué marco se usó y qué decisión futura cambia, incluyendo el papel real de la asistencia de IA",
     "un incidente no enseña por existir: aprende el equipo que compara hipótesis, evidencia y acciones y modifica una práctica verificable",
     "convertir retrospectivas en culpabilización o celebración, o registrar lecciones tan generales que ninguna decisión posterior puede aplicarlas",
     "el historial de llegadas permite revisar promesas, estados, excepciones y gobierno; el caso termina abierto porque la operación seguirá produciendo evidencia",
     "sostener aprendizaje reflexivo, responsabilidad y revisión; N36 cierra la colección sin presentar el juicio profesional como receta terminada"),
}

def _make_additions(number:int, spec:tuple[str,str,str,str,str])->list[str]:
    mechanism,example,limit,hotel,consequence=spec
    families=(
      (f"La tesis se vuelve operativa al {mechanism}. Esa secuencia obliga a declarar qué cambia, qué permanece abierto y qué evidencia podría modificar la decisión. El rigor no proviene de agregar términos, sino de hacer reconstruible el paso entre una observación, una explicación y una acción.",
       f"Un ejemplo sencillo permite verlo: {example}. El caso muestra por qué una misma señal admite explicaciones e intervenciones diferentes. Antes de ampliar alcance conviene precisar población, condición de éxito y fuente de evidencia.",
       f"El límite también importa: {limit}. Ese contraejemplo evita convertir una idea útil en receta universal. Una decisión puede ser provisional, pero debe decir qué protege ahora y cuándo volverá a examinarse.",
       f"En Hotel Horizonte, {hotel}. El caso longitudinal obliga a sostener la misma promesa mientras cambian el modelo y la evidencia; así puede verse qué aprendió realmente el equipo.",
       f"La consecuencia profesional es {consequence}. La tesis no cierra la discusión: fija un criterio común para que el encuentro pueda comparar argumentos, producir evidencia y decidir sin ocultar incertidumbre."),
      (f"En términos prácticos, el mecanismo consiste en {mechanism}. Cada parte cumple una función distinta y evita que una herramienta o una métrica reemplace al razonamiento que debería sostenerla. Lo importante es poder explicar por qué esa secuencia resulta adecuada para este problema.",
       f"Puede verse en una situación cotidiana: {example}. La escena comienza simple y gana complejidad cuando aparecen población, tiempo, dependencias y consecuencias. Esa progresión permite aprender sin saltar directamente a una solución total.",
       f"Un contraejemplo marca la frontera de la tesis: {limit}. La misma práctica deja de ser defendible cuando ya no produce evidencia, desplaza daño o impide revisar el compromiso. Nombrar el límite es parte de comprender, no una nota marginal.",
       f"Hotel Horizonte vuelve concreta la distinción: {hotel}. Las voces del caso no ilustran una respuesta predeterminada; muestran cómo una decisión cambia según quién sostiene la promesa, quién opera y quién recibe las consecuencias.",
       f"Para la práctica profesional, esto implica {consequence}. El documento ofrece un paso acumulativo del recorrido, pero conserva abierta la evidencia que podría obligar a corregirlo en el núcleo siguiente."),
      (f"Para pasar de la idea a una decisión hace falta {mechanism}. Así se distinguen descripción, explicación y compromiso, tres movimientos que suelen mezclarse. El resultado es una argumentación que otra persona puede revisar sin tener que aceptar la autoridad de quien la produjo.",
       f"Consideremos un ejemplo de baja escala: {example}. Seguirlo de punta a punta permite reconocer primero el fenómeno simple y luego las relaciones que vuelven insuficiente la explicación inicial. Esa es la progresión de lo general a lo particular que propone la colección.",
       f"La tesis no autoriza cualquier uso. Su contraejemplo es {limit}. Allí se vuelve visible que una técnica correcta puede ser inadecuada para cierto riesgo, población o momento. La calidad depende del uso, no del prestigio de la herramienta.",
       f"Aplicado a Hotel Horizonte, {hotel}. La continuidad del caso permite comparar la nueva lectura con las anteriores y evita inventar una situación distinta para confirmar cada concepto.",
       f"De aquí se desprende una responsabilidad concreta: {consequence}. Profesores y estudiantes pueden discutirla con ejemplos, objeciones y evidencia; no necesitan memorizar una definición aislada ni aceptar una receta cerrada."),
    )
    return list(families[(number-1)%3])

ADDITIONS: dict[int,list[str]]={n:_make_additions(n,s) for n,s in SPECS.items()}

def replace_thesis(text: str, additions: list[str]) -> str:
    pattern = re.compile(r"(^## Tesis\s*\n)(.*?)(?=^## )", re.M | re.S)
    match = pattern.search(text)
    if not match:
        raise RuntimeError("No se encontró la sección Tesis")
    first = re.sub(r"\n{2,}", " ", match.group(2).strip())
    replacement = match.group(1) + "\n\n".join([first, *additions]) + "\n\n"
    return text[:match.start()] + replacement + text[match.end():]

def normalize_thesis_spacing(text:str)->str:
    """Promueve las seis líneas ya aplicadas a párrafos Markdown reales."""
    pattern=re.compile(r"(^## Tesis\s*\n)(.*?)(?=^## )",re.M|re.S)
    match=pattern.search(text)
    if not match: raise RuntimeError("No se encontró la sección Tesis")
    body=match.group(2).strip()
    paragraphs=[p.strip() for p in re.split(r"\n+",body) if p.strip()]
    replacement=match.group(1)+"\n\n".join(paragraphs)+"\n\n"
    return text[:match.start()]+replacement+text[match.end():]

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def current_package_source(number: int) -> Path:
    package_names = {1:"N01-v18-final",2:"N02-v15-final",3:"N03-v10-final",4:"N04-v9-final",5:"N05-v10-final",6:"N06-v10-final",7:"N07-v10-final",8:"N08-v10-final",9:"N09-v10-final",10:"N10-v9-final"}
    package = ROOT / (package_names[number] if number <= 10 else f"N{number:02d}-content-canonical")
    record = json.loads((package / "source-manifest.json").read_text(encoding="utf-8"))
    return package / record["source"]

def master_source(number: int, package_source: Path) -> Path:
    return ROOT / f"N{number:02d}-content-final" / "source" / package_source.name if number <= 10 else package_source

def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--normalize-spacing",action="store_true")
    args=parser.parse_args()
    missing = sorted(set(range(1,37)) - set(ADDITIONS))
    if missing:
        raise RuntimeError(f"Faltan tesis: {missing}")
    report=[]
    for number in range(1,37):
        packaged=current_package_source(number); authoritative=master_source(number,packaged)
        current=authoritative.read_text(encoding="utf-8")
        updated=normalize_thesis_spacing(current) if args.normalize_spacing else replace_thesis(current,ADDITIONS[number])
        authoritative.write_text(updated,encoding="utf-8")
        if packaged != authoritative: shutil.copy2(authoritative,packaged)
        if number >= 11:
            mp=ROOT/f"N{number:02d}-content-canonical"/"source-manifest.json"
            manifest=json.loads(mp.read_text(encoding="utf-8")); manifest["stage"]="content-canonical-thesis-n00-standard"; manifest["source_sha256"]=sha(authoritative)
            mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        thesis=re.search(r"^## Tesis\s*\n(.*?)(?=^## )",updated,re.M|re.S).group(1)
        report.append({"document":f"N{number:02d}","source":str(authoritative.relative_to(ROOT)),"words":len(re.findall(r"\b[\wÁÉÍÓÚÜÑáéíóúüñ'-]+\b",thesis)),"paragraphs":len([p for p in thesis.strip().split("\n") if p.strip()]),"sha256":sha(authoritative)})
    out=ROOT/"editorial-standard"/"thesis-n00-standard-application.json"
    out.write_text(json.dumps({"status":"PASS","documents":report},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","documents":len(report)},ensure_ascii=False))

if __name__ == "__main__": main()
