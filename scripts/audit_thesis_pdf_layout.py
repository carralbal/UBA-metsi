#!/usr/bin/env python3
"""Verifica que la tesis completa de N01–N36 quede en una sola página A4 legible."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PACKAGES = {
    1: ("N01-v18-final", "v18"),
    2: ("N02-v15-final", "v15"),
    3: ("N03-v10-final", "v10"),
    4: ("N04-v9-final", "v9"),
    5: ("N05-v10-final", "v10"),
    6: ("N06-v10-final", "v10"),
    7: ("N07-v10-final", "v10"),
    8: ("N08-v10-final", "v10"),
    9: ("N09-v10-final", "v10"),
    10: ("N10-v9-final", "v9"),
}


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def package(number: int) -> tuple[Path, str]:
    if number <= 10:
        name, version = PACKAGES[number]
    else:
        name, version = f"N{number:02d}-v9-editorial", "v9"
    return ROOT / name, version


def source(number: int, package_root: Path) -> Path:
    manifest = json.loads((package_root / "source-manifest.json").read_text(encoding="utf-8"))
    return package_root / manifest["source"]


def thesis_paragraphs(text: str) -> list[str]:
    match = re.search(r"^## Tesis\s*\n(.*?)(?=^## )", text, re.M | re.S)
    if not match:
        raise RuntimeError("Tesis ausente")
    return [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", match.group(1)) if p.strip()]


def main() -> None:
    rows = []
    for number in range(1, 37):
        code = f"N{number:02d}"
        root, version = package(number)
        pdf = root / "output" / f"{code}-METSI-lectura-previa-{version}-final.pdf"
        paragraphs = thesis_paragraphs(source(number, root).read_text(encoding="utf-8"))
        reader = PdfReader(str(pdf))
        pages = [normalize(page.extract_text() or "") for page in reader.pages]

        first_tokens = normalize(paragraphs[0]).split()[:12]
        last_tokens = normalize(paragraphs[-1]).split()[-12:]
        first_probe = " ".join(first_tokens)
        last_probe = " ".join(last_tokens)
        first_pages = [i + 1 for i, text in enumerate(pages) if first_probe in text]
        last_pages = [i + 1 for i, text in enumerate(pages) if last_probe in text]
        shared = sorted(set(first_pages) & set(last_pages))

        sizes = {
            (round(float(page.mediabox.width), 2), round(float(page.mediabox.height), 2))
            for page in reader.pages
        }
        checks = {
            "pdf_exists": pdf.exists() and pdf.stat().st_size > 100_000,
            "all_pages_a4": sizes == {(594.96, 841.92)},
            "first_paragraph_present": len(first_pages) >= 1,
            "last_paragraph_present": len(last_pages) >= 1,
            "entire_thesis_on_one_page": len(shared) == 1,
            "substantive_source": sum(len(normalize(p).split()) for p in paragraphs) >= 280,
            "five_or_more_paragraphs": len(paragraphs) >= 5,
        }
        rows.append(
            {
                "document": code,
                "pdf": str(pdf.relative_to(ROOT)),
                "pages": len(reader.pages),
                "thesis_page": shared[0] if len(shared) == 1 else None,
                "first_probe_pages": first_pages,
                "last_probe_pages": last_pages,
                "source_paragraphs": len(paragraphs),
                "source_words": sum(len(normalize(p).split()) for p in paragraphs),
                "checks": checks,
                "status": "PASS" if all(checks.values()) else "FAIL",
            }
        )

    result = {
        "standard": "editorial-standard/THESIS-N00-STANDARD.md",
        "status": "PASS" if all(row["status"] == "PASS" for row in rows) else "FAIL",
        "documents": rows,
    }
    target = ROOT / "editorial-standard" / "thesis-n00-standard-pdf-audit-n01-n36.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": result["status"],
                "documents": len(rows),
                "failed": [row["document"] for row in rows if row["status"] == "FAIL"],
                "thesis_pages": {row["document"]: row["thesis_page"] for row in rows},
            },
            ensure_ascii=False,
        )
    )
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
