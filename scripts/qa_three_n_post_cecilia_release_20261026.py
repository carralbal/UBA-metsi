#!/usr/bin/env python3
"""Final machine gate for the three linked METSI readings; visual QA is separate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pypdfium2 as pdfium
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
ROWS = (
    ("N02", "site/pdf/N02-METSI-lectura-previa-v16-final.pdf", 34),
    ("N14", "site/pdf/publicados/N14-METSI-lectura-previa-v10-final.pdf", 50),
    ("N21", "site/pdf/publicados/N21-METSI-lectura-previa-v10-final.pdf", 40),
)


def sha256(path: Path) -> str:
    with path.open("rb") as handle:
        digest = hashlib.sha256()
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
        return digest.hexdigest()


def ink_opening(path: Path) -> dict:
    image = pdfium.PdfDocument(str(path))[3].render(scale=1).to_pil().convert("RGB")
    width, height = image.size
    points = [(0, height // 2), (width - 1, height // 2),
              (width // 2, height - 1), (width // 2, round(height * .83))]
    samples = [image.getpixel(point) for point in points]
    # The fourth sample can land on light typography; it only rejects paper.
    return {"samples": samples, "pass": all(max(rgb) < 85 for rgb in samples[:3])
            and max(samples[3]) < 160}


def inspect(code: str, relative: str, expected_pages: int) -> dict:
    path = ROOT / relative
    reader = PdfReader(path, strict=True)
    pages = reader.pages
    dimensions = [(round(float(page.mediabox.width), 2), round(float(page.mediabox.height), 2)) for page in pages]
    nonempty = []
    for index, page in enumerate(pages, 1):
        text = (page.extract_text() or "").strip()
        if text or list(page.images):
            nonempty.append(index)
    opening = ink_opening(path)
    result = {
        "code": code,
        "path": relative,
        "pages": len(pages),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "a4_pages": sum(1 for size in dimensions if abs(size[0] - 594.96) < .1 and abs(size[1] - 841.92) < .1),
        "nonempty_pages": len(nonempty),
        "tagged_document": bool(reader.trailer["/Root"].get("/StructTreeRoot")),
        "cover_structure": pages[0].get("/StructParents") is not None,
        "named_destinations": len(reader.named_destinations),
        "ink_opening": opening,
    }
    result["pass"] = (
        result["pages"] == expected_pages
        and result["a4_pages"] == expected_pages
        and result["nonempty_pages"] == expected_pages
        and result["tagged_document"]
        and result["cover_structure"]
        and opening["pass"]
    )
    return result


def main() -> None:
    receipts = [inspect(*row) for row in ROWS]
    n14_text = PdfReader(ROOT / ROWS[1][1], strict=True).pages[21].extract_text() or ""
    receipts[1]["five_routes_at_page_22"] = "Una constancia, cinco recorridos" in n14_text
    receipts[1]["pass"] = receipts[1]["pass"] and receipts[1]["five_routes_at_page_22"]
    catalog = {row["code"]: row for row in json.loads((ROOT / "site/course-manifest.json").read_text(encoding="utf-8"))["readings"]}
    homepage = (ROOT / "site/index.html").read_text(encoding="utf-8")
    site_links = {}
    for receipt in receipts:
        code = receipt["code"]
        row = catalog[code]
        url = row["pdf"]
        good = (row["pages"] == receipt["pages"] and url in homepage
                and url.split("?", 1)[0] == receipt["path"].removeprefix("site/"))
        site_links[code] = {"url": url, "pages": row["pages"], "pass": good}
    site_links["N14"]["bibliography_page_49"] = (
        "N14-METSI-lectura-previa-v10-final.pdf?v=n14-editorial-20261026#page=49" in homepage
        and "Bibliografía de N14, página 48" not in homepage)
    site_links["N14"]["pass"] &= site_links["N14"]["bibliography_page_49"]
    output = {"status": "PASS" if all(row["pass"] for row in receipts) else "FAIL",
              "scope": "N02, N14, N21 public PDF artifacts; visual page review recorded separately",
              "documents": receipts, "site_links": site_links}
    if not all(row["pass"] for row in site_links.values()):
        output["status"] = "FAIL"
    target = ROOT / "audits/N02-N14-N21-post-cecilia-release-20261026.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if output["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
