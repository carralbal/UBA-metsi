#!/usr/bin/env python3
"""Make an overview of every page of a staged reading for visual review."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def contact(stage: Path, number: int, published: bool = False) -> Path:
    folder = stage / f"N{number:02d}"
    if published:
        root = Path(__file__).resolve().parents[1]
        public_dir = root / ("site/pdf" if number <= 10 else "site/pdf/publicados")
        matches = list(public_dir.glob(f"N{number:02d}-*.pdf"))
        if len(matches) != 1:
            raise ValueError(f"N{number:02d}: expected one published PDF, found {matches}")
        pdf = matches[0]
        folder.mkdir(parents=True, exist_ok=True)
    else:
        pdf = folder / "candidate.pdf"
    with tempfile.TemporaryDirectory(prefix=f"metsi-n{number:02d}-") as scratch:
        prefix = Path(scratch) / "page"
        subprocess.run(
            ["pdftoppm", "-jpeg", "-scale-to", "320", str(pdf), str(prefix)],
            check=True,
            capture_output=True,
        )
        pages = sorted(prefix.parent.glob("page-*.jpg"))
        width, height = 214, 338
        columns = 6
        rows = (len(pages) + columns - 1) // columns
        canvas = Image.new("RGB", (columns * width, rows * height), "#d3d3d3")
        draw = ImageDraw.Draw(canvas)
        for index, page in enumerate(pages):
            thumbnail = Image.open(page).convert("RGB")
            thumbnail.thumbnail((width - 12, height - 31))
            x = (index % columns) * width + (width - thumbnail.width) // 2
            y = (index // columns) * height + 3
            canvas.paste(thumbnail, (x, y))
            draw.text((index % columns * width + 9, y + height - 27), str(index + 1), fill="#111")
        output = folder / ("published-contact.jpg" if published else "contact.jpg")
        canvas.save(output, quality=88)
        return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", type=Path)
    parser.add_argument("numbers", nargs="*", type=int)
    parser.add_argument("--published", action="store_true")
    options = parser.parse_args()
    for number in options.numbers or range(1, 37):
        print(contact(options.stage, number, options.published))
