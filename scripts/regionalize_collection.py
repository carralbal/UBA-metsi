#!/usr/bin/env python3
"""Create a source-faithful regionalized layer for METSI N01-N36.

The script never edits the approved canonical packages. It creates a new,
auditable source layer, adds one situated section, completes the bibliography
to at least one third regional sources, and sets two of six featured referents
for N11-N36. N01-N10 visual selection is handled by build_collection.py.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "regionalized-sources"
MANIFEST = ROOT / "academic-content-regionalization-manifest-n01-n36.json"


SOURCE_PATHS = {
    1: "N01-v18-final/source/N01_metodologia_sin_recetas-content-final.md",
    2: "N02-v15-final/source/N02_el_sistema_no_cabe_en_una_aplicacion-content-final-v2.md",
    3: "N03-v10-final/source/N03_fronteras_retroalimentacion_y_efectos-content-final-v2.md",
    4: "N04-v9-final/source/N04_hechos_sintomas_relatos_hipotesis_y_decisiones-content-final.md",
    5: "N05-v10-final/source/N05_actores_afectados_poder_y_perspectivas-content-final-v2.md",
    6: "N06-v10-final/source/N06_discovery_como_reduccion_de_incertidumbre-content-final-v2.md",
    7: "N07-v10-final/source/N07_entrevistar_no_es_pedir_requisitos-content-final.md",
    8: "N08-v10-final/source/N08_observar_el_trabajo_invisible-content-final-v2.md",
    9: "N09-v10-final/source/N09_experiencia_accesibilidad_y_adopcion-content-final-v2.md",
    10: "N10-v9-final/source/N10_construir_el_problema_y_outcomes-content-final.md",
}


REGIONAL_REFERENCES = {
    "garcia": "García, R. (2006). *Sistemas complejos: conceptos, método y fundamentación epistemológica de la investigación interdisciplinaria*. Gedisa.",
    "bunge": "Bunge, M. (2004). *Emergencia y convergencia: novedad cualitativa y unidad del conocimiento*. Gedisa.",
    "maturana": "Maturana, H. R. y Varela, F. J. (1984). *El árbol del conocimiento: las bases biológicas del entendimiento humano*. Editorial Universitaria.",
    "flores": "Flores, F. (1997). *Creando organizaciones para el futuro*. Dolmen.",
    "freire": "Freire, P. (2005). *Pedagogía del oprimido*. Siglo XXI Editores.",
    "etkin": "Etkin, J. y Schvarstein, L. (1989). *Identidad de las organizaciones: invariancia y cambio*. Paidós.",
    "scolari": "Scolari, C. A. (2018). *Las leyes de la interfaz: diseño, ecología, evolución, tecnología*. Gedisa.",
    "varsavsky": "Varsavsky, O. (1972). *Hacia una política científica nacional*. Ediciones Periferia.",
    "ricaurte": "Ricaurte, P. (2019). “Data Epistemologies, the Coloniality of Power, and Resistance”. *Television & New Media*, 20(4), 350–365. https://doi.org/10.1177/1527476419831640",
    "sosa": "Sosa Escudero, W. (2019). *Big Data: breve manual para conocer la ciencia de datos que ya invadió nuestras vidas*. Siglo XXI Editores.",
    "fals_borda": "Fals Borda, O. (1987). “The Application of Participatory Action-Research in Latin America”. *International Sociology*, 2(4), 329–347. https://doi.org/10.1177/026858098700200401",
    "echeverria": "Echeverría, R. (2005). *Ontología del lenguaje*. Granica.",
    "quijano": "Quijano, A. (2000). “Colonialidad del poder, eurocentrismo y América Latina”. En E. Lander (comp.), *La colonialidad del saber: eurocentrismo y ciencias sociales*. CLACSO.",
    "cepal": "CEPAL (2022). *Un camino digital para el desarrollo sostenible de América Latina y el Caribe*. Naciones Unidas.",
}


REGIONAL_MARKERS = (
    "garcía, r.", "bunge, m.", "maturana", "varela, f.", "flores, f.",
    "freire, p.", "etkin, j.", "schvarstein", "scolari", "varsavsky",
    "ricaurte", "sosa escudero", "fals borda", "echeverría", "echeverria",
    "quijano", "cepal", "clacso", "república argentina", "argentina — ley",
    "unesco iesalc",
)


BLOCK_POOLS = {
    "A": ["garcia", "bunge", "maturana", "etkin", "flores", "freire", "varsavsky", "echeverria", "fals_borda", "scolari", "ricaurte", "cepal", "quijano", "sosa"],
    "B": ["freire", "fals_borda", "scolari", "ricaurte", "maturana", "garcia", "etkin", "echeverria", "quijano", "bunge", "flores", "cepal", "sosa", "varsavsky"],
    "C": ["bunge", "flores", "garcia", "scolari", "maturana", "etkin", "sosa", "echeverria", "varsavsky", "ricaurte", "cepal", "freire", "quijano", "fals_borda"],
    "D": ["flores", "varsavsky", "etkin", "bunge", "garcia", "maturana", "echeverria", "freire", "scolari", "cepal", "fals_borda", "ricaurte", "quijano", "sosa"],
    "E": ["flores", "scolari", "etkin", "varsavsky", "freire", "garcia", "bunge", "maturana", "cepal", "echeverria", "fals_borda", "ricaurte", "quijano", "sosa"],
    "F": ["flores", "bunge", "garcia", "scolari", "etkin", "maturana", "varsavsky", "cepal", "echeverria", "sosa", "ricaurte", "freire", "quijano", "fals_borda"],
    "G": ["ricaurte", "sosa", "freire", "bunge", "quijano", "cepal", "scolari", "garcia", "maturana", "varsavsky", "etkin", "flores", "fals_borda", "echeverria"],
    "H": ["freire", "maturana", "garcia", "bunge", "etkin", "flores", "fals_borda", "scolari", "varsavsky", "echeverria", "ricaurte", "quijano", "cepal", "sosa"],
}


VISUAL_PAIRS = {
    "A": ("Mario Bunge", "Humberto Maturana"),
    "B": ("Paulo Freire", "Fernando Flores"),
    "C": ("Mario Bunge", "Fernando Flores"),
    "D": ("Fernando Flores", "Mario Bunge"),
    "E": ("Fernando Flores", "Paulo Freire"),
    "F": ("Fernando Flores", "Mario Bunge"),
    "G": ("Paulo Freire", "Mario Bunge"),
    "H": ("Paulo Freire", "Humberto Maturana"),
}

REFERENT_KEYS = {
    "Mario Bunge": "bunge",
    "Humberto Maturana": "maturana",
    "Fernando Flores": "flores",
    "Paulo Freire": "freire",
}


REFERENT_DESCRIPTIONS = {
    "Mario Bunge": "Exige conceptos precisos, mecanismos discutibles y evidencia capaz de distinguir una explicación de una etiqueta técnica.",
    "Humberto Maturana": "Muestra que conocer y coordinar no son actos externos al sistema: dependen de distinciones, lenguaje e historia compartida.",
    "Fernando Flores": "Vincula lenguaje, compromisos y tecnología para observar cómo una organización promete, coordina y repara acciones.",
    "Paulo Freire": "Une reflexión, diálogo y acción situada para que las personas afectadas participen en la comprensión y transformación del problema.",
}


SITUATED_SECTIONS = {
    "A": """## Una lectura situada desde América Latina

