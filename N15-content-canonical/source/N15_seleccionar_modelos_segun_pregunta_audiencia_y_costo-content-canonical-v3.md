# N15 · Seleccionar modelos según pregunta, audiencia y costo

## Pregunta profesional

¿Qué modelo conviene construir para responder una pregunta concreta sin agregar detalle, confusión o mantenimiento que la decisión no necesita?

## Seis diagramas correctos y ninguna respuesta

Una universidad debe decidir si puede abrir la inscripción a exámenes durante una semana de alta demanda. El equipo técnico prepara seis diagramas. Uno muestra servidores y bases. Otro enumera servicios. Un tercero contiene clases y relaciones. Un cuarto representa el flujo de inscripción. El quinto describe estados de una solicitud. El último exhibe un mapa de capacidades institucionales.

Cada diagrama es prolijo y, dentro de su notación, correcto. Dirección pregunta si una caída del sistema puede producir inscripciones dobles, qué estudiantes quedarían afectados y quién puede suspender el proceso. La reunión dedica veinte minutos a explicar símbolos. Nadie puede responder con el conjunto presentado.

El problema no es que falte un diagrama “completo”. Las preguntas mezclan estructura, transición, proceso, riesgo, actores y autoridad. Cada modelo recorta algunas relaciones y deja otras fuera. El equipo construyó representaciones desde herramientas disponibles, no desde decisiones pendientes.

Una desarrolladora propone agregar todas las piezas al diagrama de arquitectura. Incorpora estudiantes, reglas, colas, estados, bases, áreas, riesgos y responsables. El resultado ocupa una pared. Cuanto más completo parece, menos se puede leer. Las líneas cruzan niveles de abstracción; una caja puede significar aplicación, oficina o función. La totalidad visual produce una ilusión de comprensión.

El equipo reinicia con tres preguntas. Para conocer si dos comandos pueden comprometer la misma vacante, utiliza una transición de estado con invariante y concurrencia. Para ver qué grupos encuentran barreras antes de enviar el comando, construye un mapa de experiencia y actores. Para decidir quién suspende, representa autoridad, umbral y escalamiento. La arquitectura técnica queda como apoyo para localizar componentes afectados.

Los cuatro modelos no cuentan historias idénticas. La vista de experiencia comienza antes que el sistema. La transición termina al aceptar o rechazar. La arquitectura muestra componentes persistentes. La autoridad atraviesa áreas. La diferencia no es defecto: cada vista responde una pregunta.

El equipo agrega a cada modelo propósito, audiencia, alcance, fecha, fuentes, supuestos y decisión. También registra costo de mantenerlo. El diagrama de componentes puede generarse desde código y actualizarse con frecuencia. El mapa de autoridad necesita revisión cuando cambia una norma. El recorrido de experiencia requiere nueva evidencia si se modifica el canal.

La solución no consiste en producir modelos para cada aspecto. Se selecciona un conjunto mínimo capaz de responder preguntas y descubrir contradicciones. Si una representación no cambia una decisión, comunica algo necesario ni reduce riesgo, no se construye. Si dos vistas repiten lo mismo para la misma audiencia, se combinan o una se elimina.

La discusión revela además una asimetría. Quienes diseñaron los diagramas conocen el contexto y completan mentalmente relaciones ausentes. Dirección sólo recibe el artefacto. Cuando pregunta por una flecha, el autor agrega una explicación oral que nunca quedará disponible para la siguiente persona. El costo de interpretación estaba escondido en la reunión.

El equipo incorpora una prueba sin autor presente. Entrega cada vista con una pregunta y un escenario. Registra qué entiende la audiencia, qué confunde y qué no puede decidir. Algunas láminas técnicamente correctas fallan porque mezclan tiempo actual y futuro. Otras mejoran con una etiqueta, no con más detalle.

Durante la prueba, dirección comprende por qué disponibilidad técnica y capacidad institucional no son equivalentes. El área académica detecta que el criterio de suspensión no tiene autoridad suplente. Desarrollo localiza dónde implementar control de versión. El modelo funciona porque permite actuar y porque sus límites permanecen visibles.

Esta lectura estudia la selección de modelos. Modelar es simplificar con propósito. La calidad no depende de cantidad de elementos ni prestigio de la notación, sino de la relación entre pregunta, audiencia, evidencia, decisión, costo y vigencia.

## Hotel Horizonte: el mapa que cada área quería convertir en el único

HH-14 reconstruyó doce llegadas completas y mostró que los cuatro minutos informados para el mostrador ocultaban una espera promedio de veintisiete. Al revisar ese hallazgo, Ricardo Sosa quiere ampliar el mapa de proceso hasta incluir todas las tareas de Operaciones. Federico Müller propone reemplazarlo por una arquitectura que ubique PMS, integrador y cerraduras. Camila Duarte pide un recorrido de experiencia que conserve la promesa comunicada. Elena Acosta solicita un tablero para decidir si autoriza el piloto de validación previa.

Lucía Ferreyra objeta que ninguna de esas vistas, por sí sola, muestra cuándo puede asignar una habitación, qué autoridad tiene ante una excepción ni qué recibe el huésped mientras espera. Mariela Benítez agrega los registros de inspección y las diferencias entre habitación preparada y habitación efectivamente entregable. El desacuerdo ya no es sobre estética. Cada rol necesita decidir algo distinto con evidencia que los otros modelos recortan.

El mapa de proceso muestra colas y handoffs, pero no explica componentes ni datos. La arquitectura localiza integraciones y contratos, pero no muestra la espera del huésped. El recorrido de experiencia conserva la perspectiva del huésped y puede ocultar reglas operativas. El tablero resume resultados y no reconstruye mecanismos. Los episodios de HH-14, los eventos del PMS, los mensajes entre Recepción y Housekeeping, las vigencias de cerradura y las reglas comerciales forman la base común para contrastarlos.

HH-15 no elegirá un ganador universal. Construirá una cartera mínima vinculada por reserva, habitación, huésped, promesa, asignación y excepción. Cada vista tendrá pregunta, audiencia, decisión, alcance, evidencia, costo y fecha de revisión. La decisión concreta es si la validación previa puede probarse como opción asistida sin bloquear a quien no use el canal digital ni anticipar una confirmación que Recepción todavía no pueda sostener.

El equipo formula un criterio de salida. La cartera estará lista cuando Elena pueda decidir el piloto, Federico localizar impactos, Lucía y Mariela reconstruir excepciones y Camila explicar límites de la promesa. No necesita representar nómina, compras ni cada tabla del PMS. Después del piloto, o ante un cambio de regla, canal o proveedor, se revisarán las vistas afectadas y la decisión. El propósito protege la frontera contra la expansión permanente y conserva revisabilidad.

## Tesis

Un modelo selecciona una parte de la realidad para responder una pregunta y ayudar a tomar una decisión. Su valor depende tanto de lo que muestra como de lo que deja afuera. Más detalle no siempre mejora el modelo. Puede mezclar niveles, dificultar la lectura y exigir mantenimiento sin mejorar la decisión. La selección debe considerar objeto, relaciones, dinámica, audiencia, evidencia, notación, costo y vigencia. Diferentes modelos pueden ser simultáneamente válidos porque responden preguntas distintas. La coherencia no exige identidad, sino conceptos y límites compatibles. Una cartera mínima supera al modelo total. Combina sólo las vistas necesarias, conserva trazabilidad y declara contradicciones. La notación sirve al razonamiento; no lo reemplaza.

