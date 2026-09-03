#!/usr/bin/env python3
"""Controles deterministas para el manuscrito canónico de N06.

Este validador no compone ni inspecciona PDF. Sólo controla la fuente Markdown
y escribe un informe JSON reproducible.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source" / "N06_discovery_como_reduccion_de_incertidumbre-content-final.md"
REPORT = ROOT / "provenance" / "integrity-report.json"
MANIFEST = ROOT / "source-manifest.json"


def words(text: str) -> list[str]:
    return re.findall(
        r"\b[\wÁÉÍÓÚÜÑáéíóúüñ]+(?:[-‑][\wÁÉÍÓÚÜÑáéíóúüñ]+)*\b",
        text,
        flags=re.UNICODE,
    )


def check(name: str, passed: bool, evidence: object) -> dict[str, object]:
    return {"check": name, "result": "pass" if passed else "fail", "evidence": evidence}


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    before_references, references = text.split("## Referencias base", 1)
    substantive = text[text.index("## Tesis") : text.index("## Cinco píldoras para recordar")]
    headings = re.findall(r"^(#{1,4}) (.+)$", text, flags=re.MULTILINE)
    heading_names = [name for _, name in headings]

    required_order = [
        "Pregunta profesional",
        "La médica que pidió un estudio menos",
        "Tesis",
        "De N05 a N06: de los actores a una estrategia de aprendizaje",
        "Movimiento 1 · Formular incertidumbres que puedan cambiar una decisión",
        "Movimiento 2 · Diseñar una cartera mínima de evidencia",
        "Movimiento 3 · Decidir con evidencia suficiente y riesgo residual",
        "Caso de transferencia: alertas de abandono universitario",
        "Errores frecuentes",
        "Consecuencias profesionales",
        "Límites y tensiones",
        "Síntesis",
        "Cinco píldoras para recordar",
        "Glosario esencial",
        "Preguntas de preparación",
        "Referencias base",
    ]
    positions = [heading_names.index(item) for item in required_order]

    reference_lines = [line for line in references.splitlines() if line.startswith("- ")]
    anchors = {
        "DORA (2025)": r"\bDORA \(2025\)",
        "Hubbard (2014)": r"\bHubbard \(2014\)",
        "ISO 9241-210:2019": r"ISO 9241-210:2019",
        "March (1991)": r"\bMarch \(1991\)",
        "Patton (2015)": r"\bPatton \(2015\)",
        "Ries (2011)": r"\bRies \(2011\)",
        "Schön (1983)": r"\bSchön \(1983\)",
        "NIST AI RMF 1.0 (2023)": r"NIST \(Tabassi, 2023\)",
        "Torres (2021)": r"\bTorres \(2021\)",
        "Tversky y Kahneman (1974)": r"Tversky y Kahneman \(1974\)",
    }
    anchor_results = {
        key: bool(re.search(pattern, before_references, flags=re.IGNORECASE))
        for key, pattern in anchors.items()
    }

    pills_block = text[text.index("## Cinco píldoras para recordar") : text.index("## Glosario esencial")]
    questions_block = text[text.index("## Preguntas de preparación") : text.index("## Referencias base")]
    pill_count = len(re.findall(r"^\d+\. \*\*", pills_block, flags=re.MULTILINE))
    question_count = len(re.findall(r"^\d+\. ¿", questions_block, flags=re.MULTILINE))
    urls = re.findall(r"https://[^\s)]+", references)
    placeholders = {
        token: len(re.findall(re.escape(token), text, flags=re.IGNORECASE))
        for token in ("TBD", "lorem", "XXX", "[TODO]")
    }
    prose_dash_lines = [
        number
        for number, line in enumerate(before_references.splitlines(), 1)
        if " — " in line or " – " in line
    ]
    second_person_hits = re.findall(
        r"\b(?:vos|tú|usted|ustedes|podés|deberías|hacé|mirá|situá|seleccioná|usarías|convertirías)\b",
        before_references,
        flags=re.IGNORECASE,
    )
    first_person_plural_hits = re.findall(
        r"\b(?:nos|nuestro|nuestra|nuestros|nuestras|podemos|pensemos|aprendimos|veamos|recordemos|hagamos)\b",
        before_references,
        flags=re.IGNORECASE,
    )
    deferred_terms = re.findall(r"\boutcomes?\b", before_references, flags=re.IGNORECASE)
    english_residue = re.findall(
        r"\b(?:dashboard|cloud|logs?|backlog|portfolio|insights?|rollback|fallback|score)\b",
        before_references,
        flags=re.IGNORECASE,
    )
    operational_fields = [
        "decisión asociada",
        "evidencia disponible",
        "próxima acción",
        "responsable",
        "fecha de revisión",
        "criterio de parada",
        "riesgo residual",
    ]
    repeated_paragraphs = []
    paragraph_seen: dict[str, int] = {}
    for paragraph in re.split(r"\n\s*\n", before_references):
        normalized = re.sub(r"\s+", " ", paragraph.strip())
        if len(words(normalized)) < 20 or normalized.startswith(("#", "|", "- ", "1. ")):
            continue
        if normalized in paragraph_seen:
            repeated_paragraphs.append((paragraph_seen[normalized], normalized[:90]))
        else:
            paragraph_seen[normalized] = len(paragraph_seen) + 1

    results = [
        check("canonical_heading_order", positions == sorted(positions), required_order),
        check("three_movement_architecture", sum(name.startswith("Movimiento ") for name in heading_names) == 3, positions[4:7]),
        check("substantive_word_floor", len(words(substantive)) >= 6000, len(words(substantive))),
        check("total_word_count", 7600 <= len(words(text)) <= 9000, len(words(text))),
        check("hotel_horizonte_conductor", before_references.count("HH-06") >= 6 and before_references.count("Hotel Horizonte") >= 4, {"HH-06": before_references.count("HH-06"), "Hotel Horizonte": before_references.count("Hotel Horizonte")}),
        check("three_hh06_applications", len(re.findall(r"^### (?:Primera|Segunda|Tercera) aplicación de HH-06", before_references, flags=re.MULTILINE)) == 3, 3),
        check("operational_strategy_fields", all(field in before_references for field in operational_fields), operational_fields),
        check("reference_count", len(reference_lines) == len(anchors) == 10, len(reference_lines)),
        check("all_references_anchored", all(anchor_results.values()), anchor_results),
        check("five_pills", pill_count == 5, pill_count),
        check("six_questions", question_count == 6, question_count),
        check("preparation_instruction", "dos de las seis preguntas" in questions_block and "tablero HH-06" in questions_block, "present" if "tablero HH-06" in questions_block else "missing"),
        check("no_placeholders", all(value == 0 for value in placeholders.values()), placeholders),
        check("no_prose_dashes", not prose_dash_lines, prose_dash_lines),
        check("impersonal_register", not second_person_hits and not first_person_plural_hits, {"second_person": second_person_hits, "first_person_plural": first_person_plural_hits}),
        check("n10_term_not_anticipated", not deferred_terms, deferred_terms),
        check("anglicisms_normalized", not english_residue, english_residue),
        check("no_exact_duplicate_paragraphs", not repeated_paragraphs, repeated_paragraphs),
        check("urls_unique", len(urls) == len(set(urls)), {"count": len(urls), "unique": len(set(urls))}),
        check("content_only_package", not re.search(r"\.(?:pdf|html|css|png|jpe?g)\b", before_references, flags=re.IGNORECASE), "no layout or image artifact references"),
    ]

    payload = {
        "document": "N06",
        "stage": "content-final",
        "source": str(SOURCE.relative_to(ROOT)),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "bytes": SOURCE.stat().st_size,
        "word_counts": {
            "total": len(words(text)),
            "substantive_from_thesis_through_synthesis": len(words(substantive)),
        },
        "references": {"entries": len(reference_lines), "urls": urls, "anchors": anchor_results},
        "results": results,
        "overall": "pass" if all(item["result"] == "pass" for item in results) else "fail",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    h2_matches = list(re.finditer(r"^## (.+)$", text, flags=re.MULTILINE))
    sections = []
    for index, match in enumerate(h2_matches):
        end = h2_matches[index + 1].start() if index + 1 < len(h2_matches) else len(text)
        section_text = text[match.start() : end].strip() + "\n"
        sections.append(
            {
                "order": index + 1,
                "heading": match.group(1),
                "words": len(words(section_text)),
                "sha256": hashlib.sha256(section_text.encode("utf-8")).hexdigest(),
            }
        )
    manifest = {
        "document": "N06",
        "stage": "content-final",
        "title": "Discovery como estrategia de reducción de incertidumbre",
        "language": "es-AR",
        "format": "Markdown source only",
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": payload["sha256"],
        "source_bytes": payload["bytes"],
        "word_counts": payload["word_counts"],
        "sections": sections,
        "reference_entries": len(reference_lines),
        "urls": urls,
        "excluded_artifacts": ["PDF", "HTML", "CSS", "photography", "illustration", "layout"],
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["overall"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
