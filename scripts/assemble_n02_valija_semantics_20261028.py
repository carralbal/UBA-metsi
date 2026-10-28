#!/usr/bin/env python3
"""Put the corrected, source-rendered N02 p. 6 into the tagged public baseline."""

from __future__ import annotations

import hashlib
import io
from pathlib import Path
import re
import sys

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, NameObject
from reportlab.lib.colors import HexColor
from reportlab.pdfgen.canvas import Canvas


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "site/pdf/N02-METSI-lectura-previa-v16-final.pdf"
BASELINE_SHA = "2bd5f7838c1f75ecf7d82d2974d42fe5f2257c1d06182a8eaf4c1f4332f3f880"
PAGE_INDEX = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mcids(page) -> list[bytes]:
    return re.findall(rb"/MCID\s+(\d+)", page.get_contents().get_data())


def ordinary_footer(width: float, height: float):
    buffer = io.BytesIO()
    canvas = Canvas(buffer, pagesize=(width, height), pageCompression=1)
    canvas.setFillColor(HexColor("#ffffff"))
    canvas.rect(0, 0, width, 43, fill=1, stroke=0)
    canvas.setStrokeColor(HexColor("#c9cac8"))
    canvas.setLineWidth(0.35)
    canvas.line(46, 43, width - 46, 43)
    canvas.setFillColor(HexColor("#686967"))
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(46, 21, "06")
    canvas.drawRightString(width - 46, 21, "Diego Carralbal, 2026  ·  linkedin.com/in/carralbal")
    canvas.showPage()
    canvas.save()
    buffer.seek(0)
    return PdfReader(buffer).pages[0]


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: assemble_n02_valija_semantics_20261028.py RENDERED.pdf OUTPUT.pdf")
    rendered = Path(sys.argv[1])
    output = Path(sys.argv[2])
    if sha256(BASELINE) != BASELINE_SHA:
        raise ValueError("N02 published baseline changed; re-audit before assembly")
    old = PdfReader(BASELINE)
    new = PdfReader(rendered)
    if len(old.pages) != 34 or len(new.pages) != 34:
        raise ValueError("N02 page count changed")
    before, after = old.pages[PAGE_INDEX], new.pages[PAGE_INDEX]
    if before.get("/StructParents") != after.get("/StructParents") or mcids(before) != mcids(after):
        raise ValueError("N02 p. 6 tag/MCID topology changed")
    if "dato correcto sobre algo" not in " ".join(before.extract_text().split()) or "estado falso" not in " ".join(after.extract_text().split()):
        raise ValueError("N02 textual precondition failed")

    writer = PdfWriter()
    writer.clone_document_from_reader(old)
    page = writer.pages[PAGE_INDEX]
    after.merge_page(ordinary_footer(float(after.mediabox.width), float(after.mediabox.height)))
    if mcids(before) != mcids(after):
        raise ValueError("N02 p. 6 MCIDs changed after footer")
    stream = DecodedStreamObject()
    stream.set_data(after.get_contents().get_data())
    page[NameObject("/Contents")] = writer._add_object(stream)
    page[NameObject("/Resources")] = after["/Resources"].get_object().clone(writer)
    with output.open("wb") as handle:
        writer.write(handle)

    check = PdfReader(output)
    if len(check.pages) != 34 or not check.trailer["/Root"].get("/StructTreeRoot"):
        raise ValueError("N02 structure/page count lost")
    text = " ".join(check.pages[PAGE_INDEX].extract_text().split())
    if "estado falso" not in text or "Un escaneo real" not in text or "dato correcto sobre algo" in text or "Diego Carralbal" not in text:
        raise ValueError("N02 correction did not survive PDF assembly")
    if check.pages[0].get_contents().get_data() != old.pages[0].get_contents().get_data():
        raise ValueError("N02 approved cover changed")
    for index, (prior, current) in enumerate(zip(old.pages, check.pages)):
        if index != PAGE_INDEX and prior.get_contents().get_data() != current.get_contents().get_data():
            raise ValueError(f"N02 unrelated page changed: {index + 1}")
    print(f"N02 assembled: 34 pages, only p. 6 drawing changed; SHA-256 {sha256(output)}")


if __name__ == "__main__":
    main()
