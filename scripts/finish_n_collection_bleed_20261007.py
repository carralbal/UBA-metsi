#!/usr/bin/env python3
"""Finish the published N01–N36 full-bleed pages without changing their prose.

The approved PDF remains the semantic/searchable layer. Corrected 300-dpi
artwork is placed above only the opening, photographic pauses and closing.
The approved covers and every ordinary interior page remain untouched.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import re
from pathlib import Path

import pdfplumber
import pypdfium2 as pdfium
from PIL import Image
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf._page import PageObject
from pypdf.generic import RectangleObject
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

from prepare_prepress_bleed_proofs import (
    ROOT,
    opening_page_with_bleed,
    photo_pause_with_bleed,
    footer_overlay,
)


MANIFEST = ROOT / "course-manifest.json"
OUTPUT = ROOT / "output/pdf/METSI-N00-N36-fullbleed-editorial-2026-10-07"
PAGE_W = 594.96
PAGE_H = 841.92
ART_W = 572.5
ART_H = 809.7


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def light_footer() -> PageObject:
    stream = io.BytesIO()
    canvas = Canvas(stream, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    # The image continues behind this quiet footer; no exposed paper margin.
    canvas.setFillColor(HexColor("#f7f6f2"))
    canvas.rect(0, 0, PAGE_W, 43, fill=1, stroke=0)
    canvas.setStrokeColor(HexColor("#aaaaa7"))
    canvas.setLineWidth(.35)
    canvas.line(46, 43, PAGE_W - 46, 43)
    canvas.showPage()
    canvas.save()
    stream.seek(0)
    return PdfReader(stream).pages[0]


def footer_text(folio: int, *, dark: bool) -> PageObject:
    stream = io.BytesIO()
    canvas = Canvas(stream, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    canvas.setFillColor(HexColor("#f4f2ed" if dark else "#5d5d59"))
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(46, 21, f"{folio:02d}")
    canvas.drawRightString(PAGE_W - 46, 21,
                           "Diego Carralbal, 2026  ·  linkedin.com/in/carralbal")
    canvas.showPage()
    canvas.save()
    stream.seek(0)
    return PdfReader(stream).pages[0]


def scale_existing_art(source: PageObject, folio: int, *, closing: bool) -> PageObject:
    """Scale only the 572.5×809.7 artwork, never the blank export margin."""
    width, height = float(source.mediabox.width), float(source.mediabox.height)
    if abs(width - PAGE_W) > .5 or abs(height - PAGE_H) > .5:
        raise ValueError(f"Unexpected A4 media box: {width} × {height}")
    clipped = copy.copy(source)
    clipped.cropbox = RectangleObject([0, height - ART_H, ART_W, height])
    page = PageObject.create_blank_page(width=width, height=height)
    transform = Transformation().translate(0, -(height - ART_H)).scale(width / ART_W, height / ART_H)
    page.merge_transformed_page(clipped, transform, expand=False)
    if closing:
        page.merge_page(light_footer())
        page.merge_page(footer_text(folio, dark=False))
    else:
        page.merge_page(footer_overlay(width, height, folio))
    return page


def image_only_overlay(visual: PageObject, *, photo: bool) -> PageObject:
    """Rasterize only the changed visual layer, retaining source PDF tags below."""
    writer = PdfWriter()
    writer.add_page(visual)
    stream = io.BytesIO()
    writer.write(stream)
    stream.seek(0)
    document = pdfium.PdfDocument(stream.getvalue())
    image = document[0].render(scale=300 / 72).to_pil().convert("RGB")
    image_stream = io.BytesIO()
    if photo:
        image.save(image_stream, format="JPEG", quality=94, subsampling=0, optimize=True)
    else:
        image.save(image_stream, format="PNG", optimize=True)
    image_stream.seek(0)
    output = io.BytesIO()
    canvas = Canvas(output, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    canvas.drawImage(ImageReader(image_stream), 0, 0, width=PAGE_W, height=PAGE_H)
    canvas.showPage()
    canvas.save()
    output.seek(0)
    return PdfReader(output).pages[0]


def page_text(page: PageObject) -> str:
    text = page.extract_text() or ""
    text = re.sub(r"Diego Carralbal,?\s*2026\s*[·•]\s*linkedin\.com/in/carralbal", "", text)
    text = re.sub(r"(?m)^\s*\d{1,2}\s*$", "", text)
    return re.sub(r"\W", "", text.casefold())


def candidate_pages(path: Path) -> tuple[list[int], tuple[float, float, float, float] | None, list[str]]:
    with pdfplumber.open(path) as document:
        last = len(document.pages)
        photos = []
        for index, page in enumerate(document.pages, start=1):
            if index in (1, 5, last):
                continue
            if any(image["width"] >= .8 * page.width and image["height"] >= .8 * page.height
                   for image in page.images):
                photos.append(index)
        fourth = document.pages[3]
        panels = [rectangle for rectangle in fourth.rects
                  if rectangle["width"] > 250 and rectangle["height"] > 50
                  and rectangle["x0"] > 20 and rectangle["top"] > 400
                  and rectangle["bottom"] < 760]
        if len(panels) > 1:
            raise ValueError(f"Ambiguous ink-page paper panels in {path}")
        bounds = None
        if panels:
            panel = panels[0]
            bounds = (panel["x0"], panel["top"], panel["x1"], panel["bottom"])
        lines = [line.strip() for line in (document.pages[4].extract_text() or "").splitlines()
                 if line.strip() and not re.match(r"^05\s+Diego Carralbal", line)]
        lines = [line for line in lines if not re.fullmatch(r"05", line)
                 and not line.startswith("Diego Carralbal, 2026")]
        return photos, bounds, lines


def finish(row: dict, out_dir: Path) -> dict:
    code = row["code"]
    source_path = ROOT / row["public_pdf"]
    output_path = out_dir / f"{code}-METSI-fullbleed-editorial-A4.pdf"
    if code == "N00":
        # The current N00 has its own full-bleed export; preserve it bit-for-bit.
        import shutil
        shutil.copyfile(source_path, output_path)
        return {"document": code, "pages": len(PdfReader(source_path).pages),
                "source": str(source_path.relative_to(ROOT)),
                "output": str(output_path.relative_to(ROOT)), "sha256": sha256(output_path),
                "changed_pages": [], "paper_panel_restyled": False}

    original = PdfReader(source_path)
    mid_photos, panel_bounds, quote_lines = candidate_pages(source_path)
    if len(mid_photos) > 1:
        raise ValueError(f"{code}: unexpected additional full-page photos {mid_photos}")
    if not 1 <= len(quote_lines) <= 5:
        raise ValueError(f"{code}: pause quote extraction failed: {quote_lines!r}")

    writer = PdfWriter()
    writer.clone_document_from_reader(original)
    changes = [4, 5, *mid_photos, len(original.pages)]
    for folio in changes:
        source = original.pages[folio - 1]
        if folio == 4:
            visual = opening_page_with_bleed(source, folio, source_path, panel_bounds)
            photo = False
        elif folio == 5:
            visual = photo_pause_with_bleed(source, quote_lines, folio)
            photo = True
        else:
            visual = scale_existing_art(source, folio, closing=(folio == len(original.pages)))
            photo = True
        writer.pages[folio - 1].merge_page(image_only_overlay(visual, photo=photo))

    writer.add_metadata({"/Title": original.metadata.title or f"METSI · {code}",
                         "/Author": "Diego Carralbal",
                         "/Subject": "Corrección editorial de sangrado A4 y superficie ink"})
    with output_path.open("wb") as handle:
        writer.write(handle)
    result = PdfReader(output_path)
    if len(result.pages) != len(original.pages):
        raise ValueError(f"{code}: changed page count")
    if not result.trailer["/Root"].get("/StructTreeRoot"):
        raise ValueError(f"{code}: tagged structure was lost")
    if result.pages[0].get_contents().get_data() != original.pages[0].get_contents().get_data():
        raise ValueError(f"{code}: approved cover changed")
    for index, (before, after) in enumerate(zip(original.pages, result.pages), start=1):
        if page_text(before) != page_text(after):
            raise ValueError(f"{code}/p{index}: searchable academic text changed")
        if index not in changes and before.get_contents().get_data() != after.get_contents().get_data():
            raise ValueError(f"{code}/p{index}: unrelated page changed")
    return {"document": code, "pages": len(result.pages),
            "source": str(source_path.relative_to(ROOT)),
            "output": str(output_path.relative_to(ROOT)), "sha256": sha256(output_path),
            "changed_pages": sorted(changes), "paper_panel_restyled": bool(panel_bounds),
            "tagged_pdf_preserved": True}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("numbers", nargs="*", type=int)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    out_dir = args.output
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text())["documents"]
    selected = set(args.numbers) if args.numbers else set(range(37))
    receipts = []
    for row in manifest:
        number = int(row["code"][1:])
        if number not in selected:
            continue
        receipt = finish(row, out_dir)
        receipts.append(receipt)
        print(f"{row['code']}: {receipt['changed_pages']} corrected; tagged source preserved", flush=True)
    (out_dir / "manifest.json").write_text(json.dumps(receipts, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
