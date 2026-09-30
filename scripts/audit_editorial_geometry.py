#!/usr/bin/env python3
"""Flag suspicious interior leaves in the cover-locked editorial recovery.

This is a triage aid, not an automatic design approval. Full-bleed and large
photographic pages are excluded from the low-text-density warning.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import pdfplumber


def inspect(pdf_path: Path) -> list[dict]:
    findings: list[dict] = []
    with pdfplumber.open(pdf_path) as pdf:
        for index, page in enumerate(pdf.pages, start=1):
            if index <= 5 or index >= len(pdf.pages) - 1:
                continue
            words = page.extract_words()
            nonblank = [ch for ch in page.chars if ch["text"].strip()]
            out = [
                ch for ch in nonblank
                if ch["x0"] < -0.75 or ch["x1"] > page.width + 0.75
                or ch["top"] < -0.75 or ch["bottom"] > page.height + 0.75
            ]
            large_image = any(
                image["width"] * image["height"] > page.width * page.height * 0.17
                for image in page.images
            )
            text_bottom = max((word["bottom"] for word in words), default=0)
            fill = text_bottom / page.height
            overlap = 0
            buckets: dict[tuple[int, int], list[dict]] = defaultdict(list)
            for char in nonblank:
                bx, by = int(char["x0"] // 12), int(char["top"] // 12)
                for xx in range(bx - 1, bx + 2):
                    for yy in range(by - 2, by + 2):
                        for other in buckets[xx, yy]:
                            if abs(char["bottom"] - other["bottom"]) < 2:
                                continue
                            ix = min(char["x1"], other["x1"]) - max(char["x0"], other["x0"])
                            iy = min(char["bottom"], other["bottom"]) - max(char["top"], other["top"])
                            if ix > min(char["width"], other["width"]) * 0.65 and iy > min(char["height"], other["height"]) * 0.55:
                                overlap += 1
                buckets[bx, by].append(char)
            sparse = not large_image and (fill < 0.46 or len(words) < 85)
            if sparse or out or overlap:
                findings.append({
                    "page": index,
                    "words": len(words),
                    "text_fill": round(fill, 3),
                    "large_image": large_image,
                    "out_of_bounds": len(out),
                    "overlap_candidates": overlap,
                })
    return findings


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", type=Path)
    args = parser.parse_args()
    report = {}
    for number in range(1, 37):
        code = f"N{number:02d}"
        report[code] = inspect(args.stage / code / "candidate.pdf")
        if report[code]:
            print(code, " ".join(
                f"p{row['page']}:{row['words']}w/{row['text_fill']:.0%}"
                + (f" OOB{row['out_of_bounds']}" if row['out_of_bounds'] else "")
                + (f" overlap{row['overlap_candidates']}" if row['overlap_candidates'] else "")
                for row in report[code]
            ))
    (args.stage / "geometry-audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    )
