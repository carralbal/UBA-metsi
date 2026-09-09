#!/usr/bin/env python3
"""Auditoría transversal, no destructiva, de las fuentes canónicas METSI N11 a N36."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parent
WORD_RE = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+")
REQUIRED_HEADINGS = (
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
ORG_ANCHORS = {
    "international organization for standardization": "ISO",
    "international electrotechnical commission": "IEC",
    "project management institute": "PMI",
    "national institute of standards and technology": "NIST",
    "world wide web consortium": "W3C",
    "software engineering body of knowledge": "SEBoK",
    "sebok editorial board": "SEBoK",
    "organisation for economic co operation and development": "OECD",
    "organization for economic cooperation and development": "OECD",
    "european union": "Unión Europea",
}

# A reference can be anchored by the standard, work, or institutional name
# actually used in the prose.  These aliases prevent the audit from requiring
# an ornamental author citation when the body correctly names the artefact.
REFERENCE_ALIASES = {
    "national academies of sciences engineering and medicine": ("Academias Nacionales de Estados Unidos",),
    "cloud native computing foundation": ("CloudEvents",),
    "asyncapi initiative": ("AsyncAPI",),
    "featonby m": ("AWS", "Amazon Builders’ Library"),
    "beck k et al": ("Manifiesto Ágil",),
}


def normalized(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    return " ".join(re.findall(r"[a-z0-9]+", "".join(ch for ch in value if not unicodedata.combining(ch))))


def words(value: str) -> list[str]:
    return WORD_RE.findall(value)


def segment(text: str, start: str, stop: str) -> str:
    left = text.find(start)
    right = text.find(stop, max(left, 0))
    return text[left if left >= 0 else 0 : right if right >= 0 else None]


def source_for(number: int) -> Path:
    package = ROOT / f"N{number:02d}-content-canonical" / "source"
    matches = sorted(package.glob("*.md"))
    if len(matches) != 1:
        raise RuntimeError(f"N{number:02d}: se esperaba una fuente y se encontraron {len(matches)}")
    return matches[0]


def anchor_for(reference: str) -> tuple[str, tuple[str, ...]]:
    author = reference.split(" (", 1)[0].strip()
    folded = normalized(author)
    title_match = re.search(r"\*([^*]+)\*", reference)
    title = title_match.group(1).strip() if title_match else ""
    title_tokens = [token for token in re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+", title) if len(token) >= 5]
    title_candidates = tuple(filter(None, (
        title,
        " ".join(title_tokens[:4]),
        " ".join(title_tokens[:3]),
        " ".join(title_tokens[:2]),
        *(title_tokens[:1]),
        *(re.findall(r"\b[A-Z][A-Z0-9.-]{1,}\b", title)),
    )))
    aliases: list[str] = []
    normalized_reference = normalized(reference)
    for phrase, values in REFERENCE_ALIASES.items():
        if phrase in normalized_reference:
            aliases.extend(values)
    if "object management group" in folded:
        if "unified modeling language" in normalized_reference:
            aliases.append("UML")
        if "business process model and notation" in normalized_reference:
            aliases.append("BPMN")
        if "business architecture core metamodel" in normalized_reference:
            aliases.extend(("Business Architecture Core Metamodel", "OMG"))
    if "the open group" in folded:
        if "archimate" in normalized_reference:
            aliases.append("ArchiMate")
        if "togaf" in normalized_reference:
            aliases.append("TOGAF")
    for phrase, anchor in ORG_ANCHORS.items():
        if phrase in folded:
            return author, (anchor, author, *aliases, *title_candidates)
    acronyms = tuple(re.findall(r"\b[A-Z][A-Z0-9]{1,}\b", author))
    first = author.split(",", 1)[0].strip()
    if first and len(first) > 2:
        return author, (*acronyms, first, *aliases, *title_candidates)
    tokens = [token for token in re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", author) if len(token) > 2]
    return author, (*acronyms, *(tokens[:1] or (author,)), *aliases, *title_candidates)


def audit_one(number: int) -> dict[str, object]:
    code = f"N{number:02d}"
    source = source_for(number)
    text = source.read_text(encoding="utf-8")
    headings = re.findall(r"^##\s+(.+)$", text, re.MULTILINE)
    substantive = segment(text, "## Tesis", "## Cinco píldoras para recordar")
    pre_referents = text.split("## Referentes", 1)[0]
    references_part = text.split("## Referencias base", 1)[1] if "## Referencias base" in text else ""
    references = [line[2:].strip() for line in references_part.splitlines() if line.startswith("- ")]
    anchors: list[dict[str, object]] = []
    for reference in references:
        author, candidates = anchor_for(reference)
        found = next((candidate for candidate in candidates if candidate and normalized(candidate) in normalized(pre_referents)), None)
        anchors.append({"reference": author, "candidates": candidates, "found": found})
    pills_part = segment(text, "## Cinco píldoras para recordar", "## Glosario esencial")
    questions_part = segment(text, "## Preguntas de preparación", "## Referentes")
    referents_part = segment(text, "## Referentes", "## Referencias base")
    checks = {
        "substantive_floor_6000": len(words(substantive)) >= 6000,
        "required_headings": all(any(heading.startswith(required) for heading in headings) for required in REQUIRED_HEADINGS),
        "three_movements": len(re.findall(r"^## Movimiento [123]", text, re.MULTILINE)) == 3,
        "hotel_continuity": f"HH-{number:02d}" in text and "Hotel Horizonte" in text,
        "five_pills": len(re.findall(r"^[1-5]\.\s", pills_part, re.MULTILINE)) == 5,
        "six_questions": len(re.findall(r"^[1-6]\.\s", questions_part, re.MULTILINE)) == 6,
        "six_referents": len(re.findall(r"^\*\*[^\n]+\.\*\*", referents_part, re.MULTILINE)) == 6,
        "reference_depth": len(references) >= 10,
        "reference_anchors": all(item["found"] for item in anchors),
        "no_placeholders": not re.search(r"\b(?:TBD|TODO|XXX)\b|\b(?:lorem)\b|\[(?:pendiente|completar|insertar)[^]]*]", text),
        "no_incidental_rule_dashes": "—" not in text.split("## Referencias base", 1)[0] and "–" not in text.split("## Referencias base", 1)[0],
        "impersonal_register": not re.search(r"\b(?:vos|usted|ustedes|tu|tus|te|seleccioná|elegí|hacé|podés|deberías)\b", pre_referents, re.IGNORECASE),
    }
    return {
        "document": code,
        "source": str(source.relative_to(ROOT)),
        "sha256": hashlib.sha256(text.encode()).hexdigest(),
        "words_total": len(words(text)),
        "words_substantive": len(words(substantive)),
        "references": len(references),
        "missing_reference_anchors": [item for item in anchors if not item["found"]],
        "checks": checks,
        "result": "PASS" if all(checks.values()) else "FAIL",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=11)
    parser.add_argument("--end", type=int, default=36)
    args = parser.parse_args()
    documents = [audit_one(number) for number in range(args.start, args.end + 1)]
    report = {
        "scope": f"N{args.start:02d}-N{args.end:02d}",
        "result": "PASS" if all(item["result"] == "PASS" for item in documents) else "FAIL",
        "documents": documents,
    }
    (ROOT / "BLOCK-CANONICAL-AUDIT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Auditoría canónica METSI N11 a N36", "", f"Resultado global: **{report['result']}**.", ""]
    for item in documents:
        failed = ", ".join(key for key, value in item["checks"].items() if not value) or "ninguno"
        lines.append(f"- {item['document']}: {item['result']}, {item['words_substantive']} palabras sustantivas, fallos: {failed}.")
    (ROOT / "BLOCK-CANONICAL-AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"result": report["result"], "documents": {item["document"]: item["result"] for item in documents}}, ensure_ascii=False))
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
