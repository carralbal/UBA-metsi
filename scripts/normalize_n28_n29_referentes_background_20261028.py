"""Normalize the Referentes paper on the published N28/N29 digital editions.

Only the nonsemantic gray middle-column background paint on physical page 3 is
disabled. This is a guarded, in-place repair of the single canonical PDF; no
persistent private candidate is created. The equivalent editable CSS override
is recorded alongside the QA receipt in pedagogy/source-overrides.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import sys

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream


BASELINES = {
    "N28": ("e5ce7ee145f935cb5cae8932beae49db25ac3cb8b96cafbb4cc0d9f8afb20006", 38),
    "N29": ("fb12efc5e00fe20a60656f57a517a65c65e8325d97cf2bfa10a22b0bba901a5c", 39),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def annotation_data(page) -> list[str]:
    return [str({str(key): value for key, value in item.get_object().items() if key != "/P"})
            for item in page.get("/Annots", [])]


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[1] not in BASELINES:
        raise SystemExit("Usage: normalize_n28_n29_referentes_background_20261028.py N28|N29 CANONICAL.pdf")
    number, source = sys.argv[1], Path(sys.argv[2]).resolve()
    expected_sha, expected_pages = BASELINES[number]
    if digest(source) != expected_sha:
        raise ValueError(f"Unexpected {number} input SHA: {digest(source)}")
    old = PdfReader(str(source))
    writer = PdfWriter(clone_from=str(source))
    if len(old.pages) != expected_pages or len(writer.pages) != expected_pages:
        raise ValueError(f"Unexpected {number} page count")
    page = writer.pages[2]
    contents = ContentStream(page.get_contents(), writer)
    matches = [i for i, (operands, op) in enumerate(contents.operations)
               if op == b"scn" and len(operands) == 1 and str(operands[0]).startswith("/P")]
    if len(matches) != 1:
        raise ValueError(f"Expected one background pattern, found {matches}")
    index = matches[0]
    if [contents.operations[index + n][1] for n in range(1, 5)] != [b"gs", b"BDC", b"re", b"f"]:
        raise ValueError("Unexpected background paint sequence")
    if [float(x) for x in contents.operations[index + 3][0]] != [0.0, 2336.0, 794.0, 1123.0]:
        raise ValueError("Unexpected background rectangle")
    contents.operations[index + 4] = (contents.operations[index + 4][0], b"n")
    page.replace_contents(contents)
    transient = source.with_name(f".{source.name}.normalizing")
    if transient.exists():
        raise FileExistsError(transient)
    try:
        writer.write(str(transient))
        result = PdfReader(str(transient))
        if len(result.pages) != expected_pages:
            raise AssertionError("Page count changed")
        for p in range(expected_pages):
            if old.pages[p].extract_text() != result.pages[p].extract_text():
                raise AssertionError(f"Text changed on page {p + 1}")
            if annotation_data(old.pages[p]) != annotation_data(result.pages[p]):
                raise AssertionError(f"Annotations changed on page {p + 1}")
            if old.pages[p].mediabox != result.pages[p].mediabox:
                raise AssertionError(f"Page geometry changed on page {p + 1}")
        os.replace(transient, source)
    finally:
        transient.unlink(missing_ok=True)
    print(f"{number}: {expected_pages}/{expected_pages} pages, text, annotations and geometry preserved; SHA-256 {digest(source)}")


if __name__ == "__main__":
    main()
