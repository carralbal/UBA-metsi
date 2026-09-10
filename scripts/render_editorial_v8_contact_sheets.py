#!/usr/bin/env python3
"""Render every N11-N36 v8 PDF and build deterministic visual QA sheets."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "qa-reports" / "n11-n36-v8" / "contact-sheets"


def render(number: int) -> Path:
    code = f"N{number:02d}"
    pdf = ROOT / f"{code}-v8-editorial" / "output" / f"{code}-METSI-lectura-previa-v8-final.pdf"
    if not pdf.is_file():
        raise FileNotFoundError(pdf)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"metsi-{code}-v8-") as folder:
        prefix = Path(folder) / "page"
        subprocess.run(
            ["pdftoppm", "-png", "-r", "54", str(pdf), str(prefix)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        pages = sorted(Path(folder).glob("page-*.png"))
        tiles: list[Image.Image] = []
        for index, path in enumerate(pages, 1):
            image = Image.open(path).convert("RGB")
            image.thumbnail((170, 240), Image.Resampling.LANCZOS)
            tile = Image.new("RGB", (182, 264), "white")
            tile.paste(image, ((182 - image.width) // 2, 5))
            ImageDraw.Draw(tile).text((7, 247), f"{code} · p. {index:02d}", fill="#171917")
            tiles.append(tile)
        columns = 5
        rows = (len(tiles) + columns - 1) // columns
        sheet = Image.new("RGB", (columns * 182, rows * 264), "#D9DAD7")
        for index, tile in enumerate(tiles):
            sheet.paste(tile, ((index % columns) * 182, (index // columns) * 264))
        target = OUTPUT / f"{code}-contact-sheet-v8.png"
        sheet.save(target, format="PNG", optimize=True)
    print(f"RENDERED {code} {len(pages)} pages", flush=True)
    return target


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=11)
    parser.add_argument("--end", type=int, default=36)
    args = parser.parse_args()
    for number in range(args.start, args.end + 1):
        render(number)


if __name__ == "__main__":
    main()
