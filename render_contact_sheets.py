from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "qa-contact-sheets"


def pdf_path(number: int) -> Path:
    code = f"N{number:02d}"
    if number == 1:
        return ROOT / "N01-v18-final" / "output" / "N01-METSI-lectura-previa-v18-final.pdf"
    if number == 2:
        return ROOT / "N02-v14-final" / "output" / "N02-METSI-lectura-previa-v14-final.pdf"
    if number == 3:
        return ROOT / "N03-v9-final" / "output" / "N03-METSI-lectura-previa-v9-final.pdf"
    if number == 4:
        return ROOT / "N04-v9-final" / "output" / "N04-METSI-lectura-previa-v9-final.pdf"
    return ROOT / code / "output" / f"{code}-METSI-lectura-previa-final.pdf"


def render(number: int) -> Path:
    code = f"N{number:02d}"
    tmp = OUT / f"{code}-pages"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    subprocess.run(
        ["pdftoppm", "-jpeg", "-r", "42", "-jpegopt", "quality=74", str(pdf_path(number)), str(tmp / "p")],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    pages = [Image.open(p).convert("RGB") for p in sorted(tmp.glob("p-*.jpg"))]
    thumb_w = 248
    gap = 18
    label_h = 28
    thumbs = []
    for idx, page in enumerate(pages, 1):
        h = round(page.height * thumb_w / page.width)
        thumb = page.resize((thumb_w, h), Image.Resampling.LANCZOS)
        cell = Image.new("RGB", (thumb_w, h + label_h), "#d9d9d9")
        cell.paste(thumb, (0, label_h))
        ImageDraw.Draw(cell).text((6, 6), f"{code} · {idx:02d}", fill="#222222")
        thumbs.append(cell)
    cols = 5
    rows = (len(thumbs) + cols - 1) // cols
    cell_h = max(t.height for t in thumbs)
    sheet = Image.new("RGB", (cols * thumb_w + (cols + 1) * gap, rows * cell_h + (rows + 1) * gap), "#bcbcbc")
    for idx, thumb in enumerate(thumbs):
        x = gap + (idx % cols) * (thumb_w + gap)
        y = gap + (idx // cols) * (cell_h + gap)
        sheet.paste(thumb, (x, y))
    output = OUT / f"{code}-contact-sheet.jpg"
    sheet.save(output, quality=87, optimize=True)
    if number == 1:
        package_qa = ROOT / "N01-v18-final" / "qa"
        package_qa.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output, package_qa / output.name)
    if number == 2:
        package_qa = ROOT / "N02-v14-final" / "qa"
        package_qa.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output, package_qa / output.name)
    if number == 3:
        package_qa = ROOT / "N03-v9-final" / "qa"
        package_qa.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output, package_qa / output.name)
    if number == 4:
        package_qa = ROOT / "N04-v9-final" / "qa"
        package_qa.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output, package_qa / output.name)
    shutil.rmtree(tmp)
    return output


OUT.mkdir(parents=True, exist_ok=True)
for raw in sys.argv[1:]:
    print(render(int(raw)))
