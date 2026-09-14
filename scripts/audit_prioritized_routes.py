#!/usr/bin/env python3
"""Audit the N01–N36 prioritized-reading contract in packages and final PDFs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pypdf import PdfReader

from apply_prioritized_routes import CSS_MARKER, PACKAGE_ROOTS, ROOT


VERSIONS = {
    1: "v18",
    2: "v15",
    3: "v10",
    4: "v9",
    5: "v10",
    6: "v10",
    7: "v10",
    8: "v10",
    9: "v10",
    10: "v9",
    **{number: "v9" for number in range(11, 37)},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    records: list[dict[str, object]] = []
    for number, relative in PACKAGE_ROOTS.items():
        code = f"N{number:02d}"
        package = ROOT / relative
        version = VERSIONS[number]
        pdf = package / "output" / f"{code}-METSI-lectura-previa-{version}-final.pdf"
        html_text = (package / "index.html").read_text(encoding="utf-8")
        css_text = (package / "magazine.css").read_text(encoding="utf-8")
        metadata = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
        reader = PdfReader(str(pdf))
        contents_text = reader.pages[1].extract_text() or ""
        checks = {
            "html_route": "Ruta priorizada: 1 h 20 min a 1 h 40 min." in html_text,
            "html_core_labels": "contents-core" in html_text and "NÚCLEO" in html_text,
            "html_extension_labels": "contents-extension" in html_text and "EXT." in html_text,
            "css_volt_signal": CSS_MARKER in css_text and "#CFFF00" in css_text,
            "metadata_contract": metadata.get("prioritized_reading_route", {}).get("contract") == "metsi-prioritized-reading/v1",
            "pdf_route": "Ruta priorizada" in contents_text,
            "pdf_time": "1 h 20 min a 1 h 40 min" in contents_text,
            "pdf_core": "NÚCLEO" in contents_text and "Núcleo de lectura" in contents_text,
            "pdf_extension": "EXT." in contents_text and "extensiones" in contents_text.casefold(),
        }
        records.append({
            "document": code,
            "package": relative,
            "pdf": pdf.relative_to(ROOT).as_posix(),
            "pdf_pages": len(reader.pages),
            "pdf_sha256": sha256(pdf),
            "checks": checks,
            "status": "PASS" if all(checks.values()) else "FAIL",
        })
    report = {
        "schema": "metsi-prioritized-reading-audit/v1",
        "scope": "N01–N36",
        "status": "PASS" if all(record["status"] == "PASS" for record in records) else "FAIL",
        "documents": records,
    }
    output = ROOT / "editorial-standard" / "prioritized-reading-route-audit-n01-n36.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "documents": len(records),
        "failed": [record["document"] for record in records if record["status"] != "PASS"],
        "report": output.relative_to(ROOT).as_posix(),
    }, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