Para pasar de la idea a una decisión hace falta seleccionar qué aspecto representar según pregunta, audiencia, costo de mantenimiento y aquello que el modelo deja deliberadamente afuera. Así se distinguen descripción, explicación y compromiso, tres movimientos que suelen mezclarse. El resultado es una argumentación que otra persona puede revisar sin tener que aceptar la autoridad de quien la produjo.

Consideremos un ejemplo de baja escala: experiencia muestra barreras, BPMN eventos y responsabilidades, C4 relaciones de software; superponerlos no produce automáticamente una mejor explicación. Seguirlo de punta a punta permite reconocer primero el fenómeno simple y luego las relaciones que vuelven insuficiente la explicación inicial. Esa es la progresión de lo general a lo particular que propone la colección.

La tesis no autoriza cualquier uso. Su contraejemplo es usar UML, BPMN o una plantilla porque es estándar, aunque su precisión no sirva a la conversación o decisión presente. Allí se vuelve visible que una técnica correcta puede ser inadecuada para cierto riesgo, población o momento. La calidad depende del uso, no del prestigio de la herramienta.

Aplicado a Hotel Horizonte, Lucía sigue el episodio, Federico los contratos y Elena autoridad y riesgo; los modelos comparten objetos pero no escala. La continuidad del caso permite comparar la nueva lectura con las anteriores y evita inventar una situación distinta para confirmar cada concepto.

De aquí se desprende una responsabilidad concreta: justificar utilidad y límite de cada representación; N16 gobernará versiones, vínculos y contradicciones durante el ciclo de vida. Profesores y estudiantes pueden discutirla con ejemplos, objeciones y evidencia; no necesitan memorizar una definición aislada ni aceptar una receta cerrada.

## De N14 a N15: del proceso real a la representación adecuada

N14 utilizó un mapa de proceso porque necesitaba secuencia, handoffs, colas y excepciones. HH-14 dejó además preguntas sobre arquitectura, datos, estados, actores y decisiones que el proceso no representa con precisión.

N15 convierte esa limitación en criterio. No vuelve a reconstruir el flujo ni compara todavía coherencia entre ciclos de vida, tarea de N16. Selecciona qué modelos vale la pena construir y cómo justificar el costo de cada uno.

El producto será HH-15, cartera mínima de modelos. Recibe preguntas abiertas de HH-14 y asigna a cada una una representación, audiencia, decisión, evidencia, nivel, costo, vigencia y relación con otras vistas.

## Movimiento 1 · Comenzar por la pregunta, no por la notación

### Modelo: simplificación deliberada

Un modelo conserva ciertas propiedades de un objeto para comprender, comunicar, predecir o decidir. George Box recordó que los modelos son incorrectos como reproducciones completas y útiles cuando su simplificación sirve. La frase no autoriza arbitrariedad: obliga a explicar para qué es útil y dónde deja de serlo.

Un mapa de subte omite distancias y edificios para mostrar conexiones. Resulta excelente para elegir combinación y malo para calcular una caminata. Agregar calles puede empeorar su función principal.

En sistemas, una entidad relación selecciona estructura de datos; una máquina de estados, transiciones; un modelo causal, mecanismos; un proceso, secuencia y responsabilidad. Llamarlos “modelos del sistema” no los vuelve intercambiables.

La evidencia de utilidad es una decisión mejor, una contradicción descubierta o una comunicación comprobable. La belleza visual puede ayudar a leer y no sustituye ese resultado.

La prueba negativa también importa. Si retirar una relación no cambia ninguna conclusión, quizá no era necesaria. Si un caso límite exige una pieza ausente, el recorte fue excesivo. El modelo se calibra por sensibilidad a diferencias relevantes.

### Pregunta, decisión y carga de prueba

La pregunta determina qué relaciones deben ser visibles. “¿Dónde espera el huésped?” requiere tiempo y recorrido. “¿Qué componente puede duplicar una asignación?” requiere frontera técnica y transición. “¿Quién absorbe el daño?” requiere actores, poder y reparación.

La decisión define suficiente detalle. Para elegir entre dos canales puede bastar un flujo comparado. Para autorizar acceso se necesitan reglas, estados y autoridad. Modelar sin decisión conduce a acumular información por precaución.

La carga de prueba también cambia. Un modelo exploratorio puede contener hipótesis marcadas. Un modelo usado para comprometer presupuesto necesita procedencia, supuestos y revisión. HH-11 aporta fuerza de evidencia; N15 la vincula con el uso del modelo.

Una buena consigna completa tres frases: necesitamos decidir, necesitamos ver y podemos ignorar por ahora. La tercera protege el recorte.

La pregunta debe poder refutarse o cerrarse provisionalmente. “Modelar el sistema” no tiene condición de suficiencia. “Determinar si la validación previa puede excluir una doble asignación” permite reconocer qué evidencia y representación alcanzan.

### Partes interesadas, preocupaciones y puntos de vista

ISO/IEC/IEEE 42010:2022 distingue arquitectura de descripción de arquitectura y organiza partes interesadas, preocupaciones, puntos de vista y vistas. En la terminología del estándar, un *viewpoint* especifica convenciones para construir una vista que responde a preocupaciones de ciertas audiencias.

La contribución es metodológica: no existe una vista neutral para todos. Seguridad necesita límites de confianza. Operaciones, dependencias y recuperación. Dirección, capacidades y riesgos. Desarrollo, estructura suficiente para cambiar.

La audiencia no determina verdad por jerarquía. Una vista ejecutiva no debe ocultar incertidumbre para parecer simple. Una vista técnica no debe usar detalle para excluir. Se adapta lenguaje y densidad, no la evidencia central.

La prueba consiste en pedir a la audiencia que explique qué decisión tomaría. Si sólo puede repetir cajas, la vista no cumplió.

También se registran preocupaciones en tensión. Seguridad puede pedir más control; experiencia, menos fricción; operación, reparación rápida. Una vista puede mostrar el conflicto sin resolverlo. Ocultarlo para alcanzar consenso produce una descripción políticamente cómoda y metodológicamente débil.

### Alcance, nivel y resolución

Alcance define qué sistema, período y frontera entra. Nivel define tipo de elemento: organización, capacidad, sistema, contenedor, componente o código. Resolución define cuánto detalle se muestra dentro de ese nivel.

Mezclar niveles crea relaciones ambiguas. Una flecha entre “Recepción” y “API” puede significar uso, responsabilidad, mensaje o dependencia. Separar vistas o etiquetar relaciones resta espectacularidad y agrega significado.

El modelo C4 de Simon Brown propone niveles jerárquicos de contexto, contenedores, componentes y código. Su sitio oficial aclara que no todos son necesarios y que contexto y contenedores suelen alcanzar. Esa selectividad coincide con N15.

Acercar el zoom no corrige una frontera equivocada. Un diagrama de código perfecto no explica una promesa comercial. Primero se elige pregunta; luego nivel.

La resolución puede variar dentro de una cartera, no dentro de cada símbolo. Un contexto general enlaza una vista detallada de la zona crítica. Esa navegación conserva orientación y evita que toda página cargue el máximo detalle disponible.

### Tiempo y versión del modelo

Un modelo puede describir situación actual, historia, escenario futuro o transición. Mezclarlos sin marca produce contradicción aparente. “El PMS envía a la cerradura” puede ser vigente, propuesto o deseado.

Toda vista necesita fecha o evento de validez, fuente y responsable. Un modelo sin vigencia se convierte en documento ceremonial. La actualización puede ser automática, periódica o disparada por cambio.

