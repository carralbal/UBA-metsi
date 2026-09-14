#!/usr/bin/env python3
"""Remove production metadata from the 37 final METSI reading PDFs."""

from __future__ import annotations

import os
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject


ROOT = Path(__file__).resolve().parents[1]
PACKAGES = {
    0: ("N00-v3-final", "v3"),
    1: ("N01-v18-final", "v18"),
    2: ("N02-v15-final", "v15"),
    3: ("N03-v10-final", "v10"),
    4: ("N04-v9-final", "v9"),
    5: ("N05-v10-final", "v10"),
    6: ("N06-v10-final", "v10"),
    7: ("N07-v10-final", "v10"),
    8: ("N08-v10-final", "v10"),
    9: ("N09-v10-final", "v10"),
    10: ("N10-v9-final", "v9"),
    **{number: (f"N{number:02d}-v9-editorial", "v9") for number in range(11, 37)},
}


def sanitize(path: Path) -> tuple[int, int]:
    reader = PdfReader(str(path), strict=False)
    before_text = [page.extract_text() or "" for page in reader.pages]
    before_annots = [len(page.get("/Annots", [])) for page in reader.pages]
    before_pages = len(reader.pages)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    writer._info = None
    writer._ID = None
    writer.root_object.pop(NameObject("/Metadata"), None)
    temporary = path.with_suffix(".metadata-clean.pdf")
    with temporary.open("wb") as stream:
        writer.write(stream)
    check = PdfReader(str(temporary), strict=False)
    after_text = [page.extract_text() or "" for page in check.pages]
    after_annots = [len(page.get("/Annots", [])) for page in check.pages]
    if (
        len(check.pages) != before_pages
        or after_text != before_text
        or after_annots != before_annots
        or check.metadata
        or "/Metadata" in check.trailer["/Root"]
        or "/ID" in check.trailer
        or temporary.stat().st_size < 100_000
    ):
        temporary.unlink(missing_ok=True)
        raise RuntimeError(f"El saneamiento alteró el documento o dejó metadatos: {path}")
    os.replace(temporary, path)
    return before_pages, path.stat().st_size


def main() -> int:
    for number, (package, version) in PACKAGES.items():
        code = f"N{number:02d}"
        path = ROOT / package / "output" / f"{code}-METSI-lectura-previa-{version}-final.pdf"
        pages, size = sanitize(path)
        print(f"SANITIZED {code} {pages} pages {size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