Rolando García ayuda a mirar un sistema como una construcción del problema y no como una lista de componentes. Una frontera sirve si permite explicar relaciones que importan para decidir. Mario Bunge agrega una exigencia: nombrar un mecanismo no alcanza; hay que mostrar cómo produciría el efecto y qué observación lo pondría en duda. En simple, decir «falló el sistema» es demasiado amplio. Hay que poder señalar qué relación falló, para quién y bajo qué condiciones.

Humberto Maturana y Francisco Varela recuerdan que quienes observan también forman parte de la situación que describen. Jorge Etkin y Leonardo Schvarstein permiten reconocer que una organización conserva identidades, reglas y tensiones aun cuando cambian sus pantallas. En Hotel Horizonte, una nueva aplicación puede modificar el trabajo sin cambiar la promesa comercial, o cambiar la promesa sin resolver la coordinación. La lectura regional obliga a verificar ambas cosas antes de llamar solución a una intervención.
""",
    "B": """## Una lectura situada desde América Latina

Paulo Freire y Orlando Fals Borda proponen conocer con las personas involucradas, no sólo obtener información de ellas. En simple: una entrevista no es un buzón de pedidos y una observación no convierte a alguien en objeto de estudio. La investigación debe permitir que las personas expliquen, cuestionen y revisen la interpretación que se construye sobre su trabajo.

Carlos Scolari muestra que una interfaz organiza relaciones y no sólo botones. Paola Ricaurte agrega que categorías y datos distribuyen poder: deciden qué experiencia aparece como normal y cuál queda fuera. En Hotel Horizonte, escuchar a Recepción, Housekeeping y huéspedes no sirve si el registro sólo admite los estados definidos por el proveedor. La evidencia mejora cuando el vocabulario, los casos y las decisiones también pueden discutirse.
""",
    "C": """## Una lectura situada desde América Latina

