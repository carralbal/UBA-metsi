"""Replace only N11 p. 3 with its reflowed readable composition.

The recovered v76 source is exact for the current 47-page PDF except that the
published PDF has a nonsemantic p. 3 background neutralization. Keep every
other published page, annotation and structural parent untouched.
"""

from __future__ import annotations

from collections import Counter
import hashlib
from pathlib import Path
import sys

import pdfplumber
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream, NameObject


ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "site/pdf/publicados/N11-METSI-lectura-previa-v10-final.pdf"
EXPECTED_SHA = "ffee9ee8ce8594cf4ab3b231e814c441562106a6d15aab44da300ea45cef12df"


def mcids(page, pdf):
    stream = ContentStream(page.get_contents(), pdf)
    return [
        (str(args[0]), int(args[1]["/MCID"]))
        for args, op in stream.operations
        if op == b"BDC" and len(args) > 1 and hasattr(args[1], "get")
        and args[1].get("/MCID") is not None
    ]


def text_characters(path: Path) -> Counter:
    with pdfplumber.open(path) as pdf:
        return Counter(c["text"] for c in pdf.pages[2].chars
                       if not c["text"].isspace())


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: replace_n11_referents_page_20261028.py CANDIDATE.pdf TEMP_FINAL.pdf")
    candidate = Path(sys.argv[1]).resolve()
    destination = Path(sys.argv[2]).resolve()
    if destination.exists() or destination == CURRENT or destination == candidate:
        raise FileExistsError(destination)
    if hashlib.sha256(CURRENT.read_bytes()).hexdigest() != EXPECTED_SHA:
        raise ValueError("Current N11 PDF changed; refuse unreviewed substitution")
    if text_characters(CURRENT) != text_characters(candidate):
        raise ValueError("Referents page changed non-whitespace content")

    original = PdfReader(CURRENT)
    revised = PdfReader(candidate)
    if len(original.pages) != len(revised.pages) or len(original.pages) != 47:
        raise ValueError("Expected two 47-page PDFs")
    if mcids(original.pages[2], original) != mcids(revised.pages[2], revised):
        raise ValueError("Referents marked-content ordering changed")

    writer = PdfWriter(clone_from=str(CURRENT))
    writer.add_page(revised.pages[2])
    target = writer.pages[2]
    imported = writer.pages[-1]
    target.replace_contents(ContentStream(imported.get_contents(), writer))
    target[NameObject("/Resources")] = imported.raw_get("/Resources")
    writer.remove_page(len(writer.pages) - 1)
    writer.write(str(destination))
    print(destination)


if __name__ == "__main__":
    main()
