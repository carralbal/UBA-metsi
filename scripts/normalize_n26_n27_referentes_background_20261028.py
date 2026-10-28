"""Remove the inherited middle-column stripe from the final N26/N27 PDFs.

The source PDFs are the exact, already-published digital editions documented in
pedagogy/N26 and pedagogy/N27. This deliberately changes only one nonsemantic
paint operation on physical page 3. The editable CSS equivalent is recorded in
pedagogy/source-overrides/referentes-paper-n26-n27.css.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream


BASELINES = {
    "N26": ("7afc9844649c6fb0c539492d74533ea1104de3519181ed02b570504ee54dd1b5", 37),
    "N27": ("57e6ec1d38753a0b2613322bbc3b9af6d27a931e7a89e53a09d91fab004893ea", 38),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def annotation_data(page) -> list[str]:
    # /P is the PDF-internal parent page reference, not annotation content.
    return [str({str(key): value for key, value in item.get_object().items() if key != "/P"})
            for item in page.get("/Annots", [])]


def main() -> None:
    if len(sys.argv) != 4 or sys.argv[1] not in BASELINES:
        raise SystemExit("Usage: normalize_n26_n27_referentes_background_20261028.py N26|N27 INPUT.pdf OUTPUT.pdf")
    number, source, output = sys.argv[1], Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()
    if output.exists() or source == output:
        raise FileExistsError(output)
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
    rectangle = contents.operations[index + 3][0]
    if [float(x) for x in rectangle] != [0.0, 2336.0, 794.0, 1123.0]:
        raise ValueError(f"Unexpected background rectangle: {rectangle}")
    # Keep the nonstructural marked-content span and its rectangle, but don't paint it.
    contents.operations[index + 4] = (contents.operations[index + 4][0], b"n")
    page.replace_contents(contents)
    writer.write(str(output))

    result = PdfReader(str(output))
    if len(result.pages) != expected_pages:
        raise AssertionError("Page count changed")
    for p in range(expected_pages):
        if old.pages[p].extract_text() != result.pages[p].extract_text():
            raise AssertionError(f"Text changed on page {p + 1}")
        if annotation_data(old.pages[p]) != annotation_data(result.pages[p]):
            raise AssertionError(f"Annotations changed on page {p + 1}")
        if old.pages[p].mediabox != result.pages[p].mediabox:
            raise AssertionError(f"Page geometry changed on page {p + 1}")
    print(f"{number}: {expected_pages}/{expected_pages} pages, text, annotations and geometry preserved; SHA-256 {digest(output)}")


if __name__ == "__main__":
    main()
