#!/usr/bin/env python3
"""Report page-level text, image and vertical-fill evidence for METSI PDFs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pdfplumber


def page_record(page: pdfplumber.page.Page, number: int) -> dict[str, object]:
    text = page.extract_text() or ""
    words = page.extract_words(use_text_flow=True, keep_blank_chars=False)
    content_words = [word for word in words if float(word["top"]) < 790]
    images = page.images
    tops = [float(word["top"]) for word in content_words]
    bottoms = [float(word["bottom"]) for word in content_words]
    for image in images:
        top = image.get("top")
        bottom = image.get("bottom")
        if top is not None and bottom is not None and float(top) < 790:
            tops.append(float(top))
            bottoms.append(float(bottom))
    content_top = min(tops) if tops else None
    content_bottom = max(bottoms) if bottoms else None
    vertical_span = (
        round(content_bottom - content_top, 2)
        if content_top is not None and content_bottom is not None
        else 0
    )
    return {
        "page": number,
        "text_preview": " | ".join(text.splitlines())[:260],
        "content_top": content_top,
        "content_bottom": content_bottom,
        "vertical_span": vertical_span,
        "fill_ratio_of_744pt": round(vertical_span / 744, 3),
        "image_count": len(images),
        "image_bounds": [
            {
                "x0": round(float(image.get("x0", 0)), 1),
                "x1": round(float(image.get("x1", 0)), 1),
                "top": round(float(image.get("top", 0)), 1),
                "bottom": round(float(image.get("bottom", 0)), 1),
            }
            for image in images
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    with pdfplumber.open(args.pdf) as document:
        records = [page_record(page, index) for index, page in enumerate(document.pages, 1)]
    if args.json:
        print(json.dumps(records, ensure_ascii=False, indent=2))
        return
    for record in records:
        print(
            f"p{record['page']:02d} fill={record['fill_ratio_of_744pt']:.3f} "
            f"span={record['vertical_span']:>6} images={record['image_count']} "
            f"{record['text_preview']}"
        )


if __name__ == "__main__":
    main()