La frecuencia depende de volatilidad y consecuencia. Arquitectura generada desde código puede renovarse en cada despliegue. Autoridad normativa cambia menos, pero exige revisión formal. Un recorrido de experiencia requiere nueva investigación cuando cambia la experiencia.

El costo de desactualización se compara con el de mantener. Si nadie puede sostener una vista detallada, conviene reducirla o generarla.

La versión debe vincularse con la decisión que utilizó el modelo. Corregir una vista después no reescribe lo que el equipo sabía. La trazabilidad conserva por qué una decisión anterior era defendible y qué evidencia posterior obliga a revisarla.

### Notación y semántica

Una notación define elementos, relaciones y reglas de lectura. UML 2.5.1 ofrece múltiples diagramas; BPMN 2.0.2, semántica para procesos. ArchiMate 3.2 relaciona capas y aspectos de arquitectura empresarial. Ninguna es mejor en abstracto.

Daniel Moody propone principios para evaluar notaciones visuales, como discriminación perceptual, transparencia semántica, complejidad y manejo de diferencias cognitivas. Una notación puede ser formal y difícil para la audiencia.

Las cajas y flechas libres permiten velocidad y crean ambigüedad si no tienen leyenda. Una notación rigurosa puede exceder la decisión. El criterio combina precisión necesaria y costo de comprensión.

La relación debe etiquetarse con verbo. “PMS informa disponibilidad a Comercial” explica más que una flecha. Formas y colores sólo se usan si conservan significado estable.

La notación también debe ser accesible. Depender sólo del color, utilizar íconos sin texto o saturar cruces excluye lectores y favorece interpretaciones. Una explicación textual y un orden de lectura permiten reconstruir el argumento fuera del dibujo.

## Primera aplicación de HH-15: separar cuatro preguntas del ingreso

Ricardo Sosa, Federico Müller, Camila Duarte y Lucía Ferreyra separan cuatro decisiones que la reunión había mezclado. Reducir espera requiere flujo end-to-end. Evitar doble asignación requiere estados e invariantes. Evaluar dependencia del integrador requiere arquitectura y contratos. Reparar promesas requiere actores y autoridad.

El equipo construye cuatro vistas pequeñas vinculadas por identificadores y por los episodios observados en HH-14. El proceso no incluye tablas. La arquitectura no intenta narrar toda la experiencia. La matriz de autoridad no duplica cada mensaje. Cada una declara alcance.

Al compararlas, Mariela Benítez señala una ausencia: ninguna representa qué evidencia recibe el huésped mientras inspección, asignación y acceso todavía no coinciden. Se agrega una vista de experiencia acotada, no un recorrido total.

La cartera aumenta a cinco modelos porque una pregunta lo exige. El límite sigue siendo utilidad, no un número prefijado.

El equipo registra además una correspondencia entre vistas. “Habitación asignable” en proceso debe referir al estado definido en HH-12. Si una vista usa “disponible” con otro sentido, lo declara. La selección prepara coherencia sin forzar identidad visual.

Antes de aceptar la quinta vista, el equipo intenta resolver la ausencia mediante una anotación en el proceso. La prueba con huéspedes muestra que no alcanza: la pregunta trata percepción, acceso y reparación. El nuevo modelo no aparece por preferencia de Diseño, sino por evidencia de una decisión no cubierta.

### Modelo del problema antes que modelo de la solución

Michael Jackson propone problem frames para separar fenómenos del mundo, requisitos y máquina. La distinción impide que la estructura de la solución capture demasiado pronto la pregunta. Un modelo de aplicaciones existentes puede hacer parecer inevitable conservarlas.

Antes de diseñar, se representa el dominio y la discrepancia: dos promesas sobre una vacante, una regla sin autoridad suplente o una persona bloqueada antes del formulario. Luego se agregan componentes necesarios. La dirección del razonamiento va del problema a la solución, aunque la evidencia técnica informe restricciones.

El modelo del problema no es neutral. También selecciona frontera y lenguaje. Se contrasta con actores y episodios. Su utilidad aparece cuando permite comparar alternativas que una arquitectura actual ocultaba.

La condición de borde es el cambio técnico acotado. Si la pregunta consiste en localizar un error dentro de una función, un modelo de código puede ser suficiente. La regla no prohíbe comenzar cerca de la solución; exige justificarlo.

## Movimiento 2 · Elegir una familia de modelo y un costo defendible

### Modelos de estructura

Los modelos de estructura muestran elementos relativamente persistentes y relaciones: datos, componentes, capacidades, organización o despliegue. Responden qué existe, cómo se compone y de qué depende.

Una entidad relación ayuda a decidir integridad y correspondencia. C4 comunica estructura de software a distintos niveles. ArchiMate conecta negocio, aplicaciones y tecnología. El Business Architecture Core Metamodel de OMG, publicado en 2024, ofrece conceptos para arquitectura de negocio.

La frontera es crucial. Un inventario de aplicaciones no es arquitectura si no muestra relaciones relevantes. Un organigrama no es modelo de autoridad si confunde cargo con decisión.

La evidencia suele provenir de repositorios, configuraciones, entrevistas y normas. La actualización automática reduce deriva técnica y no valida significado de negocio.

Marc Lankhorst vincula arquitectura empresarial con partes interesadas y coherencia entre dominios. Esa amplitud ayuda cuando una decisión cruza capacidades y tecnología. También puede exceder un problema local. El modelo estructural debe declarar si representa dependencia, composición, propiedad, uso o flujo; una línea genérica impide decidir impacto.

### Modelos de comportamiento y tiempo

Máquinas de estados, secuencias, procesos y simulaciones muestran cambio. Responden qué ocurre, en qué orden, bajo qué condición y con qué demora.

Un modelo de estados protege transiciones de una entidad. Un BPMN representa coordinación. Un diagrama de secuencia localiza intercambios. Una simulación explora capacidad y variabilidad. Elegir uno depende de la pregunta.

No se debe forzar comportamiento dentro de una estructura estática mediante flechas ambiguas. Tampoco llenar un proceso con cada mensaje técnico. Se vinculan vistas cuando el detalle cambia audiencia.

La evidencia necesita episodios y tiempos. El camino normativo puede coexistir con el observado si se distinguen.

Los modelos de comportamiento deben tratar alternativas y excepciones. Una secuencia única parece predecir lo que apenas prescribe. Una simulación agrega supuestos sobre llegadas y capacidad; si no se documentan, produce precisión aparente. La prueba compara el comportamiento modelado con casos ordinarios y adversos.

El tiempo puede representarse como orden, duración, demora o frecuencia. Un diagrama de secuencia muestra intercambios y no necesariamente espera de personas. Una simulación puede estimar distribución y no explicar autoridad. La decisión define qué dimensión temporal se necesita.

### Modelos de decisión y causalidad

Una tabla de decisión representa combinaciones de condiciones y resultados. Un árbol muestra ramificación. Un modelo causal expresa mecanismos, retroalimentación y demoras. Un argumento vincula afirmación, evidencia y rivales.

John Sterman muestra que los modelos de dinámica de sistemas permiten explorar cómo estructura y retroalimentación generan comportamiento. Peter Checkland utiliza modelos conceptuales en Soft Systems Methodology como dispositivos para aprender sobre situaciones, no como copias de la realidad.

