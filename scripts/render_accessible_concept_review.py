#!/usr/bin/env python3
"""Renderiza las páginas que recibieron puentes llanos para revisión visual."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "editorial-standard" / "accessible-concept-integration-audit-n00-n36.json"
OUT = ROOT / "qa-accessible-concepts"


def final_pdf(package: Path) -> Path:
    matches = sorted((package / "output").glob("*final.pdf"))
    if len(matches) != 1:
        raise RuntimeError(f"{package.name}: PDF final ambiguo")
    return matches[0]


def main() -> None:
    data = json.loads(REPORT.read_text(encoding="utf-8"))
    OUT.mkdir(exist_ok=True)
    renderer = shutil.which("pdftoppm")
    if not renderer:
        raise RuntimeError("pdftoppm no disponible")

    rendered: list[tuple[str, int, Path]] = []
    for row in data["results"]:
        doc = row["document"]
        package = ROOT / row["package"]
        pdf = final_pdf(package)
        for page in sorted({item["pdf_page"] for item in row["concepts"]}):
            target = OUT / f"{doc}-page-{page:02d}"
            png = target.with_suffix(".png")
            subprocess.run([
                renderer, "-f", str(page), "-l", str(page), "-r", "135",
                "-png", "-singlefile", str(pdf), str(target),
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            rendered.append((doc, page, png))

    thumb_w, thumb_h = 300, 424
    label_h, gap, cols = 28, 16, 5
    rows = (len(rendered) + cols - 1) // cols
    sheet = Image.new("RGB", (gap + cols * (thumb_w + gap), gap + rows * (thumb_h + label_h + gap)), "#b8b8b8")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, (doc, page, png) in enumerate(rendered):
        image = Image.open(png).convert("RGB")
        image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        col, row = index % cols, index // cols
        x, y = gap + col * (thumb_w + gap), gap + row * (thumb_h + label_h + gap)
        draw.text((x, y), f"{doc} · página {page}", fill="#111111", font=font)
        sheet.paste(image, (x, y + label_h))
    sheet.save(OUT / "accessible-concept-pages-contact-sheet.jpg", quality=92)
    print(json.dumps({"status": "RENDERED", "pages": len(rendered), "sheet": str(OUT / "accessible-concept-pages-contact-sheet.jpg")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
