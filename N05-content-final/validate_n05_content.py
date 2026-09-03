#!/usr/bin/env python3
"""Controles deterministas para el manuscrito canónico de N05.

Este validador no compone ni inspecciona PDF. Sólo controla la fuente Markdown
y escribe un informe JSON reproducible.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source" / "N05_actores_afectados_poder_y_perspectivas-content-final.md"
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
        "La mesa con una silla vacía",
        "Tesis",
        "De N04 a N05: de la afirmación a las relaciones que la sostienen",
        "Movimiento 1 · Pasar de interesados genéricos a relaciones de poder",
        "Movimiento 2 · Diseñar participación capaz de cambiar una decisión",
        "Movimiento 3 · Gobernar objeción, supervisión y reparación",
        "Síntesis",
        "Cinco píldoras para recordar",
        "Glosario esencial",
        "Preguntas de preparación",
        "Referencias base",
    ]
    positions = [heading_names.index(item) for item in required_order]

    reference_lines = [line for line in references.splitlines() if line.startswith("- ")]
    anchors = {
        "Freeman (1984)": r"\bFreeman\b",
        "Winner (1980)": r"\bWinner\b",
        "Fricker (2007)": r"\bFricker\b",
        "Star y Strauss (1999)": r"Star y Strauss",
        "Arnstein (1969)": r"\bArnstein\b",
        "Mumford (2003)": r"\bMumford\b",
        "Costanza-Chock (2020)": r"Costanza-Chock",
        "Suresh et al. (2024)": r"Suresh y sus colegas",
        "NIST AI 100-1 (2023)": r"marco de gestión de riesgos de IA de NIST",
        "Reglamento UE 2024/1689": r"Reglamento europeo de IA",
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
    deferred_terms = re.findall(r"\boutcome\b", before_references, flags=re.IGNORECASE)

    results = [
        check("canonical_heading_order", positions == sorted(positions), required_order),
        check("three_movement_architecture", sum(name.startswith("Movimiento ") for name in heading_names) == 3, positions[4:7]),
        check("substantive_word_floor", len(words(substantive)) >= 6000, len(words(substantive))),
        check("total_word_count", 7600 <= len(words(text)) <= 9200, len(words(text))),
        check("hotel_horizonte_conductor", before_references.count("HH-05") >= 5 and before_references.count("Hotel Horizonte") >= 4, {"HH-05": before_references.count("HH-05"), "Hotel Horizonte": before_references.count("Hotel Horizonte")}),
        check("adc_operational_method", before_references.count("mapa ADC") >= 5 and all(f"Paso {number}." in before_references for number in range(1, 9)), {"mapa ADC": before_references.count("mapa ADC"), "steps": 8}),
        check("reference_count", len(reference_lines) == len(anchors) == 10, len(reference_lines)),
        check("all_references_anchored", all(anchor_results.values()), anchor_results),
        check("five_pills", pill_count == 5, pill_count),
        check("six_questions", question_count == 6, question_count),
        check("preparation_instruction", "dos de las seis preguntas" in questions_block, "present" if "dos de las seis preguntas" in questions_block else "missing"),
        check("no_placeholders", all(value == 0 for value in placeholders.values()), placeholders),
        check("no_prose_dashes", not prose_dash_lines, prose_dash_lines),
        check("impersonal_register", not second_person_hits and not first_person_plural_hits, {"second_person": second_person_hits, "first_person_plural": first_person_plural_hits}),
        check("n10_term_not_anticipated", not deferred_terms, deferred_terms),
        check("urls_unique", len(urls) == len(set(urls)), {"count": len(urls), "unique": len(set(urls))}),
        check("content_only_package", not re.search(r"\.(?:pdf|html|css|png|jpe?g)\b", before_references, flags=re.IGNORECASE), "no layout or image artifact references"),
    ]

    payload = {
        "document": "N05",
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
        "document": "N05",
        "stage": "content-final",
        "title": "Actores, afectados, poder y perspectivas",
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