Mario Bunge propone distinguir con precisión conceptos, hechos y mecanismos. Fernando Flores muestra que muchos sistemas de información coordinan compromisos expresados en lenguaje. En simple: un modelo no es correcto porque tenga muchas cajas; sirve cuando permite saber quién prometió qué, qué condición cambió y quién puede actuar ante una excepción.

Rolando García ayuda a no separar el modelo de la situación que intenta explicar. Carlos Scolari permite leer diagramas e interfaces como dispositivos que hacen visibles algunas relaciones y ocultan otras. En Hotel Horizonte, «habitación liberada», «disponible» y «asignable» pueden parecer equivalentes en un diagrama y producir decisiones distintas en la operación. Modelar exige conservar esa diferencia y probarla con episodios reales.
""",
    "D": """## Una lectura situada desde América Latina

Fernando Flores permite leer una estrategia como una red de compromisos, no como una secuencia de tareas. Oscar Varsavsky agrega una pregunta incómoda: quién define qué problema merece recursos y qué futuro se considera deseable. En simple, elegir una metodología también es elegir qué se aprende primero, qué riesgo se acepta y quién espera.

Jorge Etkin y Leonardo Schvarstein muestran que el cambio convive con identidades y contradicciones organizacionales. Mario Bunge exige que las decisiones conserven una explicación y una prueba posible. En Hotel Horizonte, combinar enfoques predictivos y adaptativos puede ser razonable, pero sólo si cada uno tiene propósito, evidencia esperada, autoridad y condición de salida. El nombre del método no reemplaza esa justificación.
""",
    "E": """## Una lectura situada desde América Latina

Fernando Flores ayuda a pensar productos y servicios como compromisos sostenidos entre personas y organizaciones. Carlos Scolari muestra que la interfaz es una red de relaciones que distribuye capacidades. En simple, un producto no vale por la cantidad de funciones: vale cuando alguien puede lograr un resultado, comprender el estado y obtener reparación si algo falla.

Oscar Varsavsky invita a preguntar qué necesidades y poblaciones orientan la inversión. Paulo Freire recuerda que participar no es validar una solución ya decidida. En Hotel Horizonte, priorizar una llegada accesible puede exigir renunciar a otra función visible. La decisión se vuelve defendible cuando declara quién se beneficia, quién espera, qué evidencia se observará y cuándo volverá a revisarse.
""",
    "F": """## Una lectura situada desde América Latina

Fernando Flores permite ver la operación como una red de pedidos, promesas, condiciones de satisfacción y reparaciones. Mario Bunge exige explicar mecanismos, no confundir una señal técnica con el resultado del servicio. En simple, que un servidor responda no demuestra que un huésped pueda entrar a su habitación.

Rolando García ayuda a reconstruir relaciones entre tecnología, reglas, proveedores y trabajo humano. La CEPAL sitúa esas decisiones en economías con capacidades e infraestructuras desiguales. En Hotel Horizonte, integrar o automatizar sin observar dependencias locales puede trasladar el problema a otra capa. Operar bien implica conservar identidad, evidencia, límites y una salida practicable cuando el contexto real contradice el diseño.
""",
    "G": """## Una lectura situada desde América Latina

Paola Ricaurte muestra que los datos y los sistemas de inteligencia artificial también organizan quién puede conocer, clasificar y decidir. Walter Sosa Escudero ayuda a separar el tamaño de los datos de la calidad de una inferencia. En simple, muchas filas y una respuesta fluida no garantizan que la decisión sea justa, pertinente ni correcta para la población local.

Paulo Freire exige que las personas afectadas puedan comprender y discutir la intervención. Mario Bunge pide que una afirmación conserve evidencia y condiciones de refutación. En Hotel Horizonte, evaluar una IA incluye idioma, categorías, severidad del daño, capacidad de supervisión y reparación. Una métrica global puede orientar, pero no reemplaza probar tareas y consecuencias en el contexto donde el sistema actuará.
""",
    "H": """## Una lectura situada desde América Latina

Paulo Freire une reflexión y acción: aprender no es recibir una respuesta terminada, sino revisar una interpretación con otros y transformar la práctica. Humberto Maturana y Francisco Varela muestran que esa revisión cambia las distinciones con las que un equipo observa. En simple, una retrospectiva sirve cuando modifica la próxima decisión, no cuando sólo archiva conclusiones.

