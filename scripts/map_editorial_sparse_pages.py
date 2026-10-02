#!/usr/bin/env python3
"""Map sparse candidate PDF pages back to their source magazine sections."""

from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

import pdfplumber
from lxml import html

from audit_editorial_page_density import audit


def words(text: str) -> list[str]:
    text = unicodedata.normalize("NFKD", text).lower()
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.findall(r"[a-z0-9]{3,}", text)


def shingles(tokens: list[str], width: int = 5) -> set[tuple[str, ...]]:
    return set(zip(*(tokens[offset:] for offset in range(width))))


def section_matches(source: Path, page_text: str) -> list[tuple[int, str, str]]:
    tree = html.parse(str(source))
    page_shingles = shingles(words(page_text))
    ranked = []
    for section in tree.xpath("//section[contains(@class,'reading-section')]"):
        section_shingles = shingles(words(" ".join(section.itertext())))
        overlap = len(page_shingles & section_shingles)
        if overlap:
            ranked.append((overlap, section.get("data-section", "?"), section.get("class", "")))
    return sorted(ranked, reverse=True)[:3]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", type=Path)
    parser.add_argument("numbers", nargs="*", type=int)
    options = parser.parse_args()
    for number in options.numbers or range(1, 37):
        folder = options.stage / f"N{number:02d}"
        sparse = audit(folder / "candidate.pdf")
        if not sparse:
            continue
        with pdfplumber.open(folder / "candidate.pdf") as pdf:
            for page_number, count, fill in sparse:
                matches = section_matches(folder / "index.html", pdf.pages[page_number - 1].extract_text() or "")
                if matches:
                    score, section_number, classes = matches[0]
                    print(f"N{number:02d} p{page_number}: {count}w {fill:.0%} → §{section_number} ({score} matches) {classes}")


if __name__ == "__main__":
    main()