Donald Schön y Peter Senge permiten tratar la representación como apoyo para reflexión y aprendizaje organizacional. Martin Fowler y Grady Booch muestran que una notación o una vista sólo vale por las preguntas y responsabilidades que vuelve manejables. Thomas Davenport agrega que información, proceso y cambio organizacional deben evaluarse juntos. Estos aportes refuerzan el criterio de N15: seleccionar una cartera mínima de modelos, no premiar la exhaustividad gráfica.

Estas familias responden por qué y qué pasaría si, preguntas que un flujo puede no resolver. Su riesgo es convertir hipótesis en causalidad establecida. Cada relación declara evidencia y alternativa.

La selección depende de reversibilidad. Para explorar puede bastar un modelo cualitativo. Para automatizar una decisión se exige formalización, prueba y autoridad.

Un lazo causal no demuestra magnitud ni demora. Una tabla de decisión no explica cómo cambian sus entradas. Combinar vistas puede ser necesario, pero cada vínculo conserva estatus: evidencia, hipótesis o regla. La representación se debilita cuando transforma asociación observada en mecanismo.

### Modelos de experiencia y perspectiva

Journey, blueprint de servicio, mapa de actores y escenario conservan lo que vive una persona y cómo se relaciona con trabajo interno. Responden dónde aparece fricción, información, emoción, exclusión o reparación. Stickdorn, Hormess, Lawrence y Schneider organizan esta relación mediante recorridos y blueprints de servicio que conectan la experiencia visible con la operación que la sostiene.

No reemplazan proceso ni arquitectura. Una línea emocional no prueba causa. Una persona ficticia no sustituye evidencia. Su valor consiste en mantener la promesa y las perspectivas que los modelos técnicos excluyen.

La evidencia proviene de observación, entrevistas, accesibilidad y episodios. N05 y N09 aportan criterios de poder y participación. La audiencia incluye diseño, producto, operaciones y actores afectados.

El límite se alcanza cuando el modelo estetiza experiencia o habla en nombre de quien no participó.

Una foto de persona o una curva emocional no agrega evidencia por sí misma. Se necesita episodio, cita autorizada, patrón o condición. El modelo puede declarar “perspectiva no relevada” en lugar de inventar una voz. Esa ausencia es información para decidir investigación.

La representación debe separar experiencia observada de interpretación del equipo. “Esperó cuarenta minutos” es evidencia temporal; “se sintió abandonada” requiere relato o inferencia marcada. La precisión protege la voz en lugar de volverla decorativa.

### Elegir entre recorrido, prototipo, blueprint y modelo formal

Un journey map sigue la experiencia de una persona o población a través de etapas y puntos de contacto. Resulta adecuado cuando la decisión depende de expectativa, esfuerzo, información, emoción, barrera o reparación a lo largo del tiempo. No explica por sí solo las causas internas. En Hotel Horizonte permite mostrar que la llegada comienza con la promesa comercial y no en el mostrador, pero necesita vincularse con evidencia operacional para no atribuir cada dificultad a la interfaz visible.

Un prototipo vuelve experimentable una alternativa antes de construirla por completo. Puede ser una conversación simulada, una secuencia en papel, una interfaz interactiva o un ensayo de servicio. Conviene cuando existe incertidumbre sobre comprensión, acción o coordinación futura. Su fidelidad se decide por la pregunta. Una pantalla detallada no ayuda si todavía se discute quién puede autorizar una excepción; una simulación con roles puede revelar esa relación con menor costo.

Un blueprint de servicio conecta acciones de la persona con puntos de contacto, trabajo visible, trabajo interno y procesos de apoyo. Se elige cuando el resultado depende de varias capas y la decisión necesita localizar un handoff, una espera o una función invisible. No reemplaza un modelo formal de estados ni un contrato técnico. Su fuerza reside en mantener unida la experiencia con el sistema de trabajo que la produce.

BPMN corresponde cuando la pregunta exige representar coordinación mediante eventos, actividades, decisiones, participantes, mensajes y excepciones con una semántica compartida. Permite distinguir el flujo interno de un participante y los mensajes entre participantes. En HH-15 puede modelar qué ocurre cuando una llegada anticipada encuentra una habitación no disponible y qué compensación sigue a una asignación ya comunicada. No es la mejor opción para mostrar arquitectura de componentes, distribución emocional, causalidad acumulativa o reglas combinatorias extensas.

El modelo de estados conviene cuando importa proteger el ciclo de vida de una entidad y sus transiciones válidas. Una tabla de decisiones resulta mejor cuando muchas condiciones producen resultados discretos. Un diagrama de secuencia sirve para ordenar intercambios técnicos. Un modelo causal ayuda a explorar retroalimentaciones. La elección no premia la notación más formal. Selecciona la semántica mínima que vuelve examinable la decisión sin ocultar relaciones relevantes.

Scolari permite agregar otro criterio. La interfaz no es sólo una superficie, sino una red de relaciones entre actores y tecnologías. Un journey, un blueprint o un prototipo también actúan como interfaces de conocimiento: habilitan algunas lecturas, ocultan otras y organizan quién puede discutir. Elegir un modelo implica diseñar esa relación. Una vista ejecutiva que elimina toda excepción puede facilitar lectura y, al mismo tiempo, impedir que Operaciones objete una promesa imposible.

La selección se comprueba retirando una vista. Si sin journey desaparece la experiencia previa al mostrador, esa representación cubre una función propia. Si sin blueprint nadie localiza el trabajo de Housekeeping, su aporte es distinto. Si sin BPMN la organización no puede acordar eventos y rutas de excepción, el modelo formal agrega semántica necesaria. Si dos vistas permiten tomar exactamente la misma decisión con la misma evidencia, se conserva la de menor costo total de construcción, lectura y mantenimiento.

El límite aparece cuando se exige a una representación responder todo. Agregar emociones a un BPMN, componentes a un journey y responsabilidades a cada pantalla produce una lámina exhaustiva e ilegible. N15 conserva un conjunto pequeño de vistas vinculadas por episodios, estados e identificadores. La coherencia proviene de esas correspondencias y no de superponer todos los lenguajes en un único dibujo.

### Audiencia y traducción entre vistas

Una misma pregunta puede requerir distintas vistas por audiencia. Dirección necesita riesgo y decisión; desarrollo, interfaces y reglas; operación, excepciones y señales. La traducción debe conservar conceptos y cambiar resolución.

Crear una copia manual para cada audiencia aumenta inconsistencia. Conviene mantener un modelo base cuando existe semántica común y derivar vistas. No todo puede centralizarse: relatos y normas tienen fuentes distintas.

La traducción se prueba con escenarios. Cada audiencia localiza la misma reserva, transición o excepción. Si los nombres cambian sin correspondencia, la cartera fragmenta comprensión.

La simplificación debe declarar lo omitido. “Vista ejecutiva” no autoriza esconder dependencia crítica.

La traducción incluye orden de preguntas. Una persona directiva puede comenzar por consecuencia y abrir evidencia; desarrollo, por componente y contrato. Dos recorridos pueden usar la misma base sin repetir documentos. Diseñar navegación forma parte de la comunicación del modelo.

La traducción también puede revelar desacuerdo. Si Tecnología llama “éxito” a la recepción del comando y Comercial a la confirmación del huésped, no se corrige sólo con vocabulario. Se revisan evento, alcance y consecuencia. La cartera funciona como lugar de negociación semántica.

### Costo total de un modelo

El costo incluye investigar, construir, explicar, validar, mantener, gobernar y retirar. También incluye decisiones equivocadas por ambigüedad o desactualización.

Un diagrama generado puede ser barato de actualizar y caro de comprender. Un taller participativo puede ser costoso y revelar una frontera decisiva. La comparación utiliza consecuencia evitada, frecuencia de uso y vida esperada.

