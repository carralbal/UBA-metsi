#!/usr/bin/env python3
"""Audit visible text collisions on every METSI ``Errores frecuentes`` page."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pdfplumber


ROOT = Path(__file__).resolve().parents[1]
EARLY_PACKAGES = {
    0: ("N00", None),
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
HISTORICAL_VISIBLE_FINDINGS = [
    "N17", "N20", "N21", "N22", "N23", "N29",
    "N31", "N32", "N33", "N34", "N35",
]
HISTORICAL_STRUCTURAL_FINDINGS = [
    "N15", *HISTORICAL_VISIBLE_FINDINGS, "N36",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_and_pdf(number: int) -> tuple[Path, Path]:
    code = f"N{number:02d}"
    if number <= 10:
        package_name, _version = EARLY_PACKAGES[number]
        package = ROOT / package_name
    else:
        package = ROOT / f"{code}-v9-editorial"
    candidates = sorted((package / "output").glob("*final.pdf"))
    if not candidates:
        raise RuntimeError(f"{code}: final PDF not found")
    return package, candidates[-1]


def microgap_count(page: pdfplumber.page.Page, left: float, right: float) -> int:
    tops = sorted({
        round(float(char["top"]), 2)
        for char in page.chars
        if left < float(char["x0"]) < right
        and 120 < float(char["top"]) < 780
        and str(char.get("text", "")).strip()
    })
    return sum(1 for first, second in zip(tops, tops[1:]) if .5 < second - first < 8)


def structural_check(package: Path) -> dict[str, object] | None:
    html_path = package / "index.html"
    if not html_path.is_file() or "-v9-editorial" not in package.name:
        return None
    html = html_path.read_text(encoding="utf-8")
    match = re.search(
        r'(<section\b(?=[^>]*class="[^"]*\bblock-c-errors\b[^"]*")[^>]*>.*?</section>)',
        html,
        re.S,
    )
    if not match:
        return {"passed": False, "reason": "errors section missing"}
    section = match.group(1)
    cards = section.count('class="error-card"')
    labels = len(re.findall(r'<h3\b', section)) + len(re.findall(
        r'<p\b[^>]*>\s*<strong\b', section, re.S
    ))
    declared = re.search(r'--error-rows:(\d+)', section)
    declared_rows = int(declared.group(1)) if declared else None
    expected_rows = (cards + 1) // 2 if cards else None
    return {
        "passed": cards > 0 and cards == labels and declared_rows == expected_rows,
        "cards": cards,
        "labels": labels,
        "declared_rows": declared_rows,
        "expected_rows": expected_rows,
    }


def main() -> None:
    documents = []
    for number in range(37):
        code = f"N{number:02d}"
        package, pdf_path = package_and_pdf(number)
        error_pages = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages, 1):
                if page_number <= 2 or "Errores frecuentes" not in (page.extract_text() or ""):
                    continue
                midpoint = float(page.width) / 2
                gaps = [
                    microgap_count(page, 35, midpoint - 4),
                    microgap_count(page, midpoint + 4, float(page.width) - 35),
                ]
                error_pages.append({
                    "page": page_number,
                    "column_microgap_counts": gaps,
                    "collision_signal": max(gaps) >= 6,
                })
        structure = structural_check(package)
        passed = not any(page["collision_signal"] for page in error_pages)
        if structure is not None:
            passed = passed and bool(structure["passed"])
        documents.append({
            "document": code,
            "pdf": str(pdf_path.relative_to(ROOT)),
            "pdf_sha256": sha256(pdf_path),
            "errors_pages": error_pages,
            "structure": structure,
            "status": "PASS" if passed else "FAIL",
        })

    report = {
        "audit": "METSI recurring errors-page text-overlap audit",
        "scope": "N00-N36",
        "status": "PASS" if all(item["status"] == "PASS" for item in documents) else "FAIL",
        "historical_visible_findings_before_repair": HISTORICAL_VISIBLE_FINDINGS,
        "historical_structural_findings_before_repair": HISTORICAL_STRUCTURAL_FINDINGS,
        "documents": documents,
    }
    target = ROOT / "editorial-standard" / "text-overlap-audit-n00-n36.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "documents": len(documents),
        "failed": [item["document"] for item in documents if item["status"] != "PASS"],
        "historical_visible": HISTORICAL_VISIBLE_FINDINGS,
        "historical_structural": HISTORICAL_STRUCTURAL_FINDINGS,
    }, ensure_ascii=False))
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
