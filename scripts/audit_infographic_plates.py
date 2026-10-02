#!/usr/bin/env python3
"""Check the revised N11–N36 decision-map pages and render a contact sheet."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
import statistics
from pathlib import Path

from PIL import Image, ImageDraw
from pypdf import PdfReader
import pdfplumber


ROOT = Path(__file__).resolve().parents[1]
NUMBERS = [n for n in range(11, 37) if n != 34]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", type=int, default=11)
    parser.add_argument("--contact-sheet", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    contact = args.contact_sheet.resolve()
    contact.parent.mkdir(parents=True, exist_ok=True)

    cells: list[tuple[int, Image.Image]] = []
    report: list[dict] = []
    with tempfile.TemporaryDirectory(prefix="metsi-map-audit-") as temporary:
        for number in NUMBERS:
            package = ROOT / f"N{number:02d}-v{args.version}-editorial"
            pdf = package / "output" / f"N{number:02d}-METSI-lectura-previa-v{args.version}.pdf"
            integrity = json.loads((package / "integrity-report.json").read_text())
            reader = PdfReader(pdf)
            pages = [
                index for index, page in enumerate(reader.pages)
                if "MAPA DE DECISIÓN" in (page.extract_text() or "")
            ]
            if len(pages) != 1 or integrity["status"] != "PASS":
                raise RuntimeError(f"N{number:02d}: mapa o integridad no verificables")
            index = pages[0]
            page = reader.pages[index]
            width, height = float(page.mediabox.width), float(page.mediabox.height)
            expected_landscape = number <= 19
            if (width > height) != expected_landscape:
                raise RuntimeError(f"N{number:02d}: orientación inesperada")
            with pdfplumber.open(pdf) as measured_pdf:
                characters = [c for c in measured_pdf.pages[index].chars if c["text"].strip()]
                sizes = [float(c["size"]) for c in characters]
                typography = {
                    "minimum_pt": round(min(sizes), 2),
                    "median_character_pt": round(statistics.median(sizes), 2),
                    "percent_characters_below_8pt": round(100 * sum(s < 8 for s in sizes) / len(sizes), 1),
                    "note": "Screening of all text on this plate, including caption and running matter; not a visual QA pass.",
                }

            output = Path(temporary) / f"N{number:02d}"
            subprocess.run(
                [
                    "pdftoppm", "-f", str(index + 1), "-l", str(index + 1),
                    "-png", "-scale-to", "420", "-singlefile", str(pdf), str(output),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            with Image.open(output.with_suffix(".png")) as rendered:
                cells.append((number, rendered.convert("RGB").copy()))
            report.append({
                "document": f"N{number:02d}",
                "page": index + 1,
                "orientation": "landscape" if expected_landscape else "portrait",
                "pages": len(reader.pages),
                "source_integrity": integrity["status"],
                "typography_screening": typography,
            })

    tile_width, tile_height = 460, 590
    columns = 5
    rows = (len(cells) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * tile_width, rows * tile_height), "#e9e9e7")
    draw = ImageDraw.Draw(sheet)
    for position, (number, rendered) in enumerate(cells):
        left = (position % columns) * tile_width
        top = (position // columns) * tile_height
        rendered.thumbnail((tile_width - 28, tile_height - 42))
        x = left + (tile_width - rendered.width) // 2
        y = top + 30 + (tile_height - 42 - rendered.height) // 2
        sheet.paste(rendered, (x, y))
        draw.text((left + 14, top + 8), f"N{number:02d}", fill="#191919")
    sheet.save(contact)
    if args.report:
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"CONTACT_SHEET {contact}")


if __name__ == "__main__":
    main()
