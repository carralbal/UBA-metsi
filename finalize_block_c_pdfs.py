#!/usr/bin/env python3
"""Add the canonical METSI folio/footer layer to Block C PDFs."""

from __future__ import annotations

import io
import argparse
from pathlib import Path

import pdfplumber
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent
LINKEDIN = "https://www.linkedin.com/in/carralbal"
PACKAGE_VERSION = 6
AVENIR = Path("/System/Library/Fonts/Avenir.ttc")


def register_fonts() -> None:
    """Keep the footer inside the approved METSI type system."""
    if "Avenir" not in pdfmetrics.getRegisteredFontNames():
        if not AVENIR.is_file():
            raise FileNotFoundError(f"Tipografía editorial no disponible: {AVENIR}")
        pdfmetrics.registerFont(TTFont("Avenir", str(AVENIR), subfontIndex=0))


def footer_page(width: float, height: float, number: int, total: int, white: bool) -> PdfReader:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(width, height), pageCompression=1)
    color = (0.96, 0.96, 0.93) if white else (0.23, 0.25, 0.23)
    c.setStrokeColorRGB(*color)
    c.setFillColorRGB(*color)
    c.setLineWidth(0.45)
    c.line(49, 30, width - 49, 30)
    c.setFont("Avenir", 6.4)
    folio = f"{number:02d}"
    credit = "Diego Carralbal, 2026  ·  linkedin.com/in/carralbal"
    c.drawString(49, 16, folio)
    credit_width = c.stringWidth(credit, "Avenir", 6.4)
    x = width - 49 - credit_width
    c.drawString(x, 16, credit)
    c.linkURL(LINKEDIN, (x, 12, width - 49, 24), relative=0, thickness=0)
    c.save()
    buffer.seek(0)
    return PdfReader(buffer)


def finalize(number: int) -> Path:
    register_fonts()
    package = ROOT / f"N{number:02d}-v{PACKAGE_VERSION}-editorial"
    source = package / "output" / f"N{number:02d}-METSI-lectura-previa-v{PACKAGE_VERSION}.pdf"
    target = package / "output" / f"N{number:02d}-METSI-lectura-previa-v{PACKAGE_VERSION}-final.pdf"
    reader = PdfReader(source)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    visual = pdfplumber.open(source)
    total = len(reader.pages)
    for index, page in enumerate(writer.pages):
        words = visual.pages[index].extract_words() or []
        images = visual.pages[index].images or []
        is_dark_or_photo = index in {0, 3} or (index != total - 1 and len(images) > 0 and len(words) < 60)
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        overlay = footer_page(width, height, index + 1, total, is_dark_or_photo).pages[0]
        page.merge_page(overlay, over=True)
    visual.close()
    metadata = dict(reader.metadata or {})
    metadata.update({
        "/Title": f"N{number:02d} · METSI · Lectura previa",
        "/Author": "Diego Carralbal",
        "/Subject": "Metodología de Sistemas de Información, FCE UBA",
        "/Keywords": "METSI, sistemas de información, FCE UBA, lectura previa",
        "/Creator": "METSI editorial system",
    })
    writer.add_metadata(metadata)
    writer._root_object.update({NameObject("/Lang"): TextStringObject("es-AR")})
    with target.open("wb") as handle:
        writer.write(handle)
    if not target.is_file() or target.stat().st_size < 100_000:
        raise RuntimeError(f"Finalización incompleta: {target}")
    print(f"FINALIZED N{number:02d} {total} pages {target.stat().st_size} bytes")
    return target


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=11)
    parser.add_argument("--end", type=int, default=16)
    args = parser.parse_args()
    if args.start < 11 or args.end > 36 or args.start > args.end:
        raise ValueError("El finalizador cubre N11–N36")
    for number in range(args.start, args.end + 1):
        finalize(number)


if __name__ == "__main__":
    main()