La deuda de modelo aparece cuando una representación continúa circulando sin responsable ni fecha. Puede ser peor que no tenerla porque ofrece confianza falsa. Se necesita política de revisión y retiro.

El modelo mínimo no es el más pequeño. Es el menor conjunto que responde la pregunta con evidencia y permite descubrir límites relevantes.

El costo de oportunidad cuenta. Mantener una vista que nadie utiliza desplaza observación, pruebas o reparación. La revisión pregunta frecuencia de consulta y decisiones efectivamente influenciadas. Un modelo puede conservar valor histórico y salir de la cartera operativa.

También existe costo de dependencia de herramienta. Un formato propietario puede dificultar revisión, versión y acceso. La elección considera exportación, búsqueda, accesibilidad y capacidad de reconstrucción, no sólo facilidad inicial de dibujo.

### Inteligencia artificial como productora de representaciones

En 2026, herramientas de inteligencia artificial pueden inferir diagramas desde código, registros o texto y traducir entre notaciones. Reducen costo de producción y pueden multiplicar modelos sin propósito.

Una representación generada hereda sesgos y ausencias de la fuente. Desde código omitirá trabajo manual. Desde entrevistas puede inventar continuidad. Desde registros puede confundir frecuencia con importancia.

La persona responsable debe verificar elementos, relaciones, nivel, fecha y evidencia. También debe decidir si el modelo merecía existir. La velocidad no elimina costo de revisión ni mantenimiento.

La IA resulta valiosa para explorar variantes, detectar inconsistencias de nombres y generar vistas desde un modelo estructurado. No adquiere autoridad para declarar la arquitectura real.

La verificación no puede consistir en preguntar al mismo modelo si su salida es correcta. Se contrasta con fuentes y personas responsables. Cuando la herramienta resume una norma o infiere una relación, el artefacto conserva referencia y nivel de confianza. La rapidez permite iterar; no reduce la carga de prueba del uso.

## Segunda aplicación de HH-15: reducir una cartera que creció sin control

Elena Acosta solicita revisar los diecisiete diagramas que circulan en Hotel Horizonte antes de usarlos para decidir el piloto. Cinco son copias de arquitectura con nombres distintos. Tres procesos describen versiones pasadas. Dos journeys no tienen fuentes. El resto responde preguntas vigentes.

Federico Müller registra fuente y vigencia técnica; Ricardo Sosa y Mariela Benítez verifican el proceso observado; Lucía Ferreyra y Camila Duarte contrastan autoridad, excepción y promesa. El equipo retira seis, combina cuatro, actualiza tres y conserva cuatro. Agrega vínculos entre reserva, habitación, asignación y excepción.

La reducción no pierde conocimiento porque conserva historial y motivo. Disminuye contradicciones accidentales y libera esfuerzo para validar las vistas que sí influyen.

Una vista retirada puede reabrirse si vuelve la pregunta. El retiro no borra procedencia.

El proceso detecta una dependencia cultural: cada equipo conserva “su” mapa como territorio. La cartera cambia propiedad simbólica por responsabilidad sobre la evidencia. Las áreas siguen aportando conocimiento, pero ninguna vista adquiere verdad por pertenencia. Una revisión conjunta resuelve nombres y retira duplicados.

Los tres modelos actualizados reciben fecha y caso de prueba. Si no pasan, no vuelven al circuito decisional. Esta regla evita que corregir metadatos se confunda con recuperar utilidad. La cartera deja de medir cantidad y comienza a medir cobertura confiable.

### Criterio de descarte y suficiencia

Antes de construir, se aplican cinco filtros. La pregunta debe estar abierta. La decisión debe tener consecuencia. La representación debe mejorar algo frente a texto, consulta o prueba directa. Debe existir evidencia accesible. El costo debe ser proporcional a uso y riesgo.

Después de construir se aplica descarte. Si la audiencia no puede leer, si no cambia la decisión, si duplica otra vista, si no puede mantenerse o si su incertidumbre excede el uso, se corrige o retira. Un modelo no se conserva para justificar el trabajo invertido.

La suficiencia es provisional. Una vista puede alcanzar para explorar y no para autorizar. Se etiqueta su nivel de compromiso. Esto evita que un boceto de taller circule meses después como arquitectura aprobada.

La evidencia de descarte se registra brevemente. “Sin uso” es menos útil que “la consulta automatizada responde la misma pregunta con fuente vigente”. El historial ayuda a no recrear modelos por olvido.

## Movimiento 3 · Construir una cartera mínima y probar su utilidad

## Instrumento HH-15: ficha de selección de modelo

Cada modelo se justifica mediante diez decisiones:

1. **Pregunta:** qué necesita comprenderse.
2. **Decisión:** qué acción o compromiso puede cambiar.
3. **Audiencia:** quién debe leer, discutir o mantener.
4. **Objeto y alcance:** qué entra, qué queda fuera y en qué período.
5. **Relaciones necesarias:** estructura, secuencia, causalidad, autoridad o experiencia.
6. **Familia y notación:** qué representación ofrece semántica suficiente.
7. **Evidencia:** qué fuentes sostienen elementos y vínculos.
8. **Resolución:** qué nivel y detalle evita mezcla o saturación.
9. **Costo y vigencia:** cómo se construye, mantiene y retira.
10. **Prueba de utilidad:** qué escenario o decisión demostrará que funciona.

La ficha puede concluir “no construir”. Esa es una decisión válida si una pregunta ya está respondida o el costo excede consecuencia.

También puede concluir “construir para una sola decisión”. No toda vista necesita vida permanente. Un modelo efímero de taller puede cumplir, conservarse como evidencia y retirarse del conjunto operativo. La temporalidad reduce deuda sin despreciar aprendizaje.

### Matriz pregunta modelo

Se listan preguntas en filas y modelos candidatos en columnas. Cada cruce indica cobertura fuerte, parcial o nula, costo y audiencia. La matriz evita elegir por costumbre.

Una pregunta puede requerir modelos complementarios. Cuando necesita muchas vistas, se revisan alcance, decisiones mezcladas y costo de comprensión; la cantidad no demuestra por sí sola que esté mal formulada. Una vista que cubre todo parcialmente puede no cubrir nada con suficiente precisión.

La comparación incorpora alternativas no visuales: consulta, tabla, prototipo, relato o prueba. No toda pregunta necesita diagrama.

La matriz se revisa al cambiar decisión. Un modelo útil para diagnosticar puede no servir para operar.

Se agrega una columna de riesgo de omisión. Un modelo barato que cubre parcialmente una pregunta crítica puede ser peor que una investigación costosa. Otra columna registra dependencia de fuente, para no elegir una vista que no podrá actualizarse.

La matriz no produce un puntaje automático. Las coberturas requieren argumento. Una suma podría premiar una vista amplia y superficial. El equipo conserva comparación cualitativa y explicita el criterio que inclina la decisión.

### Matriz aplicada a la validación previa

Hotel Horizonte completa la matriz con preguntas suficientemente distintas para no esconder una decisión compuesta. La primera pregunta es dónde se forma la espera total. Su audiencia principal reúne Operaciones y Recepción, usa episodios observados y requiere un modelo de proceso. La segunda pregunta es qué transición puede producir doble asignación. Tecnología y Recepción necesitan una máquina de estados vinculada con eventos del PMS.

