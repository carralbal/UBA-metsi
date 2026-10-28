"""Correct the canonical N32/N33 Referentes page without private PDF copies.

The gray stripe is one paint operation. The over-zoomed Mario Bunge portrait
is replaced with the already-published N28 framing of the same source photo.
N33's smaller raster is resized to its existing XObject dimensions; its
circular alpha mask, text, links, tags, and the other pages remain untouched.
"""

from __future__ import annotations

import hashlib
import io
import os
from pathlib import Path
import sys
import zlib

from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream


BASELINES = {
    "N32": ("9ee583076e157ad9a7e9d4aeed1c9c49ab14011fefbc67807f417ceed6eddb93", 43, (366, 367), 14979),
    "N33": ("6aeeaaae976191b39a3b5b0266f88ec386906d0a32d25abb7a783bf1483e67f3", 40, (321, 319), 13872),
}
DONOR_SHA = "4bd945eb9ccf76ec8c1f7bbf47d725e1b24791df0547a32dc74b98f1df979b3e"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def annotations(page) -> list[str]:
    return [str({str(key): value for key, value in item.get_object().items() if key != "/P"})
            for item in page.get("/Annots", [])]


def main() -> None:
    if len(sys.argv) != 4 or sys.argv[1] not in BASELINES:
        raise SystemExit("Usage: normalize_n32_n33_referentes_20261028.py N32|N33 CANONICAL.pdf N28_DONOR.pdf")
    number, source, donor = sys.argv[1], Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()
    expected_sha, expected_pages, dimensions, encoded_size = BASELINES[number]
    if digest(source) != expected_sha or digest(donor) != DONOR_SHA:
        raise ValueError("Unexpected PDF baseline SHA")
    old = PdfReader(str(source))
    writer = PdfWriter(clone_from=str(source))
    if len(old.pages) != expected_pages:
        raise ValueError(f"Unexpected {number} page count")

    page = writer.pages[2]
    contents = ContentStream(page.get_contents(), writer)
    matches = [i for i, (args, op) in enumerate(contents.operations)
               if op == b"scn" and len(args) == 1 and str(args[0]).startswith("/P")]
    if len(matches) != 1:
        raise ValueError(f"Expected one gray background pattern: {matches}")
    index = matches[0]
    if [contents.operations[index + n][1] for n in range(1, 5)] != [b"gs", b"BDC", b"re", b"f"]:
        raise ValueError("Unexpected background paint sequence")
    if [float(x) for x in contents.operations[index + 3][0]] != [0.0, 2336.0, 794.0, 1123.0]:
        raise ValueError("Unexpected gray background rectangle")
    contents.operations[index + 4] = (contents.operations[index + 4][0], b"n")
    page.replace_contents(contents)

    donor_reader = PdfReader(str(donor))
    donor_image = donor_reader.pages[2]["/Resources"]["/XObject"]["/X55"].get_object()
    target_image = page["/Resources"]["/XObject"]["/X64"].get_object()
    for key in ("/Subtype", "/ColorSpace", "/BitsPerComponent", "/Filter"):
        if donor_image[key] != target_image[key]:
            raise ValueError(f"Incompatible portrait {key}")
    if (int(donor_image["/Width"]), int(donor_image["/Height"])) != (366, 367):
        raise ValueError("Unexpected donor portrait dimensions")
    if (int(target_image["/Width"]), int(target_image["/Height"])) != dimensions:
        raise ValueError("Unexpected target portrait dimensions")
    if len(target_image._data) != encoded_size or len(donor_image._data) != 60363:
        raise ValueError("Unexpected portrait encoded size")
    original_mask = bytes(target_image["/SMask"].get_object()._data)
    if number == "N32":
        replacement = bytes(donor_image._data)
    else:
        decoded = donor_image.get_data()
        if len(decoded) != 366 * 367 * 3:
            raise ValueError("Unexpected donor RGB pixel count")
        image = Image.frombytes("RGB", (366, 367), decoded)
        image = image.resize(dimensions, Image.Resampling.LANCZOS)
        replacement = zlib.compress(image.tobytes(), 9)
    target_image._data = replacement

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
        out_image = result.pages[2]["/Resources"]["/XObject"]["/X64"].get_object()
        if out_image._data != replacement or out_image["/SMask"].get_object()._data != original_mask:
            raise AssertionError("Portrait or circular mask did not survive")
        if len(out_image.get_data()) != dimensions[0] * dimensions[1] * 3:
            raise AssertionError("Incorrect resulting RGB pixel count")
        os.replace(transient, source)
    finally:
        transient.unlink(missing_ok=True)
    print(f"{number}: {expected_pages} pages, all text/links/geometry and tags preserved; SHA-256 {digest(source)}")


if __name__ == "__main__":
    main()
