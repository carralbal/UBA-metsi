#!/usr/bin/env python3
"""Validate and manifest the N35 plain-language canonical rewrite."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent
SOURCE = PACKAGE / "source" / "N35_comunicar_defender_y_transferir_criterios-content-canonical-v4.md"
MANIFEST = PACKAGE / "source-manifest.json"
REPORT = PACKAGE / "provenance" / "integrity-report.json"

sys.path.insert(0, str(ROOT / "pedagogy" / "readability"))
import audit_readability  # noqa: E402


WORD_RE = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+")


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def blocks(text: str) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    buffer: list[str] = []

    def flush() -> None:
        if not buffer:
            return
        value = " ".join(part.strip() for part in buffer).strip()
        if value:
            result.append({"kind": "paragraph", "text": value})
        buffer.clear()

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            flush()
            continue
        if line.startswith("#"):
            flush()
            result.append({"kind": "heading", "text": line})
            continue
        if re.match(r"^(?:\d+\.|- )", line):
            flush()
            result.append({"kind": "list-item", "text": line})
            continue
        buffer.append(line)
    flush()
    for index, item in enumerate(result, 1):
        item["source_id"] = f"src-{index:04d}"
    return result


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    substantive = text[text.index("## Tesis") : text.index("## Cinco píldoras para recordar")]
    referents = text[text.index("## Referentes") : text.index("## Referencias base")]
    references = text.split("## Referencias base", 1)[1]
    movement_body = text[text.index("## Movimiento 1") : text.index("## Instrumento HH-35")]
    row = audit_readability.analyse(35, SOURCE.resolve())

    required = (
        "## Pregunta profesional",
        "## Tesis",
        "## Del cierre anterior al nuevo avance",
        "## Movimiento 1",
        "## Movimiento 2",
        "## Movimiento 3",
        "## Instrumento HH-35",
        "## Caso de transferencia",
        "## Contraejemplo",
        "## Prueba integral",
        "## Errores frecuentes",
        "## Consecuencias profesionales",
        "## Límites y tensiones",
        "## De N35 a N36",
        "## Síntesis",
        "## Cinco píldoras para recordar",
        "## Glosario esencial",
        "## Preguntas de preparación",
        "## Referentes",
        "## Referencias base",
    )
    central_terms = (
        "audiencia y decisión",
        "tesis comunicable",
        "afirmación, evidencia y garantía",
        "narrativa ejecutiva",
        "defensa técnica",
        "transferencia operativa",
        "comunicación con personas afectadas",
        "objeción",
        "incertidumbre comunicada",
        "evidencia visual",
        "transferencia por criterios",
        "comprobación por reexplicación",
    )
    reference_anchors = (
        "Toulmin", "Tufte", "Schön", "Argyris", "Freire", "Wenger",
        "Norman", "ISO 9241-210", "WCAG 2.2", "Project Management Institute",
        "Checkland", "Popper", "Edmondson",
    )
    checks = {
        "title": text.startswith("# N35 · Comunicar, defender y transferir criterios sin copiar soluciones"),
        "total_word_floor": len(words(text)) >= 7600,
        "substantive_word_floor": len(words(substantive)) >= 6100,
        "required_sections": all(item in text for item in required),
        "three_movements": len(re.findall(r"^## Movimiento [123]", text, re.M)) == 3,
        "twelve_concept_units": len(re.findall(r"^### ", movement_body, re.M)) == 12,
        "five_pills": len(re.findall(r"^[1-5]\. ", text[text.index("## Cinco píldoras") : text.index("## Glosario")], re.M)) == 5,
        "six_questions": len(re.findall(r"^[1-6]\. ", text[text.index("## Preguntas") : text.index("## Referentes")], re.M)) == 6,
        "six_referents": len(re.findall(r"^\*\*[^\n]+\.\*\*", referents, re.M)) == 6,
        "fourteen_references": len(re.findall(r"^- ", references, re.M)) == 14,
        "reference_anchors_in_body": all(anchor in substantive for anchor in reference_anchors),
        "central_terms_preserved": all(term.casefold() in text.casefold() for term in central_terms),
        "hotel_continuity": all(name in text for name in ("Elena Acosta", "Lucía Ferreyra", "Ricardo Sosa", "Federico Müller", "Mariela Benítez", "Camila Duarte")),
        "no_placeholders": re.search(r"\b(?:TBD|LOREM|XXX)\b|\[(?:pendiente|completar|insertar)", text, re.I) is None,
        "no_incidental_dashes": "—" not in text and "–" not in text,
        "readability_signal_low": row.automatic_signal == "BAJA",
        "paragraph_mean": 35 <= row.avg_paragraph_words <= 55,
        "paragraph_p90": row.p90_paragraph_words <= 85,
        "sentence_p90": row.p90_sentence_words <= 30,
        "very_long_paragraphs_absent": row.very_long_paragraphs_pct == 0,
    }
    eligible = blocks(text)
    overall = "pass" if all(checks.values()) else "fail"
    stage = "content-canonical-v4-plain-language"
    MANIFEST.write_text(json.dumps({
        "document": "N35",
        "stage": stage,
        "source": str(SOURCE.relative_to(PACKAGE)),
        "source_sha256": digest,
        "eligible_blocks": eligible,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "document": "N35",
        "stage": stage,
        "overall": overall,
        "source": str(SOURCE.relative_to(PACKAGE)),
        "source_sha256": digest,
        "word_counts": {
            "total": len(words(text)),
            "substantive_from_thesis_through_synthesis": len(words(substantive)),
        },
        "block_count": len(eligible),
        "readability": row.__dict__,
        "checks": checks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "overall": overall,
        "word_counts": {"total": len(words(text)), "substantive": len(words(substantive))},
        "readability": row.automatic_signal,
        "failed": [key for key, value in checks.items() if not value],
    }, ensure_ascii=False))
    raise SystemExit(0 if overall == "pass" else 1)


if __name__ == "__main__":
    main()