La tercera pregunta es qué dependencia impide emitir acceso. Tecnología y proveedor necesitan arquitectura y contratos. La cuarta pregunta es quién puede detener, autorizar o reparar una promesa. Operaciones y Comercial necesitan una matriz de autoridad. La quinta pregunta es qué información recibe el huésped durante la espera. Comercial, Recepción y personas afectadas necesitan una vista acotada de experiencia.

Cada fila incluye una alternativa no gráfica. Para observar espera se comparan proceso, tabla de tiempos y relato de episodio. La tabla calcula duración con menor costo, pero no muestra handoffs ni responsabilidad. El relato conserva experiencia y dificulta comparar doce casos. El proceso resulta preferible porque la decisión necesita secuencia y permite enlazar los registros.

Para examinar doble asignación, una consulta a la base puede probar frecuencia y no explicar qué transiciones deberían rechazarse. La máquina de estados agrega esa semántica y justifica su mantenimiento.

La columna de omisión cambia la elección. Un diagrama de arquitectura podría mostrar que PMS y cerraduras están conectados, pero omitir la autoridad comercial que convierte un estado en promesa. Una vista de experiencia podría mostrar frustración sin localizar el contrato que debe repararse. La matriz no intenta que cada modelo responda todo. Registra qué consecuencia quedaría invisible si una vista fuera la única fuente para decidir.

El costo se estima por construcción, lectura y actualización. La matriz de autoridad parece barata porque contiene pocas filas, pero exige validación formal y revisión cuando rota un rol. La arquitectura puede generarse parcialmente desde configuración y todavía requiere verificar significado. La vista de experiencia necesita observación nueva si cambia el canal. El modelo de proceso reutiliza HH-14 y su costo incremental es menor que reconstruirlo. Esta comparación evita confundir una lámina breve con una representación barata.

La prueba final retira de manera simulada cada vista. Sin estados, el equipo no puede demostrar que la última unidad quede protegida. Sin autoridad, reconoce el conflicto y no sabe quién puede resolverlo. Sin experiencia, el piloto parece exitoso aunque quien no use el canal digital quede bloqueado. Sin arquitectura, la recomendación no localiza dependencia de proveedor. Sin proceso, las mejoras locales no explican espera total. El ejercicio muestra complementariedad mediante decisiones perdidas, no mediante preferencia estética.

La matriz conserva una fila abierta para el tablero solicitado por Elena Acosta. Antes de construirlo se identifica qué decisión adicional habilitaría y qué afirmaciones resumiría. Si sólo repite tiempos ya disponibles y no cambia la puerta del piloto, queda como consulta derivada y no como sexto modelo mantenido. La selección puede posponer una representación sin negar que la necesidad de información exista.

### Prueba de lectura y decisión

La audiencia recibe un escenario sin explicación del autor. Debe identificar alcance, elementos, relaciones, supuestos y decisión. Se observa dónde interpreta distinto.

Luego se introduce un caso límite: mensaje tardío, huésped con accesibilidad, servicio externo caído o norma modificada. El modelo debe permitir localizar la pregunta o declarar que queda fuera.

Una lectura idéntica no siempre es necesaria. Sí debe haber acuerdo sobre significado operativo de los elementos usados para decidir. La leyenda y las etiquetas forman parte de la prueba.

Si el autor debe explicar cada flecha oralmente, el modelo todavía no es transferible.

La prueba registra desacuerdos, no sólo tasa de acierto. Dos interpretaciones pueden revelar término polisémico o concern en tensión. Se corrige etiqueta, separa vista o documenta diferencia legítima. El propósito es comunicación defendible, no unanimidad artificial.

Una segunda ronda verifica aprendizaje. Si la audiencia puede usar el modelo sólo después de una capacitación extensa, ese costo se registra. En decisiones infrecuentes y críticas puede justificarse; en operación cotidiana, probablemente no.

### Comparar carteras antes de comprometer mantenimiento

La prueba de una vista individual no demuestra que la cartera sea mínima. Dos modelos pueden funcionar por separado y duplicar la misma decisión; también pueden dejar una brecha entre ambos. Antes de aprobar el conjunto se comparan al menos dos carteras candidatas sobre los mismos escenarios y con las mismas audiencias. La comparación registra decisiones correctas, preguntas sin respuesta, tiempo de lectura, desacuerdos y esfuerzo estimado de actualización.

La primera alternativa de HH-15 combina proceso, arquitectura y tablero. Resulta fácil de presentar a conducción, pero no permite reconstruir autoridad ni la experiencia de una confirmación anticipada. La segunda agrega estados, matriz de autoridad y vista de experiencia. Aumenta costo y descubre que la palabra “disponible” habilita acciones diferentes. El equipo intenta una tercera opción: incorporar las aclaraciones dentro del proceso.

La lámina crece, mezcla actores con componentes y obliga a una leyenda que ninguna audiencia interpreta de la misma manera. Esa prueba justifica vistas separadas sin convertir la cantidad en objetivo.

Cada cartera se somete a un cambio controlado. Se modifica la regla de accesibilidad y se observa cuántos elementos deben localizarse, quién puede actualizarlos y qué decisión queda temporalmente suspendida. Esta no es todavía la auditoría de coherencia de N16. N15 sólo estima si la selección permite encontrar el impacto y si el costo de mantenerla es compatible con su uso. Una cartera que responde hoy y no puede actualizarse no supera la prueba de selección.

También se evalúa la alternativa de no modelar. Para una pregunta ya resuelta por una consulta reproducible, agregar un diagrama puede aumentar trabajo sin mejorar comprensión. Para una decisión infrecuente, un relato estructurado y una tabla pueden resultar suficientes. La comparación obliga a expresar qué propiedad aporta la representación y qué se perdería al reemplazarla. “Conviene verlo” no constituye justificación.

El cierre registra por qué fue elegida la cartera, qué alternativa se descartó y bajo qué cambio podría volver a evaluarse. Así el recorte no depende de la memoria de quienes participaron. La decisión conserva apertura: una nueva audiencia, una regulación o una fuente diferente pueden volver insuficiente el conjunto sin demostrar que la selección anterior fue negligente.

### Trazabilidad sin modelo total

Las vistas se vinculan mediante identificadores y glosario, no mediante una lámina gigantesca. Reserva R73 puede aparecer en proceso, estado y arquitectura bajo el mismo concepto.

Cada relación registra fuente o hipótesis. Un repositorio permite encontrar vistas afectadas por un cambio. La trazabilidad no implica sincronía automática de toda representación.

Se define una vista índice liviana que muestra preguntas, modelos y vínculos. No pretende representar el sistema. Ayuda a navegar la cartera.

La coherencia entre modelos se trabajará en N16. N15 sólo asegura que las comparaciones sean posibles.

Los vínculos deben poder recorrerse en ambas direcciones. Desde una decisión se encuentran vistas y evidencia; desde un elemento, decisiones afectadas. Esto permite estimar impacto de un cambio sin concentrar toda información en una lámina.

La trazabilidad se mantiene en el nivel necesario. Relacionar cada píxel con una fuente sería inviable. Se vinculan afirmaciones, elementos y relaciones cuya modificación cambia una decisión. El resto puede conservar procedencia por bloque.

## Tercera aplicación de HH-15: cinco familias de representación para una decisión de llegada

Elena Acosta debe decidir si Hotel Horizonte incorpora validación digital previa. El equipo selecciona cinco familias de representación: un par temporal de procesos con vistas actual y propuesta separadas, un recorrido de experiencia acotado, estados de identidad, arquitectura de integración y matriz de autoridad. El par se mantiene vinculado para comparar, pero nunca superpone vigencia actual y objetivo en una misma vista.

