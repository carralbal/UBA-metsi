#!/usr/bin/env python3
"""Expand only page 1 artwork to the PDF media box.

Chromium occasionally prints a named zero-margin cover at about 90.7% while
leaving all subsequent A4 pages correct.  This post-process maps the detected
cover artwork bounds to the unchanged A4 media box and copies every interior
page without transformation.
"""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

from PIL import Image
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import RectangleObject


def rendered_content_bbox(pdf: Path) -> tuple[int, int, int, int, int, int]:
    with tempfile.TemporaryDirectory(prefix="metsi-cover-bbox-") as tmp:
        prefix = Path(tmp) / "cover"
        subprocess.run(
            [
                "pdftoppm",
                "-f",
                "1",
                "-singlefile",
                "-r",
                "72",
                "-png",
                str(pdf),
                str(prefix),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        image = Image.open(prefix.with_suffix(".png")).convert("RGB")
        pixels = image.load()
        xs: list[int] = []
        ys: list[int] = []
        for y in range(image.height):
            for x in range(image.width):
                if min(pixels[x, y]) < 247:
                    xs.append(x)
                    ys.append(y)
        if not xs:
            raise RuntimeError("No se detectó arte en la primera página")
        return (
            min(xs),
            min(ys),
            max(xs) + 1,
            max(ys) + 1,
            image.width,
            image.height,
        )


def fix(input_pdf: Path, output_pdf: Path) -> None:
    x0_px, y0_px, x1_px, y1_px, image_w, image_h = rendered_content_bbox(input_pdf)
    reader = PdfReader(str(input_pdf))
    first = reader.pages[0]
    page_w = float(first.mediabox.width)
    page_h = float(first.mediabox.height)

    x0 = x0_px / image_w * page_w
    x1 = x1_px / image_w * page_w
    y0 = (image_h - y1_px) / image_h * page_h
    y1 = (image_h - y0_px) / image_h * page_h
    content_w = x1 - x0
    content_h = y1 - y0

    # Uniform scaling preserves the editorial typography.  Centering absorbs
    # the sub-pixel A4/raster ratio difference as a fraction of a point.
    scale = max(page_w / content_w, page_h / content_h)
    translate_x = (page_w - content_w * scale) / 2 - x0 * scale
    translate_y = (page_h - content_h * scale) / 2 - y0 * scale
    first.add_transformation(
        Transformation((scale, 0, 0, scale, translate_x, translate_y))
    )
    page_box = RectangleObject((0, 0, page_w, page_h))
    first.mediabox = page_box
    first.cropbox = RectangleObject((0, 0, page_w, page_h))
    first.trimbox = RectangleObject((0, 0, page_w, page_h))
    first.bleedbox = RectangleObject((0, 0, page_w, page_h))

    writer = PdfWriter()
    writer.add_page(first)
    for page in reader.pages[1:]:
        writer.add_page(page)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    with output_pdf.open("wb") as handle:
        writer.write(handle)
    print(
        f"FULL_BLEED first-page bbox={x0_px},{y0_px},{x1_px},{y1_px} "
        f"scale={scale:.6f} pages={len(reader.pages)}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    fix(args.input.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
