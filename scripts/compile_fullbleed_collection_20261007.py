#!/usr/bin/env python3
"""Bind the verified N00–N36 A4 PDFs into one duplex-ready print file."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pypdf import PdfReader, PdfWriter


ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "output/pdf/METSI-N00-N36-fullbleed-editorial-2026-10-07"
OUTPUT = ROOT / "output/pdf/METSI-N00-N36-impresion-A4-fullbleed-2026-10-07.pdf"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    proof = json.loads((FOLDER / "qa.json").read_text())
    if proof["status"] != "PASS" or proof["documents"] != 37:
        raise ValueError("Individual full-bleed PDFs have not passed QA")
    receipts = json.loads((FOLDER / "manifest.json").read_text())
    writer = PdfWriter()
    entries = []
    next_page = 1
    for receipt in receipts:
        path = ROOT / receipt["output"]
        if digest(path) != receipt["sha256"]:
            raise ValueError(f"{receipt['document']}: PDF changed after QA")
        reader = PdfReader(path)
        if len(reader.pages) != receipt["pages"]:
            raise ValueError(f"{receipt['document']}: page count changed")
        start = next_page
        writer.add_outline_item(receipt["document"], start - 1)
        for page in reader.pages:
            writer.add_page(page)
        next_page += len(reader.pages)
        blank = bool(len(reader.pages) % 2)
        if blank:
            writer.add_blank_page(width=float(reader.pages[-1].mediabox.width),
                                  height=float(reader.pages[-1].mediabox.height))
            next_page += 1
        entries.append({"document": receipt["document"], "source": receipt["output"],
                        "source_sha256": receipt["sha256"], "source_pages": len(reader.pages),
                        "compiled_first_page": start,
                        "compiled_last_content_page": start + len(reader.pages) - 1,
                        "duplex_blank_after": blank})
        print(f"{receipt['document']}: p{start}–{start + len(reader.pages) - 1}"
              + (" + duplex blank" if blank else ""), flush=True)
    if next_page - 1 != 1470:
        raise AssertionError(f"Expected 1,470 pages, got {next_page - 1}")
    writer.add_metadata({"/Title": "METSI · N00–N36 · Impresión A4 con sangrado editorial",
                         "/Author": "Diego Carralbal",
                         "/Subject": "37 lecturas; 17 separadores en blanco para impresión a doble cara"})
    with OUTPUT.open("wb") as handle:
        writer.write(handle)
    if len(PdfReader(OUTPUT).pages) != 1470:
        raise AssertionError("Compiled PDF page count changed during serialization")
    report = {"status": "FULLBLEED_PRINT_FILE", "pages": 1470,
              "content_pages": 1453, "duplex_blanks": 17,
              "sha256": digest(OUTPUT), "documents": entries}
    OUTPUT.with_suffix(".json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()
