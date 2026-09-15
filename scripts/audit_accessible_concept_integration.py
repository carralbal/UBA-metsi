#!/usr/bin/env python3
"""Verifica la integración de los puentes llanos desde fuente hasta PDF."""

from __future__ import annotations

import hashlib
import html
import importlib.util
import json
import re
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]


def load_bridge_module():
    path = ROOT / "scripts" / "apply_accessible_concept_bridges.py"
    spec = importlib.util.spec_from_file_location("bridges", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pdf_path(package: Path) -> Path:
    finals = sorted((package / "output").glob("*final.pdf"))
    if len(finals) != 1:
        raise RuntimeError(f"{package.name}: se esperaba un único PDF final")
    return finals[0]


def pdf_pages(path: Path) -> list[str]:
    with pdfplumber.open(path) as pdf:
        return [normalized(page.extract_text() or "").lower() for page in pdf.pages]


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def page_token_coverage(bridge: str, pages: list[str]) -> tuple[float, int]:
    # En diseños multicolumna el extractor intercala líneas de columnas. Por
    # eso verificamos que el vocabulario distintivo esté reunido en una misma
    # página, en lugar de exigir una cadena continua artificial.
    tokens = {
        token.lower()
        for token in re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{5,}", bridge)
    }
    if not tokens:
        return 0.0, 0
    coverages = [sum(token in page for token in tokens) / len(tokens) for page in pages]
    best = max(range(len(coverages)), key=coverages.__getitem__)
    return coverages[best], best + 1


def main() -> None:
    bridges = load_bridge_module()
    rows = []
    by_document: dict[int, list[tuple[str, str]]] = {}
    for (number, title), bridge in bridges.BRIDGES.items():
        by_document.setdefault(number, []).append((title, bridge))

    for number, concepts in sorted(by_document.items()):
        authority = bridges.authoritative_folder(number)
        package = bridges.package_folder(number)
        authority_source, authority_manifest = bridges.load_source(authority)
        package_source, package_manifest = bridges.load_source(package)
        html_text = (package / "index.html").read_text(encoding="utf-8")
        rendered_pages = pdf_pages(pdf_path(package))

        checks = {
            "authority_and_package_sources_identical": authority_source.read_bytes() == package_source.read_bytes(),
            "authority_hash_matches": authority_manifest.get("source_sha256") == digest(authority_source),
            "package_hash_matches": package_manifest.get("source_sha256") == digest(package_source),
        }
        concept_rows = []
        for title, bridge in concepts:
            source_id, manifest_text = bridges.paragraph_id(package_manifest, title)
            escaped = html.escape(bridge, quote=False)
            element_match = re.search(
                rf'<[^>]+data-source-id="{re.escape(source_id)}"[^>]*>(.*?)(?=</(?:p|li|h[1-6])>)',
                html_text,
                re.S,
            )
            pdf_coverage, pdf_page = page_token_coverage(bridge, rendered_pages)
            concept_checks = {
                "authority_once": authority_source.read_text(encoding="utf-8").count(bridge) == 1,
                "package_once": package_source.read_text(encoding="utf-8").count(bridge) == 1,
                "manifest_starts_with_bridge": bool(re.match(
                    r"^(?:En simple(?::|, con un ejemplo:) |Ejemplo cercano: )?" + re.escape(bridge),
                    manifest_text,
                )),
                "html_once": html_text.count(escaped) == 1,
                "html_bound_to_source_id": bool(element_match and escaped in element_match.group(1)),
                "pdf_token_coverage_at_least_90_percent": pdf_coverage >= 0.90,
            }
            concept_rows.append({
                "title": title,
                "source_id": source_id,
                "pdf_page": pdf_page,
                "pdf_token_coverage": round(pdf_coverage, 3),
                "status": "PASS" if all(concept_checks.values()) else "FAIL",
                "checks": concept_checks,
            })

        status = "PASS" if all(checks.values()) and all(row["status"] == "PASS" for row in concept_rows) else "FAIL"
        rows.append({
            "document": f"N{number:02d}",
            "package": package.name,
            "status": status,
            "checks": checks,
            "concepts": concept_rows,
        })

    report = {
        "status": "PASS" if all(row["status"] == "PASS" for row in rows) else "FAIL",
        "documents": len(rows),
        "concept_bridges": sum(len(row["concepts"]) for row in rows),
        "results": rows,
    }
    out = ROOT / "editorial-standard" / "accessible-concept-integration-audit-n00-n36.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "documents", "concept_bridges")}, ensure_ascii=False))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
