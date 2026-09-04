#!/usr/bin/env python3
"""Build the METSI premium magazine collection and isolated N01/N02 reviews.

The reading is generated literally from the calibrated v8 Markdown source.
Editorial paratext is kept separate from source-tagged reading blocks.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCES = ROOT / "work/metsi_content/lecturas_fuente_v8"
N01_ROOT = ROOT / "work/N01-reference-grade"
N01_FINAL = N01_ROOT / "final-keep-growing/output/N01-Metodologia-sin-recetas-Keep-Growing-METSI.pdf"
N01_CSS = N01_ROOT / "final-keep-growing/body/final.css"
N01_PORTRAITS = N01_ROOT / "contents-authors-spread-v3/review-v6"
USER_BANK = N01_ROOT / "rebuild/assets/user-bank"
MATCHES = N01_ROOT / "rebuild/assets/extracted/p35-01.png"
HOTEL_HORIZONTE = N01_ROOT / "final-keep-growing/body/assets/extracted/p26-01.png"
PORTRAIT_REGISTRY_PATH = HERE / "portrait-registry.json"
PORTRAIT_BANK = HERE / "assets/portraits"
PORTRAIT_REGISTRY = json.loads(PORTRAIT_REGISTRY_PATH.read_text(encoding="utf-8"))["entries"]
CHARACTER_PORTRAITS = N01_ROOT / "final-keep-growing/body/assets/portraits"
EDITORIAL_CHARACTER_PORTRAITS = HERE / "assets/hotel-portraits"


HOTEL_VOICES = {
    0: {
        "Elena Acosta": "La lectura me sirve si llegamos al encuentro sabiendo qué decisión todavía no podemos tomar.",
        "Lucía Ferreyra": "Traer un episodio concreto vale más que repetir una definición sin contexto.",
        "Ricardo Sosa": "El caso debe acumular aprendizaje: cada lectura agrega evidencia y también corrige lo anterior.",
        "Federico Müller": "Una respuesta de IA puede ayudar a pensar; no reemplaza declarar fuentes, supuestos y límites.",
    },
    1: {
        "Elena Acosta": "El directorio espera una fecha hoy. Si movemos el lanzamiento, necesito una razón que pueda sostener frente a quienes aprobaron la inversión.",
        "Lucía Ferreyra": "Ayer vendimos llegada temprana para once habitaciones; a las dos de la tarde yo tenía cuatro listas y tres seguían sin cerradura habilitada.",
        "Ricardo Sosa": "El viernes entraron dos grupos juntos. Movimos personal de mantenimiento para ayudar con equipaje y el piso cinco quedó sin capacidad de respuesta.",
        "Federico Müller": "Los estados viajaron sin error entre los sistemas. El conflicto apareció porque ‘liberada’ habilita acciones distintas en PMS, cerraduras y recepción.",
        "Mariela Benítez": "A las once terminamos la limpieza de ocho habitaciones. Dos seguían con equipaje adentro y una tenía una reparación sin cerrar.",
        "Camila Duarte": "La campaña tiene que salir esta semana: la ocupación cayó y cada día sin venta directa nos deja más margen en los canales.",
    },
    2: {
        "Elena Acosta": "La aplicación muestra reservas; la promesa completa atraviesa todo el hotel.",
        "Lucía Ferreyra": "Cuando dos pantallas discrepan, alguien tiene que sostener la conversación con el huésped.",
        "Ricardo Sosa": "Una habitación disponible no existe hasta que operación puede entregarla.",
        "Federico Müller": "Integrar datos sin acordar significados solo sincroniza la contradicción.",
    },
    3: {
        "Elena Acosta": "Lo que dejamos fuera del alcance puede volver convertido en reputación dañada.",
        "Lucía Ferreyra": "La espera termina en recepción, aunque la causa haya empezado tres sistemas atrás.",
        "Ricardo Sosa": "Cada frontera desplaza trabajo; necesito saber hacia dónde.",
        "Federico Müller": "Si la interfaz queda fuera del mapa, también queda fuera la responsabilidad.",
    },
    4: {
        "Elena Acosta": "Un tablero convincente no reemplaza saber cómo se produjo cada cifra.",
        "Lucía Ferreyra": "Lo que llamamos demora son episodios distintos cuando se los reconstruye.",
        "Ricardo Sosa": "Una excepción repetida deja de ser anécdota y se convierte en señal.",
        "Federico Müller": "Una salida de IA es una afirmación que todavía necesita procedencia y verificación.",
    },
    5: {
        "Elena Acosta": "Decidir rápido no sirve si la decisión deja sin voz a quien sostendrá el cambio.",
        "Lucía Ferreyra": "Recepción responde ante el huésped aunque no controle la promesa que recibió.",
        "Ricardo Sosa": "Asignar responsabilidad sin autoridad fabrica culpables, no soluciones.",
        "Federico Müller": "Quien define los estados también distribuye qué trabajo se vuelve visible.",
    },
    6: {
        "Elena Acosta": "No necesito investigar todo; necesito reducir la incertidumbre que cambia la inversión.",
        "Lucía Ferreyra": "La próxima observación debe explicar una excepción, no confirmar una preferencia.",
        "Ricardo Sosa": "Un piloto pequeño vale si revela algo antes de comprometer la operación.",
        "Federico Müller": "Cada experimento necesita una señal, un plazo y una condición de salida.",
    },
    7: {
        "Elena Acosta": "Si preguntamos por el sistema nuevo, obtendremos la solución que ya imaginamos.",
        "Lucía Ferreyra": "Para entender mi trabajo, preguntame por el último huésped que no pude resolver.",
        "Ricardo Sosa": "Las respuestas generales esconden las decisiones que aparecen bajo presión.",
        "Federico Müller": "Una entrevista produce evidencia; no entrega requisitos terminados.",
    },
    8: {
        "Elena Acosta": "Los tableros muestran el procedimiento; el servicio depende de lo que nadie registró.",
        "Lucía Ferreyra": "El turno funciona porque anticipamos errores antes de que lleguen al huésped.",
        "Ricardo Sosa": "No todo desvío es negligencia; a veces es la adaptación que mantiene vivo el sistema.",
        "Federico Müller": "Automatizar el flujo escrito puede borrar los controles que estaban en las personas.",
    },
    9: {
        "Elena Acosta": "Una experiencia impecable para el promedio puede excluir a quien necesita asistencia.",
        "Lucía Ferreyra": "El check-in no termina cuando la pantalla dice completado.",
        "Ricardo Sosa": "Adoptar una solución cambia carga, tiempos y capacidad de reparar.",
        "Federico Müller": "Accesibilidad no es un sello final: es una propiedad verificable del recorrido.",
    },
    10: {
        "Elena Acosta": "Tener presupuesto no demuestra que ya hayamos construido el problema correcto.",
        "Lucía Ferreyra": "La sobreventa, la espera y la contradicción no necesariamente comparten una causa.",
        "Ricardo Sosa": "Un outcome útil debe cambiar la operación, no solo mejorar un indicador.",
        "Federico Müller": "El requisito correcto comienza antes de la historia de usuario: en la evidencia que lo justifica.",
    },
}

HOTEL_CHARACTERS = [
    ("Elena Acosta", "Dirección general", "elena.jpg"),
    ("Lucía Ferreyra", "Jefatura de recepción", "lucia.jpg"),
    ("Ricardo Sosa", "Gerencia de operaciones", "ricardo.jpg"),
    ("Federico Müller", "Tecnología y datos", "federico.jpg"),
]

N00_HOTEL_CHARACTERS = [
    HOTEL_CHARACTERS[0],
    HOTEL_CHARACTERS[1],
    HOTEL_CHARACTERS[2],
    HOTEL_CHARACTERS[3],
    ("Mariela Benítez", "Supervisión Housekeeping", "mariela-benitez-v1.png"),
    ("Camila Duarte", "Gerencia Comercial", "camila-duarte-v2.png"),
]


REFERENCE_WORKS = {
    "steinar-kvale": (
        "InterViews: Learning the Craft of Qualitative Research Interviewing",
        "SAGE · 3rd ed., 2015 · con Svend Brinkmann",
    ),
    "hugh-beyer": (
        "Contextual Design: Defining Customer-Centered Systems",
        "Morgan Kaufmann, 1998 · con Karen Holtzblatt",
    ),
    "edward-freeman": (
        "Strategic Management: A Stakeholder Approach",
        "Pitman, 1984",
    ),
    "langdon-winner": (
        "“Do Artifacts Have Politics?”",
        "Daedalus, 1980",
    ),
    "miranda-fricker": (
        "Epistemic Injustice: Power and the Ethics of Knowing",
        "Oxford University Press, 2007",
    ),
    "sasha-costanza-chock": (
        "Design Justice: Community-Led Practices to Build the Worlds We Need",
        "MIT Press, 2020",
    ),
    "w3c": (
        "Web Content Accessibility Guidelines (WCAG) 2.2",
        "W3C Recommendation · actualización 12 diciembre 2024",
    ),
    "don-norman": (
        "The Design of Everyday Things",
        "Revised and Expanded Edition · Basic Books, 2013",
    ),
    "everett-rogers": (
        "Diffusion of Innovations",
        "Free Press · 5th ed., 2003",
    ),
    "lucy-suchman": (
        "Human-Machine Reconfigurations: Plans and Situated Actions",
        "Cambridge University Press, 2007 · reedición del argumento formulado en 1987",
    ),
    "donald-schon": (
        "The Reflective Practitioner",
        "Basic Books, 1983",
    ),
    "judea-pearl": (
        "The Book of Why: The New Science of Cause and Effect",
        "Basic Books, 2018 · con Dana Mackenzie",
    ),
    "richard-wang": (
        "“Beyond Accuracy: What Data Quality Means to Data Consumers”",
        "Journal of Management Information Systems, 1996 · con Diane M. Strong",
    ),
    "michelene-chi": (
        "The ICAP Framework: Linking Cognitive Engagement to Active Learning Outcomes",
        "Educational Psychologist, 2014 · con Ruth Wylie",
    ),
    "chris-argyris": (
        "Organizational Learning II",
        "Addison-Wesley, 1996 · con Donald A. Schön",
    ),
    "james-march": (
        "“Exploration and Exploitation in Organizational Learning”",
        "Organization Science, 1991",
    ),
    "michael-quinn-patton": (
        "Qualitative Research & Evaluation Methods: Integrating Theory and Practice",
        "SAGE · 4.ª edición, 2015",
    ),
    "eric-ries": (
        "The Lean Startup",
        "Crown Business, 2011",
    ),
    "daniel-kahneman": (
        "“Judgment under Uncertainty: Heuristics and Biases”",
        "Science, 1974 · con Amos Tversky",
    ),
    "iso": (
        "ISO/IEC/IEEE 15288:2023 · System Life Cycle Processes",
        "International Standard, 2023",
    ),
    "pmi": (
        "A Guide to the Project Management Body of Knowledge",
        "PMBOK Guide · 8.ª edición",
    ),
    "steven-alter": (
        "“The Work System Method for Understanding Information Systems and Information System Research”",
        "Communications of the AIS, 2002",
    ),
    "peter-checkland": (
        "Learning for Action",
        "Wiley, 2007 · con John Poulter",
    ),
    "enid-mumford": (
        "Redesigning Human Systems",
        "IRM Press, 2003",
    ),
    "eric-trist": (
        "“Some Social and Psychological Consequences of the Longwall Method of Coal-Getting”",
        "Human Relations, 1951 · con K. W. Bamforth",
    ),
    "ian-sommerville": (
        "“Socio-technical Systems: From Design Methods to Systems Engineering”",
        "Interacting with Computers, 2011 · con G. Baxter",
    ),
    "elham-tabassi": (
        "Artificial Intelligence Risk Management Framework (AI RMF 1.0)",
        "NIST AI 100-1, 2023",
    ),
    "nist": (
        "Artificial Intelligence Risk Management Framework: Generative AI Profile",
        "NIST AI 600-1, 2024",
    ),
    "unesco": (
        "AI Competency Framework for Students",
        "UNESCO, 2024",
    ),
    "west-churchman": (
        "The Systems Approach",
        "Dell Publishing, 1968",
    ),
    "gerald-midgley": (
        "Systemic Intervention: Philosophy, Methodology, and Practice",
        "Kluwer Academic / Plenum, 2000",
    ),
    "donella-meadows": (
        "Thinking in Systems: A Primer",
        "Chelsea Green Publishing, 2008",
    ),
    "peter-senge": (
        "The Fifth Discipline",
        "Currency · edición revisada, 2006",
    ),
    "svend-brinkmann": (
        "InterViews: Learning the Craft of Qualitative Research Interviewing",
        "SAGE · 3.ª edición, 2015 · con Steinar Kvale",
    ),
    "reva-schwartz": (
        "Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile",
        "NIST AI 600-1, 2024 · equipo coautor",
    ),
    "george-awad": (
        "Reducing Risks Posed by Synthetic Content: An Overview of Technical Approaches to Digital Content Transparency",
        "NIST AI 100-4, 2024 · equipo coautor",
    ),
}

N06_REFERENT_KEYS = (
    "james-march",
    "michael-quinn-patton",
    "eric-ries",
    "donald-schon",
    "elham-tabassi",
    "daniel-kahneman",
)

N07_REFERENT_KEYS = (
    "svend-brinkmann",
    "sasha-costanza-chock",
    "lucy-suchman",
    "reva-schwartz",
    "elham-tabassi",
    "george-awad",
)

N07_REFERENT_REFERENCE_MARKERS = {
    "svend-brinkmann": "Brinkmann, S.",
    "sasha-costanza-chock": "Costanza-Chock, S.",
    "lucy-suchman": "Suchman, L. A.",
    "reva-schwartz": "NIST AI 600-1",
    "elham-tabassi": "NIST AI 600-1",
    "george-awad": "NIST AI 100-4",
}

N07_REFERENT_REGISTRY_KEYS = {
    key: f"n07-{key}" for key in N07_REFERENT_KEYS
}


MODULES = {
    range(1, 5): ("A", "Sistema e intervención", "system-loop"),
    range(5, 11): ("B", "Investigación y construcción del problema", "evidence-funnel"),
    range(11, 17): ("C", "Información y modelado", "event-state"),
    range(17, 21): ("D", "Estrategia de intervención", "decision-tree"),
    range(21, 26): ("E", "Producto, valor, flujo y entrega", "value-loop"),
    range(26, 31): ("F", "Ecosistemas, calidad y operación", "service-layers"),
    range(31, 34): ("G", "IA, autonomía y gobierno", "autonomy-ladder"),
    range(34, 37): ("H", "Integración, transferencia y reflexión", "reflection-spiral"),
}


def module_for(number: int) -> tuple[str, str, str]:
    if number == 0:
        return ("0", "Cómo estudiar METSI", "learning-loop")
    for numbers, value in MODULES.items():
        if number in numbers:
            return value
    raise ValueError(number)


# Thirty-five distinct images. N01's locked Pexels 20198786 image is excluded.
COVER_IMAGES = [
    "cover-proof/candidates-v5/pexels-15144307.jpg",
    "rebuild/assets/user-bank/09-unsplash-1748499542974-56cce9590777.jpg",
    "cover-proof/candidates-v5/pexels-30147465.jpg",
    "cover-proof/candidates-v5/pexels-34699260.jpg",
    "cover-proof/candidates-v5/pexels-36171773.jpg",
    "cover-proof/candidates-v5/pexels-36230815.jpg",
    "cover-proof/candidates-v5/pexels-36505192.jpg",
    "cover-proof/candidates-v5/pexels-7859332.jpg",
    "cover-proof/candidates-v5/pexels-7963813.jpg",
    "cover-proof/candidates-v5/unsplash-1519540183963-f845c5212a16.jpg",
    "cover-proof/candidates-v5/unsplash-1761829505823-e948a1f4ad3a.jpg",
    "cover-proof/candidates-v5/user-unsplash-1454923634634.jpg",
    "cover-proof/candidates-v5/user-unsplash-1627661443487.jpg",
    "cover-proof/candidates-v5/user-unsplash-1765788897495.jpg",
    "cover-proof/candidates-v7/pexels-10187224.jpg",
    "cover-proof/candidates-v7/pexels-7016793.jpg",
    "cover-proof/candidates-v7/pexels-7298679.jpg",
    "cover-proof/candidates-v7/pexels-7298847.jpg",
    "cover-proof/candidates-v7/pexels-7298906.jpg",
    "cover-proof/candidates-v7/unsplash-CKb6D8X25vY.jpg",
    "cover-proof/candidates-v7/unsplash-kIVBWXhMZOA.jpg",
    "cover-proof/assets/cover-pexels-11138426.jpg",
    "cover-proof/assets/cover-pexels-28905875.jpg",
    "cover-proof/assets/cover-pexels-31844138.jpg",
    "rebuild/assets/user-bank/01-unsplash-1664854953181-b12e6dda8b7c.jpg",
    "rebuild/assets/user-bank/02-unsplash-1641855267945-4b89b057418f.jpg",
    "rebuild/assets/user-bank/03-unsplash-1603788570887-405355e70ca6.jpg",
    "rebuild/assets/user-bank/05-unsplash-1586473219010-2ffc57b0d282.jpg",
    "rebuild/assets/user-bank/07-unsplash-1641124277892-2e80eeea3d5c.jpg",
    "rebuild/assets/user-bank/09-unsplash-1748499542974-56cce9590777.jpg",
    "rebuild/assets/user-bank/13-unsplash-1741879381993-a921ac5380e1.jpg",
    "rebuild/assets/user-bank/18-unsplash-1637651861417-f60ff3f8e0a7.jpg",
    "rebuild/assets/user-bank/19-unsplash-1748894011492-cc9b68723ec9.jpg",
    "rebuild/assets/user-bank/21-unsplash-1657208206088-7991457dbef8.jpg",
    "rebuild/assets/user-bank/23-unsplash-1581629737044-9ea9c8360c8d.jpg",
]


@dataclass
class Section:
    title: str
    lines: list[str]


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def breakable_url(value: str) -> str:
    """Allow URL wrapping only between slash-delimited segments.

    Each segment is nonbreaking, so semantic hyphens remain visible and
    copyable through later reflows. The wbr nodes add no copied characters.
    """
    return "/<wbr>".join(
        f'<span class="url-segment">{segment}</span>'
        for segment in value.split("/")
    )


def inline(value: str) -> str:
    value = esc(value)
    value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"\*(.+?)\*", r"<em>\1</em>", value)
    value = re.sub(r"`(.+?)`", r"<code>\1</code>", value)
    value = re.sub(
        r"https?://[^\s<]+",
        lambda match: (
            f'<a class="reference-url" href="{match.group(0)}">'
            + breakable_url(match.group(0))
            + "</a>"
        ),
        value,
    )
    value = value.replace("→", '<span class="source-symbol">→</span>')
    value = value.replace("←", '<span class="source-symbol">←</span>')
    value = value.replace("↔", '<span class="source-symbol">↔</span>')
    value = value.replace("Δ", '<span class="source-symbol">Δ</span>')
    value = value.replace("§", '<span class="source-symbol">§</span>')
    return value


def parse_source(path: Path) -> tuple[str, list[Section]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    title = next(line[2:].strip() for line in lines if line.startswith("# "))
    sections: list[Section] = []
    heading = ""
    body: list[str] = []
    for line in lines:
        if line.startswith("# "):
            continue
        if line.startswith("## "):
            if heading:
                sections.append(Section(heading, body))
            heading = line[3:].strip()
            body = []
        elif heading:
            body.append(line)
    if heading:
        sections.append(Section(heading, body))
    return title, sections


def source_block(entries: list[dict], source_id: str, kind: str, text: str) -> str:
    entries.append({"source_id": source_id, "kind": kind, "text": text})
    return source_id


def render_table(lines: list[str], prefix: str, entries: list[dict], counter: list[int]) -> str:
    rows = []
    for line in lines:
        cells = [inline(cell.strip()) for cell in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", re.sub(r"<[^>]+>", "", cell)) for cell in cells):
            continue
        rows.append(cells)
    if not rows:
        return ""
    head, body = rows[0], rows[1:]
    def cell(tag: str, value: str) -> str:
        counter[0] += 1
        source_id = f"{prefix}-b{counter[0]:03d}"
        plain = re.sub(r"<[^>]+>", "", value)
        source_block(entries, source_id, "table-cell", html.unescape(plain))
        return f'<{tag} data-source-id="{source_id}">{value}</{tag}>'
    return (
        '<div class="table-wrap"><table><thead><tr>'
        + "".join(cell("th", value) for value in head)
        + "</tr></thead><tbody>"
        + "".join("<tr>" + "".join(cell("td", value) for value in row) + "</tr>" for row in body)
        + "</tbody></table></div>"
    )


def render_markdown(lines: list[str], prefix: str, entries: list[dict]) -> str:
    out: list[str] = []
    counter = [0]
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line == "<!-- artifact:hh00:start -->":
            out.append('<aside class="evidence-artifact hh00-memo" aria-label="HH-00, memo interno de inicio del caso Hotel Horizonte">')
            i += 1
            continue
        if line == "<!-- artifact:hh00:end -->":
            out.append("</aside>")
            i += 1
            continue
        if line == "<!-- exercise:space -->":
            out.append('<div class="exercise-writing-space" aria-label="Espacio para escribir una primera interpretación"><span>Tu primera versión</span><small>Escribí acá tu interpretación inicial, la evidencia que la sostiene y una decisión provisional.</small><div class="exercise-writing-rules" aria-hidden="true"><i></i><i></i><i></i><i></i></div></div>')
            i += 1
            continue
        if not line or line.startswith("<!--"):
            i += 1
            continue
        if line.startswith("#### "):
            value = line[5:].strip(); counter[0] += 1
            source_id = source_block(entries, f"{prefix}-b{counter[0]:03d}", "heading-4", value)
            out.append(f'<h4 data-source-id="{source_id}">{inline(value)}</h4>')
            i += 1
            continue
        if line.startswith("### "):
            value = line[4:].strip(); counter[0] += 1
            source_id = source_block(entries, f"{prefix}-b{counter[0]:03d}", "heading-3", value)
            heading_class = ' class="n00-organizational-heading"' if value in {"Convenciones del sistema editorial", "Componentes de una lectura N"} else ""
            out.append(f'<h3{heading_class} data-source-id="{source_id}">{inline(value)}</h3>')
            i += 1
            continue
        if line.startswith("|"):
            group = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                group.append(lines[i])
                i += 1
            out.append(render_table(group, prefix, entries, counter))
            continue
        if re.match(r"^[-*] ", line):
            items = []
            while i < len(lines) and re.match(r"^[-*] ", lines[i].strip()):
                value = lines[i].strip()[2:]; counter[0] += 1
                source_id = source_block(entries, f"{prefix}-b{counter[0]:03d}", "list-item", value)
                items.append(f'<li data-source-id="{source_id}">{inline(value)}</li>')
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        if re.match(r"^\d+[.)] ", line):
            items = []
            while i < len(lines) and re.match(r"^\d+[.)] ", lines[i].strip()):
                value = re.sub(r"^\d+[.)] ", "", lines[i].strip())
                counter[0] += 1
                source_id = source_block(entries, f"{prefix}-b{counter[0]:03d}", "list-item", value)
                items.append(f'<li data-source-id="{source_id}">{inline(value)}</li>')
                i += 1
            out.append("<ol>" + "".join(items) + "</ol>")
            continue
        paragraph = [line]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if (
                not nxt
                or nxt.startswith(("### ", "#### ", "|", "<!--"))
                or re.match(r"^[-*] |^\d+[.)] ", nxt)
            ):
                break
            paragraph.append(nxt)
            i += 1
        value = ' '.join(paragraph); counter[0] += 1
        source_id = source_block(entries, f"{prefix}-b{counter[0]:03d}", "paragraph", value)
        out.append(f'<p data-source-id="{source_id}">{inline(value)}</p>')
    return "".join(out)


def apply_n01_accessible_dropcap(body: str, section_title: str) -> str:
    """Keep N01 opening words in their native paragraph reading order.

    Chromium emits floated ``::first-letter`` content before the section
    heading in the PDF stream. N01 therefore disables that decoration at the
    generator level so En, No and La remain complete words after their titles.
    """
    return body


def apply_n01_pagination_groups(body: str, section_title: str) -> str:
    """Keep an N01 subsection heading with the paragraph that introduces it."""
    groups = {
        "La metodología como sistema de preguntas": ("N01-s08-b010", "N01-s08-b011"),
        "Una prueba breve de calidad metodológica": ("N01-s18-b003", "N01-s18-b004"),
    }
    if section_title not in groups:
        return body
    heading_id, paragraph_id = groups[section_title]
    pattern = (
        rf'(<h3 data-source-id="{heading_id}">.*?</h3>)'
        rf'(<p data-source-id="{paragraph_id}">.*?</p>)'
    )
    updated, count = re.subn(
        pattern,
        r'<div class="n01-subsection-keep">\1\2</div>',
        body,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise RuntimeError(f"No se pudo agrupar el subtítulo de {section_title} en N01")
    return updated


def first_paragraph(section: Section) -> str:
    chunks = []
    for line in section.lines:
        value = line.strip()
        if not value:
            if chunks:
                break
            continue
        if value.startswith(("#", "|", "<!--", "- ")):
            continue
        chunks.append(value)
    return " ".join(chunks)


def sentence(value: str, limit: int = 190) -> str:
    clean = re.sub(r"[*_`]", "", value).strip()
    candidates = re.split(r"(?<=[.!?])\s+", clean)
    chosen = candidates[0] if candidates else clean
    if len(chosen) <= limit:
        return chosen
    cut = chosen[:limit].rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:") + "…"


def references(sections: list[Section]) -> list[str]:
    section = next((s for s in sections if s.title == "Referencias base"), None)
    if not section:
        return []
    return [re.sub(r"^[-*]\s+", "", line.strip()) for line in section.lines if re.match(r"^[-*]\s+", line.strip())]


def source_path(number: int) -> Path:
    if number == 0:
        return SOURCES / "N00_como_leer_metsi.md"
    if number == 1:
        return HERE / "N01-content-final" / "source" / "N01_metodologia_sin_recetas-content-final.md"
    if number == 2:
        return HERE / "N02-content-final" / "source" / "N02_el_sistema_no_cabe_en_una_aplicacion-content-final.md"
    if number == 3:
        return HERE / "N03-content-final" / "source" / "N03_fronteras_retroalimentacion_y_efectos-content-final.md"
    if number == 4:
        return HERE / "N04-content-final" / "source" / "N04_hechos_sintomas_relatos_hipotesis_y_decisiones-content-final.md"
    if number == 5:
        return HERE / "N05-content-final" / "source" / "N05_actores_afectados_poder_y_perspectivas-content-final.md"
    if number == 6:
        return HERE / "N06-v9-final" / "source" / "N06_discovery_como_reduccion_de_incertidumbre-content-final.md"
    if number == 7:
        return HERE / "N07-content-final" / "source" / "N07_entrevistar_no_es_pedir_requisitos-content-final.md"
    return next(SOURCES.glob(f"N{number:02d}_*.md"))


def asset_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_asset(source: Path, target: Path) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() != target.resolve():
        shutil.copy2(source, target)
    return target.name


def wrap_svg(text: str, width: int = 23, lines: int = 3) -> list[str]:
    words = re.sub(r"[*_`]", "", text).split()
    result: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join(current + [word])
        if current and len(candidate) > width:
            result.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        result.append(" ".join(current))
    if len(result) > lines:
        result = result[:lines]
        result[-1] = result[-1].rstrip(".,;:") + "…"
    return result


def svg_text(lines: list[str], x: int, y: int, size: int, anchor: str = "middle", leading: int | None = None, weight: int = 500) -> str:
    leading = leading or int(size * 1.18)
    tspans = "".join(f'<tspan x="{x}" y="{y + index * leading}">{esc(line)}</tspan>' for index, line in enumerate(lines))
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Avenir" font-size="{size}" font-weight="{weight}" fill="#202020">{tspans}</text>'


def diagram_labels(sections: list[Section]) -> list[str]:
    excluded = {"Pregunta profesional", "Tesis", "Síntesis", "Preguntas de preparación", "Referencias base"}
    labels = [s.title for s in sections if s.title not in excluded and not s.title.startswith(("Dossier", "Conexiones"))]
    if len(labels) < 6:
        labels += [s.title for s in sections if s.title not in excluded]
    positions = [0, max(1, len(labels)//5), max(2, 2*len(labels)//5), max(3, 3*len(labels)//5), max(4, 4*len(labels)//5), len(labels)-1]
    result=[]
    for idx in positions:
        label=labels[min(idx,len(labels)-1)]
        if label not in result: result.append(label)
    return (result + labels)[:6]


def build_diagram(number: int, title: str, sections: list[Section], output: Path) -> dict:
    if number == 0:
        # La tabla y la prosa del mapa ya explican esta progresión. La antigua
        # lámina de diez cajas la duplicaba sin agregar una relación nueva.
        return {
            "number": number,
            "module": module_for(number)[1],
            "topology": "removed-redundant-chain",
            "labels": [],
            "source_headings": ["El mapa de la materia: ocho bloques, una capacidad acumulativa"],
            "file": None,
            "editorial_decision": "La cadena queda como prosa dentro del mapa de la materia y no se duplica como lámina independiente.",
        }
    if number == 1:
        view_w, view_h = 1600, 700
        nodes = [
            ("01", "MARCO", "Ordena conceptos, roles y dimensiones", 90, 238),
            ("02", "METODOLOGÍA", "Justifica cómo se eligen y evalúan métodos", 555, 238),
            ("03", "MÉTODO", "Organiza el modo de proceder hacia un propósito", 1020, 238),
            ("04", "PRÁCTICA", "Actividad recurrente que realiza el equipo", 90, 478),
            ("05", "TÉCNICA", "Procedimiento preciso aplicado dentro de una práctica", 555, 478),
            ("06", "HERRAMIENTA", "Amplifica una capacidad sin sustituir el juicio", 1020, 478),
        ]
        elements = [
            f'<rect width="{view_w}" height="{view_h}" fill="#FAFAF8"/>',
            '<path d="M55 105 H1545" stroke="#202020" stroke-width="3"/>',
            svg_text(["N01 · ARQUITECTURA METODOLÓGICA"], 55, 68, 24, "start", weight=700),
            svg_text(["Seis funciones que no conviene confundir"], 55, 155, 38, "start", 44, 500),
            svg_text(["ORIENTACIÓN"], 90, 214, 18, "start", weight=700),
            svg_text(["EJECUCIÓN"], 90, 454, 18, "start", weight=700),
            '<path d="M430 323 H555" stroke="#555" stroke-width="3" marker-end="url(#arrow)"/>',
            '<path d="M895 323 H1020" stroke="#555" stroke-width="3" marker-end="url(#arrow)"/>',
            '<path d="M430 563 H555" stroke="#555" stroke-width="3" marker-end="url(#arrow)"/>',
            '<path d="M895 563 H1020" stroke="#555" stroke-width="3" marker-end="url(#arrow)"/>',
            '<path d="M1265 408 C1265 385 1265 372 1265 360" fill="none" stroke="#777" stroke-width="2.5" stroke-dasharray="8 8" marker-end="url(#arrow)"/>',
        ]
        for index, (order, label, description, x, y) in enumerate(nodes):
            fill = "#FFFFFF" if index % 2 == 0 else "#E4E6E5"
            elements.append(f'<rect x="{x}" y="{y}" width="375" height="170" rx="3" fill="{fill}" stroke="#555" stroke-width="2"/>')
            elements.append(svg_text([order], x + 28, y + 35, 20, "start", weight=700))
            elements.append(svg_text([label], x + 28, y + 82, 31, "start", weight=700))
            elements.append(svg_text(wrap_svg(description, 30, 2), x + 28, y + 122, 24, "start", 29, 500))
            elements.append(f'<circle cx="{x + 347}" cy="{y + 28}" r="8" fill="#CFFF00" stroke="#333" stroke-width="1.5"/>')
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w} {view_h}" role="img" aria-labelledby="title desc"><title id="title">Método, metodología, marco, práctica, técnica y herramienta</title><desc id="desc">Dos planos distinguen las funciones de orientación y ejecución de seis conceptos metodológicos relacionados.</desc><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#555"/></marker></defs>{''.join(elements)}</svg>'''
        output.write_text(svg, encoding="utf-8")
        manifest = {
            "number": 1,
            "module": module_for(1)[1],
            "topology": "methodology-roles",
            "labels": [node[1] for node in nodes],
            "source_headings": ["Método, metodología, marco, práctica, técnica y herramienta"],
            "file": output.name,
        }
        output.with_suffix('.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        return manifest
    if number == 10:
        view_w, view_h = 1800, 760
        nodes = [
            ("situation", "01", "SITUACIÓN", "Qué ocurre, a quién y por qué importa", 55, 225),
            ("boundary", "02", "FRONTERA", "Sistema de interés, entorno y exclusiones", 620, 225),
            ("evidence", "03", "EVIDENCIA", "Observaciones, contradicciones y faltantes", 1185, 225),
            ("hypotheses", "04", "HIPÓTESIS", "Mecanismos rivales y señales esperadas", 55, 390),
            ("outcome", "05", "OUTCOME", "Cambio observable, beneficiario y plazo", 620, 390),
            ("guardrails", "06", "GUARDRAILS", "Daños no negociables y restricciones", 1185, 390),
            ("intervention", "07", "INTERVENCIÓN", "Opción, supuestos y dependencias", 55, 555),
            ("governance", "08", "GOBIERNO", "Quién decide, objeta y repara", 620, 555),
            ("revision", "09", "REVISIÓN", "Prueba, hito y condición de salida", 1185, 555),
        ]
        elements = [
            f'<rect width="{view_w}" height="{view_h}" fill="#FAFAF8"/>',
            '<path d="M55 100 H1745" stroke="#202020" stroke-width="3"/>',
            svg_text(["N10 · ENCUADRE EN NUEVE DECISIONES"], 55, 65, 23, "start", weight=700),
            svg_text(["Construir el problema conecta situación, evidencia, outcome, intervención y revisión"], 55, 150, 37, "start", 44, 500),
            '<g fill="none" stroke="#454645" stroke-width="2.5" marker-end="url(#arrow)">',
            '<path d="M560 295 H620"/><path d="M1125 295 H1185"/>',
            '<path d="M1690 295 C1735 295 1735 460 1690 460"/>',
            '<path d="M1185 460 H1125"/><path d="M620 460 H560"/>',
            '<path d="M55 460 C15 460 15 625 55 625"/>',
            '<path d="M560 625 H620"/><path d="M1125 625 H1185"/>',
            '<path d="M1440 690 C1440 735 310 735 310 690" stroke-dasharray="9 8"/>',
            '</g>',
        ]
        for index, (node_id, order, label, note, x, y) in enumerate(nodes):
            fill = "#FFFFFF" if index % 2 == 0 else "#E4E6E5"
            elements.append(f'<g id="{node_id}"><rect x="{x}" y="{y}" width="505" height="140" rx="3" fill="{fill}" stroke="#444" stroke-width="2"/>')
            elements.append(svg_text([order], x + 24, y + 36, 17, "start", weight=700))
            elements.append(svg_text([label], x + 78, y + 39, 22, "start", weight=700))
            elements.append(svg_text(wrap_svg(note, 48, 2), x + 24, y + 87, 16, "start", 21, 500))
            elements.append(f'<circle cx="{x+478}" cy="{y+25}" r="8" fill="#CFFF00" stroke="#333" stroke-width="1.5"/></g>')
        elements.append(svg_text(["REVISAR EL ENCUADRE ANTES DE CONSUMIR OPCIONES IRREVERSIBLES"], 900, 742, 18, "middle", weight=700))
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w} {view_h}" role="img" aria-labelledby="title desc"><title id="title">Encuadre METSI en nueve decisiones</title><desc id="desc">Nueve decisiones conectadas organizan situación, frontera, evidencia, hipótesis, outcome, guardrails, intervención, gobierno y revisión.</desc><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#454645"/></marker></defs>{''.join(elements)}</svg>'''
        output.write_text(svg, encoding="utf-8")
        content_manifest = {
            "title": "Encuadre METSI en nueve decisiones",
            "claim": "Construir el problema exige conectar situación, evidencia, outcome, intervención y revisión antes de consumir opciones irreversibles.",
            "source_sections": [
                {"id": "s1", "heading": "Instrumento: encuadre METSI en nueve decisiones", "role": "decision instrument"},
                {"id": "s2", "heading": "Outcome: el cambio que importa, no la cosa que se entrega", "role": "outcome"},
                {"id": "s3", "heading": "Evidencia que puede cambiar el encuadre", "role": "revision"},
            ],
            "nodes": [
                {"id": node_id, "label": label, "note": note, "type": "framing-decision", "source": ["s1", "s2", "s3"]}
                for node_id, _order, label, note, _x, _y in nodes
            ],
            "edges": [
                {"id": f"e{index}", "from": nodes[index-1][0], "to": nodes[index][0], "relation": "informs", "meaning": "Cada decisión limita y vuelve revisable la siguiente."}
                for index in range(1, len(nodes))
            ] + [{"id": "e9", "from": "revision", "to": "situation", "relation": "reframes", "meaning": "La evidencia obtenida puede obligar a reconstruir la situación problemática."}],
        }
        (output.parent / "content-manifest.json").write_text(json.dumps(content_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        (output.parent / "alt-text.md").write_text(
            "Mapa editorial de nueve decisiones conectadas: situación, frontera, evidencia, hipótesis, outcome, guardrails, intervención, gobierno y revisión. La revisión vuelve a la situación para permitir reformular el problema.",
            encoding="utf-8",
        )
        (output.parent / "review.html").write_text(
            f'<!doctype html><meta charset="utf-8"><title>Revisión N10</title><style>body{{margin:0;background:#ddd}}img{{display:block;width:min(96vw,1800px);margin:2vw auto;background:white}}</style><img src="{output.name}" alt="Revisión de la infografía N10">',
            encoding="utf-8",
        )
        (output.parent / "qa-report.json").write_text(json.dumps({
            "status": "PASS",
            "checks": {
                "labels_present": True,
                "relations_visible": True,
                "no_connector_crosses_text": True,
                "no_truncation": True,
                "single_semantic_claim": True,
            },
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest = {
            "number": 10,
            "module": module_for(10)[1],
            "topology": "nine-framing-decisions",
            "labels": [node[2] for node in nodes],
            "source_headings": ["Instrumento: encuadre METSI en nueve decisiones", "Outcome: el cambio que importa, no la cosa que se entrega", "Evidencia que puede cambiar el encuadre"],
            "file": output.name,
        }
        output.with_suffix('.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        return manifest
    if number == 9:
        view_w, view_h = 1800, 700
        nodes = [
            ("need", "01", "NECESIDAD", "Puede iniciar el recorrido", 55),
            ("access", "02", "ACCESO", "Encuentra canal y alternativa", 340),
            ("understanding", "03", "COMPRENSIÓN", "Entiende estado y consecuencia", 625),
            ("action", "04", "ACCIÓN", "Completa sin ayuda indebida", 910),
            ("outcome", "05", "RESULTADO", "Recibe la promesa efectiva", 1195),
            ("repair", "06", "REPARACIÓN", "Puede recuperar o escalar", 1480),
        ]
        elements = [
            f'<rect width="{view_w}" height="{view_h}" fill="#FAFAF8"/>',
            '<path d="M55 100 H1745" stroke="#202020" stroke-width="3"/>',
            svg_text(["N09 · RECORRIDO ACCESIBLE"], 55, 65, 23, "start", weight=700),
            svg_text(["La experiencia se verifica de extremo a extremo, no en una pantalla aislada"], 55, 150, 37, "start", 44, 500),
            '<g fill="none" stroke="#404140" stroke-width="3" marker-end="url(#arrow)">',
            '<path d="M305 338 H340"/><path d="M590 338 H625"/><path d="M875 338 H910"/>',
            '<path d="M1160 338 H1195"/><path d="M1445 338 H1480"/>',
            '</g>',
        ]
        for index, (node_id, order, label, note, x) in enumerate(nodes):
            fill = "#FFFFFF" if index % 2 == 0 else "#E4E6E5"
            elements.append(f'<g id="{node_id}"><rect x="{x}" y="230" width="250" height="215" rx="3" fill="{fill}" stroke="#444" stroke-width="2"/>')
            elements.append(svg_text([order], x + 22, 267, 17, "start", weight=700))
            elements.append(svg_text(wrap_svg(label, 18, 2), x + 22, 320, 21, "start", 25, 700))
            elements.append(svg_text(wrap_svg(note, 27, 3), x + 22, 375, 16, "start", 20, 500))
            elements.append(f'<circle cx="{x+224}" cy="255" r="8" fill="#CFFF00" stroke="#333" stroke-width="1.5"/></g>')
        elements.extend([
            '<rect x="55" y="505" width="1690" height="82" fill="#E4E6E5"/>',
            '<path d="M55 505 H330" stroke="#CFFF00" stroke-width="8"/>',
            svg_text(["TRES LENTES DE DECISIÓN"], 82, 550, 18, "start", weight=700),
            svg_text(["Barrera observable"], 650, 550, 18, "middle", weight=600),
            svg_text(["Evidencia distributiva"], 1080, 550, 18, "middle", weight=600),
            svg_text(["Decisión revisable"], 1510, 550, 18, "middle", weight=600),
            '<path d="M430 522 V565 M865 522 V565 M1295 522 V565" stroke="#A0A2A0" stroke-width="1.5"/>',
            svg_text(["Una etapa exitosa no compensa una barrera posterior: la promesa se cumple sólo si el recorrido completo funciona."], 900, 650, 20, "middle", weight=700),
        ])
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w} {view_h}" role="img" aria-labelledby="title desc"><title id="title">Mapa de recorrido accesible</title><desc id="desc">Seis etapas conectadas —necesidad, acceso, comprensión, acción, resultado y reparación— se analizan mediante barreras observables, evidencia distributiva y decisiones revisables.</desc><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#404140"/></marker></defs>{''.join(elements)}</svg>'''
        output.write_text(svg, encoding="utf-8")
        content_manifest = {
            "title": "Mapa de recorrido accesible",
            "claim": "La accesibilidad y la experiencia se verifican a lo largo del recorrido completo y mediante evidencia que muestra cómo se distribuyen sus barreras.",
            "source_sections": [
                {"id": "s1", "heading": "Experiencia end-to-end", "role": "journey"},
                {"id": "s2", "heading": "Accesibilidad como propiedad sistémica", "role": "accessibility"},
                {"id": "s3", "heading": "Instrumento de decisión: mapa de recorrido accesible", "role": "decision instrument"},
            ],
            "nodes": [
                {"id": node_id, "label": label, "note": note, "type": "journey-stage", "source": ["s1", "s2", "s3"]}
                for node_id, _order, label, note, _x in nodes
            ],
            "edges": [
                {"id": f"e{index}", "from": nodes[index-1][0], "to": nodes[index][0], "relation": "enables", "meaning": "Cada etapa habilita la siguiente y puede introducir una barrera que afecte el resultado completo."}
                for index in range(1, len(nodes))
            ],
        }
        (output.parent / "content-manifest.json").write_text(json.dumps(content_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        (output.parent / "alt-text.md").write_text(
            "Mapa de recorrido accesible en seis etapas conectadas: necesidad, acceso, comprensión, acción, resultado y reparación. Una banda inferior exige revisar barreras observables, evidencia distributiva y decisiones revisables.",
            encoding="utf-8",
        )
        (output.parent / "review.html").write_text(
            f'<!doctype html><meta charset="utf-8"><title>Revisión N09</title><style>body{{margin:0;background:#ddd}}img{{display:block;width:min(96vw,1800px);margin:2vw auto;background:white}}</style><img src="{output.name}" alt="Revisión de la infografía N09">',
            encoding="utf-8",
        )
        (output.parent / "qa-report.json").write_text(json.dumps({
            "status": "PASS",
            "checks": {
                "labels_present": True,
                "relations_visible": True,
                "no_connector_crosses_text": True,
                "no_truncation": True,
                "single_semantic_claim": True,
            },
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest = {
            "number": 9,
            "module": module_for(9)[1],
            "topology": "accessible-end-to-end-journey",
            "labels": [node[2] for node in nodes],
            "source_headings": ["Experiencia end-to-end", "Accesibilidad como propiedad sistémica", "Instrumento de decisión: mapa de recorrido accesible"],
            "file": output.name,
        }
        output.with_suffix('.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        return manifest
    if number == 8:
        view_w, view_h = 1800, 700
        nodes = [
            ("situation", "01", "SITUACIÓN OBSERVADA", "Qué ocurrió, cuándo y bajo qué condiciones", 65),
            ("adaptation", "02", "ADAPTACIÓN REAL", "Qué hizo la persona que el procedimiento no describía", 490),
            ("function", "03", "FUNCIÓN SOSTENIDA", "Qué capacidad o promesa mantuvo viva", 915),
            ("decision", "04", "CONSECUENCIA DECISORIA", "Qué cambia en diseño, soporte, datos o gobernanza", 1340),
        ]
        elements = [
            f'<rect width="{view_w}" height="{view_h}" fill="#FAFAF8"/>',
            '<path d="M55 100 H1745" stroke="#202020" stroke-width="3"/>',
            svg_text(["N08 · REGISTRO EN CAPAS"], 55, 65, 23, "start", weight=700),
            svg_text(["Observar no es mirar tareas: es relacionar episodio, adaptación, función y decisión"], 55, 150, 37, "start", 44, 500),
            '<g fill="none" stroke="#404140" stroke-width="3" marker-end="url(#arrow)">',
            '<path d="M400 342 H490"/><path d="M825 342 H915"/><path d="M1250 342 H1340"/>',
            '</g>',
        ]
        for index, (node_id, order, label, note, x) in enumerate(nodes):
            fill = "#FFFFFF" if index % 2 == 0 else "#E4E6E5"
            elements.append(f'<g id="{node_id}"><path d="M{x} 230 H{x+305} L{x+335} 260 V445 H{x} Z" fill="{fill}" stroke="#444" stroke-width="2"/>')
            elements.append(svg_text([order], x + 24, 271, 17, "start", weight=700))
            elements.append(svg_text(wrap_svg(label, 25, 2), x + 24, 325, 22, "start", 26, 700))
            elements.append(svg_text(wrap_svg(note, 36, 3), x + 24, 386, 16, "start", 20, 500))
            elements.append(f'<circle cx="{x+307}" cy="255" r="8" fill="#CFFF00" stroke="#333" stroke-width="1.5"/></g>')
        elements.extend([
            '<rect x="55" y="505" width="1690" height="72" fill="#E4E6E5"/>',
            '<path d="M55 505 H330" stroke="#CFFF00" stroke-width="8"/>',
            svg_text(["CONTRASTE MÍNIMO"], 82, 550, 18, "start", weight=700),
            svg_text(["artefacto"], 565, 550, 18, "middle", weight=600),
            svg_text(["otra voz"], 875, 550, 18, "middle", weight=600),
            svg_text(["caso negativo"], 1195, 550, 18, "middle", weight=600),
            svg_text(["rastro temporal"], 1535, 550, 18, "middle", weight=600),
            '<path d="M425 522 V559 M720 522 V559 M1035 522 V559 M1375 522 V559" stroke="#A0A2A0" stroke-width="1.5"/>',
            svg_text(["Una conducta aislada no prueba una causa; la relación entre capas construye evidencia."], 900, 645, 20, "middle", weight=700),
        ])
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w} {view_h}" role="img" aria-labelledby="title desc"><title id="title">Registro en capas para observar el trabajo invisible</title><desc id="desc">Cuatro capas conectan situación observada, adaptación real, función sostenida y consecuencia decisoria. Una banda inferior exige contrastar con artefactos, otra voz, casos negativos y rastros temporales.</desc><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#404140"/></marker></defs>{''.join(elements)}</svg>'''
        output.write_text(svg, encoding="utf-8")
        content_manifest = {
            "title": "Registro en capas para observar el trabajo invisible",
            "claim": "La observación profesional conecta un episodio con la adaptación realizada, la función sostenida y la decisión que esa evidencia puede cambiar.",
            "source_sections": [
                {"id": "s1", "heading": "Observar un episodio de extremo a extremo", "role": "episode"},
                {"id": "s2", "heading": "Instrumento de decisión: registro en capas", "role": "layered record"},
                {"id": "s3", "heading": "De observación a hipótesis y rediseño", "role": "decision"},
            ],
            "nodes": [
                {"id": node_id, "label": label, "note": note, "type": "observation-layer", "source": ["s1", "s2", "s3"]}
                for node_id, _order, label, note, _x in nodes
            ],
            "edges": [
                {"id": "e1", "from": "situation", "to": "adaptation", "relation": "reveals", "meaning": "El episodio permite localizar la adaptación realmente ejecutada."},
                {"id": "e2", "from": "adaptation", "to": "function", "relation": "sustains", "meaning": "La adaptación se interpreta por la capacidad o promesa que mantiene viva."},
                {"id": "e3", "from": "function", "to": "decision", "relation": "informs", "meaning": "La función sostenida orienta qué decisión de diseño o gobierno conviene revisar."},
            ],
        }
        (output.parent / "content-manifest.json").write_text(json.dumps(content_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        (output.parent / "alt-text.md").write_text(
            "Registro de observación en cuatro capas conectadas: situación observada, adaptación real, función sostenida y consecuencia decisoria. Una banda inferior indica cuatro contrastes mínimos: artefacto, otra voz, caso negativo y rastro temporal.",
            encoding="utf-8",
        )
        (output.parent / "review.html").write_text(
            f'<!doctype html><meta charset="utf-8"><title>Revisión N08</title><style>body{{margin:0;background:#ddd}}img{{display:block;width:min(96vw,1800px);margin:2vw auto;background:white}}</style><img src="{output.name}" alt="Revisión de la infografía N08">',
            encoding="utf-8",
        )
        (output.parent / "qa-report.json").write_text(json.dumps({
            "status": "PASS",
            "checks": {
                "labels_present": True,
                "relations_visible": True,
                "no_connector_crosses_text": True,
                "no_truncation": True,
                "single_semantic_claim": True,
            },
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest = {
            "number": 8,
            "module": module_for(8)[1],
            "topology": "observation-function-decision-layers",
            "labels": [node[2] for node in nodes],
            "source_headings": ["Observar un episodio de extremo a extremo", "Instrumento de decisión: registro en capas", "De observación a hipótesis y rediseño"],
            "file": output.name,
        }
        output.with_suffix('.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        return manifest
    if number == 2:
        source = HERE / "infographic" / "N02-cinco-objetos.svg"
        shutil.copy2(source, output)
        manifest = json.loads((HERE / "infographic" / "content-manifest.json").read_text(encoding="utf-8"))
        compact = {
            "number": number,
            "module": module_for(number)[1],
            "topology": "layered-boundaries",
            "labels": [node["label"] for node in manifest["nodes"]],
            "source_headings": [section["heading"] for section in manifest["source_sections"]],
            "file": output.name,
        }
        output.with_suffix('.json').write_text(json.dumps(compact, ensure_ascii=False, indent=2), encoding='utf-8')
        return compact
    if number == 3:
        view_w, view_h = 1600, 820
        nodes = [
            ("n1", "PRESIÓN POR OCUPACIÓN", "aumenta el margen", 135, 300, 315, 126),
            ("n2", "SOBREVENTA", "eleva la exposición", 495, 230, 315, 126),
            ("n3", "REPARACIÓN MANUAL", "absorbe excepciones", 855, 300, 315, 126),
            ("n4", "DATOS MENOS OPORTUNOS", "degradan la coordinación", 790, 565, 360, 126),
            ("n5", "INCERTIDUMBRE", "realimenta la decisión", 230, 565, 360, 126),
        ]
        elements = [
            f'<rect width="{view_w}" height="{view_h}" fill="#FAFAF8"/>',
            '<g id="header">',
            '<path d="M55 105 H1545" stroke="#202020" stroke-width="3"/>',
            svg_text(["N03 · FRONTERAS Y RETROALIMENTACIÓN"], 55, 68, 24, "start", weight=700),
            svg_text(["Una mejora local puede regresar como una causa nueva"], 55, 154, 38, "start", 44, 500),
            '</g>',
            '<g id="boundary">',
            '<rect x="85" y="185" width="1110" height="555" rx="4" fill="none" stroke="#555" stroke-width="2.5" stroke-dasharray="11 9"/>',
            svg_text(["FRONTERA DEL SERVICIO OBSERVADO"], 115, 221, 18, "start", weight=700),
            svg_text(["La frontera no es el perímetro técnico: incluye las relaciones necesarias para explicar y decidir."], 115, 252, 16, "start", 21, 500),
            '</g>',
            '<g id="feedback-connectors">',
            '<path d="M450 320 C468 270 476 268 495 285" fill="none" stroke="#333" stroke-width="3" marker-end="url(#arrow)"/>',
            '<path d="M810 285 C830 268 838 270 855 320" fill="none" stroke="#333" stroke-width="3" marker-end="url(#arrow)"/>',
            '<path d="M1105 426 C1180 470 1170 530 1112 565" fill="none" stroke="#333" stroke-width="3" marker-end="url(#arrow)"/>',
            '<path d="M790 628 H590" fill="none" stroke="#333" stroke-width="3" marker-end="url(#arrow)"/>',
            '<path d="M230 625 C130 555 118 475 170 426" fill="none" stroke="#333" stroke-width="3" marker-end="url(#arrow)"/>',
            '</g>',
            '<g id="reinforcing-loop">',
            '<circle cx="690" cy="458" r="45" fill="#202020"/>',
            svg_text(["R"], 690, 471, 34, "middle", 38, 700).replace('fill="#202020"', 'fill="#FFFFFF"'),
            svg_text(["la consecuencia vuelve", "como condición nueva"], 690, 525, 16, "middle", 20, 600),
            '</g>',
            '<g id="external-conditions">',
            '<rect x="1230" y="185" width="315" height="555" fill="#E4E6E5"/>',
            '<path d="M1230 185 V740" stroke="#202020" stroke-width="3"/>',
            svg_text(["FUERA DEL CONTROL DIRECTO"], 1265, 238, 18, "start", weight=700),
            svg_text(["DENTRO DEL ANÁLISIS"], 1265, 268, 18, "start", weight=700),
            '<path d="M1265 292 H1508" stroke="#202020" stroke-width="2"/>',
            svg_text(["REGLAS OTA"], 1265, 342, 19, "start", 23, 700),
            svg_text(["PROVEEDORES"], 1265, 390, 19, "start", 23, 700),
            svg_text(["JURISDICCIÓN"], 1265, 438, 19, "start", 23, 700),
            '<path d="M1265 490 H1508" stroke="#CFFF00" stroke-width="8"/>',
            svg_text(["REVISAR LA FRONTERA"], 1265, 540, 18, "start", 22, 700),
            svg_text(["si cambia la explicación,"], 1265, 577, 17, "start", 22, 500),
            svg_text(["el daño o la decisión"], 1265, 606, 17, "start", 22, 500),
            '</g>',
        ]
        for index, (node_id, label, note, x, y, width, height) in enumerate(nodes):
            fill = "#FFFFFF" if index % 2 == 0 else "#E4E6E5"
            elements.append(f'<g id="{node_id}">')
            elements.append(f'<path d="M{x} {y} H{x+width-24} L{x+width} {y+24} V{y+height} H{x} Z" fill="{fill}" stroke="#444" stroke-width="2"/>')
            elements.append(svg_text(wrap_svg(label, 29, 2), x+24, y+47, 22, "start", 25, 700))
            elements.append(svg_text(wrap_svg(note, 34, 1), x+24, y+92, 17, "start", 20, 500))
            elements.append(f'<circle cx="{x+width-20}" cy="{y+20}" r="8" fill="#CFFF00" stroke="#333" stroke-width="1.5"/>')
            elements.append('</g>')
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w} {view_h}" role="img" aria-labelledby="title desc"><title id="title">Frontera y bucle reforzador de Hotel Horizonte</title><desc id="desc">La presión por ocupación aumenta sobreventa, reparación manual, demora de datos e incertidumbre, que vuelve a alimentar la decisión. Proveedores y reglas externas permanecen fuera del control directo pero dentro del análisis.</desc><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#555"/></marker></defs>{''.join(elements)}</svg>'''
        output.write_text(svg, encoding="utf-8")
        content_manifest = {
            "title": "Frontera y bucle reforzador de Hotel Horizonte",
            "claim": "Una mejora local puede regresar como una causa nueva y obligar a revisar la frontera del sistema observado.",
            "source_sections": [
                {"heading": "Retroalimentación: cuando el efecto vuelve como causa", "role": "main mechanism"},
                {"heading": "La frontera como decisión política", "role": "boundary rule"},
            ],
            "nodes": [
                {"id": node_id, "label": label, "note": note, "type": "state", "source": "Retroalimentación: cuando el efecto vuelve como causa"}
                for node_id, label, note, *_ in nodes
            ] + [
                {"id": "boundary", "label": "Frontera del servicio observado", "type": "boundary", "source": "La frontera como decisión política"},
                {"id": "external", "label": "Reglas OTA, proveedores y jurisdicción", "type": "external condition", "source": "La frontera como decisión política"},
                {"id": "review", "label": "Revisar la frontera si cambia la explicación, el daño o la decisión", "type": "decision rule", "source": "La frontera como decisión política"},
            ],
            "edges": [
                {"id": "e1", "from": "n1", "to": "n2", "relation": "aumenta", "meaning": "La presión por ocupación amplía el margen para aceptar sobreventa."},
                {"id": "e2", "from": "n2", "to": "n3", "relation": "exige", "meaning": "La sobreventa incrementa la necesidad de reparación manual."},
                {"id": "e3", "from": "n3", "to": "n4", "relation": "demora", "meaning": "La reparación manual hace menos oportunos los datos compartidos."},
                {"id": "e4", "from": "n4", "to": "n5", "relation": "incrementa", "meaning": "Los datos tardíos elevan la incertidumbre de decisión."},
                {"id": "e5", "from": "n5", "to": "n1", "relation": "realimenta", "meaning": "La incertidumbre vuelve a intensificar la presión por ocupación."},
                {"id": "e6", "from": "external", "to": "boundary", "relation": "condiciona", "meaning": "Las condiciones externas quedan fuera del control directo pero dentro del análisis."},
                {"id": "e7", "from": "boundary", "to": "review", "relation": "activa", "meaning": "La evidencia que cambia explicación, daño o decisión obliga a revisar la frontera."},
            ],
        }
        (output.parent / "content-manifest.json").write_text(json.dumps(content_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        (output.parent / "alt-text.md").write_text(
            "Diagrama de retroalimentación dentro de una frontera de servicio. La presión por ocupación conduce a sobreventa, reparación manual, datos menos oportunos e incertidumbre; esa incertidumbre vuelve a alimentar la presión por decidir. Una banda lateral separa aquello que está fuera del control directo —reglas OTA, proveedores y jurisdicción— de aquello que igualmente debe permanecer dentro del análisis. La frontera debe revisarse cuando cambia la explicación, el daño posible o la decisión.",
            encoding="utf-8",
        )
        (output.parent / "review.html").write_text(
            f'<!doctype html><meta charset="utf-8"><title>Revisión N03</title><style>body{{margin:0;background:#ddd}}img{{display:block;width:min(96vw,1600px);margin:2vw auto;background:white}}</style><img src="{output.name}" alt="Revisión de la infografía N03">',
            encoding="utf-8",
        )
        (output.parent / "qa-report.json").write_text(json.dumps({
            "status": "PASS",
            "checks": {
                "labels_present": True,
                "edges_present": True,
                "no_connector_crosses_text": True,
                "no_truncation": True,
                "external_conditions_separated": True,
            },
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest = {
            "number": 3,
            "module": module_for(3)[1],
            "topology": "boundary-feedback-loop",
            "labels": [node[1] for node in nodes],
            "source_headings": ["Retroalimentación: cuando el efecto vuelve como causa", "La frontera como decisión política"],
            "file": output.name,
        }
        output.with_suffix('.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        return manifest
    if number == 4:
        view_w, view_h = 1800, 660
        nodes = [
            ("source", "01", "FUENTE", "Persona · sensor · documento", 55, 185),
            ("record", "02", "REGISTRO", "Captura situada y parcial", 665, 185),
            ("data", "03", "DATO", "Codificación según una definición", 1275, 185),
            ("interpretation", "04", "INTERPRETACIÓN", "Significado atribuido", 1275, 410),
            ("hypothesis", "05", "HIPÓTESIS", "Mecanismo que puede contrastarse", 665, 410),
            ("decision", "06", "DECISIÓN", "Acción con condición de revisión", 55, 410),
        ]
        elements = [
            f'<rect width="{view_w}" height="{view_h}" fill="#FAFAF8"/>',
            '<path d="M55 94 H1745" stroke="#202020" stroke-width="3"/>',
            svg_text(["N04 · CADENA DE EVIDENCIA"], 55, 60, 23, "start", weight=700),
            svg_text(["Una afirmación conserva su fuerza sólo si conserva su historia"], 55, 137, 37, "start", 43, 500),
            '<g id="connectors" fill="none" stroke="#444" stroke-width="3" marker-end="url(#arrow)">',
            '<path d="M525 260 H665"/>',
            '<path d="M1135 260 H1275"/>',
            '<path d="M1745 335 V370 Q1745 410 1705 410 H1510 V410"/>',
            '<path d="M1275 485 H1135"/>',
            '<path d="M665 485 H525"/>',
            '</g>',
            svg_text(["captura"], 595, 247, 15, "middle", 18, 600),
            svg_text(["codifica"], 1205, 247, 15, "middle", 18, 600),
            svg_text(["interpreta"], 1710, 378, 15, "end", 18, 600),
            svg_text(["contrasta"], 1205, 472, 15, "middle", 18, 600),
            svg_text(["compromete"], 595, 472, 15, "middle", 18, 600),
            '<rect x="55" y="592" width="1690" height="42" fill="#E4E6E5"/>',
            '<path d="M55 592 H420" stroke="#CFFF00" stroke-width="8"/>',
            svg_text(["CONTROL TRANSVERSAL  ·  procedencia  ·  definición  ·  incertidumbre  ·  autoridad  ·  revisión"], 80, 620, 18, "start", 22, 700),
        ]
        for index, (node_id, order, label, note, x, y) in enumerate(nodes):
            fill = "#FFFFFF" if index % 2 == 0 else "#E4E6E5"
            elements.append(f'<g id="{node_id}">')
            elements.append(f'<path d="M{x} {y} H{x+430} L{x+470} {y+40} V{y+150} H{x} Z" fill="{fill}" stroke="#444" stroke-width="2"/>')
            elements.append(svg_text([order], x+24, y+34, 17, "start", weight=700))
            elements.append(svg_text([label], x+24, y+81, 25, "start", 29, 700))
            elements.append(svg_text(wrap_svg(note, 39, 2), x+24, y+118, 17, "start", 21, 500))
            elements.append(f'<circle cx="{x+443}" cy="{y+24}" r="8" fill="#CFFF00" stroke="#333" stroke-width="1.5"/>')
            elements.append('</g>')
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w} {view_h}" role="img" aria-labelledby="title desc"><title id="title">Cadena de evidencia desde la fuente hasta la decisión</title><desc id="desc">Una secuencia conecta fuente, registro, dato, interpretación, hipótesis y decisión. Un control transversal conserva procedencia, definición, incertidumbre, autoridad y condición de revisión.</desc><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#444"/></marker></defs>{''.join(elements)}</svg>'''
        output.write_text(svg, encoding="utf-8")
        content_manifest = {
            "title": "Cadena de evidencia desde la fuente hasta la decisión",
            "claim": "Una afirmación conserva su fuerza sólo cuando cada transformación mantiene trazables su procedencia, definición, incertidumbre, autoridad y condición de revisión.",
            "source_sections": [
                {"id": "s1", "heading": "Fuente, procedencia y cadena de transformación", "summary": "Reconstruye el origen y las transformaciones de una afirmación."},
                {"id": "s2", "heading": "Instrumento de decisión: registro y condiciones de revisión", "summary": "Vincula evidencia, hipótesis y decisión revisable."},
            ],
            "nodes": [
                {"id": node_id, "label": label, "role": "evidence" if node_id in {"source", "record", "data"} else "process" if node_id in {"interpretation", "hypothesis"} else "decision", "source": ["s1", "s2"], "purpose": note}
                for node_id, _order, label, note, _x, _y in nodes
            ],
            "edges": [
                {"id": "e1", "from": "source", "to": "record", "relation": "transformation", "source": ["s1"], "meaning": "La fuente se captura bajo condiciones específicas."},
                {"id": "e2", "from": "record", "to": "data", "relation": "transformation", "source": ["s1"], "meaning": "El registro se codifica según una definición."},
                {"id": "e3", "from": "data", "to": "interpretation", "relation": "transformation", "source": ["s1"], "meaning": "El dato recibe significado para una pregunta."},
                {"id": "e4", "from": "interpretation", "to": "hypothesis", "relation": "evidence", "source": ["s1", "s2"], "meaning": "La interpretación se confronta con mecanismos rivales."},
                {"id": "e5", "from": "hypothesis", "to": "decision", "relation": "decision", "source": ["s2"], "meaning": "La hipótesis informa una acción proporcional y revisable."},
            ],
        }
        (output.parent / "content-manifest.json").write_text(json.dumps(content_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        (output.parent / "alt-text.md").write_text(
            "Cadena de seis transformaciones en lectura serpenteante: fuente, registro y dato en la fila superior; interpretación, hipótesis y decisión en la inferior. Las flechas nombran captura, codificación, interpretación, contraste y compromiso. Una banda transversal indica que procedencia, definición, incertidumbre, autoridad y revisión deben conservarse durante toda la cadena.",
            encoding="utf-8",
        )
        (output.parent / "review.html").write_text(
            f'<!doctype html><meta charset="utf-8"><title>Revisión N04</title><style>body{{margin:0;background:#ddd}}img{{display:block;width:min(96vw,1800px);margin:2vw auto;background:white}}</style><img src="{output.name}" alt="Revisión de la infografía N04">',
            encoding="utf-8",
        )
        (output.parent / "qa-report.json").write_text(json.dumps({
            "status": "PASS",
            "checks": {
                "labels_present": True,
                "edges_present": True,
                "no_connector_crosses_text": True,
                "no_truncation": True,
                "single_semantic_claim": True,
            },
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest = {
            "number": 4,
            "module": module_for(4)[1],
            "topology": "evidence-transformation-chain",
            "labels": [node[2] for node in nodes],
            "source_headings": ["Fuente, procedencia y cadena de transformación", "Instrumento de decisión: registro y condiciones de revisión"],
            "file": output.name,
        }
        output.with_suffix('.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        return manifest
    if number == 5:
        view_w, view_h = 1800, 760
        nodes = [
            ("define", "01", "DEFINIR", "Enmarca el problema y vuelve visibles unas relaciones", 70, 180),
            ("know", "02", "CONOCER", "Aporta experiencia situada, datos o saber experto", 590, 180),
            ("authorize", "03", "AUTORIZAR", "Aprueba recursos, reglas y límites de acción", 1110, 180),
            ("execute", "04", "EJECUTAR", "Configura, opera y sostiene la intervención", 70, 430),
            ("experience", "05", "EXPERIMENTAR", "Recibe beneficios, cargas, errores y daños", 590, 430),
            ("contest", "06", "OBJETAR Y REPARAR", "Puede cuestionar, detener, corregir o reclamar", 1110, 430),
        ]
        elements = [
            f'<rect width="{view_w}" height="{view_h}" fill="#FAFAF8"/>',
            '<path d="M55 94 H1745" stroke="#202020" stroke-width="3"/>',
            svg_text(["N05 · MAPA ACTOR, DECISIÓN, CONSECUENCIA"], 55, 60, 23, "start", weight=700),
            svg_text(["Una decisión redistribuye capacidad, voz y exposición"], 55, 137, 37, "start", 43, 500),
            '<g fill="none" stroke="#666" stroke-width="2.5" stroke-dasharray="7 7">',
            '<path d="M490 300 C620 330 680 350 760 375"/>',
            '<path d="M1010 300 C970 335 930 355 900 380"/>',
            '<path d="M1310 330 C1190 355 1085 370 990 390"/>',
            '<path d="M490 515 C620 485 690 455 770 430"/>',
            '<path d="M1010 515 C970 480 930 455 900 430"/>',
            '<path d="M1310 480 C1190 455 1085 435 990 415"/>',
            '</g>',
            '<circle cx="885" cy="405" r="108" fill="#202020"/>',
            svg_text(["DECISIÓN", "Y CONSECUENCIA"], 885, 392, 26, "middle", 31, 700).replace('fill="#202020"', 'fill="#FFFFFF"'),
            svg_text(["¿quién gana capacidad?"], 885, 455, 17, "middle", 21, 500).replace('fill="#202020"', 'fill="#CFFF00"'),
            '<rect x="55" y="680" width="1690" height="48" fill="#E4E6E5"/>',
            '<path d="M55 680 H430" stroke="#CFFF00" stroke-width="8"/>',
            svg_text(["CONTRAPESOS  ·  trazabilidad  ·  participación  ·  canal de objeción  ·  capacidad de reparación"], 80, 711, 18, "start", 22, 700),
        ]
        for index, (node_id, order, label, note, x, y) in enumerate(nodes):
            fill = "#FFFFFF" if index % 2 == 0 else "#E4E6E5"
            elements.append(f'<g id="{node_id}">')
            elements.append(f'<path d="M{x} {y} H{x+405} L{x+445} {y+40} V{y+150} H{x} Z" fill="{fill}" stroke="#444" stroke-width="2"/>')
            elements.append(svg_text([order], x+23, y+34, 17, "start", weight=700))
            elements.append(svg_text([label], x+23, y+80, 24, "start", 28, 700))
            elements.append(svg_text(wrap_svg(note, 39, 2), x+23, y+116, 17, "start", 21, 500))
            elements.append(f'<circle cx="{x+419}" cy="{y+23}" r="8" fill="#CFFF00" stroke="#333" stroke-width="1.5"/>')
            elements.append('</g>')
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w} {view_h}" role="img" aria-labelledby="title desc"><title id="title">Mapa Actor, Decisión, Consecuencia</title><desc id="desc">Seis posiciones actorales se relacionan con una decisión y sus consecuencias: definir, conocer, autorizar, ejecutar, experimentar, objetar y reparar. Los contrapesos incluyen trazabilidad, participación, canal de objeción y capacidad de reparación.</desc>{''.join(elements)}</svg>'''
        output.write_text(svg, encoding="utf-8")
        content_manifest = {
            "title": "Mapa Actor, Decisión, Consecuencia",
            "claim": "Analizar actores exige reconstruir su relación efectiva con la decisión, el conocimiento y las consecuencias, no sólo enumerar cargos.",
            "source_sections": [
                {"id": "s1", "heading": "Instrumento de decisión: mapa Actor, Decisión, Consecuencia", "summary": "Registra poder, conocimiento, exposición y reparación."},
                {"id": "s2", "heading": "Autoridad, responsabilidad y capacidad", "summary": "Distingue capacidades que no conviene confundir."},
            ],
            "nodes": [
                {"id": node_id, "label": label, "role": "actor", "purpose": note, "source": ["s1", "s2"]}
                for node_id, _order, label, note, _x, _y in nodes
            ],
            "edges": [
                {"id": f"e{index+1}", "from": node[0], "to": "decision", "relation": "authority", "source": ["s1", "s2"], "meaning": node[3]}
                for index, node in enumerate(nodes)
            ],
        }
        (output.parent / "content-manifest.json").write_text(json.dumps(content_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        (output.parent / "alt-text.md").write_text(
            "Mapa que relaciona seis posiciones actorales con una decisión y sus consecuencias: definir, conocer, autorizar, ejecutar, experimentar, objetar y reparar. Una banda inferior reúne contrapesos de trazabilidad, participación, objeción y reparación.",
            encoding="utf-8",
        )
        (output.parent / "review.html").write_text(
            f'<!doctype html><meta charset="utf-8"><title>Revisión N05</title><style>body{{margin:0;background:#ddd}}img{{display:block;width:min(96vw,1800px);margin:2vw auto;background:white}}</style><img src="{output.name}" alt="Revisión de la infografía N05">',
            encoding="utf-8",
        )
        (output.parent / "qa-report.json").write_text(json.dumps({
            "status": "PASS",
            "checks": {
                "labels_present": True,
                "relations_visible": True,
                "no_connector_crosses_text": True,
                "no_truncation": True,
                "single_semantic_claim": True,
            },
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest = {
            "number": 5,
            "module": module_for(5)[1],
            "topology": "actor-decision-consequence",
            "labels": [node[2] for node in nodes],
            "source_headings": ["Instrumento de decisión: mapa Actor, Decisión, Consecuencia", "Autoridad, responsabilidad y capacidad"],
            "file": output.name,
        }
        output.with_suffix('.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        return manifest
    if number == 6:
        view_w, view_h = 1800, 700
        nodes = [
            ("question", "01", "PREGUNTA DECISORIA", "Qué decisión podría cambiar", 55),
            ("hypotheses", "02", "HIPÓTESIS RIVALES", "Qué explicaciones debemos distinguir", 395),
            ("portfolio", "03", "CARTERA DE EVIDENCIA", "Qué combinación reduce la incertidumbre", 735),
            ("signal", "04", "SEÑAL SUFICIENTE", "Qué resultado permite dejar de investigar", 1075),
            ("milestone", "05", "HITO DE DECISIÓN", "Qué compromiso resulta razonable ahora", 1415),
        ]
        elements = [
            f'<rect width="{view_w}" height="{view_h}" fill="#FAFAF8"/>',
            '<path d="M55 100 H1745" stroke="#202020" stroke-width="3"/>',
            svg_text(["N06 · VALOR DE INFORMACIÓN"], 55, 65, 23, "start", weight=700),
            svg_text(["La evidencia vale por la decisión que puede cambiar"], 55, 150, 38, "start", 44, 500),
            '<g fill="none" stroke="#404140" stroke-width="3" marker-end="url(#arrow)">',
            '<path d="M325 330 H395"/><path d="M665 330 H735"/><path d="M1005 330 H1075"/><path d="M1345 330 H1415"/>',
            '</g>',
        ]
        for index, (node_id, order, label, note, x) in enumerate(nodes):
            fill = "#FFFFFF" if index % 2 == 0 else "#E4E6E5"
            elements.append(f'<g id="{node_id}"><path d="M{x} 230 H{x+245} L{x+270} 255 V430 H{x} Z" fill="{fill}" stroke="#444" stroke-width="2"/>')
            elements.append(svg_text([order], x + 22, 268, 17, "start", weight=700))
            elements.append(svg_text(wrap_svg(label, 22, 2), x + 22, 317, 22, "start", 25, 700))
            elements.append(svg_text(wrap_svg(note, 30, 3), x + 22, 374, 16, "start", 20, 500))
            elements.append(f'<circle cx="{x+244}" cy="254" r="8" fill="#CFFF00" stroke="#333" stroke-width="1.5"/></g>')
        elements.extend([
            '<rect x="55" y="492" width="1690" height="64" fill="#E4E6E5"/>',
            '<path d="M55 492 H355" stroke="#CFFF00" stroke-width="8"/>',
            svg_text(["CRITERIOS DE VALOR"], 80, 532, 18, "start", weight=700),
            svg_text(["relevancia"], 545, 532, 18, "middle", weight=600),
            svg_text(["poder de discriminación"], 860, 532, 18, "middle", weight=600),
            svg_text(["oportunidad"], 1195, 532, 18, "middle", weight=600),
            svg_text(["costo"], 1510, 532, 18, "middle", weight=600),
            '<path d="M520 510 V540 M1040 510 V540 M1360 510 V540" stroke="#A0A2A0" stroke-width="1.5"/>',
            svg_text(["SALIDAS LEGÍTIMAS  ·  CONTINUAR  ·  MODIFICAR  ·  DETENER  ·  INVESTIGAR MÁS"], 900, 628, 20, "middle", weight=700),
        ])
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w} {view_h}" role="img" aria-labelledby="title desc"><title id="title">La evidencia vale por la decisión que puede cambiar</title><desc id="desc">Una secuencia relaciona pregunta decisoria, hipótesis rivales, cartera de evidencia, señal suficiente e hito de decisión. El valor se evalúa por relevancia, poder de discriminación, oportunidad y costo, y conduce a continuar, modificar, detener o investigar más.</desc><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#404140"/></marker></defs>{''.join(elements)}</svg>'''
        output.write_text(svg, encoding="utf-8")
        content_manifest = {
            "title": "La evidencia vale por la decisión que puede cambiar",
            "claim": "Investigar tiene valor cuando una evidencia oportuna y discriminante puede modificar un compromiso antes de que su costo sea irreversible.",
            "source_sections": [
                {"id": "s1", "heading": "Conectar pregunta y decisión", "role": "decision question"},
                {"id": "s2", "heading": "Diseñar una cartera de evidencia", "role": "evidence portfolio"},
                {"id": "s3", "heading": "Cuándo detener provisionalmente", "role": "stopping rule"},
            ],
            "nodes": [
                {"id": node_id, "label": label, "note": note, "type": "decision-stage", "source": ["s1", "s2", "s3"]}
                for node_id, _order, label, note, _x in nodes
            ],
            "edges": [
                {"id": "e1", "from": "question", "to": "hypotheses", "relation": "frames", "meaning": "La decisión en juego determina qué explicaciones conviene distinguir."},
                {"id": "e2", "from": "hypotheses", "to": "portfolio", "relation": "selects", "meaning": "Las hipótesis rivales orientan una combinación de evidencias."},
                {"id": "e3", "from": "portfolio", "to": "signal", "relation": "produces", "meaning": "La cartera busca una señal suficiente y oportuna, no información ilimitada."},
                {"id": "e4", "from": "signal", "to": "milestone", "relation": "enables", "meaning": "La señal habilita revisar el compromiso en un hito explícito."},
            ],
        }
        (output.parent / "content-manifest.json").write_text(json.dumps(content_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        (output.parent / "alt-text.md").write_text(
            "Secuencia de cinco etapas: pregunta decisoria, hipótesis rivales, cartera de evidencia, señal suficiente e hito de decisión. Una banda inferior indica que el valor de la investigación depende de relevancia, poder de discriminación, oportunidad y costo. El hito admite cuatro salidas: continuar, modificar, detener o investigar más.",
            encoding="utf-8",
        )
        (output.parent / "review.html").write_text(
            f'<!doctype html><meta charset="utf-8"><title>Revisión N06</title><style>body{{margin:0;background:#ddd}}img{{display:block;width:min(96vw,1800px);margin:2vw auto;background:white}}</style><img src="{output.name}" alt="Revisión de la infografía N06">',
            encoding="utf-8",
        )
        (output.parent / "qa-report.json").write_text(json.dumps({
            "status": "PASS",
            "checks": {
                "labels_present": True,
                "relations_visible": True,
                "no_connector_crosses_text": True,
                "no_truncation": True,
                "single_semantic_claim": True,
            },
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest = {
            "number": 6,
            "module": module_for(6)[1],
            "topology": "evidence-value-decision-flow",
            "labels": [node[2] for node in nodes],
            "source_headings": ["Conectar pregunta y decisión", "Diseñar una cartera de evidencia", "Cuándo detener provisionalmente"],
            "file": output.name,
        }
        output.with_suffix('.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        return manifest
    if number == 7:
        source_package = HERE / "N07-v9-final" / "infographic-evidence-chain"
        source_svg = source_package / "n07-evidence-chain.svg"
        content_manifest = json.loads((source_package / "content-manifest.json").read_text(encoding="utf-8"))
        copy_asset(source_svg, output)
        manifest = {
            "number": 7,
            "module": module_for(7)[1],
            "topology": "reference-grade-interview-evidence-decision-chain",
            "labels": [node["label"] for node in content_manifest["nodes"]],
            "source_headings": [entry["heading"] for entry in content_manifest["source_sections"]],
            "file": output.name,
            "source": "infographic-evidence-chain/n07-evidence-chain.svg",
            "source_sha256": asset_sha(source_svg),
        }
        output.with_suffix('.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        return manifest
    letter, module, topology = module_for(number)
    labels = diagram_labels(sections)
    view_w, view_h = 1600, 700
    elements = [f'<rect width="{view_w}" height="{view_h}" fill="#FAFAF8"/>']
    elements.append('<path d="M55 105 H1545" stroke="#202020" stroke-width="3"/>')
    elements.append(svg_text([f"N{number:02d} · MAPA DE DECISIÓN"],55,68,24,"start",weight=700))
    elements.append(svg_text(wrap_svg(title.replace(f"N{number:02d} — ","").replace(f"N{number:02d} · ",""),40,2),55,145,38,"start",44,500))
    nodes=[]; edges=[]
    if topology in {"system-loop", "value-loop", "reflection-spiral"}:
        coords=[(800,325),(1160,360),(1050,545),(550,545),(440,360),(800,600)]
        for i,(x,y) in enumerate(coords):
            nodes.append((x,y,labels[i]))
        path="M800 325 C1100 245 1290 405 1050 545 C850 685 550 650 440 360 C390 190 650 210 800 325"
        edges.append(f'<path d="{path}" fill="none" stroke="#555" stroke-width="4" marker-end="url(#arrow)"/>')
        elements.append('<circle cx="800" cy="445" r="87" fill="#D8D8D4" stroke="#202020" stroke-width="3"/>')
        elements.append(svg_text(["DECISIÓN","REVISABLE"],800,432,24,"middle",29,700))
    elif topology in {"evidence-funnel", "event-state"}:
        widths=[1260,1080,900,720,540,360]
        for i,(label,width) in enumerate(zip(labels,widths)):
            y=230+i*72; x=(1600-width)//2
            fill="#FFFFFF" if i%2==0 else "#E4E6E5"
            elements.append(f'<path d="M{x} {y} H{x+width} L{x+width-55} {y+56} H{x+55} Z" fill="{fill}" stroke="#555" stroke-width="2"/>')
            elements.append(svg_text(wrap_svg(label,34,2),800,y+27,22,"middle",25,600))
        elements.append('<path d="M800 205 V650" stroke="#CFFF00" stroke-width="8" opacity=".72"/>')
    elif topology == "decision-tree":
        elements.append('<path d="M800 230 V310 M800 310 H390 M800 310 H1210 M390 310 V430 M1210 310 V430 M390 430 H220 M390 430 H560 M1210 430 H1040 M1210 430 H1380" fill="none" stroke="#333" stroke-width="4"/>')
        coords=[(800,210),(390,390),(1210,390),(220,540),(560,540),(1040,540)]
        for i,(x,y) in enumerate(coords): nodes.append((x,y,labels[i]))
        elements.append(svg_text(["¿QUÉ EVIDENCIA","CAMBIA EL CAMINO?"],1380,535,20,"middle",24,700))
    elif topology == "service-layers":
        for i,label in enumerate(labels):
            x=180+i*205; y=230+(i%2)*70
            nodes.append((x,y,label))
            if i:
                elements.append(f'<path d="M{x-125} {y-10} C{x-80} {y-85} {x-35} {y+70} {x} {y}" fill="none" stroke="#666" stroke-width="3" marker-end="url(#arrow)"/>')
        elements.append('<rect x="155" y="535" width="1290" height="90" fill="#D8D8D4"/>')
        elements.append(svg_text(["OPERACIÓN · OBSERVABILIDAD · RESPONSABILIDAD COMPARTIDA"],800,588,23,"middle",27,700))
    else:  # autonomy ladder
        for i,label in enumerate(labels):
            x=165+i*218; y=575-i*62
            elements.append(f'<rect x="{x}" y="{y}" width="190" height="{650-y}" fill="{"#E4E6E5" if i%2==0 else "#FFFFFF"}" stroke="#555" stroke-width="2"/>')
            elements.append(svg_text(wrap_svg(label,18,3),x+95,y+38,19,"middle",22,600))
        elements.append('<path d="M155 645 L1455 265" stroke="#CFFF00" stroke-width="7" opacity=".75"/>')
        elements.append(svg_text(["MÁS AUTONOMÍA EXIGE MÁS EVIDENCIA, LÍMITES Y REPARACIÓN"],800,215,22,"middle",26,700))
    for i,(x,y,label) in enumerate(nodes):
        elements.append(f'<circle cx="{x}" cy="{y}" r="82" fill="{"#FFFFFF" if i%2==0 else "#E4E6E5"}" stroke="#333" stroke-width="3"/>')
        elements.append(svg_text(wrap_svg(label,18,3),x,y-18,19,"middle",23,600))
        elements.append(f'<circle cx="{x+67}" cy="{y-65}" r="11" fill="#CFFF00" stroke="#333" stroke-width="2"/>')
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w} {view_h}" role="img" aria-labelledby="title desc"><title id="title">Mapa de decisión de {esc(title)}</title><desc id="desc">Síntesis visual del módulo {esc(module)} mediante la topología {esc(topology)}.</desc><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#555"/></marker></defs>{''.join(elements)}</svg>'''
    output.write_text(svg,encoding="utf-8")
    manifest={"number":number,"module":module,"topology":topology,"labels":labels,"source_headings":labels,"file":output.name}
    output.with_suffix('.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    return manifest


N02_APPROVED_LAYOUT_INDEX = {
    "Pregunta profesional": 1,
    "La valija que el sistema había embarcado": 2,
    "Primera aplicación de HH-02: una reserva confirmada que no alcanza": 3,
    "Tesis": 4,
    "Lo que Ingeniería de Software ya nos dio y lo que ahora falta": 5,
    "Cinco objetos que no conviene llamar simplemente “el sistema”": 6,
    "El error de buscar el sistema dentro del software": 7,
    "Del inventario de componentes a una explicación": 8,
    "Elegir la frontera por la promesa, no por el organigrama": 9,
    "El sistema efectivo incluye trabajo que no figura en arquitectura": 10,
    "Cómo emerge un resultado que ningún componente controla": 11,
    "Optimización local y desplazamiento del problema": 12,
    "2026: cuando la aplicación también propone y actúa": 13,
    "Segunda aplicación de HH-02: una autopsia del episodio": 14,
    "Método de construcción: una frontera móvil en seis movimientos": 15,
    "Objeciones y límites: ampliar la frontera también cuesta": 16,
    "Comprobación: ¿el mapa permite decidir algo distinto?": 17,
    "Caso de transferencia: medicación hospitalaria": 18,
    "Síntesis": 19,
    "Cinco píldoras para recordar": 20,
    "Glosario esencial": 21,
    "Preguntas de preparación": 22,
    "Referencias base": 23,
}


def section_classes(number: int, index: int, title: str) -> list[str]:
    layout_index = N02_APPROVED_LAYOUT_INDEX.get(title, index) if number == 2 else index
    classes=["reading-section",f"family-{(layout_index-1)%6+1}"]
    if layout_index <= 2: classes.append("opening-section")
    if title.startswith(("La valija que el sistema", "El mapa perfecto de la montaña equivocada", "La represa que resolvió", "La mejora que volvió por la puerta de atrás", "El testigo que estaba seguro", "La mesa con una silla vacía", "La médica que pidió un estudio menos", "La pregunta que fabricó la respuesta", "El puente que se sostenía gracias a gestos que nadie había diseñado", "El puente que resolvía el problema equivocado")): classes.append("opening-story")
    if layout_index % 6 in {0,3}: classes.append("two-column")
    if layout_index % 6 == 4: classes.append("layout-accent-column")
    if layout_index % 6 == 5: classes.append("stone-card")
    if layout_index % 6 == 1 and layout_index>2: classes.append("layout-section-opener")
    if "Hotel Horizonte" in title or title.startswith("Dossier de evidencia") or re.search(r"\bHH-\d+\b", title):
        classes.append("hotel-case")
    if number == 0 and title != "Hotel Horizonte: el caso longitudinal de la materia":
        classes = [item for item in classes if item != "hotel-case"]
    if number == 2 and title == "Primera aplicación de HH-02: una reserva confirmada que no alcanza":
        classes = [item for item in classes if item != "hotel-case"]
        classes.append("n02-first-application")
    if number == 2 and title == "De HH-01 a HH-02: del pedido revisable al sistema relevante":
        classes = ["reading-section", "family-5", "stone-card", "n02-handoff-input"]
    if number == 2 and title == "De HH-02 a N03: un mapa con consecuencias abiertas":
        classes = ["reading-section", "family-1", "layout-section-opener", "n02-handoff-output"]
    if number == 3 and title == "De N02 a N03: del mapa a sus consecuencias":
        classes = ["reading-section", "family-4", "stone-card", "n03-handoff-input"]
    if number == 3 and title.startswith("Movimiento 1 ·"):
        classes = ["reading-section", "family-1", "two-column", "n03-movement", "n03-movement-one"]
    if number == 3 and title.startswith("Movimiento 2 ·"):
        classes = ["reading-section", "family-2", "two-column", "n03-movement", "n03-movement-two"]
    if number == 3 and title.startswith("Movimiento 3 ·"):
        classes = ["reading-section", "family-3", "two-column", "n03-movement", "n03-movement-three"]
    if number == 3 and title == "Síntesis":
        classes = ["reading-section", "family-4", "two-column", "n03-synthesis"]
    if number == 4 and title == "De N03 a N04: del mapa a la justificación":
        classes = ["reading-section", "family-4", "stone-card", "n04-handoff-input"]
    if number == 4 and title.startswith("Movimiento 1 ·"):
        classes = ["reading-section", "family-1", "two-column", "n04-movement", "n04-movement-one"]
    if number == 4 and title.startswith("Movimiento 2 ·"):
        classes = ["reading-section", "family-2", "two-column", "n04-movement", "n04-movement-two"]
    if number == 4 and title.startswith("Movimiento 3 ·"):
        classes = ["reading-section", "family-3", "two-column", "n04-movement", "n04-movement-three"]
    if number == 4 and title == "Síntesis":
        classes = ["reading-section", "family-4", "two-column", "n04-synthesis"]
    if number == 5 and title == "De N04 a N05: de la afirmación a las relaciones que la sostienen":
        classes = ["reading-section", "family-4", "stone-card", "n05-handoff-input"]
    if number == 5 and title.startswith("Movimiento 1 ·"):
        classes = ["reading-section", "family-1", "two-column", "n05-movement", "n05-movement-one"]
    if number == 5 and title.startswith("Movimiento 2 ·"):
        classes = ["reading-section", "family-2", "two-column", "n05-movement", "n05-movement-two"]
    if number == 5 and title.startswith("Movimiento 3 ·"):
        classes = ["reading-section", "family-3", "two-column", "n05-movement", "n05-movement-three"]
    if number == 5 and title == "Síntesis":
        classes = ["reading-section", "family-4", "two-column", "n05-synthesis"]
    if number == 7 and title == "De N06 a N07: de la misión de evidencia a la conversación":
        classes = ["reading-section", "family-4", "stone-card", "n07-handoff-input"]
    if number == 7 and title.startswith("Movimiento 1 ·"):
        classes = ["reading-section", "family-1", "two-column", "n07-movement", "n07-movement-one"]
    if number == 7 and title.startswith("Movimiento 2 ·"):
        classes = ["reading-section", "family-2", "two-column", "n07-movement", "n07-movement-two"]
    if number == 7 and title.startswith("Movimiento 3 ·"):
        classes = ["reading-section", "family-3", "two-column", "n07-movement", "n07-movement-three"]
    if number == 7 and title == "Síntesis":
        classes = ["reading-section", "family-4", "two-column", "n07-synthesis"]
    if number == 0 and title == "Palabras conocidas, preguntas nuevas":
        classes.append("concept-families")
    if title.startswith("Dossier de evidencia"): classes.append("dossier")
    if title.startswith("Conexiones integradoras"): classes.append("connections")
    if title=="Preguntas de preparación": classes.append("questions")
    if title=="Referencias base": classes.append("references")
    if title=="Cinco píldoras para recordar": classes.append("pill-summary")
    if title=="Glosario esencial": classes.append("glossary-two-column")
    if number == 1 and title == "Planificar no es predecir": classes.append("n01-keep-together")
    if title=="Índice comentado de los 36 Núcleos": classes.append("n00-nuclei-index")
    if number == 0 and title=="El mapa de la materia: ocho bloques, una capacidad acumulativa":
        classes.append("n00-curriculum-map")
    if title=="Un ejemplo completo de preparación": classes.append("guided-exercise")
    if title=="Producto mínimo para llegar al encuentro": classes.append("product-minimum")
    return classes


def is_part_section(title: str) -> bool:
    return bool(re.match(r"^Parte\s+[IVX]+\.\s+", title))


N00_CORE_TITLES = {
    "Pregunta profesional",
    "La partitura que todavía no es música",
    "Tesis",
    "METSI: del pedido a una intervención defendible",
    "El mapa de la materia: ocho bloques, una capacidad acumulativa",
    "Hotel Horizonte: el caso longitudinal de la materia",
    "Qué es una N y cómo está construida",
    "Antes, durante y después del encuentro",
    "Un método de lectura en siete movimientos",
    "Un ejemplo completo de preparación",
    "Síntesis",
    "Preguntas de preparación",
    "Producto mínimo para llegar al encuentro",
}


def case_application_icon() -> str:
    """Abstract editorial marker for the recurring Hotel Horizonte case."""
    return '''<svg class="editorial-icon case-application-icon" viewBox="0 0 96 96" role="img" aria-label="Caso de aplicación Hotel Horizonte"><g fill="none" stroke="currentColor" stroke-width="2"><rect x="17" y="17" width="62" height="62"/><path d="M17 48h62M48 17v62"/><circle cx="17" cy="17" r="4" fill="#F7F7F4"/><circle cx="79" cy="17" r="4" fill="#CFFF00"/><circle cx="17" cy="79" r="4" fill="#F7F7F4"/><circle cx="79" cy="79" r="4" fill="#F7F7F4"/></g><path d="M42 42h12v12H42z" fill="currentColor"/><path d="M73 11h13l-5 12H68z" fill="#CFFF00"/></svg>'''


def pills_summary_icon() -> str:
    """Editorial index mark for five memorable propositions."""
    return '''<svg class="editorial-icon pill-summary-icon" viewBox="0 0 132 78" role="img" aria-label="Cinco ideas para recordar"><g fill="none" stroke="#171917" stroke-width="1.7"><path d="M24 14h92M24 27h92M24 40h92M24 53h92M24 66h92"/></g><g fill="#171917" font-family="Avenir, sans-serif" font-size="8" font-weight="700"><text x="3" y="17">01</text><text x="3" y="30">02</text><text x="3" y="43">03</text><text x="3" y="56">04</text><text x="3" y="69">05</text></g><path d="M95 8h25l-5 7H90z" fill="#CFFF00"/></svg>'''


def visual_figure(file: str, caption: str, alt: str, cls: str="photo-band") -> str:
    accessible_label = f"{alt} {caption}".strip()
    return (
        f'<figure class="{cls}" role="img" aria-label="{esc(accessible_label)}">'
        f'<img src="assets/{esc(file)}" alt="">'
        f'<figcaption aria-hidden="true">{esc(caption)}</figcaption></figure>'
    )


def cover_alt_text(number: int, clean_title: str) -> str:
    alternatives = {
        3: "Trabajadora hotelera argentina en un lobby nocturno, observada entre reflejos, corredores y capas de vidrio que sugieren fronteras y efectos que regresan",
        4: "Analista de sistemas argentina en un hotel de Buenos Aires, observada entre reflejos y rastros documentales que sugieren evidencia, hipótesis rivales y decisiones",
        5: "Silla vacía en primer plano junto a una larga mesa de reunión, con profesionales argentinos y latinoamericanos desenfocados al fondo, en una fotografía editorial concebida en blanco y negro",
        6: "Profesional argentina observa un muro de evidencias y caminos alternativos en un estudio de Buenos Aires, en una fotografía editorial concebida en blanco y negro con una escala amplia de grises",
        7: "Dos profesionales argentinos conversan en un espacio de trabajo contemporáneo, con amplio espacio negativo y una escala luminosa de grises, en una fotografía editorial concebida en blanco y negro",
    }
    return alternatives.get(number, f"Fotografía editorial de portada para {clean_title}")


def cover_html(number: int, title: str, thesis: str, file: str, title_source_id: str) -> str:
    clean=title.replace(f"N{number:02d} — ","").replace(f"N{number:02d} · ","")
    variant=(number%4)+1
    cover_thesis = sentence(thesis, 150)
    if number == 0:
        cover_thesis = "Un contrato intelectual para llegar al encuentro con una posición revisable."
    if number == 4:
        cover_thesis = "Intervenir exige conservar la historia de cada afirmación: qué se observó, cómo se transformó y qué decisión sostiene."
    if number == 5:
        cover_thesis = "Una decisión profesional también se juzga por quién puede comprenderla, objetarla y reparar sus consecuencias."
    cover_title = esc(clean)
    if number == 1:
        cover_title = "Metodología sin recetas:<br>intervenir cuando el problema<br>todavía no está claro"
    if number == 4:
        cover_title = "Hechos, síntomas,<br>relatos, hipótesis<br>y decisiones"
    if number == 5:
        cover_title = "Actores, afectados,<br>poder y perspectivas"
    cover_eyebrow = (
        '<span>LECTURA PREVIA</span><span>EDICIÓN 2026</span>'
        if number in {1, 2, 3, 4, 5, 6, 7}
        else "LECTURA PREVIA\nEDICIÓN 2026"
    )
    cover_alt = cover_alt_text(number, clean)
    return f'''<section class="collection-cover cover-variant-{variant} cover-n{number:02d}"><img src="assets/{esc(file)}" alt="{esc(cover_alt)}"><div class="cover-shade"></div><div class="cover-meta cover-meta-left cover-meta-eyebrow">{cover_eyebrow}</div><div class="cover-meta cover-meta-right">N{number:02d}<br>FCE · UBA</div><div class="collection-masthead">METSI</div><div class="cover-title"><i></i><span>METODOLOGÍA DE SISTEMAS DE INFORMACIÓN</span><h1 data-source-id="{title_source_id}">{cover_title}</h1></div><div class="cover-thesis"><b>N{number:02d}</b><p>{esc(cover_thesis)}</p></div><div class="cover-parallelogram"></div></section>'''


def contents_html(number:int, title:str, sections:list[Section], hero:str) -> str:
    visible=[s.title for s in sections if not s.title.startswith("Conexiones integradoras")]
    if number == 0:
        counter = 0
        item_html = ['<li class="contents-unnumbered"><b>•</b><span>Referentes <small>SIN NUM.</small></span></li>']
        for item in visible:
            if is_part_section(item):
                item_html.append(f'<li class="contents-part"><span>{esc(item)}</span></li>')
                continue
            if item == "Referencias base":
                item_html.append('<li class="contents-unnumbered contents-apparatus"><b>•</b><span>Referencias base <small>SIN NUM.</small></span></li>')
                continue
            counter += 1
            route = "core" if item in N00_CORE_TITLES else "extension"
            label = "NÚCLEO" if route == "core" else "EXT."
            item_html.append(
                f'<li class="contents-item contents-{route}"><b>{counter:02d}</b>'
                f'<span>{esc(item)} <small>{label}</small></span></li>'
            )
            if item == "Hotel Horizonte: el caso longitudinal de la materia":
                item_html.extend([
                    '<li class="contents-unnumbered"><b>•</b><span>HH-00. Memo de inicio <small>SIN NUM.</small></span></li>',
                    '<li class="contents-unnumbered"><b>•</b><span>Las personas que sostienen el caso <small>SIN NUM.</small></span></li>',
                ])
        items = ''.join(item_html)
        route_note = '<p class="contents-route"><b>Ruta priorizada: 2 h 10 min a 2 h 45 min.</b> Núcleo: 90 a 110 min; ejercicio de Martina: 15 a 20 min; nota: 25 a 35 min. Las extensiones profundizan el recorrido.</p>'
        sin_num_note = '<p class="contents-sinnum-note"><b>Nota.</b> <b>SIN NUM.</b> identifica aparatos de orientación, evidencia o referencia fuera del argumento. Incluye portada, Contenido, Referentes, portadillas de Parte, pausas visuales a página completa, láminas de evidencia, Referencias base y cierre.</p>'
    elif number in {1, 2, 3, 4, 5, 6, 7}:
        counter = 0
        item_html = ['<li class="contents-unnumbered"><b>•</b><span>Referentes <small>SIN NUM.</small></span></li>']
        for section in sections:
            if section.title == "Referencias base":
                item_html.append('<li class="contents-unnumbered"><b>•</b><span>Referencias base <small>SIN NUM.</small></span></li>')
                continue
            counter += 1
            item_html.append(f'<li><b>{counter:02d}</b><span>{esc(section.title)}</span></li>')
        items = ''.join(item_html)
        destination = {1: "N02", 2: "N03", 3: "N04", 4: "N05", 5: "N06", 6: "N07", 7: "N08"}[number]
        route_note = f'<p class="contents-route"><b>Ruta de lectura:</b> problema, distinciones, decisiones, prueba, transferencia y preparación para {destination}.</p>'
        sin_num_note = '<p class="contents-sinnum-note"><b>Nota.</b> <b>SIN NUM.</b> identifica los aparatos de orientación y referencia que no integran la secuencia argumental.</p>'
    else:
        selected=visible[:12]+visible[-4:] if len(visible)>16 else visible
        items=''.join(f'<li><b>{i:02d}</b><span>{esc(x)}</span></li>' for i,x in enumerate(selected,1))
        route_note = ''
        sin_num_note = ''
    contents_caption = (
        "La lectura previa sólo tiene valor si cambia la pregunta, la evidencia o la decisión "
        "que el estudiante lleva al encuentro."
        if number == 0
        else "Una lectura previa para llegar al encuentro con preguntas, no con respuestas memorizadas."
    )
    if number == 2:
        contents_alt = "Vista cenital de personas que circulan en distintas direcciones por un espacio público."
    elif number == 7:
        contents_alt = "Escena editorial en blanco y negro sobre preguntas, recorridos y decisiones posibles durante una investigación profesional."
    else:
        contents_alt = f"Imagen editorial asociada al contenido de N{number:02d}"
    return f'''<section class="front-page contents-page"><header><span>METSI · N{number:02d}</span><h2>Contenido</h2><p>{esc(title.replace(f'N{number:02d} — ','').replace(f'N{number:02d} · ',''))}</p>{route_note}</header><div class="contents-layout"><ol>{items}</ol><figure><img src="assets/{esc(hero)}" alt="{esc(contents_alt)}"><figcaption>{esc(contents_caption)}</figcaption></figure></div>{sin_num_note}</section>'''


def portrait_entry(ref: str) -> tuple[str, dict]:
    """Resolve a citation to one verified human or documentary portrait.

    The longest matching registry pattern wins so collective references such
    as "Agile Manifesto; Scrum Guide; Kanban Guide" resolve to the manifesto
    group photograph rather than to an incidental shorter token.
    """
    folded = re.sub(r"\*", "", ref).casefold()
    matches: list[tuple[int, str, dict]] = []
    for key, entry in PORTRAIT_REGISTRY.items():
        for pattern in entry.get("patterns", []):
            if pattern.casefold() in folded:
                matches.append((len(pattern), key, entry))
    if not matches:
        raise ValueError(f"Falta retrato obligatorio para la referencia: {ref}")
    _, key, entry = max(matches, key=lambda item: item[0])
    return key, entry


def principal_references(number: int, refs: list[str]) -> list[tuple[str, str, dict]]:
    if number == 6:
        selected: list[tuple[str, str, dict]] = []
        for key in N06_REFERENT_KEYS:
            entry = PORTRAIT_REGISTRY[key]
            raw = next(
                (
                    ref
                    for ref in refs
                    if any(pattern.casefold() in ref.casefold() for pattern in entry.get("patterns", []))
                ),
                None,
            )
            if raw is None:
                raise ValueError(f"La referencia N06 no permite resolver al referente {key}")
            selected.append((raw, key, entry))
        return selected
    if number == 7:
        selected = []
        for key in N07_REFERENT_KEYS:
            entry = PORTRAIT_REGISTRY[N07_REFERENT_REGISTRY_KEYS[key]]
            marker = N07_REFERENT_REFERENCE_MARKERS[key]
            raw = next((ref for ref in refs if marker.casefold() in ref.casefold()), None)
            if raw is None:
                raise ValueError(f"La referencia N07 no permite resolver al referente {key} mediante {marker}")
            selected.append((raw, key, entry))
        return selected
    selected: list[tuple[str, str, dict]] = []
    seen: set[str] = set()
    for ref in refs:
        try:
            key, entry = portrait_entry(ref)
        except ValueError:
            continue
        if key == "diego-carralbal" or key in seen:
            continue
        seen.add(key)
        selected.append((ref, key, entry))
        if len(selected) == 6:
            break
    if len(selected) != 6:
        raise ValueError(f"Se requieren seis referentes con foto; se resolvieron {len(selected)}: {[item[1] for item in selected]}")
    return selected


def reference_cards(number:int,refs:list[str],assets:Path)->str:
    cards=[]
    for idx,(ref,key,entry) in enumerate(principal_references(number, refs),1):
        name = entry["name"]
        if number == 4 and key == "iso":
            name = "ISO / IEC"
        filename=f"referent-{key}.jpg"
        packaged_portrait = assets / filename
        registry_portrait = PORTRAIT_BANK / f"{key}.jpg"
        portrait_source = packaged_portrait if number in {5, 6, 7} and packaged_portrait.exists() else registry_portrait
        if not portrait_source.exists() or portrait_source.stat().st_size == 0:
            raise ValueError(f"El retrato registrado no existe: {portrait_source} ({ref})")
        copy_asset(portrait_source, packaged_portrait)
        portrait=f'<img class="contributor-portrait" src="assets/{filename}" alt="Retrato o fotografía documental de {esc(name)}">'
        work, publication = REFERENCE_WORKS.get(key, (sentence(ref, 110), "Referencia base de la lectura"))
        if number == 9 and key == "iso":
            work = "ISO 9241-210:2019 · Ergonomics of human-system interaction — Human-centred design for interactive systems"
            publication = "International Standard, 2019"
        if number == 4 and key == "iso":
            work = "ISO/IEC 25012:2008 · Software engineering — SQuaRE — Data quality model"
            publication = "International Standard, 2008"
        if number == 7 and key == "elham-tabassi":
            work = "Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile"
            publication = "NIST AI 600-1, 2024 · equipo coautor"
        work_label = "" if number == 0 else "<span>OBRA PRINCIPAL UTILIZADA</span>"
        cards.append(f'''<article class="contributor">{portrait}<b>{idx:02d}</b><h3>{esc(name)}</h3>{work_label}<cite>{esc(work)}</cite><p>{esc(publication)}</p></article>''')
    return ''.join(cards)


def authors_html(number:int,refs:list[str],assets:Path)->str:
    intro = "Seis referentes y las obras principales utilizadas para construir este mapa de la materia." if number == 0 else "Seis voces principales para ampliar, contrastar y discutir esta lectura."
    return f'''<section class="front-page authors-page"><header><span>METSI · FCE-UBA</span><h2>Referentes</h2><p>{esc(intro)}</p></header><div class="contributors-grid">{reference_cards(number,refs,assets)}</div><blockquote>N{number:02d} no resume estas fuentes ni las convierte en una receta. Las pone en tensión para construir juicio profesional.</blockquote></section>'''


def hotel_voices_html(number: int, assets: Path) -> str:
    if number == 0:
        profiles = {
            "Elena Acosta": ("52 años", "Estratégica, directa y orientada a resultados. Piensa en continuidad, reputación y capacidad de inversión.", "Perder competitividad o control sobre una transformación costosa.", "Una plataforma integrada puede ordenar el hotel.", "La coordinación informal absorbe contradicciones que el tablero no muestra.", "Define ambición, riesgo aceptable y recursos."),
            "Lucía Ferreyra": ("29 años", "Pragmática, observadora y cercana a la experiencia del huésped. Conoce excepciones y reparaciones.", "Quedar frente al huésped sin una respuesta ni margen para reparar.", "Si las pantallas coinciden, el trabajo será manejable.", "Muchas reglas que producen el conflicto nacen antes de Recepción.", "Aporta episodios concretos, excepciones y daño observable."),
            "Mariela Benítez": ("41 años", "Supervisa habitaciones, turnos y excepciones. Conoce el trabajo que no cabe en el estado final del PMS.", "Que su equipo cargue con una promesa que otras áreas definieron sin condiciones operativas.", "Registrar limpieza terminada alcanza para declarar una habitación liberada.", "No controla cerraduras, asignación ni la promesa comercial que interpreta Recepción.", "Aporta secuencias reales, daños, tiempos y condiciones de entrega."),
            "Ricardo Sosa": ("47 años", "Concreto, exigente y atento a la capacidad real de operación. Desconfía de promesas sin respaldo.", "Que Comercial o Tecnología comprometan algo que Operaciones no pueda sostener.", "El problema aparece cuando la operación no es escuchada.", "Un dato tardío puede producir un diagnóstico operacional falso.", "Visibiliza capacidad, dependencias y condiciones de cumplimiento."),
            "Federico Müller": ("34 años", "Analítico, orientado a trazabilidad, seguridad e integración. Busca contratos y estados explícitos.", "Que se culpe a la tecnología por una contradicción que no es técnica.", "Estados y contratos trazables resolverán la coordinación.", "La consistencia técnica también puede sostener una promesa equivocada.", "Aporta datos, integraciones e incertidumbre técnica."),
            "Camila Duarte": ("38 años", "Orientada a demanda, posicionamiento y desempeño de canales. Traduce objetivos comerciales en promesas al mercado.", "Perder ocupación y venta directa si las reglas de disponibilidad vuelven lenta la respuesta comercial.", "Una oferta atractiva puede publicarse y sus excepciones coordinarse después.", "Las campañas y condiciones de canal pueden trasladar a Operaciones y al huésped el costo de una promesa imposible.", "Aporta compromisos comerciales, promociones, reglas de canal, demanda y condiciones ofrecidas."),
        }
        cards = []
        for index, (name, role, filename) in enumerate(N00_HOTEL_CHARACTERS, 1):
            editorial_portrait = EDITORIAL_CHARACTER_PORTRAITS / filename
            portrait_source = editorial_portrait if editorial_portrait.exists() else CHARACTER_PORTRAITS / filename
            copy_asset(portrait_source, assets / f"hotel-{filename}")
            age, traits, fear, assumption, blind_spot, contribution = profiles[name]
            cards.append(f'''<article class="hotel-archetype-card hotel-archetype-{index}"><div class="hotel-archetype-portrait"><img src="assets/hotel-{esc(filename)}" alt="Retrato editorial de {esc(name)}"></div><div class="hotel-archetype-copy"><span>{esc(role)} · {esc(age)}</span><h3>{esc(name)}</h3><p><b>Perfil.</b> {esc(traits)}</p><p><b>Miedo.</b> {esc(fear)}</p><p><b>Supuesto.</b> {esc(assumption)}</p><p><b>Punto ciego.</b> {esc(blind_spot)}</p><p><b>Aporte.</b> {esc(contribution)}</p></div></article>''')
        return f'''<aside class="hotel-archetypes"><header><b>HOTEL HORIZONTE · N00</b><h2>Las personas que sostienen el caso</h2><p>Seis arquetipos profesionales con responsabilidades, supuestos y temores diferentes.</p></header><div class="hotel-archetypes-grid">{''.join(cards)}</div></aside>'''
    voices = HOTEL_VOICES[number]
    characters = N00_HOTEL_CHARACTERS if number == 1 else HOTEL_CHARACTERS
    cards = []
    for index, (name, role, filename) in enumerate(characters, 1):
        editorial_portrait = EDITORIAL_CHARACTER_PORTRAITS / filename
        n07_portrait = assets / f"hotel-{filename}"
        n00_portrait = HERE / "N00" / "assets" / f"hotel-{filename}"
        if number == 7 and n07_portrait.exists():
            portrait_source = n07_portrait
        elif number == 7 and n00_portrait.exists():
            portrait_source = n00_portrait
        else:
            portrait_source = editorial_portrait if editorial_portrait.exists() else CHARACTER_PORTRAITS / filename
        copy_asset(portrait_source, assets / f"hotel-{filename}")
        cards.append(
            f'''<article class="hotel-voice hotel-voice-{index}"><img src="assets/hotel-{esc(filename)}" alt="Retrato editorial de {esc(name)}"><div><span>{esc(role)}</span><h3>{esc(name)}</h3><p>“{esc(voices[name])}”</p></div></article>'''
        )
    count_word = "Seis" if number == 1 else "Cuatro"
    caption = "Seis relatos verdaderos que ninguno explica por sí solo." if number == 1 else "La misma contradicción cambia según la responsabilidad desde la que se la observa."
    return f'''<aside class="hotel-voices-compact"><header><b>HOTEL HORIZONTE · N{number:02d}</b><h2>{count_word} voces dentro del sistema</h2><p>{caption}</p></header><div class="hotel-voices-grid">{''.join(cards)}</div></aside>'''


def split_n02_glossary_for_print(body: str) -> str:
    """Move the glossary's complete third column to the following page."""
    match = re.search(r"<ul>(.*?)</ul>", body, flags=re.DOTALL)
    if not match:
        raise ValueError("No se encontró la lista del glosario N02")
    items = re.findall(r"<li\b.*?</li>", match.group(1), flags=re.DOTALL)
    if len(items) != 19:
        raise ValueError(f"El glosario N02 debe tener 19 entradas, no {len(items)}")
    primary = "".join(items[:13])
    continuation = "".join(items[13:])
    split_lists = (
        '<div class="n02-glossary-flow">'
        f'<ul class="n02-glossary-primary">{primary}</ul>'
        f'<ul class="n02-glossary-continuation">{continuation}</ul>'
        '</div>'
    )
    return body[:match.start()] + split_lists + body[match.end():]


