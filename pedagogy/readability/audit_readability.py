#!/usr/bin/env python3
"""Deterministic pedagogical-readability screening for METSI N00-N36.

This is deliberately not a grammar checker. It measures signals associated with
cognitive load, abstraction, fragmentation and loss of situated human voice.
The output is evidence for a human audit, not an automatic quality verdict.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = Path(__file__).resolve().parent

WORD_RE = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+(?:[-'][A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)*")
SENTENCE_RE = re.compile(r"(?<=[.!?])(?:[\"»”’)*_\]]+)?\s+(?=[A-ZÁÉÍÓÚÜÑ¿¡0-9])")

EXCLUDED_H2_PREFIXES = (
    "contenido",
    "referentes",
    "referencias base",
    "cinco píldoras",
    "glosario esencial",
    "preguntas de preparación",
)

# Domain abstractions are not errors. Their density is used only as a proxy for
# how much conceptual working memory a passage may demand without relief.
ABSTRACT_STEMS = (
    "abstrac", "agencia", "aprendiz", "arquitect", "autoridad", "autonom",
    "capacidad", "causal", "coheren", "complej", "concept", "condici",
    "consecuen", "consisten", "context", "contradic", "contrato", "criteri",
    "decisi", "defendib", "dependen", "diseñ", "eviden", "explica",
    "gobern", "hipótes", "incertid", "informaci", "integr", "intervenci",
    "mecanism", "metodolog", "modelo", "operaci", "organiz", "perspect",
    "práctic", "proces", "responsab", "riesgo", "sistem", "supervisi",
    "trazab", "transfer", "valor", "verific",
)

HOTEL_NAMES = (
    "elena", "lucía", "lucia", "ricardo", "federico", "mariela", "camila",
    "acosta", "ferreyra", "sosa", "müller", "muller", "benítez", "benitez",
    "duarte",
)

NARRATIVE_MARKERS = (
    "cuando ", "después", "antes ", "esa mañana", "ese día", "durante ",
    "mientras ", "entonces", "al día", "una semana", "un mes", "horas",
    "minutos", "turno", "reunión", "episodio", "escena", "preguntó",
    "respondió", "dijo", "observó", "advirtió", "descubrió", "decidió",
)


@dataclass
class Row:
    n: str
    title: str
    source: str
    source_sha256: str
    body_words: int
    sentences: int
    avg_sentence_words: float
    p90_sentence_words: int
    long_sentences_pct: float
    paragraphs: int
    avg_paragraph_words: float
    p90_paragraph_words: int
    very_long_paragraphs_pct: float
    h3_per_1000_words: float
    abstract_terms_per_1000: float
    nominalizations_per_1000: float
    situated_names_per_1000: float
    voice_marks_per_1000: float
    narrative_paragraphs_pct: float
    load_index: int
    automatic_signal: str


def natural_version(path: Path) -> tuple[int, str]:
    match = re.search(r"(?:-v|v)(\d+)(?:\D|$)", path.name)
    return (int(match.group(1)) if match else -1, path.name)


def latest_canonical_source(number: int) -> Path | None:
    """Return the newest content-only canonical source when one exists."""
    package = ROOT / f"N{number:02d}-content-canonical" / "source"
    if not package.is_dir():
        return None
    candidates = list(package.glob("*.md"))
    if not candidates:
        return None
    return max(candidates, key=natural_version)


def source_paths() -> dict[int, Path]:
    paths: dict[int, Path] = {}

    # N00-N10 use a newer content-only canonical source when one exists. The
    # exact package linked from the public site remains the fallback until the
    # source revision is approved for a later editorial rebuild.
    site_html = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
    for number in range(0, 11):
        pattern = rf'href="[^"]*N{number:02d}-METSI-lectura-previa-v(\d+)-final\.pdf"'
        match = re.search(pattern, site_html)
        if not match:
            raise FileNotFoundError(f"No public-site package link for N{number:02d}")
        package = ROOT / f"N{number:02d}-v{match.group(1)}-final"
        sm = json.loads((package / "source-manifest.json").read_text(encoding="utf-8"))
        paths[number] = latest_canonical_source(number) or (package / sm["source"])

    # N11-N36 prefer the newest content-only canonical source. The public
    # release remains the fallback until a new canonical version is approved.
    course_manifest = json.loads((ROOT / "site" / "course-manifest.json").read_text(encoding="utf-8"))
    for item in course_manifest["publication"]["readings"]:
        number = int(item["code"][1:])
        paths[number] = latest_canonical_source(number) or (ROOT / item["package_source"])
    return paths


def clean_inline(text: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[`*_#>|]", " ", text)
    text = re.sub(r"^\s*[-+•]\s+", "", text)
    text = re.sub(r"^\s*\d+[.)]\s+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def body_paragraphs(markdown: str) -> tuple[str, list[str], int]:
    included: list[str] = []
    current: list[str] = []
    exclude = False
    h3_count = 0

    def flush() -> None:
        nonlocal current
        if current and not exclude:
            paragraph = clean_inline(" ".join(current))
            if paragraph:
                included.append(paragraph)
        current = []

    for raw in markdown.splitlines():
        line = raw.strip()
        h2 = re.match(r"^##\s+(.+)$", line)
        h3 = re.match(r"^###\s+(.+)$", line)
        if h2:
            flush()
            heading = clean_inline(h2.group(1)).casefold()
            exclude = heading.startswith(EXCLUDED_H2_PREFIXES)
            continue
        if h3:
            flush()
            if not exclude:
                h3_count += 1
            continue
        if line.startswith("# ") or line.startswith("<!--") or line.startswith("```"):
            flush()
            continue
        if line.startswith("|") or re.match(r"^(?:[-+•]|\d+[.)])\s+", line):
            # A table row or list item is an independent reading unit. Joining
            # consecutive rows/items would report a fictitious giant paragraph.
            flush()
            if not exclude:
                paragraph = clean_inline(line)
                if paragraph:
                    included.append(paragraph)
            continue
        if not line:
            flush()
            continue
        current.append(line)
    flush()
    return "\n\n".join(included), included, h3_count


def percentile(values: list[int], p: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(p * len(ordered)) - 1))
    return ordered[index]


def per_1000(count: int, total: int) -> float:
    return round((count * 1000 / total), 2) if total else 0.0


def analyse(number: int, path: Path) -> Row:
    source_bytes = path.read_bytes()
    markdown = source_bytes.decode("utf-8")
    title_match = re.search(r"^#\s+(.+)$", markdown, flags=re.MULTILINE)
    title = clean_inline(title_match.group(1)) if title_match else f"N{number:02d}"
    body, paragraphs, h3_count = body_paragraphs(markdown)
    words = [w.casefold() for w in WORD_RE.findall(body)]
    sentences = [s.strip() for s in SENTENCE_RE.split(body) if WORD_RE.search(s)]
    sentence_lengths = [len(WORD_RE.findall(s)) for s in sentences]
    paragraph_lengths = [len(WORD_RE.findall(p)) for p in paragraphs]

    abstract_count = sum(any(w.startswith(stem) for stem in ABSTRACT_STEMS) for w in words)
    nominal_count = sum(
        len(w) >= 7 and re.search(r"(?:ción|sión|dad|tad|miento|encia|ancia|aje|ura)s?$", w) is not None
        for w in words
    )
    situated_count = sum(w in HOTEL_NAMES for w in words)
    voice_count = len(re.findall(r"[«»“”\"]", body)) + len(
        re.findall(r"\b(?:dijo|preguntó|respondió|objetó|advirtió|propuso|explicó)\b", body, flags=re.I)
    )
    narrative_count = 0
    for paragraph in paragraphs:
        folded = paragraph.casefold()
        if any(marker in folded for marker in NARRATIVE_MARKERS) or any(name in folded for name in HOTEL_NAMES):
            narrative_count += 1

    avg_sentence = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
    avg_paragraph = sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0
    long_sentence_pct = 100 * sum(v >= 30 for v in sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
    very_long_paragraph_pct = 100 * sum(v >= 85 for v in paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0
    abstract_rate = per_1000(abstract_count, len(words))
    voice_rate = per_1000(voice_count, len(words))
    narrative_pct = round(100 * narrative_count / len(paragraphs), 2) if paragraphs else 0
    h3_rate = per_1000(h3_count, len(words))

    load = 0
    load += 2 if abstract_rate > 52 else 1 if abstract_rate > 43 else 0
    load += 2 if avg_paragraph > 60 else 1 if avg_paragraph > 50 else 0
    load += 2 if h3_rate > 3.7 else 1 if h3_rate > 2.7 else 0
    # Quoted speech is one way to situate an argument, not a mandatory style.
    # Do not penalize low dialogue when concrete narrative already carries the
    # situatedness signal; otherwise the index rewards decorative quotation.
    if narrative_pct < 20:
        load += 2 if voice_rate < 1.5 else 1 if voice_rate < 3.0 else 0
    load += 2 if narrative_pct < 12 else 1 if narrative_pct < 20 else 0
    load += 1 if long_sentence_pct >= 6 else 0
    automatic_signal = "ALTA" if load >= 7 else "MEDIA" if load >= 4 else "BAJA"

    return Row(
        n=f"N{number:02d}",
        title=title,
        source=str(path.relative_to(ROOT)),
        source_sha256=hashlib.sha256(source_bytes).hexdigest(),
        body_words=len(words),
        sentences=len(sentences),
        avg_sentence_words=round(avg_sentence, 2),
        p90_sentence_words=percentile(sentence_lengths, 0.9),
        long_sentences_pct=round(long_sentence_pct, 2),
        paragraphs=len(paragraphs),
        avg_paragraph_words=round(avg_paragraph, 2),
        p90_paragraph_words=percentile(paragraph_lengths, 0.9),
        very_long_paragraphs_pct=round(very_long_paragraph_pct, 2),
        h3_per_1000_words=h3_rate,
        abstract_terms_per_1000=abstract_rate,
        nominalizations_per_1000=per_1000(nominal_count, len(words)),
        situated_names_per_1000=per_1000(situated_count, len(words)),
        voice_marks_per_1000=voice_rate,
        narrative_paragraphs_pct=narrative_pct,
        load_index=load,
        automatic_signal=automatic_signal,
    )


def main() -> None:
    paths = source_paths()
    missing = [number for number in range(37) if number not in paths or not paths[number].is_file()]
    if missing:
        raise SystemExit(f"Missing source documents: {missing}")
    rows = [analyse(number, paths[number]) for number in range(37)]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with (OUT_DIR / "metrics.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)
    (OUT_DIR / "metrics.json").write_text(
        json.dumps([asdict(row) for row in rows], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "documents": len(rows),
        "automatic_load_signal": {label: sum(row.automatic_signal == label for row in rows) for label in ("BAJA", "MEDIA", "ALTA")},
        "outputs": [str(OUT_DIR / "metrics.csv"), str(OUT_DIR / "metrics.json")],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