Cada una responde una pregunta distinta. Se excluyen modelo de datos completo, organigrama y mapa empresarial porque no cambian la decisión inmediata. Se conserva un enlace a fuentes.

Lucía Ferreyra y Mariela Benítez recorren un caso ordinario y otro accesible con los registros de HH-14. La prueba descubre que el proceso propuesto reduce el trabajo en mostrador y puede bloquear a quien no completa el canal digital. El recorrido de experiencia hace visible el daño; la matriz, la autoridad de excepción; la arquitectura, la dependencia del proveedor.

La recomendación de Federico Müller cambia y Elena decide que la validación previa sea opcional, con asistencia y ruta de excepción. Camila Duarte ajusta la promesa para que la confirmación no anticipe una capacidad inexistente. La cartera justificó su costo porque reveló una condición que un único proceso ocultaba.

El hotel establece caducidad y condiciones de revisión. La vista de proceso se revisa después del piloto; el modelo de estados, cuando cambia la regla; la arquitectura, en cada modificación de integración; la matriz de autoridad, al rotar roles. Si los episodios contradicen la hipótesis de menor espera o muestran una nueva exclusión, la decisión vuelve a abrirse. La utilidad queda vinculada con evidencia y mantenimiento real.

## Caso de transferencia: seleccionar modelos para una alerta de fraude

Un banco evalúa una alerta automática. Arquitectura muestra flujo del modelo. Una tabla de decisión muestra umbrales. Un mapa de actores revela quién puede apelar. Un modelo causal explora cómo más bloqueos cambian conducta y datos futuros.

Ninguno basta solo. Tampoco se necesita modelar toda la entidad. La cartera se limita a decisión de bloquear, revisar o permitir, con evidencia y autoridad.

La transferencia muestra que el riesgo determina carga de prueba. Un modelo exploratorio no puede convertirse sin revisión en regla operacional.

El banco prueba la cartera con una alerta verdadera, una falsa y una apelación. Si el modelo de decisión explica el umbral pero no el camino de reparación, se agrega vínculo al proceso. La arquitectura no debe absorber esa ausencia mediante más cajas.

El ejemplo limita la automatización: una explicación técnica de puntaje puede no explicar la decisión institucional. Se representan modelo predictivo, regla y autoridad como piezas distintas.

## Contraejemplo: el repositorio empresarial que nadie podía usar

Una organización exige representar toda capacidad, proceso, aplicación, dato y tecnología en ArchiMate antes de aprobar cambios. El repositorio crece durante tres años. Muchas relaciones no tienen fuente; equipos actualizan para cumplir y consultan pizarras informales para decidir.

La exhaustividad creó costo, retraso y confianza falsa. El problema no es ArchiMate, sino ausencia de preguntas, audiencias y política de vigencia.

La organización reduce el núcleo, automatiza relaciones técnicas, retira vistas sin uso y exige evidencia en decisiones críticas. Un modelo menor se vuelve más gobernable y útil.

El contraejemplo limita la tesis: formalidad y cobertura no garantizan comprensión. La disciplina consiste en elegir y sostener.

El repositorio conserva una vista de paisaje para orientación y crea vistas focales por decisiones. Las relaciones sin fuente se eliminan o marcan. La reducción permite que los equipos detecten un cambio real en lugar de navegar inventario ornamental.

La excepción es una obligación regulatoria de documentación exhaustiva. Incluso allí se separa archivo de cumplimiento y vista decisional. Cumplir no exige forzar a toda audiencia a leer el mismo artefacto.

## Errores frecuentes

**Empezar por la herramienta.**

La plantilla disponible define el problema antes de formular la pregunta.

**Buscar el modelo completo.**

Mezclar niveles y preocupaciones aumenta ruido y oculta decisiones.

**Confundir audiencia con simplificación vacía.**

Reducir detalle no autoriza borrar incertidumbre, riesgo o dependencia.

**Usar una notación sin leyenda ni verbo.**

Las relaciones quedan abiertas a interpretación.

**Superponer lo vigente y lo propuesto.**

La contradicción temporal parece inconsistencia cuando ambas vigencias comparten una vista sin marcas ni relación explícita.

**Generar más de lo que puede mantenerse.**

La cartera deriva y acumula deuda de modelo.

**Tratar el registro o el código como la realidad completa.**

La fuente omite trabajo, autoridad y experiencia.

**Pedir a la IA que decida qué importa.**

La herramienta puede representar fuentes; propósito y consecuencia siguen bajo responsabilidad humana.

**Conservar modelos por costo hundido.**

Retirar una vista sin uso puede aumentar integridad de la cartera.

## Consecuencias profesionales

El análisis de sistemas incluye decidir qué no modelar. Arquitectura, producto, operaciones, diseño, seguridad y dirección necesitan vistas distintas conectadas por conceptos estables.

Un profesional puede formular pregunta, audiencia y decisión antes de elegir notación; justificar alcance y resolución; evaluar costo total; probar lectura; y retirar representaciones que perdieron vigencia.

La documentación deja de ser archivo de entregables y se convierte en cartera gobernada. El éxito es que una persona pueda decidir y reconocer límites sin depender del autor.

La gobernanza asigna responsables de concepto además de archivos. Si “reserva confirmada” aparece en cinco vistas, su cambio semántico requiere coordinación. Esto no crea un comité para cada palabra: localiza términos cuyo desacuerdo cambia promesas.

La competencia profesional incluye decir que falta evidencia. Un modelo incompleto pero honesto puede orientar investigación. Completar huecos con supuestos invisibles produce una seguridad más peligrosa que la ausencia de dibujo.

La selección también ordena colaboración. Define quién aporta evidencia, quién valida significado, quién usa y quién mantiene. Esa distribución previene que el modelado sea una tarea aislada del analista y que las áreas sólo aprueben al final.

La evaluación de alternativas mejora porque cada representación expone un tipo de consecuencia. El proceso muestra desplazamiento de espera; la arquitectura, dependencia; el estado, transición imposible; la experiencia, barrera; la causalidad, efecto indirecto. Ninguna vista obtiene prioridad permanente. La pregunta determina cuál conduce y cuáles controlan puntos ciegos.

El profesional también puede detener la producción. Si la decisión es reversible, la evidencia débil y el costo de modelar alto, un experimento puede aprender más. Si la decisión compromete seguridad o derechos, la cartera necesita mayor precisión. Elegir no modelar todavía no equivale a improvisar: declara por qué otra forma de evidencia resulta más adecuada.

Esta capacidad evita dos extremos. El primero documenta todo antes de actuar. El segundo considera cualquier modelo como burocracia. METSI propone proporcionalidad: representar lo suficiente para que la acción sea defendible, sus límites sean visibles y la revisión pueda comenzar cuando cambie el contexto.

El resultado debe poder enseñarse y transferirse. Una cartera que sólo comprende quien la construyó sigue siendo dependencia personal. Registrar pregunta, audiencia, evidencia y prueba permite que otra persona revise el recorte, cuestione una omisión y actualice la representación sin empezar nuevamente ni aceptar el modelo por autoridad.

## Límites y tensiones

Un modelo simple puede democratizar comprensión y omitir una complejidad crítica. La prueba con casos límite ayuda a distinguir claridad de simplificación engañosa.

La participación amplía perspectivas y aumenta costo. No todas las personas intervienen en cada detalle, pero quienes absorben consecuencias deben tener una vía relevante.

