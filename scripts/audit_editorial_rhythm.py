#!/usr/bin/env python3
"""Compare the page rhythm of current readings with approved editorial PDFs.

This is a triage report, not visual approval. It finds sustained text-heavy
runs, large photographic pauses and unusually sparse interior leaves so every
flagged page can be reviewed at full resolution.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]


def approved_package(number: int) -> Path:
    if number <= 10:
        early_versions = {1: 19, 2: 16, 3: 11, 4: 10, 5: 11, 6: 11, 7: 11, 8: 11, 9: 11, 10: 10}
        name = f"N{number:02d}-v{early_versions[number]}-final"
    else:
        name = f"N{number:02d}-v10-editorial"
    return ROOT / name


def pdf_for(package: Path) -> Path:
    version = package.name.split("-v", 1)[1].split("-", 1)[0]
    matches = list((package / "output").glob(f"*-v{version}-final.pdf"))
    if len(matches) != 1:
        raise ValueError(f"Expected one approved v{version} PDF in {package / 'output'}: {matches}")
    return matches[0]


def longest_run(values: list[bool]) -> tuple[int, list[list[int]]]:
    runs: list[list[int]] = []
    active: list[int] = []
    for index, value in enumerate(values, start=1):
        if value:
            active.append(index)
        elif active:
            runs.append(active)
            active = []
    if active:
        runs.append(active)
    return max((len(run) for run in runs), default=0), [run for run in runs if len(run) >= 3]


def audit(pdf_path: Path) -> dict:
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        count = len(pdf.pages)
        for index, page in enumerate(pdf.pages, start=1):
            words = page.extract_words()
            area = float(page.width * page.height)
            image_areas = [
                max(0.0, min(float(image["x1"]), page.width) - max(float(image["x0"]), 0.0))
                * max(0.0, min(float(image["bottom"]), page.height) - max(float(image["top"]), 0.0))
                for image in page.images
            ]
            photo_fraction = min(1.0, sum(image_areas) / area)
            pages.append(
                {
                    "page": index,
                    "words": len(words),
                    "images": len(page.images),
                    "image_area_fraction": round(photo_fraction, 3),
                    "text_dominant": 4 <= index <= count - 2 and len(words) >= 300 and photo_fraction < 0.08,
                    "large_image": 4 <= index <= count - 2 and photo_fraction >= 0.28,
                    "sparse": 4 <= index <= count - 2 and len(words) < 65 and photo_fraction < 0.06,
                }
            )
    max_run, long_runs = longest_run([page["text_dominant"] for page in pages])
    return {
        "path": str(pdf_path),
        "pages": len(pages),
        "text_dominant_pages": [page["page"] for page in pages if page["text_dominant"]],
        "large_image_pages": [page["page"] for page in pages if page["large_image"]],
        "sparse_pages": [page["page"] for page in pages if page["sparse"]],
        "longest_text_run": max_run,
        "text_runs_3plus": long_runs,
        "page_detail": pages,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = []
    for number in range(1, 37):
        public_dir = ROOT / ("site/pdf" if number <= 10 else "site/pdf/publicados")
        matches = list(public_dir.glob(f"N{number:02d}-*.pdf"))
        if len(matches) != 1:
            raise ValueError(f"N{number:02d}: ambiguous public PDF: {matches}")
        current = matches[0]
        before = audit(pdf_for(approved_package(number)))
        after = audit(current)
        result.append({"document": f"N{number:02d}", "approved": before, "current": after})
        print(
            f"N{number:02d} pages {before['pages']}→{after['pages']}; "
            f"large-image {len(before['large_image_pages'])}→{len(after['large_image_pages'])}; "
            f"dense text {len(before['text_dominant_pages'])}→{len(after['text_dominant_pages'])}; "
            f"longest run {before['longest_text_run']}→{after['longest_text_run']}; "
            f"sparse {len(before['sparse_pages'])}→{len(after['sparse_pages'])}"
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
