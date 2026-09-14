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
import math
import re
import shutil
import textwrap
import unicodedata
from pathlib import Path

import build_collection as base
from PIL import Image, ImageEnhance, ImageOps


ROOT = Path(__file__).resolve().parent
PORTRAIT_ROOT = ROOT / "assets" / "portraits-block-c"
SHARED_PORTRAITS = ROOT / "assets" / "portraits"
SUPPORT_ROOT = ROOT / "assets" / "rebuild-support"
APPROVED_INFOGRAPHIC_ROOT = ROOT / "editorial-standard" / "approved-infographics"
PACKAGE_VERSION = 9
BASELINE_VERSION = 8
ACADEMIC_REVISION_MANIFEST = ROOT / "academic-content-revision-manifest-n11-n36.json"
MATCHES = ROOT / "N10-v9-final" / "assets" / "matches-close.png"
HOTEL_HORIZONTE = SUPPORT_ROOT / "hotel-horizonte-canonical-v2.png"
SPECIAL_COVERS = {
    34: SUPPORT_ROOT / "N34-cover-native-bw-v2.png",
}

APPROVED_INFOGRAPHICS = {
    11: {
        "file": "N11-expediente-sosten.svg",
        "family": "assembly",
        "caption": (
            "La evidencia se vuelve defendible cuando el expediente conserva "
            "afirmación, rastro, límite y relación con una decisión."
        ),
    },
    12: {
        "file": "N12-transicion-verificable.svg",
        "family": "transition-gate",
        "caption": (
            "La transición separa lo solicitado, lo ocurrido y lo vigente, y conserva "
            "autoridad, evidencia y reparación."
        ),
    },
    13: {
        "file": "N13-convergencia-bajo-desorden.svg",
        "family": "convergence-gate",
        "caption": (
            "La convergencia conserva la identidad de la intención, protege una "
            "invariante y repara divergencias sin borrar la historia."
        ),
    },
    14: {
        "file": "N14-flujo-real-y-excepciones.svg",
        "family": "flow-map",
        "caption": (
            "El tiempo de servicio reúne trabajo, espera, handoffs y excepciones "
            "entre el evento inicial y un cierre verificable."
        ),
    },
    15: {
        "file": "N15-pregunta-elige-vista.svg",
        "family": "selection-gate",
        "caption": (
            "La pregunta y la decisión seleccionan una cartera mínima de vistas con "
            "audiencia, evidencia, costo y vigencia explícitos."
        ),
    },
    16: {
        "file": "N16-contradiccion-clasificada.svg",
        "family": "coherence-register",
        "caption": (
            "La coherencia se prueba sobre un mismo episodio, clasifica la diferencia "
            "antes de corregir y gobierna su tratamiento a través del cambio."
        ),
    },
    17: {
        "file": "N17-logicas-por-decision.svg",
        "family": "strategy-portfolio",
        "caption": (
            "Una estrategia situada asigna una lógica distinta a cada decisión y "
            "aumenta compromiso sólo cuando la evidencia atraviesa la puerta."
        ),
    },
    18: {
        "file": "N18-capacidad-antes-que-pieza.svg",
        "family": "legacy-decision-gate",
        "caption": (
            "La transición conserva capacidades, derechos y evidencia, pero puede "
            "adaptar o retirar las piezas históricas que los implementaban."
        ),
    },
    19: {
        "file": "N19-alternativas-misma-prueba.svg",
        "family": "realization-field",
        "caption": (
            "Configurar, integrar, construir, contratar, operar manualmente y no "
            "automatizar se comparan contra la misma capacidad, falla, reparación y salida."
        ),
    },
    20: {
        "file": "N20-estrategia-con-puertas.svg",
        "family": "situated-strategy-gates",
        "caption": (
            "La estrategia selecciona prácticas por función, vincula cada puerta con "
            "evidencia y autoridad, y conserva salidas efectivas antes de transferir la capacidad."
        ),
    },
    21: {
        "file": "N21-cuatro-gobiernos-una-capacidad.svg",
        "family": "object-governance-map",
        "caption": (
            "Proyecto, producto, servicio y plataforma conviven alrededor de una misma "
            "capacidad, pero exigen horizontes, evidencia, autoridad y cierres diferentes."
        ),
    },
    22: {
        "file": "N22-hipotesis-que-puede-perder.svg",
        "family": "refutable-hypothesis-dossier",
        "caption": (
            "La hipótesis explicita una explicación rival, exige evidencia acumulada "
            "para continuar y deja que una salvaguarda crítica detenga la expansión."
        ),
    },
    23: {
        "file": "N23-corte-conserva-capacidad.svg",
        "family": "capacity-cross-section",
        "caption": (
            "El corte vertical limita población y variedad, pero conserva una llegada completa, "
            "su operación, su reparación y la evidencia que habilita el próximo incremento."
        ),
    },
    24: {
        "file": "N24-prioridad-hace-visible-renuncia.svg",
        "family": "renunciation-register",
        "caption": (
            "La cartera protege límites antes de comparar, restringe el trabajo activo y "
            "conserva quién espera, qué consecuencia se acepta y cuándo se revisa."
        ),
    },
    25: {
        "file": "N25-flujo-conserva-identidad.svg",
        "family": "temporal-flow-map",
        "caption": (
            "La unidad conserva identidad entre demanda y capacidad en uso, hace visibles "
            "trabajo, espera y colas, y cierra el feedback sólo cuando cambia una decisión."
        ),
    },
    26: {
        "file": "N26-promesa-entre-capacidades.svg",
        "family": "service-ecosystem-map",
        "caption": (
            "La promesa conecta capacidades internas y participantes autónomos mediante "
            "fronteras de confianza, contingencia y responsabilidad de punta a punta."
        ),
    },
    27: {
        "file": "N27-contrato-cuatro-capas.svg",
        "family": "layered-contract-dossier",
        "caption": (
            "Un intercambio sólo se vuelve contrato cuando forma, significado, tiempo y "
            "operación permiten anticipar la misma consecuencia y una reparación practicable."
        ),
    },
    28: {
        "file": "N28-calidad-por-escenario.svg",
        "family": "risk-evidence-dossier",
        "caption": (
            "El promedio describe el conjunto, pero sólo escenarios con población, riesgo, "
            "umbral y evidencia permiten autorizar un alcance de calidad defendible."
        ),
    },
    29: {
        "file": "N29-recuperacion-promesa-completa.svg",
        "family": "release-recovery-dossier",
        "caption": (
            "La unidad de liberación reúne artefacto, configuración, infraestructura, datos, "
            "terceros y operación; la salida se elige según los efectos que ya ocurrieron."
        ),
    },
    30: {
        "file": "N30-senales-promesa-y-aprendizaje.svg",
        "family": "observability-learning-map",
        "caption": (
            "Tres tableros saludables pueden ocultar una fila real; la observación se vuelve "
            "operable cuando conecta escalas de señal, SLI, SLO, autoridad y aprendizaje."
        ),
    },
    31: {
        "file": "N31-capacidad-antes-que-ia.svg",
        "family": "ai-pertinence-dossier",
        "caption": (
            "El recorrido asigna reglas, búsqueda, predicción, generación y agencia a pasos "
            "concretos, los compara con una línea de base y limita la acción mediante una puerta."
        ),
    },
    32: {
        "file": "N32-permiso-por-tarea.svg",
        "family": "autonomy-evidence-dossier",
        "caption": (
            "El promedio se confronta con cobertura, severidad, desigualdad, robustez y "
            "supervisión real antes de asignar un permiso revisable a cada tarea."
        ),
    },
    33: {
        "file": "N33-registro-vivo-gobierno.svg",
        "family": "living-governance-register",
        "caption": (
            "El registro mantiene unido propósito, configuración, autoridad, evaluación, "
            "incidentes y salida, y reabre el permiso cuando cambia la frontera."
        ),
    },
    34: {
        "file": "N34-cadena-en-ambos-sentidos-print.png",
        "family": "integrated-evidence-chain",
        "caption": (
            "La cadena se prueba desde la promesa hasta la consecuencia y desde un incidente "
            "hasta la decisión, la evidencia y el encuadre que lo habilitaron."
        ),
    },
    35: {
        "file": "N35-tesis-y-recorridos.svg",
        "family": "defense-transfer-matrix",
        "caption": (
            "La tesis conserva afirmación, evidencia, garantía, límite, objeción y revisión, "
            "mientras cada audiencia recorre esos elementos para una decisión diferente."
        ),
    },
    36: {
        "file": "N36-sorpresa-reabre-practica.svg",
        "family": "reflective-practice-system",
        "caption": (
            "La sorpresa separa el resultado de su explicación y abre cambios en la acción, "
            "la regla, la autoridad o el propio sistema de aprendizaje antes de volver a probar."
        ),
    },
}

# Exceptionally dense maps need an independent reading surface. N34 keeps the
# deferred placement for its unusually dense vertical plate; N11 remains a
# readable thesis companion after its candidate-specific scale correction.
DEFERRED_INFOGRAPHIC_DOCS = {34}

# N11 is the first reconstruction pilot. Colour is reserved for source-relevant
# evidence on a white surface and for one full-page reading pause. Contents and
# recurring apparatus remain neutral, matching the approved N00–N10 language.
PREMIUM_COLOR_OVERRIDES: dict[int, dict[int, Path]] = {
    11: {
        3: SUPPORT_ROOT / "N11-premium-color-03.png",
    },
    12: {
        3: SUPPORT_ROOT / "N12-premium-color-03.png",
    },
    13: {
        3: SUPPORT_ROOT / "N13-premium-color-03.png",
    },
    14: {
        3: SUPPORT_ROOT / "N14-premium-color-03.png",
    },
    15: {
        3: SUPPORT_ROOT / "N15-premium-color-03.png",
    },
    16: {
        3: SUPPORT_ROOT / "N16-premium-color-03.png",
    },
    17: {
        3: SUPPORT_ROOT / "N17-premium-color-03.png",
    },
    18: {
        3: SUPPORT_ROOT / "N18-premium-color-03.png",
    },
    19: {
        3: SUPPORT_ROOT / "N19-premium-color-03.png",
    },
    20: {
        3: SUPPORT_ROOT / "N20-premium-color-03.png",
    },
    21: {
        3: SUPPORT_ROOT / "N21-premium-color-03.png",
    },
    22: {
        3: SUPPORT_ROOT / "N22-premium-color-03.png",
    },
    23: {
        3: SUPPORT_ROOT / "N23-premium-color-03.png",
    },
    24: {
        3: SUPPORT_ROOT / "N24-premium-color-03.png",
    },
    25: {
        3: SUPPORT_ROOT / "N25-premium-color-03.png",
    },
    26: {
        3: SUPPORT_ROOT / "N26-premium-color-03.png",
    },
    27: {
        3: SUPPORT_ROOT / "N27-premium-color-03.png",
    },
    28: {
        3: SUPPORT_ROOT / "N28-premium-color-03.png",
    },
    29: {
        3: SUPPORT_ROOT / "N29-premium-color-03.png",
    },
    30: {
        3: SUPPORT_ROOT / "N30-premium-color-03.png",
    },
    31: {
        3: SUPPORT_ROOT / "N31-premium-color-03.png",
    },
    32: {
        3: SUPPORT_ROOT / "N32-premium-color-03.png",
    },
    33: {
        3: SUPPORT_ROOT / "N33-premium-color-03.png",
    },
    34: {
        3: SUPPORT_ROOT / "N34-premium-color-03.png",
    },
    35: {
        3: SUPPORT_ROOT / "N35-premium-color-03.png",
    },
    36: {
        3: SUPPORT_ROOT / "N36-premium-color-03.png",
    },
}

PREMIUM_PAUSE_OVERRIDES: dict[int, dict[int, Path]] = {
    11: {
        2: SUPPORT_ROOT / "N11-premium-color-01.png",
    },
    12: {
        2: SUPPORT_ROOT / "N12-premium-color-01.png",
    },
    13: {
        2: SUPPORT_ROOT / "N13-premium-color-01.png",
    },
    14: {
        2: SUPPORT_ROOT / "N14-premium-color-01.png",
    },
    15: {
        2: SUPPORT_ROOT / "N15-premium-color-01.png",
    },
    16: {
        2: SUPPORT_ROOT / "N16-premium-color-01.png",
    },
    17: {
        2: SUPPORT_ROOT / "N17-premium-color-01.png",
    },
    18: {
        2: SUPPORT_ROOT / "N18-premium-color-01.png",
    },
    19: {
        2: SUPPORT_ROOT / "N19-premium-color-01.png",
    },
    20: {
        2: SUPPORT_ROOT / "N20-premium-color-01.png",
    },
    21: {
        2: SUPPORT_ROOT / "N21-premium-color-01.png",
    },
    22: {
        2: SUPPORT_ROOT / "N22-premium-color-01.png",
    },
    23: {
        2: SUPPORT_ROOT / "N23-premium-color-01.png",
    },
    24: {
        2: SUPPORT_ROOT / "N24-premium-color-01.png",
    },
    25: {
        2: SUPPORT_ROOT / "N25-premium-color-01.png",
    },
    26: {
        2: SUPPORT_ROOT / "N26-premium-color-01.png",
    },
    27: {
        2: SUPPORT_ROOT / "N27-premium-color-01.png",
    },
    28: {
        2: SUPPORT_ROOT / "N28-premium-color-01.png",
    },
    29: {
        2: SUPPORT_ROOT / "N29-premium-color-01.png",
    },
    30: {
        2: SUPPORT_ROOT / "N30-premium-color-01.png",
    },
    31: {
        2: SUPPORT_ROOT / "N31-premium-color-01.png",
    },
    32: {
        2: SUPPORT_ROOT / "N32-premium-color-01.png",
    },
    33: {
        2: SUPPORT_ROOT / "N33-premium-color-01.png",
    },
    34: {
        2: SUPPORT_ROOT / "N34-premium-color-01.png",
    },
    35: {
        2: SUPPORT_ROOT / "N35-premium-color-01.png",
    },
    36: {
        2: SUPPORT_ROOT / "N36-premium-color-01.png",
    },
}
ALT_TEXT_MATRIX = json.loads(
    (SUPPORT_ROOT / "N11-N36-alt-text-matrix.json").read_text(encoding="utf-8")
)["documents"]
SUPPORT_ALTS = {
    int(key[1:]): [item["alt"] for item in record["panels"]]
    for key, record in ALT_TEXT_MATRIX.items()
}
COVER_ALTS = {
    int(key[1:]): record["cover"]["suggested_alt"]
    for key, record in ALT_TEXT_MATRIX.items()
}

PORTRAIT_ALIASES = {
    "agile-alliance": "agile-manifesto",
    "chris-argyris-donald-schon": "chris-argyris",
    "forsgren-humble-kim": "nicole-forsgren",
    "google-sre": "betsy-beyer",
    "hohpe-woolf": "gregor-hohpe",
    "humble-farley": "jez-humble",
    "inioluwa-raji": "inioluwa-deborah-raji",
    "iso-iec": "iso",
    "iso-iec-ieee": "iso",
    "joy-buolamwini-timnit-gebru": "timnit-gebru",
    "mary-tom-poppendieck": "mary-poppendieck",
    "openapi-initiative": "openapi",
    "peter-checkland-john-poulter": "peter-checkland",
    "team-topologies": "matthew-skelton",
}

HOTEL_CHARACTERS = [
    ("Elena Acosta", "Dirección general", "elena.jpg"),
    ("Lucía Ferreyra", "Jefatura de recepción", "lucia.jpg"),
    ("Ricardo Sosa", "Gerencia de operaciones", "ricardo.jpg"),
    ("Federico Müller", "Tecnología y datos", "federico.jpg"),
    ("Mariela Benítez", "Supervisión de housekeeping", "mariela-benitez-v1.png"),
    ("Camila Duarte", "Gerencia comercial", "camila-duarte-v2.png"),
]

# Stable responsibilities preserve the longitudinal Hotel Horizonte cast as
# an analytical device rather than a row of decorative portraits. They are
# collection paratext shared by every N and do not replace the document's
# source-grounded case prose.
HOTEL_RESPONSIBILITIES = [
    "Define alcance, riesgo aceptable y continuidad de la promesa.",
    "Expone el episodio del huésped, las excepciones y la reparación.",
    "Vuelve visibles capacidad, dependencias y condiciones de operación.",
    "Reconstruye datos, contratos, integraciones y límites técnicos.",
    "Aporta secuencias reales, tiempos, daños y condiciones de entrega.",
    "Declara compromisos, demanda, canales y condiciones ofrecidas.",
]

# Topic-specific positions turn the stable cast into an argumentative device.
# N34 needs each role to state what it accepts, disputes and must preserve when
# the complete intervention is reconstructed.
HOTEL_POSITION_OVERRIDES = {
    34: [
        "Exige que la cadena conserve autoridad, riesgo aceptado y condición de reapertura. No aprueba el conjunto si un tramo carece de evidencia.",
        "Prueba la cadena desde el episodio del huésped. Una traza sirve sólo si permite actuar, explicar la excepción y reparar.",
        "Reclama coherencia entre promesa y capacidad operativa. Reabre la dependencia cuyo supuesto falla sin reiniciar toda la intervención.",
        "Vincula fuentes, transformaciones, contratos y versiones. Debe mostrar qué afirmaciones cambian cuando una evidencia pierde vigencia.",
        "Contrasta el expediente con turnos y habitaciones reales. Conserva discrepancias que los tableros agregados suelen ocultar.",
        "Sostiene el compromiso comercial, pero explicita población y condiciones. Una promesa no puede usar evidencia de otra experiencia.",
    ],
}

# The second approved documentary image now resolves a real editorial need
# instead of being expelled from the Hotel case onto an isolated page.
CONSEQUENCE_PHOTO_DOCS = {
    11, 12, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
}

# These documents use one documentary band before Movimiento 2.  The second
# image remains available for the full-page pause and is not repeated after
# Movimiento 3, where it previously produced isolated image-only pages.
MOVEMENT_THREE_PHOTO_DOCS = {11, 12, 13, 14, 15, 16, 17, 21, 23, 24}

HOTEL_ASSET_SOURCES = {
    "elena.jpg": ROOT / "N10-v9-final" / "assets" / "hotel-elena.jpg",
    "lucia.jpg": ROOT / "N10-v9-final" / "assets" / "hotel-lucia.jpg",
    "ricardo.jpg": ROOT / "assets" / "hotel-portraits" / "ricardo.jpg",
    "federico.jpg": ROOT / "assets" / "hotel-portraits" / "federico.jpg",
    "mariela-benitez-v1.png": ROOT / "assets" / "hotel-portraits" / "mariela-benitez-v1.png",
    "camila-duarte-v2.png": ROOT / "assets" / "hotel-portraits" / "camila-duarte-v2.png",
}

def canonical_source(number: int) -> Path:
    """Resolve the current audited canonical source and verify its digest.

    Each canonical package owns the authoritative pointer to its current
    source.  This keeps editorial version numbers independent from content
    version numbers and, unlike filename ordering or the historical v8
    approval manifest, follows the completed plain-language revision.
    """
    code = f"N{number:02d}"
    package_root = ROOT / f"{code}-content-canonical"
    source_manifest = package_root / "source-manifest.json"
    if not source_manifest.is_file():
        raise FileNotFoundError(source_manifest)
    record = json.loads(source_manifest.read_text(encoding="utf-8"))
    if record.get("document") != code:
        raise RuntimeError(f"El manifiesto canónico no corresponde a {code}")
    source = package_root / record["source"]
    if not source.is_file():
        raise FileNotFoundError(source)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    expected_digest = record.get("source_sha256") or record.get("sha256")
    if not expected_digest:
        raise RuntimeError(f"El manifiesto canónico de {code} no declara SHA-256")
    if digest != expected_digest:
        raise RuntimeError(f"La fuente {code} cambió después de la auditoría canónica")
    return source


SOURCES = {n: canonical_source(n) for n in range(11, 37)}


def editorial_primary_titles(number: int) -> set[str]:
    """Return the approved top-level section titles for the editorial system.

    The plain-language pass promoted a few pedagogical signposts from level
    three to level two so they stand out in Markdown.  They remain subsections
    in the magazine: treating every promoted signpost as a new numbered
    section creates isolated pages and breaks the established N00-N10 rhythm.
    The last approved academic source provides the stable section spine.
    """
    approval = json.loads(ACADEMIC_REVISION_MANIFEST.read_text(encoding="utf-8"))
    records = {item["code"]: item for item in approval["documents"]}
    code = f"N{number:02d}"
    source = ROOT / records[code]["source"]
    _title, sections = base.parse_source(source)
    return {section.title for section in sections}


def coalesce_editorial_sections(number: int, sections: list[base.Section]) -> list[base.Section]:
    """Keep the canonical section spine while preserving every source heading."""
    primary = editorial_primary_titles(number)
    result: list[base.Section] = []
    for section in sections:
        if section.title in primary or not result:
            result.append(base.Section(section.title, list(section.lines)))
            continue
        result[-1].lines.extend(["", f"### {section.title}", *section.lines])
    return result

# Movement prose normally flows as continuous magazine text.  Five measured
# endings are long enough to constitute a complete final argument but too short
# to occupy their own ordinary page.  They receive a deliberate editorial close
# without moving or rewriting a source block.
MOVEMENT_EDITORIAL_CLOSES: set[tuple[int, int]] = {
    (11, 3), (14, 3), (15, 3), (16, 3), (17, 3), (20, 2), (21, 3),
    (22, 3), (23, 3), (28, 3), (29, 3), (30, 2), (32, 3), (33, 3),
}
MOVEMENT_CLOSE_RETAIN_WORDS: dict[tuple[int, int], int] = {}
MOVEMENT_CLOSE_SUBSECTIONS: dict[tuple[int, int], int] = {}

REFERENTS = {
    11: ["george-box", "victoria-pillitteri", "robert-groves", "helen-nissenbaum", "elham-tabassi", "cathy-oneil"],
    12: ["grady-booch", "leslie-lamport", "martin-fowler", "david-ferraiolo", "nancy-leveson", "elham-tabassi"],
    13: ["leslie-lamport", "jim-gray", "barbara-liskov", "werner-vogels", "david-parnas", "leonard-kleinrock"],
    14: ["august-wilhelm-scheer", "thomas-davenport", "jan-vom-brocke", "wil-van-der-aalst", "leonard-kleinrock", "henry-mintzberg"],
    15: ["george-box", "donald-schon", "peter-senge", "martin-fowler", "grady-booch", "thomas-davenport"],
    16: ["peter-senge", "amy-edmondson", "donald-schon", "grady-booch", "barry-boehm", "winston-royce"],
    17: ["barry-boehm", "winston-royce", "donald-schon", "amy-edmondson", "david-snowden", "kent-beck"],
    18: ["manny-lehman", "david-parnas", "martin-fowler", "murugiah-souppaya", "karen-scarfone", "tim-berners-lee"],
    19: ["ronald-coase", "oliver-williamson", "thomas-davenport", "tim-berners-lee", "murugiah-souppaya", "elham-tabassi"],
    20: ["barry-boehm", "donald-schon", "henry-mintzberg", "rita-gunther-mcgrath", "kent-beck", "alistair-cockburn"],
    21: ["steve-blank", "geoffrey-g-parker", "marshall-w-van-alstyne", "tim-berners-lee", "grady-booch", "karen-scarfone"],
    22: ["karl-popper", "judea-pearl", "eric-ries", "steve-blank", "george-box", "elham-tabassi"],
    23: ["kent-beck", "steve-blank", "grady-booch", "martin-fowler", "karen-scarfone", "alistair-cockburn"],
    24: ["david-anderson", "ronald-coase", "oliver-williamson", "wil-van-der-aalst", "eric-ries", "george-box"],
    25: ["david-anderson", "wil-van-der-aalst", "werner-vogels", "kent-beck", "amy-edmondson", "george-box"],
    26: ["geoffrey-g-parker", "marshall-w-van-alstyne", "sangeet-paul-choudary", "ronald-coase", "henry-mintzberg", "alistair-cockburn"],
    27: ["roy-t-fielding", "martin-fowler", "david-parnas", "leslie-lamport", "werner-vogels", "jim-gray"],
    28: ["len-bass", "nancy-leveson", "barry-boehm", "david-parnas", "george-box", "amy-edmondson"],
    29: ["kent-beck", "martin-fowler", "amy-edmondson", "werner-vogels", "murugiah-souppaya", "karen-scarfone"],
    30: ["nancy-leveson", "david-snowden", "amy-edmondson", "karen-scarfone", "murugiah-souppaya", "werner-vogels"],
    31: ["stuart-russell", "peter-norvig", "judea-pearl", "virginia-dignum", "helen-nissenbaum", "ben-shneiderman"],
    32: ["joy-buolamwini", "timnit-gebru", "helen-nissenbaum", "ben-shneiderman", "cathy-oneil", "inioluwa-raji"],
    33: ["inioluwa-raji", "elham-tabassi", "timnit-gebru", "kate-crawford", "virginia-dignum", "cathy-oneil"],
    34: ["david-snowden", "alistair-cockburn", "donald-schon", "karl-popper", "amy-edmondson", "paulo-freire"],
    35: ["karl-popper", "edward-tufte", "donald-schon", "amy-edmondson", "paulo-freire", "etienne-wenger"],
    36: ["donald-schon", "peter-senge", "john-dewey", "david-kolb", "amy-edmondson", "paulo-freire"],
}

