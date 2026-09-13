#!/usr/bin/env python3
"""Validate and manifest the N36 plain-language readability rewrite."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent
SOURCE = PACKAGE / "source" / "N36_practica_reflexiva_y_aprendizaje_profesional-content-canonical-v5.md"
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
    movement_body = text[text.index("## Movimiento 1") : text.index("## Hotel Horizonte")]
    row = audit_readability.analyse(36, SOURCE.resolve())
    reference_anchors = (
        "Schön", "Argyris", "Dewey", "Kolb", "Edmondson", "Mezirow",
        "Senge", "Freire", "Tabassi", "UNESCO", "Moon", "Wenger", "Ericsson",
    )
    central_terms = (
        "reflexión en la acción", "reflexión sobre la acción", "sorpresa",
        "teoría declarada", "teoría en uso", "bucle simple", "doble bucle",
        "diario de decisiones", "revisión posterior", "práctica deliberada",
        "portafolio de aprendizaje", "IA como interlocutora crítica",
        "sistema de aprendizaje profesional",
    )

    required = (
        "## Pregunta profesional",
        "## Tesis",
        "## Del cierre anterior al nuevo avance",
        "## Hotel Horizonte",
        "## Instrumento HH-36",
        "## Caso de transferencia",
        "## Contraejemplo",
        "## Prueba integral",
        "## Tradiciones y marcos utilizados",
        "## Errores frecuentes",
        "## Consecuencias profesionales",
        "## Límites y tensiones",
        "## Después de N36",
        "## Síntesis",
        "## Cinco píldoras para recordar",
        "## Glosario esencial",
        "## Preguntas de preparación",
        "## Referentes",
        "## Referencias base",
    )
    checks = {
        "title": text.startswith("# N36 · Práctica reflexiva: aprender de decisiones, errores, sorpresas y asistencia de IA"),
        "total_word_floor": len(words(text)) >= 7000,
        "substantive_word_floor": len(words(substantive)) >= 6000,
        "required_sections": all(item in text for item in required),
        "three_movements": len(re.findall(r"^## Movimiento [123]", text, re.M)) == 3,
        "twelve_concept_units": len(re.findall(r"^### ", movement_body, re.M)) == 12,
        "five_pills": len(re.findall(r"^[1-5]\. ", text[text.index("## Cinco píldoras") : text.index("## Glosario")], re.M)) == 5,
        "six_questions": len(re.findall(r"^[1-6]\. ", text[text.index("## Preguntas") : text.index("## Referentes")], re.M)) == 6,
        "six_referents": len(re.findall(r"^\*\*[^\n]+\.\*\*", referents, re.M)) == 6,
        "thirteen_references": len(re.findall(r"^- ", references, re.M)) == 13,
        "reference_anchors_in_body": all(anchor in substantive for anchor in reference_anchors),
        "central_terms_preserved": all(term.casefold() in text.casefold() for term in central_terms),
        "current_2026_implication": "En 2026" in substantive,
        "hotel_continuity": all(name in text for name in ("Elena Acosta", "Lucía Ferreyra", "Ricardo Sosa", "Federico Müller", "Mariela Benítez", "Camila Duarte")),
        "no_placeholders": re.search(r"\b(?:TBD|LOREM|XXX)\b|\[(?:pendiente|completar|insertar)", text, re.I) is None,
        "no_incidental_dashes": "—" not in text and "–" not in text,
        "readability_signal_low": row.automatic_signal == "BAJA",
        "paragraph_mean": 35 <= row.avg_paragraph_words <= 55,
        "paragraph_p90": row.p90_paragraph_words <= 85,
        "sentence_p90": row.p90_sentence_words <= 30,
        "very_long_paragraphs_absent": row.very_long_paragraphs_pct == 0,
    }
    overall = "pass" if all(checks.values()) else "fail"
    eligible = blocks(text)
    manifest = {
        "document": "N36",
        "stage": "content-canonical-v5-plain-language-pattern",
        "source": str(SOURCE.relative_to(PACKAGE)),
        "source_sha256": digest,
        "eligible_blocks": eligible,
    }
    payload = {
        "document": "N36",
        "stage": "content-canonical-v5-plain-language-pattern",
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
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"overall": overall, "word_counts": payload["word_counts"], "readability": row.automatic_signal, "failed": [key for key, value in checks.items() if not value]}, ensure_ascii=False))
    raise SystemExit(0 if overall == "pass" else 1)


if __name__ == "__main__":
    main()
