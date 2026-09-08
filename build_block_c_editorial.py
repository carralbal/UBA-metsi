#!/usr/bin/env python3
"""Build the editorial source packages for METSI N11 through N36.

The canonical Markdown remains authoritative and untouched. This generator
adds only editorial paratext, source-grounded diagrams, licensed portraits and
the approved METSI publication structure.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
from pathlib import Path

import build_collection as base


ROOT = Path(__file__).resolve().parent
PORTRAIT_ROOT = ROOT / "assets" / "portraits-block-c"
SHARED_PORTRAITS = ROOT / "assets" / "portraits"
MATCHES = ROOT / "N30-v1-editorial" / "assets" / "matches-close.png"

SOURCES = {
    n: next((ROOT / f"N{n}-content-canonical" / "source").glob("*.md"))
    for n in range(11, 37)
}

REFERENTS = {
    11: ["richard-wang", "luc-moreau", "robert-groves", "helen-nissenbaum", "elham-tabassi", "cathy-oneil"],
    12: ["eric-evans", "leslie-lamport", "martin-fowler", "david-ferraiolo", "nancy-leveson", "elham-tabassi"],
    13: ["leslie-lamport", "jim-gray", "pat-helland", "werner-vogels", "martin-kleppmann", "peter-bailis"],
    14: ["michael-hammer", "thomas-davenport", "geary-rummler", "wil-van-der-aalst", "john-little", "wallace-hopp"],
    15: ["george-box", "peter-checkland", "john-sterman", "daniel-moody", "simon-brown", "marc-lankhorst"],
    16: ["peter-checkland", "chris-argyris", "john-sterman", "michael-jackson", "barry-boehm", "winston-royce"],
    17: ["barry-boehm", "winston-royce", "donald-schon", "cynthia-kurtz-david-snowden", "pmi", "agile-alliance"],
    18: ["manny-lehman", "david-parnas", "ward-cunningham", "michael-feathers", "iso-iec-ieee", "nist"],
    19: ["ronald-coase", "oliver-williamson", "carliss-baldwin-kim-clark", "martin-fowler", "nist", "cisa"],
    20: ["pmi", "iso-iec-ieee", "barry-boehm", "donald-schon", "henry-mintzberg", "sebok"],
    21: ["pmi", "marty-cagan", "itil", "parker-van-alstyne-choudary", "mik-kersten", "team-topologies"],
    22: ["karl-popper", "donald-campbell", "eric-ries", "teresa-torres", "ron-kohavi", "nist"],
    23: ["tom-gilb", "jeff-patton", "mary-tom-poppendieck", "jez-humble", "nicole-forsgren", "alistair-cockburn"],
    24: ["donald-reinertsen", "eliyahu-goldratt", "john-little", "david-anderson", "mik-kersten", "pmi"],
    25: ["john-little", "wallace-hopp-mark-spearman", "donald-reinertsen", "taiichi-ohno", "david-anderson", "nicole-forsgren"],
    26: ["itil", "parker-van-alstyne-choudary", "team-topologies", "nist", "cisa", "iso-iec"],
    27: ["ietf", "openapi-initiative", "json-schema", "eric-evans", "martin-kleppmann", "hohpe-woolf"],
    28: ["iso-iec", "bass-clements-kazman", "victor-basili", "nist", "w3c", "forsgren-humble-kim"],
    29: ["humble-farley", "forsgren-humble-kim", "nist", "slsa", "cisa", "iso-iec"],
    30: ["google-sre", "opentelemetry", "nist", "forsgren-humble-kim", "erik-hollnagel", "nancy-leveson"],
    31: ["oecd", "nist", "unesco", "stuart-russell", "judea-pearl", "virginia-dignum"],
    32: ["nist", "joy-buolamwini-timnit-gebru", "batya-friedman-david-hendry", "madeleine-elish", "ben-shneiderman", "iso-iec"],
    33: ["nist", "iso-iec", "european-union", "inioluwa-raji", "margaret-mitchell", "timnit-gebru"],
    34: ["peter-checkland-john-poulter", "donald-schon", "stephen-toulmin", "iso-iec-ieee", "sebok", "pmi"],
    35: ["stephen-toulmin", "edward-tufte", "donald-schon", "chris-argyris", "paulo-freire", "etienne-wenger"],
    36: ["donald-schon", "chris-argyris-donald-schon", "john-dewey", "david-kolb", "amy-edmondson", "jack-mezirow"],
}

PORTRAIT_NAMES = {
    "richard-wang": "Richard Y. Wang", "luc-moreau": "Luc Moreau", "robert-groves": "Robert M. Groves",
    "helen-nissenbaum": "Helen Nissenbaum", "elham-tabassi": "Elham Tabassi", "cathy-oneil": "Cathy O’Neil",
    "eric-evans": "Eric Evans", "leslie-lamport": "Leslie Lamport", "martin-fowler": "Martin Fowler",
    "david-ferraiolo": "David Ferraiolo", "nancy-leveson": "Nancy Leveson", "jim-gray": "Jim Gray",
    "pat-helland": "Pat Helland", "werner-vogels": "Werner Vogels", "martin-kleppmann": "Martin Kleppmann",
    "peter-bailis": "Peter Bailis", "michael-hammer": "Michael Hammer", "thomas-davenport": "Thomas Davenport",
    "geary-rummler": "Geary Rummler", "wil-van-der-aalst": "Wil van der Aalst", "john-little": "John D. C. Little",
    "wallace-hopp": "Wallace Hopp", "george-box": "George Box", "peter-checkland": "Peter Checkland",
    "john-sterman": "John Sterman", "daniel-moody": "Daniel Moody", "simon-brown": "Simon Brown",
    "marc-lankhorst": "Marc Lankhorst", "chris-argyris": "Chris Argyris", "michael-jackson": "Michael A. Jackson",
    "barry-boehm": "Barry Boehm", "winston-royce": "Winston W. Royce",
    "donald-schon": "Donald Schön", "cynthia-kurtz-david-snowden": "Cynthia Kurtz y David Snowden",
    "pmi": "Project Management Institute", "agile-alliance": "Agile Alliance",
    "manny-lehman": "Manny Lehman", "david-parnas": "David Parnas", "ward-cunningham": "Ward Cunningham",
    "michael-feathers": "Michael Feathers", "iso-iec-ieee": "ISO/IEC/IEEE", "nist": "NIST",
    "ronald-coase": "Ronald Coase", "oliver-williamson": "Oliver Williamson",
    "carliss-baldwin-kim-clark": "Carliss Baldwin y Kim Clark", "cisa": "CISA",
    "henry-mintzberg": "Henry Mintzberg", "sebok": "SEBoK",
    "marty-cagan": "Marty Cagan", "itil": "ITIL", "parker-van-alstyne-choudary": "Parker, Van Alstyne y Choudary",
    "mik-kersten": "Mik Kersten", "team-topologies": "Team Topologies", "karl-popper": "Karl Popper",
    "donald-campbell": "Donald Campbell", "eric-ries": "Eric Ries", "teresa-torres": "Teresa Torres",
    "ron-kohavi": "Ron Kohavi", "tom-gilb": "Tom Gilb", "jeff-patton": "Jeff Patton",
    "mary-tom-poppendieck": "Mary y Tom Poppendieck", "jez-humble": "Jez Humble", "nicole-forsgren": "Nicole Forsgren",
    "alistair-cockburn": "Alistair Cockburn", "donald-reinertsen": "Donald Reinertsen", "eliyahu-goldratt": "Eliyahu Goldratt",
    "john-little": "John D. C. Little", "david-anderson": "David J. Anderson",
    "wallace-hopp-mark-spearman": "Wallace Hopp y Mark Spearman", "taiichi-ohno": "Taiichi Ohno",
    "iso-iec": "ISO/IEC", "ietf": "IETF", "openapi-initiative": "OpenAPI Initiative",
    "json-schema": "JSON Schema", "hohpe-woolf": "Gregor Hohpe y Bobby Woolf",
    "bass-clements-kazman": "Len Bass, Paul Clements y Rick Kazman", "victor-basili": "Victor Basili",
    "w3c": "W3C", "forsgren-humble-kim": "Nicole Forsgren, Jez Humble y Gene Kim",
    "humble-farley": "Jez Humble y David Farley", "slsa": "SLSA", "google-sre": "Google SRE",
    "opentelemetry": "OpenTelemetry", "erik-hollnagel": "Erik Hollnagel",
    "oecd": "OECD", "unesco": "UNESCO", "stuart-russell": "Stuart Russell",
    "judea-pearl": "Judea Pearl", "virginia-dignum": "Virginia Dignum",
    "joy-buolamwini-timnit-gebru": "Joy Buolamwini y Timnit Gebru",
    "batya-friedman-david-hendry": "Batya Friedman y David Hendry",
    "madeleine-elish": "Madeleine Clare Elish", "ben-shneiderman": "Ben Shneiderman",
    "european-union": "European Union", "inioluwa-raji": "Inioluwa Deborah Raji",
    "margaret-mitchell": "Margaret Mitchell", "timnit-gebru": "Timnit Gebru",
    "peter-checkland-john-poulter": "Peter Checkland y John Poulter",
    "stephen-toulmin": "Stephen Toulmin", "edward-tufte": "Edward Tufte",
    "paulo-freire": "Paulo Freire", "etienne-wenger": "Etienne Wenger",
    "chris-argyris-donald-schon": "Chris Argyris y Donald Schön",
    "john-dewey": "John Dewey", "david-kolb": "David Kolb",
    "amy-edmondson": "Amy Edmondson", "jack-mezirow": "Jack Mezirow",
}

PHOTO_ALTS = {
    11: [
        "Una analista argentina contrasta un registro impreso con una pared de evidencias y proyecciones en una sala de operaciones luminosa.",
        "Una mano recorre un registro impreso junto a una regla y reflejos de una pantalla, mientras el fenómeno medido permanece fuera de campo.",
        "Una profesional recorre un archivo institucional donde una carpeta adelantada y los reflejos hacen visibles las capas de procedencia.",
    ],
    12: [
        "Un profesional hotelero argentino acciona un lector de acceso ante un umbral de vidrio mientras otro trabajador sostiene el estado operativo desde el interior.",
        "Dos manos sostienen una credencial de acceso y una ficha de estado a ambos lados de un umbral de servicio.",
        "Una trabajadora reconstruye un episodio entre un reloj, un registro temporal, una notificación y el reflejo de una puerta.",
    ],
    13: [
        "Dos trabajadores hoteleros se aproximan desde corredores opuestos a la última habitación, entre puertas reflejadas y un reloj.",
        "Dos manos acercan sobres de llave idénticos desde lados opuestos de un mostrador donde queda una sola llave física.",
        "Un trabajador compara dos registros demorados junto a un reloj mientras un carro espera en la bifurcación de dos corredores.",
    ],
    14: [
        "Una trabajadora hotelera recorre un corredor de servicio con carros, ascensor y cruces de personal que vuelven visibles handoffs y colas.",
        "Tres carros esperan en colas diferentes mientras trabajadores intercambian ropa blanca y una ficha en un corredor de servicio.",
        "Una profesional sigue un expediente físico a través de un mostrador, una escalera y una sala de espera vistos en reflejos sucesivos.",
    ],
    15: [
        "Una profesional argentina compara varias representaciones materiales de la misma operación antes de elegir cuál responde la pregunta.",
        "Una mano retira una vista innecesaria de una mesa que reúne un modelo de flujo, láminas transparentes y tarjetas de escenario.",
        "Tres profesionales observan la misma operación desde posiciones distintas alrededor de un muro de vidrio.",
    ],
    16: [
        "Dos profesionales comparan diagramas transparentes que no coinciden y conservan una versión anterior en una sala de planificación.",
        "Una profesional marca el punto exacto donde dos representaciones superpuestas se contradicen sobre un muro de vidrio iluminado.",
        "Una profesional retira un modelo obsoleto sin borrar su rastro mientras otra prueba la versión nueva contra un episodio real.",
    ],
    17: [
        "Una profesional argentina organiza sobre vidrio rutas de intervención con ritmos y compromisos diferentes.",
        "Un equipo compara una secuencia planificada, un prototipo y una prueba acotada sobre una mesa de trabajo.",
        "Una profesional observa cómo varios caminos convergen en una única puerta de decisión.",
    ],
    18: [
        "Una especialista argentina examina capas de documentación, planos y terminales heredadas en un archivo técnico.",
        "Una mano revela anotaciones y dependencias ocultas entre registros de épocas diferentes.",
        "Una profesional recorre un depósito de equipos retirados mientras conserva una carpeta de evidencia vigente.",
    ],
    19: [
        "Un equipo argentino compara módulos, contratos y conexiones antes de elegir cómo realizar una capacidad.",
        "Varias piezas técnicas, una ficha contractual y una herramienta manual ocupan la misma mesa de decisión.",
        "Una profesional permanece entre dos corredores de proveedores y conserva una salida visible.",
    ],
    20: [
        "Una directora argentina ordena hitos, evidencias y rutas de salida en una pared de planificación editorial.",
        "Una mano mueve un marcador de compromiso entre puertas de decisión y registros de prueba.",
        "Un equipo transfiere una carpeta y una llave operacional al final de un recorrido verificable.",
    ],
    21: [
        "Una profesional argentina atraviesa un umbral de hotel donde conviven una transición temporal y capacidades permanentes.",
        "Personas recorren una fachada porteña en transformación mientras el servicio continúa a través de una puerta estable.",
        "Varias personas eligen recorridos distintos desde un descanso compartido dentro de un edificio institucional argentino.",
    ],
    22: [
        "Un profesional argentino retira una alternativa de una pared de hipótesis conectadas por evidencia.",
        "Una investigadora argentina observa explicaciones rivales iluminadas sobre capas translúcidas.",
        "Un trabajador prueba una salida limitada mientras otro conserva visible el punto de retorno del servicio.",
    ],
    23: [
        "Dos profesionales hoteleros argentinos coordinan un recorrido de punta a punta entre puertas y mostradores conectados.",
        "Una secuencia material atraviesa un mostrador hotelero y conecta a dos responsables del mismo episodio.",
        "Una persona recorre un corredor institucional completo con una unidad de trabajo desde origen hasta destino.",
    ],
    24: [
        "Una directora argentina retira opciones de una mesa y deja visible una única trayectoria protegida.",
        "Personas toman caminos diferentes dentro de un gran espacio cívico, mientras una ruta permanece vacía.",
        "Dos manos preservan un expediente y apartan otro sobre una mesa de trabajo iluminada.",
    ],
    25: [
        "Trabajadores hoteleros argentinos ocupan etapas distintas mientras un carro espera en el centro del corredor.",
        "Un carro permanece inmóvil en un umbral mientras varias personas trabajan a ambos lados.",
        "Dos profesionales devuelven una evidencia desde operación hacia una mesa de decisión a través de reflejos.",
    ],
    26: [
        "Una profesional hotelera argentina observa un corredor de vidrio donde convergen trabajadores, proveedores y recorridos de servicio independientes.",
        "Tres trabajadores ocupan umbrales diferentes de un corredor de servicio y vuelven visibles dependencias internas y externas.",
        "El interior y la calle de un hotel porteño se reflejan mientras distintos participantes sostienen una misma promesa.",
    ],
    27: [
        "Dos profesionales argentinos intercambian una llave y un registro a través de un mostrador donde el tiempo también condiciona el acuerdo.",
        "Dos manos intercambian una llave y una ficha mientras otras esperan, haciendo visibles orden, duplicación y consecuencia.",
        "Una secuencia de puertas e indicadores muestra que estructura, significado, tiempo y operación deben coincidir.",
    ],
    28: [
        "Una especialista argentina examina un umbral accesible junto con la operación que debe sostenerlo.",
        "Una especialista y una trabajadora hotelera prueban accesibilidad, seguridad y continuidad sobre el recorrido real.",
        "Dos rutas de servicio con ritmos distintos muestran que desempeño, inclusión y confiabilidad pueden entrar en tensión.",
    ],
    29: [
        "Una directora de operaciones argentina y un especialista técnico evalúan una ruta de avance y otra de recuperación.",
        "Un técnico recorre una vía física de recuperación que incluye infraestructura, evidencia y trabajo humano.",
        "Tres umbrales se habilitan de manera progresiva para limitar exposición antes de ampliar una liberación.",
    ],
    30: [
        "Una responsable nocturna argentina observa señales humanas y técnicas que revelan una degradación del recorrido de ingreso.",
        "Un trabajador nocturno responde a una secuencia de señales en un corredor donde emerge un incidente.",
        "Tres integrantes de operación reconstruyen un episodio con evidencia para aprender sin reducirlo a culpa individual.",
    ],
    31: ["Una profesional argentina delimita el uso pertinente de inteligencia artificial en una recepción porteña.", "Un equipo separa reglas, predicción y decisión sobre una mesa de operaciones.", "Una mano se detiene antes de automatizar una acción mientras conserva una vía manual."],
    32: ["Una especialista argentina observa dos recorridos de servicio y evalúa consecuencias desiguales.", "Un equipo hotelero prueba casos ordinarios y extremos con evidencia material.", "Una supervisora nocturna enfrenta varias excepciones simultáneas y vuelve visible el límite del control humano."],
    33: ["Una responsable argentina recorre un archivo operativo donde versiones, accesos y cambios deben permanecer gobernados.", "Un equipo actualiza un inventario vivo de capacidades, fuentes y responsables.", "Una profesional retira un acceso preservando evidencia y continuidad del servicio."],
    34: ["Una profesional argentina sigue una cadena de intervención a través de varios umbrales institucionales.", "Dos profesionales conectan evidencia, mapa operativo y consecuencia en un mismo expediente.", "Un recorrido hotelero atraviesa personas y áreas sin perder la promesa común."],
    35: ["Una profesional argentina escucha una objeción ante audiencias diversas y conserva visible la evidencia.", "Profesionales discuten un mismo caso desde perspectivas distintas.", "Una persona transfiere expediente y capacidad operacional a otro equipo."],
    36: ["Una profesional argentina revisa decisiones y evidencia después de una intervención.", "Un equipo reconstruye una sorpresa sin reducirla a culpa individual.", "Una persona egresada sale a la ciudad con un método abierto de aprendizaje profesional."],
}

DIAGRAMS = {
    11: [
        ("Cadena de sostén", ["Fenómeno", "Registro", "Dato", "Afirmación", "Decisión"]),
        ("Procedencia y transformación", ["Entidad", "Actividad", "Agente", "Selección", "Agregación", "Incertidumbre"]),
        ("Puertas de evidencia", ["Observar", "Contrastar", "Probar sensibilidad", "Decidir", "Preparar revisión"]),
    ],
    12: [
        ("Transición verificable", ["Comando", "Regla", "Evento", "Evidencia", "Estado"]),
        ("Autoridad y reparación", ["Proponer", "Autorizar", "Ejecutar", "Verificar", "Reparar"]),
        ("Tres tiempos de un episodio", ["Ocurrió", "Se registró", "Se conoció", "Se proyectó", "Se corrigió"]),
    ],
    13: [
        ("Falla parcial", ["Intención", "Envío", "Timeout", "Reintento", "Efecto protegido"]),
        ("Convergencia defendible", ["Detectar", "Correlacionar", "Comparar", "Explicar", "Resolver"]),
        ("Perturbaciones", ["Demora", "Duplicación", "Reordenamiento", "Concurrencia", "Caída"]),
    ],
    14: [
        ("Proceso de punta a punta", ["Promesa", "Caso", "Handoff", "Cola", "Excepción", "Cierre"]),
        ("Tiempo real del servicio", ["Trabajo", "Espera", "Retrabajo", "Demanda de falla", "Calendario"]),
        ("Mapa de flujo real", ["Declarado", "Ejecutado", "Experimentado", "Evidencia", "Prueba de mejora"]),
    ],
    15: [
        ("Selección por pregunta", ["Pregunta", "Decisión", "Audiencia", "Evidencia", "Costo", "Vigencia"]),
        ("Familias de modelo", ["Estructura", "Comportamiento", "Decisión", "Causalidad", "Experiencia"]),
        ("Cartera mínima", ["Elegir", "Vincular", "Probar lectura", "Mantener", "Retirar"]),
    ],
    16: [
        ("Contradicciones productivas", ["Término", "Frontera", "Tiempo", "Norma", "Cantidad", "Autoridad"]),
        ("Gobierno entre vistas", ["Correspondencia", "Contrato", "Versión", "Impacto", "Decisión"]),
        ("Ciclo de vida", ["Crear", "Usar", "Revisar", "Sustituir", "Retirar", "Recordar"]),
    ],
    17: [
        ("Continuo de intervención", ["Anticipar", "Iterar", "Incrementar", "Adaptar", "Experimentar"]),
        ("Compromiso progresivo", ["Hipótesis", "Prueba", "Puerta", "Capacidad", "Ampliación"]),
        ("Mapa HH-17", ["Incertidumbre", "Lógica", "Evidencia", "Autoridad", "Salida"]),
    ],
    18: [
        ("Capas del legado", ["Código", "Datos", "Rutinas", "Contratos", "Obligaciones"]),
        ("Trazabilidad normativa", ["Norma", "Interpretación", "Control", "Prueba", "Reparación"]),
        ("Mapa HH-18", ["Valor", "Dependencia", "Riesgo", "Transición", "Retiro"]),
    ],
    19: [
        ("Espacio de realización", ["Configurar", "Integrar", "Construir", "Contratar", "No automatizar"]),
        ("Costo de vida", ["Adquirir", "Operar", "Cambiar", "Reparar", "Salir"]),
        ("Mapa HH-19", ["Capacidad", "Opción", "Dependencia", "Evidencia", "Salida"]),
    ],
    20: [
        ("Arquitectura de estrategia", ["Comprender", "Elegir", "Preparar", "Ampliar", "Transferir"]),
        ("Puertas de decisión", ["Entrada", "Evidencia", "Autoridad", "Salida", "Detención"]),
        ("Mapa HH-20", ["Hipótesis", "Tailoring", "Hitos", "Operación", "Retiro"]),
    ],
    21: [("Cuatro objetos de gestión", ["Proyecto", "Producto", "Servicio", "Plataforma", "Capacidad"]), ("Horizontes y ownership", ["Transición", "Aprendizaje", "Operación", "Ecosistema", "Retiro"]), ("Mapa HH-21", ["Outcome", "Objeto", "Autoridad", "Evidencia", "Cierre"])],
    22: [("Anatomía de una hipótesis", ["Población", "Intervención", "Mecanismo", "Outcome", "Umbral"]), ("Prueba refutable", ["Baseline", "Rival", "Señal", "Salvaguarda", "Decisión"]), ("Mapa HH-22", ["Apuesta", "Exposición", "Evidencia", "Autoridad", "Retiro"])],
    23: [("Slice de capacidad", ["Necesidad", "Regla", "Dato", "Operación", "Outcome"]), ("Aprendizaje por corte", ["Hipótesis", "Episodio", "Integración", "Prueba", "Expansión"]), ("Mapa HH-23", ["Población", "Capacidad", "Excepción", "Evidencia", "Siguiente corte"])],
    24: [("Decisión y renuncia", ["Opción", "Valor", "Demora", "Capacidad", "Renuncia"]), ("Cartera limitada", ["Obligación", "Apuesta", "Habilitador", "Trabajo en curso", "Revisión"]), ("Mapa HH-24", ["Outcome", "Costo", "Dependencia", "Autoridad", "No ahora"])],
    25: [("Flujo de punta a punta", ["Demanda", "Cola", "Trabajo", "Uso", "Feedback"]), ("Economía del flujo", ["Trabajo en curso", "Throughput", "Tiempo", "Lote", "Variabilidad"]), ("Mapa HH-25", ["Unidad", "Espera", "Handoff", "Política", "Reparación"])],
    26: [("Ecosistema de la promesa", ["Promesa", "Capacidad", "Plataforma", "Tercero", "Reparación"]), ("Dependencia gobernada", ["Ownership", "Confianza", "Señal", "Degradación", "Salida"]), ("Mapa HH-26", ["Participante", "Contrato", "Concentración", "Contingencia", "Revisión"])],
    27: [("Capas del contrato", ["Sintaxis", "Semántica", "Tiempo", "Operación"]), ("Comportamiento verificable", ["Precondición", "Invariante", "Error", "Reintento", "Evolución"]), ("Mapa HH-27", ["Productor", "Consumidor", "Efecto", "Prueba", "Reparación"])],
    28: [("Argumento de calidad", ["Promesa", "Escenario", "Riesgo", "Reclamo", "Evidencia"]), ("Atributos en tensión", ["Confiabilidad", "Desempeño", "Seguridad", "Accesibilidad", "Cambio"]), ("Mapa HH-28", ["Población", "Oráculo", "Umbral", "Renuncia", "Autoridad"])],
    29: [("Cadena de liberación", ["Fuente", "Artefacto", "Ambiente", "Despliegue", "Cierre"]), ("Compromiso progresivo", ["Evidencia", "Aprobación", "Cohorte", "Señal", "Detención"]), ("Mapa HH-29", ["Código", "Datos", "Infraestructura", "Rollback", "Reparación"])],
    30: [("Señales de la promesa", ["Recorrido", "Telemetría", "Negocio", "Experiencia", "Decisión"]), ("Confiabilidad gobernada", ["SLI", "SLO", "Presupuesto", "Alerta", "Respuesta"]), ("Mapa HH-30", ["Incidente", "Contención", "Reparación", "Revisión", "Aprendizaje"])],
    31: [("Capacidades diferentes", ["Regla", "Predicción", "Generación", "Agencia"]), ("Juicio de pertinencia", ["Tarea", "Alternativa", "Valor", "Consecuencia", "Control"]), ("Mapa HH-31", ["Propósito", "Evidencia", "Autoridad", "No uso", "Revisión"])],
    32: [("Arquitectura de evaluación", ["Tarea", "Cobertura", "Métrica", "Severidad", "Decisión"]), ("Autonomía proporcional", ["Baseline", "Desagregación", "Robustez", "Supervisión"]), ("Mapa HH-32", ["Prueba", "Umbral", "Exposición", "Monitoreo", "Retiro"])],
    33: [("Registro vivo", ["Uso", "Frontera", "Owner", "Versión", "Riesgo"]), ("Ciclo de gobierno", ["Datos", "Proveedor", "Cambio", "Monitoreo", "Incidente"]), ("Mapa HH-33", ["Contestar", "Reparar", "Aprender", "Retirar"] )],
    34: [("Cadena completa", ["Problema", "Evidencia", "Decisión", "Operación", "Gobierno"]), ("Coherencia defendible", ["Vertical", "Horizontal", "Contradicción", "Puerta"]), ("Mapa HH-34", ["Supuesto", "Prueba", "Consecuencia", "Revisión"])],
    35: [("Argumento situado", ["Audiencia", "Tesis", "Evidencia", "Garantía", "Objeción"]), ("Cuatro defensas", ["Ejecutiva", "Técnica", "Operativa", "Afectada"]), ("Mapa HH-35", ["Transferir", "Apropiar", "Probar", "Reformular"])],
    36: [("Ciclo reflexivo", ["Decidir", "Actuar", "Observar", "Sorprender", "Revisar"]), ("Aprender en dos bucles", ["Corregir acción", "Revisar marco", "Cambiar práctica"]), ("Mapa HH-36", ["Episodio", "Evidencia", "IA crítica", "Próxima prueba"])],
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean_title(number: int, title: str) -> str:
    return re.sub(rf"^N{number:02d}\s*[·—-]\s*", "", title).strip()


def referent_paragraphs(section: base.Section) -> list[str]:
    return [line.strip() for line in section.lines if line.strip().startswith("**")]


def portrait_source(key: str) -> Path | None:
    for root in (PORTRAIT_ROOT, SHARED_PORTRAITS):
        for suffix in (".jpg", ".jpeg", ".png", ".webp"):
            path = root / f"{key}{suffix}"
            if path.is_file() and path.stat().st_size:
                return path
    return None


def initials(name: str) -> str:
    return "".join(part[0] for part in re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", name)[:2]).upper()


def build_referents(number: int, section: base.Section, assets: Path) -> tuple[str, list[dict]]:
    paragraphs = referent_paragraphs(section)
    if len(paragraphs) != 6:
        raise ValueError(f"N{number:02d} requiere seis Referentes; se encontraron {len(paragraphs)}")
    cards = []
    records = []
    for index, (key, raw) in enumerate(zip(REFERENTS[number], paragraphs), 1):
        match = re.match(r"\*\*(.+?)\.\*\*\s*(.*)", raw)
        display = match.group(1) if match else PORTRAIT_NAMES[key]
        body = match.group(2) if match else raw
        source = portrait_source(key)
        if source:
            target = assets / f"referent-{key}{source.suffix.lower()}"
            shutil.copy2(source, target)
            visual = f'<img src="assets/{target.name}" alt="Retrato documental de {html.escape(PORTRAIT_NAMES[key])}">'
            status = "verified_local_portrait"
        else:
            target = None
            visual = f'<div class="portrait-unavailable" role="img" aria-label="Retrato no reproducido por falta de una fuente con derechos verificados"><span>{initials(PORTRAIT_NAMES[key])}</span></div>'
            status = "portrait_withheld_pending_rights"
        cards.append(
            f'<article class="contributor"><div class="portrait-frame">{visual}</div><b>{index:02d}</b>'
            f'<h3>{html.escape(display)}</h3><p>{base.inline(body)}</p></article>'
        )
        records.append({
            "key": key,
            "name": PORTRAIT_NAMES[key],
            "file": f"assets/{target.name}" if target else "",
            "sha256": sha(target) if target else "",
            "rights_status": status,
        })
    page = (
        f'<section class="front-page authors-page" id="referentes"><header><span>METSI · FCE-UBA</span>'
        f'<h2>Referentes</h2><p>Seis voces para ampliar, contrastar y discutir N{number:02d}.</p></header>'
        f'<div class="contributors-grid">{"".join(cards)}</div>'
        f'<blockquote>N{number:02d} no resume estas fuentes ni las convierte en receta. Las pone en tensión para construir juicio profesional.</blockquote></section>'
    )
    return page, records


def diagram_svg(number: int, index: int, title: str, labels: list[str], target: Path) -> dict:
    width, height = 1600, 760
    cols = len(labels)
    gap = 28
    cell = (width - 120 - gap * (cols - 1)) / cols
    nodes = []
    edges = []
    for i, label in enumerate(labels):
        x = 60 + i * (cell + gap)
        y = 255 + (45 if i % 2 else 0)
        nodes.append(
            f'<g><rect x="{x:.1f}" y="{y}" width="{cell:.1f}" height="245" rx="8" fill="{"#E3E6E4" if i % 2 else "#FAFAF8"}" stroke="#242523" stroke-width="2"/>'
            f'<text x="{x + 22:.1f}" y="{y + 50}" font-family="Avenir,Arial,sans-serif" font-size="19" font-weight="700" letter-spacing="2">{i+1:02d}</text>'
            f'<text x="{x + 22:.1f}" y="{y + 116}" font-family="Didot,Georgia,serif" font-size="28">{html.escape(label)}</text>'
            f'<circle cx="{x + cell - 23:.1f}" cy="{y + 23}" r="8" fill="#CFFF00"/></g>'
        )
        if i:
            x1 = 60 + (i - 1) * (cell + gap) + cell
            x2 = x
            edges.append(f'<path d="M{x1:.1f} {y+122} H{x2:.1f}" stroke="#333" stroke-width="3" marker-end="url(#a)"/>')
    claim = f"{title}: la representación conecta {', '.join(labels).lower()} para sostener una decisión revisable."
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="t d"><title id="t">{html.escape(title)}</title><desc id="d">{html.escape(claim)}</desc><rect width="1600" height="760" fill="#F8F7F3"/><defs><marker id="a" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#333"/></marker></defs><path d="M60 106H1540" stroke="#232422" stroke-width="3"/><path d="M60 76h155l-18 22H42z" fill="#CFFF00"/><text x="60" y="164" font-family="Didot,Georgia,serif" font-size="54">{html.escape(title)}</text>{''.join(edges)}{''.join(nodes)}<text x="60" y="690" font-family="Avenir,Arial,sans-serif" font-size="22" fill="#555">METSI · N{number:02d} · MAPA {index:02d}</text></svg>'''
    target.write_text(svg, encoding="utf-8")
    return {"file": f"diagrams/{target.name}", "title": title, "labels": labels, "claim": claim, "sha256": sha(target)}


def route_for(number: int, index: int, title: str) -> str:
    if index <= 5:
        return "PROBLEMA"
    if (number >= 17 and index == 6) or title.startswith("Movimiento 1"):
        return "DISTINCIONES"
    if title.startswith("Movimiento 2"):
        return "DECISIONES"
    if title.startswith("Movimiento 3"):
        return "PRUEBA"
    if index <= 12:
        return "TRANSFERENCIA"
    return "PREPARACIÓN"


def icon_strip(section: base.Section) -> str:
    labels = [line[4:].strip() for line in section.lines if line.startswith("### ")][:8]
    items = []
    for index, label in enumerate(labels, 1):
        items.append(f'<div><svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="18"/><path d="M13 24h22M24 13v22"/></svg><span>{html.escape(base.sentence(label, 42))}</span></div>')
    return f'<aside class="icon-strip" aria-label="Ocho distinciones de la lectura">{"".join(items)}</aside>'


def build(number: int) -> dict:
    source = SOURCES[number]
    title, all_sections = base.parse_source(source)
    out = ROOT / f"N{number:02d}-v1-editorial"
    assets, diagrams, output, source_dir = (out / "assets", out / "diagrams", out / "output", out / "source")
    for folder in (assets, diagrams, output, source_dir):
        folder.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, source_dir / source.name)
    shutil.copy2(MATCHES, assets / "matches-close.png")
    cover = assets / "cover-source-premium-bw-v1.png"
    if not cover.is_file():
        raise FileNotFoundError(cover)
    for name in ("pause-01.png", "pause-02.png"):
        if not (assets / name).is_file():
            raise FileNotFoundError(assets / name)

    referents_section = next(s for s in all_sections if s.title == "Referentes")
    referents_page, portrait_records = build_referents(number, referents_section, assets)
    sections = [s for s in all_sections if s.title != "Referentes"]
    references = base.references(all_sections)
    thesis_section = next(s for s in sections if s.title == "Tesis")
    thesis = base.first_paragraph(thesis_section)

    diagram_records = []
    for index, (diagram_title, labels) in enumerate(DIAGRAMS[number], 1):
        diagram_records.append(diagram_svg(number, index, diagram_title, labels, diagrams / f"N{number:02d}-mapa-{index:02d}.svg"))

    entries: list[dict] = []
    title_id = base.source_block(entries, f"N{number:02d}-h1", "heading-1", clean_title(number, title))
    body_chunks: list[str] = []
    rendered_section = 0
    diagram_cursor = 0
    first_pause_after = 1 if number >= 21 else 5
    pause_map = {
        first_pause_after: ("pause-01.png", base.sentence(thesis, 170), PHOTO_ALTS[number][1]),
        11: ("pause-02.png", "", PHOTO_ALTS[number][2]),
    }
    second_quote_section = next((s for s in sections if s.title == "Límites y tensiones"), thesis_section)
    pause_map[11] = ("pause-02.png", base.sentence(base.first_paragraph(second_quote_section), 170), PHOTO_ALTS[number][2])

    for index, section in enumerate(sections, 1):
        rendered_section += 1
        prefix = f"N{number:02d}-s{rendered_section:02d}"
        heading_id = base.source_block(entries, f"{prefix}-h2", "heading-2", section.title)
        section_body = base.render_markdown(section.lines, prefix, entries)
        if number >= 17:
            section_body = section_body.replace("</ol><ol>", "").replace("</ul><ul>", "")
        section_body = re.sub(r"\bHH-(\d+)\b", r'<span class="identifier">HH-\1</span>', section_body)
        classes = base.section_classes(number, rendered_section, section.title)
        if index == 1:
            classes += ["block-c-question"]
        if section.title.startswith("Movimiento"):
            classes += ["block-c-movement", "two-column"]
        if section.title == "Síntesis":
            classes += ["two-column", "block-c-synthesis"]
        if section.title == "Referencias base":
            classes += ["block-c-references"]
        if section.title.startswith("De N") or section.title == "Después de N36":
            classes += ["block-c-handoff"]
        marker = (
            f'<div class="section-marker"><span>{rendered_section:02d}</span>'
            f'<b>METSI · N{number:02d} <em>{route_for(number, index, section.title)}</em></b></div>'
        )
        extra = ""
        if section.title == "Tesis":
            extra += icon_strip(next(s for s in sections if s.title.startswith("Movimiento 1")))
        if section.title.startswith("Movimiento") and diagram_cursor < 3:
            diagram = diagram_records[diagram_cursor]
            extra += (
                f'<figure class="infographic block-c-infographic"><img src="{diagram["file"]}" alt="{html.escape(diagram["claim"])}">'
                f'<figcaption>{html.escape(diagram["claim"])}</figcaption></figure>'
            )
            diagram_cursor += 1
        section_attrs = ""
        if section.title == "Glosario esencial":
            glossary_entries = sum(1 for line in section.lines if line.strip().startswith("**"))
            glossary_rows = max(1, (glossary_entries + 2) // 3)
            section_attrs = f' style="--glossary-rows:{glossary_rows}"'
        body_chunks.append(
            f'<section class="{" ".join(dict.fromkeys(classes))}" id="section-{rendered_section:02d}" data-section="{rendered_section:02d}"{section_attrs}>'
            f'<div class="section-heading">{marker}<h2 data-source-id="{heading_id}">{html.escape(section.title)}</h2></div>'
            f'{extra}<div class="section-body">{section_body}</div></section>'
        )
        if index in pause_map:
            file, quote, alt = pause_map[index]
            body_chunks.append(
                f'</article><section class="full-bleed full-bleed-quote block-c-pause"><img src="assets/{file}" alt="{html.escape(alt)}">'
                f'<p>{html.escape(quote)}</p></section><article class="reading">'
            )

    visible_sections = [s for s in sections if s.title != "Referencias base"]
    content_items = ['<li class="contents-unnumbered"><b>•</b><span>Referentes <small>SIN NUM.</small></span></li>']
    for index, section in enumerate(visible_sections, 1):
        content_items.append(f'<li><b>{index:02d}</b><span>{html.escape(section.title)}</span></li>')
    content_items.append('<li class="contents-unnumbered"><b>•</b><span>Referencias base <small>SIN NUM.</small></span></li>')
    contents = (
        f'<section class="front-page contents-page contents-page-text-only block-c-contents"><header><span>METSI · N{number:02d}</span>'
        f'<h2>Contenido</h2><p>{html.escape(clean_title(number, title))}</p>'
        f'<p class="contents-route"><b>Ruta de lectura:</b> problema, distinciones, decisiones, prueba, transferencia y preparación.</p></header>'
        f'<div class="contents-layout"><ol>{"".join(content_items)}</ol></div>'
        f'<p class="contents-sinnum-note"><b>Nota.</b> SIN NUM. identifica aparatos de orientación y referencia.</p></section>'
    )
    closing_alt = "Diez fósforos dispuestos en secuencia vertical, desde intactos hasta consumidos y convertidos en ceniza."
    closing_caption = "La secuencia vuelve visible que toda intervención consume recursos, deja huellas y necesita un criterio de cierre."
    html_text = (
        '<!doctype html><html lang="es-AR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<meta name="description" content="Lectura previa METSI N{number:02d}, FCE UBA"><title>{html.escape(title)}</title>'
        '<link rel="stylesheet" href="magazine.css"></head>'
        f'<body class="premium-magazine document-n{number:02d} block-c"><main>'
        f'{base.cover_html(number, title, thesis, cover.name, title_id)}{contents}{referents_page}'
        f'<article class="reading">{"".join(body_chunks)}</article>'
        f'<section class="full-bleed closing-image"><img src="assets/matches-close.png" alt="{html.escape(closing_alt)}">'
        f'<figcaption>{html.escape(closing_caption)}</figcaption></section></main></body></html>'
    )
    (out / "index.html").write_text(html_text, encoding="utf-8")

    stable_css = (ROOT / "N10-v9-final" / "magazine.css").read_text(encoding="utf-8")
    css = stable_css + "\n\n" + BLOCK_C_CSS
    (out / "magazine.css").write_text(css, encoding="utf-8")

    rendered_ids = re.findall(r'data-source-id="([^"]+)"', html_text)
    source_ids = [entry["source_id"] for entry in entries]
    integrity = {
        "status": "PASS" if sorted(source_ids) == sorted(rendered_ids) and len(rendered_ids) == len(set(rendered_ids)) else "FAIL",
        "source_block_count": len(source_ids),
        "rendered_source_id_count": len(rendered_ids),
        "missing_source_ids": sorted(set(source_ids) - set(rendered_ids)),
        "unexpected_source_ids": sorted(set(rendered_ids) - set(source_ids)),
    }
    (out / "source-manifest.json").write_text(json.dumps({"document": f"N{number:02d}", "source": f"source/{source.name}", "eligible_blocks": entries}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "integrity-report.json").write_text(json.dumps(integrity, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "number": number,
        "title": title,
        "module": "Integrar, defender, transferir y seguir aprendiendo" if number >= 34 else "Incorporar IA sin delegar el juicio" if number >= 31 else "Sostener la promesa en operación" if number >= 26 else "Pasar de entregar cosas a gobernar capacidades" if number >= 21 else "Diseñar una estrategia situada" if number >= 17 else "Modelar sólo lo que ayuda a decidir",
        "source": f"source/{source.name}",
        "source_sha256": sha(source),
        "source_words": len(re.findall(r"\b[\wÁÉÍÓÚÜÑáéíóúüñ'-]+\b", source.read_text(encoding="utf-8"))),
        "content_audit": "canonical-v1-pass",
        "cover": {"file": cover.name, "source": f"assets/{cover.name}", "sha256": sha(cover), "alt": PHOTO_ALTS[number][0], "photographic_origin": "native_black_and_white", "render_treatment": "no_grayscale_conversion"},
        "internal_images": ["pause-01.png", "pause-02.png"],
        "image_manifest": [
            {"file": f"assets/pause-01.png", "sha256": sha(assets / "pause-01.png"), "alt": PHOTO_ALTS[number][1], "role": "full_page_pause", "rights_status": "project_bound_generated_media"},
            {"file": f"assets/pause-02.png", "sha256": sha(assets / "pause-02.png"), "alt": PHOTO_ALTS[number][2], "role": "full_page_pause", "rights_status": "project_bound_generated_media"},
        ],
        "portrait_references": portrait_records,
        "diagrams": diagram_records,
        "quotes": [pause_map[first_pause_after][1], pause_map[11][1]],
        "references": references,
        "closing": {"file": "matches-close.png", "sha256": sha(assets / "matches-close.png"), "alt": closing_alt, "caption": closing_caption, "folio": True, "footer": True},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "document.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (diagrams / "content-manifest.json").write_text(json.dumps({"document": f"N{number:02d}", "diagrams": diagram_records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


BLOCK_C_CSS = r'''
/* METSI Block C · editorial source system */
.block-c .collection-cover>img,.block-c .full-bleed-quote>img{filter:none!important;opacity:1}
.block-c .collection-cover .cover-shade{inset:0;width:100%;height:100%;background:linear-gradient(180deg,rgba(5,7,6,.24) 0,rgba(5,7,6,.02) 31%,rgba(5,7,6,.03) 58%,rgba(8,9,8,.62) 100%)}
.block-c .collection-masthead{top:16mm}
.block-c .cover-title h1{max-width:139mm;font-size:34pt;line-height:.96}
.block-c-contents .contents-layout{display:block;height:208mm;margin-top:5mm}
.block-c-contents .contents-layout ol{columns:2;column-count:2;column-gap:13mm}
.block-c-contents .contents-layout li{grid-template-columns:8mm 1fr;padding:2.15mm 0;font-size:8.4pt;line-height:1.19;break-inside:avoid}
.block-c-contents .contents-sinnum-note{position:absolute;left:18mm;right:18mm;bottom:18mm;margin:0;padding-top:2mm;border-top:.2mm solid #BFC1BD;font:6.7pt/1.25 Avenir,sans-serif;color:#5B5D58}
.block-c .authors-page .contributors-grid{grid-template-columns:repeat(3,1fr);gap:5mm}
.block-c .authors-page .contributor{min-height:79mm}
.block-c .portrait-frame{width:100%;height:37mm;margin-bottom:3mm;overflow:hidden;background:#D8DAD7}
.block-c .portrait-frame img{display:block;width:100%;height:100%;object-fit:cover;object-position:50% 28%;filter:grayscale(1) contrast(1.03)}
.block-c .portrait-unavailable{display:grid;place-items:center;width:100%;height:100%;background:linear-gradient(135deg,#ECEDE9,#C7CAC6);color:#555;font:400 28pt/1 Didot,serif}
.block-c .contributors-grid .contributor p{font-size:7.2pt;line-height:1.3}
.block-c .reading-section[data-section="01"]{page:fullbleed;position:relative;box-sizing:border-box;width:210mm;height:297mm;margin:0;padding:24mm;display:flex;flex-direction:column;justify-content:flex-end;background:#191919;color:#F7F6F2;border:0;break-before:page;page-break-before:always;break-after:page;page-break-after:always}
.block-c .reading-section[data-section="01"]::before{content:"";position:absolute;left:24mm;top:24mm;width:24mm;height:3.2mm;background:#CFFF00;clip-path:polygon(10% 0,100% 0,90% 100%,0 100%)}
.block-c .reading-section[data-section="01"] .section-marker{color:#CFFF00}
.block-c .reading-section[data-section="01"] h2{color:#F7F6F2;font-size:18pt}
.block-c .reading-section[data-section="01"] .section-body{max-width:155mm}
.block-c .reading-section[data-section="01"] .section-body p{margin:0;color:#F7F6F2;font:400 28pt/1.08 Didot,"Bodoni 72",serif;letter-spacing:-.018em}
.block-c .opening-section:nth-child(2) .section-body>p:first-child::first-letter,
.block-c .layout-section-opener .section-body>p:first-child::first-letter{float:none;margin:0;color:inherit;font:inherit}
.block-c .reading-section[data-section="02"] .section-body{font-size:10.1pt;line-height:1.35}
.block-c .reading-section[data-section="02"] .section-body p{margin-bottom:2.5mm;orphans:4;widows:4}
.block-c.document-n21 .reading-section[data-section="02"],.block-c.document-n22 .reading-section[data-section="02"],.block-c.document-n23 .reading-section[data-section="02"],.block-c.document-n24 .reading-section[data-section="02"],.block-c.document-n25 .reading-section[data-section="02"],.block-c.document-n26 .reading-section[data-section="02"],.block-c.document-n27 .reading-section[data-section="02"],.block-c.document-n28 .reading-section[data-section="02"],.block-c.document-n29 .reading-section[data-section="02"],.block-c.document-n30 .reading-section[data-section="02"]{min-height:230mm;box-sizing:border-box;padding:16mm 14mm;background:#F0F1EE;display:flex;flex-direction:column;justify-content:center;border-left:1.5mm solid #CFFF00}
.block-c .section-marker b{display:inline-flex;align-items:baseline;gap:2.2mm}
.block-c .section-marker b em{font-style:normal;font-size:5.7pt;font-weight:600;letter-spacing:.12em;opacity:.72}
.block-c .identifier{white-space:nowrap}
.block-c .block-c-movement{break-before:auto;page-break-before:auto;padding:0;background:#FAFAF8!important;border-left:0!important}
.block-c .block-c-movement .section-body h3,.block-c .block-c-movement .section-body h4{break-after:avoid-column;page-break-after:avoid}
.block-c .block-c-movement .section-body h3{margin:5mm 0 2mm;padding-top:2.5mm;border-top:.3mm solid #202020}
.block-c .block-c-movement .section-body table,.block-c .block-c-movement .section-body ul,.block-c .block-c-movement .section-body ol{break-inside:avoid-page}
.block-c .block-c-handoff{break-inside:avoid-page;background:#E3E6E4;padding:6mm;border-left:1.5mm solid #CFFF00}
.block-c .block-c-synthesis .section-body{columns:2;column-count:2;column-gap:8mm;column-rule:.2mm solid #C5C7C5}
.block-c .block-c-references{break-before:page;page-break-before:always;padding-left:0!important;border-left:0!important;background:#FAFAF8!important}
.block-c .block-c-references .section-body{columns:auto!important;display:block!important;font:9.25pt/1.34 Avenir,sans-serif}
.block-c .block-c-references .section-body ul{columns:2;column-count:2;column-gap:9mm;list-style:none;margin:0;padding:0}
.block-c .block-c-references li{break-inside:avoid;margin:0 0 3.2mm;padding:0;overflow-wrap:normal;word-break:normal;hyphens:none}
.block-c .block-c-references .url-segment{white-space:nowrap}
.block-c.document-n13 .block-c-references .section-body ul,
.block-c.document-n14 .block-c-references .section-body ul,
.block-c.document-n15 .block-c-references .section-body ul,
.block-c.document-n16 .block-c-references .section-body ul,
.block-c.document-n17 .block-c-references .section-body ul,
.block-c.document-n18 .block-c-references .section-body ul,
.block-c.document-n19 .block-c-references .section-body ul,
.block-c.document-n20 .block-c-references .section-body ul,
.block-c.document-n21 .block-c-references .section-body ul,
.block-c.document-n22 .block-c-references .section-body ul,
.block-c.document-n23 .block-c-references .section-body ul,
.block-c.document-n24 .block-c-references .section-body ul,
.block-c.document-n25 .block-c-references .section-body ul,
.block-c.document-n26 .block-c-references .section-body ul,
.block-c.document-n27 .block-c-references .section-body ul,
.block-c.document-n28 .block-c-references .section-body ul,
.block-c.document-n29 .block-c-references .section-body ul,
.block-c.document-n30 .block-c-references .section-body ul{columns:1;column-count:1;max-width:155mm}
.block-c.document-n13 .block-c-references li,
.block-c.document-n14 .block-c-references li,
.block-c.document-n15 .block-c-references li,
.block-c.document-n16 .block-c-references li,
.block-c.document-n17 .block-c-references li,
.block-c.document-n18 .block-c-references li,
.block-c.document-n19 .block-c-references li,
.block-c.document-n20 .block-c-references li,
.block-c.document-n21 .block-c-references li,
.block-c.document-n22 .block-c-references li,
.block-c.document-n23 .block-c-references li,
.block-c.document-n24 .block-c-references li,
.block-c.document-n25 .block-c-references li,
.block-c.document-n26 .block-c-references li,
.block-c.document-n27 .block-c-references li,
.block-c.document-n28 .block-c-references li,
.block-c.document-n29 .block-c-references li,
.block-c.document-n30 .block-c-references li{margin-bottom:3.8mm}
.block-c.document-n13 .reading-section[data-section="11"],
.block-c.document-n16 .reading-section[data-section="11"]{break-before:page;page-break-before:always;break-inside:avoid-page;page-break-inside:avoid;min-height:220mm;padding:12mm;background:#E3E6E4;display:flex;flex-direction:column;justify-content:center;border-left:1.5mm solid #CFFF00}
.block-c .glossary-two-column{break-before:page;page-break-before:always;min-height:246mm;padding:7mm;background:#F0F1EE;border-left:1.5mm solid #CFFF00}
.block-c .glossary-two-column .section-body{columns:auto!important;column-count:auto!important;column-rule:none!important;display:grid;grid-auto-flow:column;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(var(--glossary-rows),minmax(0,1fr));gap:0 6mm;min-height:145mm;font-size:9.2pt;line-height:1.2}
.block-c .glossary-two-column .section-body p{margin:0;padding:3mm 0 2mm;border-top:.2mm solid #AEB1AD;break-inside:avoid;orphans:3;widows:3}
.block-c .questions{break-before:page;page-break-before:always;padding:7mm;background:#E3E6E4}
.block-c .questions .section-body{font-size:11.7pt;line-height:1.42}
.block-c .questions .section-body ol{display:grid;grid-template-columns:1fr 1fr;grid-auto-flow:column;grid-template-rows:repeat(3,1fr);gap:8mm 12mm;min-height:145mm;columns:auto;margin:0;padding-left:7mm}
.block-c .questions .section-body li{break-inside:avoid;margin:0}
.block-c .questions .section-body>p:last-child{margin-top:7mm;padding:4mm;border-top:.6mm solid #171917;border-left:1.5mm solid #CFFF00;background:#FAFAF8;font:8.8pt/1.3 Avenir,sans-serif}
.block-c .pill-summary{break-inside:avoid-page;padding:6mm 7mm;background:#E3E6E4}
.block-c .icon-strip{display:grid;grid-template-columns:repeat(4,1fr);gap:4mm;margin:6mm 0;padding:5mm 0;border-top:.25mm solid #888;border-bottom:.25mm solid #888;break-inside:avoid-page}
.block-c .icon-strip div{display:grid;grid-template-columns:12mm 1fr;align-items:center;gap:2mm;font:7.1pt/1.22 Avenir,sans-serif;text-transform:uppercase;letter-spacing:.04em}
.block-c .icon-strip svg{width:10mm;height:10mm;fill:none;stroke:#202020;stroke-width:1.8}
.block-c .block-c-infographic{column-span:all;width:100%;margin:5mm 0 6mm;break-inside:avoid-page}
.block-c .block-c-infographic img{width:100%;max-height:82mm;object-fit:contain;filter:none}
.block-c .block-c-infographic figcaption{font:7.2pt/1.3 Avenir,sans-serif;color:#5A5A56}
.block-c .block-c-pause::after{background:linear-gradient(180deg,rgba(0,0,0,0) 50%,rgba(0,0,0,.54) 100%)}
.block-c .block-c-pause p{font-size:24pt;max-width:160mm}
.block-c .closing-image>img{filter:none}
.block-c.document-n11 .reading-section[data-section="09"]{break-before:page;page-break-before:always}
.block-c.document-n16 [data-section="05"].block-c-handoff{min-height:246mm;display:flex;flex-direction:column;justify-content:center}
.block-c.document-n17 article.reading + .block-c-pause{break-before:auto;page-break-before:auto}
.block-c.document-n17 .questions,.block-c.document-n18 .questions,.block-c.document-n19 .questions,.block-c.document-n20 .questions,
.block-c.document-n21 .questions,.block-c.document-n22 .questions,.block-c.document-n23 .questions,.block-c.document-n24 .questions,.block-c.document-n25 .questions,.block-c.document-n26 .questions,.block-c.document-n27 .questions,.block-c.document-n28 .questions,.block-c.document-n29 .questions,.block-c.document-n30 .questions{min-height:230mm;box-sizing:border-box;break-inside:avoid-page;page-break-inside:avoid}
.block-c.document-n22 .reading-section[data-section="11"],
.block-c.document-n23 .reading-section[data-section="11"],
.block-c.document-n24 .reading-section[data-section="11"],
.block-c.document-n25 .reading-section[data-section="11"]{min-height:180mm;box-sizing:border-box;display:flex;flex-direction:column;justify-content:center}
.block-c.document-n26 .reading-section[data-section="11"],
.block-c.document-n27 .reading-section[data-section="11"],
.block-c.document-n28 .reading-section[data-section="11"],
.block-c.document-n29 .reading-section[data-section="11"],
.block-c.document-n30 .reading-section[data-section="11"]{min-height:120mm;box-sizing:border-box;display:flex;flex-direction:column;justify-content:center}
.block-c.document-n21 .reading-section[data-section="11"]{min-height:120mm;box-sizing:border-box;display:flex;flex-direction:column;justify-content:center}
.block-c.document-n21 .pill-summary,.block-c.document-n22 .pill-summary,.block-c.document-n23 .pill-summary,.block-c.document-n24 .pill-summary,.block-c.document-n25 .pill-summary,.block-c.document-n26 .pill-summary,.block-c.document-n27 .pill-summary,.block-c.document-n28 .pill-summary,.block-c.document-n29 .pill-summary,.block-c.document-n30 .pill-summary{min-height:230mm;box-sizing:border-box;display:flex;flex-direction:column;justify-content:center;padding:16mm 14mm}
.block-c.document-n21 .pill-summary .section-body ol,.block-c.document-n22 .pill-summary .section-body ol,.block-c.document-n23 .pill-summary .section-body ol,.block-c.document-n24 .pill-summary .section-body ol,.block-c.document-n25 .pill-summary .section-body ol,.block-c.document-n26 .pill-summary .section-body ol,.block-c.document-n27 .pill-summary .section-body ol,.block-c.document-n28 .pill-summary .section-body ol,.block-c.document-n29 .pill-summary .section-body ol,.block-c.document-n30 .pill-summary .section-body ol{columns:auto;display:grid;grid-template-columns:1fr;gap:6mm;margin:7mm 0 0;padding-left:8mm}
.block-c.document-n21 .pill-summary .section-body li,.block-c.document-n22 .pill-summary .section-body li,.block-c.document-n23 .pill-summary .section-body li,.block-c.document-n24 .pill-summary .section-body li,.block-c.document-n25 .pill-summary .section-body li,.block-c.document-n26 .pill-summary .section-body li,.block-c.document-n27 .pill-summary .section-body li,.block-c.document-n28 .pill-summary .section-body li,.block-c.document-n29 .pill-summary .section-body li,.block-c.document-n30 .pill-summary .section-body li{font-size:12pt;line-height:1.38;margin:0;break-inside:avoid}
.block-c.document-n27 .reading-section[data-section="06"]{break-inside:avoid-page;page-break-inside:avoid}
.block-c.document-n27 .reading-section[data-section="06"] .section-body{columns:auto;column-count:auto;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:2.2mm 7.5mm;font-size:9.15pt;line-height:1.23}
.block-c.document-n27 .reading-section[data-section="06"] .section-body p{margin:0;break-inside:avoid}
.block-c:is(.document-n31,.document-n32,.document-n33,.document-n34,.document-n35,.document-n36) .reading-section[data-section="02"]{height:246mm;min-height:246mm;box-sizing:border-box;padding:16mm 14mm;background:#F0F1EE;display:flex;flex-direction:column;justify-content:center;border-left:1.5mm solid #CFFF00;break-inside:avoid-page;page-break-inside:avoid}
.block-c:is(.document-n31,.document-n32,.document-n33,.document-n34,.document-n35,.document-n36) .block-c-references{min-height:246mm;box-sizing:border-box;padding:13mm 12mm!important;background:#F0F1EE!important;display:flex;flex-direction:column;justify-content:center}
.block-c:is(.document-n31,.document-n32,.document-n33,.document-n34,.document-n35,.document-n36) .block-c-references .section-body ul{columns:2;column-count:2;column-gap:10mm;max-width:none}
.block-c:is(.document-n31,.document-n32,.document-n33,.document-n34,.document-n35,.document-n36) .block-c-references li{margin-bottom:5mm;font-size:9pt;line-height:1.38}
.block-c.document-n31 .block-c-references .section-body ul{columns:1;column-count:1;max-width:155mm}
.block-c.document-n31 .block-c-references li{margin-bottom:3.8mm;font-size:9.25pt;line-height:1.34}
.block-c:is(.document-n31,.document-n32,.document-n33,.document-n34,.document-n35,.document-n36) .questions{min-height:230mm;box-sizing:border-box;break-inside:avoid-page;page-break-inside:avoid}
.block-c:is(.document-n31,.document-n32,.document-n33,.document-n34,.document-n35,.document-n36) .pill-summary{min-height:230mm;box-sizing:border-box;display:flex;flex-direction:column;justify-content:center;padding:16mm 14mm}
.block-c:is(.document-n31,.document-n32,.document-n33,.document-n34,.document-n35,.document-n36) .pill-summary .section-body ol{columns:auto;display:grid;grid-template-columns:1fr;gap:6mm;margin:7mm 0 0;padding-left:8mm}
.block-c:is(.document-n31,.document-n32,.document-n33,.document-n34,.document-n35,.document-n36) .pill-summary .section-body li{font-size:12pt;line-height:1.38;margin:0;break-inside:avoid}
.block-c:is(.document-n31,.document-n32,.document-n33,.document-n34,.document-n35,.document-n36) .reading-section[data-section="11"]{min-height:230mm;box-sizing:border-box;display:flex;flex-direction:column;justify-content:center;padding:16mm 14mm;background:#E3E6E4;border-left:1.5mm solid #CFFF00}
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=11)
    parser.add_argument("--end", type=int, default=16)
    args = parser.parse_args()
    if args.start < 11 or args.end > 36 or args.start > args.end:
        raise ValueError("El generador cubre N11–N36")
    for number in range(args.start, args.end + 1):
        manifest = build(number)
        print(f"BUILT N{number:02d} {manifest['source_words']} words")


if __name__ == "__main__":
    main()
