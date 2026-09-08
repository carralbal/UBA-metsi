#!/usr/bin/env python3
"""Remove only objectively blank pagination artifacts from Block D raw PDFs."""

from pathlib import Path

import pdfplumber
from pypdf import PdfWriter

ROOT = Path(__file__).resolve().parent


for number in range(17, 21):
    path = ROOT / f"N{number:02d}-v1-editorial/output/N{number:02d}-METSI-lectura-previa-v1.pdf"
    with pdfplumber.open(path) as pdf:
        blanks = [i for i, page in enumerate(pdf.pages) if not (page.extract_text() or "").strip() and not page.images]
    if not blanks:
        print(f"N{number:02d}: no blank pages")
        continue
    writer = PdfWriter(clone_from=str(path))
    for index in reversed(blanks):
        del writer.pages[index]
    temporary = path.with_suffix(".pruned.pdf")
    with temporary.open("wb") as handle:
        writer.write(handle)
    temporary.replace(path)
    print(f"N{number:02d}: removed pages {', '.join(str(i + 1) for i in blanks)}")