PORTRAIT_NAMES = {
    "richard-wang": "Richard Y. Wang", "luc-moreau": "Luc Moreau", "robert-groves": "Robert M. Groves",
    "helen-nissenbaum": "Helen Nissenbaum", "elham-tabassi": "Elham Tabassi", "cathy-oneil": "Cathy O’Neil",
    "eric-evans": "Eric Evans", "leslie-lamport": "Leslie Lamport", "martin-fowler": "Martin Fowler",
    "david-ferraiolo": "David Ferraiolo", "nancy-leveson": "Nancy Leveson", "jim-gray": "Jim Gray",
    "pat-helland": "Pat Helland", "werner-vogels": "Werner Vogels", "martin-kleppmann": "Martin Kleppmann",
    "peter-bailis": "Peter Bailis", "michael-hammer": "Michael Hammer", "thomas-davenport": "Thomas Davenport",
    "geary-rummler": "Geary Rummler", "wil-van-der-aalst": "Wil van der Aalst", "john-little": "John D. C. Little",
    "wallace-hopp": "Wallace Hopp", "george-box": "George Box", "karen-scarfone": "Karen Scarfone", "victoria-pillitteri": "Victoria Pillitteri",
    "peter-checkland": "Peter Checkland",
    "john-sterman": "John Sterman", "daniel-moody": "Daniel Moody", "simon-brown": "Simon Brown",
    "marc-lankhorst": "Marc Lankhorst", "chris-argyris": "Chris Argyris", "michael-jackson": "Michael A. Jackson",
    "barry-boehm": "Barry Boehm", "winston-royce": "Winston Royce",
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
    "geoffrey-g-parker": "Geoffrey G. Parker", "marshall-w-van-alstyne": "Marshall W. Van Alstyne",
    "sangeet-paul-choudary": "Sangeet Paul Choudary", "roy-t-fielding": "Roy T. Fielding",
    "len-bass": "Len Bass", "kent-beck": "Kent Beck", "murugiah-souppaya": "Murugiah Souppaya",
    "david-snowden": "David Snowden", "peter-norvig": "Peter Norvig", "joy-buolamwini": "Joy Buolamwini",
    "inioluwa-deborah-raji": "Inioluwa Deborah Raji", "peter-senge": "Peter Senge",
    "grady-booch": "Grady Booch", "barbara-liskov": "Barbara Liskov",
    "leonard-kleinrock": "Leonard Kleinrock", "august-wilhelm-scheer": "August-Wilhelm Scheer",
    "jan-vom-brocke": "Jan vom Brocke", "tim-berners-lee": "Tim Berners-Lee",
    "rita-gunther-mcgrath": "Rita Gunther McGrath", "steve-blank": "Steve Blank",
    "geoffrey-parker": "Geoffrey Parker", "marshall-van-alstyne": "Marshall Van Alstyne",
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
        "Una trabajadora hotelera recorre un corredor de servicio con carros, ascensor y cruces de personal que vuelven visibles transferencias y colas.",
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
        ("Proceso de punta a punta", ["Promesa", "Caso", "Transferencia", "Cola", "Excepción", "Cierre"]),
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
        ("Mapa HH-20", ["Hipótesis", "Adaptación", "Hitos", "Operación", "Retiro"]),
    ],
    21: [("Cuatro objetos de gestión", ["Proyecto", "Producto", "Servicio", "Plataforma", "Capacidad"]), ("Horizontes y responsabilidad", ["Transición", "Aprendizaje", "Operación", "Ecosistema", "Retiro"]), ("Mapa HH-21", ["Resultado", "Objeto", "Autoridad", "Evidencia", "Cierre"])],
    22: [("Anatomía de una hipótesis", ["Población", "Intervención", "Mecanismo", "Resultado", "Umbral"]), ("Prueba refutable", ["Línea de base", "Rival", "Señal", "Salvaguarda", "Decisión"]), ("Mapa HH-22", ["Apuesta", "Exposición", "Evidencia", "Autoridad", "Retiro"])],
    23: [("Corte de capacidad", ["Necesidad", "Regla", "Dato", "Operación", "Resultado"]), ("Aprendizaje por corte", ["Hipótesis", "Episodio", "Integración", "Prueba", "Expansión"]), ("Mapa HH-23", ["Población", "Capacidad", "Excepción", "Evidencia", "Siguiente corte"])],
    24: [("Decisión y renuncia", ["Opción", "Valor", "Demora", "Capacidad", "Renuncia"]), ("Cartera limitada", ["Obligación", "Apuesta", "Habilitador", "Trabajo en curso", "Revisión"]), ("Mapa HH-24", ["Resultado", "Costo", "Dependencia", "Autoridad", "No ahora"])],
    25: [("Flujo de punta a punta", ["Demanda", "Cola", "Trabajo", "Uso", "Retroalimentación"]), ("Economía del flujo", ["Trabajo en curso", "Caudal", "Tiempo", "Lote", "Variabilidad"]), ("Mapa HH-25", ["Unidad", "Espera", "Transferencia", "Política", "Reparación"])],
    26: [("Ecosistema de la promesa", ["Promesa", "Capacidad", "Plataforma", "Tercero", "Reparación"]), ("Dependencia gobernada", ["Responsabilidad", "Confianza", "Señal", "Degradación", "Salida"]), ("Mapa HH-26", ["Participante", "Contrato", "Concentración", "Contingencia", "Revisión"])],
    27: [("Capas del contrato", ["Sintaxis", "Semántica", "Tiempo", "Operación"]), ("Comportamiento verificable", ["Precondición", "Invariante", "Error", "Reintento", "Evolución"]), ("Mapa HH-27", ["Productor", "Consumidor", "Efecto", "Prueba", "Reparación"])],
    28: [("Argumento de calidad", ["Promesa", "Escenario", "Riesgo", "Reclamo", "Evidencia"]), ("Atributos en tensión", ["Confiabilidad", "Desempeño", "Seguridad", "Accesibilidad", "Cambio"]), ("Mapa HH-28", ["Población", "Oráculo", "Umbral", "Renuncia", "Autoridad"])],
    29: [("Cadena de liberación", ["Fuente", "Artefacto", "Ambiente", "Despliegue", "Cierre"]), ("Compromiso progresivo", ["Evidencia", "Aprobación", "Cohorte", "Señal", "Detención"]), ("Mapa HH-29", ["Código", "Datos", "Infraestructura", "Reversión", "Reparación"])],
    30: [("Señales de la promesa", ["Recorrido", "Telemetría", "Negocio", "Experiencia", "Decisión"]), ("Confiabilidad gobernada", ["SLI", "SLO", "Presupuesto", "Alerta", "Respuesta"]), ("Mapa HH-30", ["Incidente", "Contención", "Reparación", "Revisión", "Aprendizaje"])],
    31: [("Capacidades diferentes", ["Regla", "Predicción", "Generación", "Agencia"]), ("Juicio de pertinencia", ["Tarea", "Alternativa", "Valor", "Consecuencia", "Control"]), ("Mapa HH-31", ["Propósito", "Evidencia", "Autoridad", "No uso", "Revisión"])],
    32: [("Arquitectura de evaluación", ["Tarea", "Cobertura", "Métrica", "Severidad", "Decisión"]), ("Autonomía proporcional", ["Línea de base", "Desagregación", "Robustez", "Supervisión"]), ("Mapa HH-32", ["Prueba", "Umbral", "Exposición", "Seguimiento", "Retiro"])],
    33: [("Registro vivo", ["Uso", "Frontera", "Responsable", "Versión", "Riesgo"]), ("Ciclo de gobierno", ["Datos", "Proveedor", "Cambio", "Seguimiento", "Incidente"]), ("Mapa HH-33", ["Contestar", "Reparar", "Aprender", "Retirar"] )],
    34: [("Cadena completa", ["Problema", "Evidencia", "Decisión", "Operación", "Gobierno"]), ("Coherencia defendible", ["Vertical", "Horizontal", "Contradicción", "Puerta"]), ("Mapa HH-34", ["Supuesto", "Prueba", "Consecuencia", "Revisión"])],
    35: [("Argumento situado", ["Audiencia", "Tesis", "Evidencia", "Garantía", "Objeción"]), ("Cuatro defensas", ["Ejecutiva", "Técnica", "Operativa", "Afectada"]), ("Mapa HH-35", ["Transferir", "Apropiar", "Probar", "Reformular"])],
    36: [("Ciclo reflexivo", ["Decidir", "Actuar", "Observar", "Sorprender", "Revisar"]), ("Aprender en dos bucles", ["Corregir acción", "Revisar marco", "Cambiar práctica"]), ("Mapa HH-36", ["Episodio", "Evidencia", "IA crítica", "Próxima prueba"])],
}

HH_MAP_FAMILIES = {
    17: "constellation", 18: "hub", 19: "matrix", 20: "cycle", 21: "hub",
    22: "layers", 23: "sequence", 24: "hub", 25: "constellation", 26: "cycle",
    27: "hub", 28: "sequence", 29: "layers", 30: "matrix", 31: "cycle",
    32: "bridge", 33: "sequence", 34: "hub", 35: "layers", 36: "matrix",
}

# One argument map per reading, with deliberate visual alternation across the
# collection.  Families recur only after several documents and remain matched
# to the relation being explained; no generic flowchart is repeated as filler.
DOCUMENT_DIAGRAM_FAMILIES = {
    11: "sequence", 12: "cycle", 13: "constellation", 14: "sequence",
    15: "matrix", 16: "bridge", 17: "staircase", 18: "layers",
    19: "matrix", 20: "hub", 21: "constellation", 22: "layers",
    23: "sequence", 24: "staircase", 25: "cycle", 26: "hub",
    27: "layers", 28: "bridge", 29: "sequence", 30: "constellation",
    31: "matrix", 32: "bridge", 33: "cycle", 34: "traceability",
    35: "argument", 36: "learning-ledger",
}

# Cover and first-pause copy must be complete thoughts.  The inherited helper
# shortened long sentences with an ellipsis, which made several covers and
# photographic pauses publish visibly unfinished prose.
COVER_PULL_QUOTES = {
    11: "Un dato sostiene una afirmación cuando conserva fenómeno, población, reglas, transformaciones y decisión.",
    12: "Un sistema de información conserva mejor la realidad operacional cuando distingue cinco funciones.",
    13: "En un sistema distribuido, la ausencia de respuesta no prueba ausencia de efecto ni determina un orden legítimo.",
    14: "La promesa, no el área ni la aplicación, define la frontera de un proceso de punta a punta.",
    15: "Un modelo es una representación selectiva construida para una pregunta y una decisión.",
    16: "La coherencia entre modelos no exige que contengan los mismos elementos ni que coincidan literalmente.",
    17: "N17 separa las lógicas de intervención por el modo en que producen conocimiento y compromiso.",
    18: "N18 convierte legado, regulación y documentación en objetos de análisis con valor, costo, evidencia y ciclo de vida.",
    19: "N19 transforma la adquisición en diseño sociotécnico.",
    20: "Falla cuando el calendario o el nombre de un marco sustituyen las condiciones para avanzar, detener, transferir o retirar.",
    21: "El sistema falla cuando el cumplimiento de una capa se usa como prueba del resultado de otra.",
    22: "Una mejora agregada no valida al mismo tiempo causalidad, legitimidad y conveniencia.",
    23: "Una sucesión de componentes terminados no constituye por sí sola un resultado en uso.",
    24: "Priorizar exige volver explícitas las renuncias y quién deberá esperar.",
    25: "La velocidad local no demuestra que el sistema de cambio produzca un mejor resultado de servicio.",
    26: "Una promesa distribuida exige compromisos explícitos entre capacidades autónomas y una salida verificable.",
    27: "Integrar exige compartir o traducir significado, vigencia, efecto y manejo de la indeterminación.",
    28: "La calidad sólo puede sostenerse para una población, un escenario y una consecuencia.",
    29: "Una liberación exige evidencia común de versión, exposición, recuperación y autoridad.",
    30: "Observar un servicio exige señales que permitan inferir la promesa y actuar antes de normalizar la degradación.",
    31: "La inteligencia artificial es pertinente cuando agrega valor frente a una alternativa simple y su riesgo puede gobernarse.",
    32: "Un promedio de desempeño no autoriza autonomía.",
    33: "La aprobación de una inteligencia artificial pertenece a un uso verificable, no al nombre comercial de un modelo.",
    34: "Una colección de artefactos correctos no constituye una intervención coherente.",
    35: "Comunicar con fidelidad exige conservar evidencia, límites y revisión para cada audiencia.",
    36: "Un resultado favorable no valida la explicación que condujo a él ni demuestra aprendizaje.",
}

