"""Repair the canonical N30/N31 Referentes page without a private PDF copy.

N30: disable one inherited gray background paint.
N31: same, and replace only Mario Bunge's over-zoomed image pixels with the
properly framed image already published in N28. N28 and N31 used the exact
same original 200x200 portrait; N31's CSS scaled it 2.7x. The existing N31
circular alpha mask, accessibility marks, text and link annotations remain.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import sys

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream


BASELINES = {
    "N30": ("a838b7b1f85b77bde2127a9b1fd5d0d219d4f5d6fc8be2b1521564c3f5a0cc22", 39, 2246.0),
    "N31": ("f9a63e6b9f062ab568611de3cc5ba38589d1a524ef936acfe3f0b357f74dcb01", 39, 2336.0),
}
N28_DONOR_SHA = "4bd945eb9ccf76ec8c1f7bbf47d725e1b24791df0547a32dc74b98f1df979b3e"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def annotations(page) -> list[str]:
    return [str({str(key): value for key, value in item.get_object().items() if key != "/P"})
            for item in page.get("/Annots", [])]


def main() -> None:
    if len(sys.argv) not in (3, 4) or sys.argv[1] not in BASELINES:
        raise SystemExit("Usage: normalize_n30_n31_referentes_20261028.py N30 CANONICAL.pdf | N31 CANONICAL.pdf N28_DONOR.pdf")
    number, source = sys.argv[1], Path(sys.argv[2]).resolve()
    if (number == "N30" and len(sys.argv) != 3) or (number == "N31" and len(sys.argv) != 4):
        raise ValueError("Only N31 takes the N28 donor PDF")
    expected_sha, expected_pages, y = BASELINES[number]
    if digest(source) != expected_sha:
        raise ValueError(f"Unexpected {number} input SHA: {digest(source)}")
    old = PdfReader(str(source))
    writer = PdfWriter(clone_from=str(source))
    if len(old.pages) != expected_pages:
        raise ValueError(f"Unexpected {number} page count")

    page = writer.pages[2]
    contents = ContentStream(page.get_contents(), writer)
    matches = [i for i, (args, op) in enumerate(contents.operations)
               if op == b"scn" and len(args) == 1 and str(args[0]).startswith("/P")]
    if len(matches) != 1:
        raise ValueError(f"Expected one background pattern, found {matches}")
    index = matches[0]
    if [contents.operations[index + n][1] for n in range(1, 5)] != [b"gs", b"BDC", b"re", b"f"]:
        raise ValueError("Unexpected background paint sequence")
    if [float(x) for x in contents.operations[index + 3][0]] != [0.0, y, 794.0, 1123.0]:
        raise ValueError("Unexpected background rectangle")
    contents.operations[index + 4] = (contents.operations[index + 4][0], b"n")
    page.replace_contents(contents)

    original_mask = None
    donor_data = None
    if number == "N31":
        donor = Path(sys.argv[3]).resolve()
        if digest(donor) != N28_DONOR_SHA:
            raise ValueError("Unexpected N28 donor SHA")
        donor_reader = PdfReader(str(donor))
        donor_image = donor_reader.pages[2]["/Resources"]["/XObject"]["/X55"].get_object()
        target_image = page["/Resources"]["/XObject"]["/X59"].get_object()
        for key in ("/Subtype", "/Width", "/Height", "/ColorSpace", "/BitsPerComponent", "/Filter"):
            if donor_image[key] != target_image[key]:
                raise ValueError(f"Incompatible portrait {key}")
        if (int(target_image["/Width"]), int(target_image["/Height"])) != (366, 367):
            raise ValueError("Unexpected N31 portrait dimensions")
        if len(target_image._data) != 14979 or len(donor_image._data) != 60363:
            raise ValueError("Unexpected encoded portrait lengths")
        original_mask = bytes(target_image["/SMask"].get_object()._data)
        donor_data = bytes(donor_image._data)
        target_image._data = donor_data

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
                raise AssertionError(f"Page geometry changed on page {p + 1}")
            if p != 2 and old.pages[p].get_contents().get_data() != result.pages[p].get_contents().get_data():
                raise AssertionError(f"Content stream changed outside page 3: {p + 1}")
        if not result.trailer["/Root"].get("/StructTreeRoot"):
            raise AssertionError("Tagged structure lost")
        if number == "N31":
            image = result.pages[2]["/Resources"]["/XObject"]["/X59"].get_object()
            if image._data != donor_data or image["/SMask"].get_object()._data != original_mask:
                raise AssertionError("Portrait or original circular mask not preserved as intended")
        os.replace(transient, source)
    finally:
        transient.unlink(missing_ok=True)
    print(f"{number}: {expected_pages} pages, all text/links/geometry and tags preserved; SHA-256 {digest(source)}")


if __name__ == "__main__":
    main()
