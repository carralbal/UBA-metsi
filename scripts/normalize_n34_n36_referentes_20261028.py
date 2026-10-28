"""Remove the inherited gray Referentes stripe in canonical N34–N36 PDFs.

SHA guards and structural checks prevent this page-level edit from silently
changing text, links, pagination, accessibility tags or other page streams.
No separate candidate PDF is retained after successful atomic replacement.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import sys

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream


BASELINES = {
    "N34": ("aed35d5fd6bd43d7f2ab3eff4a57b8cc379cf3d91dbc9aeb93006142b903dc66", 39),
    "N35": ("6a9d52f9c6b16c538e52896bc3381b6ce148e3f6120216b5fb413243a79c26d2", 40),
    "N36": ("31cb648d61dfb78a635b5d34947960629e05f28d662296b7b64a8b4eb2484a18", 41),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def annotations(page) -> list[str]:
    return [str({str(key): value for key, value in item.get_object().items() if key != "/P"})
            for item in page.get("/Annots", [])]


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[1] not in BASELINES:
        raise SystemExit("Usage: normalize_n34_n36_referentes_20261028.py N34|N35|N36 CANONICAL.pdf")
    number, source = sys.argv[1], Path(sys.argv[2]).resolve()
    baseline, expected_pages = BASELINES[number]
    if digest(source) != baseline:
        raise ValueError(f"Unexpected {number} input SHA")
    old = PdfReader(str(source))
    writer = PdfWriter(clone_from=str(source))
    if len(old.pages) != expected_pages:
        raise ValueError(f"Unexpected {number} page count")

    page = writer.pages[2]
    contents = ContentStream(page.get_contents(), writer)
    matches = [i for i, (args, op) in enumerate(contents.operations)
               if op == b"scn" and len(args) == 1 and str(args[0]).startswith("/P")]
    if len(matches) != 1:
        raise ValueError(f"Expected one stripe paint: {matches}")
    index = matches[0]
    if [contents.operations[index + n][1] for n in range(1, 5)] != [b"gs", b"BDC", b"re", b"f"]:
        raise ValueError("Unexpected background paint sequence")
    if [float(x) for x in contents.operations[index + 3][0]] != [0.0, 2336.0, 794.0, 1123.0]:
        raise ValueError("Unexpected stripe rectangle")
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
            if annotations(old.pages[p]) != annotations(result.pages[p]):
                raise AssertionError(f"Annotations changed on page {p + 1}")
            if old.pages[p].mediabox != result.pages[p].mediabox:
                raise AssertionError(f"Geometry changed on page {p + 1}")
            if p != 2 and old.pages[p].get_contents().get_data() != result.pages[p].get_contents().get_data():
                raise AssertionError(f"Content stream changed outside page 3: {p + 1}")
        if not result.trailer["/Root"].get("/StructTreeRoot"):
            raise AssertionError("Tagged structure lost")
        os.replace(transient, source)
    finally:
        transient.unlink(missing_ok=True)
    print(f"{number}: {expected_pages} pages, all text/links/geometry and tags preserved; SHA-256 {digest(source)}")


if __name__ == "__main__":
    main()
