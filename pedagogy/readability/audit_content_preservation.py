#!/usr/bin/env python3
"""Verify that the N00-N36 plain-language rewrite preserves course content."""

from __future__ import annotations

import csv
import difflib
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT))
import audit_readability  # noqa: E402


WORD_RE = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+")
TERM_RE = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{5,}")
VERSION_RE = re.compile(r"-v(\d+)\.md$")
ALLOWED_DASH_TITLE = "ISO/IEC/IEEE 15288:2023 Systems and software engineering — System life cycle processes"
HOTEL_NAMES = (
    "Elena Acosta", "Lucía Ferreyra", "Ricardo Sosa",
    "Federico Müller", "Mariela Benítez", "Camila Duarte",
)
PRESERVED_SECTIONS = (
    "Pregunta profesional", "Tesis", "Cinco píldoras para recordar",
    "Glosario esencial", "Preguntas de preparación", "Referencias base",
)
STOPWORDS = set(
    "para como pero porque cuando desde hasta sobre entre donde quien quienes una uno unos unas "
    "este esta esto estos estas ese esa esos esas del las los con sin por que qué cual cuáles cada "
    "más menos muy ya hay ser son fue eran puede pueden debe deben tiene tienen hacia ante bajo tras "
    "durante mediante también no sí se su sus al o y e u ni a en de la el lo".split()
)


def version(path: Path) -> int:
    match = VERSION_RE.search(path.name)
    return int(match.group(1)) if match else -1


def public_sources() -> dict[int, Path]:
    result: dict[int, Path] = {}
    site = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
    for number in range(11):
        match = re.search(
            rf'href="[^"]*N{number:02d}-METSI-lectura-previa-v(\d+)-final\.pdf"',
            site,
        )
        if not match:
            raise FileNotFoundError(f"Missing public package for N{number:02d}")
        package = ROOT / f"N{number:02d}-v{match.group(1)}-final"
        manifest = json.loads((package / "source-manifest.json").read_text(encoding="utf-8"))
        result[number] = package / manifest["source"]

    course = json.loads((ROOT / "site" / "course-manifest.json").read_text(encoding="utf-8"))
    for item in course["publication"]["readings"]:
        result[int(item["code"][1:])] = ROOT / item["package_source"]
    return result


def baseline(number: int, current: Path, public: dict[int, Path]) -> Path:
    older = [path for path in current.parent.glob("*.md") if version(path) < version(current)]
    return max(older, key=version) if older else public[number]


def words(text: str) -> int:
    return len(WORD_RE.findall(text))


def section_exists(text: str, heading: str) -> bool:
    return re.search(rf"^## {re.escape(heading)}$", text, re.M) is not None


def section_body(text: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\s*$", text, re.M)
    if not match:
        return ""
    tail = text[match.end():]
    end = re.search(r"^## ", tail, re.M)
    return tail[:end.start()] if end else tail


def bibliography_entries(text: str) -> list[str]:
    body = section_body(text, "Referencias base")
    result: list[str] = []
    current: list[str] = []
    for line in body.splitlines():
        if line.startswith("- "):
            if current:
                result.append(" ".join(current))
            current = [line[2:].strip()]
        elif current and line.strip():
            current.append(line.strip())
        elif current:
            result.append(" ".join(current))
            current = []
    if current:
        result.append(" ".join(current))
    return result


def normalized_reference(value: str) -> str:
    value = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"https?://\S+", "", value)
    value = value.replace("—", "-").replace("–", "-")
    value = re.sub(r"[^\wáéíóúüñ]+", " ", value.casefold())
    return re.sub(r"\s+", " ", value).strip()


def bibliography_coverage(old: list[str], new: list[str]) -> tuple[float, float]:
    if not old:
        return (1.0, 1.0)
    scores = []
    for item in old:
        normalized = normalized_reference(item)
        scores.append(max(
            (difflib.SequenceMatcher(None, normalized, normalized_reference(candidate)).ratio() for candidate in new),
            default=0.0,
        ))
    return (round(sum(score >= 0.8 for score in scores) / len(scores), 3), round(min(scores), 3))


def top_terms(text: str, limit: int = 60) -> list[str]:
    body = text.split("## Referencias base", 1)[0].casefold()
    counts = Counter(word for word in TERM_RE.findall(body) if word not in STOPWORDS)
    return [word for word, count in counts.most_common(limit) if count >= 2]


def count_questions(text: str) -> int:
    return len(re.findall(r"^\d+\. ", section_body(text, "Preguntas de preparación"), re.M))


