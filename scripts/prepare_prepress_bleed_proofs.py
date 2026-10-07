#!/usr/bin/env python3
"""Make reversible, content-preserving bleed proofs from the published PDFs.

This is a prepress proof, not an installer.  It changes only the two opening
editorial pages (question and photographic pause) and leaves every other page
as the original PDF page object.  The existing source PDFs are never written.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import tempfile
from pathlib import Path

import pdfplumber
from pypdf import PdfReader, PdfWriter
from pypdf._page import PageObject
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image, ImageDraw, ImageOps


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "course-manifest.json"
PAPER_WIDTH = 594.95996
ART_WIDTH = 567.7
FOOTER_HEIGHT = 43.0
INK = HexColor("#191919")
PAPER_TEXT = HexColor("#f4f2ed")
BASKERVILLE = Path("/System/Library/Fonts/Supplemental/Baskerville.ttc")


def footer_overlay(width: float, height: float, folio: int) -> PageObject:
    stream = io.BytesIO()
    canvas = Canvas(stream, pagesize=(width, height), pageCompression=1)
    canvas.setFillColor(INK)
    canvas.rect(0, 0, width, FOOTER_HEIGHT + 0.75, fill=1, stroke=0)
    canvas.setStrokeColor(HexColor("#777875"))
    canvas.setLineWidth(0.35)
    canvas.line(46, FOOTER_HEIGHT + 0.4, width - 46, FOOTER_HEIGHT + 0.4)
    canvas.setFillColor(PAPER_TEXT)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(46, 21, f"{folio:02d}")
    canvas.drawRightString(width - 46, 21, "Diego Carralbal, 2026  ·  linkedin.com/in/carralbal")
    canvas.showPage()
    canvas.save()
    stream.seek(0)
    return PdfReader(stream).pages[0]


def paper_panel_to_ink(source_path: Path, bounds: tuple[float, float, float, float]) -> PageObject:
    """Recolour the original type, preserving its exact content and line breaks."""

    x0, top, x1, bottom = bounds
    with tempfile.TemporaryDirectory(prefix="metsi-panel-") as temporary:
        target = Path(temporary) / "panel"
        subprocess.run(
            ["pdftoppm", "-f", "4", "-l", "4", "-r", "300", "-singlefile",
             "-png", str(source_path), str(target)],
            capture_output=True, check=True,
        )
        with Image.open(target.with_suffix(".png")) as full:
            scale_x = full.width / PAPER_WIDTH
            scale_y = full.height / 841.91998
            crop = full.convert("L").crop((
                round(x0 * scale_x), round(top * scale_y),
                round(x1 * scale_x), round(bottom * scale_y),
            ))
    # Paper and the original text become the same ink/white palette as the
    # surrounding spread.  The underlying PDF retains selectable text.
    shades = [round(25 + 220 * max(0, min(1, (242 - level) / 195))) for level in range(256)]
    crop = crop.point(shades).convert("RGB")
    stream = io.BytesIO()
    canvas = Canvas(stream, pagesize=(PAPER_WIDTH, 841.91998), pageCompression=1)
    canvas.drawImage(ImageReader(crop), x0, 841.91998 - bottom,
                     width=x1 - x0, height=bottom - top)
    # The volt rule remains an accent, never a text colour.
    canvas.setFillColor(HexColor("#d6ff00"))
    canvas.rect(x0, 841.91998 - bottom, 3.0, bottom - top, fill=1, stroke=0)
    canvas.showPage()
    canvas.save()
    stream.seek(0)
    return PdfReader(stream).pages[0]


def opening_page_with_bleed(source: PageObject, folio: int,
                            source_path: Path, panel_bounds: tuple[float, float, float, float] | None) -> PageObject:
    width = float(source.mediabox.width)
    height = float(source.mediabox.height)
    if abs(width - PAPER_WIDTH) > 1 or abs(height - 841.92) > 1:
        raise ValueError(f"Unexpected page size: {width} × {height}")
    proof = PageObject.create_blank_page(width=width, height=height)
    proof.merge_page(source)
    stream = io.BytesIO()
    canvas = Canvas(stream, pagesize=(width, height), pageCompression=1)
    # Extend only the solid-ink artwork, not the typography. This avoids
    # the even small horizontal distortion of a whole-page PDF scale.
    canvas.setFillColor(INK)
    canvas.rect(ART_WIDTH, FOOTER_HEIGHT, width - ART_WIDTH, height - FOOTER_HEIGHT,
                fill=1, stroke=0)
    canvas.showPage()
    canvas.save()
    stream.seek(0)
    proof.merge_page(PdfReader(stream).pages[0])
    if panel_bounds is not None:
        proof.merge_page(paper_panel_to_ink(source_path, panel_bounds))
    proof.merge_page(footer_overlay(width, height, folio))
    return proof


def photo_pause_with_bleed(source: PageObject, lines: list[str], folio: int = 5) -> PageObject:
    """Recompose the same embedded photo and quotation as a full-bleed pause."""

    if len(source.images) != 1:
        raise ValueError(f"Photo opening has {len(source.images)} images")
    with Image.open(io.BytesIO(source.images[0].data)) as embedded:
        image = embedded.convert("L").convert("RGB")
    image = ImageOps.fit(image, (1190, 1684), Image.Resampling.LANCZOS,
                         centering=(0.5, 0.46))
    # A cinematic black gradient makes every quotation legible without a
    # paper frame; it keeps the exact photograph extracted from this PDF.
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    brush = ImageDraw.Draw(overlay)
    start = round(image.height * 0.53)
    for y in range(start, image.height):
        progress = (y - start) / max(1, image.height - start)
        brush.line((0, y, image.width, y), fill=(0, 0, 0, round(235 * progress ** 0.5)))
    image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    stream = io.BytesIO()
    canvas = Canvas(stream, pagesize=(PAPER_WIDTH, 841.91998), pageCompression=1)
    canvas.drawImage(ImageReader(image), 0, 0, width=PAPER_WIDTH, height=841.91998)
    canvas.setFillColor(HexColor("#d6ff00"))
    path = canvas.beginPath()
    path.moveTo(52, 778)
    path.lineTo(122, 778)
    path.lineTo(115, 770)
    path.lineTo(45, 770)
    path.close()
    canvas.drawPath(path, fill=1, stroke=0)
    if BASKERVILLE.is_file():
        if "MetsiBaskerville" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("MetsiBaskerville", str(BASKERVILLE), subfontIndex=0))
        font = "MetsiBaskerville"
    else:
        font = "Times-Roman"
    paragraph = " ".join(lines)
    size = 27.0
    lines = simpleSplit(paragraph, font, size, PAPER_WIDTH - 116)
    while size > 19 and len(lines) > 5:
        size -= 0.5
        lines = simpleSplit(paragraph, font, size, PAPER_WIDTH - 116)
    canvas.setFont(font, size)
    canvas.setFillColor(PAPER_TEXT)
    canvas.setStrokeColor(HexColor("#a4a4a1"))
    canvas.setLineWidth(0.55)
    top = 212 + max(0, len(lines) - 3) * 15
    canvas.line(60, top + 36, PAPER_WIDTH - 60, top + 36)
    for offset, line in enumerate(lines):
        canvas.drawString(60, top - offset * (size + 7), line)
    canvas.showPage()
    canvas.save()
    stream.seek(0)
    proof = PdfReader(stream).pages[0]
    proof.merge_page(footer_overlay(PAPER_WIDTH, 841.91998, folio))
    return proof


def prepare(number: int, output_dir: Path) -> dict:
    code = f"N{number:02d}"
    manifest = json.loads(MANIFEST.read_text())
    item = next(entry for entry in manifest["documents"] if entry["code"] == code)
    source_path = ROOT / item["public_pdf"]
    source = PdfReader(source_path)
    with pdfplumber.open(source_path) as document:
        pause_text = document.pages[4].extract_text() or ""
        card_rectangles = [rect for rect in document.pages[3].rects
                           if rect["width"] > 250 and rect["height"] > 50
                           and rect["x0"] > 20 and rect["top"] > 400
                           and rect["bottom"] < 760]
        if len(card_rectangles) > 1:
            raise ValueError(f"{code}: ambiguous opening panels")
        panel_bounds = None
        if card_rectangles:
            rect = card_rectangles[0]
            panel_bounds = (rect["x0"], rect["top"], rect["x1"], rect["bottom"])
    quote_lines = [line.strip() for line in pause_text.splitlines()
                   if line.strip() and not re.match(r"^05\s+Diego Carralbal", line)]
    if not 1 <= len(quote_lines) <= 5:
        raise ValueError(f"{code}: unexpected quote lines {quote_lines!r}")
    if len(source.pages) < 5:
        raise ValueError(f"{code}: fewer than five pages")
    writer = PdfWriter()
    for index, page in enumerate(source.pages):
        if index == 4:
            writer.add_page(photo_pause_with_bleed(page, quote_lines))
        else:
            writer.add_page(opening_page_with_bleed(page, index + 1, source_path, panel_bounds)
                            if index == 3 else page)
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{code}-preprensa-prueba.pdf"
    with output.open("wb") as handle:
        writer.write(handle)
    check = PdfReader(output)
    if len(check.pages) != len(source.pages):
        raise AssertionError(f"{code}: page count changed")
    for index in range(len(source.pages)):
        if index in (3, 4):
            continue
        if (check.pages[index].extract_text() or "") != (source.pages[index].extract_text() or ""):
            raise AssertionError(f"{code} page {index+1}: text changed")
    return {"document": code, "pages": len(source.pages), "proof": str(output)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("numbers", nargs="*", type=int)
    args = parser.parse_args()
    for number in args.numbers or range(1, 37):
        print(json.dumps(prepare(number, args.output_dir), ensure_ascii=False))
