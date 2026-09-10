#!/usr/bin/env python3
"""Audita la ampliación curricular METSI sin tocar fuentes ni PDF."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = (
    "N02", "N03", "N05", "N06", "N08", "N09", "N12", "N14", "N15",
    "N16", "N17", "N18", "N19", "N20", "N21", "N23", "N24", "N25",
    "N27", "N28", "N29", "N30", "N31", "N32", "N33", "N35", "N36",
)
MINIMUM_DELTAS = {
    "N02": 180, "N03": 170, "N05": 180, "N06": 200, "N08": 250,
    "N09": 700, "N12": 300, "N14": 550, "N15": 450, "N16": 180,
    "N17": 700, "N18": 250, "N19": 200, "N20": 450, "N21": 450,
    "N23": 450, "N24": 350, "N25": 600, "N27": 600, "N28": 200,
    "N29": 600, "N30": 550, "N31": 180, "N32": 180, "N33": 180,
    "N35": 0, "N36": 0,
}
TERM_CHECKS = {
    "N02": ("García",),
    "N03": ("García",),
    "N05": ("Etkin", "Schvarstein", "Ricaurte"),
    "N06": ("ISO 9241-210", "investigación de diseño"),
    "N08": ("blueprint",),
    "N09": ("UI", "UX", "Scolari"),
    "N12": ("BPMN", "Flores", "Winograd"),
    "N14": ("BPMN", "pool", "lane", "Flores", "Winograd"),
    "N15": ("BPMN", "Scolari"),
    "N16": ("Etkin", "Schvarstein"),
    "N17": ("PMBOK", "Scrum", "Kanban"),
    "N18": ("Git", "Chacon"),
    "N19": ("Varsavsky",),
    "N20": ("PMBOK", "Varsavsky"),
    "N21": ("PMBOK", "Etkin", "Schvarstein"),
    "N23": ("Scrum", "Definición de Terminado"),
    "N24": ("Kanban", "trabajo en curso"),
    "N25": ("Kanban", "DORA"),
    "N27": ("OpenAPI", "AsyncAPI", "Flores", "Winograd"),
    "N28": ("ISO 9241-210", "usabilidad"),
    "N29": ("GitHub", "DevOps", "rama principal"),
    "N30": ("DORA", "tasa de retrabajo"),
    "N31": ("Ricaurte",),
    "N32": ("Ricaurte",),
    "N33": ("Ricaurte",),
    "N35": ("Freire",),
    "N36": ("Freire",),
}
REQUIRED_HEADINGS = (
    "## Pregunta profesional", "## Tesis", "## Síntesis",
    "## Cinco píldoras para recordar", "## Glosario esencial",
    "## Preguntas de preparación", "## Referencias base",
)


def words(text: str) -> int:
    return len(re.findall(r"\b[\wÁÉÍÓÚÜÑáéíóúüñ]+(?:[-‑][\wÁÉÍÓÚÜÑáéíóúüñ]+)*\b", text))


def sources() -> dict[str, tuple[Path, Path]]:
    found: dict[str, tuple[Path, Path]] = {}
    for candidate in ROOT.glob("N*-content-*/source/*-v2.md"):
        doc = candidate.name[:3]
        if "content-canonical-v2.md" in candidate.name:
            baseline = candidate.with_name(candidate.name.replace("-v2.md", "-v1.md"))
        else:
            baseline = candidate.with_name(candidate.name.replace("-v2.md", ".md"))
        found[doc] = (baseline, candidate)
    return found


def added_lines(old: str, new: str) -> list[str]:
    return [line[2:] for line in difflib.ndiff(old.splitlines(), new.splitlines()) if line.startswith("+ ")]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    located = sources()
    checks: list[dict[str, object]] = []
    documents: dict[str, object] = {}
    paragraphs: dict[str, list[str]] = defaultdict(list)

    def record(name: str, passed: bool, evidence: object) -> None:
        checks.append({"check": name, "result": "pass" if passed else "fail", "evidence": evidence})

    record("expected_sources", set(located) == set(EXPECTED), sorted(located))
    for doc in EXPECTED:
        if doc not in located:
            continue
        baseline, candidate = located[doc]
        old = baseline.read_text(encoding="utf-8")
        new = candidate.read_text(encoding="utf-8")
        delta = words(new) - words(old)
        additions = added_lines(old, new)
        body = new.split("## Referencias base", 1)[0]
        references = new.split("## Referencias base", 1)[1]
        missing_headings = [heading for heading in REQUIRED_HEADINGS if heading not in new]
        missing_terms = [term for term in TERM_CHECKS[doc] if term.casefold() not in new.casefold()]
        placeholders = re.findall(r"(?i)(?:\bTBD\b|\blorem\b|\bXXX\b|\[TODO\])", new)
        added_dashes = [line for line in additions if " — " in line or " – " in line]
        hotel_mentions = len(re.findall(r"Hotel Horizonte|HH-[0-9]+", body))
        if doc not in ("N35", "N36"):
            record(f"{doc}_minimum_delta", delta >= MINIMUM_DELTAS[doc], delta)
        else:
            record(f"{doc}_byte_preservation", old == new, hashlib.sha256(new.encode()).hexdigest())
        record(f"{doc}_structure", not missing_headings, missing_headings)
        record(f"{doc}_topic_anchors", not missing_terms, missing_terms)
        record(f"{doc}_hotel_continuity", hotel_mentions > 0, hotel_mentions)
        record(f"{doc}_no_placeholders", not placeholders, placeholders)
        record(f"{doc}_no_added_prose_dashes", not added_dashes, added_dashes)
        for paragraph in re.split(r"\n\s*\n", body):
            normalized = re.sub(r"\s+", " ", paragraph.strip())
            if len(normalized) >= 220 and not normalized.startswith(("#", "-", "1.", "2.", "3.", "4.", "5.", "6.")):
                paragraphs[normalized].append(doc)
        documents[doc] = {
            "baseline": str(baseline.relative_to(ROOT)),
            "candidate": str(candidate.relative_to(ROOT)),
            "baseline_words": words(old),
            "candidate_words": words(new),
            "delta_words": delta,
            "hotel_mentions": hotel_mentions,
            "sha256": hashlib.sha256(new.encode()).hexdigest(),
        }

    duplicates = {text[:180]: docs for text, docs in paragraphs.items() if len(set(docs)) > 1}
    record("no_cross_document_duplicate_paragraphs", not duplicates, duplicates)
    pdf_changes = [line for line in __import__("subprocess").run(
        ["git", "status", "--short", "--", "*.pdf"], cwd=ROOT, text=True,
        capture_output=True, check=True,
    ).stdout.splitlines() if line]
    record("pdfs_untouched", not pdf_changes, pdf_changes)
    total_old = sum(int(row["baseline_words"]) for row in documents.values())
    total_new = sum(int(row["candidate_words"]) for row in documents.values())
    payload = {
        "schema": "metsi-curricular-expansion-audit/v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": list(EXPECTED),
        "totals": {"baseline_words": total_old, "candidate_words": total_new, "delta_words": total_new - total_old},
        "documents": documents,
        "checks": checks,
        "overall": "pass" if all(row["result"] == "pass" for row in checks) else "fail",
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.write:
        target = args.write if args.write.is_absolute() else ROOT / args.write
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if payload["overall"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
