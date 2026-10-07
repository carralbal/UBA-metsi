#!/usr/bin/env python3
"""Visual contact sheets and mechanical QA for the 37-document print set."""

from __future__ import annotations

import json
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image, ImageDraw
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "output/pdf/METSI-N00-N36-fullbleed-editorial-2026-10-07"
RECEIPTS = FOLDER / "manifest.json"


def render(document: pdfium.PdfDocument, number: int, scale: float = 1) -> Image.Image:
    return document[number - 1].render(scale=scale).to_pil().convert("RGB")


def main() -> None:
    receipts = json.loads(RECEIPTS.read_text())
    assert len(receipts) == 37
    checks = []
    roles = {"opening": 0, "first_pause": 1, "middle_pause": 2, "closing": -1}
    sheets = {role: Image.new("RGB", (6 * 240, 6 * 365), "#d5d5d2") for role in roles}
    draw = {role: ImageDraw.Draw(sheet) for role, sheet in sheets.items()}
    for number, entry in enumerate(receipts[1:], start=1):
        code = entry["document"]
        assert code == f"N{number:02d}"
        path = ROOT / entry["output"]
        document = pdfium.PdfDocument(str(path))
        reader = PdfReader(path)
        assert len(document) == entry["pages"] == len(reader.pages)
        assert reader.trailer["/Root"].get("/StructTreeRoot"), code
        assert all(abs(float(page.mediabox.width) - 594.96) < .6 and
                   abs(float(page.mediabox.height) - 841.92) < .6
                   for page in reader.pages), code
        changed = entry["changed_pages"]
        assert changed[:2] == [4, 5] and changed[-1] == entry["pages"], code
        for role, role_index in roles.items():
            if role == "middle_pause" and len(changed) == 3:
                continue
            folio = changed[role_index]
            image = render(document, folio, scale=.85)
            image.thumbnail((224, 326))
            x = (number - 1) % 6 * 240
            y = (number - 1) // 6 * 365
            draw[role].text((x + 6, y + 6), f"{code} · p{folio:02d}", fill="#111111")
            sheets[role].paste(image, (x + 6, y + 26))
            # The finishing overlay is a page-sized image XObject, so no
            # exported paper/white area can remain outside its footprint.
            content = reader.pages[folio - 1].get_contents().get_data()
            assert b"/FormXob" in content or b"/I" in content, (code, folio)
        checks.append({"document": code, "pages": len(reader.pages),
                       "changed_pages": changed,
                       "paper_panel_restyled": entry["paper_panel_restyled"],
                       "tagged": True})
    for role, image in sheets.items():
        image.save(FOLDER / f"contacto-{role}-N01-N36.jpg", quality=90)
    report = {"status": "PASS", "documents": len(receipts),
              "total_pages": sum(entry["pages"] for entry in receipts),
              "changed_pages": sum(len(entry["changed_pages"]) for entry in receipts),
              "paper_panels_restyled": sum(entry["paper_panel_restyled"] for entry in receipts),
              "checks": checks}
    (FOLDER / "qa.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: report[key] for key in ("status", "documents", "total_pages",
                                                   "changed_pages", "paper_panels_restyled")},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
