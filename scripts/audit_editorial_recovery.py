#!/usr/bin/env python3
"""Check PDF extraction against every staged source block, before visual QA."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

from lxml import html
from pypdf import PdfReader


def words(text: str) -> list[str]:
    text = text.lower().replace("ﬁ", "fi").replace("ﬂ", "fl")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.findall(r"[a-z0-9]+", text)


def audit(number: int, stage: Path) -> dict:
    folder = stage / f"N{number:02d}"
    source = html.parse(str(folder / "index.html"))
    pdf = PdfReader(str(folder / "candidate.pdf"))
    extracted = " ".join(words(" ".join(page.extract_text() for page in pdf.pages)))
    compact = extracted.replace(" ", "")
    missing_start, missing_end = [], []
    blocks = source.xpath("//*[@data-source-id]")
    for block in blocks:
        tokens = words(block.text_content())
        if len(tokens) < 7:
            continue
        first = " ".join(tokens[:7])
        last = " ".join(tokens[-7:])
        # A designed drop cap is extracted as its own glyph, sometimes ahead
        # of the section heading (for example D + "iscovery" in N06).
        detached_dropcap = (
            len(tokens[0]) > 3
            and (" ".join([tokens[0][1:]] + tokens[1:7])) in extracted
            and tokens[0][0] in extracted.split()
        )
        if first not in extracted and first.replace(" ", "") not in compact and not detached_dropcap:
            missing_start.append(block.get("data-source-id"))
        if last not in extracted and last.replace(" ", "") not in compact:
            missing_end.append(block.get("data-source-id"))
    result = {
        "number": number,
        "pages": len(pdf.pages),
        "source_blocks": len(blocks),
        "image_pages": sum(bool(page.images) for page in pdf.pages),
        "images": sum(len(page.images) for page in pdf.pages),
        "missing_start": missing_start,
        "missing_end": missing_end,
    }
    (folder / "text-audit.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", type=Path)
    parser.add_argument("numbers", nargs="*", type=int)
    options = parser.parse_args()
    for number in options.numbers or range(1, 37):
        result = audit(number, options.stage)
        print(
            f"N{number:02d} {result['pages']:2} pp; "
            f"{result['source_blocks']:3} blocks; "
            f"missing start/end {len(result['missing_start'])}/"
            f"{len(result['missing_end'])}"
        )
