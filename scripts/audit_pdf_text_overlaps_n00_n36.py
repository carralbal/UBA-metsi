#!/usr/bin/env python3
"""Detecta texto recortado y cajas de palabras superpuestas en N00–N36."""

from __future__ import annotations

import json
from pathlib import Path

import pdfplumber
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = {
    0: ("N00-v3-final", "v3"), 1: ("N01-v18-final", "v18"),
    2: ("N02-v15-final", "v15"), 3: ("N03-v10-final", "v10"),
    4: ("N04-v9-final", "v9"), 5: ("N05-v10-final", "v10"),
    6: ("N06-v10-final", "v10"), 7: ("N07-v10-final", "v10"),
    8: ("N08-v10-final", "v10"), 9: ("N09-v10-final", "v10"),
    10: ("N10-v9-final", "v9"),
}


def pdf_path(number: int) -> Path:
    code = f"N{number:02d}"
    if number <= 10:
        package, version = PACKAGES[number]
    else:
        package, version = f"{code}-v9-editorial", "v9"
    return ROOT / package / "output" / f"{code}-METSI-lectura-previa-{version}-final.pdf"


def intersection(a: dict, b: dict) -> tuple[float, float, float]:
    width = max(0.0, min(float(a["x1"]), float(b["x1"])) - max(float(a["x0"]), float(b["x0"])))
    height = max(0.0, min(float(a["bottom"]), float(b["bottom"])) - max(float(a["top"]), float(b["top"])))
    area = width * height
    return width, height, area


def page_collisions(words: list[dict]) -> list[dict]:
    collisions = []
    ordered = sorted(words, key=lambda item: (float(item["top"]), float(item["x0"])))
    for i, left in enumerate(ordered):
        for right in ordered[i + 1:]:
            if float(right["top"]) > float(left["bottom"]) + 1.0:
                break
            width, height, area = intersection(left, right)
            if width <= 1.0 or height <= 1.0:
                continue
            left_area = max(1.0, (float(left["x1"]) - float(left["x0"])) * (float(left["bottom"]) - float(left["top"])))
            right_area = max(1.0, (float(right["x1"]) - float(right["x0"])) * (float(right["bottom"]) - float(right["top"])))
            ratio = area / min(left_area, right_area)
            same = left.get("text") == right.get("text")
            if ratio >= 0.18 and not same:
                collisions.append({
                    "left": left.get("text"), "right": right.get("text"),
                    "overlap_ratio": round(ratio, 3),
                    "left_bbox": [round(float(left[k]), 2) for k in ("x0", "top", "x1", "bottom")],
                    "right_bbox": [round(float(right[k]), 2) for k in ("x0", "top", "x1", "bottom")],
                })
                if len(collisions) >= 30:
                    break
        if len(collisions) >= 30:
            break
    return collisions


def audit(number: int) -> dict:
    code = f"N{number:02d}"
    path = pdf_path(number)
    reader = PdfReader(path, strict=True)
    pages = []
    with pdfplumber.open(path) as pdf:
        for index, page in enumerate(pdf.pages, 1):
            words = page.extract_words(use_text_flow=False) or []
            clipped = [
                {"text": word.get("text"), "bbox": [word.get(k) for k in ("x0", "top", "x1", "bottom")]}
                for word in words
                if float(word["x0"]) < -0.5 or float(word["x1"]) > float(page.width) + 0.5
                or float(word["top"]) < -0.5 or float(word["bottom"]) > float(page.height) + 0.5
            ]
            collisions = page_collisions(words)
            if clipped or collisions:
                pages.append({"page": index, "clipped": clipped[:20], "collisions": collisions})
    a4 = all(
        abs(float(page.mediabox.width) - 595.28) <= 1.0
        and abs(float(page.mediabox.height) - 841.89) <= 1.0
        for page in reader.pages
    )
    return {
        "document": code,
        "pdf": str(path.relative_to(ROOT)),
        "pages": len(reader.pages),
        "a4": a4,
        "problem_pages": pages,
        "status": "PASS" if a4 and not pages else "FAIL",
    }


def main() -> None:
    documents = [audit(number) for number in range(37)]
    report = {
        "scope": "N00-N36 final PDFs",
        "documents": documents,
        "summary": {
            "documents": len(documents),
            "passed": sum(item["status"] == "PASS" for item in documents),
            "failed": sum(item["status"] != "PASS" for item in documents),
            "pages": sum(item["pages"] for item in documents),
        },
    }
    output = ROOT / "editorial-standard" / "pdf-text-overlap-audit-n00-n36.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
