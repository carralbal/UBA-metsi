"""Measure dominant reading-size text in the 37 published digital PDFs.

This is a typography triage, not a visual-readability or accessibility verdict.
It excludes cover, contents, references and very sparse pages by selecting
interior pages with substantial text in the central reading area.
"""

from __future__ import annotations

from collections import Counter
import json
import os
from pathlib import Path

import pdfplumber


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get("METSI_TYPE_REPORT", str(ROOT / "AUDITORIA-TIPO-LECTURA-37-N-20261028.json")))


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    rows = json.loads((ROOT / "site/course-manifest.json").read_text(encoding="utf-8"))["readings"]
    items = []
    for row in rows:
        path = ROOT / "site" / row["pdf"].split("?", 1)[0]
        page_results = []
        with pdfplumber.open(path) as pdf:
            for folio, page in enumerate(pdf.pages, 1):
                if folio < 4:
                    continue
                sizes = Counter(
                    round(float(ch["size"]) * 2) / 2
                    for ch in page.chars
                    if 72 < float(ch["top"]) < min(705, float(page.height) - 72)
                    and ch.get("text", "").strip()
                )
                if sum(sizes.values()) < 700:
                    continue
                dominant, count = sizes.most_common(1)[0]
                if count / sum(sizes.values()) < 0.48:
                    continue
                page_results.append({"page": folio, "size_pt_rounded_half": dominant,
                                     "dominant_chars": count, "all_chars": sum(sizes.values())})
        counts = Counter(p["size_pt_rounded_half"] for p in page_results)
        items.append({"code": row["code"], "pdf": row["pdf"].split("?", 1)[0],
                      "qualified_body_pages": len(page_results),
                      "dominant_sizes_by_page": dict(sorted(counts.items())),
                      "pages_with_dominant_below_10pt": [p for p in page_results if p["size_pt_rounded_half"] < 10],
                      "mode_body_size_pt": counts.most_common(1)[0][0] if counts else None})
    result = {"scope": "dominant font size on high-text interior pages; half-point rounding",
              "total": len(items), "items": items,
              "limitations": "Does not assess font quality, contrast, zoom, reading order, image text, or individual small captions."}
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"total": len(items),
                      "n02": next(i for i in items if i["code"] == "N02"),
                      "n21": next(i for i in items if i["code"] == "N21"),
                      "codes_with_small_dominant_pages": [i["code"] for i in items if i["pages_with_dominant_below_10pt"]]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
