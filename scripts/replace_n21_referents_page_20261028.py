"""Replace only N21 p. 3 with the reflowed, readable referents composition.

The public PDF has post-render editorial changes elsewhere, so a full rerender
would not be source-faithful. Import the reflowed p. 3 content and resources,
retain the published document's page tree/semantic parent and append its exact
vector running footer. The operation is guarded by SHA, MCID sequence and text.
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
CURRENT = ROOT / "site/pdf/publicados/N21-METSI-lectura-previa-v10-final.pdf"
EXPECTED_SHA = "fb21c41abcffb3e1fe4bb0a16b25f81ec8139141e73e61208e3b7c9a0ae68e45"


def semantic_mcid_sequence(page, pdf):
    stream = ContentStream(page.get_contents(), pdf)
    return [
        (str(args[0]), int(args[1]["/MCID"]))
        for args, op in stream.operations
        if op == b"BDC" and len(args) > 1 and hasattr(args[1], "get")
        and args[1].get("/MCID") is not None
    ]


def visible_letters(path: Path) -> Counter:
    with pdfplumber.open(path) as pdf:
        return Counter(c["text"] for c in pdf.pages[2].chars
                       if c["top"] < 800 and not c["text"].isspace())


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: replace_n21_referents_page_20261028.py CANDIDATE.pdf TEMP_FINAL.pdf")
    candidate = Path(sys.argv[1]).resolve()
    destination = Path(sys.argv[2]).resolve()
    if destination.exists() or destination == CURRENT or destination == candidate:
        raise FileExistsError(destination)
    if hashlib.sha256(CURRENT.read_bytes()).hexdigest() != EXPECTED_SHA:
        raise ValueError("Current N21 PDF changed; refuse unreviewed substitution")
    if visible_letters(CURRENT) != visible_letters(candidate):
        raise ValueError("Referents page changed non-whitespace content")

    old = PdfReader(CURRENT)
    new = PdfReader(candidate)
    if len(old.pages) != len(new.pages) or len(old.pages) != 40:
        raise ValueError("Expected two 40-page PDFs")
    old_tags = semantic_mcid_sequence(old.pages[2], old)
    new_tags = semantic_mcid_sequence(new.pages[2], new)
    if old_tags != new_tags[:len(old_tags)] or len(new_tags) != len(old_tags) + 1:
        raise ValueError("Referents marked-content ordering changed")
    if old.pages[2].get("/StructParents") != new.pages[2].get("/StructParents"):
        raise ValueError("Referents structural parent changed")

    writer = PdfWriter(clone_from=str(CURRENT))
    writer.add_page(new.pages[2])
    imported = writer.pages[-1]
    target = writer.pages[2]
    original_stream = ContentStream(target.get_contents(), writer)
    footer_start = len(original_stream.operations) - 27
    footer = original_stream.operations[footer_start:]
    if [op for _, op in footer[-15:]].count(b"Tj") != 2:
        raise ValueError("Could not isolate the original running footer")
    if footer[0][1] != b"q" or footer[-1][1] != b"Q":
        raise ValueError("Unexpected footer graphics-state envelope")

    imported_resources = imported["/Resources"]
    imported_fonts = imported_resources["/Font"]
    old_fonts = target["/Resources"]["/Font"]
    if NameObject("/F2+0") in imported_fonts:
        raise ValueError("Footer font key collides with candidate resources")
    imported_fonts[NameObject("/F2+0")] = old_fonts.raw_get("/F2+0")
    content = ContentStream(imported.get_contents(), writer)
    # Chromium's first instruction changes the page CTM without an envelope.
    # Restore the PDF-page coordinate system before replaying the original footer.
    content.operations = [([], b"q"), *content.operations, ([], b"Q"), *footer]
    target.replace_contents(content)
    target[NameObject("/Resources")] = imported.raw_get("/Resources")
    writer.remove_page(len(writer.pages) - 1)
    writer.write(str(destination))
    print(destination)


if __name__ == "__main__":
    main()