La generación automática reduce deriva y puede privilegiar lo técnicamente observable. Los elementos sociales necesitan otras fuentes y responsabilidades.

Los estándares aportan lenguaje compartido y pueden imponer categorías ajenas al problema. Se adaptan con trazabilidad, no se obedecen como fin.

Finalmente, una cartera mínima no es estable para siempre. Cambian preguntas, sistemas y autoridad. El costo de revisión forma parte del diseño desde el inicio.

Existe tensión entre consistencia y autonomía. Un lenguaje común facilita impacto; una taxonomía central puede borrar particularidades. Se gobiernan conceptos compartidos y se permiten vistas locales con correspondencia explícita.

También existe tensión entre transparencia y seguridad. Una vista amplia de dependencias puede revelar información sensible. La audiencia y el acceso se diseñan sin usar confidencialidad como excusa para ocultar riesgos a quienes deben decidir.

## De N15 a N16: de seleccionar vistas a aprender de sus contradicciones

HH-15 deja modelos con propósito, alcance, evidencia, vigencia y vínculos. Al compararlos aparecerán nombres incompatibles, fronteras distintas y estados que no coinciden. Algunas diferencias serán errores; otras, perspectivas o tiempos legítimos.

N16 trabajará coherencia y contradicciones productivas entre modelos y ciclos de vida. No agregará modelos por reflejo. Utilizará las tensiones para revisar supuestos y cerrar el Bloque C.

## Síntesis

Un modelo es una simplificación deliberada. Se evalúa por pregunta, decisión, audiencia, evidencia, alcance, resolución, costo y vigencia. Más detalle puede reducir utilidad.

Estructura, comportamiento, decisión, causalidad y experiencia requieren familias diferentes. Notaciones como UML, BPMN, ArchiMate o C4 ofrecen semánticas y límites. Ninguna decide qué importa.

Una cartera mínima vincula vistas sin fabricar un modelo total. Cada representación debe pasar una prueba de lectura y decisión. También puede retirarse.

HH-15 organiza diez decisiones desde pregunta hasta utilidad. Prepara comparaciones para N16, donde la coherencia no consistirá en uniformar, sino en explicar acuerdos y contradicciones.

## Cinco píldoras para recordar

1. Modelar es decidir qué diferencia conservar y qué omitir.
2. La pregunta elige la vista; la herramienta no elige la pregunta.
3. Audiencias diferentes pueden necesitar resoluciones distintas de los mismos conceptos.
4. El costo incluye mantener, explicar, gobernar y retirar.
5. Una cartera mínima conectada supera a un modelo total ilegible.

## Glosario esencial

**Alcance:** frontera espacial, organizacional y temporal de una representación.

**Audiencia:** personas que deben interpretar, discutir, decidir o mantener un modelo.

**Cartera de modelos:** conjunto gobernado de representaciones y sus relaciones.

**Concern:** preocupación o interés relevante de un stakeholder según ISO/IEC/IEEE 42010.

**Deuda de modelo:** costo y riesgo acumulados por representaciones desactualizadas o ambiguas.

**Familia de modelo:** tipo de representación orientado a estructura, comportamiento, decisión, causalidad o experiencia.

**Modelo:** representación selectiva construida con un propósito.

**Notación:** convenciones que definen elementos, relaciones y reglas de lectura.

**Resolución:** grado de detalle dentro de un nivel y alcance.

**Trazabilidad:** vínculo entre modelo, fuente, decisión y otras vistas.

**Punto de vista (*viewpoint*):** convenciones para construir vistas que atienden preocupaciones de una audiencia.

**Vista:** expresión de un sistema desde un punto de vista y para ciertas preocupaciones.

**Vigencia:** período o condición durante la cual una representación puede utilizarse.

## Preguntas de preparación

1. ¿Por qué un modelo más detallado puede ser menos útil?
2. ¿Qué diferencia existe entre alcance, nivel y resolución?
3. ¿Qué preguntas del check-in requieren proceso, estados, arquitectura o experiencia?
4. ¿Cómo se prueba que una audiencia puede decidir con una vista?
5. ¿Cuándo conviene retirar un modelo?
6. ¿Qué riesgos introduce generar representaciones automáticamente desde código o registros?

Para el encuentro, seleccionar una decisión conocida. Formular tres preguntas y comparar al menos cuatro familias de representación. Justificar una cartera mínima mediante audiencia, evidencia, resolución, costo, vigencia y prueba de utilidad.

## Referentes

**George Box.** Formuló la utilidad de modelos deliberadamente simplificados y sus límites.

**Donald Schön.** Mostró cómo una representación puede sostener reflexión y revisión durante la práctica profesional.

**Peter Senge.** Integró modelos mentales, aprendizaje organizacional y pensamiento sistémico.

**Martin Fowler.** Sistematizó el uso selectivo de modelos y patrones para comunicar decisiones de software.

**Grady Booch.** Desarrolló abstracciones y vistas orientadas a responsabilidades, estructura y comportamiento.

**Thomas Davenport.** Vinculó procesos, información, tecnología y cambio organizacional.

## Referencias base

- Box, G. E. P. (1976). “Science and Statistics”. *Journal of the American Statistical Association*, 71(356), 791 a 799. https://doi.org/10.1080/01621459.1976.10480949
- Checkland, P. y Poulter, J. (2007). *Learning for Action*. Wiley. ISBN 978-0-470-02554-3.
- Sterman, J. D. (2000). *Business Dynamics*. McGraw-Hill.
- Moody, D. (2009). “The ‘Physics’ of Notations: Toward a Scientific Basis for Constructing Visual Notations in Software Engineering”. *IEEE Transactions on Software Engineering*, 35(6), 756 a 779. https://doi.org/10.1109/TSE.2009.67
- ISO/IEC/IEEE (2022). *ISO/IEC/IEEE 42010:2022 Software, systems and enterprise: Architecture description*. https://www.iso.org/standard/74393.html
- Object Management Group (2017). *Unified Modeling Language, Version 2.5.1*. https://www.omg.org/spec/UML/2.5.1
- Object Management Group (2014). *Business Process Model and Notation, Version 2.0.2*. https://www.omg.org/spec/BPMN/2.0.2
- Scolari, C. A. (2018). *Las leyes de la interfaz: diseño, ecología, evolución, tecnología*. Gedisa.
- Stickdorn, M., Hormess, M. E., Lawrence, A. y Schneider, J. (2018). *This Is Service Design Doing*. O’Reilly Media.
- The Open Group (2022). *ArchiMate Specification, Version 3.2*. https://www.opengroup.org/archimate-licensed-downloads
- Brown, S. (s. f.). *The C4 Model for Visualising Software Architecture*. Consultado el 8 de septiembre de 2026. https://c4model.com/
- Lankhorst, M. et al. (2017). *Enterprise Architecture at Work*. Springer. https://doi.org/10.1007/978-3-662-53933-0
- Jackson, M. (2001). *Problem Frames*. Addison-Wesley.
- Object Management Group (2024). *Business Architecture Core Metamodel, Version 1.0*. https://www.omg.org/spec/BACM/1.0
- Schön, D. A. (1983). *The Reflective Practitioner*. Basic Books.
- Senge, P. M. (2006). *The Fifth Discipline*, Revised Edition. Currency.
- Fowler, M. (2003). *UML Distilled*. Addison-Wesley.
- Booch, G. et al. (2007). *Object-Oriented Analysis and Design with Applications*. Addison-Wesley.
- Davenport, T. H. (1993). *Process Innovation: Reengineering Work through Information Technology*. Harvard Business School Press.
