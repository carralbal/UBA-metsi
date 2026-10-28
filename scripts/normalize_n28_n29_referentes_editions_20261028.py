"""Remove the orphan leading comma before an edition on N28/N29 page 3.

The source HTML keeps a comma at the start of a separate <small> block. The
PDF draws that comma as its own glyph before the edition text. This guarded
change removes only that one glyph in the canonical published PDF. See the
source correction note in pedagogy/source-overrides.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import sys

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream, TextStringObject


BASELINES = {
    "N28": ("41d4ecffc53d0b6764e8c72a8552bde83e6482d5f05683e6884e745007558ef1", 38,
            530.21875, ", Fourth Edition", "  Fourth Edition"),
    "N29": ("32d8e31bc3ec3c9706162197ed6005c8b01295d12201eeb5f4f7e029357ea738", 39,
            541.54688, ", Second Edition", "  Second Edition"),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def annotation_data(page) -> list[str]:
    return [str({str(key): value for key, value in item.get_object().items() if key != "/P"})
            for item in page.get("/Annots", [])]


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[1] not in BASELINES:
        raise SystemExit("Usage: normalize_n28_n29_referentes_editions_20261028.py N28|N29 CANONICAL.pdf")
    number, source = sys.argv[1], Path(sys.argv[2]).resolve()
    expected_sha, expected_pages, expected_x, before, after = BASELINES[number]
    if digest(source) != expected_sha:
        raise ValueError(f"Unexpected {number} input SHA: {digest(source)}")
    old = PdfReader(str(source))
    writer = PdfWriter(clone_from=str(source))
    if len(old.pages) != expected_pages:
        raise ValueError(f"Unexpected {number} page count")
    old_text = old.pages[2].extract_text()
    if old_text.count(before) != 1:
        raise ValueError(f"Expected exactly one {before!r} in page text")
    page = writer.pages[2]
    contents = ContentStream(page.get_contents(), writer)
    matches = [i for i, (args, op) in enumerate(contents.operations)
               if op == b"Tm" and len(args) == 6 and float(args[4]) == expected_x
               and float(args[5]) == 2749.0]
    if len(matches) != 1:
        raise ValueError(f"Expected one edition text matrix, found {matches}")
    index = matches[0] + 1
    operands, op = contents.operations[index]
    if op != b"Tj" or len(operands) != 1 or str(operands[0]) != "]":
        raise ValueError(f"Unexpected leading glyph: {op!r}, {operands!r}")
    contents.operations[index] = ([TextStringObject("")], b"Tj")
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
            expected_text = old.pages[p].extract_text().replace(before, after, 1) if p == 2 else old.pages[p].extract_text()
            actual_text = result.pages[p].extract_text()
            if actual_text != expected_text:
                import difflib
                delta = "".join(difflib.unified_diff(expected_text.splitlines(True), actual_text.splitlines(True), n=1))
                raise AssertionError(f"Unexpected text change on page {p + 1}: {delta[:800]}")
            if annotation_data(old.pages[p]) != annotation_data(result.pages[p]):
                raise AssertionError(f"Annotations changed on page {p + 1}")
            if old.pages[p].mediabox != result.pages[p].mediabox:
                raise AssertionError(f"Page geometry changed on page {p + 1}")
        os.replace(transient, source)
    finally:
        transient.unlink(missing_ok=True)
    print(f"{number}: edition punctuation corrected; {expected_pages} pages and annotations preserved; SHA-256 {digest(source)}")


if __name__ == "__main__":
    main()
