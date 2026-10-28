#!/usr/bin/env python3
"""Restore the six approved N00 route pages into a privately regenerated base.

The 49-page base comes from the recovered editable HTML and original assembler.
Route artwork is copied from the 55-page published N00 strictly as a reference.
Neither input is modified and this script does not publish its output.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.constants import PageLabelStyle


def normalized(text: str | None) -> str:
    return re.sub(r"\s+", "", (text or "").replace("ﬁ", "fi").replace("ﬂ", "fl"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("base", type=Path)
    parser.add_argument("published", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--allow-changed-base-pages", default="",
                        help="Comma-separated one-based base pages intentionally edited in the candidate")
    args = parser.parse_args()
    if args.output.exists() or args.output.resolve() in {args.base.resolve(), args.published.resolve()}:
        raise ValueError("Output must be a new, separate private file")
    base = PdfReader(args.base)
    published = PdfReader(args.published)
    if len(base.pages) != 49 or len(published.pages) != 55:
        raise ValueError(f"Unexpected N00 pages: {len(base.pages)}, {len(published.pages)}")
    public_base = [page for index, page in enumerate(published.pages) if not 13 <= index <= 18]
    allowed = {int(value) for value in args.allow_changed_base_pages.split(",") if value.strip()}
    bad = [index + 1 for index, (a, b) in enumerate(zip(base.pages, public_base))
           if normalized(a.extract_text()) != normalized(b.extract_text())]
    if set(bad) != allowed:
        raise ValueError(f"Unexpected changed base pages {bad}; expected {sorted(allowed)}")
    writer = PdfWriter(clone_from=base)
    for index in range(6):
        writer.insert_page(published.pages[13 + index], index=13 + index)
    writer.set_page_label(0, 12, style=PageLabelStyle.DECIMAL, start=1)
    writer.set_page_label(13, 18, style=PageLabelStyle.UPPERCASE_LETTER, prefix="12", start=1)
    writer.set_page_label(19, 54, style=PageLabelStyle.DECIMAL, start=14)
    writer._info = None
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("wb") as stream:
        writer.write(stream)
    candidate = PdfReader(args.output)
    if len(candidate.pages) != 55:
        raise AssertionError("Route insertion lost a page")
    bad = [index + 1 for index in range(55) if normalized(candidate.pages[index].extract_text()) !=
           normalized(published.pages[index].extract_text())]
    expected = {page if page <= 13 else page + 6 for page in allowed}
    if set(bad) != expected:
        raise AssertionError(f"Unexpected changed pages after route insertion: {bad}; expected {sorted(expected)}")
    print(f"N00 private route inserted: 55 pages; deliberate changes {bad}; {args.output}")


if __name__ == "__main__":
    main()
