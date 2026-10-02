#!/usr/bin/env python3
"""Find likely printed-text collisions in staged N PDFs for visual review.

Geometry is only a triage signal: intentional drop caps and layered typography
still need a human review of the rendered page.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pdfplumber


def collisions(pdf: Path) -> list[tuple[int, str, str, float, float]]:
    found = []
    with pdfplumber.open(pdf) as document:
        for page_number, page in enumerate(document.pages, start=1):
            words = sorted(page.extract_words(), key=lambda word: word["top"])
            for index, left in enumerate(words):
                for right in words[index + 1 :]:
                    if right["top"] >= left["bottom"]:
                        break
                    overlap_x = min(left["x1"], right["x1"]) - max(left["x0"], right["x0"])
                    overlap_y = min(left["bottom"], right["bottom"]) - max(left["top"], right["top"])
                    if overlap_x <= 0 or overlap_y <= 0:
                        continue
                    narrower = min(left["x1"] - left["x0"], right["x1"] - right["x0"])
                    shorter = min(left["bottom"] - left["top"], right["bottom"] - right["top"])
                    if overlap_x / narrower < .4 or overlap_y / shorter < .42:
                        continue
                    found.append((page_number, left["text"], right["text"], left["top"], left["x0"]))
    return found


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", type=Path)
    parser.add_argument("numbers", nargs="*", type=int)
    args = parser.parse_args()
    for number in args.numbers or range(1, 37):
        pdf = args.stage / f"N{number:02d}" / "candidate.pdf"
        matches = collisions(pdf)
        print(f"N{number:02d}: {len(matches)} possible overlaps")
        for page, a, b, y, x in matches[:25]:
            print(f"  p{page:02d} x{x:.1f} y{y:.1f} {a!r} / {b!r}")


if __name__ == "__main__":
    main()
