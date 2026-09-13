#!/usr/bin/env python3
"""Render deterministic visual QA contact sheets for editorial candidates."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]


def render(number: int, version: int) -> Path:
    code = f"N{number:02d}"
    package = ROOT / f"{code}-v{version}-editorial"
    pdf = package / "output" / f"{code}-METSI-lectura-previa-v{version}-final.pdf"
    if not pdf.is_file():
        raise FileNotFoundError(pdf)
    output = package / "qa"
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"metsi-{code}-v{version}-") as folder:
        prefix = Path(folder) / "page"
        subprocess.run(
            ["pdftoppm", "-png", "-r", "60", str(pdf), str(prefix)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        pages = sorted(
            Path(folder).glob("page-*.png"),
            key=lambda path: int(path.stem.rsplit("-", 1)[-1]),
        )
        tiles: list[Image.Image] = []
        for index, path in enumerate(pages, 1):
            image = Image.open(path).convert("RGB")
            image.thumbnail((196, 278), Image.Resampling.LANCZOS)
            tile = Image.new("RGB", (208, 304), "white")
            tile.paste(image, ((208 - image.width) // 2, 5))
            ImageDraw.Draw(tile).text((7, 285), f"{code} · p. {index:02d}", fill="#171917")
            tiles.append(tile)
        columns = 5
        rows = (len(tiles) + columns - 1) // columns
        sheet = Image.new("RGB", (columns * 208, rows * 304), "#D9DAD7")
        for index, tile in enumerate(tiles):
            sheet.paste(tile, ((index % columns) * 208, (index // columns) * 304))
        target = output / f"{code}-contact-sheet-v{version}.png"
        sheet.save(target, format="PNG", optimize=True)
    print(f"RENDERED {code} v{version} {len(pages)} pages")
    return target


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--version", type=int, required=True)
    args = parser.parse_args()
    for number in range(args.start, args.end + 1):
        render(number, args.version)


if __name__ == "__main__":
    main()
