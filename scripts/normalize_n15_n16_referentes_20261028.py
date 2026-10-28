"""Remove p.3 stripe/orphan edition comma directly from canonical N15/N16.

Inputs are SHA-guarded; preserve every other page stream, page geometry,
links, text and the document's tagged structure. No retained PDF clone.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import sys

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream, TextStringObject


BASELINES = {
    "N15": ("a4977a3ea477a05640f45413d9ec06d27f8978c75fc6ecb3b19db6c4605bf1f5", 48, 314.53125, 3138.0),
    "N16": ("d3a1926e5bd2a838c1d7154c543061cf981addd9acf19be2aef04afbebb16020", 41, 545.07813, 2749.0),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def annotations(page) -> list[str]:
    return [str({str(k): v for k, v in item.get_object().items() if k != "/P"})
            for item in page.get("/Annots", [])]


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[1] not in BASELINES:
        raise SystemExit("Usage: normalize_n15_n16_referentes_20261028.py N15|N16 CANONICAL.pdf")
    number, source = sys.argv[1], Path(sys.argv[2]).resolve()
    baseline, expected_pages, comma_x, comma_y = BASELINES[number]
    if sha(source) != baseline:
        raise ValueError(f"Unexpected {number} input SHA")
    old = PdfReader(str(source))
    if len(old.pages) != expected_pages or old.pages[2].extract_text().count(", Revised Edition") != 1:
        raise ValueError("Unexpected page count or edition credit")
    writer = PdfWriter(clone_from=str(source))
    page = writer.pages[2]
    contents = ContentStream(page.get_contents(), writer)
    paints = [i for i, (args, op) in enumerate(contents.operations)
              if op == b"scn" and len(args) == 1 and str(args[0]).startswith("/P")]
    if len(paints) != 1:
        raise ValueError(f"Expected one background paint: {paints}")
    index = paints[0]
    if [contents.operations[index + n][1] for n in range(1, 5)] != [b"gs", b"BDC", b"re", b"f"]:
        raise ValueError("Unexpected paint sequence")
    if [float(x) for x in contents.operations[index + 3][0]] != [0.0, 2336.0, 794.0, 1123.0]:
        raise ValueError("Unexpected gray rectangle")
    contents.operations[index + 4] = (contents.operations[index + 4][0], b"n")
    commas = [i for i, (args, op) in enumerate(contents.operations)
              if op == b"Tm" and len(args) == 6
              and abs(float(args[4]) - comma_x) < 0.001
              and abs(float(args[5]) - comma_y) < 0.001]
    if len(commas) != 1:
        raise ValueError(f"Expected one comma text matrix: {commas}")
    comma_i = commas[0] + 1
    args, op = contents.operations[comma_i]
    if op != b"Tj" or len(args) != 1 or str(args[0]) != "]":
        raise ValueError(f"Unexpected comma glyph: {op!r} {args!r}")
    contents.operations[comma_i] = ([TextStringObject("")], b"Tj")
    page.replace_contents(contents)

    transient = source.with_name(f".{source.name}.normalizing")
    if transient.exists():
        raise FileExistsError(transient)
    try:
        writer.write(str(transient))
        result = PdfReader(str(transient))
        if len(result.pages) != expected_pages or not result.trailer["/Root"].get("/StructTreeRoot"):
            raise AssertionError("Document structure changed")
        for p in range(expected_pages):
            original = old.pages[p]
            revised = result.pages[p]
            expected_text = original.extract_text().replace(", Revised Edition", "  Revised Edition", 1) if p == 2 else original.extract_text()
            if revised.extract_text() != expected_text:
                raise AssertionError(f"Unexpected text change on page {p + 1}")
            if annotations(original) != annotations(revised) or original.mediabox != revised.mediabox:
                raise AssertionError(f"Links or geometry changed on page {p + 1}")
            if p != 2 and original.get_contents().get_data() != revised.get_contents().get_data():
                raise AssertionError(f"Other page stream changed: {p + 1}")
        os.replace(transient, source)
    finally:
        transient.unlink(missing_ok=True)
    print(f"{number}: {expected_pages} A4; stripe/comma removed; other text/links/geometry/tags preserved; SHA-256 {sha(source)}")


if __name__ == "__main__":
    main()
