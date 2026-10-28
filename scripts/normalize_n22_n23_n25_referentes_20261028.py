"""Correct p.3 stripe and orphan edition comma in canonical N22/N23/N25.

Each PDF is SHA-guarded. The operation removes only the inherited gray
background paint and the single leading comma glyph of a separate edition
credit, retaining all other content, annotations and structure tags.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import sys

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream, TextStringObject


BASELINES = {
    "N22": ("52850ee5c0348a5893d7184c532355ee56b002426626dde4170cef24466b89ce", 38, 70.34375, 3129.0),
    "N23": ("0bcedcb116f53b1d0d105cb7702301728c9486e2374a0a90e9edd9b9b0160b69", 34, 311.0, 3158.0),
    "N25": ("19cd382b9ea34ef09878dbc0e4ccfa4502740e809e524b9015df360e8adeb241", 33, 541.54688, 3137.0),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def annotations(page) -> list[str]:
    return [str({str(key): value for key, value in item.get_object().items() if key != "/P"})
            for item in page.get("/Annots", [])]


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[1] not in BASELINES:
        raise SystemExit("Usage: normalize_n22_n23_n25_referentes_20261028.py N22|N23|N25 CANONICAL.pdf")
    number, source = sys.argv[1], Path(sys.argv[2]).resolve()
    baseline, expected_pages, comma_x, comma_y = BASELINES[number]
    if digest(source) != baseline:
        raise ValueError(f"Unexpected {number} input SHA")
    old = PdfReader(str(source))
    writer = PdfWriter(clone_from=str(source))
    if len(old.pages) != expected_pages:
        raise ValueError(f"Unexpected {number} page count")
    old_text = old.pages[2].extract_text()
    if old_text.count(", Second Edition") != 1:
        raise ValueError("Expected one orphan edition comma in p.3 text")

    page = writer.pages[2]
    contents = ContentStream(page.get_contents(), writer)
    paints = [i for i, (args, op) in enumerate(contents.operations)
              if op == b"scn" and len(args) == 1 and str(args[0]).startswith("/P")]
    if len(paints) != 1:
        raise ValueError(f"Expected one gray background paint: {paints}")
    index = paints[0]
    if [contents.operations[index + n][1] for n in range(1, 5)] != [b"gs", b"BDC", b"re", b"f"]:
        raise ValueError("Unexpected background paint sequence")
    if [float(x) for x in contents.operations[index + 3][0]] != [0.0, 2336.0, 794.0, 1123.0]:
        raise ValueError("Unexpected background rectangle")
    contents.operations[index + 4] = (contents.operations[index + 4][0], b"n")

    commas = [i for i, (args, op) in enumerate(contents.operations)
              if op == b"Tm" and len(args) == 6
              and abs(float(args[4]) - comma_x) < 0.001
              and abs(float(args[5]) - comma_y) < 0.001]
    if len(commas) != 1:
        raise ValueError(f"Expected one edition comma text matrix: {commas}")
    comma_i = commas[0] + 1
    args, op = contents.operations[comma_i]
    if op != b"Tj" or len(args) != 1 or str(args[0]) != "]":
        raise ValueError(f"Unexpected edition comma glyph: {op!r} {args!r}")
    contents.operations[comma_i] = ([TextStringObject("")], b"Tj")
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
            expected_text = old.pages[p].extract_text().replace(", Second Edition", "  Second Edition", 1) if p == 2 else old.pages[p].extract_text()
            if result.pages[p].extract_text() != expected_text:
                raise AssertionError(f"Unexpected text change on page {p + 1}")
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
    print(f"{number}: {expected_pages} pages, stripe/comma removed; other text/links/geometry/tags preserved; SHA-256 {digest(source)}")


if __name__ == "__main__":
    main()
