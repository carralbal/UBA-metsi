#!/usr/bin/env python3
"""Validate one METSI plain-language canonical source and refresh its manifests."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_readability  # noqa: E402


WORD_RE = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+")
COMMON_SECTIONS = (
    "## Pregunta profesional",
    "## Tesis",
    "## Cinco píldoras para recordar",
    "## Glosario esencial",
    "## Preguntas de preparación",
    "## Referentes",
    "## Referencias base",
)
HOTEL_NAMES = (
    "Elena Acosta", "Lucía Ferreyra", "Ricardo Sosa",
    "Federico Müller", "Mariela Benítez", "Camila Duarte",
)


def word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def section_start(text: str, heading: str) -> int:
    """Locate an exact Markdown heading, without matching a deeper H3."""
    match = re.search(rf"^{re.escape(heading)}$", text, re.M)
    if not match:
        raise ValueError(f"Missing section: {heading}")
    return match.start()


def has_section(text: str, heading: str) -> bool:
    return re.search(rf"^{re.escape(heading)}$", text, re.M) is not None


def source_blocks(text: str) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    buffer: list[str] = []

    def flush() -> None:
        if buffer:
            value = " ".join(part.strip() for part in buffer).strip()
            if value:
                result.append({"kind": "paragraph", "text": value})
            buffer.clear()

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            flush()
        elif line.startswith("#"):
            flush()
            result.append({"kind": "heading", "text": line})
        elif re.match(r"^(?:\d+\.|- )", line):
            flush()
            result.append({"kind": "list-item", "text": line})
        else:
            buffer.append(line)
    flush()
    for index, item in enumerate(result, 1):
        item["source_id"] = f"src-{index:04d}"
    return result


def incidental_dashes(text: str) -> list[str]:
    offenders = []
    for line in text.splitlines():
        if "—" not in line and "–" not in line:
            continue
        if "ISO/IEC/IEEE 15288:2023 Systems and software engineering — System life cycle processes" in line:
            reduced = line.replace("ISO/IEC/IEEE 15288:2023 Systems and software engineering — System life cycle processes", "")
            if "—" not in reduced and "–" not in reduced:
                continue
        offenders.append(line)
    return offenders


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--document", required=True)
    parser.add_argument("--stage", required=True)
    parser.add_argument("--min-total", type=int, default=7000)
    parser.add_argument("--min-substantive", type=int, default=5800)
    parser.add_argument("--min-references", type=int, default=12)
    parser.add_argument("--expected-h3", type=int, default=12)
    parser.add_argument("--expected-movements", type=int, default=3)
    parser.add_argument("--expected-questions", type=int, default=6)
    parser.add_argument("--min-paragraph-mean", type=float, default=35)
    parser.add_argument("--skip-referents", action="store_true")
    parser.add_argument("--skip-hotel-names", action="store_true")
    parser.add_argument("--term", action="append", default=[])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = args.source.resolve()
    package = source.parent.parent
    text = source.read_text(encoding="utf-8")
    number = int(args.document[1:])
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    row = audit_readability.analyse(number, source)
    substantive = text[section_start(text, "## Tesis") : section_start(text, "## Cinco píldoras para recordar")]
    has_referents = has_section(text, "## Referentes")
    referents = (
        text[section_start(text, "## Referentes") : section_start(text, "## Referencias base")]
        if has_referents else ""
    )
    references = text[section_start(text, "## Referencias base") :]
    pills = text[section_start(text, "## Cinco píldoras para recordar") : section_start(text, "## Glosario esencial")]
    question_end = section_start(text, "## Referentes") if has_referents else section_start(text, "## Referencias base")
    questions = text[section_start(text, "## Preguntas de preparación") : question_end]
    required_sections = tuple(
        section for section in COMMON_SECTIONS
        if not (args.skip_referents and section == "## Referentes")
    )
    checks = {
        "title": text.startswith(f"# {args.document} ·"),
        "total_word_floor": word_count(text) >= args.min_total,
        "substantive_word_floor": word_count(substantive) >= args.min_substantive,
        "common_sections": all(section in text for section in required_sections),
        "three_movements": len(re.findall(r"^## Movimiento [123]", text, re.M)) == args.expected_movements,
        "concept_units": len(re.findall(r"^### ", text, re.M)) == args.expected_h3,
        "five_pills": len(re.findall(r"^[1-5]\. ", pills, re.M)) == 5,
        "preparation_questions": len(re.findall(r"^\d+\. ", questions, re.M)) == args.expected_questions,
        "six_referents": args.skip_referents or len(re.findall(r"^\*\*[^\n]+\.\*\*", referents, re.M)) == 6,
        "reference_floor": len(re.findall(r"^- ", references, re.M)) >= args.min_references,
        "requested_terms": all(term.casefold() in text.casefold() for term in args.term),
        "hotel_continuity": args.skip_hotel_names or all(name in text for name in HOTEL_NAMES),
        "no_placeholders": re.search(r"\b(?:TBD|LOREM|XXX)\b|\[(?:pendiente|completar|insertar)", text, re.I) is None,
        "no_incidental_dashes": not incidental_dashes(text),
        "readability_signal_low": row.automatic_signal == "BAJA",
        "paragraph_mean": args.min_paragraph_mean <= row.avg_paragraph_words <= 55,
        "paragraph_p90": row.p90_paragraph_words <= 85,
        "sentence_p90": row.p90_sentence_words <= 30,
        "very_long_paragraphs_absent": row.very_long_paragraphs_pct == 0,
    }
    eligible = source_blocks(text)
    overall = "pass" if all(checks.values()) else "fail"
    manifest = {
        "document": args.document,
        "stage": args.stage,
        "source": str(source.relative_to(package)),
        "source_sha256": digest,
        "eligible_blocks": eligible,
    }
    report = {
        "document": args.document,
        "stage": args.stage,
        "overall": overall,
        "source": str(source.relative_to(package)),
        "source_sha256": digest,
        "word_counts": {"total": word_count(text), "substantive": word_count(substantive)},
        "block_count": len(eligible),
        "readability": row.__dict__,
        "dash_offenders": incidental_dashes(text),
        "checks": checks,
    }
    (package / "source-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path = package / "provenance" / "integrity-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "document": args.document,
        "overall": overall,
        "words": report["word_counts"],
        "readability": row.automatic_signal,
        "failed": [key for key, value in checks.items() if not value],
    }, ensure_ascii=False))
    raise SystemExit(0 if overall == "pass" else 1)


if __name__ == "__main__":
    main()
