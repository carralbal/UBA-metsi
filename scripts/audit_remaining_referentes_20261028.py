"""Read-only p.3 inspection of remaining METSI background-stripe PDFs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

from pypdf import PdfReader
from pypdf.generic import ContentStream


ROOT = Path(__file__).resolve().parents[1]
TARGETS = {f"N{i:02d}" for i in (0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 18, 20)}


def main() -> None:
    manifest = json.loads((ROOT / "site/course-manifest.json").read_text())
    for item in manifest["readings"]:
        number = item["code"]
        if number not in TARGETS:
            continue
        path = ROOT / "site" / urlsplit(item["pdf"]).path
        reader = PdfReader(str(path))
        page = reader.pages[2]
        ops = ContentStream(page.get_contents(), reader).operations
        paints = [(i, [str(x) for x in args]) for i, (args, op) in enumerate(ops)
                  if op == b"scn" and len(args) == 1 and str(args[0]).startswith("/P")]
        rectangles = [([float(x) for x in args], i) for i, (args, op) in enumerate(ops)
                      if op == b"re" and len(args) == 4 and [float(x) for x in args] == [0.0, 2336.0, 794.0, 1123.0]]
        text = page.extract_text()
        edition_lines = [line for line in text.splitlines() if line.lstrip().startswith(", ")]
        print(json.dumps({"code": number, "path": str(path.relative_to(ROOT)),
                          "pages": len(reader.pages), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                          "p3_paint_count": len(paints), "p3_rect_count": len(rectangles),
                          "paint_index": paints[0][0] if len(paints) == 1 else None,
                          "rect_index": rectangles[0][1] if len(rectangles) == 1 else None,
                          "leading_comma_lines": edition_lines[:10], "tagged": bool(reader.trailer["/Root"].get("/StructTreeRoot"))},
                         ensure_ascii=False))


if __name__ == "__main__":
    main()
