#!/usr/bin/env python3
"""Render all newly composed argument plates for one collection-level visual pass."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw
from pypdf import PdfReader

from prepare_editorial_recovery import EDITORIAL_FIELD_NOTES


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", type=Path)
    options = parser.parse_args()
    cells = []
    for number in EDITORIAL_FIELD_NOTES:
        folder = options.stage / f"N{number:02d}"
        pdf = folder / "candidate.pdf"
        pages = [
            index + 1 for index, page in enumerate(PdfReader(pdf).pages)
            if "LECTURA VISUAL" in (page.extract_text() or "")
        ]
        expected = 2 if number in {24, 26} else 1
        if len(pages) != expected:
            raise ValueError(f"N{number:02d}: argument plate appears on {pages}")
        for page in pages:
            prefix = folder / f"field-note-preview-{page}"
            subprocess.run(
                ["pdftoppm", "-f", str(page), "-l", str(page),
                 "-singlefile", "-png", "-scale-to", "700", str(pdf), str(prefix)],
                check=True,
                stdout=subprocess.DEVNULL,
            )
            with Image.open(prefix.with_suffix(".png")) as rendered:
                cells.append((number, page, rendered.convert("RGB").copy()))
    width, height, cols = 372, 570, 4
    rows = (len(cells) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * width, rows * height), "#dddcd8")
    draw = ImageDraw.Draw(sheet)
    for index, (number, page, image) in enumerate(cells):
        image.thumbnail((width - 16, height - 34))
        x = (index % cols) * width + (width - image.width) // 2
        y = (index // cols) * height + 5
        sheet.paste(image, (x, y))
        draw.text((x + 8, (index // cols) * height + height - 24), f"N{number:02d} · página {page}", fill="#171917")
    target = options.stage / "editorial-field-notes-contact.png"
    sheet.save(target)
    print(target)


if __name__ == "__main__":
    main()