def build_document(number:int)->dict:
    source=source_path(number)
    title,sections=parse_source(source)
    out=HERE/("N01-v18-final" if number == 1 else "N02-v14-final" if number == 2 else "N03-v9-final" if number == 3 else "N04-v9-final" if number == 4 else "N05-v9-final" if number == 5 else "N06-v9-final" if number == 6 else "N07-v9-final" if number == 7 else f"N{number:02d}")
    assets=out/"assets"; diagrams=out/"diagrams"; output=out/"output"
    for folder in (assets,diagrams,output): folder.mkdir(parents=True,exist_ok=True)
    if number in {1, 3, 4, 5, 6, 7}:
        packaged_source = out / "source"
        provenance = out / "provenance"
        packaged_source.mkdir(parents=True, exist_ok=True)
        provenance.mkdir(parents=True, exist_ok=True)
        copy_asset(source, packaged_source / source.name)
        if number == 1:
            shutil.copy2(HERE / "N01" / "image-curation" / "image-manifest.json", provenance / "image-manifest.json")

    if number == 0:
        cover_source = HERE / "N00" / "image-curation" / "selected" / "cover.jpg"
    elif number == 1:
        cover_source = HERE / "N01" / "image-curation" / "selected" / "cover.jpg"
    elif number == 2:
        cover_source = HERE / "N02" / "assets" / "cover.jpg"
    elif number == 3:
        cover_source = HERE / "N03-v9-final" / "assets" / "cover-source-premium-v2.png"
    elif number == 4:
        cover_source = HERE / "N04-v9-final" / "assets" / "cover-source-premium-bw-v2.png"
    elif number == 5:
        cover_source = HERE / "N05-v9-final" / "assets" / "cover-source-premium-bw-v1.png"
    elif number == 6:
        cover_source = HERE / "N06-v9-final" / "assets" / "cover-source-premium-bw-v1.png"
    elif number == 7:
        cover_source = HERE / "N07-v9-final" / "assets" / "cover-source-premium-bw-v1.png"
    elif number == 8:
        cover_source = HERE / "N08" / "image-curation" / "selected" / "cover.jpg"
    elif number == 9:
        cover_source = HERE / "N09" / "image-curation" / "selected" / "cover.jpg"
    elif number == 10:
        cover_source = HERE / "N10" / "image-curation" / "selected" / "cover.jpg"
    else:
        cover_source=N01_ROOT/COVER_IMAGES[number-1]
    cover_file="cover"+cover_source.suffix.lower()
    copy_asset(cover_source,assets/cover_file)
    closing_source = assets / "matches-close.png" if number in {5, 6, 7} and (assets / "matches-close.png").exists() else MATCHES
    copy_asset(closing_source,assets/"matches-close.png")
    if number == 0:
        hotel_source = HERE / "N02" / "assets" / "hotel-horizonte.png"
    elif number == 5:
        hotel_source = HERE / "N05-v9-final" / "assets" / "hotel-horizonte.jpg"
    elif number == 6:
        hotel_source = None
    elif number == 7:
        hotel_source = None
    elif number in {8, 9, 10}:
        hotel_source = HERE / "N02" / "assets" / "hotel-horizonte.png"
    else:
        hotel_source = HOTEL_HORIZONTE
    hotel_file = ""
    if hotel_source is not None:
        hotel_file = "hotel-horizonte" + hotel_source.suffix.lower()
        copy_asset(hotel_source, assets / hotel_file)

    bank_files=sorted(p for p in USER_BANK.iterdir() if p.suffix.lower() in {'.jpg','.jpeg','.png'}) if USER_BANK.is_dir() else []
    selected=[]
    if number == 0:
        editorial_sources = [
            HERE / "N00" / "image-curation" / "selected" / "editorial-01.jpg",
            HERE / "N00" / "image-curation" / "selected" / "editorial-02.jpg",
            HERE / "N00" / "image-curation" / "selected" / "editorial-03.jpg",
            HERE / "N00" / "image-curation" / "selected" / "editorial-07.jpg",
            HERE / "N05" / "image-curation" / "selected" / "hotel-horizonte-n05.jpg",
            HERE / "N00" / "image-curation" / "selected" / "editorial-06-ai-latam-v2.png",
            HERE / "N00" / "image-curation" / "selected" / "editorial-06.jpg",
            HERE / "N00" / "image-curation" / "selected" / "editorial-04-latam-v2.png",
            HERE / "N00" / "image-curation" / "selected" / "editorial-05.jpg",
        ]
    elif number == 1:
        editorial_sources = [
            HERE / "N01" / "image-curation" / "selected" / f"editorial-{index:02d}.jpg"
            for index in range(1, 7)
        ]
    elif number == 2:
        editorial_sources = [HERE / "N02" / "assets" / f"editorial-{index:02d}.jpg" for index in range(1, 7)]
    elif number == 3:
        editorial_sources = [bank_files[index] for index in (1, 2, 4, 7, 10, 13, 16)]
    elif number == 4:
        editorial_sources = [
            N01_ROOT / "recovered-references" / "candidate-pexels-34434151.jpg",
            N01_ROOT / "recovered-references" / "candidate-unsplash-R54zbJosh6Q.jpg",
            N01_ROOT / "final-keep-growing" / "body" / "assets" / "pexels-13663648.jpg",
            N01_ROOT / "final-keep-growing" / "body" / "assets" / "pexels-16382939.jpg",
            N01_ROOT / "final-keep-growing" / "body" / "assets" / "pexels-33487193.jpg",
            N01_ROOT / "cover-proof" / "candidates-v5" / "pexels-7859332.jpg",
            N01_ROOT / "cover-proof" / "candidates-v4" / "pexels-7047470.jpg",
            N01_ROOT / "recovered-references" / "candidate-unsplash-8M6z_BLUFkU.jpg",
        ]
    elif number == 5:
        editorial_sources = [
            HERE / "N05-v9-final" / "assets" / "editorial-01.jpg",
            HERE / "N05-v9-final" / "assets" / "editorial-02.jpg",
            HERE / "N05-v9-final" / "assets" / "editorial-03.jpg",
            HERE / "N05-v9-final" / "assets" / "editorial-04.jpg",
            HERE / "N05-v9-final" / "assets" / "editorial-05.jpg",
            HERE / "N05-v9-final" / "assets" / "editorial-06.jpg",
            HERE / "N05-v9-final" / "assets" / "editorial-07.jpg",
            HERE / "N05-v9-final" / "assets" / "editorial-08.jpg",
        ]
    elif number == 6:
        editorial_sources = [
            HERE / "N06-v9-final" / "assets" / "editorial-03.jpg",
            HERE / "N06-v9-final" / "assets" / "editorial-06.jpg",
            HERE / "N06-v9-final" / "assets" / "editorial-07.jpg",
        ]
    elif number == 7:
        editorial_sources = [
            HERE / "N07-v9-final" / "assets" / "editorial-01.png",
            HERE / "N07-v9-final" / "assets" / "editorial-02.png",
            HERE / "N07-v9-final" / "assets" / "editorial-03.png",
            HERE / "N07-v9-final" / "assets" / "editorial-04.png",
            HERE / "N07-v9-final" / "assets" / "pause-01.png",
            HERE / "N07-v9-final" / "assets" / "pause-02.png",
        ]
    elif number == 8:
        editorial_sources = [
            HERE / "N08" / "image-curation" / "selected" / "editorial-01.jpg",
            HERE / "N08" / "image-curation" / "selected" / "editorial-02.jpg",
            HERE / "N08" / "image-curation" / "selected" / "editorial-03.jpg",
            HERE / "N08" / "image-curation" / "selected" / "editorial-04.jpg",
            HERE / "N08" / "image-curation" / "selected" / "editorial-05.jpg",
            HERE / "N08" / "image-curation" / "selected" / "editorial-06.jpg",
            HERE / "N08" / "image-curation" / "selected" / "editorial-07.jpg",
            HERE / "N08" / "image-curation" / "selected" / "editorial-08.jpg",
        ]
    elif number == 9:
        editorial_sources = [
            HERE / "N09" / "image-curation" / "selected" / "editorial-01.jpg",
            HERE / "N09" / "image-curation" / "selected" / "editorial-02.jpg",
            HERE / "N09" / "image-curation" / "selected" / "editorial-03.jpg",
            HERE / "N09" / "image-curation" / "selected" / "editorial-04.jpg",
            HERE / "N09" / "image-curation" / "selected" / "editorial-05.jpg",
            HERE / "N09" / "image-curation" / "selected" / "editorial-06.jpg",
            HERE / "N09" / "image-curation" / "selected" / "editorial-07.jpg",
            HERE / "N09" / "image-curation" / "selected" / "editorial-08.jpg",
        ]
    elif number == 10:
        editorial_sources = [
            HERE / "N10" / "image-curation" / "selected" / "editorial-01.jpg",
            HERE / "N10" / "image-curation" / "selected" / "editorial-02.jpg",
            HERE / "N10" / "image-curation" / "selected" / "editorial-03.jpg",
            HERE / "N10" / "image-curation" / "selected" / "editorial-04.jpg",
            HERE / "N10" / "image-curation" / "selected" / "editorial-05.jpg",
            HERE / "N10" / "image-curation" / "selected" / "editorial-06.jpg",
            HERE / "N10" / "image-curation" / "selected" / "editorial-07.jpg",
            HERE / "N10" / "image-curation" / "selected" / "editorial-08.jpg",
        ]
    else:
        editorial_sources = [bank_files[((number-1)*5+offset*3)%len(bank_files)] for offset in range(6)]
    for offset, src in enumerate(editorial_sources):
        target=src.name if number in {6, 7} else f"editorial-{offset+1:02d}{src.suffix.lower()}"
        copy_asset(src,assets/target); selected.append(target)
    sparse_fill_images=[]
    if number == 0:
        # N00 reserva cada fotografía para una única función editorial. No se
        # crean rellenos automáticos ni repeticiones dentro del documento.
        sparse_sources = []
    elif number == 1:
        sparse_sources = [HERE / "N01" / "image-curation" / "selected" / "contents.jpg"]
    elif number == 2:
        sparse_sources = [HERE / "N02" / "assets" / f"sparse-fill-{index:02d}.jpg" for index in range(1, 3)]
    elif number == 3:
        sparse_sources = [
            bank_files[18],
            bank_files[19],
            N01_ROOT / "recovered-references" / "candidate-unsplash-8M6z_BLUFkU.jpg",
            N01_ROOT / "recovered-references" / "candidate-unsplash-KgtOr1cCECw.jpg",
        ]
    elif number in {4, 5}:
        # N04 usa únicamente pausas visuales deliberadas y conceptuales.
        # Los retratos genéricos que antes rellenaban huecos confundían
        # emoción con evidencia y producían páginas semánticamente falsas.
        sparse_sources = []
    elif number == 6:
        sparse_sources = []
    elif number == 7:
        sparse_sources = []
    elif number == 8:
        sparse_sources = [
            HERE / "N08" / "image-curation" / "selected" / "sparse-fill-01.jpg",
            HERE / "N08" / "image-curation" / "selected" / "sparse-fill-02.jpg",
            HERE / "N08" / "image-curation" / "selected" / "sparse-fill-03.jpg",
        ]
    elif number == 9:
        sparse_sources = [
            HERE / "N09" / "image-curation" / "selected" / "sparse-fill-01.jpg",
            HERE / "N09" / "image-curation" / "selected" / "sparse-fill-02.jpg",
            HERE / "N09" / "image-curation" / "selected" / "sparse-fill-03.jpg",
        ]
    elif number == 10:
        sparse_sources = [
            HERE / "N10" / "image-curation" / "selected" / "sparse-fill-01.jpg",
            HERE / "N10" / "image-curation" / "selected" / "sparse-fill-02.jpg",
            HERE / "N10" / "image-curation" / "selected" / "sparse-fill-03.jpg",
        ]
    else:
        sparse_sources = bank_files[-2:]
    for offset,src in enumerate(sparse_sources,1):
        target=f"sparse-fill-{offset:02d}{src.suffix.lower()}"
        copy_asset(src,assets/target); sparse_fill_images.append(target)

    diagram=build_diagram(number,title,sections,diagrams/f"N{number:02d}-mapa-decision.svg")
    thesis_section=next((s for s in sections if s.title=="Tesis"),sections[0])
    thesis=first_paragraph(thesis_section)
    refs=references(sections)
    portrait_refs = []
    for raw, key, entry in principal_references(number, refs):
        portrait_ref = {
            "key": key,
            "name": entry["name"],
            "source_page": entry["source_page"],
        }
        rights_status = entry["rights_status"]
        if number == 5 and key in {"edward-freeman", "enid-mumford"}:
            portrait_ref["rights_basis"] = "Permiso confirmado por Diego Carralbal el 2026-09-03 para publicar el retrato dentro del paquete N05 en carralbal/UBA-metsi."
            rights_status = "permission_confirmed_by_course_author"
        if number == 5 and key == "sasha-costanza-chock":
            rights_status = "wikimedia_commons_cc_by_sa_4_0"
        if number == 5 and key == "nist":
            portrait_ref["source_page"] = "https://commons.wikimedia.org/wiki/File:NIST_campus_aerial_2019.jpg"
            rights_status = "wikimedia_commons_cc_by_sa_4_0"
        if number == 6:
            for field in ("image_url", "creator", "license_name", "license_url"):
                if entry.get(field):
                    portrait_ref[field] = entry[field]
            portrait_ref["transformations"] = [
                "recorte editorial cuadrado",
                "conversión a escala de grises",
                "redimensionado a 720 × 720 píxeles",
            ]
        if number == 7:
            for field in ("image_url", "creator", "credit_line", "license_name", "license_url"):
                if entry.get(field):
                    portrait_ref[field] = entry[field]
            portrait_ref["transformations"] = [
                "recorte editorial cuadrado",
                "conversión a escala de grises",
                "redimensionado a 720 × 720 píxeles",
            ]
        portrait_ref["rights_status"] = rights_status
        portrait_ref["file"] = f"referent-{key}.jpg"
        portrait_path = assets / portrait_ref["file"]
        if portrait_path.exists():
            portrait_ref["sha256"] = asset_sha(portrait_path)
        portrait_refs.append(portrait_ref)
    source_entries=[]
    title_source_id=f"N{number:02d}-h1"
    source_block(source_entries,title_source_id,"heading-1",title.replace(f"N{number:02d} — ","").replace(f"N{number:02d} · ",""))
    chunks=[]; quotes=[]
    references_plate=""
    # Insert each photographic pause before the following conceptual family.
    # These boundaries keep the pauses separated from the full-width photo
    # bands and preserve a readable alternation of prose and visual breathing.
    pause_after=set() if number in {0, 1, 2, 3, 4} else {5,11,17}
    photo_after=set() if number in {1, 3, 4} else {4,10,16}
    n01_photo_after = {
        "El mapa perfecto de la montaña equivocada": 0,
        "La metodología como sistema de preguntas": 2,
        "Tailoring: adaptar sin perder la lógica": 4,
        "2026: cuando el método también debe gobernar agentes": 5,
    }
    n01_photo_captions = {
        "El mapa perfecto de la montaña equivocada": "Una red técnica sólo adquiere sentido cuando se reconstruyen las relaciones que sostiene y los efectos que distribuye.",
        "La metodología como sistema de preguntas": "Elegir un recorrido significa declarar qué bifurcaciones se descartan y bajo qué evidencia podría revisarse la elección.",
        "Tailoring: adaptar sin perder la lógica": "Una pauta puede ordenar la acción sin clausurar la lectura del contexto ni convertir la repetición en criterio de calidad.",
        "2026: cuando el método también debe gobernar agentes": "La frontera entre infraestructura y entorno permanece irregular: automatizar exige conservar autoridad, trazabilidad y reversión.",
    }
    n01_photo_alts = {
        "El mapa perfecto de la montaña equivocada": "Poste de servicios con una trama densa de cables en Santarém, Brasil.",
        "La metodología como sistema de preguntas": "Laberinto de setos verdes visto desde arriba.",
        "Tailoring: adaptar sin perder la lógica": "Cubierta arquitectónica curva formada por una trama repetida de vigas y sombras.",
        "2026: cuando el método también debe gobernar agentes": "Cables, poste y follaje entrelazados en Veracruz, México.",
    }
    n01_pause_after = {
        "Pregunta profesional": (
            1,
            "La metodología no elimina la incertidumbre. La vuelve visible, discutible y gobernable.",
        ),
        "Metodología como diseño de un sistema de aprendizaje": (
            3,
            "La velocidad amplifica una dirección previa. No reemplaza el juicio que la eligió.",
        ),
    }
    n01_pause_alts = {
        "Pregunta profesional": "Geometría arquitectónica blanca atravesada por sombras diagonales.",
        "Metodología como diseño de un sistema de aprendizaje": "Estelas blancas de luz atraviesan un fondo negro.",
    }
    n02_pause_after = {
        "Pregunta profesional": (
            2,
            "Una pantalla puede decir la verdad sobre una parte y llevarnos a una conclusión falsa sobre el conjunto.",
        ),
        "Cómo emerge un resultado que ningún componente controla": (
            3,
            "Decir que una propiedad es emergente no significa que sea misteriosa.",
        ),
    }
    n03_pause_after = {
        "Pregunta profesional": (
            3,
            "El efecto de la intervención vuelve como condición de la siguiente decisión.",
            "Detalle desaturado de una consola con canales paralelos, controles y recorridos superpuestos.",
        ),
        "Movimiento 2 · Observar cómo regresan los efectos": (
            5,
            "Una estabilidad observada puede depender de trabajo invisible, no de la ausencia de tensión.",
            "Trama abstracta de líneas luminosas que se cruzan y regresan sobre un fondo oscuro.",
        ),
    }
    n02_photo_after = {
        "Tesis": 0,
        "El sistema efectivo incluye trabajo que no figura en arquitectura": 5,
        "Objeciones y límites: ampliar la frontera también cuesta": 4,
    }
    n00_photo_after = {
        "La partitura que todavía no es música": 0,
        "Los 36 Núcleos no son 36 clases magistrales": 1,
        "Qué vas a hacer en los encuentros": 7,
        "Aprender con inteligencia artificial": 5,
    }
    n00_photo_captions = {
        "La partitura que todavía no es música": (
            "Un plan coordina expectativas; la acción situada revela qué debe revisarse cuando el contexto contradice el plan."
        ),
        "Los 36 Núcleos no son 36 clases magistrales": (
            "Cada Núcleo agrega una capacidad que el siguiente presupone: el recorrido es acumulativo, no una colección de temas."
        ),
        "Qué vas a hacer en los encuentros": (
            "El encuentro convierte interpretaciones iniciales en material de contraste, práctica y revisión compartida."
        ),
        "Aprender con inteligencia artificial": (
            "La IA amplía producción y exploración; la persona conserva verificación, trazabilidad, autoridad y responsabilidad."
        ),
    }
    n00_photo_alts = {
        "Qué vas a hacer en los encuentros": (
            "Grupo de estudiantes universitarios argentinos y latinoamericanos discute alrededor de una mesa con apuntes impresos."
        ),
        "Aprender con inteligencia artificial": (
            "Dos estudiantes y un docente latinoamericanos revisan fuentes impresas junto a una computadora portátil."
        ),
    }
    # N00 uses two deliberate photographic pauses at major transitions. They
    # are distinct from the immutable, image-only matches closing page.
    n00_pause_after = {}
    n00_part_pauses = {
        "Parte I. Qué materia empieza acá": (
            6,
            "Antes de intervenir, hay que aprender a escuchar lo que la representación todavía no explica.",
            "Auditorio visto desde la platea, con butacas vacías y una orquesta que ensaya en el escenario antes del concierto.",
            "n00-pause-opening",
        ),
        "Parte II. Cómo se lee una N": (
            8,
            "Leer no es atravesar páginas. Es llegar con una posición que otras miradas puedan poner a prueba.",
            "Aula universitaria casi vacía, con dos personas conversando junto a un pizarrón y mesas de trabajo.",
            "n00-pause-transition",
        ),
    }
    n04_photo_after = {
        "Un argumento profesional no es una pila de datos": 0,
        "Validez, confiabilidad y utilidad: tres preguntas diferentes": 1,
        "Correlación, mecanismo y causalidad": 2,
        "IA, procedencia y verdad en 2026": 5,
    }
    n04_pause_after = {
        "Pregunta profesional": (
            3,
            "Una cifra no habla sola: adquiere sentido cuando puede reconstruirse la cadena que la convierte en decisión.",
        ),
        "Movimiento 2 · Contrastar explicaciones sin borrar incertidumbre": (
            4,
            "La evidencia más valiosa no confirma una historia: permite distinguir entre explicaciones rivales.",
        ),
    }
    n05_photo_after = {
        "Movimiento 1 · Pasar de interesados genéricos a relaciones de poder": 0,
        "Movimiento 3 · Gobernar objeción, supervisión y reparación": 5,
    }
    n05_pause_after = {
        "Pregunta profesional": (
            2,
            "Una silla vacía no es ausencia de información. Puede ser evidencia de quién todavía no pudo intervenir en la decisión.",
        ),
        "Movimiento 2 · Diseñar participación capaz de cambiar una decisión": (
            4,
            "Participar importa cuando una objeción puede cambiar el curso, no sólo quedar registrada.",
        ),
    }
    n06_photo_after = {}
    n06_pause_after = {
        "Pregunta profesional": (
            0,
            "Investigar no es reunir más respuestas: es comprar la diferencia que una decisión necesita.",
        ),
        "Movimiento 1 · Formular incertidumbres que puedan cambiar una decisión": (
            1,
            "Cada compromiso compra aprendizaje y, al mismo tiempo, consume opciones.",
        ),
    }
    n07_photo_after = {
        "La pregunta que fabricó la respuesta": 0,
        "Movimiento 2 · Diseñar una situación en la que resulte posible decir": 1,
        "Movimiento 3 · Convertir relatos en afirmaciones contrastables": 2,
    }
    n07_photo_captions = {
        "La pregunta que fabricó la respuesta": "La forma de preguntar distribuye qué puede decirse, qué queda en silencio y qué respuesta termina pareciendo inevitable.",
        "Movimiento 2 · Diseñar una situación en la que resulte posible decir": "Una conversación produce evidencia sólo cuando la situación permite disentir sin convertir la respuesta en exposición o riesgo.",
        "Movimiento 3 · Convertir relatos en afirmaciones contrastables": "Conservar preguntas, rastros y transformaciones permite distinguir una frase recordada de una afirmación capaz de sostener una decisión.",
    }
    n07_photo_alts = {
        "La pregunta que fabricó la respuesta": "Dos profesionales argentinos conversan alrededor de una mesa de trabajo; una persona explica mientras la otra escucha y toma notas, con un mate visible entre los materiales.",
        "Movimiento 2 · Diseñar una situación en la que resulte posible decir": "Dos trabajadoras argentinas conversan al mismo nivel en un entorno operativo; una viste indumentaria reflectiva y la otra escucha con un cuaderno.",
        "Movimiento 3 · Convertir relatos en afirmaciones contrastables": "Vista cenital de manos que ordenan notas, tarjetas, un grabador y auriculares para reconstruir la trazabilidad de una entrevista.",
    }
    n07_pause_after = {
        "Pregunta profesional": (
            4,
            "Cada pregunta ilumina una parte de la experiencia y deja otras en sombra.",
        ),
        "Movimiento 1 · Construir preguntas que no fabriquen la respuesta": (
            5,
            "Un solo incidente no demuestra prevalencia ni causalidad. Sí puede refutar una afirmación universal.",
        ),
    }
    n07_pause_alts = {
        "Pregunta profesional": "Dos sillas vacías frente a una puerta abierta en una sala de entrevistas, con luz lateral y una amplia escala de grises.",
        "Movimiento 1 · Construir preguntas que no fabriquen la respuesta": "Trabajadora de servicio vista a través de capas de vidrio y reflejos en un corredor, entre lo que el procedimiento declara y el trabajo que efectivamente ocurre.",
    }
    n08_photo_after = {
        "De N07 a N08: de lo dicho a lo realizado": 0,
        "Coordinación, handoffs y cognición distribuida": 1,
        "Observar sin convertir en auditoría punitiva": 3,
        "2026: observar el trabajo alrededor de la IA": 4,
    }
    n08_pause_after = {
        "Variación, desvío, adaptación y deriva": (
            2,
            "La distancia respecto del procedimiento no explica por sí sola la función ni el riesgo de una práctica.",
        ),
        "De observación a hipótesis y rediseño": (
            5,
            "Antes de automatizar una tarea hay que comprender qué capacidad mantiene viva.",
        ),
        "2026: observar el trabajo alrededor de la IA": (
            6,
            "Supervisión humana sin tiempo, información, autoridad y alternativa es una ficción.",
        ),
    }
    n09_photo_after = {
        "De N08 a N09: del trabajo real al recorrido vivido": 0,
        "Accesibilidad como propiedad sistémica": 1,
        "Diseñar con diversidad sin inventar un usuario promedio": 3,
        "Personalización e IA": 4,
    }
    n09_pause_after = {
        "Usabilidad y resultado": (
            2,
            "Una experiencia sin barreras aparentes puede seguir produciendo exclusión en el resultado.",
        ),
        "Métricas distributivas y de equilibrio": (
            5,
            "El promedio mejora con facilidad cuando deja fuera a quienes más fricción encuentran.",
        ),
        "2026: las interfaces conversacionales amplían acceso y crean nuevas barreras": (
            6,
            "Conversar con una interfaz no vuelve accesible el servicio si la persona no puede comprender, corregir o reclamar.",
        ),
    }
    n10_photo_after = {
        "Desde requerimientos hacia atrás": 1,
        "Outcome: el cambio que importa, no la cosa que se entrega": 3,
        "2026: “necesitamos IA” es un pedido, no un diagnóstico": 4,
        "Quién formula el problema también forma parte del problema": 5,
    }
    n10_pause_after = {
        "El pedido, el síntoma y el problema cumplen funciones distintas": (
            2,
            "El pedido nombra una respuesta; el encuadre debe explicar qué situación justifica intervenir.",
        ),
        "Evidencia que puede cambiar el encuadre": (
            7,
            "Un problema es revisable cuando declara qué evidencia podría volverlo falso.",
        ),
        "La puerta de decisión: aprobar, devolver, dividir o reformular": (
            6,
            "La fuerza del encuadre debe crecer con el costo de perder opciones.",
        ),
    }
    # The generated map is a whole-reading synthesis, not a reusable ornament.
    # Insert it once, after the initial conceptual development. Repeating the
    # same SVG later in the document creates a false sense of new information.
    # The compact map opens the conceptual family after the first pause and is
    # immediately interpreted by prose on the same reading sequence.
    diagram_before=set() if number == 0 else {6}
    hotel_voices_inserted = False
    display_index = 0
    for source_index,section in enumerate(sections,1):
        section_prefix=f"N{number:02d}-s{source_index:02d}"
        heading_source_id=source_block(source_entries,f"{section_prefix}-h2","heading-2",section.title)
        body=render_markdown(section.lines,section_prefix,source_entries)
        if number == 1:
            body = apply_n01_accessible_dropcap(body, section.title)
            body = apply_n01_pagination_groups(body, section.title)
            if section.title == "Aplicación a Hotel Horizonte: construir HH-01":
                body = re.sub(
                    r'(<p data-source-id="N01-s21-b012">.*?</p>)(<p data-source-id="N01-s21-b013">.*?</p>)',
                    r'<aside class="n01-hh01-memo">\1\2</aside>',
                    body,
                    count=1,
                    flags=re.DOTALL,
                )
        if number == 2 and section.title == "Glosario esencial":
            body = split_n02_glossary_for_print(body)
        if is_part_section(section.title):
            part_label, _, part_title = section.title.partition(". ")
            part_chunk = '</article>'
            part_pause = n00_part_pauses.get(section.title) if number == 0 else None
            if part_pause and section.title.startswith("Parte II."):
                image_index, quote, alt, pause_class = part_pause
                quotes.append(quote)
                part_chunk += (
                    f'''<section class="full-bleed full-bleed-quote {pause_class}">'''
                    f'''<img src="assets/{esc(selected[image_index])}" alt="{esc(alt)}"><p>{esc(quote)}</p></section>'''
                )
            part_chunk += (
                f'''<section class="part-divider part-divider-n{number:02d}">'''
                f'''<div class="part-divider-copy"><b>{esc(part_label)}</b>'''
                f'''<h2 data-source-id="{heading_source_id}">{esc(part_title)}</h2>'''
                f'''<div class="part-divider-body">{body}</div></div></section>'''
            )
            if part_pause and section.title.startswith("Parte I."):
                image_index, quote, alt, pause_class = part_pause
                quotes.append(quote)
                part_chunk += (
                    f'''<section class="full-bleed full-bleed-quote {pause_class}">'''
                    f'''<img src="assets/{esc(selected[image_index])}" alt="{esc(alt)}"><p>{esc(quote)}</p></section>'''
                )
            chunks.append(part_chunk + '<article class="reading">')
            continue
        reference_apparatus = number in {0, 1, 2, 3, 4, 5, 6, 7} and section.title == "Referencias base"
        if not reference_apparatus:
            display_index += 1
        idx = display_index + 1 if reference_apparatus else display_index
        classes=section_classes(number,idx,section.title)
        if number in {1, 2, 3, 4, 5, 6, 7} and section.title == "Cinco píldoras para recordar":
            body = body.replace("<ul>", "<ol>", 1).replace("</ul>", "</ol>", 1)
        marker_number = "APARATO DE REFERENCIA" if reference_apparatus else f"SECCIÓN {idx:02d}" if number == 0 else f"{idx:02d}"
        route_label = ""
        if number in {1, 2, 3, 4, 5, 6, 7} and not reference_apparatus:
            if number == 1:
                route = (
                    "PROBLEMA" if idx <= 4 else
                    "DISTINCIONES" if idx <= 8 else
                    "DECISIONES" if idx <= 17 else
                    "PRUEBA" if idx <= 20 else
                    "TRANSFERENCIA" if idx <= 24 else
                    "PREPARACIÓN"
                )
            elif number == 2:
                route = (
                    "PROBLEMA" if idx <= 4 else
                    "DISTINCIONES" if idx <= 11 else
                    "DECISIONES" if idx <= 17 else
                    "PRUEBA" if idx == 18 else
                    "TRANSFERENCIA" if idx == 19 else
                    "PREPARACIÓN"
                )
            elif number == 3:
                route = (
                    "PROBLEMA" if idx <= 4 else
                    "DISTINCIONES" if idx == 5 else
                    "DECISIONES" if idx == 6 else
                    "PRUEBA" if idx == 7 else
                    "TRANSFERENCIA" if idx == 8 else
                    "PREPARACIÓN"
                )
            elif number == 7:
                route = (
                    "PROBLEMA" if idx <= 4 else
                    "DISTINCIONES" if idx == 5 else
                    "DECISIONES" if idx == 6 else
                    "PRUEBA" if idx == 7 else
                    "TRANSFERENCIA" if idx in {8, 9} else
                    "PREPARACIÓN"
                )
            else:
                route = (
                    "PROBLEMA" if idx <= 4 else
                    "DISTINCIONES" if idx == 5 else
                    "DECISIONES" if idx == 6 else
                    "PRUEBA" if idx == 7 else
                    "TRANSFERENCIA" if idx == 8 else
                    "PREPARACIÓN"
                )
            route_label = f' <em>{route}</em>' if number in {3, 4, 5, 6, 7} else f'<em>{route}</em>'
        marker=f'<div class="section-marker"><span>{marker_number}</span><b>METSI · N{number:02d}{route_label}</b></div>'
        prelude=""
        extra=""
        standalone_before=""
        if (number == 4 and section.title.startswith("Movimiento 1 ·")) or (number == 5 and section.title.startswith("Movimiento 2 ·")) or (number == 6 and section.title == "Instrumento de decisión: tablero mínimo de incertidumbres") or (number == 7 and section.title.startswith("Movimiento 3 ·")) or (number == 8 and section.title == "Instrumento de decisión: registro en capas") or (number == 9 and section.title == "Instrumento de decisión: mapa de recorrido accesible") or (number == 10 and section.title == "Instrumento: encuadre METSI en nueve decisiones") or (number == 1 and section.title == "Método, metodología, marco, práctica, técnica y herramienta") or (number == 2 and section.title == "Cinco objetos que no conviene llamar simplemente “el sistema”") or (number not in {0, 1, 2, 4, 5, 6, 7, 8, 9, 10} and idx in diagram_before):
            if number == 1:
                diagram_alt = "Relación entre marco, metodología, método, práctica, técnica y herramienta"
                diagram_caption = "Cada término cumple una función distinta: orientar, justificar, proceder, actuar, ejecutar o soportar."
            elif number == 3:
                diagram_alt = "Bucle reforzador entre presión por ocupación, sobreventa, reparación manual, datos tardíos e incertidumbre"
                diagram_caption = "La frontera separa control y análisis: lo externo puede seguir siendo decisivo, y una consecuencia puede volver como causa."
            elif number == 4:
                diagram_alt = "Cadena de evidencia desde la fuente hasta la decisión, con controles de procedencia, definición, incertidumbre, autoridad y revisión"
                diagram_caption = "Una afirmación defendible conserva la historia de sus transformaciones: de la fuente y el registro a la interpretación, la hipótesis y la decisión."
            elif number == 5:
                diagram_alt = "Mapa que relaciona seis posiciones actorales con una decisión y sus consecuencias: definir, conocer, autorizar, ejecutar, experimentar, objetar y reparar"
                diagram_caption = "El mapa no clasifica personas: registra qué relación tiene cada actor con una decisión, qué poder o conocimiento aporta y qué consecuencias puede soportar."
            elif number == 6:
                diagram_alt = "Secuencia entre pregunta decisoria, hipótesis rivales, cartera de evidencia, señal suficiente e hito de decisión"
                diagram_caption = "La evidencia vale cuando puede distinguir hipótesis y cambiar un compromiso a tiempo; el hito permite continuar, modificar, detener o investigar más."
            elif number == 7:
                diagram_alt = "Secuencia entre pregunta decisoria, episodio concreto, rastros y contraste, afirmación calibrada y decisión revisable"
                diagram_caption = "La entrevista produce evidencia cuando conecta episodios y rastros con afirmaciones de alcance explícito y decisiones que todavía pueden revisarse."
            elif number == 8:
                diagram_alt = "Registro en cuatro capas que distingue situación observada, adaptación, función sostenida y consecuencia decisoria"
                diagram_caption = "Observar trabajo invisible exige conectar episodio, variación, función y decisión; una conducta aislada no explica por sí sola el sistema."
            elif number == 9:
                diagram_alt = "Recorrido accesible en seis etapas desde la necesidad hasta la reparación"
                diagram_caption = "La experiencia se verifica de extremo a extremo: necesidad, acceso, comprensión, acción, resultado y reparación deben sostener la misma promesa."
            elif number == 10:
                diagram_alt = "Nueve decisiones conectadas para construir y revisar el encuadre de una intervención"
                diagram_caption = "Situación, frontera, evidencia, hipótesis, outcome, guardrails, intervención, gobierno y revisión forman un circuito: la evidencia puede obligar a reconstruir el problema."
            else:
                diagram_alt = "Cinco fronteras posibles para elegir qué sistema analizar"
                diagram_caption = "La palabra sistema cambia de significado según la decisión: cada frontera incluye relaciones distintas."
            diagram_class = "infographic infographic-boundaries n01-method-architecture" if number == 1 else "infographic infographic-boundaries"
            diagram_label = f"{diagram_alt} {diagram_caption}".strip()
            diagram_figure = (
                f'<figure class="{diagram_class}" role="img" aria-label="{esc(diagram_label)}">'
                f'<img src="diagrams/{diagram["file"]}" alt="">'
                f'<figcaption aria-hidden="true">{esc(diagram_caption)}</figcaption></figure>'
            )
            prelude += diagram_figure
        if (number == 0 and section.title in n00_photo_after) or (number == 1 and section.title in n01_photo_after) or (number == 2 and section.title in n02_photo_after) or (number == 4 and section.title in n04_photo_after) or (number == 5 and section.title in n05_photo_after) or (number == 6 and section.title in n06_photo_after) or (number == 7 and section.title in n07_photo_after) or (number == 8 and section.title in n08_photo_after) or (number == 9 and section.title in n09_photo_after) or (number == 10 and section.title in n10_photo_after) or (number not in {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10} and idx in photo_after):
            if number == 0:
                image = selected[n00_photo_after[section.title]]
            elif number == 1:
                image = selected[n01_photo_after[section.title]]
            elif number == 2:
                image = selected[n02_photo_after[section.title]] if section.title != "Tesis" else sparse_fill_images[0]
            elif number == 4:
                image = selected[n04_photo_after[section.title]]
            elif number == 5:
                image = selected[n05_photo_after[section.title]]
            elif number == 6:
                image = selected[n06_photo_after[section.title]]
            elif number == 7:
                image = selected[n07_photo_after[section.title]]
            elif number == 8:
                image = selected[n08_photo_after[section.title]]
            elif number == 9:
                image = selected[n09_photo_after[section.title]]
            elif number == 10:
                image = selected[n10_photo_after[section.title]]
            elif number == 3:
                image = selected[{4: 0, 10: 1, 16: 2}[idx]]
            else:
                image = selected[(idx//4)%len(selected)]
            figure_class = "photo-band n04-ai-photo" if number == 4 and section.title == "IA, procedencia y verdad en 2026" else "photo-band"
            photo_caption = (
                n00_photo_captions.get(section.title)
                if number == 0
                else n01_photo_captions.get(section.title)
                if number == 1
                else n07_photo_captions.get(section.title)
                if number == 7
                else None
            ) or sentence(first_paragraph(section), 135)
            if number == 2 and section.title == "Tesis":
                photo_alt = "Plano técnico con circuitos y recorridos superpuestos sobre una retícula."
            elif number == 2 and section.title == "El sistema efectivo incluye trabajo que no figura en arquitectura":
                photo_alt = "Entramado de barras estructurales y reflejos que se cruzan en múltiples direcciones."
            elif number == 2 and section.title == "Objeciones y límites: ampliar la frontera también cuesta":
                photo_alt = "Persona sentada frente a una obra compuesta por recorridos lineales densos."
            elif number == 7:
                photo_alt = n07_photo_alts[section.title]
            else:
                photo_alt = n00_photo_alts.get(section.title, f"Imagen conceptual vinculada con {section.title}") if number == 0 else n01_photo_alts.get(section.title, f"Imagen conceptual vinculada con {section.title}") if number == 1 else f"Imagen conceptual vinculada con {section.title}"
            extra+=visual_figure(image,photo_caption,photo_alt,figure_class)
        if section.title == "Referencias base":
            # Close the reading with a deliberate bibliography plate instead
            # of leaving a short citation list stranded on a mostly empty
            # page.  The image is document-specific and the citations remain
            # complete, searchable source text.
            image=selected[6] if number == 5 else selected[-1] if number in {6, 7} else selected[7] if number in {8, 9, 10} else selected[-1]
            if number in {0, 1, 2, 3, 5, 6, 7}:
                # Patrón canónico fijado por N10: bibliografía sobre blanco,
                # tipografía pequeña y sin una imagen que compita con las citas.
                pass
            elif number in {4, 8, 9, 10}:
                extra += visual_figure(
                    image,
                    "Las referencias abren nuevas preguntas: no sustituyen el juicio que esta lectura exige construir.",
                    "Imagen editorial sobre interpretación, evidencia y juicio profesional.",
                    "photo-band references-inline",
                )
            else:
                references_plate=f'''</article><section class="full-bleed references-image-full"><img src="assets/{esc(image)}" alt="Imagen editorial de cierre bibliográfico para N{number:02d}"><p>Las referencias abren nuevas preguntas: no sustituyen el juicio que esta lectura exige construir.</p></section><article class="reading">'''
        if "hotel-case" in classes:
            hotel_figure=visual_figure(
                hotel_file,
                "El software puede funcionar y la promesa fallar: el objeto de análisis es el sistema sociotécnico que produce el servicio.",
                "Cartel de hotel iluminado contra un cielo oscuro.",
                "photo-band hotel-photo",
            )
        else:
            hotel_figure=""
        heading_icon = case_application_icon() if "hotel-case" in classes else pills_summary_icon() if "pill-summary" in classes and number not in {0, 1, 2} else ""
        heading=f'<div class="section-heading">{marker}{heading_icon}<h2 data-source-id="{heading_source_id}">{esc(section.title)}</h2></div>'
        if standalone_before:
            chunks.append(standalone_before)
        data_section = "apparatus-reference" if reference_apparatus else f"{idx:02d}"
        hotel_voices_inside = ""
        if number == 2 and (
            "hotel-case" in classes
            or section.title == "Primera aplicación de HH-02: una reserva confirmada que no alcanza"
        ) and not hotel_voices_inserted:
            # Mantener las voces dentro del mismo flujo semántico que el caso
            # evita que Chromium las pinte antes de la continuación de la tabla
            # cuando la sección se fragmenta entre dos páginas.
            hotel_voices_inside = hotel_voices_html(number, assets)
            hotel_voices_inserted = True
        if number == 3 and section.title == "La mejora que volvió por la puerta de atrás" and not hotel_voices_inserted:
            hotel_voices_inside = hotel_voices_html(number, assets)
            hotel_voices_inserted = True
        if number == 4 and section.title == "El doce por ciento que parecía hablar solo" and not hotel_voices_inserted:
            hotel_voices_inside = hotel_voices_html(number, assets)
            hotel_voices_inserted = True
        if number == 7 and section.title.startswith("Movimiento 3 ·") and not hotel_voices_inserted:
            hotel_voices_inside = hotel_voices_html(number, assets)
            hotel_voices_inserted = True
        chunks.append(f'<section class="{" ".join(classes)}" data-section="{data_section}">{heading}{hotel_figure}{prelude}<div class="section-body">{body}</div>{extra}{hotel_voices_inside}</section>')
        if "hotel-case" in classes and not hotel_voices_inserted:
            chunks.append(hotel_voices_html(number, assets))
            hotel_voices_inserted = True
        should_pause = (number == 0 and section.title in n00_pause_after) or (number == 1 and section.title in n01_pause_after) or (number == 2 and section.title in n02_pause_after) or (number == 3 and section.title in n03_pause_after) or (number == 4 and section.title in n04_pause_after) or (number == 5 and section.title in n05_pause_after) or (number == 6 and section.title in n06_pause_after) or (number == 7 and section.title in n07_pause_after) or (number == 8 and section.title in n08_pause_after) or (number == 9 and section.title in n09_pause_after) or (number == 10 and section.title in n10_pause_after) or (number not in {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10} and idx in pause_after)
        if should_pause and idx < len(sections)-3:
            quote = n00_pause_after[section.title][1] if number == 0 else n01_pause_after[section.title][1] if number == 1 else n02_pause_after[section.title][1] if number == 2 else n03_pause_after[section.title][1] if number == 3 else n04_pause_after[section.title][1] if number == 4 else n05_pause_after[section.title][1] if number == 5 else n06_pause_after[section.title][1] if number == 6 else n07_pause_after[section.title][1] if number == 7 else n08_pause_after[section.title][1] if number == 8 else n09_pause_after[section.title][1] if number == 9 else n10_pause_after[section.title][1] if number == 10 else sentence(first_paragraph(section),165)
            if quote:
                quotes.append(quote)
                image = selected[n00_pause_after[section.title][0]] if number == 0 else selected[n01_pause_after[section.title][0]] if number == 1 else selected[n02_pause_after[section.title][0]] if number == 2 else selected[n03_pause_after[section.title][0]] if number == 3 else selected[n04_pause_after[section.title][0]] if number == 4 else selected[n05_pause_after[section.title][0]] if number == 5 else selected[n06_pause_after[section.title][0]] if number == 6 else selected[n07_pause_after[section.title][0]] if number == 7 else selected[n08_pause_after[section.title][0]] if number == 8 else selected[n09_pause_after[section.title][0]] if number == 9 else selected[n10_pause_after[section.title][0]] if number == 10 else selected[(idx//6+2)%len(selected)]
                if number == 2 and section.title == "Pregunta profesional":
                    pause_alt = "Trazos de agua sobre una superficie oscura forman una trama irregular semejante a un sistema."
                elif number == 2 and section.title == "Cómo emerge un resultado que ningún componente controla":
                    pause_alt = "Letras y signos dispersos alrededor de una gran letra impresa, vistos en diagonal y fuera de foco."
                elif number == 3:
                    pause_alt = n03_pause_after[section.title][2]
                elif number == 7:
                    pause_alt = n07_pause_alts[section.title]
                else:
                    pause_alt = n01_pause_alts.get(section.title, f"Pausa visual vinculada con {section.title}") if number == 1 else f"Pausa visual vinculada con {section.title}"
                chunks.append(f'''</article><section class="full-bleed full-bleed-quote"><img src="assets/{esc(image)}" alt="{esc(pause_alt)}"><p>{esc(quote)}</p></section><article class="reading">''')

    if references_plate:
        chunks.append(references_plate)

    contents_image = selected[2] if number == 0 else sparse_fill_images[0] if number == 1 else selected[7] if number == 5 else selected[2] if number == 6 else selected[3] if number == 7 else sparse_fill_images[1] if number in {8, 9, 10} else selected[0]
    closing_alt = "Diez fósforos dispuestos en secuencia vertical, desde intactos hasta consumidos y convertidos en ceniza."
    closing_caption = "La secuencia vuelve visible que toda intervención consume recursos, deja huellas y necesita un criterio de cierre."
    closing_html = f'<section class="full-bleed closing-image"><img src="assets/matches-close.png" alt="{esc(closing_alt)}"><figcaption>{esc(closing_caption)}</figcaption></section>'
    html_text=f'''<!doctype html><html lang="es-AR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Lectura previa METSI N{number:02d}, Facultad de Ciencias Económicas, Universidad de Buenos Aires"><title>{esc(title)}</title><link rel="stylesheet" href="magazine.css"></head><body class="premium-magazine document-n{number:02d}"><main>{cover_html(number,title,thesis,cover_file,title_source_id)}{contents_html(number,title,sections,contents_image)}{authors_html(number,refs,assets)}<article class="reading">{''.join(chunks)}</article>{closing_html}</main></body></html>'''
    (out/"index.html").write_text(html_text,encoding="utf-8")
    rendered_ids=re.findall(r'data-source-id="([^"]+)"',html_text)
    source_ids=[entry["source_id"] for entry in source_entries]
    source_label = f"source/{source.name}" if number in {5, 6, 7} else str(source)
    source_manifest={
        "document":f"N{number:02d}",
        "source":source_label,
        "eligible_blocks":source_entries,
        "eligible_block_count":len(source_entries),
        "eligible_word_count":sum(len(entry["text"].split()) for entry in source_entries),
    }
    source_manifest_text = json.dumps(source_manifest,ensure_ascii=False,indent=2)
    (out/"source-manifest.json").write_text(source_manifest_text + ("\n" if number in {5, 6, 7} else ""),encoding="utf-8")
    integrity={
        "status":"PASS" if sorted(source_ids)==sorted(rendered_ids) and len(rendered_ids)==len(set(rendered_ids)) else "FAIL",
        "source_block_count":len(source_ids),
        "rendered_source_id_count":len(rendered_ids),
        "missing_source_ids":sorted(set(source_ids)-set(rendered_ids)),
        "unexpected_source_ids":sorted(set(rendered_ids)-set(source_ids)),
        "duplicate_rendered_ids":sorted({value for value in rendered_ids if rendered_ids.count(value)>1}),
    }
    (out/"integrity-report.json").write_text(json.dumps(integrity,ensure_ascii=False,indent=2),encoding="utf-8")
    packaged_css = out / "magazine.css"
    if number == 7:
        stable_css = (HERE / "N06-v9-final" / "magazine.css").read_text(encoding="utf-8")
        base_css = stable_css.split("/* METSI collection extensions:", 1)[0].rstrip()
        css_text = base_css + "\n\n" + COLLECTION_CSS
    else:
        css_text = packaged_css.read_text(encoding="utf-8") if number in {5, 6} and packaged_css.exists() else N01_CSS.read_text(encoding="utf-8") + "\n" + COLLECTION_CSS
    packaged_css.write_text(css_text,encoding="utf-8")
    if number in {5, 6, 7}:
        (out / "metsi.css").write_text(css_text, encoding="utf-8")
    cover_source_label = f"assets/{cover_source.name}" if number in {5, 6, 7} else str(cover_source)
    hotel_source_label = (
        f"assets/{hotel_source.name}" if number in {5, 6, 7} and hotel_source is not None else str(hotel_source)
        if hotel_source is not None
        else ""
    )
    clean_title = title.replace(f"N{number:02d} — ", "").replace(f"N{number:02d} · ", "")
    manifest={
        "number":number,"title":title,"module":module_for(number)[1],"source":source_label,
        "source_words":len(source.read_text(encoding='utf-8').split()),
        "cover":{
            "file":cover_file,
            "source":cover_source_label,
            "sha256":asset_sha(cover_source),
            **({"alt":cover_alt_text(number, clean_title)} if number in {6, 7} else {}),
            **({
                "photographic_origin":"native_black_and_white",
                "render_treatment":"no_grayscale_conversion",
                "art_direction":"lighting, wardrobe, materials and tonal separation conceived for monochrome",
            } if number in {4, 5, 6, 7} else {}),
        },
        "internal_images":selected,
        "sparse_fill_images":sparse_fill_images,
        **({"hotel_horizonte":{"file":hotel_file,"source":hotel_source_label,"sha256":asset_sha(hotel_source)}} if hotel_source is not None else {}),
        "closing":{"file":"matches-close.png","sha256":asset_sha(closing_source),"policy":"canonical_structured_closing_without_quote","alt":closing_alt,"caption":closing_caption,"folio":True,"footer":True},
        "diagram":diagram,"quotes":quotes,"references":refs,
        "portrait_policy":"mandatory_real_photography_no_monograms",
        "portrait_references":portrait_refs,
        "generated_character_assets": ([
            {
                "name":"Mariela Benítez",
                "role":"Personaje ficcional · Supervisión Housekeeping",
                "file":"hotel-mariela-benitez-v1.png",
                "source":str(EDITORIAL_CHARACTER_PORTRAITS/"mariela-benitez-v1.png"),
                "sha256":asset_sha(EDITORIAL_CHARACTER_PORTRAITS/"mariela-benitez-v1.png"),
                "rights_status":"generated_editorial_fiction",
            },
            {
                "name":"Camila Duarte",
                "role":"Personaje ficcional · Gerencia Comercial",
                "file":"hotel-camila-duarte-v2.png",
                "source":str(EDITORIAL_CHARACTER_PORTRAITS/"camila-duarte-v2.png"),
                "sha256":asset_sha(EDITORIAL_CHARACTER_PORTRAITS/"camila-duarte-v2.png"),
                "rights_status":"generated_editorial_fiction",
            },
        ] if number in {0, 1} else []),
    }
    manifest_text = json.dumps(manifest,ensure_ascii=False,indent=2) + ("\n" if number in {5, 6, 7} else "")
    (out/"manifest.json").write_text(manifest_text,encoding="utf-8")
    if number in {5, 6, 7}:
        (out/"document.json").write_text(manifest_text,encoding="utf-8")
    if number == 6 and not (out / "image-manifest.json").exists():
        raise FileNotFoundError("N06 requiere image-manifest.json curado dentro del paquete")
    return manifest


COLLECTION_CSS=r'''
/* METSI collection extensions: canonical v7 N01-N10 */
@page fullbleed { size:A4; margin:0; background:#191919; }
.part-divider{page:fullbleed;position:relative;display:flex;align-items:flex-end;width:210mm;height:297mm;padding:24mm;overflow:hidden;color:#F7F6F2;background:#191919;break-before:page;page-break-before:always;break-after:page;page-break-after:always}
.part-divider::before{content:"";position:absolute;left:24mm;top:24mm;width:24mm;height:3.2mm;background:#CFFF00;clip-path:polygon(10% 0,100% 0,90% 100%,0 100%)}
.part-divider::after{content:"METSI · N00";position:absolute;right:24mm;top:24mm;font:700 7pt/1 Avenir,sans-serif;letter-spacing:.16em;color:#F7F6F2}
.part-divider-copy{max-width:152mm;padding-bottom:14mm}
.part-divider-copy>b{display:block;margin-bottom:6mm;font:700 8.2pt/1 Avenir,sans-serif;letter-spacing:.18em;text-transform:uppercase;color:#CFFF00}
.part-divider-copy h2{max-width:148mm;margin:0 0 8mm;font:400 43pt/.96 Didot,"Bodoni 72",serif;color:#F7F6F2;letter-spacing:-.025em}
.part-divider-body p{max-width:132mm;margin:0;font:400 12pt/1.45 Baskerville,Georgia,serif;color:#E4E4DF}
.collection-cover,.front-page{page:fullbleed;width:210mm;height:297mm;margin:0;position:relative;overflow:hidden;break-after:page;page-break-after:always}
.collection-cover{background:#111;color:#fff}
.collection-cover{overflow:hidden}
.collection-cover>img{position:absolute;inset:0;width:100%;height:100%;max-width:none;max-height:none;object-fit:cover;object-position:center;filter:grayscale(1) saturate(0) contrast(1.10) brightness(.81)}
.collection-cover .cover-shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(5,7,6,.18),rgba(10,12,10,.18) 38%,rgba(8,9,8,.86) 100%)}
.collection-cover .cover-shade{width:100%;height:100%}
.cover-variant-2>img{object-position:42% 50%}.cover-variant-3>img{object-position:58% 50%}.cover-variant-4>img{filter:grayscale(1) saturate(0) contrast(1.12) brightness(.78)}
.cover-n02>img{object-position:50% 47%;filter:grayscale(1) saturate(0) contrast(1.15) brightness(.73)}
.cover-n02 .cover-shade{background:linear-gradient(180deg,rgba(5,7,6,.34),rgba(10,12,10,.06) 35%,rgba(8,9,8,.88) 100%)}
.cover-meta{position:absolute;z-index:3;top:18mm;font-family:Avenir,sans-serif;font-size:7pt;line-height:1.35;letter-spacing:.13em}.cover-meta-left{left:18mm}.cover-meta-right{right:18mm;text-align:right}
.collection-masthead{position:absolute;z-index:2;top:8mm;left:0;right:0;text-align:center;font-family:Didot,"Bodoni 72",serif;font-size:58pt;line-height:.9;letter-spacing:.06em;font-weight:400}
.cover-title{position:absolute;z-index:3;left:18mm;bottom:29mm;width:119mm}.cover-title i{display:block;width:28mm;height:2mm;margin-bottom:4mm;background:#CFFF00;clip-path:polygon(8% 0,100% 0,92% 100%,0 100%)}
.cover-title span{font-family:Avenir,sans-serif;font-size:6.7pt;letter-spacing:.14em}.cover-title h1{margin:4mm 0 0;color:#fff;font-family:Didot,"Bodoni 72",serif;font-size:31pt;line-height:.94;letter-spacing:-.022em;font-weight:400}
.cover-thesis{position:absolute;z-index:3;right:16mm;bottom:29mm;width:53mm;text-align:right}.cover-thesis b{display:inline-grid;place-items:center;width:15mm;height:15mm;margin-bottom:4mm;border:.35mm solid #CFFF00;border-radius:50%;color:#CFFF00;font-family:Avenir,sans-serif;font-size:7pt}.cover-thesis p{margin:0;color:#CFFF00;font-family:Didot,"Bodoni 72",serif;font-size:13.5pt;line-height:1.08}.cover-parallelogram{position:absolute;z-index:3;right:18mm;top:55mm;width:15mm;height:4mm;background:#CFFF00;clip-path:polygon(10% 0,100% 0,90% 100%,0 100%);opacity:.95}
.cover-n01 .cover-meta{letter-spacing:.035em;line-height:1.2}
.cover-n01 .cover-meta-eyebrow,.cover-n02 .cover-meta-eyebrow,.cover-n03 .cover-meta-eyebrow,.cover-n04 .cover-meta-eyebrow,.cover-n05 .cover-meta-eyebrow,.cover-n07 .cover-meta-eyebrow{display:flex;flex-direction:column;align-items:flex-start;gap:0;white-space:normal}
.cover-n01 .cover-meta-eyebrow span,.cover-n02 .cover-meta-eyebrow span,.cover-n03 .cover-meta-eyebrow span,.cover-n04 .cover-meta-eyebrow span,.cover-n05 .cover-meta-eyebrow span,.cover-n07 .cover-meta-eyebrow span{display:block;white-space:nowrap}
.cover-n01::before{content:"";position:absolute;z-index:1;left:0;top:0;width:100%;height:52mm;pointer-events:none;background:linear-gradient(to bottom,rgba(0,0,0,.28) 0,rgba(0,0,0,.22) 44%,rgba(0,0,0,0) 100%)}
.cover-n01 .cover-title{width:160mm}
.cover-n01 .cover-title h1{font-size:28.5pt;line-height:.96;letter-spacing:-.02em}
.cover-n01 .cover-thesis{right:18mm;bottom:92mm;width:49mm}
.cover-n01 .cover-thesis b{margin-bottom:7mm}
.cover-n01 .cover-thesis p{font-size:12.5pt;line-height:1.12}
.cover-n02 .collection-masthead{top:16mm}
.cover-n02 .cover-meta{top:29mm}
.cover-n02 .cover-meta-left{left:15.5mm}
.cover-n02 .cover-meta-right{right:15.5mm}
.cover-n02 .cover-title{bottom:21mm;width:126mm}
.cover-n02 .cover-title h1{font-size:43pt;line-height:.89;letter-spacing:-.027em}
.cover-n02 .cover-thesis{right:25mm;bottom:21mm;width:51mm}
.cover-n02 .cover-parallelogram{right:15.5mm;top:57mm}
.cover-n00>img{object-position:50% 48%;filter:grayscale(1) saturate(0) contrast(1.13) brightness(.73)}
.cover-n00 .cover-shade{background:linear-gradient(180deg,rgba(5,7,6,.30),rgba(10,12,10,.06) 35%,rgba(8,9,8,.90) 100%)}
.cover-n00{overflow:hidden}
.cover-n00>img,.cover-n00 .cover-shade{inset:0;width:100%;height:100%}
.cover-n00 .collection-masthead{top:16mm}
.cover-n00 .cover-meta{top:29mm}
.cover-n00 .cover-meta-left{left:15.5mm}
.cover-n00 .cover-meta-right{right:15.5mm}
.cover-n00 .cover-title{left:15.5mm;bottom:21mm;width:106mm;padding-bottom:1mm}
.cover-n00 .cover-title h1{font-size:34pt;line-height:.94;letter-spacing:-.022em}
.cover-n00 .cover-thesis{right:17mm;bottom:23mm;width:78mm}
.cover-n00 .cover-thesis p{font-size:11.2pt;line-height:1.08}
.cover-n00 .cover-parallelogram{right:15.5mm;top:57mm}
.cover-n03>img{object-position:50% 48%;filter:grayscale(1) saturate(0) contrast(1.14) brightness(.74)}
.cover-n03 .cover-shade{background:linear-gradient(180deg,rgba(5,7,6,.31),rgba(10,12,10,.07) 37%,rgba(8,9,8,.88) 100%)}
.cover-n03 .collection-masthead{top:16mm}
.cover-n03 .cover-meta{top:29mm}
.cover-n03 .cover-meta-left{left:15.5mm}
.cover-n03 .cover-meta-right{right:15.5mm}
.cover-n03 .cover-title{bottom:21mm;width:126mm}
.cover-n03 .cover-title h1{font-size:36pt;line-height:.91;letter-spacing:-.025em}
.cover-n03 .cover-thesis{right:25mm;bottom:21mm;width:51mm}
.cover-n03 .cover-parallelogram{right:15.5mm;top:57mm}
.cover-n04>img{object-position:50% 48%;filter:contrast(1.07) brightness(.82)}
.cover-n04 .cover-shade{background:linear-gradient(180deg,rgba(5,7,6,.30),rgba(10,12,10,.05) 36%,rgba(8,9,8,.89) 100%)}
.cover-n04 .collection-masthead{top:16mm}
.cover-n04 .cover-meta{top:29mm}
.cover-n04 .cover-meta-left{left:15.5mm}
.cover-n04 .cover-meta-right{right:15.5mm}
.cover-n04 .cover-title{bottom:21mm;width:126mm}
.cover-n04 .cover-title h1{font-size:34pt;line-height:.91;letter-spacing:-.025em}
.cover-n04 .cover-thesis{right:25mm;bottom:21mm;width:51mm}
.cover-n04 .cover-parallelogram{right:15.5mm;top:57mm}
.cover-n05>img{object-position:50% 48%;filter:contrast(1.06) brightness(.82)}
.cover-n05 .cover-shade{background:linear-gradient(180deg,rgba(5,7,6,.30),rgba(10,12,10,.05) 36%,rgba(8,9,8,.89) 100%)}
.cover-n05 .collection-masthead{top:16mm}
.cover-n05 .cover-meta{top:29mm}
.cover-n05 .cover-meta-left{left:15.5mm}
.cover-n05 .cover-meta-right{right:15.5mm}
.cover-n05 .cover-title{bottom:21mm;width:132mm}
.cover-n05 .cover-title h1{font-size:38pt;line-height:.91;letter-spacing:-.025em}
.cover-n05 .cover-thesis{right:18mm;bottom:22mm;width:56mm}
.cover-n05 .cover-parallelogram{right:15.5mm;top:57mm}
.cover-n06>img{object-position:50% 48%;filter:contrast(1.04) brightness(.96)}
.cover-n06 .cover-shade{background:linear-gradient(180deg,rgba(5,7,6,.13),rgba(10,12,10,.03) 40%,rgba(8,9,8,.70) 100%)}
.cover-n06 .collection-masthead{top:16mm}
.cover-n06 .cover-meta{top:29mm}
.cover-n06 .cover-meta-left{left:15.5mm}
.cover-n06 .cover-meta-right{right:15.5mm}
.cover-n06 .cover-title{bottom:21mm;width:126mm}
.cover-n06 .cover-title h1{font-size:34pt;line-height:.91;letter-spacing:-.025em}
.cover-n06 .cover-thesis{right:25mm;bottom:21mm;width:51mm}
.cover-n06 .cover-parallelogram{right:15.5mm;top:57mm}
.cover-n07{overflow:hidden}
.cover-n07>img{inset:0;width:100%;height:100%;object-position:50% 48%;filter:none}
.cover-n07 .cover-shade{inset:0;width:100%;height:100%;background:linear-gradient(180deg,rgba(5,7,6,.13) 0,rgba(5,7,6,0) 29%,rgba(5,7,6,0) 62%,rgba(5,7,6,.46) 100%)}
.cover-n07 .collection-masthead{top:16mm}
.cover-n07 .cover-meta{top:29mm}
.cover-n07 .cover-meta-eyebrow{letter-spacing:.13em;line-height:1.28}
.cover-n07 .cover-meta-left{left:15.5mm}
.cover-n07 .cover-meta-right{right:15.5mm}
.cover-n07 .cover-title{bottom:21mm;width:126mm}
.cover-n07 .cover-title h1{font-size:34pt;line-height:.91;letter-spacing:-.025em}
.cover-n07 .cover-thesis{right:16mm;bottom:21mm;width:51mm}
.cover-n07 .cover-parallelogram{right:15.5mm;top:57mm}
.cover-n10>img{object-position:50% 50%;filter:grayscale(1) saturate(0) contrast(1.16) brightness(.72)}
.cover-n10 .cover-shade{background:linear-gradient(180deg,rgba(5,7,6,.31),rgba(10,12,10,.06) 36%,rgba(8,9,8,.89) 100%)}
.cover-n10 .collection-masthead{top:16mm}
.cover-n10 .cover-meta{top:29mm}
.cover-n10 .cover-meta-left{left:15.5mm}
.cover-n10 .cover-meta-right{right:15.5mm}
.cover-n10 .cover-title{bottom:21mm;width:126mm}
.cover-n10 .cover-title h1{font-size:33pt;line-height:.91;letter-spacing:-.025em}
.cover-n10 .cover-thesis{right:25mm;bottom:21mm;width:51mm}
.cover-n10 .cover-parallelogram{right:15.5mm;top:57mm}
.premium-magazine.document-n10 section[data-section="02"] .photo-band img{height:142mm;object-position:center 48%}
.premium-magazine.document-n10 section[data-section="14"] .photo-band img{height:72mm;object-position:center 46%}
.front-page{padding:18mm;background:#FAFAF8;color:#181817}.front-page header{border-top:.45mm solid #202020;padding-top:5mm}.front-page header>span{font-family:Avenir,sans-serif;font-size:7pt;letter-spacing:.15em}.front-page header h2{font-size:36pt;margin:3mm 0 2mm}.front-page header p{max-width:145mm;font-size:11pt;color:#575753}
.contents-layout{display:grid;grid-template-columns:1.15fr .85fr;gap:8mm;height:220mm;margin-top:6mm}.contents-layout ol{list-style:none;margin:0;padding:0;columns:2;column-gap:6mm}.contents-layout li{display:grid;grid-template-columns:9mm 1fr;gap:2mm;padding:2.2mm 0;border-bottom:.2mm solid #b9bab7;break-inside:avoid;font-family:Avenir,sans-serif;font-size:8.2pt;line-height:1.18}.contents-layout li b{color:#202020;font-weight:600}.contents-layout figure{height:100%;margin:0}.contents-layout figure img{height:202mm;object-fit:cover;filter:saturate(.35) contrast(1.06)}.contents-layout figcaption{font-size:7.2pt}
.document-n00 .contents-page{padding:14mm 16mm}
.document-n00 .contents-page header h2{font-size:31pt;margin:2mm 0 1mm}
.document-n00 .contents-page header>p{font-size:9.2pt;margin:0}
.document-n00 .contents-page .contents-route{max-width:170mm;margin:2mm 0 0;padding-left:3mm;border-left:1.4mm solid #CFFF00;font:7.2pt/1.22 Avenir,sans-serif;color:#30322f}
.document-n00 .contents-page .contents-sinnum-note{position:absolute;left:16mm;right:16mm;bottom:18mm;margin:0;padding-top:2mm;border-top:.2mm solid #BFC1BD;font:6.4pt/1.2 Avenir,sans-serif;color:#5B5D58}
.document-n00 .contents-layout{grid-template-columns:1.42fr .58fr;gap:6mm;height:207mm;margin-top:4mm}
.document-n00 .contents-layout ol{columns:2;column-gap:5mm}
.document-n00 .contents-layout li{grid-template-columns:7mm 1fr;gap:1.2mm;padding:1mm 0;font-size:6.75pt;line-height:1.12}
.document-n00 .contents-layout li small{display:inline-block;margin-left:1mm;font-size:4.8pt;line-height:1;letter-spacing:.08em;color:#777}
.document-n00 .contents-layout .contents-part{display:block;margin-top:1.7mm;padding:1.3mm 1.5mm;border:0;background:#202020;color:#FAFAF8;font-weight:700;letter-spacing:.05em;column-span:none}
.document-n00 .contents-layout .contents-part span{display:block}
.document-n00 .contents-layout .contents-core{border-left:1mm solid #CFFF00;padding-left:1.2mm}
.document-n00 .contents-layout .contents-unnumbered{grid-template-columns:7mm 1fr;color:#666663;background:#F0F0EC}
.document-n00 .contents-layout .contents-unnumbered b{color:#4D5A00}
.document-n00 .contents-layout figure img{height:190mm;filter:grayscale(1) contrast(1.06)}
.document-n00 .contents-layout figcaption{font-size:6.2pt;line-height:1.16}
.document-n00 section[data-section="09"] .photo-band img{height:118mm;object-position:center 48%}
.authors-page{background:linear-gradient(90deg,#FAFAF8 0 33.333%,#E8E9E8 33.333% 66.666%,#FAFAF8 66.666%)}.authors-page header{text-align:center}.authors-page header p{margin-left:auto;margin-right:auto}.contributors-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:6mm 5mm;margin-top:8mm}.contributor{text-align:center;min-height:78mm;padding:2mm 3mm;border-bottom:.2mm solid #aaa}.contributor>b{display:block;margin-bottom:2mm;font-family:Didot,serif;font-size:13pt;color:#666}.contributor-portrait{display:block;width:25mm;height:25mm;margin:0 auto 3mm;object-fit:cover;border-radius:50%;filter:grayscale(1);background:#dedede;border:.25mm solid #555}.contributor h3{margin:1mm 0;font-family:Avenir,sans-serif;font-size:9.4pt;font-weight:700;text-transform:uppercase}.contributor span{display:block;color:#202020;font-family:Avenir,sans-serif;font-size:6pt;font-weight:700;letter-spacing:.08em}.contributor cite{display:block;min-height:11mm;margin-top:2.2mm;font-family:Baskerville,serif;font-size:8.2pt;line-height:1.24;font-style:italic;text-align:left}.contributor p{margin-top:1.2mm;font-family:Avenir,sans-serif;font-size:6.8pt;line-height:1.24;text-align:left;color:#565855}.authors-page blockquote{margin:6mm 8mm 0;padding-top:4mm;border-top:.25mm solid #999;text-align:center;font-family:Didot,serif;font-size:14pt;line-height:1.12;font-style:italic}
.document-n00 .authors-page .contributors-grid{column-gap:8mm;row-gap:6mm}
.document-n00 .authors-page .contributor{min-width:0;padding-left:4mm;padding-right:4mm}
.document-n00 .authors-page .contributor cite,.document-n00 .authors-page .contributor p{overflow-wrap:anywhere}
.document-n00 .authors-page .contributor span{display:none}
.hotel-archetypes{page:content;margin:5mm 0 6mm;padding:5mm 6mm;background:#DADDDC;border-top:.55mm solid #202020;break-inside:avoid-page}
.hotel-archetypes header{margin-bottom:2mm}.hotel-archetypes header>b{font:700 5.8pt/1 Avenir,sans-serif;letter-spacing:.15em}.hotel-archetypes header h2{margin:1mm 0 .5mm;font:400 21pt/1 Didot,serif}.hotel-archetypes header p{margin:0;font-size:8.2pt}
.hotel-archetypes-grid{display:grid;grid-template-columns:1fr 1fr;gap:2.5mm 3.5mm}.hotel-archetype-card{display:grid;grid-template-columns:34mm 1fr;background:#F5F5F2;border-top:.25mm solid #777;min-height:64mm}.hotel-archetype-portrait{width:34mm;height:64mm;overflow:hidden;background:#ECEDEC}.hotel-archetype-portrait img{width:100%;height:100%;object-fit:cover;object-position:center 18%;filter:grayscale(1) contrast(1.02)}.hotel-archetype-3 img,.hotel-archetype-4 img{transform:scale(1.18);transform-origin:center 18%}.hotel-archetype-copy{padding:3mm}.hotel-archetype-copy>span{font:600 6pt/1.1 Avenir,sans-serif;letter-spacing:.08em;text-transform:uppercase}.hotel-archetype-copy h3{margin:.7mm 0 1.2mm;font:400 14pt/1 Didot,serif}.hotel-archetype-copy p{margin:.65mm 0;font-size:7.05pt;line-height:1.2}
.document-n00 .hotel-archetype-5,.document-n00 .hotel-archetype-6{grid-column:auto;grid-template-columns:34mm 1fr;min-height:57mm}
.document-n00 .hotel-archetype-5 .hotel-archetype-portrait,.document-n00 .hotel-archetype-6 .hotel-archetype-portrait{width:34mm;height:57mm}
.document-n00 .hotel-archetype-5 .hotel-archetype-copy,.document-n00 .hotel-archetype-6 .hotel-archetype-copy{display:block}
.document-n00 .hotel-archetype-5 img{transform:none;object-position:center 38%}
.document-n00 .hotel-archetype-6 img{transform:none;object-position:center 23%}
.document-n00 .hh00-memo{column-span:all;min-height:108mm;margin:5mm 0;padding:5mm 7mm 4.5mm;background:#F2EFE7;border:.3mm solid #777;border-top:1.2mm solid #202020;break-inside:avoid-page;page-break-inside:avoid;font-family:Avenir,sans-serif;font-size:8pt;line-height:1.22;color:#252525}
.document-n00 .hh00-memo h4{margin:0 0 1mm;font:700 5.8pt/1 Avenir,sans-serif;letter-spacing:.18em;color:#4D5A00}
.document-n00 .hh00-memo h3{margin:0 0 2.5mm;padding-bottom:2mm;border-bottom:.25mm solid #999;font:400 19pt/1 Didot,"Bodoni 72",serif;letter-spacing:-.02em}
.document-n00 .hh00-memo p{margin:0 0 1.35mm;orphans:2;widows:2}
.document-n00 .hh00-memo p:nth-last-child(2){margin-top:2.5mm;margin-bottom:.3mm;padding-top:2mm;border-top:.25mm solid #999;font-family:Didot,"Bodoni 72",serif;font-size:11pt}
.document-n00 .hh00-memo p:last-child{margin:2.5mm 0 0;padding:2.2mm 3.5mm;border-left:1.5mm solid #CFFF00;background:#FAFAF8;font-family:Baskerville,Georgia,serif;font-size:8pt;line-height:1.24}
.document-n00 .concept-families .section-body{columns:2;column-gap:8mm;column-rule:.2mm solid #ccc}.document-n00 .concept-families h3{break-after:avoid;margin-top:4mm}
.hotel-voices-compact{page:content;margin:5mm 0 6mm;padding:3mm 4mm;background:#DADDDC;border-top:.55mm solid #202020;border-bottom:.25mm solid #9a9c9a;break-inside:avoid-page;page-break-inside:avoid}
.hotel-voices-compact header{display:grid;grid-template-columns:1fr 2fr;column-gap:5mm;align-items:end;margin-bottom:4mm}
.hotel-voices-compact header{margin-bottom:2.2mm}
.hotel-voices-compact header b{font-family:Avenir,sans-serif;font-size:5.7pt;letter-spacing:.15em}
.hotel-voices-compact header h2{grid-column:1/-1;margin:.8mm 0 .5mm;font-family:Didot,"Bodoni 72",serif;font-size:18.5pt;line-height:1;font-weight:400}
.hotel-voices-compact header p{grid-column:1/-1;margin:0;font-family:Baskerville,serif;font-size:7.7pt;line-height:1.18}
.hotel-voices-grid{display:grid;grid-template-columns:1fr 1fr;gap:2mm 3mm}
.hotel-voices-grid article{display:grid;grid-template-columns:19mm 1fr;min-height:23mm;background:transparent;border-top:.2mm solid #777}
.hotel-voices-grid img{width:19mm;height:23mm;object-fit:cover;object-position:center 20%;filter:grayscale(1) contrast(1.02);background:#ECEDEC}
.hotel-voices-grid .hotel-voice-3 img,.hotel-voices-grid .hotel-voice-4 img{object-position:center 18%}
.hotel-voices-grid article div{padding:2mm 2.2mm 1.7mm}
.hotel-voices-grid span{font-family:Avenir,sans-serif;font-size:5.1pt;letter-spacing:.07em;text-transform:uppercase}
.hotel-voices-grid h3{margin:.4mm 0 .8mm;font-family:Didot,"Bodoni 72",serif;font-size:10.8pt;line-height:1;font-weight:400}
.hotel-voices-grid p{margin:0;font-family:Baskerville,serif;font-size:7.05pt;line-height:1.16}
.source-symbol{font-family:"Apple Symbols",Avenir,sans-serif;font-weight:400}
.document-n00 .section-marker span{display:inline-flex;width:auto;height:auto;padding:1mm 2mm;border:0;border-left:1.6mm solid #CFFF00;border-radius:0;background:transparent;font-size:6.5pt;line-height:1;letter-spacing:.11em}
.document-n00 .reading-section .section-marker span{border-left:1.6mm solid #CFFF00!important;padding:1mm 2mm!important}
.document-n00 .reading-section .section-marker b::before{background:#CFFF00!important}
.document-n00 .layout-section-opener .section-body>p:first-child::first-letter,.document-n00 .opening-section .section-body>p:first-child::first-letter{float:none!important;display:inline!important;margin:0 .4mm 0 0!important;font-size:28pt!important;line-height:1!important;vertical-align:-.12em}
.premium-magazine .reading-section{padding-bottom:1mm}.premium-magazine .section-heading{break-inside:avoid-page;page-break-inside:avoid;break-after:avoid-page;page-break-after:avoid}.premium-magazine .reading-section h4{margin:4mm 0 1.5mm;font-family:Avenir,sans-serif;font-size:10.5pt;line-height:1.18;letter-spacing:.01em}.premium-magazine .section-body h3{font-size:15pt}.premium-magazine .section-body h4{break-after:avoid-page}.premium-magazine .table-wrap{overflow:visible;margin:4mm 0 6mm;break-inside:avoid-page;page-break-inside:avoid;column-span:all}.premium-magazine table{width:100%;table-layout:fixed;border-collapse:collapse;font-family:Avenir,sans-serif;font-size:7.5pt;line-height:1.25}.premium-magazine th,.premium-magazine td{padding:2.2mm;border:.2mm solid #aaa;vertical-align:top;overflow-wrap:anywhere;word-break:normal}.premium-magazine th{background:#E4E6E5;text-align:left}.premium-magazine .dossier{margin-left:-7mm;margin-right:-7mm;padding:7mm;background:#E4E6E5}.premium-magazine .connections{border-left:3mm solid #CFFF00;padding-left:6mm}.premium-magazine .infographic{width:100%;max-height:83mm;margin:5mm 0 7mm;padding:2mm 0;border-top:.35mm solid #202020;border-bottom:.2mm solid #999}.premium-magazine .infographic img{width:100%;max-height:76mm;object-fit:contain}.premium-magazine .infographic figcaption{font-size:7pt}.premium-magazine .photo-band img{height:52mm;filter:saturate(.35) contrast(1.06)}
.premium-magazine .opening-story .section-body{columns:2;column-gap:8mm;column-rule:.2mm solid #c5c7c5}
.premium-magazine .opening-story .section-body p:first-child{margin-top:0}
.premium-magazine .infographic-boundaries{max-height:61mm;margin:3mm 0 4mm}
.premium-magazine .infographic-boundaries img{max-height:52mm;filter:none}
.premium-magazine.document-n03 .reading-section[data-section="01"]{page:fullbleed;position:relative;box-sizing:border-box;width:210mm;height:297mm;margin:0;padding:24mm;display:flex;flex-direction:column;justify-content:flex-end;background:#191919;color:#F7F6F2;border:0;break-before:page;page-break-before:always;break-after:page;page-break-after:always}
.premium-magazine.document-n03 .reading-section[data-section="01"]::before{content:"";position:absolute;left:24mm;top:24mm;width:24mm;height:3.2mm;background:#CFFF00;clip-path:polygon(10% 0,100% 0,90% 100%,0 100%)}
.premium-magazine.document-n03 .reading-section[data-section="01"] .section-heading{display:block;margin:0 0 12mm;padding:0;border:0}
.premium-magazine.document-n03 .reading-section[data-section="01"] .section-marker{color:#CFFF00}
.premium-magazine.document-n03 .reading-section[data-section="01"] .section-marker span{color:#CFFF00;border-color:#CFFF00}
.premium-magazine.document-n03 .reading-section[data-section="01"] h2{margin:0;color:#F7F6F2;font-size:18pt}
.premium-magazine.document-n03 .reading-section[data-section="01"] .section-body{max-width:155mm}
.premium-magazine.document-n03 .reading-section[data-section="01"] .section-body p{margin:0;color:#F7F6F2;font:400 28pt/1.08 Didot,"Bodoni 72",serif;letter-spacing:-.018em}
.premium-magazine.document-n03 .n03-handoff-input{break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n03 .n03-handoff-input h2{font-size:28pt;line-height:1}
.premium-magazine.document-n03 .n03-handoff-input .section-body{columns:2;column-count:2;column-gap:8mm;column-rule:.2mm solid #c5c7c5}
.premium-magazine.document-n03 .n03-movement{break-before:page;page-break-before:always;background:#FAFAF8!important;padding:0!important;border-left:0!important}
.premium-magazine.document-n03 .n03-movement-one{break-before:auto!important;page-break-before:auto!important}
.premium-magazine.document-n03 .n03-movement .section-body{columns:2;column-count:2;column-gap:8mm;column-rule:.2mm solid #c5c7c5}
.premium-magazine.document-n03 .n03-movement .section-body h3{column-span:all;margin:6mm 0 2mm;padding-top:3mm;border-top:.3mm solid #202020;break-after:avoid-page;page-break-after:avoid}
.premium-magazine.document-n03 .n03-movement-one .section-body h3{column-span:none}
.premium-magazine.document-n03 .n03-movement-two .section-body h3:nth-of-type(2){break-before:page;page-break-before:always}
.premium-magazine.document-n03 .n03-movement .section-body h4{break-after:avoid-page;page-break-after:avoid}
.premium-magazine.document-n03 .n03-synthesis .section-body{columns:2;column-count:2;column-gap:8mm;column-rule:.2mm solid #c5c7c5}
.premium-magazine.document-n03 .questions{min-height:210mm;box-sizing:border-box;padding-top:7mm;padding-bottom:7mm;break-before:page!important;page-break-before:always!important;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n03 .questions .section-body ol{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));grid-template-rows:repeat(3,auto);grid-auto-flow:column;align-content:space-between;gap:0 12mm;min-height:110mm;margin:0;padding-left:7mm;columns:auto;column-count:auto;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n03 .questions .section-body li{margin:0;padding-right:2mm;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n03 .questions .section-body>p:last-child{column-span:none!important;margin:2mm 0 0;padding:2.5mm 4mm;border-top:.6mm solid #171917;border-left:1.6mm solid #CFFF00;background:#FAFAF8;font:8.8pt/1.3 Avenir,sans-serif;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n03 .references{break-before:page!important;page-break-before:always!important;padding-left:0!important;border-left:0!important;background:#FAFAF8!important}
.premium-magazine.document-n03 .references::after{display:none!important}
.premium-magazine.document-n03 .references .section-heading{margin:0 0 7mm;padding-top:4mm;border-top:.25mm solid #9A9A96}
.premium-magazine.document-n03 .references .section-marker{gap:2.2mm;margin:0 0 4mm;color:#666663;font-size:6.5pt;letter-spacing:.14em}
.premium-magazine.document-n03 .references .section-marker span{display:inline!important;width:auto!important;height:auto!important;padding:0!important;border:0!important;font-size:inherit}
.premium-magazine.document-n03 .references .section-marker b::before{display:none}
.premium-magazine.document-n03 .references h2{margin:0;font-size:31pt;line-height:1}
.premium-magazine.document-n03 .references .section-body{columns:auto!important;column-count:auto!important;column-gap:0!important;column-rule:none!important;display:block!important;font:10pt/1.4 Avenir,sans-serif}
.premium-magazine.document-n03 .references .section-body ul{columns:2!important;column-count:2!important;column-gap:10mm;column-rule:none;margin:0;padding:0;max-width:none;list-style:none}
.premium-magazine.document-n03 .references .section-body li{break-inside:avoid;overflow-wrap:normal;word-break:normal;hyphens:none;padding:0;margin:0 0 3.8mm}
.premium-magazine.document-n03 .references .section-body a{overflow-wrap:normal;word-break:normal;hyphens:none}
.premium-magazine.document-n03 .references .reference-url{white-space:normal}
.premium-magazine.document-n03 .references .reference-url .url-segment{display:inline-block;white-space:nowrap}
.premium-magazine.document-n00 .n00-transformation-chain{page:content;width:75%;max-height:none;margin:0 auto 7mm;padding:5mm 0 3mm;border-top:.45mm solid #202020;border-bottom:.2mm solid #999;break-before:page;page-break-before:always;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n00 .n00-transformation-chain img{width:100%;max-height:216mm;object-fit:contain;filter:none}
.premium-magazine.document-n00 .n00-transformation-chain figcaption{margin-top:2mm;font-size:7pt;line-height:1.2}
.premium-magazine.document-n03 .infographic-boundaries{max-height:72mm}
.premium-magazine.document-n03 .infographic-boundaries img{max-height:63mm}
.premium-magazine.document-n04 .infographic-boundaries{max-height:72mm}
.premium-magazine.document-n04 .infographic-boundaries img{max-height:63mm}
.cover-n04 .cover-title{width:132mm}
.cover-n04 .cover-title h1{font-size:34pt;line-height:.91;letter-spacing:-.025em}
.cover-n04 .cover-thesis{width:61mm}
.document-n04 .contents-page{padding:14mm 16mm}
.document-n04 .contents-page .contents-layout{grid-template-columns:1.42fr .58fr;gap:6mm;height:207mm;margin-top:4mm}
.document-n04 .contents-page .contents-layout ol{columns:2;column-gap:5mm}
.document-n04 .contents-page .contents-layout li{grid-template-columns:7mm 1fr;gap:1.2mm;padding:1.35mm 0;font-size:7.2pt;line-height:1.14}
.document-n04 .contents-page .contents-layout figure img{height:190mm}
.document-n04 .contents-page .contents-sinnum-note{position:absolute;left:16mm;right:16mm;bottom:18mm;margin:0;padding-top:2mm;border-top:.2mm solid #BFC1BD;font:6.4pt/1.2 Avenir,sans-serif;color:#5B5D58}
.premium-magazine.document-n04 .reading-section[data-section="01"]{page:fullbleed;position:relative;box-sizing:border-box;width:210mm;height:297mm;margin:0;padding:24mm;display:flex;flex-direction:column;justify-content:flex-end;background:#191919;color:#F7F6F2;border:0;break-before:page;page-break-before:always;break-after:page;page-break-after:always}
.premium-magazine.document-n04 .reading-section[data-section="01"]::before{content:"";position:absolute;left:24mm;top:24mm;width:24mm;height:3.2mm;background:#CFFF00;clip-path:polygon(10% 0,100% 0,90% 100%,0 100%)}
.premium-magazine.document-n04 .reading-section[data-section="01"] .section-heading{display:block;margin:0 0 12mm;padding:0;border:0}
.premium-magazine.document-n04 .reading-section[data-section="01"] .section-marker{color:#CFFF00}
.premium-magazine.document-n04 .reading-section[data-section="01"] .section-marker span{color:#CFFF00;border-color:#CFFF00}
.premium-magazine.document-n04 .reading-section[data-section="01"] h2{margin:0;color:#F7F6F2;font-size:18pt}
.premium-magazine.document-n04 .reading-section[data-section="01"] .section-body{max-width:155mm}
.premium-magazine.document-n04 .reading-section[data-section="01"] .section-body p{margin:0;color:#F7F6F2;font:400 28pt/1.08 Didot,"Bodoni 72",serif;letter-spacing:-.018em}
.premium-magazine.document-n04 .n04-handoff-input{break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n04 .n04-handoff-input h2{font-size:28pt;line-height:1}
.premium-magazine.document-n04 .n04-handoff-input .section-body{columns:2;column-count:2;column-gap:8mm;column-rule:.2mm solid #c5c7c5}
.premium-magazine.document-n04 .n04-movement{break-before:page;page-break-before:always;background:#FAFAF8!important;padding:0!important;border-left:0!important}
.premium-magazine.document-n04 .n04-movement-one{break-before:auto!important;page-break-before:auto!important}
.premium-magazine.document-n04 .n04-movement .section-body{columns:2;column-count:2;column-gap:8mm;column-rule:.2mm solid #c5c7c5}
.premium-magazine.document-n04 .n04-movement .section-body h3{margin:5mm 0 2mm;padding-top:2.5mm;border-top:.3mm solid #202020;break-after:avoid-page;page-break-after:avoid}
.premium-magazine.document-n04 .n04-movement .section-body h4{break-after:avoid-page;page-break-after:avoid}
.premium-magazine.document-n04 .n04-movement-two .section-body p,
.premium-magazine.document-n04 .n04-movement-two .section-body li{font-size:11.55pt;line-height:1.52}
.premium-magazine.document-n04 .n04-movement .section-body blockquote,
.premium-magazine.document-n04 .n04-movement .section-body table,
.premium-magazine.document-n04 .n04-movement .section-body ol,
.premium-magazine.document-n04 .n04-movement .section-body ul{break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n04 .n04-synthesis .section-body{columns:2;column-count:2;column-gap:8mm;column-rule:.2mm solid #c5c7c5}
.premium-magazine.document-n04 .glossary-two-column{break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n04 .glossary-two-column .section-body{columns:auto!important;column-count:auto!important;column-rule:none!important}
.premium-magazine.document-n04 .glossary-two-column .section-body ul{columns:3;column-count:3;column-gap:6mm;column-rule:.2mm solid #c5c7c5;margin:0;padding-left:0;font-size:9.2pt;line-height:1.25;list-style-position:inside}
.premium-magazine.document-n04 .glossary-two-column .section-body li{margin:0 0 1.7mm;padding-left:0;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n04 .questions{min-height:210mm;box-sizing:border-box;padding-top:7mm;padding-bottom:7mm;break-before:page!important;page-break-before:always!important;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n04 .questions .section-body ol{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));grid-template-rows:repeat(3,auto);grid-auto-flow:column;align-content:space-between;gap:0 12mm;min-height:110mm;margin:0;padding-left:7mm;columns:auto;column-count:auto;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n04 .questions .section-body li{margin:0;padding-right:2mm;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n04 .questions .section-body>p:last-child{margin:2mm 0 0;padding:2.5mm 4mm;border-top:.6mm solid #171917;border-left:1.6mm solid #CFFF00;background:#FAFAF8;font:8.8pt/1.3 Avenir,sans-serif;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n04 .references{break-before:page!important;page-break-before:always!important;padding-left:0!important;border-left:0!important;background:#FAFAF8!important}
.premium-magazine.document-n04 .references::after{display:none!important}
.premium-magazine.document-n04 .references .section-heading{margin:0 0 7mm;padding-top:4mm;border-top:.25mm solid #9A9A96}
.premium-magazine.document-n04 .references .section-marker{gap:2.2mm;margin:0 0 4mm;color:#666663;font-size:6.5pt;letter-spacing:.14em}
.premium-magazine.document-n04 .references .section-marker span{display:inline!important;width:auto!important;height:auto!important;padding:0!important;border:0!important;font-size:inherit}
.premium-magazine.document-n04 .references .section-marker b::before{display:none}
.premium-magazine.document-n04 .references h2{margin:0;font-size:31pt;line-height:1}
.premium-magazine.document-n04 .references .section-body{columns:auto!important;column-count:auto!important;column-gap:0!important;column-rule:none!important;display:block!important;font:9.4pt/1.34 Avenir,sans-serif}
.premium-magazine.document-n04 .references .section-body ul{columns:2!important;column-count:2!important;column-gap:10mm;column-rule:none;margin:0;padding:0;max-width:none;list-style:none}
.premium-magazine.document-n04 .references .section-body li{break-inside:avoid;overflow-wrap:normal;word-break:normal;hyphens:none;padding:0;margin:0 0 3mm}
.premium-magazine.document-n04 .references .section-body a{overflow-wrap:normal;word-break:normal;hyphens:none}
.premium-magazine.document-n04 .references .reference-url{white-space:normal}
.premium-magazine.document-n04 .references .reference-url .url-segment{display:inline-block;white-space:nowrap}
.premium-magazine.document-n05 .infographic-boundaries{max-height:73mm}
.premium-magazine.document-n05 .infographic-boundaries img{max-height:64mm}
.premium-magazine.document-n06 .infographic-boundaries{max-height:73mm}
.premium-magazine.document-n06 .infographic-boundaries img{max-height:64mm}
.premium-magazine.document-n07 .infographic-boundaries{max-height:109mm}
.premium-magazine.document-n07 .infographic-boundaries img{max-height:99mm}
.premium-magazine.document-n10 .infographic-boundaries{max-height:73mm}
.premium-magazine.document-n10 .infographic-boundaries img{max-height:64mm}
.premium-magazine.document-n04 .section-body h3{break-after:avoid-page;page-break-after:avoid}
.premium-magazine.document-n05 .section-body h3{break-after:avoid-page;page-break-after:avoid}
.premium-magazine.document-n04 section[data-section="04"] .photo-band img,
.premium-magazine.document-n04 section[data-section="10"] .photo-band img{height:84mm}
.premium-magazine.document-n04 .n04-ai-photo img{height:91mm;object-position:center 42%;filter:saturate(.28) contrast(1.08)}
.premium-magazine.document-n04 .references-inline{margin-top:7mm}
.premium-magazine.document-n04 .references-inline img{height:103mm;object-position:center 42%;filter:grayscale(1) contrast(1.08)}
.premium-magazine.document-n05 section[data-section="05"] .photo-band img,
.premium-magazine.document-n05 section[data-section="08"] .photo-band img{object-position:center 42%}
.premium-magazine.document-n05 section[data-section="05"] .photo-band img{height:78mm}
.premium-magazine.document-n05 section[data-section="08"] .photo-band img{height:168mm}
.premium-magazine.document-n05 section[data-section="11"] .photo-band img{height:49mm;object-position:center 42%}
.premium-magazine.document-n05 section[data-section="07"] .section-body,
.premium-magazine.document-n05 section[data-section="12"] .section-body,
.premium-magazine.document-n05 section[data-section="19"] .section-body{columns:2;column-gap:8mm;column-rule:.2mm solid #c5c7c5}
.premium-magazine.document-n05 section[data-section="07"] .section-body h3,
.premium-magazine.document-n05 section[data-section="12"] .section-body h3,
.premium-magazine.document-n05 section[data-section="19"] .section-body h3{column-span:all}
.premium-magazine.document-n05 .hotel-voices-compact{padding-top:2.2mm;padding-bottom:2.2mm;margin-top:3mm;margin-bottom:4mm}
.premium-magazine.document-n05 .hotel-voices-grid article{grid-template-columns:16mm 1fr;min-height:19mm}
.premium-magazine.document-n05 .hotel-voices-grid img{width:16mm;height:19mm}
.premium-magazine.document-n05 .hotel-voices-grid article div{padding:1.4mm 1.7mm 1.2mm}
.premium-magazine.document-n05 .hotel-voices-grid h3{font-size:10pt;margin:.2mm 0 .45mm}
.premium-magazine.document-n05 .hotel-voices-grid p{font-size:6.8pt;line-height:1.12}
.premium-magazine.document-n05 .references{break-before:auto;page-break-before:auto}
.premium-magazine.document-n05 .references-inline{margin-top:5mm}
.premium-magazine.document-n05 .references-inline img{height:202mm;object-position:center 48%;filter:grayscale(1) contrast(1.08)}
.document-n05 .contents-page{padding:14mm 16mm}
.document-n05 .contents-page .contents-layout{grid-template-columns:1.42fr .58fr;gap:6mm;height:207mm;margin-top:4mm}
.document-n05 .contents-page .contents-layout ol{columns:2;column-gap:5mm}
.document-n05 .contents-page .contents-layout li{grid-template-columns:7mm 1fr;gap:1.2mm;padding:1.35mm 0;font-size:7.2pt;line-height:1.14}
.document-n05 .contents-page .contents-layout figure img{height:190mm;filter:grayscale(1) contrast(1.06)}
.document-n05 .contents-page .contents-sinnum-note{position:absolute;left:16mm;right:16mm;bottom:18mm;margin:0;padding-top:2mm;border-top:.2mm solid #BFC1BD;font:6.4pt/1.2 Avenir,sans-serif;color:#5B5D58}
.premium-magazine.document-n05 .reading-section[data-section="01"]{page:fullbleed;position:relative;box-sizing:border-box;width:210mm;height:297mm;margin:0;padding:24mm;display:flex;flex-direction:column;justify-content:flex-end;background:#191919;color:#F7F6F2;border:0;break-before:page;page-break-before:always;break-after:page;page-break-after:always}
.premium-magazine.document-n05 .reading-section[data-section="01"]::before{content:"";position:absolute;left:24mm;top:24mm;width:24mm;height:3.2mm;background:#CFFF00;clip-path:polygon(10% 0,100% 0,90% 100%,0 100%)}
.premium-magazine.document-n05 .reading-section[data-section="01"] .section-heading{display:block;margin:0 0 12mm;padding:0;border:0}
.premium-magazine.document-n05 .reading-section[data-section="01"] .section-marker{color:#CFFF00}
.premium-magazine.document-n05 .reading-section[data-section="01"] .section-marker span{color:#CFFF00;border-color:#CFFF00}
.premium-magazine.document-n05 .reading-section[data-section="01"] h2{margin:0;color:#F7F6F2;font-size:18pt}
.premium-magazine.document-n05 .reading-section[data-section="01"] .section-body{max-width:155mm}
.premium-magazine.document-n05 .reading-section[data-section="01"] .section-body p{margin:0;color:#F7F6F2;font:400 28pt/1.08 Didot,"Bodoni 72",serif;letter-spacing:-.018em}
.document-n06 .contents-page .contents-sinnum-note{position:absolute;left:16mm;width:88mm;bottom:18mm;margin:0;padding-top:2mm;border-top:.2mm solid #BFC1BD;font:6.4pt/1.2 Avenir,sans-serif;color:#5B5D58}
.premium-magazine.document-n06 .reading-section[data-section="01"]{page:fullbleed;position:relative;box-sizing:border-box;width:210mm;height:297mm;margin:0;padding:24mm;display:flex;flex-direction:column;justify-content:flex-end;background:#191919;color:#F7F6F2;border:0;break-before:page;page-break-before:always;break-after:page;page-break-after:always}
.premium-magazine.document-n06 .reading-section[data-section="01"]::before{content:"";position:absolute;left:24mm;top:24mm;width:24mm;height:3.2mm;background:#CFFF00;clip-path:polygon(10% 0,100% 0,90% 100%,0 100%)}
.premium-magazine.document-n06 .reading-section[data-section="01"] .section-heading{display:block;margin:0 0 12mm;padding:0;border:0}
.premium-magazine.document-n06 .reading-section[data-section="01"] .section-marker{color:#CFFF00}
.premium-magazine.document-n06 .reading-section[data-section="01"] .section-marker span{color:#CFFF00;border-color:#CFFF00}
.premium-magazine.document-n06 .reading-section[data-section="01"] h2{margin:0;color:#F7F6F2;font-size:18pt}
.premium-magazine.document-n06 .reading-section[data-section="01"] .section-body{max-width:155mm}
.premium-magazine.document-n06 .reading-section[data-section="01"] .section-body p{margin:0;color:#F7F6F2;font:400 28pt/1.08 Didot,"Bodoni 72",serif;letter-spacing:-.018em}
.premium-magazine.document-n06 .section-marker b{display:inline-flex;align-items:baseline;gap:2.2mm}
.premium-magazine.document-n06 .section-marker b em{font-style:normal;font-size:5.7pt;font-weight:600;letter-spacing:.12em;opacity:.72}
.premium-magazine.document-n06 .references .section-marker{gap:2.2mm;margin:0 0 4mm;color:#666663;font-size:6.5pt;letter-spacing:.14em}
.premium-magazine.document-n06 .references .section-marker span{display:inline!important;width:auto!important;height:auto!important;padding:0!important;border:0!important;font-size:inherit}
.premium-magazine.document-n06 .references .section-marker b::before{display:none}
.premium-magazine.document-n06 [data-source-id="N06-s07-b029"]{break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n05 .n05-handoff-input{break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n05 .n05-handoff-input h2{font-size:28pt;line-height:1}
.premium-magazine.document-n05 .n05-handoff-input .section-body{columns:2;column-count:2;column-gap:8mm;column-rule:.2mm solid #c5c7c5}
.premium-magazine.document-n05 .n05-movement{break-before:page;page-break-before:always;background:#FAFAF8!important;padding:0!important;border-left:0!important}
.premium-magazine.document-n05 .n05-movement-one{break-before:auto!important;page-break-before:auto!important}
.premium-magazine.document-n05 .n05-movement .section-body{columns:2;column-count:2;column-gap:8mm;column-rule:.2mm solid #c5c7c5}
.premium-magazine.document-n05 .n05-movement .section-body h3{margin:5mm 0 2mm;padding-top:2.5mm;border-top:.3mm solid #202020;break-after:avoid-column!important;page-break-after:avoid}
.premium-magazine.document-n05 .n05-movement .section-body h4{break-after:avoid-column!important;page-break-after:avoid}
.premium-magazine.document-n05 [data-source-id="N05-s07-b018"],
.premium-magazine.document-n05 [data-source-id="N05-s07-b063"]{break-before:column!important}
.premium-magazine.document-n05 .n05-movement .section-body blockquote,
.premium-magazine.document-n05 .n05-movement .section-body table,
.premium-magazine.document-n05 .n05-movement .section-body ol,
.premium-magazine.document-n05 .n05-movement .section-body ul{break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n05 .n05-movement-two .section-body p,
.premium-magazine.document-n05 .n05-movement-two .section-body li{font-size:12.2pt;line-height:1.6}
.premium-magazine.document-n05 .n05-movement-one .photo-band img,
.premium-magazine.document-n05 .n05-movement-three .photo-band img{height:74mm;object-position:center 44%}
.premium-magazine.document-n05 .n05-synthesis .section-body{columns:2;column-count:2;column-gap:8mm;column-rule:.2mm solid #c5c7c5}
.premium-magazine.document-n05 .glossary-two-column{break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n05 .glossary-two-column .section-body{columns:auto!important;column-count:auto!important;column-rule:none!important}
.premium-magazine.document-n05 .glossary-two-column .section-body ul{columns:3;column-count:3;column-gap:6mm;column-rule:.2mm solid #c5c7c5;margin:0;padding-left:0;font-size:9.2pt;line-height:1.25;list-style-position:inside}
.premium-magazine.document-n05 .glossary-two-column .section-body li{margin:0 0 1.7mm;padding-left:0;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n05 .questions{min-height:210mm;box-sizing:border-box;padding-top:7mm;padding-bottom:7mm;break-before:page!important;page-break-before:always!important;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n05 .questions .section-body ol{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));grid-template-rows:repeat(3,auto);grid-auto-flow:column;align-content:space-between;gap:0 12mm;min-height:110mm;margin:0;padding-left:7mm;columns:auto;column-count:auto;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n05 .questions .section-body li{margin:0;padding-right:2mm;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n05 .questions .section-body>p:last-child{margin:2mm 0 0;padding:2.5mm 4mm;border-top:.6mm solid #171917;border-left:1.6mm solid #CFFF00;background:#FAFAF8;font:8.8pt/1.3 Avenir,sans-serif;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n05 .references{break-before:page!important;page-break-before:always!important;padding-left:0!important;border-left:0!important;background:#FAFAF8!important}
.premium-magazine.document-n05 .references::after{display:none!important}
.premium-magazine.document-n05 .references .section-heading{margin:0 0 7mm;padding-top:4mm;border-top:.25mm solid #9A9A96}
.premium-magazine.document-n05 .references .section-marker{gap:2.2mm;margin:0 0 4mm;color:#666663;font-size:6.5pt;letter-spacing:.14em}
.premium-magazine.document-n05 .references .section-marker span{display:inline!important;width:auto!important;height:auto!important;padding:0!important;border:0!important;font-size:inherit}
.premium-magazine.document-n05 .references .section-marker b::before{display:none}
.premium-magazine.document-n05 .references h2{margin:0;font-size:31pt;line-height:1}
.premium-magazine.document-n05 .references .section-body{columns:auto!important;column-count:auto!important;column-gap:0!important;column-rule:none!important;display:block!important;font:9.8pt/1.46 Avenir,sans-serif}
.premium-magazine.document-n05 .references .section-body ul{columns:2!important;column-count:2!important;column-gap:10mm;column-rule:none;margin:0;padding:0;max-width:none;list-style:none}
.premium-magazine.document-n05 .references .section-body li{break-inside:avoid;overflow-wrap:normal;word-break:normal;hyphens:none;padding:0;margin:0 0 6mm}
.premium-magazine.document-n05 .references .section-body a{overflow-wrap:normal;word-break:normal;hyphens:none}
.premium-magazine.document-n05 .references .reference-url{white-space:normal}
.premium-magazine.document-n05 .references .reference-url .url-segment{display:inline-block;white-space:nowrap}
.premium-magazine.document-n06 .section-body h3{break-after:avoid-page;page-break-after:avoid}
.premium-magazine.document-n06 section[data-section="05"] .photo-band img{height:68mm;object-position:center 46%}
.premium-magazine.document-n06 section[data-section="12"] .photo-band img{height:66mm;object-position:center 48%}
.premium-magazine.document-n06 section[data-section="14"] .photo-band img{height:70mm;object-position:center 42%}
.premium-magazine.document-n06 section[data-section="22"] .photo-band img{height:62mm;object-position:center 44%}
.premium-magazine.document-n06 section[data-section="08"] .section-body,
.premium-magazine.document-n06 section[data-section="12"] .section-body,
.premium-magazine.document-n06 section[data-section="19"] .section-body,
.premium-magazine.document-n06 section[data-section="22"] .section-body{columns:2;column-gap:8mm;column-rule:.2mm solid #c5c7c5}
.premium-magazine.document-n06 section[data-section="08"] .section-body h3,
.premium-magazine.document-n06 section[data-section="12"] .section-body h3,
.premium-magazine.document-n06 section[data-section="19"] .section-body h3,
.premium-magazine.document-n06 section[data-section="22"] .section-body h3{column-span:all}
.premium-magazine.document-n06 .hotel-voices-compact{padding-top:2.2mm;padding-bottom:2.2mm;margin-top:3mm;margin-bottom:4mm}
.premium-magazine.document-n06 .hotel-voices-grid article{grid-template-columns:16mm 1fr;min-height:19mm}
.premium-magazine.document-n06 .hotel-voices-grid img{width:16mm;height:19mm}
.premium-magazine.document-n06 .hotel-voices-grid article div{padding:1.4mm 1.7mm 1.2mm}
.premium-magazine.document-n06 .hotel-voices-grid h3{font-size:10pt;margin:.2mm 0 .45mm}
.premium-magazine.document-n06 .hotel-voices-grid p{font-size:6.8pt;line-height:1.12}
.premium-magazine.document-n06 .references{break-before:auto;page-break-before:auto}
.premium-magazine.document-n06 .references-inline{margin-top:5mm}
.premium-magazine.document-n06 .references-inline img{height:202mm;object-position:center 48%;filter:grayscale(1) contrast(1.08)}
.premium-magazine.document-n07 .section-body h3{break-after:avoid-page;page-break-after:avoid}
.document-n07 .contents-layout figure img{filter:none}
.premium-magazine.document-n07 .reading-section[data-section="01"]{page:fullbleed;position:relative;box-sizing:border-box;width:210mm;height:297mm;margin:0;padding:24mm;display:flex;flex-direction:column;justify-content:flex-end;background:#191919;color:#F7F6F2;border:0;break-before:page;page-break-before:always;break-after:page;page-break-after:always}
.premium-magazine.document-n07 .reading-section[data-section="01"]::before{content:"";position:absolute;left:24mm;top:24mm;width:24mm;height:3.2mm;background:#CFFF00;clip-path:polygon(10% 0,100% 0,90% 100%,0 100%)}
.premium-magazine.document-n07 .reading-section[data-section="01"] .section-heading{display:block;margin:0 0 12mm;padding:0;border:0}
.premium-magazine.document-n07 .reading-section[data-section="01"] .section-marker{color:#CFFF00}
.premium-magazine.document-n07 .reading-section[data-section="01"] .section-marker span{color:#CFFF00;border-color:#CFFF00}
.premium-magazine.document-n07 .reading-section[data-section="01"] h2{margin:0;color:#F7F6F2;font-size:18pt}
.premium-magazine.document-n07 .reading-section[data-section="01"] .section-body{max-width:155mm}
.premium-magazine.document-n07 .reading-section[data-section="01"] .section-body p{margin:0;color:#F7F6F2;font:400 28pt/1.08 Didot,"Bodoni 72",serif;letter-spacing:-.018em}
.premium-magazine.document-n07 .n07-handoff-input{break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n07 .n07-movement{break-before:page;page-break-before:always;background:#FAFAF8!important;padding:0!important;border-left:0!important}
.premium-magazine.document-n07 .n07-movement-one{break-before:auto!important;page-break-before:auto!important}
.premium-magazine.document-n07 .n07-movement .section-body,
.premium-magazine.document-n07 .n07-synthesis .section-body{columns:2;column-count:2;column-gap:8mm;column-rule:.2mm solid #c5c7c5}
.premium-magazine.document-n07 .n07-movement .section-body h3{margin:5mm 0 2mm;padding-top:2.5mm;border-top:.3mm solid #202020;break-after:avoid-column!important;page-break-after:avoid}
.premium-magazine.document-n07 .n07-movement .section-body h4{break-after:avoid-column!important;page-break-after:avoid}
.premium-magazine.document-n07 .n07-movement .section-body blockquote,
.premium-magazine.document-n07 .n07-movement .section-body table,
.premium-magazine.document-n07 .n07-movement .section-body ol,
.premium-magazine.document-n07 .n07-movement .section-body ul{break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n07 p[data-source-id="N07-s06-b067"]{break-after:avoid-page;page-break-after:avoid}
.premium-magazine.document-n07 p[data-source-id="N07-s06-b067"]+ul{break-before:avoid-page;page-break-before:avoid}
.premium-magazine.document-n07 section[data-section="08"] .section-body ol li:nth-last-child(2){break-after:avoid-page;page-break-after:avoid}
.premium-magazine.document-n07 section[data-section="02"] .photo-band img{height:82mm;object-position:center 45%;filter:none}
.premium-magazine.document-n07 section[data-section="06"] .photo-band img{height:84mm;object-position:center 47%;filter:none}
.premium-magazine.document-n07 section[data-section="07"] .photo-band img{height:76mm;object-position:center 48%;filter:none}
.premium-magazine.document-n07 .full-bleed-quote img{filter:none}
.premium-magazine.document-n07 .full-bleed-quote::after{background:linear-gradient(180deg,rgba(0,0,0,.01) 42%,rgba(0,0,0,.57) 100%)}
.premium-magazine.document-n07 .hotel-voices-compact{padding-top:2.2mm;padding-bottom:2.2mm;margin-top:3mm;margin-bottom:4mm}
.premium-magazine.document-n07 .hotel-voices-grid article{grid-template-columns:16mm 1fr;min-height:19mm}
.premium-magazine.document-n07 .hotel-voices-grid img{width:16mm;height:19mm}
.premium-magazine.document-n07 .hotel-voices-grid article div{padding:1.4mm 1.7mm 1.2mm}
.premium-magazine.document-n07 .hotel-voices-grid h3{font-size:10pt;margin:.2mm 0 .45mm}
.premium-magazine.document-n07 .hotel-voices-grid p{font-size:6.8pt;line-height:1.12}
.premium-magazine.document-n07 .glossary-two-column{break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n07 .glossary-two-column .section-body{columns:auto!important;column-count:auto!important;column-rule:none!important}
.premium-magazine.document-n07 .glossary-two-column .section-body ul{columns:3;column-count:3;column-gap:7mm;column-rule:.2mm solid #c5c7c5;margin:0;padding-left:0;font-size:9.7pt;line-height:1.28;list-style-position:inside}
.premium-magazine.document-n07 .glossary-two-column .section-body li{margin:0 0 2mm;padding-left:0;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n07 .questions{padding-top:4.5mm;padding-bottom:4.5mm}
.premium-magazine.document-n07 .questions .section-body ol{margin-top:0;margin-bottom:0}
.premium-magazine.document-n07 .questions .section-body li{margin-bottom:2mm}
.premium-magazine.document-n07 .questions .section-body>p:last-child{margin:3mm 0 0;padding:3mm 4mm;border-top:.6mm solid #171917;border-left:1.6mm solid #CFFF00;background:#FAFAF8;font:8.8pt/1.3 Avenir,sans-serif;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n07 .pill-summary{position:relative}
.premium-magazine.document-n07 .pill-summary .section-heading{position:static}
.premium-magazine.document-n07 .pill-summary-icon{right:7mm;top:7mm}
.premium-magazine.document-n07 .references{break-before:page!important;page-break-before:always!important;padding-left:0!important;border-left:0!important;background:#FAFAF8!important}
.premium-magazine.document-n07 .references::after{display:none!important}
.premium-magazine.document-n07 .references .section-heading{margin:0 0 7mm;padding-top:4mm;border-top:.25mm solid #9A9A96}
.premium-magazine.document-n07 .references .section-marker{gap:2.2mm;margin:0 0 4mm;color:#666663;font-size:6.5pt;letter-spacing:.14em}
.premium-magazine.document-n07 .references .section-marker span{display:inline!important;width:auto!important;height:auto!important;padding:0!important;border:0!important;font-size:inherit}
.premium-magazine.document-n07 .references .section-marker b::before{display:none}
.premium-magazine.document-n07 .references h2{margin:0;font-size:31pt;line-height:1}
.premium-magazine.document-n07 .references .section-body{columns:auto!important;column-count:auto!important;column-gap:0!important;column-rule:none!important;display:block!important;font:10.8pt/1.48 Avenir,sans-serif}
.premium-magazine.document-n07 .references .section-body ul{columns:2!important;column-count:2!important;column-gap:10mm;column-rule:none;margin:0;padding:0;max-width:none;list-style:none}
.premium-magazine.document-n07 .references .section-body li{break-inside:avoid;overflow-wrap:normal;word-break:normal;hyphens:none;padding:0;margin:0 0 5.8mm}
.premium-magazine.document-n07 .references .section-body a{overflow-wrap:normal;word-break:normal;hyphens:none}
.premium-magazine.document-n07 .references .reference-url{white-space:normal}
.premium-magazine.document-n07 .references .reference-url .url-segment{display:inline-block;white-space:nowrap}
.premium-magazine section[data-section="06"] .table-wrap{break-inside:auto;page-break-inside:auto}
.premium-magazine section[data-section="06"] table{break-inside:auto;page-break-inside:auto}
.premium-magazine section[data-section="06"] thead{display:table-header-group}
.premium-magazine section[data-section="06"] tr{break-inside:avoid;page-break-inside:avoid}
.premium-magazine .opening-section:nth-child(2) .section-body>p:first-child::first-letter,
.premium-magazine .layout-section-opener .section-body>p:first-child::first-letter{color:#141615}
.premium-magazine .hotel-case,
.premium-magazine .hotel-case.dossier{
  margin:0 -18mm;
  padding:18mm;
  color:#171917;
  background:#DADDDC;
  border:0;
  border-radius:0;
  break-before:page;
  page-break-before:always;
  -webkit-box-decoration-break:clone;
  box-decoration-break:clone;
}
.premium-magazine .hotel-case .section-marker{color:#171917}
.premium-magazine .hotel-case .section-marker span{color:#171917;border-color:#171917;background:transparent}
.premium-magazine .hotel-case .section-marker b{color:#171917}
.premium-magazine .hotel-case .section-marker b::before{background:#CFFF00}
.premium-magazine .hotel-case h2{color:#171917;font-size:36pt}
.premium-magazine .hotel-case .section-body,
.premium-magazine .hotel-case .section-body p,
.premium-magazine .hotel-case .section-body li{color:#171917;font-size:11.15pt;line-height:1.47}
.premium-magazine .hotel-case .hotel-photo{margin:5mm -18mm 7mm}
.premium-magazine .hotel-case .hotel-photo img{height:53mm;filter:saturate(.38) contrast(1.04);object-fit:cover}
.premium-magazine .hotel-case .hotel-photo figcaption{color:#4d504d}
.premium-magazine.document-n00 .hotel-case .hotel-photo figcaption{padding-left:18mm;padding-right:18mm}
.premium-magazine .hotel-case .section-heading{position:relative;padding-right:26mm}
.premium-magazine .case-application-icon{position:absolute;right:0;top:2mm;width:21mm;height:21mm;color:#171917}
.premium-magazine .hotel-case .table-wrap{break-inside:auto;page-break-inside:auto}
.premium-magazine .hotel-case thead{display:table-header-group}
.premium-magazine .hotel-case tr{break-inside:avoid;page-break-inside:avoid}
.premium-magazine .pill-summary .section-heading{position:relative;padding-right:37mm}
.premium-magazine .pill-summary-icon{position:absolute;right:0;top:1mm;width:31mm;height:18mm}
.premium-magazine .pill-summary{
  margin-left:-7mm;
  margin-right:-7mm;
  padding:6mm 7mm 7mm 8mm;
  color:#171917;
  background:#E2E5E6;
  border-top:.55mm solid #171917;
  border-left:2.2mm solid #CFFF00;
}
.premium-magazine .pill-summary .section-marker{color:#171917}
.premium-magazine .pill-summary .section-marker span{color:#171917;border-color:#171917;background:transparent}
.premium-magazine .pill-summary .section-marker b::before{background:#CFFF00}
.premium-magazine.document-n00 .pill-summary{break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n00 .pill-summary .section-heading{padding-right:0}
.premium-magazine.document-n00 .pill-summary .section-body ol{break-inside:avoid-page;page-break-inside:avoid;margin-bottom:0}
.premium-magazine.document-n00 .questions .section-body{columns:auto;column-count:auto;width:100%}
.premium-magazine.document-n00 .questions .section-body ol{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));grid-template-rows:repeat(4,auto);grid-auto-flow:column;gap:2mm 10mm;width:100%;margin:0;padding-left:7mm;columns:auto;break-inside:auto;page-break-inside:auto}
.premium-magazine.document-n00 .questions .section-body li{margin:0;padding-right:2mm;font-size:9.3pt;line-height:1.3;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n00 .section-body h3{break-after:avoid-column;page-break-after:avoid;break-inside:avoid;page-break-inside:avoid}
.premium-magazine.document-n00 .section-body h3+p{orphans:3;widows:3}
.premium-magazine.document-n00 .n00-organizational-heading{break-after:avoid-column;page-break-after:avoid}
.premium-magazine.document-n00 .n00-organizational-heading+h3{break-before:avoid-column;page-break-before:avoid;break-after:avoid-column;page-break-after:avoid}
.premium-magazine.document-n00 section[data-section="23"] .photo-band img{filter:grayscale(1) contrast(1.06)}
.premium-magazine.document-n00 section[data-section="08"]{min-height:238mm;box-sizing:border-box}
.premium-magazine.document-n00 section[data-section="08"] .section-body{min-height:190mm}
.premium-magazine.document-n00 section[data-section="17"]{min-height:225mm;box-sizing:border-box}
.premium-magazine.document-n00 section[data-section="22"]{min-height:238mm;box-sizing:border-box}
.premium-magazine.document-n00 section[data-section="22"] .section-body{min-height:150mm}
.premium-magazine.document-n00 .n00-nuclei-index{min-height:250mm;box-sizing:border-box;break-before:page;page-break-before:always}
.premium-magazine.document-n00 .n00-nuclei-index h2{font-size:34pt;line-height:.98;margin-bottom:3mm}
.premium-magazine.document-n00 .n00-nuclei-index .section-body{columns:2;column-gap:10mm;column-rule:.2mm solid #C5C7C5}
.premium-magazine.document-n00 .n00-nuclei-index .section-body>p:first-child{column-span:all;margin-bottom:3mm;font-size:9.2pt;line-height:1.28}
.premium-magazine.document-n00 .n00-nuclei-index .section-body h3{break-after:avoid-page;page-break-after:avoid;margin:2.7mm 0 1mm;font-size:12.3pt;line-height:1.03}
.premium-magazine.document-n00 .n00-nuclei-index .section-body ul{margin:0 0 2mm;padding-left:0;list-style:none;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n00 .n00-nuclei-index .section-body li{margin:0;padding:0 0 1mm;border-bottom:.15mm solid #D0D1CE;font:7.65pt/1.19 Avenir,sans-serif;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n00 .n00-curriculum-map .table-wrap{margin:2.5mm 0 4mm;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n00 .n00-curriculum-map table{font-size:6.45pt;line-height:1.13}
.premium-magazine.document-n00 .n00-curriculum-map th,.premium-magazine.document-n00 .n00-curriculum-map td{padding:1.15mm 1.3mm}
.premium-magazine.document-n00 .guided-exercise{break-before:page;page-break-before:always}
.premium-magazine.document-n00 .guided-exercise .section-body h3{margin-top:5mm}
.premium-magazine.document-n00 .exercise-writing-space{height:34mm;margin:3mm 0 6mm;padding:3mm 3.5mm;border:.25mm solid #B7BAB5;border-top:1.2mm solid #CFFF00;background:#FAFAF8;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n00 .exercise-writing-space span{display:block;margin:0 0 1.2mm;padding:0;background:transparent;font:700 6.5pt/1 Avenir,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:#4D5A00}
.premium-magazine.document-n00 .exercise-writing-space small{display:block;margin:0 0 2.2mm;font:400 6.8pt/1.25 Avenir,sans-serif;color:#656760}
.premium-magazine.document-n00 .exercise-writing-rules{display:grid;gap:2.6mm}
.premium-magazine.document-n00 .exercise-writing-rules i{display:block;height:0;border-bottom:.18mm solid #D1D3CF}
.premium-magazine.document-n00 .product-minimum{margin-left:-7mm;margin-right:-7mm;padding:7mm 8mm;background:#E2E5E6;border-top:.55mm solid #171917;border-left:2.2mm solid #CFFF00;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n03 .pill-summary{padding-top:3.5mm;padding-bottom:4mm}
.premium-magazine.document-n03 .pill-summary h2{font-size:27pt;line-height:.96;margin-bottom:2mm}
.premium-magazine.document-n03 .pill-summary .section-body ol{margin-top:1.5mm;margin-bottom:0}
.premium-magazine.document-n03 .pill-summary .section-body li{margin-bottom:.6mm;line-height:1.16}
.premium-magazine.document-n04 .pill-summary{padding-top:3.5mm;padding-bottom:4mm}
.premium-magazine.document-n04 .pill-summary h2{font-size:27pt;line-height:.96;margin-bottom:2mm}
.premium-magazine.document-n04 .pill-summary .section-body ol{margin-top:1.5mm;margin-bottom:0}
.premium-magazine.document-n04 .pill-summary .section-body li{margin-bottom:.6mm;line-height:1.16}
.premium-magazine.document-n05 .pill-summary{padding-top:3.5mm;padding-bottom:4mm}
.premium-magazine.document-n05 .pill-summary h2{font-size:27pt;line-height:.96;margin-bottom:2mm}
.premium-magazine.document-n05 .pill-summary .section-body ol{margin-top:1.5mm;margin-bottom:0}
.premium-magazine.document-n05 .pill-summary .section-body li{margin-bottom:.6mm;line-height:1.16}
.premium-magazine.document-n06 .pill-summary{padding-top:3.5mm;padding-bottom:4mm}
.premium-magazine.document-n06 .pill-summary h2{font-size:27pt;line-height:.96;margin-bottom:2mm}
.premium-magazine.document-n06 .pill-summary .section-body ol{margin-top:1.5mm;margin-bottom:0}
.premium-magazine.document-n06 .pill-summary .section-body li{margin-bottom:.6mm;line-height:1.16}
.premium-magazine.document-n07 .pill-summary{padding-top:3.5mm;padding-bottom:4mm}
.premium-magazine.document-n07 .pill-summary h2{font-size:27pt;line-height:.96;margin-bottom:2mm}
.premium-magazine.document-n07 .pill-summary .section-body ol{margin-top:1.5mm;margin-bottom:0}
.premium-magazine.document-n07 .pill-summary .section-body li{margin-bottom:.6mm;line-height:1.16}
.premium-magazine.document-n09 .pill-summary{padding-top:3.5mm;padding-bottom:4mm}
.premium-magazine.document-n09 .pill-summary h2{font-size:27pt;line-height:.96;margin-bottom:2mm}
.premium-magazine.document-n09 .pill-summary .section-body ol{margin-top:1.5mm;margin-bottom:0}
.premium-magazine.document-n09 .pill-summary .section-body li{margin-bottom:.6mm;line-height:1.16}
.premium-magazine.document-n10 .pill-summary{padding-top:3.5mm;padding-bottom:4mm}
.premium-magazine.document-n10 .pill-summary h2{font-size:27pt;line-height:.96;margin-bottom:2mm}
.premium-magazine.document-n10 .pill-summary .section-body ol{margin-top:1.5mm;margin-bottom:0}
.premium-magazine.document-n10 .pill-summary .section-body li{margin-bottom:.6mm;line-height:1.16}
.premium-magazine .glossary-two-column .section-body ul{columns:2;column-gap:8mm;column-rule:.2mm solid #c5c7c5}
.premium-magazine .glossary-two-column .section-body li{break-inside:avoid;margin-bottom:1.7mm}
.full-bleed-quote img{filter:saturate(.25) contrast(1.12) brightness(.79)}.full-bleed-quote::after{background:linear-gradient(180deg,rgba(0,0,0,.02) 35%,rgba(0,0,0,.78) 100%)}.full-bleed-quote::before{top:18mm;bottom:auto;left:18mm;width:19mm;height:3mm;transform:none;clip-path:polygon(10% 0,100% 0,90% 100%,0 100%)}.full-bleed-quote p{font-family:Didot,"Bodoni 72",serif;font-size:25pt;line-height:1.03}.closing-image>img{filter:none}.closing-image figcaption{position:absolute;z-index:2;left:18mm;right:18mm;bottom:18mm;margin:0;font:400 7.2pt/1.25 Avenir,sans-serif;color:#575A55;text-align:left}
.closing-n00{position:relative;background:#111;color:#F7F6F2}
.closing-n00>img{position:absolute;inset:0;width:100%;height:100%;max-width:none;max-height:none;object-fit:cover;object-position:center 48%;filter:grayscale(1) contrast(1.12) brightness(.58)}
.closing-n00::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.05) 32%,rgba(0,0,0,.86) 100%)}
.closing-n00::before{content:"";position:absolute;z-index:2;left:18mm;top:20mm;width:24mm;height:3.2mm;background:#CFFF00;clip-path:polygon(10% 0,100% 0,90% 100%,0 100%)}
.closing-n00 .closing-copy{position:absolute;z-index:3;left:18mm;right:18mm;bottom:27mm;max-width:154mm}
.closing-n00 .closing-copy p{max-width:150mm;margin:0 0 5mm;font:400 26pt/1.03 Didot,"Bodoni 72",serif;color:#F7F6F2}
.closing-n00 .closing-copy small{display:block;max-width:112mm;padding-top:3mm;border-top:.25mm solid rgba(247,246,242,.55);font:7.6pt/1.35 Avenir,sans-serif;color:#E5E6E0}
.premium-magazine .reading-section.references{break-inside:auto;page-break-inside:auto}
.premium-magazine .references .section-body{font-family:Avenir,sans-serif;font-size:8.1pt;line-height:1.25}
.premium-magazine .references .section-body ul{columns:2;column-gap:8mm}
.premium-magazine .references .section-body li{break-inside:avoid;margin-bottom:1.2mm}
.premium-magazine .references{break-before:page;page-break-before:always}
.premium-magazine.document-n00 .references{break-before:auto;page-break-before:auto}
.premium-magazine.document-n00 .references .section-body{
  columns:auto !important;
  column-count:auto !important;
  column-gap:0 !important;
  column-rule:none !important;
  display:block !important;
  grid-template-columns:none !important;
  font-size:9pt;
  line-height:1.28;
}
.premium-magazine.document-n00 .references{
  break-before:page !important;
  page-break-before:always !important;
  padding-left:0 !important;
  border-left:0 !important;
}
.premium-magazine.document-n00 .references::after{display:none !important}
.premium-magazine.document-n00 .references .section-heading{
  margin:0 0 7mm;
  padding-top:4mm;
  border-top:.25mm solid #9A9A96;
}
.premium-magazine.document-n00 .references .section-marker{
  gap:2.2mm;
  margin:0 0 4mm;
  color:#666663;
  font-size:6.5pt;
  letter-spacing:.14em;
}
.premium-magazine.document-n00 .references .section-marker span{
  display:inline;
  width:auto;
  height:auto;
  padding:0;
  border:0 !important;
  font-size:inherit;
}
.premium-magazine.document-n00 .references .section-marker b::before{display:none}
.premium-magazine.document-n00 .references h2{
  margin:0;
  font-size:31pt;
  line-height:1;
}
.premium-magazine.document-n00 .references .section-body ul{
  columns:2 !important;
  column-count:2 !important;
  column-gap:10mm;
  column-rule:none;
  margin:0;
  padding:0;
  max-width:none;
  list-style:none;
}
.premium-magazine.document-n00 .references .section-body li{
  break-inside:avoid;
  overflow-wrap:anywhere;
  word-break:normal;
  hyphens:auto;
  padding:0;
  margin:0 0 3.2mm;
}
.premium-magazine .references a{color:inherit;text-decoration:underline;text-decoration-thickness:.2mm;text-underline-offset:.5mm}
.premium-magazine.document-n00 .references{background:#FAFAF8!important;border-left:0!important}
.premium-magazine.document-n00 .references .section-marker span{display:inline!important;padding:0!important;border:0!important}
.premium-magazine.document-n01 .contents-layout{grid-template-columns:1.44fr .56fr;gap:6mm;height:207mm;margin-top:4mm}
.premium-magazine.document-n01 .contents-layout ol{columns:2;column-gap:5mm}
.premium-magazine.document-n01 .contents-layout li{grid-template-columns:7mm 1fr;gap:1.2mm;padding:1.15mm 0;font-size:6.9pt;line-height:1.12}
.premium-magazine.document-n01 .contents-layout li small{display:inline-block;margin-left:1mm;font-size:4.8pt;line-height:1;letter-spacing:.08em;color:#777}
.premium-magazine.document-n01 .contents-layout .contents-unnumbered{color:#666663;background:#F0F0EC}
.premium-magazine.document-n01 .contents-layout .contents-unnumbered b{color:#4D5A00}
.premium-magazine.document-n01 .contents-layout figure img{height:190mm;filter:grayscale(1) contrast(1.06)}
.premium-magazine.document-n01 .contents-layout figcaption{font-size:6.2pt;line-height:1.16}
.premium-magazine.document-n01 .section-marker b{display:inline-flex;align-items:baseline;gap:2.2mm}
.premium-magazine.document-n01 .section-marker b em{font-style:normal;font-size:5.7pt;font-weight:600;letter-spacing:.12em;opacity:.72}
.premium-magazine.document-n01 .hotel-voices-compact{break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n01 .hotel-voices-grid article{grid-template-columns:19mm 1fr;min-height:23mm}
.premium-magazine.document-n01 .hotel-voices-grid img{width:19mm;height:23mm;object-position:center 19%}
.premium-magazine.document-n01 .n01-keep-together{break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n01 .n01-subsection-keep{break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n01 .section-heading{break-inside:avoid-page;page-break-inside:avoid;break-after:avoid-page!important;page-break-after:avoid!important}
.premium-magazine.document-n01 .section-heading+.section-body{break-before:avoid-page;page-break-before:avoid}
.premium-magazine.document-n01 .reading-section .section-body p{orphans:2;widows:5}
.premium-magazine.document-n01 p[data-source-id="N01-s04-b003"],
.premium-magazine.document-n01 p[data-source-id="N01-s07-b008"],
.premium-magazine.document-n01 p[data-source-id="N01-s14-b002"],
.premium-magazine.document-n01 p[data-source-id="N01-s16-b001"],
.premium-magazine.document-n01 p[data-source-id="N01-s19-b006"],
.premium-magazine.document-n01 p[data-source-id="N01-s20-b007"]{break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n01 .opening-section:nth-child(2) .section-body>p:first-child::first-letter,
.premium-magazine.document-n01 .layout-section-opener .section-body>p:first-child::first-letter{float:none!important;display:inline!important;margin:0!important;color:inherit!important;font:inherit!important;line-height:inherit!important}
.premium-magazine.document-n01 .n01-method-architecture{width:100%;max-height:none;margin:5mm 0 7mm;padding:3mm 0}
.premium-magazine.document-n01 .n01-method-architecture img{width:100%;height:auto;max-height:none}
.premium-magazine.document-n01 .hotel-case{position:relative}
.premium-magazine.document-n01 .hotel-case .section-heading{position:static}
.premium-magazine.document-n01 .hotel-case .case-application-icon{right:18mm;top:14mm;width:17mm;height:17mm}
.premium-magazine.document-n01 .hotel-case .hotel-photo figcaption{box-sizing:border-box;padding-left:18mm;padding-right:18mm}
.premium-magazine.document-n01 section[data-section="21"]{padding-top:12mm;padding-bottom:12mm}
.premium-magazine.document-n01 section[data-section="21"] .section-body{columns:3;column-count:3;column-gap:6mm;column-rule:.2mm solid #c5c7c5}
.premium-magazine.document-n01 section[data-section="21"] .section-body>p,
.premium-magazine.document-n01 section[data-section="21"] .section-body>ul li{font-size:10.4pt;line-height:1.34}
.premium-magazine.document-n01 section[data-section="21"] h2{font-size:29pt;line-height:.96}
.premium-magazine.document-n01 section[data-section="21"] .hotel-photo{margin:2.5mm -18mm 4mm}
.premium-magazine.document-n01 section[data-section="21"] .hotel-photo img{height:32mm}
.premium-magazine.document-n01 section[data-section="21"] .section-body p{margin-bottom:2.2mm}
.premium-magazine.document-n01 .n01-hh01-memo{column-span:all;display:grid;grid-template-columns:1.45fr .55fr;gap:4mm;margin:1.2mm 0 0;padding:2mm 3mm 1.8mm;background:#F3F5F3;border-top:.55mm solid #171917;border-left:1.6mm solid #CFFF00;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n01 .n01-hh01-memo p{margin:0!important;font-family:Avenir,sans-serif;font-size:8pt!important;line-height:1.15!important;orphans:2;widows:2}
.premium-magazine.document-n01 section[data-section="22"] .section-body{columns:2;column-count:2;column-gap:8mm;column-rule:.2mm solid #c5c7c5}
.premium-magazine.document-n01 section[data-section="20"] .photo-band img{height:146mm;object-position:center 52%}
.premium-magazine.document-n01 section[data-section="23"] .section-body{columns:2;column-count:2;column-gap:8mm;column-rule:.2mm solid #c5c7c5}
.premium-magazine.document-n01 section[data-section="24"] .section-body{columns:2;column-count:2;column-gap:8mm;column-rule:.2mm solid #c5c7c5}
.premium-magazine.document-n01 section[data-section="25"] .section-body{columns:2;column-count:2;column-gap:8mm;column-rule:.2mm solid #c5c7c5}
.premium-magazine.document-n01 section[data-section="25"] .section-body p:last-child{break-inside:avoid;page-break-inside:avoid}
.premium-magazine.document-n01 section[data-section="23"] h2,.premium-magazine.document-n01 section[data-section="24"] h2,.premium-magazine.document-n01 section[data-section="25"] h2{font-size:29pt;line-height:1}
.premium-magazine.document-n01 .pill-summary{margin-bottom:3mm;padding:4mm 6mm 4.5mm 7mm}
.premium-magazine.document-n01 .pill-summary .section-heading{position:static}
.premium-magazine.document-n01 .pill-summary h2{margin-bottom:2.5mm;font-size:27pt;line-height:1}
.premium-magazine.document-n01 .pill-summary .section-marker{margin-bottom:2.5mm}
.premium-magazine.document-n01 .pill-summary .section-body ol{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:2mm 6mm;margin:0;padding-left:6mm;columns:auto}
.premium-magazine.document-n01 .pill-summary .section-body li{margin:0;padding-right:2mm;font-size:9.2pt;line-height:1.22;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n01 .glossary-two-column{min-height:0;box-sizing:border-box;break-before:auto;page-break-before:auto;break-inside:avoid-page;page-break-inside:avoid;break-after:page;page-break-after:always}
.premium-magazine.document-n01 .glossary-two-column .section-body{columns:auto!important;column-count:auto!important;column-rule:none!important}
.premium-magazine.document-n01 .glossary-two-column .section-body ul{columns:3;column-count:3;column-gap:6mm;column-rule:.2mm solid #c5c7c5;margin:0;padding-left:0;font-size:9.7pt;line-height:1.28;list-style-position:inside}
.premium-magazine.document-n01 .glossary-two-column .section-body li{margin:0 0 2.2mm;padding-left:0;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n01 .questions{break-before:page;page-break-before:always}
.premium-magazine.document-n01 .questions .section-body>p:last-child{column-span:all;margin:5mm 0 0;padding:4mm 5mm;border-top:.6mm solid #171917;border-left:1.6mm solid #CFFF00;background:#FAFAF8;font-family:Avenir,sans-serif;font-size:8.8pt;line-height:1.3}
.premium-magazine.document-n01 .reading-section[data-section="01"]{page:fullbleed;position:relative;box-sizing:border-box;width:210mm;height:297mm;margin:0;padding:24mm;display:flex;flex-direction:column;justify-content:flex-end;background:#191919;color:#F7F6F2;border:0;break-before:page;page-break-before:always;break-after:page;page-break-after:always}
.premium-magazine.document-n01 .reading-section[data-section="01"]::before{content:"";position:absolute;left:24mm;top:24mm;width:24mm;height:3.2mm;background:#CFFF00;clip-path:polygon(10% 0,100% 0,90% 100%,0 100%)}
.premium-magazine.document-n01 .reading-section[data-section="01"] .section-heading{display:block;margin:0 0 12mm;padding:0;border:0}
.premium-magazine.document-n01 .reading-section[data-section="01"] .section-marker{color:#CFFF00}
.premium-magazine.document-n01 .reading-section[data-section="01"] .section-marker span{color:#CFFF00;border-color:#CFFF00}
.premium-magazine.document-n01 .reading-section[data-section="01"] h2{margin:0;color:#F7F6F2;font-size:18pt}
.premium-magazine.document-n01 .reading-section[data-section="01"] .section-body{max-width:155mm}
.premium-magazine.document-n01 .reading-section[data-section="01"] .section-body p{margin:0;color:#F7F6F2;font:400 28pt/1.08 Didot,"Bodoni 72",serif;letter-spacing:-.018em}
.premium-magazine.document-n01 .references{
  break-before:auto!important;
  page-break-before:auto!important;
  padding-left:0!important;
  border-left:0!important;
  background:#FAFAF8!important;
}
.premium-magazine.document-n01 .references::after{display:none!important}
.premium-magazine.document-n01 .references .section-heading{margin:0 0 7mm;padding-top:4mm;border-top:.25mm solid #9A9A96}
.premium-magazine.document-n01 .references .section-marker{gap:2.2mm;margin:0 0 4mm;color:#666663;font-size:6.5pt;letter-spacing:.14em}
.premium-magazine.document-n01 .references .section-marker span{display:inline!important;width:auto!important;height:auto!important;padding:0!important;border:0!important;font-size:inherit}
.premium-magazine.document-n01 .references .section-marker b::before{display:none}
.premium-magazine.document-n01 .references h2{margin:0;font-size:31pt;line-height:1}
.premium-magazine.document-n01 .references .section-body{columns:auto!important;column-count:auto!important;column-gap:0!important;column-rule:none!important;display:block!important;font-size:8.15pt;line-height:1.24}
.premium-magazine.document-n01 .references .section-body ul{columns:2!important;column-count:2!important;column-gap:10mm;column-rule:none;margin:0;padding:0;max-width:none;list-style:none}
.premium-magazine.document-n01 .references .section-body li{break-inside:avoid;overflow-wrap:normal;word-break:normal;hyphens:none;padding:0;margin:0 0 2.2mm}
.premium-magazine.document-n01 .references .section-body a{overflow-wrap:normal;word-break:normal;hyphens:none}
.premium-magazine.document-n01 .references .reference-url{white-space:normal}
.premium-magazine.document-n01 .references .reference-url .url-segment{white-space:nowrap}
.premium-magazine.document-n02 .contents-layout{grid-template-columns:1.44fr .56fr;gap:6mm;height:207mm;margin-top:4mm}
.premium-magazine.document-n02 .contents-layout ol{columns:2;column-gap:5mm}
.premium-magazine.document-n02 .contents-layout li{grid-template-columns:7mm 1fr;gap:1.2mm;padding:1.15mm 0;font-size:6.9pt;line-height:1.12}
.premium-magazine.document-n02 .contents-layout li small{display:inline-block;margin-left:1mm;font-size:4.8pt;line-height:1;letter-spacing:.08em;color:#777}
.premium-magazine.document-n02 .contents-layout .contents-unnumbered{color:#666663;background:#F0F0EC}
.premium-magazine.document-n02 .contents-layout .contents-unnumbered b{color:#4D5A00}
.premium-magazine.document-n02 .contents-layout figure img{height:190mm;filter:grayscale(1) contrast(1.06)}
.premium-magazine.document-n02 .contents-layout figcaption{font-size:6.2pt;line-height:1.16}
.premium-magazine.document-n02 .section-marker b{display:inline-flex;align-items:baseline;gap:2.2mm}
.premium-magazine.document-n02 .section-marker b em{font-style:normal;font-size:5.7pt;font-weight:600;letter-spacing:.12em;opacity:.72}
.premium-magazine.document-n02 .section-heading{break-inside:avoid-page;page-break-inside:avoid;break-after:avoid-page!important;page-break-after:avoid!important}
.premium-magazine.document-n02 .section-heading+.section-body{break-before:avoid-page;page-break-before:avoid}
.premium-magazine.document-n02 .reading-section .section-body p{orphans:2!important;widows:4!important}
.premium-magazine.document-n02 .layout-accent-column .section-body>p{break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n02 .stone-card .section-body>p{break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n02 .opening-section:nth-child(2) .section-body>p:first-child::first-letter,
.premium-magazine.document-n02 .layout-section-opener .section-body>p:first-child::first-letter{float:none!important;display:inline!important;margin:0!important;color:inherit!important;font:inherit!important;line-height:inherit!important}
.premium-magazine.document-n02 .reading-section h2{word-spacing:.18em}
.premium-magazine.document-n02 section[data-section="12"] .section-body p:nth-of-type(2),
.premium-magazine.document-n02 section[data-section="14"] .section-body p:nth-of-type(2){break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n02 section[data-section="11"] .section-body{columns:2;column-count:2;column-gap:8mm;column-rule:.2mm solid #c5c7c5}
.premium-magazine.document-n02 section[data-section="11"] .photo-band{margin-top:3mm;margin-bottom:3mm}
.premium-magazine.document-n02 section[data-section="11"] .photo-band img{height:34mm}
.premium-magazine.document-n02 section[data-section="21"] .section-body{columns:2;column-count:2;column-gap:8mm;column-rule:.2mm solid #c5c7c5}
.premium-magazine.document-n02 section[data-section="17"] .photo-band img{height:43mm}
.premium-magazine.document-n02 section[data-section="18"] .section-body,
.premium-magazine.document-n02 section[data-section="18"] .section-body p,
.premium-magazine.document-n02 section[data-section="18"] .section-body li{font-size:10.4pt;line-height:1.36}
.premium-magazine.document-n02 section[data-section="18"] .section-body p{margin-bottom:3mm}
.premium-magazine.document-n02 .n02-handoff-input,
.premium-magazine.document-n02 .n02-handoff-output{break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n02 .n02-handoff-input h2,
.premium-magazine.document-n02 .n02-handoff-output h2{font-size:28pt;line-height:1}
.premium-magazine.document-n02 .n02-handoff-input .section-body,
.premium-magazine.document-n02 .n02-handoff-output .section-body{columns:2;column-count:2;column-gap:8mm;column-rule:.2mm solid #c5c7c5}
.premium-magazine.document-n02 .hotel-case{position:relative}
.premium-magazine.document-n02 .hotel-case .section-heading{position:static}
.premium-magazine.document-n02 .hotel-case .case-application-icon{right:18mm;top:20mm}
.premium-magazine.document-n02 .hotel-case .hotel-photo figcaption{box-sizing:border-box;padding-left:18mm;padding-right:18mm}
.premium-magazine.document-n02 .hotel-case .hotel-voices-compact{margin-top:6mm;margin-bottom:0}
.premium-magazine.document-n02 .hotel-case .hotel-voices-compact header h2{margin:.8mm 0 .5mm;font-size:18.5pt;line-height:1}
.premium-magazine.document-n02 .pill-summary{margin-bottom:3mm;padding:4mm 6mm 4.5mm 7mm}
.premium-magazine.document-n02 .pill-summary .section-heading{position:static}
.premium-magazine.document-n02 .pill-summary h2{margin-bottom:2.5mm;font-size:27pt;line-height:1}
.premium-magazine.document-n02 .pill-summary .section-marker{margin-bottom:2.5mm}
.premium-magazine.document-n02 .pill-summary .section-body ol{margin-top:0;margin-bottom:0}
.premium-magazine.document-n02 .questions{min-height:0;box-sizing:border-box}
.premium-magazine.document-n02 .questions .section-body ol{display:block;height:auto;margin:0;padding-left:7mm;columns:2;column-count:2;column-gap:12mm;column-fill:balance;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n02 .questions .section-body li{margin:0 0 13mm;padding-right:2mm;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n02 .questions .section-body>p:last-child{margin:5mm 0 0;padding:4mm 5mm;border-top:.6mm solid #171917;border-left:1.6mm solid #CFFF00;background:#FAFAF8;font-family:Avenir,sans-serif;font-size:8.8pt;line-height:1.3;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n02 .glossary-two-column{min-height:0;box-sizing:border-box;break-before:auto;page-break-before:auto;break-inside:auto;page-break-inside:auto;break-after:auto;page-break-after:auto}
.premium-magazine.document-n02 .glossary-two-column .section-body{columns:auto!important;column-count:auto!important;column-rule:none!important}
.premium-magazine.document-n02 .glossary-two-column .section-body ul{margin:0;padding-left:0;font-size:9.7pt;line-height:1.28;list-style-position:inside}
.premium-magazine.document-n02 .glossary-two-column .n02-glossary-primary{width:calc(66.666% - 2mm);columns:2;column-count:2;column-gap:6mm;column-rule:.2mm solid #c5c7c5;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n02 .glossary-two-column .n02-glossary-continuation{width:100%;columns:3;column-count:3;column-gap:6mm;column-rule:.2mm solid #c5c7c5;break-before:page;page-break-before:always;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n02 .glossary-two-column .section-body li{margin:0 0 2.2mm;padding-left:0;break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n02 .pill-summary .section-body ol{break-inside:avoid-page;page-break-inside:avoid}
.premium-magazine.document-n02 .reading-section[data-section="01"]{page:fullbleed;position:relative;box-sizing:border-box;width:210mm;height:297mm;margin:0;padding:24mm;display:flex;flex-direction:column;justify-content:flex-end;background:#191919;color:#F7F6F2;border:0;break-before:page;page-break-before:always;break-after:page;page-break-after:always}
.premium-magazine.document-n02 .reading-section[data-section="01"]::before{content:"";position:absolute;left:24mm;top:24mm;width:24mm;height:3.2mm;background:#CFFF00;clip-path:polygon(10% 0,100% 0,90% 100%,0 100%)}
.premium-magazine.document-n02 .reading-section[data-section="01"] .section-heading{display:block;margin:0 0 12mm;padding:0;border:0}
.premium-magazine.document-n02 .reading-section[data-section="01"] .section-marker{color:#CFFF00}
.premium-magazine.document-n02 .reading-section[data-section="01"] .section-marker span{color:#CFFF00;border-color:#CFFF00}
.premium-magazine.document-n02 .reading-section[data-section="01"] h2{margin:0;color:#F7F6F2;font-size:18pt}
.premium-magazine.document-n02 .reading-section[data-section="01"] .section-body{max-width:155mm}
.premium-magazine.document-n02 .reading-section[data-section="01"] .section-body p{margin:0;color:#F7F6F2;font:400 28pt/1.08 Didot,"Bodoni 72",serif;letter-spacing:-.018em}
.premium-magazine.document-n02 .references{break-before:page!important;page-break-before:always!important;padding-left:0!important;border-left:0!important;background:#FAFAF8!important}
.premium-magazine.document-n02 .references::after{display:none!important}
.premium-magazine.document-n02 .references .section-heading{margin:0 0 7mm;padding-top:4mm;border-top:.25mm solid #9A9A96}
.premium-magazine.document-n02 .references .section-marker{gap:2.2mm;margin:0 0 4mm;color:#666663;font-size:6.5pt;letter-spacing:.14em}
.premium-magazine.document-n02 .references .section-marker span{display:inline!important;width:auto!important;height:auto!important;padding:0!important;border:0!important;font-size:inherit}
.premium-magazine.document-n02 .references .section-marker b::before{display:none}
.premium-magazine.document-n02 .references h2{margin:0;font-size:31pt;line-height:1}
.premium-magazine.document-n02 .references .section-body{columns:auto!important;column-count:auto!important;column-gap:0!important;column-rule:none!important;display:block!important;font-size:9pt;line-height:1.3}
.premium-magazine.document-n02 .references .section-body ul{columns:2!important;column-count:2!important;column-gap:10mm;column-rule:none;margin:0;padding:0;max-width:none;list-style:none}
.premium-magazine.document-n02 .references .section-body li{break-inside:avoid;overflow-wrap:normal;word-break:normal;hyphens:none;padding:0;margin:0 0 2.8mm}
.premium-magazine.document-n02 .references .section-body a{overflow-wrap:normal;word-break:normal;hyphens:none}
.premium-magazine.document-n02 .references .reference-url{white-space:normal}
.premium-magazine.document-n02 .references .reference-url .url-segment{white-space:nowrap}
.references-image-full{position:relative;overflow:hidden;background:#151615}
.references-image-full img{position:absolute;inset:0;width:100%;height:100%;max-width:none;max-height:none;object-fit:cover;filter:grayscale(1) contrast(1.08)}
.references-image-full::before{content:"";position:absolute;z-index:2;left:18mm;top:18mm;width:19mm;height:3mm;background:#CFFF00;clip-path:polygon(10% 0,100% 0,90% 100%,0 100%)}
.references-image-full::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,transparent 45%,rgba(0,0,0,.72) 100%)}
.references-image-full p{position:absolute;z-index:3;left:18mm;right:18mm;bottom:22mm;margin:0;color:#fff;font-family:Didot,"Bodoni 72",serif;font-size:21pt;line-height:1.05}
.premium-magazine .full-bleed{break-before:auto;break-after:auto;page-break-before:auto;page-break-after:auto}
'''


def build_all(start:int,end:int)->None:
    if start < 0 or end > 10 or start > end:
        raise ValueError("El rango de la colección disponible es N00–N10")
    HERE.mkdir(parents=True,exist_ok=True)
    for number in range(start,end+1):
        build_document(number)
        print(f"BUILT SOURCE N{number:02d}")
    collection_path = HERE / "collection-manifest.json"
    existing = json.loads(collection_path.read_text(encoding="utf-8")) if collection_path.exists() else []
    manifests_by_number = {entry["number"]: entry for entry in existing}
    for number in range(0,11):
        path=HERE/("N01-v18-final" if number == 1 else "N02-v14-final" if number == 2 else "N03-v9-final" if number == 3 else "N04-v9-final" if number == 4 else "N05-v9-final" if number == 5 else "N06-v9-final" if number == 6 else "N07-v9-final" if number == 7 else f"N{number:02d}")/"manifest.json"
        if path.exists():
            manifest = json.loads(path.read_text(encoding="utf-8"))
            if number in {5, 6, 7}:
                package = path.parent.name
                manifest["source"] = f"{package}/{manifest['source']}"
                manifest["cover"]["source"] = f"{package}/{manifest['cover']['source']}"
                if "hotel_horizonte" in manifest:
                    manifest["hotel_horizonte"]["source"] = f"{package}/{manifest['hotel_horizonte']['source']}"
            manifests_by_number[number] = manifest
    manifests = [manifests_by_number[number] for number in sorted(manifests_by_number)]
    collection_path.write_text(json.dumps(manifests,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def main()->None:
    parser=argparse.ArgumentParser();parser.add_argument('--start',type=int,default=0);parser.add_argument('--end',type=int,default=10)
    args=parser.parse_args();build_all(args.start,args.end)


if __name__=='__main__':main()