FIRST_PAUSE_QUOTES = {
    11: "La exactitud es necesaria, pero no alcanza para volver pertinente, suficiente y vigente una evidencia.",
    12: "Comando, evento, estado, evidencia y autoridad cumplen funciones distintas dentro del sistema.",
    13: "Cada frontera introduce demora, repetición, pérdida, reordenamiento y conocimiento parcial.",
    14: "Un proceso coordina trabajo, decisiones, esperas y reparaciones para producir un resultado observable.",
    15: "El valor de un modelo proviene tanto de lo que incluye como de lo que excluye.",
    16: "Dos vistas pueden diferir legítimamente y seguir formando una cartera íntegra.",
    17: "Una estrategia puede combinar lógicas si cada una conserva propósito, evidencia y autoridad.",
    18: "La modernización deja de ser sustitución automática y pasa a ser un juicio de continuidad responsable.",
    19: "Comparar alternativas exige mirar capacidad, costo total, control, dependencia, evidencia y salida.",
    20: "Cada práctica debe responder al riesgo y cada hito debe vincular evidencia, autoridad y una decisión posible.",
    21: "Proyecto, producto, servicio y plataforma sostienen temporalidades y responsabilidades distintas.",
    22: "Una iniciativa aprende cuando explicita mecanismo, rival, población, línea de base, salvaguardas, umbral y decisión.",
    23: "Un corte vertical produce aprendizaje cuando conserva una capacidad completa para una población delimitada.",
    24: "Priorizar convierte la escasez en renuncias explícitas y conserva consecuencias en unidades pertinentes.",
    25: "El flujo conserva identidad desde la demanda hasta una capacidad en uso y contrasta sus efectos sobre el servicio.",
    26: "Cada dependencia necesita confianza, responsabilidad, degradación prevista y una salida verificable.",
    27: "Un contrato debe probarse sobre su consecuencia operacional y conservar quién puede detener y reparar.",
    28: "Si un promedio oculta daño severo o una población sin alternativa, la evidencia no autoriza la promesa.",
    29: "Revertir código no repara por sí solo los estados, dependencias y expectativas que ya cambiaron.",
    30: "Telemetría sin una decisión y una autoridad para actuar no vuelve observable la promesa.",
    31: "Fluidez y potencia no prueban pertinencia cuando una alternativa simple resuelve la tarea con menor riesgo.",
    32: "Una evaluación defendible representa tareas, poblaciones, severidad, robustez y capacidad real de reparación.",
    33: "El permiso pierde vigencia si cambia el uso, la versión, el proveedor, la población o el contexto.",
    34: "La coherencia se prueba recorriendo cada afirmación desde el problema hasta la consecuencia y su revisión.",
    35: "La transferencia se prueba cuando otra persona reconstruye el criterio, lo objeta y actúa responsablemente.",
    36: "Aprender exige que una sorpresa modifique una regla, una autoridad o una capacidad, y que una prueba posterior lo confirme.",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean_title(number: int, title: str) -> str:
    return re.sub(rf"^N{number:02d}\s*[·—-]\s*", "", title).strip()


def complete_pullquote(value: str, limit: int = 170) -> str:
    """Select a complete sentence without manufacturing an ellipsis."""
    clean = re.sub(r"[*_`]", "", value).strip()
    sentences = [item.strip() for item in re.split(r"(?<=[.!?])\s+", clean) if item.strip()]
    if not sentences:
        return clean
    return next((item for item in sentences if len(item) <= limit), min(sentences, key=len))


def referent_paragraphs(section: base.Section) -> list[str]:
    return [line.strip() for line in section.lines if line.strip().startswith("**")]


def valid_raster(path: Path) -> bool:
    """Reject Git LFS pointers and truncated files before they reach Chromium."""
    if not path.is_file() or path.stat().st_size < 1_024:
        return False
    header = path.read_bytes()[:16]
    return (
        header.startswith(b"\xff\xd8\xff")
        or header.startswith(b"\x89PNG\r\n\x1a\n")
        or (header.startswith(b"RIFF") and header[8:12] == b"WEBP")
    )


def portrait_source(key: str, legacy_assets: Path | None = None) -> Path | None:
    candidates = [key]
    alias = PORTRAIT_ALIASES.get(key)
    if alias:
        candidates.append(alias)
    # Curated release assets take precedence over inherited package copies:
    # inherited files can be visually valid while lacking a reusable-rights
    # record or can differ from the exact hash approved by the curator.
    roots = [PORTRAIT_ROOT, SHARED_PORTRAITS]
    if legacy_assets is not None:
        roots.append(legacy_assets)
    for root in roots:
        for candidate in candidates:
            stems = (f"referent-{candidate}", candidate) if root == legacy_assets else (candidate,)
            for stem in stems:
                for suffix in (".jpg", ".jpeg", ".png", ".webp"):
                    path = root / f"{stem}{suffix}"
                    if valid_raster(path):
                        return path
    return None


def initials(name: str) -> str:
    return "".join(part[0] for part in re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", name)[:2]).upper()


def normalized_name(name: str) -> str:
    decomposed = unicodedata.normalize("NFKD", name)
    plain = "".join(character for character in decomposed if not unicodedata.combining(character))
    return re.sub(r"[^a-z0-9]+", " ", plain.casefold()).strip()


REFERENCE_ALIAS_TOKENS = {
    "george-box": ["box"],
    "cynthia-kurtz-david-snowden": ["kurtz", "snowden"],
    "carliss-baldwin-kim-clark": ["baldwin", "clark"],
    "parker-van-alstyne-choudary": ["parker", "alstyne", "choudary"],
    "wallace-hopp-mark-spearman": ["hopp", "spearman"],
    "bass-clements-kazman": ["bass", "clements", "kazman"],
    "forsgren-humble-kim": ["forsgren", "humble", "kim"],
    "humble-farley": ["humble", "farley"],
    "hohpe-woolf": ["hohpe", "woolf"],
    "joy-buolamwini-timnit-gebru": ["buolamwini", "gebru"],
    "batya-friedman-david-hendry": ["friedman", "hendry"],
    "peter-checkland-john-poulter": ["checkland", "poulter"],
    "chris-argyris-donald-schon": ["argyris", "schon"],
    "mary-tom-poppendieck": ["poppendieck"],
    "agile-alliance": ["agile", "manifesto"],
    "team-topologies": ["team", "topologies"],
    "google-sre": ["site", "reliability"],
    "openapi-initiative": ["openapi"],
    "json-schema": ["json", "schema"],
    "iso-iec-ieee": ["iso", "iec", "ieee"],
    "iso-iec": ["iso", "iec"],
    "european-union": ["union", "europea"],
}


def reference_lines(section: base.Section) -> list[str]:
    return [line[2:].strip() for line in section.lines if line.strip().startswith("- ")]


def primary_reference_for(key: str, display: str, section: base.Section) -> str:
    """Resolve the source-backed principal work shown on a Referentes card."""
    stop = {"and", "del", "the", "van", "von", "para", "con", "initiative", "institute"}
    tokens = REFERENCE_ALIAS_TOKENS.get(key)
    if not tokens:
        tokens = [
            token for token in normalized_name(display).split()
            if len(token) >= 4 and token not in stop
        ]
    candidates: list[tuple[int, int, str]] = []
    for position, raw in enumerate(reference_lines(section)):
        normalized = normalized_name(raw)
        score = sum(1 for token in tokens if token in normalized)
        if score:
            candidates.append((score, -position, raw))
    if not candidates:
        raise ValueError(f"No se encontró una obra principal en Referencias base para {display}")
    return max(candidates)[2]


def primary_work_markup(reference: str) -> str:
    """Render title and publication metadata with the hierarchy used in N02."""
    italic = re.search(r"(?<!\*)\*([^*]+)\*(?!\*)", reference)
    quoted = re.search(r"[“\"]([^”\"]+)[”\"]", reference)
    # Articles are identified by their quoted title, while books and reports
    # use the italic title.  Preferring the quote avoids presenting the journal
    # name as if it were the contributor's principal work.
    match = quoted or italic
    if match:
        title = match.group(1).strip()
        tail = reference[match.end():]
    else:
        title = reference.split(".", 1)[-1].strip()
        tail = ""
    year_match = re.search(r"\b(?:19|20)\d{2}\b", reference)
    year = year_match.group(0) if year_match else ""
    journal = re.search(r"\*([^*]+)\*", tail)
    if quoted and match is quoted and journal:
        tail = journal.group(1)
    tail = re.sub(r"https?://\S+", "", tail)
    tail = tail.replace("*", "")
    tail = re.sub(r"\s+", " ", tail).strip(" .")
    if len(tail) > 92:
        tail = tail[:89].rsplit(" ", 1)[0] + "…"
    meta = " · ".join(part for part in (tail, year) if part)
    return (
        f'<cite>{html.escape(title)}</cite>'
        f'<small>{html.escape(meta)}</small>'
    )


def portrait_rights_registry() -> dict[str, dict]:
    """Load only the explicit, machine-readable portrait release evidence.

    Narrative research notes are intentionally ignored here.  A portrait may
    reach the package manifest only when a curator has supplied the complete
    identity, credit, licence and approval record in a portrait-rights JSON.
    """
    records: dict[str, dict] = {}
    for registry_path in sorted(PORTRAIT_ROOT.glob("portrait-rights-*.json")):
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
        raw_records = (
            payload.get("entries", payload.get("assets", payload))
            if isinstance(payload, dict)
            else payload
        )
        if isinstance(raw_records, dict):
            candidates = [dict(value, key=key) for key, value in raw_records.items() if isinstance(value, dict)]
        elif isinstance(raw_records, list):
            candidates = [value for value in raw_records if isinstance(value, dict)]
        else:
            continue
        for record in candidates:
            name = str(record.get("canonical_name") or record.get("name") or "").strip()
            if name and record.get("approved") is True:
                records[normalized_name(name)] = {**record, "_registry": registry_path.name}
    return records


def portrait_key_for_display(display: str) -> str:
    normalized = normalized_name(display)
    for key, known_name in PORTRAIT_NAMES.items():
        if normalized_name(known_name) == normalized:
            return key
    return normalized.replace(" ", "-")


def build_referents(
    number: int,
    section: base.Section,
    references_section: base.Section,
    assets: Path,
    legacy_assets: Path,
) -> tuple[str, list[dict]]:
    paragraphs = referent_paragraphs(section)
    if len(paragraphs) != 6:
        raise ValueError(f"N{number:02d} requiere seis Referentes; se encontraron {len(paragraphs)}")
    cards = []
    records = []
    rights = portrait_rights_registry()
    if 11 <= number <= 36:
        selected_keys = [portrait_key_for_display(re.match(r"\*\*(.+?)\.\*\*", raw).group(1)) for raw in paragraphs]
        expected_keys = REFERENTS[number]
        if selected_keys != expected_keys:
            raise ValueError(
                f"N{number:02d} no coincide con la matriz aprobada de retratos: "
                f"{selected_keys!r} != {expected_keys!r}"
            )
    for index, raw in enumerate(paragraphs, 1):
        match = re.match(r"\*\*(.+?)\.\*\*\s*(.*)", raw)
        display = match.group(1) if match else f"Referente {index}"
        body = match.group(2) if match else raw
        key = portrait_key_for_display(display)
        primary_reference = primary_reference_for(key, display, references_section)
        work_markup = primary_work_markup(primary_reference)
        source = portrait_source(key, legacy_assets)
        proof = rights.get(normalized_name(display), {})
        proof_sha = str(proof.get("sha256") or "")
        source_sha = sha(source) if source else ""
        approved_source = bool(source and proof and proof_sha == source_sha)
        if approved_source:
            target = assets / f"referent-{key}{source.suffix.lower()}"
            if key == "jan-vom-brocke":
                # The Commons original is a wide documentary scene. A tight,
                # deterministic crop keeps the named person recognizable in
                # the small Referentes card while preserving the licensed
                # original in the shared asset registry.
                crop_box = (.3375, .60, .46, .7067)
                with Image.open(source) as portrait:
                    portrait = ImageOps.exif_transpose(portrait).convert("RGB")
                    width, height = portrait.size
                    box = tuple(
                        round(value * (width if index % 2 == 0 else height))
                        for index, value in enumerate(crop_box)
                    )
                    portrait.crop(box).save(target, quality=94, optimize=True)
            elif key == "david-snowden":
                # The approved source documents a stage appearance. Preserve
                # that source and derive a head-and-shoulders crop so the
                # Referentes grid does not mix a long shot with five portraits.
                crop_box = (.20, .30, .64, .60)
                with Image.open(source) as portrait:
                    portrait = ImageOps.exif_transpose(portrait).convert("RGB")
                    width, height = portrait.size
                    box = tuple(
                        round(value * (width if index % 2 == 0 else height))
                        for index, value in enumerate(crop_box)
                    )
                    portrait.crop(box).save(target, quality=94, optimize=True)
            else:
                shutil.copy2(source, target)
            visual = f'<img src="assets/{target.name}" alt="Retrato documental de {html.escape(display)}">'
            status = str(proof.get("rights_status") or "approved_open_reuse")
        else:
            target = None
            visual = (
                '<div class="portrait-unavailable" role="img" '
                'aria-label="Perfil bibliográfico sin retrato reproducido">'
                f'<span>{initials(display)}</span><small>PERFIL BIBLIOGRÁFICO</small></div>'
            )
            status = "portrait_withheld_pending_rights"
        cards.append(
            f'<article class="contributor contributor-{key}"><div class="portrait-frame">{visual}</div><b>{index:02d}</b>'
            f'<h3>{html.escape(display)}</h3><div class="contributor-work">{work_markup}</div>'
            f'<p>{base.inline(body)}</p></article>'
        )
        record = {
            "key": key,
            "name": display,
            "file": f"assets/{target.name}" if target else "",
            "sha256": sha(target) if target else "",
            "rights_status": status,
            "primary_reference": primary_reference,
        }
        if approved_source:
            record.update({
                "source_page": proof.get("source_page", ""),
                "creator": proof.get("creator", ""),
                "credit_line": proof.get("credit_line", proof.get("creator", "")),
                "license_name": proof.get("license_name", ""),
                "license_url": proof.get("license_url", ""),
                "approved": True,
                "rights_registry": proof.get("_registry", ""),
            })
        records.append(record)
    page = (
        f'<section class="front-page authors-page" id="referentes"><header><span>METSI · FCE-UBA</span>'
        f'<h2>Referentes</h2><p>Seis referentes y las obras principales utilizadas para construir N{number:02d}.</p></header>'
        f'<div class="contributors-grid">{"".join(cards)}</div>'
        f'<blockquote>N{number:02d} no resume estas fuentes ni las convierte en receta. Las pone en tensión para construir juicio profesional.</blockquote></section>'
    )
    return page, records


def build_hotel_voices(number: int, assets: Path) -> str:
    cards = []
    positions = HOTEL_POSITION_OVERRIDES.get(number, HOTEL_RESPONSIBILITIES)
    for index, ((name, role, filename), responsibility) in enumerate(
        zip(HOTEL_CHARACTERS, positions), 1
    ):
        source = HOTEL_ASSET_SOURCES[filename]
        if not valid_raster(source):
            raise FileNotFoundError(f"Retrato estable de Hotel Horizonte no disponible: {source}")
        target = assets / f"hotel-{filename}"
        shutil.copy2(source, target)
        cards.append(
            f'<article class="hotel-voice hotel-voice-{index}"><figure class="hotel-portrait"><img class="hotel-character-portrait" src="assets/{target.name}" alt="" aria-hidden="true"></figure>'
            f'<div><span>{html.escape(role)}</span><h3>{html.escape(name)}</h3>'
            f'<p>{html.escape(responsibility)}</p></div></article>'
        )
    return (
        f'<aside class="hotel-voices-compact"><header><b>HOTEL HORIZONTE · N{number:02d}</b>'
        '<p class="hotel-voices-title">Seis responsabilidades dentro del sistema</p>'
        '<p>El episodio cambia según la promesa, la operación, el dato y la autoridad que cada rol debe sostener.</p></header>'
        f'<div class="hotel-voices-grid">{"".join(cards)}</div></aside>'
    )


def apply_premium_color_overrides(number: int, panels: list[Path]) -> list[Path]:
    for index, source in PREMIUM_COLOR_OVERRIDES.get(number, {}).items():
        if not valid_raster(source):
            raise FileNotFoundError(f"Fotografía editorial color inválida para N{number:02d}: {source}")
        target = panels[index]
        with Image.open(source) as image:
            ImageOps.exif_transpose(image).convert("RGB").save(target, format="PNG", optimize=True)
    return panels


def support_assets(number: int, legacy_assets: Path, assets: Path) -> list[Path]:
    """Copy eight validated editorial photographs, never a missing or LFS asset.

    The dedicated rebuild set is authoritative. During layout development only,
    the already approved native black and white cover and pauses provide a safe
    photographic fallback. The manifest records that fallback so the release
    gate can reject it before publication.
    """
    sheet = SUPPORT_ROOT / f"N{number:02d}-support-sheet.png"
    if valid_raster(sheet):
        with Image.open(sheet) as source_image:
            source_image.load()
            width, height = source_image.size
            if width < 1_000 or height < 1_500:
                raise ValueError(f"Plancha editorial insuficiente para N{number:02d}: {source_image.size}")
            panel_width = width // 2
            panel_height = height // 4
            # N13 was delivered as five irregular rows rather than the shared
            # 2 by 4 contact-sheet contract. Select four complete rows and fit
            # each scene independently so no published panel splices two
            # unrelated photographs.
            n13_rows = [(0, 306), (306, 614), (920, 1200), (1200, height)]
            panels: list[Path] = []
            for index in range(8):
                column = index % 2
                row = index // 2
                top, bottom = n13_rows[row] if number == 13 else (row * panel_height, (row + 1) * panel_height)
                crop = source_image.crop((column * panel_width, top, (column + 1) * panel_width, bottom))
                crop = ImageOps.fit(crop, (512, 384), method=Image.Resampling.LANCZOS)
                target = assets / f"editorial-{index + 1:02d}.png"
                crop.save(target, format="PNG", optimize=True)
                panels.append(target)
        return apply_premium_color_overrides(number, panels)

    fallbacks = [
        legacy_assets / "cover-source-premium-bw-v1.png",
        legacy_assets / "pause-02.png",
        legacy_assets / "pause-01.png",
        legacy_assets / "cover-source-premium-bw-v1.png",
        legacy_assets / "pause-02.png",
        legacy_assets / "pause-01.png",
        legacy_assets / "cover-source-premium-bw-v1.png",
        legacy_assets / "pause-02.png",
    ]
    copied: list[Path] = []
    for index in range(1, 9):
        dedicated = next(
            (
                path
                for suffix in (".png", ".jpg", ".jpeg", ".webp")
                if valid_raster(path := SUPPORT_ROOT / f"N{number:02d}-support-{index:02d}{suffix}")
            ),
            None,
        )
        source = dedicated or fallbacks[index - 1]
        if not valid_raster(source):
            raise FileNotFoundError(f"Fotografía editorial inválida para N{number:02d}: {source}")
        target = assets / f"editorial-{index:02d}{source.suffix.lower()}"
        shutil.copy2(source, target)
        copied.append(target)
    return apply_premium_color_overrides(number, copied)


def photo_band(path: Path, alt: str, caption: str, extra_class: str = "") -> str:
    classes = "photo-band editorial-photo-band"
    if extra_class:
        classes += f" {extra_class}"
    image_class = ' class="editorial-contact-sheet"' if path.name == "editorial-support-sheet.png" else ""
    return (
        f'<figure class="{classes}"><div class="photo-viewport"><img{image_class} src="assets/{path.name}" alt="{html.escape(alt)}"></div>'
        f'<figcaption>{html.escape(caption)}</figcaption></figure>'
    )


def photo_diptych(
    left: Path,
    left_alt: str,
    right: Path,
    right_alt: str,
    caption: str,
    extra_class: str = "",
) -> str:
    """Compose two native panels at print-safe width instead of enlarging one.

    The rebuild photographs are 512 by 384 pixels.  A paired 78 mm viewport
    keeps each one above 160 effective pixels per inch and also creates the
    visual comparison required by the argument.
    """
    classes = "photo-diptych editorial-photo-diptych"
    if extra_class:
        classes += f" {extra_class}"
    return (
        f'<figure class="{classes}"><div class="diptych-grid">'
        f'<div class="diptych-viewport"><img src="assets/{left.name}" alt="{html.escape(left_alt)}"></div>'
        f'<div class="diptych-viewport"><img src="assets/{right.name}" alt="{html.escape(right_alt)}"></div>'
        f'</div><figcaption>{html.escape(caption)}</figcaption></figure>'
    )


def insert_after_paragraphs(body: str, insertion: str, fraction: float = 0.7) -> str:
    endings = [match.end() for match in re.finditer(r"</p>", body)]
    if not endings:
        return insertion + body
    position = endings[min(len(endings) - 1, max(0, round(len(endings) * fraction) - 1))]
    return body[:position] + insertion + body[position:]


def split_lead_html(body: str) -> tuple[str, str]:
    """Keep a section heading with its first argued paragraph before media."""
    first_paragraph = re.search(r"</p>", body)
    if not first_paragraph:
        return "", body
    cut = first_paragraph.end()
    return body[:cut], body[cut:]


def split_last_paragraph_html(body: str) -> tuple[str, str]:
    """Lift the final argued paragraph into a full-width editorial close."""
    matches = list(re.finditer(r"<p\b[^>]*>.*?</p>", body, re.S))
    if not matches:
        return body, ""
    match = matches[-1]
    return body[:match.start()] + body[match.end():], match.group(0)


def split_last_subsection_as_editorial_close(
    body: str, variant: int, retain_words: int = 0, subsection_count: int = 1
) -> tuple[str, str]:
    """Keep a movement's final argument together as a designed close.

    Long final subsections remain two-column reading text; shorter ones use a
    single, larger measure.  In both cases every original heading and paragraph
    keeps its source identifier and appears exactly once.
    """
    matches = list(re.finditer(r"(<h3\b[^>]*>.*?</h3>)(.*?)(?=<h3\b|\Z)", body, re.S))
    if not matches:
        return body, ""
    selected = matches[-max(1, min(subsection_count, len(matches))):]
    match = selected[0]
    heading = selected[0].group(1)
    prose = selected[0].group(2) + "".join(item.group(1) + item.group(2) for item in selected[1:])
    word_count = len(re.findall(r"\b\w+\b", re.sub(r"<[^>]+>", " ", prose)))
    retained = ""
    close_heading = heading
    close_prose = prose
    continuation_class = ""
    if retain_words > 0:
        paragraph_matches = list(re.finditer(r"<p\b[^>]*>.*?</p>", prose, re.S))
        retained_count = 0
        retained_words = 0
        target_words = retain_words or 65
        while len(paragraph_matches) - retained_count > 2 and retained_words < target_words:
            paragraph = paragraph_matches[retained_count].group(0)
            retained_count += 1
            retained_words += len(re.findall(r"\b\w+\b", re.sub(r"<[^>]+>", " ", paragraph)))
        cut = paragraph_matches[retained_count - 1].end() if retained_count else 0
        retained = heading + prose[:cut]
        close_heading = ""
        close_prose = prose[cut:]
        continuation_class = " close-continuation"
    close_word_count = len(re.findall(r"\b\w+\b", re.sub(r"<[^>]+>", " ", close_prose)))
    length_class = "close-long" if close_word_count > 220 else "close-short"
    close = (
        f'<aside class="movement-editorial-close {length_class}{continuation_class} close-variant-{variant}">'
        f'{close_heading}<div class="movement-editorial-close-body">{close_prose}</div></aside>'
    )
    return body[:match.start()] + retained + body[selected[-1].end():], close


def wrap_hotel_text_columns(body: str, column_count: int = 3) -> str:
    """Balance the remaining Hotel prose into ordered, explicit columns.

    Browser multicolumn fragmentation may push the indivisible character panel
    below later paragraphs.  Explicit contiguous groups preserve reading order
    and keep the photographic case as a deliberate two-page unit.
    """
    paragraphs = re.findall(r"<p\b[^>]*>.*?</p>", body, re.S)
    if len(paragraphs) < column_count or "".join(paragraphs) != body:
        return f'<div class="hotel-text-column">{body}</div>'
    weights = [len(re.findall(r"\b\w+\b", re.sub(r"<[^>]+>", " ", paragraph))) for paragraph in paragraphs]
    prefix = [0]
    for weight in weights:
        prefix.append(prefix[-1] + weight)
    best: tuple[int, tuple[int, ...]] | None = None

    def search(cuts: tuple[int, ...], start: int) -> None:
        nonlocal best
        if len(cuts) == column_count - 1:
            points = (0, *cuts, len(paragraphs))
            group_weights = [prefix[points[i + 1]] - prefix[points[i]] for i in range(column_count)]
            score = max(group_weights) - min(group_weights)
            candidate = (score, cuts)
            if best is None or candidate < best:
                best = candidate
            return
        remaining_cuts = column_count - 1 - len(cuts)
        for cut in range(start, len(paragraphs) - remaining_cuts + 1):
            search((*cuts, cut), cut + 1)

    search((), 1)
    assert best is not None
    points = (0, *best[1], len(paragraphs))
    columns = ["".join(paragraphs[points[i]:points[i + 1]]) for i in range(column_count)]
    return "".join(f'<div class="hotel-text-column">{column}</div>' for column in columns)


def add_breaks_to_encoded_url_segments(body: str) -> str:
    """Permit safe line breaks after encoded spaces in exceptional long URLs.

    Normal URLs still break only after slashes.  A few official filenames are
    themselves wider than a reference column; `%20` is their only semantic
    boundary.  Separate spans and zero-width break opportunities preserve the
    copied URL exactly and never split a hyphenated token.
    """
    pattern = re.compile(r'<span class="url-segment">([^<]*%20[^<]*)</span>')

    def split(match: re.Match[str]) -> str:
        value = match.group(1)
        if len(value) < 48:
            return match.group(0)
        parts = re.split(r"(?<=%20)", value)
        return "<wbr>".join(f'<span class="url-segment">{part}</span>' for part in parts if part)

    return pattern.sub(split, body)


def wrap_error_cards(body: str) -> str:
    """Group each error heading with its explanation for a stable card grid."""
    pattern = re.compile(r"(<h3\b[^>]*>.*?</h3>\s*<p\b[^>]*>.*?</p>)", re.S)
    return pattern.sub(r'<article class="error-card">\1</article>', body)


def wrap_subsection_units(body: str) -> str:
    """Keep audited argument units intact without over-constraining all flow.

    Most subsections need only heading-plus-lead protection.  A small set of
    recurrent closing arguments was measured to leave anonymous page tails, so
    those complete units are kept together through the next heading.
    """
    unit_pattern = re.compile(r"(<h3\b[^>]*>.*?</h3>)(.*?)(?=<h3\b|\Z)", re.S)
    lead_pattern = re.compile(r"(<h3\b[^>]*>.*?</h3>\s*<p\b[^>]*>.*?</p>)", re.S)
    protected_titles = {
        "Caso de transferencia: una orden de medicación repetida",
        "Riesgo como organizador",
        "Prueba integral antes de ampliar compromiso",
        "Condición de detención",
    }

    def wrap(match: re.Match[str]) -> str:
        unit = match.group(1) + match.group(2)
        heading = re.sub(r"<[^>]+>", "", match.group(1)).strip()
        if html.unescape(heading) in protected_titles:
            return f'<div class="subsection-unit">{unit}</div>'
        return lead_pattern.sub(r'<div class="subsection-lead">\1</div>', unit, count=1)

    return unit_pattern.sub(wrap, body)


def diagram_svg(
    number: int,
    index: int,
    title: str,
    labels: list[str],
    target: Path,
    forced_family: str | None = None,
) -> dict:
    width, height = 1600, 900
    escaped_title = html.escape(title)

    def label_text(x: float, y: float, label: str, *, centered: bool = False, width_chars: int = 18) -> str:
        lines = textwrap.wrap(label, width=width_chars, break_long_words=False, break_on_hyphens=False) or [label]
        first_y = y - (len(lines) - 1) * 16
        css = "l center" if centered else "l"
        tspans = "".join(
            f'<tspan x="{x:.1f}" y="{first_y + line_index * 32:.1f}">{html.escape(line)}</tspan>'
            for line_index, line in enumerate(lines)
        )
        return f'<text class="{css}">{tspans}</text>'

    normalized = title.lower()
    if "ciclo" in normalized or "retroaliment" in normalized:
        family = "cycle"
    elif "capas" in normalized or "arquitectura" in normalized:
        family = "layers"
    elif "ecosistema" in normalized or "señales" in normalized:
        family = "hub"
    elif "atributos" in normalized or "objetos" in normalized or "capacidades" in normalized:
        family = "matrix"
    elif "mapa hh" in normalized:
        family = HH_MAP_FAMILIES[number]
    elif "decisión" in normalized or "puertas" in normalized or "renuncia" in normalized:
        family = "staircase"
    elif "cadena" in normalized or "proceso" in normalized or "flujo" in normalized:
        family = "sequence"
    else:
        family = ("bridge", "cycle", "layers", "hub", "matrix", "staircase")[(number + index) % 6]
    if forced_family:
        family = forced_family

    defs = '<defs><marker id="a" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L0,8 L9,4 z" fill="#232523"/></marker></defs>'
    parts: list[str] = []

    if family == "sequence":
        gap = 24
        cell = (1480 - gap * (len(labels) - 1)) / len(labels)
        for i, label in enumerate(labels):
            x = 60 + i * (cell + gap)
            y = 295 + (48 if i % 2 else 0)
            parts.append(f'<rect x="{x:.1f}" y="{y}" width="{cell:.1f}" height="245" rx="6" fill="{"#E3E6E4" if i % 2 else "#F8F7F3"}" stroke="#232523" stroke-width="2"/>')
            parts.append(f'<text x="{x+20:.1f}" y="{y+42}" class="n">{i+1:02d}</text>{label_text(x+20, y+108, label, width_chars=14)}')
            if i:
                previous_x = 60 + (i - 1) * (cell + gap) + cell
                parts.append(f'<path d="M{previous_x:.1f} {y+122} H{x-6:.1f}" class="edge"/>')
    elif family == "cycle":
        count = len(labels)
        positions = [
            (
                800 + 400 * math.cos(-math.pi / 2 + 2 * math.pi * i / count),
                470 + 210 * math.sin(-math.pi / 2 + 2 * math.pi * i / count),
            )
            for i in range(count)
        ]
        radius = 84 if count >= 6 else 92
        for i, (x, y) in enumerate(positions):
            nx, ny = positions[(i+1) % count]
            parts.append(f'<path d="M{x} {y} L{nx} {ny}" class="edge"/>')
        for i, label in enumerate(labels):
            x, y = positions[i]
            parts.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{"#E3E6E4" if i%2 else "#F8F7F3"}" stroke="#232523" stroke-width="2"/>')
            parts.append(f'<text x="{x}" y="{y-24}" class="n center">{i+1:02d}</text>{label_text(x, y+20, label, centered=True, width_chars=13)}')
        parts.append('<circle cx="800" cy="486" r="82" fill="#171917"/><text x="800" y="478" class="hub center">DECIDIR</text><text x="800" y="510" class="hub-small center">Y REVISAR</text>')
    elif family == "layers":
        for i, label in enumerate(labels):
            y = 270 + i * 92
            x = 100 + i * 48
            w = 1370 - i * 96
            parts.append(f'<path d="M{x} {y} H{x+w} L{x+w-38} {y+66} H{x+38} Z" fill="{"#E3E6E4" if i%2 else "#F8F7F3"}" stroke="#232523" stroke-width="2"/>')
            parts.append(f'<text x="{x+28}" y="{y+42}" class="n">{i+1:02d}</text>{label_text(x+115, y+43, label, width_chars=28)}')
    elif family == "hub":
        positions = [(310,310),(1290,310),(1370,650),(800,735),(230,650)]
        for i, label in enumerate(labels):
            x, y = positions[i % len(positions)]
            parts.append(f'<path d="M800 500 L{x} {y}" class="edge faint"/>')
            parts.append(f'<rect x="{x-155}" y="{y-58}" width="310" height="116" rx="58" fill="{"#E3E6E4" if i%2 else "#F8F7F3"}" stroke="#232523" stroke-width="2"/>')
            parts.append(f'<text x="{x}" y="{y-18}" class="n center">{i+1:02d}</text>{label_text(x, y+26, label, centered=True, width_chars=17)}')
        parts.append('<circle cx="800" cy="500" r="122" fill="#171917"/><path d="M724 500h152" stroke="#CFFF00" stroke-width="8"/><text x="800" y="465" class="hub center">SISTEMA</text><text x="800" y="545" class="hub-small center">RELACIONES</text>')
    elif family == "matrix":
        for i, label in enumerate(labels):
            col, row = i % 3, i // 3
            x, y = 100 + col * 500, 285 + row * 245
            parts.append(f'<rect x="{x}" y="{y}" width="450" height="195" fill="{"#E3E6E4" if (i+row)%2 else "#F8F7F3"}" stroke="#232523" stroke-width="2"/>')
            parts.append(f'<text x="{x+25}" y="{y+42}" class="n">{i+1:02d}</text>{label_text(x+25, y+112, label, width_chars=24)}')
        parts.append('<path d="M70 758H1530" stroke="#CFFF00" stroke-width="12"/>')
    elif family == "staircase":
        count = len(labels)
        # Fit the complete sequence inside the SVG viewBox.  The former fixed
        # step pushed the sixth card beyond x=1600 and clipped its label.
        cell_width = 225 if count <= 5 else 205
        step = (1465 - cell_width) / max(1, count - 1)
        for i, label in enumerate(labels):
            x = 75 + i * step
            y = 640 - i * 78
            parts.append(f'<path d="M{x} {y}v{-150}h{cell_width:.1f}v150z" fill="{"#E3E6E4" if i%2 else "#F8F7F3"}" stroke="#232523" stroke-width="2"/>')
            parts.append(f'<text x="{x+18}" y="{y-108}" class="n">{i+1:02d}</text>{label_text(x+18, y-54, label, width_chars=13)}')
            if i < count-1:
                parts.append(f'<path d="M{x+cell_width:.1f} {y-75} H{x+step-10:.1f} V{y-153}" class="edge"/>')
    elif family == "constellation":
        positions = [(260,380,118),(590,625,100),(820,315,140),(1130,610,112),(1370,365,94)]
        for i, label in enumerate(labels):
            x, y, radius = positions[(i + number) % len(positions)]
            for j in range(i):
                px, py, _ = positions[(j + number) % len(positions)]
                if (i + j + number) % 2 == 0:
                    parts.append(f'<path d="M{px} {py} L{x} {y}" class="edge faint"/>')
            parts.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{"#E3E6E4" if i%2 else "#F8F7F3"}" stroke="#232523" stroke-width="2"/>')
            parts.append(f'<text x="{x}" y="{y-24}" class="n center">{i+1:02d}</text>{label_text(x, y+22, label, centered=True, width_chars=14)}')
        parts.append('<path d="M90 760h250l-22 24H68z" fill="#CFFF00"/>')
    elif family == "traceability":
        # N34 audits a complete intervention across several artefacts.  A
        # traceability field makes that transverse relation visible without
        # presenting the material as yet another left-to-right process.
        rail_labels = ("COHERENCIA", "TRAZABILIDAD", "REVISIÓN")
        cell_width = 190
        gap = 60
        start_x = 265
        for i, label in enumerate(labels):
            x = start_x + i * (cell_width + gap)
            parts.append(f'<text x="{x + cell_width / 2:.1f}" y="247" class="n center">{i+1:02d}</text>')
            parts.append(label_text(x + cell_width / 2, 298, label, centered=True, width_chars=15))
            parts.append(f'<path d="M{x + cell_width / 2:.1f} 330V720" stroke="#8F948F" stroke-width="2"/>')
        for row, rail_label in enumerate(rail_labels):
            y = 405 + row * 135
            parts.append(f'<rect x="70" y="{y - 43}" width="1460" height="86" rx="43" fill="{"#E3E6E4" if row % 2 else "#F8F7F3"}" stroke="#232523" stroke-width="2"/>')
            parts.append(f'<rect x="70" y="{y - 43}" width="260" height="86" rx="43" fill="#171917"/>')
            parts.append(f'<text x="200" y="{y + 7}" class="hub-small center">{rail_label}</text>')
            for i in range(len(labels)):
                cx = start_x + i * (cell_width + gap) + cell_width / 2
                parts.append(f'<circle cx="{cx:.1f}" cy="{y}" r="15" fill="{"#CFFF00" if (i + row) % 2 == 0 else "#171917"}"/>')
        parts.append('<path d="M230 747H1370" stroke="#232523" stroke-width="3" marker-end="url(#a)"/>')
    elif family == "argument":
        # N35 is not a network of equivalent concepts.  Its invariant core is
        # a vertical argument, while audience and objection exert different
        # pressures from opposite sides.
        core = labels[1:4]
        for i, label in enumerate(core):
            y = 300 + i * 175
            fill = "#171917" if i == 0 else ("#E3E6E4" if i == 1 else "#F8F7F3")
            parts.append(f'<rect x="595" y="{y}" width="410" height="125" rx="7" fill="{fill}" stroke="#232523" stroke-width="2"/>')
            parts.append(f'<text x="630" y="{y+40}" class="{"hub-small" if i == 0 else "n"}">{i+2:02d}</text>')
            if i == 0:
                wrapped = textwrap.wrap(label, width=18, break_long_words=False, break_on_hyphens=False) or [label]
                tspans = "".join(f'<tspan x="800" y="{y+82 + line_index * 31}">{html.escape(line)}</tspan>' for line_index, line in enumerate(wrapped))
                parts.append(f'<text class="hub center">{tspans}</text>')
            else:
                parts.append(label_text(800, y+82, label, centered=True, width_chars=18))
            if i:
                parts.append(f'<path d="M800 {y-50}V{y-8}" class="edge"/>')
        side_data = ((labels[0], 280, 420), (labels[4], 1320, 545))
        for i, (label, x, y) in enumerate(side_data):
            parts.append(f'<rect x="{x-175}" y="{y-72}" width="350" height="144" rx="72" fill="{"#F8F7F3" if i == 0 else "#E3E6E4"}" stroke="#232523" stroke-width="2"/>')
            parts.append(f'<text x="{x}" y="{y-25}" class="n center">{1 if i == 0 else 5:02d}</text>{label_text(x, y+28, label, centered=True, width_chars=18)}')
            if i == 0:
                parts.append('<path d="M455 420H545V362H585" class="edge faint"/>')
            else:
                parts.append('<path d="M1145 545H1015" class="edge faint"/>')
        parts.append('<path d="M560 785H1040L1014 812H534Z" fill="#CFFF00"/>')
    elif family == "learning-ledger":
        # N36 uses two registers rather than a circular arrow: what the team
        # did and what the surprise obliges it to reconsider.
        top = labels[:3]
        bottom = labels[3:]
        parts.append('<rect x="80" y="260" width="1440" height="220" rx="8" fill="#F8F7F3" stroke="#232523" stroke-width="2"/>')
        parts.append('<rect x="80" y="535" width="1440" height="220" rx="8" fill="#E3E6E4" stroke="#232523" stroke-width="2"/>')
        parts.append('<rect x="80" y="260" width="225" height="220" fill="#171917"/><rect x="80" y="535" width="225" height="220" fill="#171917"/>')
        parts.append('<text x="192" y="345" class="hub center">QUÉ</text><text x="192" y="388" class="hub center">HICIMOS</text>')
        parts.append('<text x="192" y="620" class="hub center">QUÉ</text><text x="192" y="663" class="hub center">REVISAMOS</text>')
        top_xs = (470, 850, 1230)
        for i, label in enumerate(top):
            x = top_xs[i]
            parts.append(f'<circle cx="{x}" cy="370" r="78" fill="{"#E3E6E4" if i % 2 else "#F8F7F3"}" stroke="#232523" stroke-width="2"/>')
            parts.append(f'<text x="{x}" y="345" class="n center">{i+1:02d}</text>{label_text(x, 392, label, centered=True, width_chars=14)}')
            if i:
                parts.append(f'<path d="M{top_xs[i-1]+88} 370H{x-88}" class="edge"/>')
        bottom_xs = (610, 1110)
        for i, label in enumerate(bottom):
            x = bottom_xs[i]
            parts.append(f'<path d="M{x-145} 590H{x+145}L{x+115} 705H{x-175}Z" fill="{"#F8F7F3" if i == 0 else "#CFFF00"}" stroke="#232523" stroke-width="2"/>')
            parts.append(f'<text x="{x-115}" y="625" class="n">{i+4:02d}</text>{label_text(x, 670, label, centered=True, width_chars=17)}')
        parts.append('<path d="M1230 458V510H610V575" class="edge"/>')
        parts.append('<path d="M765 647H955" class="edge"/>')
    else:  # bridge
        midpoint = (len(labels) + 1) // 2
        for i, label in enumerate(labels):
            left = i < midpoint
            x = 105 if left else 1135
            y = 285 + (i if left else i-midpoint) * 170
            parts.append(f'<rect x="{x}" y="{y}" width="360" height="125" rx="6" fill="#F8F7F3" stroke="#232523" stroke-width="2"/>')
            parts.append(f'<text x="{x+22}" y="{y+38}" class="n">{i+1:02d}</text>{label_text(x+22, y+86, label, width_chars=20)}')
            target_x = 690 if left else 910
            parts.append(f'<path d="M{x+360 if left else x} {y+62} H{target_x}" class="edge faint"/>')
        parts.append('<path d="M665 305h270v360H665z" fill="#171917"/><path d="M715 468h170" stroke="#CFFF00" stroke-width="10"/><text x="800" y="420" class="hub center">CONTRASTE</text><text x="800" y="525" class="hub-small center">EVIDENCIA</text>')

    joined_labels = ", ".join(labels).lower()
    claim_templates = {
        "sequence": f"{title} ordena {joined_labels} para localizar dónde una promesa cambia de estado y quién debe responder por ese pasaje.",
        "cycle": f"{title} muestra cómo {joined_labels} regresan a una decisión que puede revisarse con nueva evidencia.",
        "layers": f"{title} separa {joined_labels} para impedir que una capa oculte las obligaciones de las demás.",
        "hub": f"{title} sitúa {joined_labels} alrededor de una relación común y vuelve visibles sus dependencias.",
        "matrix": f"{title} contrasta {joined_labels} sin reducir dimensiones diferentes a una única escala.",
        "staircase": f"{title} dispone {joined_labels} como compromisos progresivos, cada uno condicionado por el anterior.",
        "constellation": f"{title} conecta {joined_labels} como un sistema de relaciones que no admite una lectura lineal única.",
        "bridge": f"{title} enfrenta {joined_labels} para mostrar qué evidencia permite atravesar el desacuerdo.",
        "traceability": f"{title} cruza {joined_labels} con controles de coherencia, trazabilidad y revisión para reconstruir una intervención completa.",
        "argument": f"{title} organiza {joined_labels} como un argumento situado que debe responder a evidencia, garantías, objeciones y audiencias.",
        "learning-ledger": f"{title} registra {joined_labels} en dos planos y distingue lo que ocurrió de lo que debe revisarse en el marco de acción.",
    }
    claim = claim_templates[family]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="t d"><title id="t">{escaped_title}</title><desc id="d">{html.escape(claim)}</desc><style>.l{{font:400 28px Didot,Georgia,serif;fill:#171917}}.n{{font:700 18px Avenir,Arial,sans-serif;letter-spacing:2px;fill:#535753}}.center{{text-anchor:middle}}.edge{{fill:none;stroke:#232523;stroke-width:3;marker-end:url(#a)}}.faint{{opacity:.55}}.hub{{font:400 28px Didot,Georgia,serif;fill:#F8F7F3}}.hub-small{{font:700 16px Avenir,Arial,sans-serif;letter-spacing:3px;fill:#CFFF00}}</style><rect width="1600" height="900" fill="#F8F7F3"/>{defs}<path d="M60 96H1540" stroke="#232523" stroke-width="3"/><path d="M60 57h170l-22 25H38z" fill="#CFFF00"/><text x="60" y="165" font-family="Didot,Georgia,serif" font-size="54">{escaped_title}</text>{''.join(parts)}<path d="M60 832H1540" stroke="#8F948F" stroke-width="2"/><text x="60" y="873" font-family="Avenir,Arial,sans-serif" font-size="20" fill="#555">METSI · N{number:02d} · {family.upper()} · MAPA {index:02d}</text></svg>'''
    target.write_text(svg, encoding="utf-8")
    return {"file": f"diagrams/{target.name}", "title": title, "labels": labels, "claim": claim, "family": family, "sha256": sha(target)}


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
    symbols = [
        '<path d="M8 24h32M24 8v32"/><circle cx="24" cy="24" r="15"/>',
        '<path d="M8 34L21 21l8 8L41 11"/><circle cx="8" cy="34" r="2"/><circle cx="41" cy="11" r="2"/>',
        '<rect x="8" y="10" width="32" height="28"/><path d="M8 20h32M20 10v28"/>',
        '<path d="M7 24h12l5-12 7 24 5-12h5"/>',
        '<circle cx="14" cy="24" r="7"/><circle cx="34" cy="24" r="7"/><path d="M21 24h6"/>',
        '<path d="M9 36V12h30v24zM15 30l7-8 6 5 6-9"/>',
        '<path d="M8 14h32M8 24h23M8 34h15"/><circle cx="38" cy="24" r="3"/>',
        '<path d="M24 7v10M24 31v10M7 24h10M31 24h10"/><circle cx="24" cy="24" r="7"/>',
    ]
    items = []
    for index, label in enumerate(labels, 1):
        items.append(
            f'<div><svg viewBox="0 0 48 48" aria-hidden="true">{symbols[(index - 1) % len(symbols)]}</svg>'
            f'<span>{html.escape(base.sentence(label, 42))}</span></div>'
        )
    return f'<aside class="icon-strip" aria-label="Ocho distinciones de la lectura">{"".join(items)}</aside>'


def build(number: int) -> dict:
    source = SOURCES[number]
    title, parsed_sections = base.parse_source(source)
    all_sections = coalesce_editorial_sections(number, parsed_sections)
    # The previous approved package is the immutable visual baseline. v9 receives
    # copies of its assets and never mutates the published package in place.
    legacy = ROOT / f"N{number:02d}-v{BASELINE_VERSION}-editorial"
    legacy_assets = legacy / "assets"
    out = ROOT / f"N{number:02d}-v{PACKAGE_VERSION}-editorial"
    assets, diagrams, output, source_dir = (out / "assets", out / "diagrams", out / "output", out / "source")
    # A rebuilt package must be a closed snapshot.  Removing only the generated
    # subdirectories prevents portraits or diagrams from an earlier iteration
    # from surviving invisibly beside the current manifest.
    for folder in (assets, diagrams, output, source_dir):
        if folder.exists():
            shutil.rmtree(folder)
    for folder in (assets, diagrams, output, source_dir):
        folder.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, source_dir / source.name)
    if not valid_raster(MATCHES):
        raise FileNotFoundError(f"Cierre canónico inválido: {MATCHES}")
    shutil.copy2(MATCHES, assets / "matches-close.png")
    if not valid_raster(HOTEL_HORIZONTE):
        raise FileNotFoundError(f"Ancla canónica de Hotel Horizonte inválida: {HOTEL_HORIZONTE}")
    hotel_horizonte_asset = assets / "hotel-horizonte-canonical.png"
    shutil.copy2(HOTEL_HORIZONTE, hotel_horizonte_asset)
    cover_source = SPECIAL_COVERS.get(number, legacy_assets / "cover-source-premium-bw-v1.png")
    if not valid_raster(cover_source):
        raise FileNotFoundError(cover_source)
    cover = assets / "cover-source-premium-bw-v2.png" if number in SPECIAL_COVERS else assets / cover_source.name
    shutil.copy2(cover_source, cover)
    for pause_index, name in enumerate(("pause-01.png", "pause-02.png"), 1):
        source_pause = PREMIUM_PAUSE_OVERRIDES.get(number, {}).get(pause_index, legacy_assets / name)
        if not valid_raster(source_pause):
            raise FileNotFoundError(source_pause)
        target_pause = assets / name
        if pause_index in PREMIUM_PAUSE_OVERRIDES.get(number, {}):
            with Image.open(source_pause) as image:
                prepared = ImageOps.exif_transpose(image).convert("RGB")
                prepared = ImageEnhance.Color(prepared).enhance(0.42)
                prepared = ImageEnhance.Contrast(prepared).enhance(1.03)
                prepared.save(target_pause, format="PNG", optimize=True)
        else:
            shutil.copy2(source_pause, target_pause)
    support = support_assets(number, legacy_assets, assets)
    # The Contents page is a neutral navigation apparatus. Produce a real
    # grayscale derivative instead of a CSS filter: Chrome preserves the img
    # element and its semantic alternate text in the tagged PDF.
    contents_source = support[0]
    contents_target = assets / "contents-neutral.png"
    with Image.open(contents_source) as image:
        prepared_contents = ImageOps.exif_transpose(image).convert("L").convert("RGB")
        prepared_contents = ImageEnhance.Contrast(prepared_contents).enhance(1.02)
        prepared_contents.save(contents_target, format="PNG", optimize=True)
    support[0] = contents_target
    story_asset: Path | None = None
    story_alt = "Una profesional argentina contrasta un cronograma cumplido con evidencia de una operación que exige revisar el plan."
    if number == 17:
        story_source = SUPPORT_ROOT / "N17-story-resolution.png"
        if not valid_raster(story_source):
            raise FileNotFoundError(f"Fotografía narrativa N17 inválida: {story_source}")
        story_asset = assets / "story-resolution.png"
        shutil.copy2(story_source, story_asset)

    referents_section = next(s for s in all_sections if s.title == "Referentes")
    references_section = next(s for s in all_sections if s.title == "Referencias base")
    referents_page, portrait_records = build_referents(
        number, referents_section, references_section, assets, legacy_assets
    )
    sections = [s for s in all_sections if s.title != "Referentes"]
    references = base.references(all_sections)
    thesis_section = next(s for s in sections if s.title == "Tesis")
    thesis = base.first_paragraph(thesis_section)

    # One diagram is selected by default for the document's central explanatory
    # need.  N30 adds one different, source-grounded sequence because its
    # observability argument requires both the system map and the action chain.
    # The former quota of three ornamental diagrams remains retired.
    diagram_target = diagrams / f"N{number:02d}-mapa-01.svg"
    if number in APPROVED_INFOGRAPHICS:
        approved_spec = APPROVED_INFOGRAPHICS[number]
        approved_root = APPROVED_INFOGRAPHIC_ROOT / f"N{number:02d}"
        approved_asset = approved_root / approved_spec["file"]
        diagram_target = diagrams / f"N{number:02d}-mapa-01{approved_asset.suffix.lower()}"
        approved_manifest_path = approved_root / "content-manifest.json"
        approved_alt_path = approved_root / "alt-text.md"
        for required in (approved_asset, approved_manifest_path, approved_alt_path):
            if not required.is_file():
                raise FileNotFoundError(f"Activo editorial aprobado ausente: {required}")
        shutil.copy2(approved_asset, diagram_target)
        manifest_target = diagrams / f"N{number:02d}-mapa-01-content-manifest.json"
        alt_target = diagrams / f"N{number:02d}-mapa-01-alt-text.md"
        shutil.copy2(approved_manifest_path, manifest_target)
        shutil.copy2(approved_alt_path, alt_target)
        approved_manifest = json.loads(approved_manifest_path.read_text(encoding="utf-8"))
        diagram_records = [{
            "file": f"diagrams/{diagram_target.name}",
            "title": approved_manifest["title"],
            "labels": [node["label"] for node in approved_manifest["nodes"]],
            "claim": approved_manifest["claim"],
            "caption": approved_spec["caption"],
            "family": approved_spec["family"],
            "sha256": sha(diagram_target),
            "approved": True,
            "source_manifest": f"diagrams/{manifest_target.name}",
            "alt_text": f"diagrams/{alt_target.name}",
        }]
    else:
        diagram_title, diagram_labels = DIAGRAMS[number][0]
        diagram_records = [diagram_svg(
            number,
            1,
            diagram_title,
            diagram_labels,
            diagram_target,
            forced_family=DOCUMENT_DIAGRAM_FAMILIES[number],
        )]
    if number == 30:
        diagram_records.append(diagram_svg(
            number,
            2,
            "Del síntoma a la acción segura",
            ["Señal", "Contexto", "Impacto", "Autoridad", "Acción", "Revisión"],
            diagrams / "N30-mapa-02.svg",
            forced_family="sequence",
        ))

    entries: list[dict] = []
    title_id = base.source_block(entries, f"N{number:02d}-h1", "heading-1", clean_title(number, title))
    body_chunks: list[str] = []
    rendered_section = 0
    diagram_cursor = 0
    first_pause_after = 1
    # The second pause closes the three-movement sequence.  Interrupting it
    # after Movimiento 2 expelled the final lines of that section onto nearly
    # empty pages in several documents.
    second_pause_after = 9
    pause_map = {
        first_pause_after: ("pause-01.png", FIRST_PAUSE_QUOTES[number], PHOTO_ALTS[number][1]),
        second_pause_after: ("pause-02.png", "", PHOTO_ALTS[number][2]),
    }
    second_quote_section = next((s for s in sections if s.title == "Límites y tensiones"), thesis_section)
    pause_map[second_pause_after] = ("pause-02.png", complete_pullquote(base.first_paragraph(second_quote_section)), PHOTO_ALTS[number][2])

    article_open = False
    pending_handoff_html = ""
    pending_consequences_html = ""
    pending_pills_html = ""
    deferred_infographic_html = ""

    def open_article() -> None:
        nonlocal article_open
        if not article_open:
            body_chunks.append('<article class="reading">')
            article_open = True

    def close_article() -> None:
        nonlocal article_open
        if article_open:
            body_chunks.append("</article>")
            article_open = False

    for index, section in enumerate(sections, 1):
        rendered_section += 1
        prefix = f"N{number:02d}-s{rendered_section:02d}"
        heading_id = base.source_block(entries, f"{prefix}-h2", "heading-2", section.title)
        section_body = base.render_markdown(section.lines, prefix, entries)
        section_body = add_breaks_to_encoded_url_segments(section_body)
        if number >= 17:
            section_body = section_body.replace("</ol><ol>", "").replace("</ul><ul>", "")
        section_body = re.sub(r"\bHH-(\d+)\b", r'<span class="identifier">HH-\1</span>', section_body)
        classes = base.section_classes(number, rendered_section, section.title)
        movement_number = 0
        if index == 1:
            classes += ["block-c-question"]
        if section.title.startswith("Movimiento"):
            classes += ["block-c-movement", "two-column"]
            movement_match = re.match(r"Movimiento\s+([123])", section.title)
            if movement_match:
                movement_number = int(movement_match.group(1))
                classes += [f"movement-{movement_number}"]
        if section.title == "Síntesis":
            classes += ["two-column", "block-c-synthesis"]
        if section.title == "Tesis":
            classes += ["block-c-thesis"]
            if number in APPROVED_INFOGRAPHICS:
                classes += ["thesis-with-approved-plate"]
        if section.title == "Errores frecuentes":
            classes += ["block-c-errors"]
            section_body = wrap_error_cards(section_body)
        if section.title == "Consecuencias profesionales":
            classes += ["block-c-consequences"]
        if section.title == "Límites y tensiones":
            classes += ["block-c-limits"]
        if section.title == "Referencias base":
            classes += ["block-c-references"]
        if section.title.startswith("De N") or section.title == "Después de N36":
            classes += ["block-c-handoff"]
            classes += ["block-c-handoff-in" if index == 5 else "block-c-handoff-out"]
        marker = (
            f'<div class="section-marker"><span>{rendered_section:02d}</span>'
            f'<b>METSI · N{number:02d} <em>{route_for(number, index, section.title)}</em></b></div>'
        )
        heading_icon = base.case_application_icon() if "hotel-case" in classes else ""
        before_body = ""
        after_body = ""
        after_section = ""
        hotel_voices_html = ""
        hotel_bridge_html = ""
        hotel_continuation_photo = ""
        is_hotel_case = "hotel-case" in classes
        hotel_word_count = len(re.findall(r"\b\w+\b", re.sub(r"<[^>]+>", " ", section_body))) if is_hotel_case else 0
        is_long_hotel_case = is_hotel_case and hotel_word_count >= 500
        is_medium_hotel_case = is_hotel_case and 240 <= hotel_word_count < 500
        if is_long_hotel_case:
            classes += ["hotel-case-long"]
        elif is_medium_hotel_case:
            classes += ["hotel-case-medium"]
        if number == 17 and index == 2 and story_asset is not None:
            after_body += photo_band(
                story_asset,
                story_alt,
                "La evidencia del trabajo real obliga a revisar incluso un plan ejecutado según lo previsto.",
                "story-resolution-photo",
            )
        if section.title == "Tesis":
            if diagram_cursor < len(diagram_records):
                diagram = diagram_records[diagram_cursor]
                if number in APPROVED_INFOGRAPHICS:
                    infographic_markup = (
                        f'<section class="approved-infographic-page{' n34-full-plate' if number == 34 else ''}">'
                        '<header>'
                        f'<span>METSI · N{number:02d} · MAPA DE DECISIÓN</span>'
                        f'<p>{html.escape(diagram["claim"])}</p>'
                        '</header>'
                        f'<figure><img src="{diagram["file"]}" alt="{html.escape(diagram["claim"])}">'
                        f'<figcaption>{html.escape(diagram.get("caption", diagram["claim"]))}</figcaption>'
                        '</figure></section>'
                    )
                    if number in DEFERRED_INFOGRAPHIC_DOCS:
                        # The N34 plate carries more semantic density than a
                        # compact thesis companion can sustain.  Let the thesis
                        # share its page with the short bridge that follows and
                        # give the diagram a true full-page reading surface.
                        deferred_infographic_html = infographic_markup
                    else:
                        after_section += infographic_markup
                else:
                    after_body += (
                        f'<figure class="infographic block-c-infographic thesis-map"><img src="{diagram["file"]}" alt="{html.escape(diagram["claim"])}">'
                        f'<figcaption>{html.escape(diagram.get("caption", diagram["claim"]))}</figcaption></figure>'
                    )
                diagram_cursor += 1
        if section.title.startswith("Movimiento 3") and diagram_cursor < len(diagram_records):
            diagram = diagram_records[diagram_cursor]
            before_body += (
                f'<figure class="infographic block-c-infographic"><img src="{diagram["file"]}" alt="{html.escape(diagram["claim"])}">'
                f'<figcaption>{html.escape(diagram.get("caption", diagram["claim"]))}</figcaption></figure>'
            )
            diagram_cursor += 1
        # The preparation page is a stable typographic apparatus. Photography
        # belongs to the full-page pauses, not inside the questions panel.
        section_styles: list[str] = []
        if section.title == "Glosario esencial":
            glossary_entries = sum(1 for line in section.lines if line.strip().startswith("**"))
            glossary_rows = max(1, (glossary_entries + 1) // 2)
            section_styles.append(f"--glossary-rows:{glossary_rows}")
        if section.title == "Referencias base":
            reference_entries = section_body.count("<li")
            reference_rows = max(1, (reference_entries + 1) // 2)
            section_styles.append(f"--reference-rows:{reference_rows}")
        if section.title == "Errores frecuentes":
            error_entries = section_body.count('class="error-card"')
            error_rows = max(1, (error_entries + 1) // 2)
            section_styles.append(f"--error-rows:{error_rows}")
        section_attrs = f' style="{";".join(section_styles)}"' if section_styles else ""
        lead_body = ""
        movement_close_html = ""
        if is_hotel_case or section.title == "Tesis" or section.title.startswith("Movimiento") or section.title == "Consecuencias profesionales":
            lead_body, section_body = split_lead_html(section_body)
        if (number, movement_number) in MOVEMENT_EDITORIAL_CLOSES:
            section_body, movement_close_html = split_last_subsection_as_editorial_close(
                section_body,
                (number + movement_number) % 3,
                MOVEMENT_CLOSE_RETAIN_WORDS.get((number, movement_number), 0),
                MOVEMENT_CLOSE_SUBSECTIONS.get((number, movement_number), 1),
            )
        if section.title.startswith("Movimiento 2"):
            if number in MOVEMENT_THREE_PHOTO_DOCS:
                before_body += photo_band(
                    support[3], SUPPORT_ALTS[number][3],
                    "El registro del trabajo real permite contrastar la decisión con sus condiciones de operación.",
                    "movement-two-photo",
                )
            else:
                before_body += photo_diptych(
                    support[3], SUPPORT_ALTS[number][3], support[4], SUPPORT_ALTS[number][4],
                    "Dos registros del trabajo real permiten contrastar la decisión con sus condiciones de operación.",
                    "movement-two-photo",
                )
        if section.title == "Errores frecuentes":
            after_body += photo_band(
                support[5], SUPPORT_ALTS[number][5],
                "La escena de operación permite reconocer el error por sus efectos antes de convertirlo en una explicación cómoda.",
                "errors-photo",
            )
        if section.title == "Síntesis":
            after_body += photo_band(
                support[6], SUPPORT_ALTS[number][6],
                "La imagen reúne la tensión central de la lectura y conserva abierta la decisión que sigue.",
                "synthesis-photo",
            )
        if is_hotel_case:
            # The case reads as a two-page editorial unit.  A first argument
            # accompanies the documentary photograph; the stable six-role
            # panel then opens the continuation before the remaining prose.
            # This prevents the people who sustain Hotel Horizonte from being
            # expelled to an isolated third page in the longer readings.
            hotel_bridge_parts: list[str] = []
            for _ in range(2 if is_long_hotel_case else 1):
                hotel_bridge_part, remaining_body = split_lead_html(section_body)
                if not hotel_bridge_part:
                    break
                hotel_bridge_parts.append(hotel_bridge_part)
                section_body = remaining_body
            hotel_bridge = "".join(hotel_bridge_parts)
            before_body += photo_band(
                hotel_horizonte_asset,
                "Cartel luminoso de HOTEL recortado en diagonal sobre una fachada oscura.",
                "Hotel Horizonte conserva una misma escena para que cambie el análisis y no el caso.",
                "hotel-primary-photo hotel-canonical-anchor",
            )
            if hotel_bridge:
                hotel_bridge_html = f'<div class="section-body hotel-bridge">{hotel_bridge}</div>'
            hotel_tail_paragraphs = max(1, section_body.count("<p"))
            classes += [f"hotel-tail-{min(3, hotel_tail_paragraphs)}"]
            hotel_voices_html = build_hotel_voices(number, assets)
        if section.title != "Errores frecuentes":
            section_body = wrap_subsection_units(section_body)
        if movement_close_html:
            section_body += movement_close_html
        lead_html = f'<div class="section-body section-lead">{lead_body}</div>' if lead_body else ""
        if is_hotel_case:
            # Long cases need true newspaper flow so a complete paragraph does
            # not get expelled to a third page.  Shorter cases keep explicit
            # paragraph groups because their reading order already fits.
            hotel_columns = (
                section_body
                if is_long_hotel_case or is_medium_hotel_case
                else wrap_hotel_text_columns(section_body, min(3, max(1, section_body.count("<p"))))
            )
            body_html = (
                f'{before_body}{hotel_bridge_html}<div class="hotel-continuation">{hotel_voices_html}'
                f'<div class="section-body hotel-continuation-body">{hotel_columns}</div>'
                f'</div>'
            )
        else:
            body_html = f'{before_body}<div class="section-body">{section_body}</div>'
        section_core = (
            f'<section class="{" ".join(dict.fromkeys(classes))}" id="section-{rendered_section:02d}" data-section="{rendered_section:02d}"{section_attrs}>'
            f'<div class="section-heading">{marker}{heading_icon}<h2 data-source-id="{heading_id}">{html.escape(section.title)}</h2></div>'
            f'{lead_html}{body_html}{after_body}</section>'
        )
        section_html = (
            f'<div class="thesis-infographic-page">{section_core}{after_section}</div>'
            if section.title == "Tesis" and after_section
            else f'{section_core}{after_section}'
        )
        if number in DEFERRED_INFOGRAPHIC_DOCS and index == 5 and deferred_infographic_html:
            section_html += deferred_infographic_html
            deferred_infographic_html = ""
        if index == 1:
            close_article()
            body_chunks.append(section_html)
        else:
            open_article()
            if "block-c-consequences" in classes:
                pending_consequences_html = section_html
            elif pending_consequences_html and "block-c-limits" in classes:
                consequence_photo = ""
                wrapper_class = "consequences-limits-page"
                if number in CONSEQUENCE_PHOTO_DOCS:
                    wrapper_class += " has-consequence-photo"
                    consequence_photo = photo_band(
                        support[2], SUPPORT_ALTS[number][2],
                        "La evidencia material devuelve las consecuencias y los límites a una situación de trabajo concreta.",
                        "consequence-photo",
                    )
                body_chunks.append(
                    f'<div class="{wrapper_class}">{pending_consequences_html}{section_html}{consequence_photo}</div>'
                )
                pending_consequences_html = ""
            elif "pill-summary" in classes:
                pending_pills_html = section_html
            elif pending_pills_html and "glossary-two-column" in classes:
                body_chunks.append(
                    f'<div class="pills-glossary-page">{pending_pills_html}{section_html}</div>'
                )
                pending_pills_html = ""
            elif "block-c-handoff-out" in classes:
                pending_handoff_html = section_html
            elif pending_handoff_html and section.title == "Síntesis":
                body_chunks.append(
                    f'<div class="handoff-synthesis-page">{pending_handoff_html}{section_html}</div>'
                )
                pending_handoff_html = ""
            else:
                if pending_consequences_html:
                    body_chunks.append(pending_consequences_html)
                    pending_consequences_html = ""
                if pending_pills_html:
                    body_chunks.append(pending_pills_html)
                    pending_pills_html = ""
                if pending_handoff_html:
                    body_chunks.append(pending_handoff_html)
                    pending_handoff_html = ""
                body_chunks.append(section_html)
        if index in pause_map:
            file, quote, alt = pause_map[index]
            close_article()
            body_chunks.append(
                f'<section class="full-bleed full-bleed-quote block-c-pause"><img src="assets/{file}" alt="{html.escape(alt)}">'
                f'<p>{html.escape(quote)}</p></section>'
            )
    for pending_html in (pending_consequences_html, pending_handoff_html, pending_pills_html, deferred_infographic_html):
        if pending_html:
            body_chunks.append(pending_html)
    close_article()

    visible_sections = [s for s in sections if s.title != "Referencias base"]
    content_items = ['<li class="contents-unnumbered"><b>•</b><span>Referentes <small>SIN NUM.</small></span></li>']
    for index, section in enumerate(visible_sections, 1):
        content_items.append(f'<li><b>{index:02d}</b><span>{html.escape(section.title)}</span></li>')
    content_items.append('<li class="contents-unnumbered"><b>•</b><span>Referencias base <small>SIN NUM.</small></span></li>')
    contents = (
        f'<section class="front-page contents-page contents-page-text-only block-c-contents"><header><span>METSI · N{number:02d}</span>'
        f'<h2>Contenido</h2><p>{html.escape(clean_title(number, title))}</p>'
        f'<p class="contents-route"><b>Ruta de lectura:</b> problema, distinciones, decisiones, prueba, transferencia y preparación.</p></header>'
        f'<div class="contents-layout"><ol>{"".join(content_items)}</ol>'
        f'<figure class="contents-photo"><div class="contents-photo-viewport"><img'
        f'{" class=\"editorial-contact-sheet\"" if support[0].name == "editorial-support-sheet.png" else ""}'
        f' src="assets/{support[0].name}" alt="{html.escape(SUPPORT_ALTS[number][0])}"></div>'
        '<figcaption>Una lectura previa para llegar al encuentro con preguntas, evidencia y una decisión revisable.</figcaption></figure></div>'
        f'<p class="contents-sinnum-note"><b>Nota.</b> SIN NUM. identifica aparatos de orientación y referencia.</p></section>'
    )
    closing_alt = "Diez fósforos dispuestos en secuencia vertical, desde intactos hasta consumidos y convertidos en ceniza."
    closing_caption = "La secuencia vuelve visible que toda intervención consume recursos, deja huellas y necesita un criterio de cierre."
    cover_markup = base.cover_html(number, title, COVER_PULL_QUOTES[number], cover.name, title_id)
    cover_markup = re.sub(
        r'alt="[^"]*"',
        f'alt="{html.escape(COVER_ALTS[number])}"',
        cover_markup,
        count=1,
    )
    html_text = (
        '<!doctype html><html lang="es-AR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<meta name="description" content="Lectura previa METSI N{number:02d}, FCE UBA"><title>{html.escape(title)}</title>'
        '<link rel="stylesheet" href="magazine.css"></head>'
        f'<body class="premium-magazine document-n{number:02d} block-c editorial-variant-{((number - 11) % 6) + 1}"><main>'
        f'{cover_markup}{contents}{referents_page}'
        f'{"".join(body_chunks)}'
        f'<section class="full-bleed closing-image"><img src="assets/matches-close.png" alt="{html.escape(closing_alt)}">'
        f'<figcaption>{html.escape(closing_caption)}</figcaption></section></main></body></html>'
    )
    (out / "index.html").write_text(html_text, encoding="utf-8")

    stable_css = (ROOT / "N10-v9-final" / "magazine.css").read_text(encoding="utf-8")
    css = stable_css + "\n\n" + BLOCK_C_CSS + "\n\n" + V8_EDITORIAL_CORRECTIONS + "\n\n" + V9_N34_CORRECTIONS
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
        "content_audit": "plain-language-canonical-source-audited-pass",
        "editorial_spine": "academic-content-revision-n11-n36-audited-pass",
        "cover": {"file": cover.name, "source": f"assets/{cover.name}", "sha256": sha(cover), "alt": COVER_ALTS[number], "photographic_origin": "native_black_and_white", "render_treatment": "no_grayscale_conversion"},
        "internal_images": ["pause-01.png", "pause-02.png", hotel_horizonte_asset.name] + sorted({path.name for path in support}) + ([story_asset.name] if story_asset else []),
        "image_manifest": [
            {"file": f"assets/pause-01.png", "sha256": sha(assets / "pause-01.png"), "alt": PHOTO_ALTS[number][1], "role": "full_page_pause", "saturation_review": "neutral", "treatment": "none", "rights_status": "project_bound_generated_media"},
            {"file": f"assets/pause-02.png", "sha256": sha(assets / "pause-02.png"), "alt": PHOTO_ALTS[number][2], "role": "full_page_pause", "saturation_review": "restrained-accent" if 2 in PREMIUM_PAUSE_OVERRIDES.get(number, {}) else "neutral", "treatment": "natural_desaturated_color" if 2 in PREMIUM_PAUSE_OVERRIDES.get(number, {}) else "none", "rights_status": "project_bound_generated_media"},
            {"file": f"assets/{hotel_horizonte_asset.name}", "sha256": sha(hotel_horizonte_asset), "alt": "Cartel luminoso de HOTEL recortado en diagonal sobre una fachada oscura.", "role": "hotel_horizonte_canonical_anchor", "saturation_review": "restrained-accent", "treatment": "natural_desaturated_color", "rights_status": "project_authorized_fixed_asset"},
        ] + ([{
            "file": f"assets/{story_asset.name}",
            "sha256": sha(story_asset),
            "alt": story_alt,
            "role": "story_resolution",
            "saturation_review": "neutral",
            "treatment": "none",
            "rights_status": "project_bound_generated_media",
        }] if story_asset else []) + [
            {
                "file": f"assets/hotel-{filename}",
                "sha256": sha(assets / f"hotel-{filename}"),
                "alt": "",
                "role": "hotel_horizonte_character",
                "saturation_review": "neutral",
                "treatment": "grayscale",
                "rights_status": "project_authorized_character_asset",
            }
            for name, _role, filename in HOTEL_CHARACTERS
        ] + [
            {
                "file": f"assets/{path.name}",
                "sha256": sha(path),
                "alt": SUPPORT_ALTS[number][index - 1],
                "role": (
                    "contents_editorial",
                    "hotel_evidence_primary",
                    "problem_or_consequences_evidence",
                    "movement_two_evidence",
                    "movement_three_or_diptych_evidence",
                    "errors_evidence",
                    "synthesis_evidence",
                    "preparation",
                )[index - 1],
                "saturation_review": "restrained-accent" if (index - 1) in PREMIUM_COLOR_OVERRIDES.get(number, {}) else "neutral",
                "treatment": "natural_restrained_color" if (index - 1) in PREMIUM_COLOR_OVERRIDES.get(number, {}) else "none",
                "rights_status": "project_bound_generated_media" if valid_raster(SUPPORT_ROOT / f"N{number:02d}-support-sheet.png") or any(valid_raster(candidate) for candidate in SUPPORT_ROOT.glob(f"N{number:02d}-support-{index:02d}.*")) else "layout_fallback_not_for_release",
                "contact_sheet_panel": index if path.name == "editorial-support-sheet.png" else None,
            }
            for index, path in enumerate(support, 1)
        ],
        "portrait_references": portrait_records,
        "diagrams": diagram_records,
        "quotes": [pause_map[first_pause_after][1], pause_map[second_pause_after][1]],
        "references": references,
        "closing": {"file": "matches-close.png", "sha256": sha(assets / "matches-close.png"), "alt": closing_alt, "caption": closing_caption, "folio": True, "footer": True},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "document.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (diagrams / "content-manifest.json").write_text(json.dumps({"document": f"N{number:02d}", "diagrams": diagram_records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    spread_units = [
        {"order": 1, "role": "cover", "layout": "full_bleed_cover"},
        {"order": 2, "role": "contents", "layout": "index_with_neutral_documentary_image"},
        {"order": 3, "role": "referents", "layout": "six_voice_portrait_grid"},
    ]
    order = 4
    for section in sections:
        if section.title == "Referencias base":
            continue
        spread_units.append({
            "order": order,
            "role": "section",
            "title": section.title,
            "layout": (
                "hotel_horizonte_spread" if "Hotel Horizonte" in section.title
                else "questions_typographic" if section.title == "Preguntas de preparación"
                else "synthesis_two_column" if section.title == "Síntesis"
                else "five_pills" if section.title == "Cinco píldoras para recordar"
                else "glossary" if section.title == "Glosario esencial"
                else "compact_thesis" if section.title == "Tesis"
                else "editorial_reading"
            ),
        })
        order += 1
    spread_units.extend([
        {"order": order, "role": "references", "layout": "two_column_reference_apparatus"},
        {"order": order + 1, "role": "closing", "layout": "full_bleed_matches"},
    ])
    (out / "spread-plan.json").write_text(json.dumps({
        "document": f"N{number:02d}",
        "version": f"v{PACKAGE_VERSION}",
        "source": f"source/{source.name}",
        "invariants": [
            "two_full_page_photographic_pauses",
            "questions_without_photography",
            "contents_image_neutral_black_and_white",
            "hotel_horizonte_canonical_anchor",
            "approved_document_specific_infographic",
            "full_bleed_matches_closing",
        ],
        "units": spread_units,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
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

/* METSI N11–N36 v2 · regression-safe editorial reset */
html,body.block-c,body.block-c main{margin:0!important;padding:0!important}
body.block-c main{overflow-x:hidden!important}
body.block-c{background:#FAFAF8;color:#171917}
body.block-c .cover-meta-eyebrow{display:flex!important;flex-direction:column!important;align-items:flex-start!important;gap:0!important;white-space:normal!important;line-height:1.2!important}
body.block-c .cover-meta-eyebrow span{display:block!important;white-space:nowrap!important}
body.block-c .collection-cover,
body.block-c .full-bleed,
body.block-c .closing-image,
body.block-c .reading-section[data-section="01"]{
  page:fullbleed!important;position:relative!important;left:0!important;top:0!important;
  box-sizing:border-box!important;width:210mm!important;height:297mm!important;
  min-width:210mm!important;min-height:297mm!important;max-width:none!important;max-height:none!important;
  margin:0!important;overflow:hidden!important;border:0!important;
  break-before:page!important;page-break-before:always!important;
  break-after:page!important;page-break-after:always!important
}
body.block-c .collection-cover>img,
body.block-c .full-bleed>img,
body.block-c .closing-image>img{
  position:absolute!important;inset:0!important;display:block!important;
  width:210mm!important;height:297mm!important;max-width:none!important;max-height:none!important;
  object-fit:cover!important;filter:none!important
}
body.block-c .collection-cover .cover-shade{position:absolute!important;inset:0!important;width:210mm!important;height:297mm!important}
body.block-c article.reading{page:content;margin:0!important;padding:0!important}
body.block-c .reading-section{box-sizing:border-box;min-height:0!important;height:auto!important;margin:0 0 5mm;padding-bottom:2mm;orphans:4;widows:4}
body.block-c .section-heading,body.block-c .section-heading h2{break-inside:avoid-page;page-break-inside:avoid;break-after:avoid-page;page-break-after:avoid}
body.block-c .section-body h3,body.block-c .section-body h4{break-after:avoid-page;page-break-after:avoid}
body.block-c .section-body h3+p,body.block-c .section-body h4+p{break-before:avoid-page;page-break-before:avoid}
body.block-c .reading-section[data-section="01"]{display:flex!important;flex-direction:column!important;justify-content:flex-end!important;padding:24mm!important;background:#191919!important;color:#F7F6F2!important}
body.block-c .reading-section[data-section="01"] .section-heading{display:block;margin:0 0 12mm;padding:0;border:0}
body.block-c .reading-section[data-section="01"] .section-marker,body.block-c .reading-section[data-section="01"] .section-marker span{color:#CFFF00!important;border-color:#CFFF00!important}
body.block-c .reading-section[data-section="01"] .section-body{max-width:155mm}
body.block-c .reading-section[data-section="01"] .section-body p{margin:0;color:#F7F6F2;font:400 28pt/1.08 Didot,"Bodoni 72",serif;letter-spacing:-.018em}

body.block-c .front-page{box-sizing:border-box;width:210mm!important;height:297mm!important;margin:0!important;break-after:page!important;page-break-after:always!important}
body.block-c .block-c-contents .contents-layout{display:grid!important;grid-template-columns:minmax(0,1.38fr) minmax(0,.62fr);gap:7mm;height:204mm;margin-top:4mm}
body.block-c .block-c-contents .contents-layout ol{min-width:0;columns:2;column-count:2;column-gap:6mm;margin:0;padding:0}
body.block-c .block-c-contents .contents-layout li{grid-template-columns:7mm 1fr;gap:1.2mm;padding:1.35mm 0;font-size:7.3pt;line-height:1.16}
body.block-c .block-c-contents .contents-layout figure{display:flex;flex-direction:column;align-self:end;height:92mm;margin:0;overflow:hidden;background:#D5D7D4}
body.block-c .contents-photo-viewport{position:relative;width:100%;height:65mm;overflow:hidden;background:#D5D7D4}
body.block-c .contents-photo-viewport>img:not(.editorial-contact-sheet){display:block;width:100%;height:65mm;object-fit:cover;filter:none}
body.block-c .contents-photo-viewport>img.editorial-contact-sheet{position:absolute!important;top:0!important;left:50%!important;width:auto!important;height:400%!important;max-width:none!important;max-height:none!important;object-fit:initial!important;transform:translateX(-25%)!important}
body.block-c .block-c-contents .contents-layout figure figcaption{padding:3mm 0 0;font:6.8pt/1.3 Avenir,sans-serif;color:#565A56}

body.block-c .authors-page{padding:16mm 18mm}
body.block-c .authors-page .contributors-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:4mm 5mm;margin-top:5mm}
body.block-c .authors-page .contributor{box-sizing:border-box;min-height:73mm!important;padding-bottom:3mm;border-bottom:.2mm solid #AAA;background:transparent}
body.block-c .portrait-frame{height:34mm;margin-bottom:2mm}
body.block-c .portrait-unavailable{grid-template-rows:1fr auto;font-size:24pt;background:#E4E6E3}
body.block-c .portrait-unavailable small{padding:0 2mm 2mm;font:600 4.7pt/1 Avenir,sans-serif;letter-spacing:.12em}
body.block-c .authors-page blockquote{margin:5mm 8mm 0;padding-top:3mm;font-size:13pt}

body.block-c .reading-section[data-section="02"]{min-height:0!important;height:auto!important;display:block!important;justify-content:initial!important;padding:6mm 8mm!important;background:#F0F1EE!important;border-left:1.5mm solid #CFFF00!important}
body.block-c .reading-section[data-section="02"] .section-body{columns:2;column-count:2;column-gap:8mm;column-rule:.2mm solid #C5C7C5;font-size:9.1pt;line-height:1.24}
body.block-c .editorial-photo-band{column-span:all;margin:4mm 0 5mm;break-inside:avoid-page;page-break-inside:avoid}
body.block-c .editorial-photo-band .photo-viewport{position:relative;width:100%;height:57mm;overflow:hidden;background:#D5D7D4}
body.block-c .editorial-photo-band .photo-viewport>img:not(.editorial-contact-sheet){display:block;width:100%;height:100%;object-fit:cover;filter:none!important}
body.block-c .editorial-photo-band .photo-viewport>img.editorial-contact-sheet{position:absolute!important;top:0;left:0;width:200%!important;height:auto!important;max-width:none!important;max-height:none!important;object-fit:initial!important;filter:none!important;transform-origin:top left!important}
body.block-c .hotel-photo img.editorial-contact-sheet{transform:translate(-50%,-5%)!important}
body.block-c .movement-photo img.editorial-contact-sheet{transform:translate(0,-30%)!important}
body.block-c .handoff-photo img.editorial-contact-sheet{transform:translate(-50%,-30%)!important}
body.block-c .consequence-photo img.editorial-contact-sheet{transform:translate(0,-55%)!important}
body.block-c .pills-photo img.editorial-contact-sheet{transform:translate(-50%,-55%)!important}
body.block-c .preparation-photo img.editorial-contact-sheet{transform:translate(0,-80%)!important}
body.block-c .story-resolution-photo img.editorial-contact-sheet{transform:translate(-50%,-80%)!important}
body.block-c .movement-photo .photo-viewport{height:66mm}
body.block-c .handoff-photo .photo-viewport{height:58mm}
body.block-c .pills-photo{margin-top:6mm}
body.block-c .pills-photo .photo-viewport{height:83mm}
body.block-c .synthesis-photo{margin-top:6mm}
body.block-c .synthesis-photo .photo-viewport{height:62mm}
body.block-c .preparation-photo{margin:7mm 0 0}
body.block-c .preparation-photo .photo-viewport{height:54mm}
body.block-c .story-resolution-photo .photo-viewport{height:48mm}
body.block-c .editorial-photo-band figcaption{margin-top:1.5mm;font:7.1pt/1.28 Avenir,sans-serif;color:#5A5D59}
body.block-c .editorial-photo-diptych{
  column-span:all;margin:4mm 0 5mm;break-inside:avoid-page;page-break-inside:avoid
}
body.block-c .editorial-photo-diptych .diptych-grid{
  display:grid;grid-template-columns:repeat(2,minmax(0,78mm));justify-content:space-between;
  gap:6mm;width:100%
}
body.block-c .editorial-photo-diptych .diptych-viewport{
  position:relative;width:78mm;height:58.5mm;overflow:hidden;background:#D5D7D4
}
body.block-c .editorial-photo-diptych img{
  display:block;width:100%;height:100%;object-fit:cover;filter:none!important
}
body.block-c .editorial-photo-diptych figcaption{
  margin-top:1.5mm;font:7.1pt/1.28 Avenir,sans-serif;color:#5A5D59
}
body.block-c .hotel-case{margin-left:-7mm;margin-right:-7mm;padding:8mm 7mm;background:#E3E6E4!important;border-top:.55mm solid #202020;border-left:1.5mm solid #CFFF00!important}
body.block-c .hotel-case .case-application-icon{position:absolute;right:7mm;top:6mm;width:18mm;height:18mm}
body.block-c .hotel-case .section-heading{position:relative;padding-right:24mm}
body.block-c .hotel-case .hotel-photo{margin:5mm -7mm 6mm}
body.block-c .hotel-case .hotel-photo .diptych-grid{padding:0 7mm;box-sizing:border-box}
body.block-c .hotel-case .hotel-photo figcaption{padding:0 7mm}
body.block-c .hotel-case .hotel-primary-photo{margin:5mm -7mm 6mm}
body.block-c .hotel-case .hotel-primary-photo .photo-viewport{height:70mm!important}
body.block-c .hotel-case .hotel-primary-photo figcaption{padding:0 7mm}
body.block-c .hotel-case-long .hotel-primary-photo .photo-viewport{height:82mm!important}
body.block-c .hotel-case:not(.hotel-case-long):not(.hotel-case-medium) .hotel-photo .photo-viewport{height:142mm}
body.block-c .hotel-case-medium .hotel-photo .photo-viewport{height:78mm}
body.block-c .hotel-case-long .hotel-photo .photo-viewport{height:64mm}
body.block-c .hotel-case-long .hotel-photo .diptych-viewport{height:72mm}
body.block-c:is(.document-n22,.document-n23) .hotel-long-opening-diptych .diptych-viewport{height:110mm!important}
body.block-c .hotel-case-medium .hotel-photo .diptych-viewport{height:54mm}
body.block-c .hotel-case:not(.hotel-case-long) .hotel-photo .diptych-viewport{height:78mm}
body.block-c .hotel-case .hotel-bridge{
  columns:2!important;column-count:2!important;column-gap:8mm!important;
  column-rule:.2mm solid #C5C7C5!important;max-width:none;
  column-fill:balance!important;
  margin:0 0 5mm!important;font-size:9.05pt;line-height:1.27
}
body.block-c .hotel-case .hotel-bridge p{
  margin:0 0 2.6mm!important;break-inside:auto!important;page-break-inside:auto!important
}
body.block-c:is(.document-n11,.document-n13,.document-n14) .hotel-case .hotel-bridge{
  font-size:9.5pt!important;line-height:1.32!important;margin-bottom:6mm!important
}
body.block-c:is(.document-n11,.document-n13,.document-n14) .hotel-case .hotel-bridge p{
  margin-bottom:3.4mm!important
}
body.block-c.document-n11 .hotel-case .hotel-bridge{
  font-size:9.6pt!important;line-height:1.35!important;margin:3mm 0 6mm!important
}
body.block-c .hotel-case:not(.hotel-case-long)>.section-body:not(.section-lead):not(.hotel-bridge){
  columns:2!important;column-count:2!important;column-gap:8mm!important;
  column-rule:.2mm solid #C5C7C5!important;font-size:9.15pt!important;line-height:1.27!important
}
body.block-c .hotel-case:not(.hotel-case-long)>.section-body:not(.section-lead):not(.hotel-bridge) p{
  margin:0 0 2.8mm!important
}
body.block-c .hotel-case-long>.section-body:not(.section-lead):not(.hotel-bridge){
  columns:auto!important;column-count:auto!important;font-size:8.85pt!important;line-height:1.25!important
}
body.block-c .hotel-case-long>.section-body:not(.section-lead):not(.hotel-bridge) p{margin:0 0 2.8mm!important}
body.block-c .hotel-continuation{
  box-sizing:border-box!important;break-before:page!important;page-break-before:always!important;
  break-inside:avoid-page!important;page-break-inside:avoid!important;
  min-height:0!important;padding:0 0 6mm!important;
  display:flex!important;flex-direction:column!important
}
body.block-c .hotel-primary-photo .photo-viewport{height:110mm!important}
body.block-c .hotel-case-medium .hotel-primary-photo .photo-viewport{height:78mm!important}
body.block-c .hotel-case-long .hotel-primary-photo .photo-viewport{height:58mm!important}
body.block-c .hotel-continuation-photo{
  width:100%!important;margin:auto 0 0!important;padding-top:5mm!important;
  border-top:.25mm solid #8F948F!important
}
body.block-c .hotel-continuation-photo .photo-viewport{height:102mm!important}
body.block-c .hotel-case-medium .hotel-continuation-photo .photo-viewport{height:86mm!important}
body.block-c .hotel-case-long .hotel-continuation-photo .photo-viewport{height:64mm!important}
body.block-c .hotel-continuation-body{
  display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;
  gap:0 6mm!important;align-items:start!important;font-size:8.85pt!important;line-height:1.25!important
}
body.block-c .hotel-tail-2 .hotel-continuation-body{grid-template-columns:repeat(2,minmax(0,1fr))!important}
body.block-c .hotel-tail-1 .hotel-continuation-body{grid-template-columns:1fr!important;max-width:104mm}
body.block-c .hotel-continuation-body p{font-size:8.85pt!important;line-height:1.25!important;margin:0 0 2.8mm!important}
body.block-c .hotel-text-column{min-width:0;padding-right:3mm;border-right:.2mm solid #C5C7C5}
body.block-c .hotel-text-column:last-child{padding-right:0;border-right:0}
body.block-c .hotel-text-column p{break-inside:avoid-page!important;page-break-inside:avoid!important}
body.block-c .hotel-case-long .hotel-continuation-body{
  display:block!important;columns:3!important;column-count:3!important;
  column-gap:6mm!important;column-rule:.2mm solid #C5C7C5!important;
  font-size:8.65pt!important;line-height:1.22!important
}
body.block-c .hotel-case-long .hotel-continuation-body p{
  font-size:8.65pt!important;line-height:1.22!important;margin:0 0 2.1mm!important;
  orphans:3!important;widows:3!important
}
body.block-c .hotel-case-medium .hotel-continuation-body{
  display:block!important;columns:3!important;column-count:3!important;
  column-gap:6mm!important;column-rule:.2mm solid #C5C7C5!important;
  column-fill:balance!important;font-size:8.85pt!important;line-height:1.24!important
}
body.block-c .hotel-case-medium .hotel-continuation-body p{
  break-inside:auto!important;page-break-inside:auto!important;
  font-size:8.85pt!important;line-height:1.24!important;margin:0 0 2.2mm!important
}
body.block-c .hotel-voices-compact{margin:3mm 0 5mm;padding:3mm 4mm;background:#DADDDC;border-top:.55mm solid #202020;border-bottom:.2mm solid #999;break-inside:avoid-page;page-break-inside:avoid}
body.block-c .hotel-voices-compact header{display:block;margin-bottom:2mm}
body.block-c .hotel-voices-compact .hotel-voices-title{margin:.6mm 0;font:400 16.5pt/1 Didot,serif}
body.block-c .hotel-voices-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:3mm 4mm}
body.block-c .hotel-voices-grid article{display:grid;grid-template-columns:27mm 1fr;min-height:40mm;border-top:.2mm solid #777}
body.block-c .hotel-voices-grid .hotel-portrait{width:27mm;height:40mm;margin:0;overflow:hidden}
body.block-c .hotel-voices-grid img{display:block;width:27mm;height:40mm;object-fit:cover;object-position:center 20%;filter:grayscale(1) contrast(1.03)}
body.block-c .hotel-voices-grid article>div{min-width:0;padding:2mm 0 0 2mm}
body.block-c .hotel-voices-grid span{display:block;font:600 4.8pt/1.15 Avenir,sans-serif;letter-spacing:.035em;text-transform:uppercase;color:#565A56}
body.block-c .hotel-voices-grid h3{margin:1mm 0 .8mm;font:400 10.2pt/1.05 Didot,serif}
body.block-c .hotel-voices-grid p{margin:0!important;font:6.15pt/1.22 Avenir,sans-serif!important;color:#4F534F}

/* The recurrent Hotel spread must read as a portrait-led editorial page,
   not as a compact strip floating above an empty lower half.  Cases with two
   remaining argument groups use a two-column, three-row portrait matrix. */
body.block-c .hotel-tail-2 .hotel-voices-grid{
  grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:3mm 6mm!important
}
body.block-c .hotel-tail-2 .hotel-voices-grid article{
  grid-template-columns:31mm 1fr!important;min-height:45mm!important
}
body.block-c .hotel-tail-2 .hotel-voices-grid .hotel-portrait{
  width:31mm!important;height:45mm!important
}
body.block-c .hotel-tail-2 .hotel-voices-grid img{
  width:31mm!important;height:45mm!important
}
body.block-c .hotel-tail-2 .hotel-voices-grid span{font-size:5.25pt!important}
body.block-c .hotel-tail-2 .hotel-voices-grid h3{font-size:11.2pt!important}
body.block-c .hotel-tail-2 .hotel-voices-grid p{font-size:6.7pt!important;line-height:1.24!important}

/* N21 is the only long Hotel case whose last paragraph legitimately needs a
   third column.  A measured compacting keeps the complete case on its two
   intended pages without suppressing or rewriting any source sentence. */
body.block-c.document-n21 .hotel-voices-compact{margin-bottom:2.5mm!important;padding-bottom:2mm!important}
body.block-c.document-n21 .hotel-voices-grid{gap:2mm 4mm!important}
body.block-c.document-n21 .hotel-voices-grid article{min-height:37mm!important}
body.block-c.document-n21 .hotel-voices-grid .hotel-portrait,
body.block-c.document-n21 .hotel-voices-grid img{height:37mm!important}
body.block-c.document-n21 .hotel-continuation-body,
body.block-c.document-n21 .hotel-continuation-body p{
  font-size:8.25pt!important;line-height:1.16!important
}
body.block-c.document-n21 .hotel-continuation-body p{margin-bottom:1.25mm!important}
body.block-c.document-n21 .hotel-case-long .hotel-continuation-body{
  column-fill:balance!important
}
body.block-c.document-n21 .hotel-case-long .hotel-continuation-body p{
  break-inside:auto!important;page-break-inside:auto!important;orphans:2!important;widows:2!important
}

body.block-c .block-c-movement{min-height:0!important;height:auto!important;display:block!important;justify-content:initial!important;padding:0!important;background:#FAFAF8!important;border-left:0!important}
body.block-c .block-c-movement .section-body{columns:2;column-count:2;column-gap:8mm;column-rule:.2mm solid #C5C7C5}
body.block-c .block-c-movement:nth-of-type(even) .section-body{columns:auto;column-count:auto;display:grid;grid-template-columns:1.08fr .92fr;gap:0 8mm}
body.block-c .block-c-infographic{column-span:all;margin:4mm 0 6mm;padding:2mm 0;border-top:.35mm solid #202020;border-bottom:.2mm solid #999;break-inside:avoid-page;page-break-inside:avoid}
body.block-c .block-c-infographic img{display:block;width:100%;height:auto;max-height:94mm;object-fit:contain;filter:none}
body.block-c .block-c-problem-map{margin:5mm 0 0!important;padding-top:3mm!important}
body.block-c .block-c-problem-map img{height:70mm!important;max-height:70mm!important}
body.block-c .movement-two-photo .diptych-viewport,
body.block-c .movement-three-photo .diptych-viewport{height:58.5mm}
body.block-c .movement-closing-statement{
  column-span:all;margin:4mm 0 0;padding:5mm 6mm 4.5mm;
  background:#E3E6E4;border-left:1.5mm solid #CFFF00;
  break-inside:avoid-page;page-break-inside:avoid
}
body.block-c .movement-closing-statement p{
  margin:0!important;font:400 13.2pt/1.25 Didot,"Bodoni 72",serif!important
}
body.block-c .block-c-handoff{min-height:0!important;height:auto!important;display:block!important;justify-content:initial!important;padding:6mm!important}
body.block-c .block-c-synthesis .section-body{columns:2;column-count:2;column-gap:8mm;column-rule:.2mm solid #C5C7C5}

body.block-c .pill-summary{min-height:0!important;height:auto!important;display:block!important;justify-content:initial!important;padding:6mm 7mm!important;background:#E3E6E4;break-inside:avoid-page;page-break-inside:avoid}
/* The inherited positioned heading was painted after the non-positioned list,
   so PDF extraction returned the five items before their section title.  No
   ornament is anchored here in Block C; static positioning preserves the
   exact geometry and restores logical paint and reading order. */
body.block-c .pill-summary .section-heading{position:static!important}
body.block-c .pill-summary .section-body ol{columns:auto!important;column-count:auto!important;display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:3mm 9mm!important;margin:3mm 0 0!important;padding-left:7mm!important}
body.block-c .pill-summary .section-body li{font-size:10.2pt!important;line-height:1.32!important;margin:0!important}
body.block-c .glossary-two-column{min-height:0!important;height:auto!important;display:block!important;justify-content:initial!important;break-before:page!important;page-break-before:always!important;padding:6mm 7mm!important;background:#F0F1EE;border-left:1.5mm solid #CFFF00}
body.block-c .glossary-two-column .section-body{min-height:0!important;height:auto!important;display:grid!important;grid-auto-flow:row!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;grid-template-rows:none!important;gap:0 9mm!important;font-size:10.4pt;line-height:1.32}
body.block-c .glossary-two-column .section-body p{padding:3.5mm 0 3mm}
body.block-c .questions{min-height:0!important;height:auto!important;display:block!important;justify-content:initial!important;break-before:page!important;page-break-before:always!important;padding:7mm!important;background:#E3E6E4}
body.block-c .questions .section-body{font-size:11.2pt;line-height:1.4}
body.block-c .questions .section-body ol{min-height:0!important;height:auto!important;display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;grid-template-rows:repeat(3,auto)!important;grid-auto-flow:column!important;align-content:start!important;gap:9mm 12mm!important;margin:3mm 0 0!important;padding-left:7mm!important;columns:auto!important;column-count:auto!important}
body.block-c .questions .section-body li{margin:0!important;padding-right:2mm;break-inside:avoid-page;page-break-inside:avoid}
body.block-c .questions .section-body>p:last-child{margin:8mm 0 0;padding:4mm;border-top:.6mm solid #171917;border-left:1.5mm solid #CFFF00;background:#FAFAF8;font:8.8pt/1.3 Avenir,sans-serif}
body.document-n12.block-c .questions .section-body{font-size:12pt!important;line-height:1.45!important}
body.document-n12.block-c .questions .section-body ol{gap:11mm 12mm!important}
body.document-n12.block-c .questions .section-body>p:last-child{margin-top:11mm!important;font-size:9.1pt!important}
body.document-n13.block-c .questions .section-body{font-size:12.2pt!important;line-height:1.48!important}
body.document-n13.block-c .questions .section-body ol{gap:11mm 12mm!important}
body.document-n13.block-c .questions .section-body>p:last-child{margin-top:11mm!important;font-size:9.1pt!important;line-height:1.4!important}
body.document-n14.block-c .thesis-with-approved-plate .section-lead p{font-size:17.5pt!important;line-height:1.34!important}
body.document-n14.block-c .thesis-with-approved-plate .section-body:not(.section-lead){font-size:11.8pt!important;line-height:1.46!important}
body.document-n14.block-c .questions .section-body{font-size:12.2pt!important;line-height:1.48!important}
body.document-n14.block-c .questions .section-body ol{gap:11mm 12mm!important}
body.document-n14.block-c .questions .section-body>p:last-child{margin-top:11mm!important;font-size:9.1pt!important;line-height:1.4!important}
body.document-n15.block-c .thesis-with-approved-plate .section-lead p{font-size:18pt!important;line-height:1.36!important}
body.document-n15.block-c .thesis-with-approved-plate .section-body:not(.section-lead){font-size:12pt!important;line-height:1.5!important}
body.document-n15.block-c .questions .section-body{font-size:12.4pt!important;line-height:1.5!important}
body.document-n15.block-c .questions .section-body ol{gap:14mm 12mm!important}
body.document-n15.block-c .questions .section-body>p:last-child{margin-top:15mm!important;font-size:9.2pt!important;line-height:1.42!important}
body.document-n16.block-c .thesis-with-approved-plate .section-lead p{font-size:18pt!important;line-height:1.36!important}
body.document-n16.block-c .thesis-with-approved-plate .section-body:not(.section-lead){font-size:12pt!important;line-height:1.5!important}
body.document-n16.block-c .questions .section-body{font-size:12.4pt!important;line-height:1.5!important}
body.document-n16.block-c .questions .section-body ol{gap:14mm 12mm!important}
body.document-n16.block-c .questions .section-body>p:last-child{margin-top:15mm!important;font-size:9.2pt!important;line-height:1.42!important}
body.document-n17.block-c .thesis-with-approved-plate .section-lead p{font-size:22.5pt!important;line-height:1.38!important}
body.document-n17.block-c .questions .section-body{font-size:12.4pt!important;line-height:1.5!important}
body.document-n17.block-c .questions .section-body ol{gap:14mm 12mm!important}
body.document-n17.block-c .questions .section-body>p:last-child{margin-top:15mm!important;font-size:9.2pt!important;line-height:1.42!important}
body.document-n18.block-c .questions .section-body{font-size:12.4pt!important;line-height:1.5!important}
body.document-n18.block-c .questions .section-body ol{gap:14mm 12mm!important}
body.document-n18.block-c .questions .section-body>p:last-child{margin-top:15mm!important;font-size:9.2pt!important;line-height:1.42!important}
body.document-n18.block-c .thesis-with-approved-plate .section-lead p{font-size:25pt!important;line-height:1.42!important}
body.document-n19.block-c .thesis-with-approved-plate .section-lead p{font-size:27pt!important;line-height:1.45!important}
body.document-n19.block-c .questions .section-body{font-size:12.4pt!important;line-height:1.5!important}
body.document-n19.block-c .questions .section-body ol{gap:14mm 12mm!important}
body.document-n19.block-c .questions .section-body>p:last-child{margin-top:15mm!important;font-size:9.2pt!important;line-height:1.42!important}
body.document-n20.block-c .thesis-with-approved-plate .section-lead p{font-size:23.5pt!important;line-height:1.4!important}
body.document-n20.block-c .questions .section-body{font-size:12.4pt!important;line-height:1.5!important}
body.document-n20.block-c .questions .section-body ol{gap:14mm 12mm!important}
body.document-n20.block-c .questions .section-body>p:last-child{margin-top:15mm!important;font-size:9.2pt!important;line-height:1.42!important}
body.document-n21.block-c .thesis-with-approved-plate .section-lead p{font-size:23.5pt!important;line-height:1.4!important}
body.document-n21.block-c .questions .section-body{font-size:12.4pt!important;line-height:1.5!important}
body.document-n21.block-c .questions .section-body ol{gap:14mm 12mm!important}
body.document-n21.block-c .questions .section-body>p:last-child{margin-top:15mm!important;font-size:9.2pt!important;line-height:1.42!important}
body.block-c:is(.document-n11,.document-n12,.document-n14,.document-n15,.document-n17,.document-n20,.document-n21) .questions .section-body ol{
  gap:22mm 12mm!important
}
body.block-c:is(.document-n11,.document-n12,.document-n14,.document-n15,.document-n17,.document-n20,.document-n21) .questions .section-body>p:last-child{
  margin-top:18mm!important
}
body.document-n21.block-c .block-c-references .section-body{font-size:10.1pt!important;line-height:1.42!important}
body.document-n21.block-c .block-c-references li{margin-bottom:4.4mm!important}
body.document-n22.block-c .block-c-thesis .section-lead p{font-size:25pt!important;line-height:1.44!important}
body.document-n22.block-c .questions .section-body{font-size:12.4pt!important;line-height:1.5!important}
body.document-n22.block-c .questions .section-body ol{gap:20mm 12mm!important}
body.document-n22.block-c .questions .section-body>p:last-child{margin-top:18mm!important;font-size:9.2pt!important;line-height:1.42!important}
body.document-n23.block-c .block-c-thesis .section-lead p{font-size:25pt!important;line-height:1.44!important}
body.document-n23.block-c .questions .section-body{font-size:12.4pt!important;line-height:1.5!important}
body.document-n23.block-c .questions .section-body ol{gap:20mm 12mm!important}
body.document-n23.block-c .questions .section-body>p:last-child{margin-top:18mm!important;font-size:9.2pt!important;line-height:1.42!important}
body.document-n23.block-c .block-c-references .section-body{font-size:9.25pt!important;line-height:1.34!important}
body.document-n23.block-c .block-c-references li{margin-bottom:4.4mm!important}
body.document-n24.block-c .block-c-thesis .section-lead p{font-size:25pt!important;line-height:1.44!important}
body.document-n24.block-c .questions .section-body{font-size:12.4pt!important;line-height:1.5!important}
body.document-n24.block-c .questions .section-body ol{gap:20mm 12mm!important}
body.document-n24.block-c .questions .section-body>p:last-child{margin-top:18mm!important;font-size:9.2pt!important;line-height:1.42!important}
body.document-n25.block-c .block-c-thesis .section-lead p{font-size:25pt!important;line-height:1.44!important}
body.document-n25.block-c .questions .section-body{font-size:12.4pt!important;line-height:1.5!important}
body.document-n25.block-c .questions .section-body ol{gap:20mm 12mm!important}
body.document-n25.block-c .questions .section-body>p:last-child{margin-top:18mm!important;font-size:9.2pt!important;line-height:1.42!important}
body.document-n26.block-c .block-c-thesis .section-lead p{font-size:25pt!important;line-height:1.44!important}
body.document-n26.block-c .questions .section-body{font-size:12.4pt!important;line-height:1.5!important}
body.document-n26.block-c .questions .section-body ol{gap:20mm 12mm!important}
body.document-n26.block-c .questions .section-body>p:last-child{margin-top:18mm!important;font-size:9.2pt!important;line-height:1.42!important}
body.document-n27.block-c .block-c-thesis .section-lead p{font-size:25pt!important;line-height:1.44!important}
body.document-n27.block-c .questions .section-body{font-size:12.4pt!important;line-height:1.5!important}
body.document-n27.block-c .questions .section-body ol{gap:20mm 12mm!important}
body.document-n27.block-c .questions .section-body>p:last-child{margin-top:18mm!important;font-size:9.2pt!important;line-height:1.42!important}
body.document-n28.block-c .block-c-thesis .section-lead p{font-size:25pt!important;line-height:1.44!important}
body.document-n28.block-c .questions .section-body{font-size:12.4pt!important;line-height:1.5!important}
body.document-n28.block-c .questions .section-body ol{gap:20mm 12mm!important}
body.document-n28.block-c .questions .section-body>p:last-child{margin-top:18mm!important;font-size:9.2pt!important;line-height:1.42!important}
body.document-n29.block-c .block-c-thesis .section-lead p{font-size:25pt!important;line-height:1.44!important}
body.document-n29.block-c .questions .section-body{font-size:12.4pt!important;line-height:1.5!important}
body.document-n29.block-c .questions .section-body ol{gap:20mm 12mm!important}
body.document-n29.block-c .questions .section-body>p:last-child{margin-top:18mm!important;font-size:9.2pt!important;line-height:1.42!important}
body.document-n30.block-c .block-c-thesis .section-lead p{font-size:25pt!important;line-height:1.44!important}
body.document-n30.block-c .questions .section-body{font-size:12.4pt!important;line-height:1.5!important}
body.document-n30.block-c .questions .section-body ol{gap:20mm 12mm!important}
body.document-n30.block-c .questions .section-body>p:last-child{margin-top:18mm!important;font-size:9.2pt!important;line-height:1.42!important}
body.document-n31.block-c .block-c-thesis .section-lead p{font-size:25pt!important;line-height:1.44!important}
body.document-n31.block-c .questions .section-body{font-size:12.4pt!important;line-height:1.5!important}
body.document-n31.block-c .questions .section-body ol{gap:20mm 12mm!important}
body.document-n31.block-c .questions .section-body>p:last-child{margin-top:18mm!important;font-size:9.2pt!important;line-height:1.42!important}
body.document-n32.block-c .block-c-thesis .section-lead p{font-size:25pt!important;line-height:1.44!important}
body.document-n32.block-c .questions .section-body{font-size:12.4pt!important;line-height:1.5!important}
body.document-n32.block-c .questions .section-body ol{gap:20mm 12mm!important}
body.document-n32.block-c .questions .section-body>p:last-child{margin-top:18mm!important;font-size:9.2pt!important;line-height:1.42!important}
body.document-n33.block-c .block-c-thesis .section-lead p{font-size:25pt!important;line-height:1.44!important}
body.document-n33.block-c .questions .section-body{font-size:12.4pt!important;line-height:1.5!important}
body.document-n33.block-c .questions .section-body ol{gap:20mm 12mm!important}
body.document-n33.block-c .questions .section-body>p:last-child{margin-top:18mm!important;font-size:9.2pt!important;line-height:1.42!important}
body.document-n33.block-c .pills-glossary-page{
  height:232mm!important;min-height:232mm!important;padding:5mm 6mm!important;gap:3.5mm!important
}
body.document-n33.block-c .pills-glossary-page .pill-summary{padding-bottom:3mm!important}
body.document-n33.block-c .pills-glossary-page .pill-summary .section-body{
  columns:auto!important;column-count:auto!important
}
body.document-n33.block-c .pills-glossary-page .pill-summary .section-heading h2,
body.document-n33.block-c .pills-glossary-page .glossary-two-column .section-heading h2{
  font-size:21pt!important;line-height:1!important;margin-bottom:2mm!important
}
body.document-n33.block-c .pills-glossary-page .pill-summary .section-body ol{
  grid-template-columns:1fr!important;gap:1.2mm!important;margin-top:1mm!important;padding-left:6mm!important
}
body.document-n33.block-c .pills-glossary-page .pill-summary .section-body li{
  font-size:9pt!important;line-height:1.22!important;font-weight:600!important
}
body.document-n33.block-c .pills-glossary-page .glossary-two-column .section-body{
  font-size:8.25pt!important;line-height:1.17!important;gap:0 5mm!important
}
body.document-n33.block-c .pills-glossary-page .glossary-two-column .section-body p{
  padding:1.35mm 0 1mm!important
}
body.document-n34.block-c .block-c-thesis .section-lead p{font-size:24pt!important;line-height:1.42!important}
body.document-n34.block-c .questions .section-body{font-size:12.4pt!important;line-height:1.5!important}
body.document-n34.block-c .questions .section-body ol{gap:20mm 12mm!important}
body.document-n34.block-c .questions .section-body>p:last-child{margin-top:18mm!important;font-size:9.2pt!important;line-height:1.42!important}
body.document-n34.block-c .pills-glossary-page{
  height:232mm!important;min-height:232mm!important;padding:5mm 6mm!important;gap:3.5mm!important
}
body.document-n34.block-c .pills-glossary-page .pill-summary{padding-bottom:3mm!important}
body.document-n34.block-c .pills-glossary-page .pill-summary .section-body{columns:auto!important;column-count:auto!important}
body.document-n34.block-c .pills-glossary-page .pill-summary .section-heading h2,
body.document-n34.block-c .pills-glossary-page .glossary-two-column .section-heading h2{
  font-size:21pt!important;line-height:1!important;margin-bottom:2mm!important
}
body.document-n34.block-c .pills-glossary-page .pill-summary .section-body ol{
  grid-template-columns:1fr!important;gap:1.2mm!important;margin-top:1mm!important;padding-left:6mm!important
}
body.document-n34.block-c .pills-glossary-page .pill-summary .section-body li{
  font-size:9pt!important;line-height:1.22!important;font-weight:600!important
}
body.document-n34.block-c .pills-glossary-page .glossary-two-column .section-body{
  font-size:8.25pt!important;line-height:1.17!important;gap:0 5mm!important
}
body.document-n34.block-c .pills-glossary-page .glossary-two-column .section-body p{padding:1.35mm 0 1mm!important}
body.document-n35.block-c .block-c-thesis .section-lead p{font-size:24pt!important;line-height:1.42!important}
body.document-n35.block-c .questions .section-body{font-size:12.4pt!important;line-height:1.5!important}
body.document-n35.block-c .questions .section-body ol{gap:20mm 12mm!important}
body.document-n35.block-c .questions .section-body>p:last-child{margin-top:18mm!important;font-size:9.2pt!important;line-height:1.42!important}
body.document-n35.block-c .pills-glossary-page{
  height:232mm!important;min-height:232mm!important;padding:5mm 6mm!important;gap:3.5mm!important
}
body.document-n35.block-c .pills-glossary-page .pill-summary{padding-bottom:3mm!important}
body.document-n35.block-c .pills-glossary-page .pill-summary .section-body{columns:auto!important;column-count:auto!important}
body.document-n35.block-c .pills-glossary-page .pill-summary .section-heading h2,
body.document-n35.block-c .pills-glossary-page .glossary-two-column .section-heading h2{
  font-size:21pt!important;line-height:1!important;margin-bottom:2mm!important
}
body.document-n35.block-c .pills-glossary-page .pill-summary .section-body ol{
  grid-template-columns:1fr!important;gap:1.2mm!important;margin-top:1mm!important;padding-left:6mm!important
}
body.document-n35.block-c .pills-glossary-page .pill-summary .section-body li{
  font-size:9pt!important;line-height:1.22!important;font-weight:600!important
}
body.document-n35.block-c .pills-glossary-page .glossary-two-column .section-body{
  font-size:8.25pt!important;line-height:1.17!important;gap:0 5mm!important
}
body.document-n35.block-c .pills-glossary-page .glossary-two-column .section-body p{padding:1.35mm 0 1mm!important}
body.document-n36.block-c .block-c-thesis .section-lead p{font-size:24pt!important;line-height:1.42!important}
body.document-n36.block-c .questions .section-body{font-size:12.4pt!important;line-height:1.5!important}
body.document-n36.block-c .questions .section-body ol{gap:20mm 12mm!important}
body.document-n36.block-c .questions .section-body>p:last-child{margin-top:18mm!important;font-size:9.2pt!important;line-height:1.42!important}
body.document-n36.block-c .pills-glossary-page{
  height:232mm!important;min-height:232mm!important;padding:5mm 6mm!important;gap:3.5mm!important
}
body.document-n36.block-c .pills-glossary-page .pill-summary{padding-bottom:3mm!important}
body.document-n36.block-c .pills-glossary-page .pill-summary .section-body{columns:auto!important;column-count:auto!important}
body.document-n36.block-c .pills-glossary-page .pill-summary .section-heading h2,
body.document-n36.block-c .pills-glossary-page .glossary-two-column .section-heading h2{
  font-size:21pt!important;line-height:1!important;margin-bottom:2mm!important
}
body.document-n36.block-c .pills-glossary-page .pill-summary .section-body ol{
  grid-template-columns:1fr!important;gap:1.2mm!important;margin-top:1mm!important;padding-left:6mm!important
}
body.document-n36.block-c .pills-glossary-page .pill-summary .section-body li{
  font-size:9pt!important;line-height:1.22!important;font-weight:600!important
}
body.document-n36.block-c .pills-glossary-page .glossary-two-column .section-body{
  font-size:8.25pt!important;line-height:1.17!important;gap:0 5mm!important
}
body.document-n36.block-c .pills-glossary-page .glossary-two-column .section-body p{padding:1.35mm 0 1mm!important}

/* The closing study pages use the whole editorial box.  The extra area is
   carried by photography, never by inflated paragraph or list spacing. */
body.block-c .pill-summary{
  box-sizing:border-box!important;
  height:236mm!important;
  min-height:236mm!important;
  display:flex!important;
  flex-direction:column!important;
}
body.block-c .pill-summary .pills-photo{
  flex:1 1 auto;
  min-height:104mm;
  display:flex;
  flex-direction:column;
}
body.block-c .pill-summary .pills-photo .photo-viewport{
  flex:1 1 auto;
  height:auto!important;
  min-height:104mm;
}
body.block-c .block-c-synthesis .synthesis-photo .photo-viewport{height:82mm}
body.block-c .questions{
  box-sizing:border-box!important;
  min-height:0!important;
  height:auto!important;
  display:block!important;
}
body.block-c .questions .preparation-photo{
  width:78mm;min-height:0;margin-left:auto;display:block;
}
body.block-c .questions .preparation-photo .photo-viewport{
  width:78mm;height:58.5mm!important;
  min-height:0;
}

body.block-c .block-c-references{min-height:0!important;height:auto!important;display:block!important;justify-content:initial!important;break-before:page!important;page-break-before:always!important;padding:0!important;background:#FAFAF8!important;border-left:0!important}
body.block-c .block-c-references .section-body{columns:auto!important;column-count:auto!important;display:block!important;font:9.7pt/1.34 Avenir,sans-serif}
body.block-c .block-c-references .section-body ul{columns:2!important;column-count:2!important;column-gap:9mm!important;max-width:none!important;list-style:none;margin:0;padding:0}
body.block-c .block-c-references li{margin:0 0 3.5mm!important;break-inside:avoid;overflow-wrap:normal;word-break:normal;hyphens:none}
body.block-c .icon-strip{grid-template-columns:repeat(4,minmax(0,1fr));gap:4mm;margin:5mm 0;padding:4mm 0}
body.block-c .icon-strip div{grid-template-columns:10mm 1fr}
body.block-c .icon-strip svg{width:9mm;height:9mm}
body.block-c .block-c-pause{page:fullbleed!important;width:210mm!important;height:297mm!important;margin:0!important;break-before:page!important;page-break-before:always!important;break-after:page!important;page-break-after:always!important}
body.block-c .block-c-pause::after{inset:0!important;height:100%!important;background:linear-gradient(180deg,rgba(0,0,0,.02) 42%,rgba(0,0,0,.56) 100%)}
body.block-c .block-c-pause p{font-size:24pt;max-width:160mm}
body.block-c .closing-image{page:fullbleed!important;width:210mm!important;height:297mm!important;margin:0!important;break-before:page!important;page-break-before:always!important}

/* Deliberate magazine pages for the short recurring apparatus.  Content is
   distributed by structure and photography, never by paragraph spacing. */
body.block-c .section-lead{
  columns:auto!important;column-count:auto!important;display:block!important;
  max-width:158mm;margin:0 0 3mm;font-size:10.1pt;line-height:1.34
}
body.block-c .block-c-thesis{
  box-sizing:border-box!important;height:236mm!important;min-height:236mm!important;
  break-before:page!important;page-break-before:always!important;
  break-inside:avoid-page!important;page-break-inside:avoid!important;
  display:flex!important;flex-direction:column!important;padding:8mm!important;
  background:#E3E6E4!important;border-left:1.5mm solid #CFFF00!important
}
body.block-c .block-c-thesis .section-body:not(.section-lead){
  columns:2!important;column-count:2!important;column-gap:8mm!important;
  column-rule:.2mm solid #B9BCB9;font-size:10.8pt;line-height:1.34
}
body.block-c .block-c-thesis .section-lead p{font:400 16pt/1.25 Didot,"Bodoni 72",serif!important}
body.block-c .block-c-thesis .icon-strip{margin:3mm 0 4mm!important}
body.block-c .block-c-thesis .thesis-map{
  flex:1 1 64mm!important;min-height:52mm!important;margin:5mm 0 0!important;
  max-height:none!important;overflow:hidden;display:flex!important;flex-direction:column!important
}
body.block-c .block-c-thesis .thesis-map img{
  display:block;width:100%!important;height:calc(100% - 7mm)!important;
  min-height:0!important;max-height:none!important;object-fit:contain
}
body.block-c .block-c-thesis .thesis-map figcaption{font-size:6.7pt!important;line-height:1.22!important}
body.block-c .thesis-with-approved-plate{justify-content:center!important}
body.block-c .approved-infographic-page{
  box-sizing:border-box!important;height:236mm!important;min-height:236mm!important;
  break-before:page!important;page-break-before:always!important;
  break-after:page!important;page-break-after:always!important;
  display:grid!important;grid-template-rows:auto 1fr!important;
  align-items:start!important;padding:12mm 8mm 10mm!important;background:#F7F7F4!important
}
body.block-c .approved-infographic-page header{
  max-width:158mm!important;border-top:.35mm solid #202020!important;
  padding-top:5mm!important
}
body.block-c .approved-infographic-page header span{
  display:block!important;font:700 7pt/1 Avenir,sans-serif!important;
  letter-spacing:.16em!important;color:#4F534F!important;text-transform:uppercase!important
}
body.block-c .approved-infographic-page header p{
  max-width:150mm!important;margin:6mm 0 0!important;
  font:400 19pt/1.16 Didot,"Bodoni 72",serif!important;color:#171817!important
}
body.block-c .approved-infographic-page figure{
  width:100%!important;height:100%!important;margin:8mm 0 0!important;
  display:flex!important;flex-direction:column!important;justify-content:flex-end!important;
  align-items:stretch!important
}
body.block-c .approved-infographic-page img{
  display:block!important;width:100%!important;height:auto!important;max-height:126mm!important;
  object-fit:contain!important
}
body.block-c .approved-infographic-page figcaption{
  margin:4mm 0 0!important;font:7.2pt/1.28 Avenir,sans-serif!important;color:#565956!important
}

body.block-c .block-c-movement .section-lead{margin-bottom:2mm}
body.block-c .block-c-movement .section-body:not(.section-lead){
  display:block!important;columns:2!important;column-count:2!important;
  column-gap:8mm!important;column-rule:.2mm solid #C5C7C5!important;
  font-size:10pt!important;line-height:1.27!important
}
body.block-c .block-c-movement .section-body:not(.section-lead) p{
  margin:0 0 1.8mm!important
}
body.block-c .block-c-movement .section-body:not(.section-lead) h3{
  margin:4mm 0 1.8mm!important;padding-top:2mm!important
}
body.block-c .movement-two-photo .photo-viewport{height:62mm!important}
body.block-c .movement-three-photo{margin:6mm 0 0!important}
body.block-c .movement-three-photo .photo-viewport{height:62mm!important}
body.block-c.document-n11 .movement-three-photo .photo-viewport{height:108mm!important}
body.block-c:is(.document-n13,.document-n16) .movement-three-photo{margin-top:3mm!important}
body.block-c.document-n13 .movement-three-photo .photo-viewport{height:24mm!important}
body.block-c.document-n16 .movement-three-photo .photo-viewport{height:74mm!important}
body.block-c.document-n12 .movement-three-photo{margin-top:4mm!important}
body.block-c.document-n12 .movement-three-photo .photo-viewport{height:48mm!important}
body.block-c.document-n12 .movement-3 .section-body:not(.section-lead){
  font-size:9.2pt!important;line-height:1.18!important
}
body.block-c.document-n12 .movement-3 .section-body:not(.section-lead) p{margin-bottom:.9mm!important}
body.block-c.document-n12 .movement-3 .section-body:not(.section-lead) h3{
  margin:2.5mm 0 .9mm!important;padding-top:1.1mm!important
}
body.block-c:is(.document-n26,.document-n27,.document-n28,.document-n29,.document-n30,
  .document-n31,.document-n32,.document-n33,.document-n34,.document-n35,.document-n36)
  .reading-section[data-section="02"] .section-two-photo{margin:7mm 0 0!important}
body.block-c:is(.document-n26,.document-n27,.document-n28,.document-n29,.document-n30,
  .document-n31,.document-n32,.document-n33,.document-n34,.document-n35,.document-n36)
  .reading-section[data-section="02"] .section-two-photo .photo-viewport{height:90mm!important}
body.block-c:is(.document-n20,.document-n22,.document-n26,.document-n27,.document-n28,.document-n29,.document-n30,.document-n32) .movement-2 .section-body:not(.section-lead),
body.block-c:is(.document-n13,.document-n16,.document-n17,.document-n22,.document-n26,.document-n27,.document-n28,.document-n29,.document-n30,.document-n32,.document-n33,.document-n35,.document-n36) .movement-3 .section-body:not(.section-lead){
  font-size:9.35pt!important;line-height:1.21!important
}
body.block-c:is(.document-n20,.document-n22,.document-n26,.document-n27,.document-n28,.document-n29,.document-n30,.document-n32) .movement-2 .section-body:not(.section-lead) p,
body.block-c:is(.document-n13,.document-n16,.document-n17,.document-n22,.document-n26,.document-n27,.document-n28,.document-n29,.document-n30,.document-n32,.document-n33,.document-n35,.document-n36) .movement-3 .section-body:not(.section-lead) p{
  margin:0 0 1.25mm!important
}
body.block-c:is(.document-n20,.document-n22,.document-n26,.document-n27,.document-n28,.document-n29,.document-n30,.document-n32) .movement-2 .section-body:not(.section-lead) h3,
body.block-c:is(.document-n13,.document-n16,.document-n17,.document-n22,.document-n26,.document-n27,.document-n28,.document-n29,.document-n30,.document-n32,.document-n33,.document-n35,.document-n36) .movement-3 .section-body:not(.section-lead) h3{
  margin:3.1mm 0 1.25mm!important;padding-top:1.4mm!important
}
body.block-c:is(.document-n20,.document-n22,.document-n27,.document-n30) .movement-2 .section-body:not(.section-lead),
body.block-c:is(.document-n16,.document-n17,.document-n22,.document-n26,.document-n30) .movement-3 .section-body:not(.section-lead){
  font-size:9pt!important;line-height:1.18!important
}
body.block-c:is(.document-n20,.document-n22,.document-n27,.document-n30) .movement-2 .section-body:not(.section-lead) p,
body.block-c:is(.document-n16,.document-n17,.document-n22,.document-n26,.document-n30) .movement-3 .section-body:not(.section-lead) p{
  margin-bottom:.9mm!important
}
body.block-c:is(.document-n20,.document-n22,.document-n27,.document-n30) .movement-2 .section-body:not(.section-lead) h3,
body.block-c:is(.document-n16,.document-n17,.document-n22,.document-n26,.document-n30) .movement-3 .section-body:not(.section-lead) h3{
  margin:2.4mm 0 .9mm!important;padding-top:1.1mm!important
}
body.block-c:is(.document-n20,.document-n30) .movement-2 .section-body:not(.section-lead),
body.block-c:is(.document-n16,.document-n22,.document-n30) .movement-3 .section-body:not(.section-lead){
  font-size:9.35pt!important;line-height:1.21!important
}
body.block-c:is(.document-n20,.document-n30) .movement-2 .section-body:not(.section-lead) p,
body.block-c:is(.document-n16,.document-n22,.document-n30) .movement-3 .section-body:not(.section-lead) p{
  margin-bottom:1.25mm!important
}
body.block-c:is(.document-n20,.document-n30) .movement-2 .section-body:not(.section-lead) h3,
body.block-c:is(.document-n16,.document-n22,.document-n30) .movement-3 .section-body:not(.section-lead) h3{
  margin:3.1mm 0 1.25mm!important;padding-top:1.4mm!important
}
body.block-c.document-n16 .movement-3 .section-body:not(.section-lead){
  font-size:9.75pt!important;line-height:1.25!important
}
body.block-c.document-n16 .movement-3 .section-body:not(.section-lead) p{margin-bottom:1.5mm!important}
body.block-c.document-n16 .movement-3 .section-body:not(.section-lead) h3{
  margin:3.5mm 0 1.5mm!important;padding-top:1.7mm!important
}
body.block-c.document-n23 .movement-3 .section-body:not(.section-lead){
  font-size:12pt!important;line-height:1.42!important
}
body.block-c.document-n23 .movement-3 .section-body:not(.section-lead) p{
  margin-bottom:2.4mm!important
}
body.block-c.document-n23 .movement-3 .section-body:not(.section-lead) h3{
  margin:4mm 0 2mm!important;padding-top:2mm!important
}
body.block-c.document-n20 .movement-2 .section-body:not(.section-lead){
  font-size:10.8pt!important;line-height:1.34!important
}
body.block-c.document-n20 .movement-2 .section-body:not(.section-lead) p{
  margin-bottom:2mm!important
}
body.block-c.document-n20 .movement-2 .section-body:not(.section-lead) h3{
  margin:3.6mm 0 1.8mm!important;padding-top:1.7mm!important
}
body.block-c.document-n30 .movement-2 .section-body:not(.section-lead){
  font-size:10.2pt!important;line-height:1.3!important
}
body.block-c.document-n30 .movement-2 .section-body:not(.section-lead) p{margin-bottom:1.6mm!important}
body.block-c.document-n30 .movement-2 .section-body:not(.section-lead) h3{
  margin:3.3mm 0 1.5mm!important;padding-top:1.5mm!important
}
body.block-c .movement-editorial-close{
  column-span:all;box-sizing:border-box;width:100%;margin:5mm 0 0;padding:9mm 10mm;
  position:relative;display:flex;flex-direction:column;justify-content:center;
  border-top:.55mm solid #202020;border-bottom:.2mm solid #8F948F;
  break-inside:avoid-page;page-break-inside:avoid
}
body.block-c .movement-editorial-close::before{
  content:"";display:block;width:20mm;height:2.8mm;margin:0 0 7mm;
  background:#CFFF00;transform:skewX(-24deg);transform-origin:left center
}
body.block-c .movement-editorial-close h3{
  margin:0 0 5mm!important;font:600 11pt/1.18 Avenir,sans-serif!important;
  letter-spacing:.015em
}
body.block-c .movement-editorial-close-body{min-width:0}
body.block-c .movement-editorial-close-body p:last-child{margin-bottom:0!important}
body.block-c .movement-editorial-close.close-short{
  min-height:180mm;background:#E3E6E4
}
body.block-c .movement-editorial-close.close-short .movement-editorial-close-body{
  columns:1!important;column-count:1!important;max-width:154mm
}
body.block-c .movement-editorial-close.close-short p{
  font:400 14pt/1.34 Didot,"Bodoni 72",serif!important;margin:0 0 4mm!important
}
body.block-c .movement-editorial-close.close-long{
  min-height:184mm;background:#F0F1EE
}
body.block-c .movement-editorial-close.close-long .movement-editorial-close-body{
  columns:2!important;column-count:2!important;column-gap:9mm!important;
  column-rule:.2mm solid #B9BCB9!important;column-fill:balance!important
}
body.block-c .movement-editorial-close.close-long p{
  font-size:10.2pt!important;line-height:1.34!important;margin:0 0 3mm!important
}
body.block-c .movement-editorial-close.close-variant-1{border-left:1.5mm solid #CFFF00}
body.block-c .movement-editorial-close.close-variant-2{background:#FAFAF8}
body.block-c .movement-editorial-close.close-variant-2::before{margin-left:auto}
/* Measured movement reflow.  These values preserve every source block and the
   common leading, while preventing the last argument from becoming a nearly
   empty page immediately before the photographic pause. */
body.block-c .subsection-lead{
  break-inside:avoid-column!important;page-break-inside:avoid!important
}
body.block-c .subsection-unit{
  break-inside:avoid!important;page-break-inside:avoid!important
}
body.block-c:is(.document-n21,.document-n22,.document-n23,.document-n24,.document-n25,.document-n26,.document-n27,.document-n28,.document-n29,.document-n30,.document-n31,.document-n32,.document-n33,.document-n34,.document-n35,.document-n36) .subsection-unit,
body.block-c:is(.document-n21,.document-n22,.document-n23,.document-n24,.document-n25,.document-n26,.document-n27,.document-n28,.document-n29,.document-n30,.document-n31,.document-n32,.document-n33,.document-n34,.document-n35,.document-n36) .subsection-lead{
  break-inside:auto!important;page-break-inside:auto!important
}
body.block-c .block-c-consequences .section-lead{max-width:150mm;margin-bottom:4mm}
body.block-c .block-c-consequences .consequence-photo{margin:2mm 0 5mm}
body.block-c .block-c-consequences .consequence-photo .photo-viewport{height:58mm}

body.block-c .block-c-errors{
  box-sizing:border-box!important;height:236mm!important;min-height:236mm!important;
  break-before:page!important;page-break-before:always!important;
  break-inside:avoid-page!important;page-break-inside:avoid!important;
  padding:7mm!important;background:#F0F1EE!important;border-left:1.5mm solid #CFFF00!important
}
body.block-c .block-c-errors .section-body{
  min-height:174mm!important;display:grid!important;columns:auto!important;column-count:auto!important;
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
  grid-template-rows:repeat(var(--error-rows),minmax(0,1fr))!important;
  grid-auto-flow:row!important;gap:2.5mm 8mm!important
}
body.block-c .block-c-errors .error-card{
  min-width:0;padding:2.2mm 0 1.8mm;border-top:.25mm solid #969A96;
  break-inside:avoid-page;page-break-inside:avoid
}
body.block-c .block-c-errors .error-card h3{margin:0 0 1.2mm;font:600 9.4pt/1.2 Avenir,sans-serif}
body.block-c .block-c-errors .error-card p{margin:0;font-size:8.65pt;line-height:1.28}

body.block-c .block-c-synthesis{
  box-sizing:border-box!important;height:236mm!important;min-height:236mm!important;
  break-before:page!important;page-break-before:always!important;
  break-inside:avoid-page!important;page-break-inside:avoid!important;
  display:flex!important;flex-direction:column!important;padding:8mm!important;
  background:#F0F1EE!important;border-left:1.5mm solid #CFFF00!important
}
body.block-c .block-c-synthesis .section-body{
  columns:2!important;column-count:2!important;column-gap:8mm!important;
  column-rule:.2mm solid #B9BCB9;font-size:9.5pt;line-height:1.3
}
body.block-c .block-c-synthesis .synthesis-photo{margin-top:auto!important;margin-bottom:0!important}
body.block-c .block-c-synthesis .synthesis-photo .photo-viewport{height:82mm!important}

body.block-c .glossary-two-column{
  box-sizing:border-box!important;height:236mm!important;min-height:236mm!important;
  display:flex!important;flex-direction:column!important;padding:7mm!important;
  break-inside:avoid-page!important;page-break-inside:avoid!important
}
body.block-c .glossary-two-column .section-body{
  flex:1 1 auto!important;min-height:0!important;height:auto!important;
  display:grid!important;grid-auto-flow:column!important;
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
  grid-template-rows:repeat(var(--glossary-rows),minmax(0,1fr))!important;
  align-content:stretch!important;gap:0 9mm!important;font-size:10.2pt;line-height:1.3
}
body.block-c .glossary-two-column .section-body p{
  min-width:0;margin:0!important;padding:2.5mm 0 2mm!important;
  border-top:.2mm solid #AEB1AD;break-inside:avoid-page
}

body.block-c .block-c-references{
  box-sizing:border-box!important;min-height:224mm!important;padding:7mm!important;
  background:#FAFAF8!important
}
body.block-c .block-c-references .section-body{font:8.85pt/1.28 Avenir,sans-serif!important}
body.block-c .block-c-references .section-body ul{
  min-height:174mm!important;display:grid!important;columns:auto!important;column-count:auto!important;
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
  grid-template-rows:repeat(var(--reference-rows),auto)!important;
  grid-auto-flow:column!important;align-content:space-between!important;
  gap:2mm 9mm!important;margin:0!important;padding:0!important
}
body.block-c .block-c-references li{
  min-width:0;margin:0!important;padding:0!important;break-inside:avoid-page!important;
  page-break-inside:avoid!important;overflow-wrap:normal!important;word-break:normal!important;hyphens:none!important
}
body.block-c.document-n25 .block-c-references
a[href="https://research.google/pubs/dora-2025-state-of-ai-assisted-software-development-report/"]
.url-segment:nth-of-type(4){font-size:7pt!important;letter-spacing:-.02em!important}
body.block-c.document-n23 .block-c-references
a[href="https://research.google/pubs/dora-2025-state-of-ai-assisted-software-development-report/"]{
  font-size:7pt!important;letter-spacing:-.025em!important
}

/* The Commons scene receives a deterministic crop during assembly. The NIST
   portrait keeps its full vertical framing against the neutral card field. */
body.block-c .contributor-jan-vom-brocke .portrait-frame img{
  width:100%!important;height:100%!important;max-width:none!important;
  object-fit:cover!important;object-position:center!important;transform:none!important
}
body.block-c .contributor-murugiah-souppaya .portrait-frame img{
  width:100%!important;height:100%!important;max-width:none!important;
  object-fit:contain!important;object-position:center!important;transform:none!important;
  background:#D8DAD7
}

/* N24 keeps the complete four-line opening paragraph of section 08 on the
   preceding page.  Only the inter-section margin changes; prose and type do
   not. */
body.block-c:is(.document-n23,.document-n24) #section-07{margin-bottom:2mm!important}

/* Recurring end matter is composed as editorial spreads, not as isolated
   cards stretched with artificial whitespace. */
body.block-c .block-c-errors{
  box-sizing:border-box!important;height:236mm!important;min-height:236mm!important;
  break-before:page!important;page-break-before:always!important;
  break-inside:avoid-page!important;page-break-inside:avoid!important;
  margin:0!important;padding:7mm!important;display:grid!important;
  grid-template-rows:auto minmax(0,1fr) auto!important
}
body.block-c .block-c-errors .section-body{
  min-height:0!important;height:auto!important;display:grid!important;
  columns:auto!important;column-count:auto!important;
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
  grid-template-rows:repeat(var(--error-rows),minmax(0,1fr))!important;
  grid-auto-flow:row!important;align-content:stretch!important;gap:1.8mm 8mm!important
}
body.block-c .block-c-errors .error-card{
  display:block;margin:0!important;padding:1.7mm 0 1.3mm!important;
  break-inside:avoid-page!important;page-break-inside:avoid!important
}
body.block-c .block-c-errors .error-card h3{font-size:9.3pt!important;line-height:1.17!important;margin-bottom:.8mm!important}
body.block-c .block-c-errors .error-card p{font-size:8.45pt!important;line-height:1.2!important}
body.block-c .block-c-errors .errors-photo{margin:3mm 0 0!important}
body.block-c .block-c-errors .errors-photo .photo-viewport{height:34mm!important}

body.block-c .consequences-limits-page{
  box-sizing:border-box!important;height:236mm!important;min-height:236mm!important;
  break-before:page!important;page-break-before:always!important;
  break-inside:avoid-page!important;page-break-inside:avoid!important;
  display:grid!important;grid-template-columns:1fr!important;grid-template-rows:repeat(2,minmax(0,1fr))!important;
  gap:5mm!important;margin:0!important;padding:8mm!important;background:#F0F1EE!important;
  border-left:1.5mm solid #CFFF00!important
}
body.block-c .consequences-limits-page .reading-section{
  min-width:0!important;height:auto!important;min-height:0!important;margin:0!important;padding:0!important;
  background:transparent!important;border:0!important;break-before:auto!important;page-break-before:auto!important;
  break-inside:auto!important;page-break-inside:auto!important
}
body.block-c .consequences-limits-page .block-c-limits{
  padding-top:5mm!important;border-top:.3mm solid #9A9D99!important;border-left:0!important
}
body.block-c .consequences-limits-page .section-heading h2{font-size:22pt!important;line-height:1!important}
body.block-c .consequences-limits-page .section-marker{white-space:nowrap!important}
body.block-c .consequences-limits-page .section-lead{font-size:9.15pt!important;line-height:1.27!important}
body.block-c .consequences-limits-page .section-body{
  columns:2!important;column-count:2!important;column-gap:8mm!important;
  column-rule:.2mm solid #B9BCB9!important;display:block!important;
  font-size:8.75pt!important;line-height:1.25!important
}
body.block-c .consequences-limits-page .section-body p{margin:0 0 2.4mm!important}
body.block-c.document-n15 .consequences-limits-page{
  grid-template-rows:auto auto!important;gap:3mm!important;padding:6mm 7mm!important
}
body.block-c.document-n15 .consequences-limits-page .block-c-limits{padding-top:3mm!important}
body.block-c.document-n15 .consequences-limits-page .section-body{
  font-size:8.45pt!important;line-height:1.2!important;column-gap:7.5mm!important
}
body.block-c.document-n15 .consequences-limits-page .section-body p{margin-bottom:1.4mm!important}
body.block-c:is(.document-n12,.document-n26) .consequences-limits-page{
  grid-template-rows:auto minmax(0,1fr)!important;gap:3mm!important;padding:6mm 7mm!important
}
body.block-c:is(.document-n12,.document-n26) .consequences-limits-page .block-c-limits{padding-top:3mm!important}
body.block-c:is(.document-n12,.document-n26) .consequences-limits-page .section-body{
  font-size:8.75pt!important;line-height:1.22!important;column-gap:7.5mm!important
}
body.block-c:is(.document-n12,.document-n26) .consequences-limits-page .section-body p{margin-bottom:1.5mm!important}
body.block-c .consequences-limits-page.has-consequence-photo{
  grid-template-rows:auto auto minmax(46mm,1fr)!important;gap:4mm!important
}
body.block-c .consequences-limits-page.has-consequence-photo .reading-section{padding:0!important}
body.block-c .consequences-limits-page.has-consequence-photo .block-c-limits{padding-top:4mm!important}
body.block-c .consequences-limits-page.has-consequence-photo .consequence-photo{
  min-height:46mm!important;height:auto!important;margin:0!important;
  display:grid!important;grid-template-rows:minmax(0,1fr) auto!important
}
body.block-c .consequences-limits-page.has-consequence-photo .consequence-photo .photo-viewport{
  height:100%!important;min-height:38mm!important
}
body.block-c.document-n17 .consequences-limits-page.has-consequence-photo{
  grid-template-rows:auto auto 31mm!important;gap:2.5mm!important;padding:6mm 7mm!important
}
body.block-c.document-n17 .consequences-limits-page.has-consequence-photo .block-c-limits{
  padding-top:3mm!important
}
body.block-c.document-n17 .consequences-limits-page.has-consequence-photo .consequence-photo{
  min-height:31mm!important
}
body.block-c.document-n17 .consequences-limits-page.has-consequence-photo .consequence-photo .photo-viewport{
  height:25mm!important;min-height:25mm!important
}

body.block-c .pills-glossary-page{
  box-sizing:border-box!important;height:236mm!important;min-height:236mm!important;
  break-before:page!important;page-break-before:always!important;
  break-inside:avoid-page!important;page-break-inside:avoid!important;
  display:grid!important;grid-template-rows:auto minmax(0,1fr)!important;
  gap:7mm!important;margin:0!important;padding:7mm!important;background:#F0F1EE!important;
  border-left:1.5mm solid #CFFF00!important
}
body.block-c .pills-glossary-page .pill-summary,
body.block-c .pills-glossary-page .glossary-two-column{
  height:auto!important;min-height:0!important;margin:0!important;padding:0!important;
  background:transparent!important;border:0!important;break-before:auto!important;page-break-before:auto!important;
  break-inside:avoid-page!important;page-break-inside:avoid!important
}
body.block-c .pills-glossary-page .pill-summary{
  padding-bottom:5mm!important;border-bottom:.45mm solid #202020!important
}
body.block-c .pills-glossary-page .pill-summary .section-heading h2{font-size:24pt!important}
body.block-c .pills-glossary-page .pill-summary .section-body ol{
  display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:2.5mm 9mm!important;margin:2mm 0 0!important
}
body.block-c .pills-glossary-page .pill-summary .section-body li{
  font-size:9.35pt!important;line-height:1.27!important
}
body.block-c .pills-glossary-page .glossary-two-column{display:block!important}
body.block-c .pills-glossary-page .glossary-two-column::after{content:none!important;display:none!important}
body.block-c .pills-glossary-page .glossary-two-column .section-heading h2{font-size:24pt!important}
body.block-c .pills-glossary-page .glossary-two-column .section-body{
  display:grid!important;grid-auto-flow:row!important;
  grid-template-columns:repeat(3,minmax(0,1fr))!important;grid-template-rows:none!important;
  align-content:start!important;gap:0 6mm!important;font-size:8.9pt!important;line-height:1.25!important
}
body.block-c .pills-glossary-page .glossary-two-column .section-body p{
  padding:2.2mm 0 1.8mm!important;margin:0!important
}
body.document-n18.block-c .pills-glossary-page{
  height:232mm!important;min-height:232mm!important;padding:5mm 6mm!important;gap:3.5mm!important
}
body.document-n18.block-c .pills-glossary-page .pill-summary{
  padding-bottom:3mm!important
}
body.document-n18.block-c .pills-glossary-page .pill-summary .section-heading h2,
body.document-n18.block-c .pills-glossary-page .glossary-two-column .section-heading h2{
  font-size:21pt!important;line-height:1!important;margin-bottom:2mm!important
}
body.document-n18.block-c .pills-glossary-page .pill-summary .section-body ol{
  grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:2mm 7mm!important;margin-top:1mm!important
}
body.document-n18.block-c .pills-glossary-page .pill-summary .section-body li{
  font-size:8.8pt!important;line-height:1.2!important;font-weight:600!important
}
body.document-n18.block-c .pills-glossary-page .glossary-two-column .section-body{
  font-size:8.25pt!important;line-height:1.17!important;gap:0 5mm!important
}
body.document-n18.block-c .pills-glossary-page .glossary-two-column .section-body p{
  padding:1.35mm 0 1mm!important
}
body.document-n19.block-c .pills-glossary-page{
  height:232mm!important;min-height:232mm!important;padding:5mm 6mm!important;gap:3.5mm!important
}
body.document-n19.block-c .pills-glossary-page .pill-summary{padding-bottom:3mm!important}
body.document-n19.block-c .pills-glossary-page .pill-summary .section-heading h2,
body.document-n19.block-c .pills-glossary-page .glossary-two-column .section-heading h2{
  font-size:21pt!important;line-height:1!important;margin-bottom:2mm!important
}
body.document-n19.block-c .pills-glossary-page .pill-summary .section-body ol{
  grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:2mm 7mm!important;margin-top:1mm!important
}
body.document-n19.block-c .pills-glossary-page .pill-summary .section-body li{
  font-size:8.8pt!important;line-height:1.2!important;font-weight:600!important
}
body.document-n19.block-c .pills-glossary-page .glossary-two-column .section-body{
  font-size:8.25pt!important;line-height:1.17!important;gap:0 5mm!important
}
body.document-n19.block-c .pills-glossary-page .glossary-two-column .section-body p{
  padding:1.35mm 0 1mm!important
}
body.document-n20.block-c .pills-glossary-page{
  height:232mm!important;min-height:232mm!important;padding:5mm 6mm!important;gap:3.5mm!important
}
body.document-n20.block-c .pills-glossary-page .pill-summary{padding-bottom:3mm!important}
body.document-n20.block-c .pills-glossary-page .pill-summary .section-heading h2,
body.document-n20.block-c .pills-glossary-page .glossary-two-column .section-heading h2{
  font-size:21pt!important;line-height:1!important;margin-bottom:2mm!important
}
body.document-n20.block-c .pills-glossary-page .pill-summary .section-body ol{
  grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:2mm 7mm!important;margin-top:1mm!important
}
body.document-n20.block-c .pills-glossary-page .pill-summary .section-body li{
  font-size:8.8pt!important;line-height:1.2!important;font-weight:600!important
}
body.document-n20.block-c .pills-glossary-page .glossary-two-column .section-body{
  font-size:8.25pt!important;line-height:1.17!important;gap:0 5mm!important
}
body.document-n20.block-c .pills-glossary-page .glossary-two-column .section-body p{
  padding:1.35mm 0 1mm!important
}
body.document-n21.block-c .pills-glossary-page{
  height:232mm!important;min-height:232mm!important;padding:5mm 6mm!important;gap:3.5mm!important
}
body.document-n21.block-c .pills-glossary-page .pill-summary{padding-bottom:3mm!important}
body.document-n21.block-c .pills-glossary-page .pill-summary .section-heading h2,
body.document-n21.block-c .pills-glossary-page .glossary-two-column .section-heading h2{
  font-size:21pt!important;line-height:1!important;margin-bottom:2mm!important
}
body.document-n21.block-c .pills-glossary-page .pill-summary .section-body ol{
  grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:2mm 7mm!important;margin-top:1mm!important
}
body.document-n21.block-c .pills-glossary-page .pill-summary .section-body li{
  font-size:8.8pt!important;line-height:1.2!important;font-weight:600!important
}
body.document-n21.block-c .pills-glossary-page .glossary-two-column .section-body{
  font-size:8.25pt!important;line-height:1.17!important;gap:0 5mm!important
}
body.document-n21.block-c .pills-glossary-page .glossary-two-column .section-body p{
  padding:1.35mm 0 1mm!important
}

body.block-c .block-c-handoff-out{
  box-sizing:border-box!important;height:auto!important;min-height:72mm!important;
  break-before:auto!important;page-break-before:auto!important;
  break-inside:avoid-page!important;page-break-inside:avoid!important;
  display:grid!important;grid-template-columns:minmax(0,.92fr) minmax(0,1.08fr)!important;
  align-items:start!important;column-gap:10mm!important;
  margin:6mm 0 7mm!important;padding:10mm 11mm!important;
  background:#E3E6E4!important;border-left:1.5mm solid #CFFF00!important
}
body.block-c .block-c-handoff-out .section-heading{grid-column:1;margin:0!important}
body.block-c .block-c-handoff-out .section-marker{white-space:nowrap!important}
body.block-c .block-c-handoff-out .section-marker b{gap:1mm!important;font-size:6.4pt!important}
body.block-c .block-c-handoff-out .section-heading h2{font-size:25pt;line-height:.98;margin-bottom:0!important}
body.block-c .block-c-handoff-out .section-body{grid-column:2;columns:auto!important;column-count:auto!important;margin:0!important}
body.block-c .block-c-handoff-out .section-body p{font-size:9.5pt;line-height:1.34;margin-bottom:2.5mm}

body.block-c .handoff-synthesis-page{
  box-sizing:border-box!important;height:236mm!important;min-height:236mm!important;
  break-before:page!important;page-break-before:always!important;
  break-inside:avoid-page!important;page-break-inside:avoid!important;
  display:grid!important;grid-template-rows:auto minmax(0,1fr)!important;
  gap:4mm!important;margin:0!important;padding:0!important
}
body.block-c .handoff-synthesis-page .block-c-handoff-out{
  min-height:0!important;margin:0!important;padding:5mm 7mm!important;
  grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr)!important;column-gap:7mm!important
}
body.block-c .handoff-synthesis-page .block-c-handoff-out .section-heading h2{
  font-size:19pt!important;line-height:.98!important
}
body.block-c .handoff-synthesis-page .block-c-handoff-out .section-body p{
  font-size:8.2pt!important;line-height:1.22!important;margin:0!important
}
body.block-c .handoff-synthesis-page .block-c-synthesis{
  min-height:0!important;height:auto!important;margin:0!important;padding:7mm!important;
  break-before:auto!important;page-break-before:auto!important
}
body.block-c .handoff-synthesis-page .block-c-synthesis .section-body{
  font-size:8.9pt!important;line-height:1.24!important
}
body.block-c .handoff-synthesis-page .block-c-synthesis .synthesis-photo .photo-viewport{
  height:56mm!important
}
body.block-c.document-n11 .handoff-synthesis-page .block-c-synthesis .synthesis-photo{
  margin-top:4mm!important
}
body.block-c.document-n11 .handoff-synthesis-page .block-c-synthesis .synthesis-photo .photo-viewport{
  height:52mm!important
}

/* Measured closing adjustments.  These move complete semantic units into
   existing usable space; they do not manufacture density through tracking or
   paragraph spacing. */
body.block-c:is(.document-n13,.document-n15) .block-c-handoff-out{
  min-height:0!important;margin:0 0 2mm!important;padding:3.5mm 6mm!important;
  grid-template-columns:minmax(0,.82fr) minmax(0,1.18fr)!important;column-gap:7mm!important
}
body.block-c:is(.document-n13,.document-n15) .block-c-handoff-out .section-heading h2{
  font-size:17.5pt!important;line-height:.98!important
}
body.block-c:is(.document-n13,.document-n15) .block-c-handoff-out .section-body p{
  font-size:7.6pt!important;line-height:1.16!important;margin-bottom:1mm!important
}
body.block-c.document-n15 .reading-section.block-c-limits .section-body{
  columns:2!important;column-count:2!important;column-gap:8mm!important;
  column-rule:.2mm solid #C5C7C5!important
}
body.block-c.document-n16 .reading-section.block-c-limits{
  break-before:auto!important;page-break-before:auto!important;
  break-inside:auto!important;page-break-inside:auto!important;
  min-height:0!important;height:auto!important;margin-bottom:0!important;padding:6mm 8mm!important;
  display:block!important;justify-content:initial!important
}
body.block-c.document-n16 .reading-section.block-c-limits .section-body{
  columns:2!important;column-count:2!important;column-gap:8mm!important;
  column-rule:.2mm solid #C5C7C5!important;font-size:9pt!important;line-height:1.24!important
}
body.block-c.document-n16 .block-c-consequences .consequence-photo .photo-viewport{height:38mm!important}
body.block-c.document-n16 .block-c-consequences>.section-body:not(.section-lead){
  columns:2!important;column-count:2!important;column-gap:8mm!important;
  column-rule:.2mm solid #C5C7C5!important
}
body.block-c.document-n16 .block-c-handoff-out{
  min-height:0!important;margin:0 0 1mm!important;padding:3mm 5mm!important;
  grid-template-columns:minmax(0,.82fr) minmax(0,1.18fr)!important;column-gap:7mm!important
}
body.block-c.document-n16 .block-c-handoff-out .section-heading h2{font-size:16.5pt!important;line-height:.96!important}
body.block-c.document-n16 .block-c-handoff-out .section-body p{font-size:7.4pt!important;line-height:1.14!important;margin-bottom:.8mm!important}

/* METSI N11–N36 v5 · canonical editorial reconstruction
   The stable grid and type system remain shared; hierarchy and photographic
   mass return to the approved N02/N10 language. */
body.block-c .block-c-contents .contents-layout{
  grid-template-columns:minmax(0,1.48fr) minmax(0,.52fr)!important;
  gap:8mm!important;height:205mm!important;align-items:stretch!important
}
body.block-c .block-c-contents .contents-layout figure{
  align-self:stretch!important;height:205mm!important;background:transparent!important
}
body.block-c .block-c-contents .contents-photo-viewport{
  height:178mm!important;background:#D5D7D4!important
}
body.block-c .block-c-contents .contents-photo-viewport>img{
  width:100%!important;height:178mm!important;object-fit:cover!important;object-position:center!important
}
body.block-c .block-c-contents .contents-layout figure figcaption{
  padding-top:3mm!important;font-size:7.15pt!important;line-height:1.32!important
}

body.block-c .authors-page{padding:15mm 17mm!important}
body.block-c .authors-page .contributors-grid{
  gap:5mm 7mm!important;margin-top:5mm!important
}
body.block-c .authors-page .contributor{
  min-height:76mm!important;text-align:center!important;padding:0 1mm 4mm!important
}
body.block-c .authors-page .portrait-frame{
  width:32mm!important;height:32mm!important;margin:0 auto 2.5mm!important;
  border-radius:50%!important;overflow:hidden!important;background:#D8DAD7!important
}
body.block-c .authors-page .portrait-frame img{
  width:100%!important;height:100%!important;object-fit:cover!important;
  object-position:center 22%!important;border-radius:50%!important;filter:grayscale(1) contrast(1.03)!important
}
body.block-c .authors-page .portrait-unavailable{
  width:100%!important;height:100%!important;border-radius:50%!important;overflow:hidden!important
}
body.block-c .authors-page .contributor>b{
  display:block!important;margin:.5mm 0!important;font:400 13pt/1 Didot,serif!important;color:#777!important
}
body.block-c .authors-page .contributor h3{
  margin:1mm 0 1.3mm!important;font:600 8.1pt/1.15 Avenir,sans-serif!important;text-transform:uppercase!important
}
body.block-c .authors-page .contributor-work{min-height:17mm!important;margin:0 0 1.5mm!important}
body.block-c .authors-page .contributor-work cite{
  display:block!important;font:italic 6.9pt/1.22 Baskerville,Georgia,serif!important;color:#30302E!important
}
body.block-c .authors-page .contributor-work small{
  display:block!important;margin-top:1mm!important;font:5.9pt/1.2 Avenir,sans-serif!important;color:#666!important
}
body.block-c .authors-page .contributor p{
  margin:0!important;text-align:left!important;font:6.75pt/1.28 Avenir,sans-serif!important;color:#555!important
}
body.block-c .authors-page blockquote{margin-top:4mm!important}

body.block-c .hotel-canonical-anchor .photo-viewport{
  height:56mm!important;background:#111!important
}
body.block-c .hotel-canonical-anchor img{
  width:100%!important;height:100%!important;object-fit:cover!important;object-position:center!important;filter:none!important
}
body.block-c .hotel-canonical-anchor figcaption{
  padding:0 7mm!important;margin-top:1.6mm!important
}

body.block-c .pills-glossary-page .pill-summary .section-body li{
  font-weight:600!important;font-size:9.6pt!important;line-height:1.3!important
}
body.block-c .pills-glossary-page .glossary-two-column .section-body{
  font-size:9.15pt!important;line-height:1.28!important
}
body.block-c .block-c-references .section-body ul{
  min-height:0!important;align-content:start!important;grid-auto-rows:auto!important;gap:5mm 9mm!important
}
body.block-c .block-c-references li{font-size:8.95pt!important;line-height:1.3!important}

/* Six content-driven variants prevent the corpus from returning to a single
   mechanical page sequence.  They alter mass and alignment, never body size. */
body.block-c.editorial-variant-2 .block-c-contents .contents-layout{
  grid-template-columns:minmax(0,.56fr) minmax(0,1.44fr)!important
}
body.block-c.editorial-variant-2 .block-c-contents .contents-layout ol{grid-column:2!important}
body.block-c.editorial-variant-2 .block-c-contents .contents-layout figure{grid-column:1!important;grid-row:1!important}
body.block-c.editorial-variant-3 .block-c-contents .contents-layout{
  grid-template-columns:minmax(0,1.65fr) minmax(0,.35fr)!important;gap:6mm!important
}
body.block-c.editorial-variant-4 .block-c-contents .contents-layout{
  grid-template-columns:minmax(0,1.25fr) minmax(0,.75fr)!important
}
body.block-c.editorial-variant-5 .block-c-contents .contents-layout{
  grid-template-columns:minmax(0,.7fr) minmax(0,1.3fr)!important
}
body.block-c.editorial-variant-5 .block-c-contents .contents-layout ol{grid-column:2!important}
body.block-c.editorial-variant-5 .block-c-contents .contents-layout figure{grid-column:1!important;grid-row:1!important}
body.block-c.editorial-variant-6 .block-c-contents .contents-layout{
  grid-template-columns:minmax(0,1.55fr) minmax(0,.45fr)!important
}

/* N11 preparation is deliberately image-free. A small typographic expansion
   restores page balance without manufacturing decorative whitespace. */
body.block-c.document-n11 .questions .section-body{
  font-size:11.7pt!important;line-height:1.45!important
}
body.block-c.document-n11 .questions .section-body ol{
  gap:14mm 12mm!important
}
body.block-c.document-n11 .questions .section-body>p:last-child{
  margin-top:12mm!important
}
body.block-c.document-n17 .questions .section-body ol{gap:23mm 12mm!important}
body.block-c.document-n17 .questions .section-body>p:last-child{margin-top:19mm!important}
'''


V8_EDITORIAL_CORRECTIONS = r'''
/* METSI N11–N36 v8 · convergence with the approved N00–N10 editorial system.
   These rules remove artificial page inflation introduced by v7 while keeping
   every audited source block, approved image and infographic intact. */

/* Contents photography is an orienting apparatus and remains neutral. */
body.block-c .contents-photo-viewport img{
  filter:none!important
}

/* A thesis is a compact argumentative hinge, not an oversized poster. */
body.block-c .block-c-thesis,
body.block-c .thesis-with-approved-plate{
  height:auto!important;min-height:0!important;display:block!important;
  justify-content:initial!important;padding:7mm!important;
  break-before:page!important;page-break-before:always!important;
  break-inside:avoid-page!important;page-break-inside:avoid!important
}
body.block-c .block-c-thesis .section-lead{max-width:none!important;margin-bottom:3mm!important}
body.block-c .block-c-thesis .section-lead p{
  font:400 18pt/1.3 Didot,"Bodoni 72",serif!important
}
body.block-c .block-c-thesis .section-body:not(.section-lead){
  font-size:10.8pt!important;line-height:1.4!important
}
body.block-c .thesis-infographic-page{
  box-sizing:border-box!important;height:236mm!important;min-height:236mm!important;
  display:grid!important;grid-template-rows:auto minmax(0,1fr)!important;gap:5mm!important;
  break-before:page!important;page-break-before:always!important;
  break-after:page!important;page-break-after:always!important
}
body.block-c .thesis-infographic-page .block-c-thesis{
  break-before:auto!important;page-break-before:auto!important;
  margin:0!important;padding:6mm 7mm!important
}
body.block-c .thesis-infographic-page .block-c-thesis .section-lead p{
  font-size:15.5pt!important;line-height:1.27!important
}
body.block-c .thesis-infographic-page .approved-infographic-page{
  height:auto!important;min-height:0!important;padding:5mm 8mm 6mm!important;
  break-before:auto!important;page-break-before:auto!important;
  break-after:auto!important;page-break-after:auto!important
}
body.block-c .thesis-infographic-page .approved-infographic-page header{padding-top:3mm!important}
body.block-c .thesis-infographic-page .approved-infographic-page header p{
  margin-top:3mm!important;font-size:14.5pt!important;line-height:1.16!important
}
body.block-c .thesis-infographic-page .approved-infographic-page figure{
  min-height:0!important;margin-top:3mm!important;justify-content:flex-start!important
}
body.block-c .thesis-infographic-page .approved-infographic-page img{
  flex:1 1 auto!important;height:100%!important;max-height:118mm!important
}
body.block-c .thesis-infographic-page .approved-infographic-page figcaption{margin-top:2mm!important}

/* The readable rebuild keeps each compact thesis and decision map on one page,
   but gives the map enough physical width for labels to remain legible in
   print.  Documents enter this selector only after individual visual QA. */
body.block-c.document-n11 .thesis-infographic-page,
body.block-c.document-n12 .thesis-infographic-page,
body.block-c.document-n13 .thesis-infographic-page{
  grid-template-rows:128mm minmax(0,1fr)!important;gap:3mm!important
}
body.block-c.document-n11 .thesis-infographic-page .block-c-thesis,
body.block-c.document-n12 .thesis-infographic-page .block-c-thesis,
body.block-c.document-n13 .thesis-infographic-page .block-c-thesis{
  height:128mm!important;padding:4mm 6mm!important
}
body.block-c.document-n11 .thesis-infographic-page .block-c-thesis .section-heading,
body.block-c.document-n12 .thesis-infographic-page .block-c-thesis .section-heading,
body.block-c.document-n13 .thesis-infographic-page .block-c-thesis .section-heading{
  margin-bottom:2mm!important
}
body.block-c.document-n11 .thesis-infographic-page .block-c-thesis .section-lead p,
body.block-c.document-n12 .thesis-infographic-page .block-c-thesis .section-lead p,
body.block-c.document-n13 .thesis-infographic-page .block-c-thesis .section-lead p{
  font-size:14.6pt!important;line-height:1.2!important
}
body.block-c.document-n11 .thesis-infographic-page .block-c-thesis .section-body:not(.section-lead),
body.block-c.document-n12 .thesis-infographic-page .block-c-thesis .section-body:not(.section-lead),
body.block-c.document-n13 .thesis-infographic-page .block-c-thesis .section-body:not(.section-lead){
  font-size:9.7pt!important;line-height:1.28!important
}
body.block-c.document-n11 .thesis-infographic-page .approved-infographic-page,
body.block-c.document-n12 .thesis-infographic-page .approved-infographic-page,
body.block-c.document-n13 .thesis-infographic-page .approved-infographic-page{
  padding:3mm 5mm 4mm!important
}
body.block-c.document-n11 .thesis-infographic-page .approved-infographic-page header,
body.block-c.document-n12 .thesis-infographic-page .approved-infographic-page header,
body.block-c.document-n13 .thesis-infographic-page .approved-infographic-page header{
  padding-top:2mm!important
}
body.block-c.document-n11 .thesis-infographic-page .approved-infographic-page header p,
body.block-c.document-n12 .thesis-infographic-page .approved-infographic-page header p,
body.block-c.document-n13 .thesis-infographic-page .approved-infographic-page header p{
  margin-top:2mm!important;font-size:11.8pt!important;line-height:1.14!important
}
body.block-c.document-n11 .thesis-infographic-page .approved-infographic-page figure,
body.block-c.document-n12 .thesis-infographic-page .approved-infographic-page figure,
body.block-c.document-n13 .thesis-infographic-page .approved-infographic-page figure{
  margin-top:2mm!important;align-items:center!important
}
body.block-c.document-n11 .thesis-infographic-page .approved-infographic-page img,
body.block-c.document-n12 .thesis-infographic-page .approved-infographic-page img,
body.block-c.document-n13 .thesis-infographic-page .approved-infographic-page img{
  flex:none!important;width:128mm!important;height:auto!important;max-height:79mm!important
}
body.block-c.document-n11 .thesis-infographic-page .approved-infographic-page figcaption,
body.block-c.document-n12 .thesis-infographic-page .approved-infographic-page figcaption,
body.block-c.document-n13 .thesis-infographic-page .approved-infographic-page figcaption{
  margin-top:1.5mm!important;font-size:6.7pt!important;line-height:1.18!important
}

/* Recurring study apparatus uses content-driven height. No page is filled by
   enlarged gaps, a forced 236 mm card or a decorative photograph. */
body.block-c .pills-glossary-page{
  height:auto!important;min-height:0!important;padding:0!important;gap:5mm!important
}
body.block-c .pill-summary{
  height:auto!important;min-height:0!important;display:block!important;
  padding:6mm 7mm!important
}
body.block-c .pill-summary .pills-photo{display:none!important}
body.block-c .pill-summary .section-body ol{
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:3.5mm 9mm!important;margin-top:3mm!important
}
body.block-c .pill-summary .section-body li{
  font-size:10pt!important;line-height:1.32!important;font-weight:600!important
}
body.block-c .glossary-two-column{
  height:auto!important;min-height:0!important;padding:6mm 7mm!important
}
body.block-c .glossary-two-column .section-body,
body.block-c .pills-glossary-page .glossary-two-column .section-body{
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
  font-size:9.2pt!important;line-height:1.29!important;gap:0 9mm!important
}
body.block-c .glossary-two-column .section-body p{padding:2.7mm 0 2.3mm!important}

/* Preparation is deliberately image-free and evenly paced. */
body.block-c .questions{
  height:auto!important;min-height:0!important;display:block!important;
  padding:7mm!important
}
body.block-c .questions .preparation-photo{display:none!important}
body.block-c .questions .section-body{font-size:11.8pt!important;line-height:1.46!important}
body.block-c .questions .section-body ol{
  min-height:0!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;
  grid-template-rows:repeat(3,auto)!important;gap:14mm 12mm!important;
  margin:3mm 0 0!important
}
body.block-c .questions .section-body>p:last-child{
  margin-top:12mm!important;font-size:9pt!important;line-height:1.36!important
}

/* Final apparatus keeps the reference size readable in every N. */
body.block-c .block-c-references .section-body{
  font-size:9.2pt!important;line-height:1.34!important
}
body.block-c .block-c-references li{font-size:9.2pt!important;line-height:1.34!important}
'''


V9_N34_CORRECTIONS = r'''
/* METSI N34 v9 candidate · visual and semantic regression repair. */

/* Paper, black and volt keep separate functions. Volt never becomes small
   text over paper inside the numbered section marker. */
body.block-c .section-marker span,
body.block-c .reading-section[data-section="01"] .section-marker span{
  color:#171917!important;background:#FAFAF8!important;
  border-color:#171917!important
}

/* The dense N34 decision map is a full-page plate.  Its own title and
   hierarchy remain inside the artwork, so duplicate furniture is removed. */
body.block-c.document-n34 .block-c-thesis{
  height:auto!important;min-height:0!important;padding:6mm!important;
  margin:0 0 4mm!important;break-inside:avoid-page!important
}
body.block-c.document-n34 .block-c-thesis .section-heading{
  margin-bottom:2mm!important
}
body.block-c.document-n34 .block-c-thesis .section-heading h2{
  font-size:25pt!important;line-height:1!important
}
body.block-c.document-n34 .block-c-thesis .section-lead p{
  font-size:15pt!important;line-height:1.25!important
}
body.block-c.document-n34 .approved-infographic-page.n34-full-plate{
  height:236mm!important;min-height:236mm!important;
  padding:6mm!important;display:block!important;overflow:hidden!important;
  break-before:page!important;break-after:page!important
}
body.block-c.document-n34 .approved-infographic-page.n34-full-plate header,
body.block-c.document-n34 .approved-infographic-page.n34-full-plate figcaption{
  display:none!important
}
body.block-c.document-n34 .approved-infographic-page.n34-full-plate figure{
  width:100%!important;height:224mm!important;margin:0!important;
  display:flex!important;align-items:center!important;justify-content:center!important
}
body.block-c.document-n34 .approved-infographic-page.n34-full-plate img{
  width:168mm!important;height:224mm!important;max-width:none!important;
  max-height:none!important;object-fit:contain!important
}

/* The stage photograph remains documentary evidence, but receives a close
   portrait crop consistent with the other Referentes. */
body.block-c.document-n34 .contributor-david-snowden .portrait-frame img{
  transform:none!important;object-position:center 25%!important
}

/* Stable Hotel cast, normalized face scale and topic-specific readable copy. */
body.block-c.document-n34 .hotel-tail-2 .hotel-voices-grid article{
  min-height:48mm!important
}
body.block-c.document-n34 .hotel-tail-2 .hotel-voices-grid .hotel-portrait,
body.block-c.document-n34 .hotel-tail-2 .hotel-voices-grid img{
  height:48mm!important
}
body.block-c.document-n34 .hotel-voices-grid p{
  font-size:7.05pt!important;line-height:1.27!important;color:#343734!important
}
body.block-c.document-n34 .hotel-voice-1 img{transform:scale(1.12)!important;transform-origin:50% 24%!important}
body.block-c.document-n34 .hotel-voice-2 img{transform:scale(1.00)!important;transform-origin:50% 22%!important}
body.block-c.document-n34 .hotel-voice-3 img{transform:scale(1.28)!important;transform-origin:50% 22%!important}
body.block-c.document-n34 .hotel-voice-4 img{transform:scale(1.30)!important;transform-origin:50% 22%!important}
body.block-c.document-n34 .hotel-voice-5 img{transform:scale(1.22)!important;transform-origin:50% 22%!important}
body.block-c.document-n34 .hotel-voice-6 img{transform:scale(1.26)!important;transform-origin:50% 22%!important}
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
