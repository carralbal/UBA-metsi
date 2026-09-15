#!/usr/bin/env python3
"""Comprueba la capa llana explícita de cada concepto desde fuente hasta HTML/PDF."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
PLAIN_RE = re.compile(r"En simple(?:, con un ejemplo)?:\s*")
EXAMPLE_RE = re.compile(r"(?:Ejemplo cercano|En simple, con un ejemplo):\s*")


def load_module(filename: str, name: str):
    path = ROOT / "scripts" / filename
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_and_manifest(folder: Path) -> tuple[Path, dict]:
    manifest = json.loads((folder / "source-manifest.json").read_text(encoding="utf-8"))
    return folder / manifest["source"], manifest


def final_pdf(package: Path) -> Path:
    finals = sorted((package / "output").glob("*final.pdf"))
    if len(finals) != 1:
        raise RuntimeError(f"{package.name}: se esperaba un único PDF final")
    return finals[0]


def pdf_text(path: Path) -> str:
    with pdfplumber.open(path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    # A drop cap may be extracted as ``E\nn`` even though it renders as “En”.
    return re.sub(r"\bE\s+n simple", "En simple", text)


def counts(text: str) -> tuple[int, int]:
    return len(PLAIN_RE.findall(text)), len(EXAMPLE_RE.findall(text))


def main() -> None:
    apply = load_module("apply_explicit_accessible_layers_all_n.py", "explicit_layers")
    pedagogical = load_module("audit_pedagogical_accessibility_n00_n36.py", "pedagogical")
    rows = []
    for number in range(37):
        code = f"N{number:02d}"
        authority = pedagogical.source_for(code).parent.parent
        package = apply.package_for(number)
        authority_source, authority_manifest = source_and_manifest(authority)
        package_source, package_manifest = source_and_manifest(package)
        expected = len(apply.concept_sections(code))
        source_counts = counts(authority_source.read_text(encoding="utf-8"))
        package_counts = counts(package_source.read_text(encoding="utf-8"))
        html_counts = counts((package / "index.html").read_text(encoding="utf-8"))
        rendered_counts = counts(pdf_text(final_pdf(package)))
        checks = {
            "all_concepts_have_plain_label_in_authority": source_counts[0] == expected,
            "all_concepts_have_example_label_in_authority": source_counts[1] == expected,
            "all_concepts_have_plain_label_in_package": package_counts[0] == expected,
            "all_concepts_have_example_label_in_package": package_counts[1] == expected,
            "all_concepts_have_plain_label_in_html": html_counts[0] == expected,
            "all_concepts_have_example_label_in_html": html_counts[1] == expected,
            "all_concepts_have_plain_label_in_pdf": rendered_counts[0] == expected,
            "all_concepts_have_example_label_in_pdf": rendered_counts[1] == expected,
            "authority_hash_matches": authority_manifest.get("source_sha256") == digest(authority_source),
            "package_hash_matches": package_manifest.get("source_sha256") == digest(package_source),
        }
        rows.append({
            "document": code,
            "package": package.name,
            "concept_units": expected,
            "counts": {
                "authority": source_counts,
                "package": package_counts,
                "html": html_counts,
                "pdf": rendered_counts,
            },
            "checks": checks,
            "status": "PASS" if all(checks.values()) else "FAIL",
        })
    report = {
        "scope": "N00-N36",
        "documents": len(rows),
        "concept_units": sum(row["concept_units"] for row in rows),
        "status": "PASS" if all(row["status"] == "PASS" for row in rows) else "FAIL",
        "results": rows,
    }
    output = ROOT / "editorial-standard" / "explicit-accessible-layers-audit-n00-n36.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "documents", "concept_units")}, ensure_ascii=False))
    if report["status"] != "PASS":
        failed = [row["document"] for row in rows if row["status"] != "PASS"]
        print(json.dumps({"failed": failed}, ensure_ascii=False))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
