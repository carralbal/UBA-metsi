#!/usr/bin/env python3
"""Flag sparse interior PDF leaves for human visual review.

This is a diagnostic, not a substitute for reviewing each page. Covers,
frontmatter, photos, and deliberate visual pauses may be sparse by design.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pdfplumber


def audit(pdf_path: Path) -> list[tuple[int, int, float]]:
    result = []
    with pdfplumber.open(pdf_path) as pdf:
        for number, page in enumerate(pdf.pages, start=1):
            if number <= 5 or number >= len(pdf.pages) - 1 or page.images:
                continue
            words = page.extract_words()
            bottom = max((word["bottom"] for word in words), default=0)
            fraction = bottom / page.height
            if len(words) < 45 or fraction < 0.52:
                result.append((number, len(words), round(fraction, 2)))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", type=Path)
    options = parser.parse_args()
    for number in range(1, 37):
        pdf = options.stage / f"N{number:02d}" / "candidate.pdf"
        sparse = audit(pdf)
        if sparse:
            print(f"N{number:02d}: " + ", ".join(f"p{page} {words}w {fill:.0%}" for page, words, fill in sparse))
