#!/usr/bin/env python3
"""Audita capas de entrada llana y ejemplo en conceptos N00–N36.

La heurística no aprueba contenido por sí sola: localiza unidades que necesitan
revisión humana y deja evidencia reproducible antes y después de la reescritura.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORD_RE = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+(?:[-'][A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+)*")
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
HEADING_RE = re.compile(r"^(#{2,4})\s+(.+?)\s*$")

STRUCTURAL = {
    "pregunta profesional", "tesis", "síntesis", "cinco píldoras para recordar",
    "glosario esencial", "preguntas de preparación", "referentes", "referencias base",
    "consecuencias profesionales", "límites y tensiones", "errores frecuentes",
}
STRUCTURAL_PREFIXES = (
    "movimiento ", "parte ", "de n", "primera aplicación", "segunda aplicación",
    "tercera aplicación", "caso de transferencia", "contraejemplo", "instrumento ",
    "prueba integral", "hotel horizonte", "hh-", "paso ", "episodio", "tu turno",
    "resolución de ", "tradiciones y marcos", "las ideas que sostienen", "bloque ",
    "componentes de una lectura", "cuatro tipos de ", "seis tipos de ",
    "una taxonomía", "tres usos defectuosos", "familias de ", "cuatro encuadres",
    "método de construcción",
)
PLAIN_MARKERS = (
    "en pocas palabras", "dicho de otro modo", "en términos simples", "en simple",
    "significa", "sirve para", "podemos pensarlo", "puede pensarse", "es como",
    "se llama", "no es más que", "en la práctica",
)
EXAMPLE_MARKERS = (
    "por ejemplo", "imaginemos", "imaginá", "supongamos", "como cuando",
    "un caso simple", "ejemplo simple", "en hotel horizonte", "en hh-",
    "una estudiante", "un estudiante", "una persona", "un equipo",
)
CONCRETE_MARKERS = (
    "hotel", "hh-", "huésped", "reserva", "habitación", "recepción", "housekeeping",
    "pms", "cerradura", "turno", "estudiante", "universidad", "hospital", "paciente",
    "cliente", "proveedor", "equipo", "pantalla", "formulario", "mensaje", "correo",
    "tablero", "incidente", "trámite", "compra", "pago", "llamada", "operador",
    "persona", "empresa", "servicio", "producto", "código", "interfaz", "fotografía",
    "entrevista", "árbol", "plano", "documento",
    "facultad", "chatbot", "clasificador", "modelo", "matriz", "prototipo", "herramienta",
)


def normalize_heading(text: str) -> str:
    return re.sub(r"[*_`“”\"'«»]", "", text).strip().lower()


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def source_for(code: str) -> Path:
    number = int(code[1:])
    expanded_early_sources = {
        2: "N02_el_sistema_no_cabe_en_una_aplicacion-content-final-v2.md",
        3: "N03_fronteras_retroalimentacion_y_efectos-content-final-v2.md",
        5: "N05_actores_afectados_poder_y_perspectivas-content-final-v2.md",
        6: "N06_discovery_como_reduccion_de_incertidumbre-content-final-v2.md",
        8: "N08_observar_el_trabajo_invisible-content-final-v2.md",
        9: "N09_experiencia_accesibilidad_y_adopcion-content-final-v2.md",
    }
    # N01–N10 continuaron su revisión en los paquetes content-final; N11–N36
    # usan content-canonical como autoridad. N00 conserva su raíz canónica.
    folder = ROOT / (
        "N00-v3-final" if number == 0
        else f"{code}-content-final" if number <= 10
        else f"{code}-content-canonical"
    )
    if number in expanded_early_sources:
        return folder / "source" / expanded_early_sources[number]
    manifest = json.loads((folder / "source-manifest.json").read_text(encoding="utf-8"))
    return folder / manifest["source"]


def parse_sections(text: str) -> list[dict]:
    lines = text.splitlines()
    headings: list[tuple[int, int, str]] = []
    for i, line in enumerate(lines):
        match = HEADING_RE.match(line)
        if match:
            headings.append((i, len(match.group(1)), match.group(2)))
    sections = []
    for pos, (line_no, level, title) in enumerate(headings):
        end = headings[pos + 1][0] if pos + 1 < len(headings) else len(lines)
        body_lines = lines[line_no + 1:end]
        body = "\n".join(body_lines).strip()
        paragraphs = [
            re.sub(r"\s+", " ", p).strip()
            for p in re.split(r"\n\s*\n", body)
            if p.strip() and not p.lstrip().startswith(("|", "- ", "* ", ">", "!["))
        ]
        sections.append({
            "line": line_no + 1,
            "level": level,
            "title": title,
            "body": body,
            "paragraphs": paragraphs,
        })
    return sections


def is_concept(section: dict, previous_h2: str) -> bool:
    title = normalize_heading(section["title"])
    if not section["paragraphs"] or title in STRUCTURAL or title.startswith(STRUCTURAL_PREFIXES):
        return False
    if section["level"] >= 3 and previous_h2.startswith("errores frecuentes"):
        return False
    if section["level"] == 4:
        return len(section["paragraphs"]) >= 1 and not title.startswith(("documento ", "criterio "))
    if section["level"] == 3:
        return True
    conceptual_h2_markers = (
        "metodología", "sistema", "frontera", "evidencia", "experiencia", "diseño",
        "calidad", "flujo", "estrategia", "método", "poder", "incertidumbre",
        "modelo", "proceso", "contrato", "observabilidad", "aprendizaje", "ia",
        "inteligencia artificial", "intervención", "producto", "plataforma",
    )
    return any(marker in title for marker in conceptual_h2_markers)


def inspect(section: dict) -> dict:
    paragraphs = section["paragraphs"]
    lead = " ".join(paragraphs[:2]).lower()
    scope = " ".join(paragraphs[:4]).lower()
    sentences = [s.strip() for s in SENTENCE_RE.split(" ".join(paragraphs[:3])) if s.strip()]
    sentence_lengths = [len(words(s)) for s in sentences]
    short_sentence = any(5 <= length <= 24 for length in sentence_lengths[:4])
    has_plain_marker = any(marker in lead for marker in PLAIN_MARKERS)
    has_explicit_plain = "en simple: " in scope or "en simple, con un ejemplo: " in scope
    has_explicit_example = "ejemplo cercano: " in scope or "en simple, con un ejemplo: " in scope
    has_example = (
        any(marker in scope for marker in EXAMPLE_MARKERS)
        or any(marker in scope for marker in CONCRETE_MARKERS)
        or bool(re.search(r"[«“\"]|\b\d+[\s%:.]", scope))
    )
    long_word_ratio = 0.0
    lead_words = words(" ".join(paragraphs[:2]))
    if lead_words:
        long_word_ratio = sum(len(w) >= 12 for w in lead_words) / len(lead_words)
    has_plain_entry = short_sentence and (has_plain_marker or long_word_ratio <= 0.12)
    risks = []
    if not paragraphs:
        risks.append("sin_desarrollo")
    if not has_plain_entry:
        risks.append("sin_entrada_llana_clara")
    if not has_example:
        risks.append("sin_ejemplo_cercano_en_apertura")
    if not has_explicit_plain:
        risks.append("sin_capa_llana_explicita")
    if not has_explicit_example:
        risks.append("sin_ejemplo_explicito")
    if sentence_lengths and sum(sentence_lengths) / len(sentence_lengths) > 32:
        risks.append("oraciones_iniciales_extensas")
    return {
        "line": section["line"],
        "level": section["level"],
        "title": section["title"],
        "paragraph_words": sum(len(words(p)) for p in paragraphs),
        "initial_avg_sentence_words": round(sum(sentence_lengths) / len(sentence_lengths), 1) if sentence_lengths else 0,
        "initial_long_word_ratio": round(long_word_ratio, 3),
        "plain_entry": has_plain_entry,
        "near_example": has_example,
        "explicit_plain_layer": has_explicit_plain,
        "explicit_near_example": has_explicit_example,
        "risks": risks,
        "status": "pass" if not risks else "review",
    }


def audit_document(code: str) -> dict:
    source = source_for(code)
    text = source.read_text(encoding="utf-8")
    sections = parse_sections(text)
    previous_h2 = ""
    error_level = 99
    concepts = []
    for section in sections:
        normalized = normalize_heading(section["title"])
        if section["level"] <= error_level and normalized != "errores frecuentes":
            error_level = 99
        if normalized == "errores frecuentes":
            error_level = section["level"]
        if section["level"] == 2:
            previous_h2 = normalized
        if section["level"] > error_level:
            continue
        if is_concept(section, previous_h2):
            concepts.append(inspect(section))
    passed = sum(item["status"] == "pass" for item in concepts)
    return {
        "document": code,
        "source": str(source.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "concept_units": len(concepts),
        "passed": passed,
        "review": len(concepts) - passed,
        "pass_rate": round(passed / len(concepts), 3) if concepts else 0,
        "concepts": concepts,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="editorial-standard/pedagogical-accessibility-audit-n00-n36.json")
    args = parser.parse_args()
    documents = [audit_document(f"N{i:02d}") for i in range(37)]
    report = {
        "standard": "editorial-standard/ACCESSIBLE-CONCEPT-LAYERS-STANDARD.md",
        "scope": "N00-N36",
        "method": "heuristic_candidates_plus_human_editorial_review",
        "summary": {
            "documents": len(documents),
            "concept_units": sum(d["concept_units"] for d in documents),
            "passed": sum(d["passed"] for d in documents),
            "review": sum(d["review"] for d in documents),
        },
        "documents": documents,
    }
    output = ROOT / args.output
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