Rolando García ayuda a integrar perspectivas sin borrar sus desacuerdos. Mario Bunge exige que la síntesis conserve mecanismos, evidencia y límites. En Hotel Horizonte, cerrar el expediente significa poder recorrer la cadena desde la promesa hasta la consecuencia y también desde el incidente hasta la decisión que lo hizo posible. Si una voz afectada o una contradicción desaparece para que el relato quede prolijo, la integración todavía está incompleta.
""",
}


def block_for(number: int) -> str:
    if number <= 4:
        return "A"
    if number <= 10:
        return "B"
    if number <= 16:
        return "C"
    if number <= 20:
        return "D"
    if number <= 25:
        return "E"
    if number <= 30:
        return "F"
    if number <= 33:
        return "G"
    return "H"


def load_sources() -> dict[int, Path]:
    result = {number: ROOT / rel for number, rel in SOURCE_PATHS.items()}
    academic = json.loads((ROOT / "academic-content-revision-manifest-n11-n36.json").read_text())
    for item in academic["documents"]:
        number = int(item["code"][1:])
        result[number] = ROOT / item["source"]
    return result


def reference_lines(text: str) -> list[str]:
    tail = text.split("## Referencias base", 1)[1]
    return [line.strip() for line in tail.splitlines() if line.strip().startswith("-")]


def is_regional(reference: str) -> bool:
    folded = reference.casefold()
    return any(marker in folded for marker in REGIONAL_MARKERS)


def ensure_references(text: str, block: str) -> tuple[str, int, int, list[str]]:
    existing = reference_lines(text)
    regional = [ref for ref in existing if is_regional(ref)]
    additions: list[str] = []
    existing_folded = "\n".join(existing).casefold()
    required = [REFERENT_KEYS[name] for name in VISUAL_PAIRS[block]]
    pool = required + [key for key in BLOCK_POOLS[block] if key not in required]
    for key in pool:
        quota_met = len(regional) + len(additions) >= math.ceil((len(existing) + len(additions)) / 3)
        if quota_met and key not in required:
            break
        entry = REGIONAL_REFERENCES[key]
        surname = entry.split(",", 1)[0].casefold()
        if surname in existing_folded:
            continue
        additions.append("- " + entry)
        existing_folded += "\n" + entry.casefold()
    final_total = len(existing) + len(additions)
    final_regional = len(regional) + len(additions)
    if not (1 / 3 <= final_regional / final_total <= 1 / 2):
        raise ValueError((len(existing), len(regional), len(additions), final_total, final_regional))
    text = text.rstrip() + "\n\n" + "\n".join(additions) + "\n"
    return text, final_total, final_regional, additions


def replace_referents(text: str, block: str) -> str:
    if "## Referentes" not in text:
        return text
    before, rest = text.split("## Referentes", 1)
    body, after = rest.split("## Referencias base", 1)
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", body) if part.strip()]
    if len(paragraphs) != 6:
        raise ValueError(f"Se esperaban seis referentes; se encontraron {len(paragraphs)}")
    names = VISUAL_PAIRS[block]
    regional = [f"**{name}.** {REFERENT_DESCRIPTIONS[name]}" for name in names]
    kept = []
    for paragraph in paragraphs:
        if any(name.casefold() in paragraph.casefold() for name in names):
            continue
        kept.append(paragraph)
        if len(kept) == 4:
            break
    return before + "## Referentes\n\n" + "\n\n".join(regional + kept) + "\n\n## Referencias base" + after


def regionalize(number: int, source: Path) -> dict:
    block = block_for(number)
    text = source.read_text(encoding="utf-8")
    if "## Una lectura situada desde América Latina" in text:
        raise ValueError(f"{source} ya contiene la sección regional")
    text = text.replace("\n## Síntesis\n", "\n" + SITUATED_SECTIONS[block] + "\n## Síntesis\n", 1)
    if number >= 11:
        text = replace_referents(text, block)
    text, total, regional, additions = ensure_references(text, block)
    target_dir = OUT / f"N{number:02d}"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / (source.stem + "-regional-v1.md")
    target.write_text(text, encoding="utf-8")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    return {
        "code": f"N{number:02d}",
        "block": block,
        "source_base": str(source.relative_to(ROOT)),
        "source": str(target.relative_to(ROOT)),
        "sha256": digest,
        "references_total": total,
        "references_regional": regional,
        "regional_percentage": round(100 * regional / total, 1),
        "featured_regional_referents": list(VISUAL_PAIRS[block]),
        "references_added": [line[2:] for line in additions],
    }


def main() -> None:
    sources = load_sources()
    if set(sources) != set(range(1, 37)):
        raise ValueError(f"Fuentes incompletas: {sorted(sources)}")
    documents = [regionalize(number, sources[number]) for number in range(1, 37)]
    manifest = {
        "schema_version": 1,
        "created_at": "2026-09-15",
        "scope": "N01-N36; N00 excluded because it is the reading guide",
        "policy": "30-50% regional bibliography and 2/6 regional featured referents per reading",
        "documents": documents,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"documents": len(documents), "min": min(d["regional_percentage"] for d in documents), "max": max(d["regional_percentage"] for d in documents)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