def count_pills(text: str) -> int:
    return len(re.findall(r"^(?:[-*]|\d+\.) ", section_body(text, "Cinco píldoras para recordar"), re.M))


def main() -> None:
    sources = audit_readability.source_paths()
    public = public_sources()
    readability = {row.n: row for row in (audit_readability.analyse(n, p) for n, p in sources.items())}
    rows = []

    for number in range(37):
        code = f"N{number:02d}"
        current = sources[number]
        old = baseline(number, current, public)
        new_text = current.read_text(encoding="utf-8")
        old_text = old.read_text(encoding="utf-8")
        new_words, old_words = words(new_text), words(old_text)
        old_refs, new_refs = bibliography_entries(old_text), bibliography_entries(new_text)
        ref_coverage, ref_min_similarity = bibliography_coverage(old_refs, new_refs)
        old_terms = top_terms(old_text)
        new_vocabulary = set(TERM_RE.findall(new_text.casefold()))
        term_coverage = round(sum(term in new_vocabulary for term in old_terms) / len(old_terms), 3) if old_terms else 1.0
        old_headings = len(re.findall(r"^#{2,3} ", old_text, re.M))
        new_headings = len(re.findall(r"^#{2,3} ", new_text, re.M))
        heading_ratio = round(new_headings / old_headings, 3) if old_headings else 1.0
        lost_names = [name for name in HOTEL_NAMES if name in old_text and name not in new_text]
        stripped = new_text.replace(ALLOWED_DASH_TITLE, "")
        bridges = True
        if number == 0:
            bridges = "N01" in new_text
        elif number == 1:
            bridges = "N02" in new_text
        elif number == 36:
            bridges = "N35" in new_text
        else:
            bridges = f"N{number - 1:02d}" in new_text and f"N{number + 1:02d}" in new_text

        checks = {
            "word_ratio": 0.95 <= new_words / old_words <= 1.10,
            "top_term_coverage": term_coverage >= 0.95,
            "bibliography_count": len(new_refs) == len(old_refs),
            "bibliography_coverage": ref_coverage == 1.0 and ref_min_similarity >= 0.8,
            "named_sections": all(not section_exists(old_text, name) or section_exists(new_text, name) for name in PRESERVED_SECTIONS),
            "heading_floor": heading_ratio >= 0.70,
            "pill_count": count_pills(new_text) == count_pills(old_text),
            "question_count": count_questions(new_text) == count_questions(old_text),
            "hotel_case": "Hotel Horizonte" in new_text,
            "hotel_names": not lost_names,
            "continuity_bridges": bridges,
            "readability_low": readability[code].automatic_signal == "BAJA",
            "no_very_long_paragraphs": readability[code].very_long_paragraphs_pct == 0,
            "no_placeholders": re.search(r"\b(?:TBD|LOREM|XXX)\b|\[(?:pendiente|completar|insertar)", new_text, re.I) is None,
            "no_incidental_dashes": "—" not in stripped and "–" not in stripped,
        }
        rows.append({
            "document": code,
            "current_source": str(current.relative_to(ROOT)),
            "baseline_source": str(old.relative_to(ROOT)),
            "source_sha256": hashlib.sha256(new_text.encode("utf-8")).hexdigest(),
            "word_ratio": round(new_words / old_words, 3),
            "top_term_coverage": term_coverage,
            "reference_entries": len(new_refs),
            "reference_coverage": ref_coverage,
            "reference_min_similarity": ref_min_similarity,
            "heading_ratio": heading_ratio,
            "lost_hotel_names": lost_names,
            "readability_signal": readability[code].automatic_signal,
            "checks": checks,
            "overall": "pass" if all(checks.values()) else "fail",
        })

    csv_rows = [{key: value for key, value in row.items() if key not in {"checks", "lost_hotel_names"}} for row in rows]
    with (OUT / "content-preservation.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=csv_rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(csv_rows)
    (OUT / "content-preservation.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    failures = [row["document"] for row in rows if row["overall"] != "pass"]
    print(json.dumps({
        "documents": len(rows),
        "passed": len(rows) - len(failures),
        "failed": failures,
        "min_word_ratio": min(row["word_ratio"] for row in rows),
        "max_word_ratio": max(row["word_ratio"] for row in rows),
        "min_term_coverage": min(row["top_term_coverage"] for row in rows),
        "bibliographies_preserved": sum(row["checks"]["bibliography_coverage"] for row in rows),
        "hotel_names_lost": sum(len(row["lost_hotel_names"]) for row in rows),
    }, ensure_ascii=False, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
