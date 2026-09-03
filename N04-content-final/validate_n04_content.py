#!/usr/bin/env python3
"""Controles deterministas para el manuscrito canónico de N04.

Este validador no compone ni inspecciona PDF. Sólo controla la fuente Markdown
y escribe un informe JSON reproducible.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source" / "N04_hechos_sintomas_relatos_hipotesis_y_decisiones-content-final.md"
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
        "El doce por ciento que parecía hablar solo",
        "Tesis",
        "De N03 a N04: del mapa a la justificación",
        "Movimiento 1 · Desarmar una afirmación sin perder su historia",
        "Movimiento 2 · Contrastar explicaciones sin borrar incertidumbre",
        "Movimiento 3 · Decidir y dejar abierta la revisión",
        "Síntesis",
        "Cinco píldoras para recordar",
        "Glosario esencial",
        "Preguntas de preparación",
        "Referencias base",
    ]
    positions = [heading_names.index(item) for item in required_order]

    reference_lines = [line for line in references.splitlines() if line.startswith("- ")]
    anchors = {
        "Toulmin (2003)": r"\bToulmin\b",
        "Peirce (1998)": r"\bPeirce\b",
        "Pearl y Mackenzie (2018)": r"\bPearl\b",
        "ISO/IEC 25012:2008": r"ISO/IEC 25012",
        "Wang y Strong (1996)": r"Wang y Strong",
        "Schön (1983)": r"\bSchön\b",
        "NIST AI 100-1 (2023)": r"AI Risk Management Framework 1\.0 de NIST",
        "NIST AI 600-1 (2024)": r"NIST AI 600-1",
        "NIST AI 100-4 (2024)": r"NIST AI 100-4",
        "C2PA 2.4 (2026)": r"\bC2PA\b",
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

    results = [
        check("canonical_heading_order", positions == sorted(positions), required_order),
        check("three_movement_architecture", sum(name.startswith("Movimiento ") for name in heading_names) == 3, positions[4:7]),
        check("substantive_word_floor", len(words(substantive)) >= 6000, len(words(substantive))),
        check("total_word_count", 8000 <= len(words(text)) <= 10500, len(words(text))),
        check("hotel_horizonte_conductor", before_references.count("HH-04") >= 5 and before_references.count("Hotel Horizonte") >= 4, {"HH-04": before_references.count("HH-04"), "Hotel Horizonte": before_references.count("Hotel Horizonte")}),
        check("reference_count", len(reference_lines) == len(anchors) == 10, len(reference_lines)),
        check("all_references_anchored", all(anchor_results.values()), anchor_results),
        check("five_pills", pill_count == 5, pill_count),
        check("six_questions", question_count == 6, question_count),
        check("preparation_instruction", "dos de las seis preguntas" in questions_block, "present" if "dos de las seis preguntas" in questions_block else "missing"),
        check("no_placeholders", all(value == 0 for value in placeholders.values()), placeholders),
        check("no_prose_dashes", not prose_dash_lines, prose_dash_lines),
        check("impersonal_register", not second_person_hits, second_person_hits),
        check("urls_unique", len(urls) == len(set(urls)), {"count": len(urls), "unique": len(set(urls))}),
        check("content_only_package", not re.search(r"\.(?:pdf|html|css|png|jpe?g)\b", before_references, flags=re.IGNORECASE), "no layout or image artifact references"),
    ]

    payload = {
        "document": "N04",
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
        "document": "N04",
        "stage": "content-final",
        "title": "Hechos, síntomas, relatos, hipótesis y decisiones",
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
