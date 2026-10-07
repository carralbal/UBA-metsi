#!/usr/bin/env python3
"""Confirm every print-book page is identical to its approved finishing PDF."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
COMPILED = ROOT / "output/pdf/METSI-N00-N36-impresion-A4-fullbleed-2026-10-07.pdf"


def stream(page) -> bytes:
    contents = page.get_contents()
    return contents.get_data() if contents else b""


def images(page) -> list[str]:
    return sorted(hashlib.sha256(item.data).hexdigest() for item in page.images)


def main() -> None:
    receipt = json.loads(COMPILED.with_suffix(".json").read_text())
    compiled = PdfReader(COMPILED)
    assert len(compiled.pages) == receipt["pages"] == 1470
    checked = blanks = 0
    for entry in receipt["documents"]:
        source = PdfReader(ROOT / entry["source"])
        assert len(source.pages) == entry["source_pages"]
        for offset, page in enumerate(source.pages):
            target = compiled.pages[entry["compiled_first_page"] - 1 + offset]
            assert stream(page) == stream(target), (entry["document"], offset + 1, "contents")
            assert tuple(page.mediabox) == tuple(target.mediabox), (entry["document"], offset + 1, "size")
            assert images(page) == images(target), (entry["document"], offset + 1, "image")
            checked += 1
        if entry["duplex_blank_after"]:
            blank = compiled.pages[entry["compiled_last_content_page"]]
            assert not stream(blank) and not blank.images and not (blank.extract_text() or "").strip()
            blanks += 1
        print(f"{entry['document']}: {len(source.pages)} exact pages", flush=True)
    assert (checked, blanks) == (1453, 17)
    report = {"status": "PASS", "exact_content_pages": checked, "duplex_blanks": blanks,
              "compiled_pages": len(compiled.pages), "documents": len(receipt["documents"])}
    COMPILED.with_name("METSI-N00-N36-verificacion-impresion-A4-fullbleed-2026-10-07.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
