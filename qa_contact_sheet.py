#!/usr/bin/env python3
"""Build a numbered contact sheet from rendered PDF page images."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--columns", type=int, default=5)
    args = parser.parse_args()

    files = sorted(args.input_dir.glob("page-*.jpg"))
    if not files:
        raise SystemExit("No rendered pages found")

    thumb_w, thumb_h, label_h = 220, 311, 24
    tiles: list[Image.Image] = []
    for number, path in enumerate(files, start=1):
        page = Image.open(path).convert("RGB")
        page.thumbnail((thumb_w, thumb_h))
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(page, ((thumb_w - page.width) // 2, 0))
        ImageDraw.Draw(tile).text((8, thumb_h + 4), str(number), fill="black")
        tiles.append(tile)

    rows = math.ceil(len(tiles) / args.columns)
    sheet = Image.new(
        "RGB",
        (args.columns * thumb_w, rows * (thumb_h + label_h)),
        (40, 40, 40),
    )
    for index, tile in enumerate(tiles):
        sheet.paste(
            tile,
            ((index % args.columns) * thumb_w, (index // args.columns) * (thumb_h + label_h)),
        )
    sheet.save(args.output, quality=88)


if __name__ == "__main__":
    main()
