#!/usr/bin/env python3
"""Render every regionalized PDF page and assemble one QA contact sheet per N."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audits" / "regionalization-final-pdf-audit-n01-n36-2026-09-15.json"
OUT = ROOT / "audits" / "regionalization-contact-sheets-2026-09-15"
RENDER = Path("/private/tmp/metsi-regionalization-page-renders")


def main() -> None:
    report = json.loads(AUDIT.read_text())
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    if RENDER.exists():
        shutil.rmtree(RENDER)
    RENDER.mkdir(parents=True)
    rows = []
    for item in report["documents"]:
        code = item["document"]
        pdf = ROOT / item["pdf"]
        expected = len(PdfReader(pdf).pages)
        pages_dir = RENDER / code
        pages_dir.mkdir()
        prefix = pages_dir / code
        subprocess.run(
            ["pdftoppm", "-jpeg", "-r", "36", "-jpegopt", "quality=82", str(pdf), str(prefix)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        page_files = sorted(pages_dir.glob(f"{code}-*.jpg"))
        if len(page_files) != expected:
            raise RuntimeError(f"{code}: rendered {len(page_files)} of {expected} pages")
        cols, tile_w, tile_h, label_h = 5, 180, 255, 18
        rows_count = (expected + cols - 1) // cols
        sheet = Image.new("RGB", (cols * tile_w, rows_count * (tile_h + label_h)), "#d9d9d6")
        draw = ImageDraw.Draw(sheet)
        for index, page_file in enumerate(page_files):
            image = Image.open(page_file).convert("RGB")
            image.thumbnail((tile_w - 8, tile_h - 8))
            x = (index % cols) * tile_w + (tile_w - image.width) // 2
            y0 = (index // cols) * (tile_h + label_h)
            y = y0 + label_h + (tile_h - image.height) // 2
            sheet.paste(image, (x, y))
            draw.text((x, y0 + 2), f"{code} · {index + 1:02d}", fill="#151515")
        target = OUT / f"{code}-contact-sheet.jpg"
        sheet.save(target, quality=88, optimize=True)
        rows.append({"document": code, "pages_expected": expected, "pages_rendered": len(page_files), "contact_sheet": target.relative_to(ROOT).as_posix()})
        print(f"RENDERED {code} {expected}/{expected}")
    manifest = {
        "date": "2026-09-15",
        "documents": len(rows),
        "pages_expected": sum(row["pages_expected"] for row in rows),
        "pages_rendered": sum(row["pages_rendered"] for row in rows),
        "rows": rows,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: manifest[key] for key in ("documents", "pages_expected", "pages_rendered")}))


if __name__ == "__main__":
    main()
