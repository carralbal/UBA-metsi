"""Remove only the obsolete three-column background from N21's referents page.

This is a composition-layer correction over the already-published, tagged PDF.
It preserves the other 39 pages, source text, annotations and structure tree.
The corresponding editable CSS is in N21-v11-referentes-neutral/edition.css.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys

from pypdf import PdfWriter
from pypdf.generic import ContentStream


EXPECTED_SHA256 = "a32fb3327cc3081e7c0a655424390f63b715bb38a5ea78f8587f32d0f7d965ec"


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: normalize_n21_referentes_background_20261028.py INPUT.pdf OUTPUT.pdf")
    source = Path(sys.argv[1]).resolve()
    output = Path(sys.argv[2]).resolve()
    if output.exists() or source == output:
        raise FileExistsError(output)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError(f"Unexpected N21 input SHA: {digest}")

    writer = PdfWriter(clone_from=str(source))
    if len(writer.pages) != 40:
        raise ValueError(f"Expected 40 pages, found {len(writer.pages)}")
    page = writer.pages[2]
    contents = ContentStream(page.get_contents(), writer)
    pattern_uses = [index for index, (operands, operator) in enumerate(contents.operations)
                    if operator == b"scn" and len(operands) == 1 and str(operands[0]).startswith("/P")]
    if len(pattern_uses) != 1:
        raise ValueError(f"Expected one background pattern, found {pattern_uses}")
    pattern = pattern_uses[0]
    expected = [b"gs", b"BDC", b"re", b"f"]
    actual = [contents.operations[pattern + offset][1] for offset in range(1, 5)]
    if actual != expected:
        raise ValueError(f"Unexpected paint sequence: {actual}")
    rect = contents.operations[pattern + 3][0]
    if len(rect) != 4 or float(rect[2]) != 794 or float(rect[3]) != 1123:
        raise ValueError(f"Unexpected full-page background rectangle: {rect}")
    fill = pattern + 4
    contents.operations[fill] = (contents.operations[fill][0], b"n")
    page.replace_contents(contents)
    writer.write(str(output))
    print(f"Removed one nonsemantic background from PDF p. 3: {output}")


if __name__ == "__main__":
    main()
