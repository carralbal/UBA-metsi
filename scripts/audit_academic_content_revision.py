#!/usr/bin/env python3
"""Validate the selected N11-N36 academic content revision without building PDFs."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "academic-content-revision-manifest-n11-n36.json"
WORD_RE = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+")

sys.path.insert(0, str(ROOT))
from audit_canonical_n11_n36 import anchor_for, normalized  # noqa: E402


def words(value: str) -> list[str]:
    return WORD_RE.findall(value)


def segment(text: str, start: str, stop: str) -> str:
    left = text.find(start)
    right = text.find(stop, max(left, 0))
    return text[left if left >= 0 else 0 : right if right >= 0 else None]


def opening_segment(text: str) -> str:
    headings = list(re.finditer(r"^##\s+(.+)$", text, re.MULTILINE))
    start = headings[1].start()
    stops = [
        match.start()
        for match in headings[2:]
        if match.group(1) == "Tesis" or match.group(1).startswith("Hotel Horizonte")
    ]
    return text[start : min(stops)]


def audit_document(entry: dict[str, object]) -> dict[str, object]:
    code = str(entry["code"])
    source = ROOT / str(entry["source"])
    text = source.read_text(encoding="utf-8")
    body = text.split("## Referentes", 1)[0]
    opening = opening_segment(text)
    substantive = segment(text, opening.splitlines()[0], "## Cinco píldoras para recordar")
    conceptual_core = segment(text, "## Tesis", "## Cinco píldoras para recordar")
    references_part = text.split("## Referencias base", 1)[1]
    references = [line[2:].strip() for line in references_part.splitlines() if line.startswith("- ")]
    missing_anchors = []
    for reference in references:
        author, candidates = anchor_for(reference)
        if not any(candidate and normalized(candidate) in normalized(body) for candidate in candidates):
            missing_anchors.append(author)

    pills = segment(text, "## Cinco píldoras para recordar", "## Glosario esencial")
    questions = segment(text, "## Preguntas de preparación", "## Referentes")
    referents = segment(text, "## Referentes", "## Referencias base")
    hotel_headings = re.findall(r"^##\s+Hotel Horizonte", text, re.MULTILINE)
    headings = re.findall(r"^##\s+(.+)$", text, re.MULTILINE)
    required = (
        "Pregunta profesional",
        "Hotel Horizonte",
        "Tesis",
        "Errores frecuentes",
        "Consecuencias profesionales",
        "Límites y tensiones",
        "Síntesis",
        "Cinco píldoras para recordar",
        "Glosario esencial",
        "Preguntas de preparación",
        "Referentes",
        "Referencias base",
    )
    total_count = len(words(text))
    substantive_count = len(words(substantive))
    opening_count = len(words(opening))
    sha256 = hashlib.sha256(source.read_bytes()).hexdigest()
    checks = {
        "source_exists": source.is_file(),
        "sha256": sha256 == entry["sha256"],
        "words_total": total_count == entry["words_total"],
        "words_substantive": substantive_count == entry["words_substantive"],
        "words_opening": opening_count == entry["words_opening"],
        "substantive_floor": substantive_count >= 6000,
        "conceptual_core_floor": len(words(conceptual_core)) >= 6000,
        "substantial_opening": opening_count >= 450,
        "independent_opening": "Hotel Horizonte" not in opening,
        "required_sections": all(any(heading.startswith(item) for heading in headings) for item in required),
        "three_movements": len(re.findall(r"^## Movimiento [123]", text, re.MULTILINE)) == 3,
        "single_hotel_case": len(hotel_headings) == 1 and f"HH-{code[1:]}" in text,
        "five_pills": len(re.findall(r"^[1-5]\.\s", pills, re.MULTILINE)) == 5,
        "six_questions": len(re.findall(r"^[1-6]\.\s", questions, re.MULTILINE)) == 6,
        "six_referents": len(re.findall(r"^\*\*[^\n]+\.\*\*", referents, re.MULTILINE)) == 6,
        "reference_depth": len(references) >= 10,
        "reference_anchors": not missing_anchors,
        "no_placeholders": not re.search(
            r"\b(?:TBD|TODO|XXX|PENDING_RECALCULATION)\b|\b(?:[Ll]orem)\b|\[(?:pendiente|completar|insertar)[^]]*]",
            text,
        ),
        "impersonal_register": not re.search(
            r"\b(?:vos|usted|ustedes|tu|tus|te|seleccioná|elegí|hacé|podés|deberías)\b",
            body,
            re.IGNORECASE,
        ),
        "audit_score": int(entry["audit_score"]) >= 35,
    }
    return {
        "code": code,
        "source": str(source.relative_to(ROOT)),
        "words_total": total_count,
        "words_substantive": substantive_count,
        "words_opening": opening_count,
        "references": len(references),
        "missing_reference_anchors": missing_anchors,
        "checks": checks,
        "result": "PASS" if all(checks.values()) else "FAIL",
    }


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    documents = manifest["documents"]
    codes = [entry["code"] for entry in documents]
    expected = [f"N{number:02d}" for number in range(11, 37)]
    collection_checks = {
        "scope_complete_and_ordered": codes == expected,
        "status_publication_authorized": manifest["status"] == "content-and-editorial-approved-publication-authorized",
        "publication_authorized": "authorized for main publication" in manifest["publication_policy"],
    }
    results = [audit_document(entry) for entry in documents]
    overall = all(collection_checks.values()) and all(item["result"] == "PASS" for item in results)
    print(json.dumps({
        "result": "PASS" if overall else "FAIL",
        "collection_checks": collection_checks,
        "documents": {
            item["code"]: {
                "result": item["result"],
                "words_substantive": item["words_substantive"],
                "words_opening": item["words_opening"],
                "missing_reference_anchors": item["missing_reference_anchors"],
                "failed_checks": [name for name, passed in item["checks"].items() if not passed],
            }
            for item in results
        },
    }, ensure_ascii=False, indent=2))
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
