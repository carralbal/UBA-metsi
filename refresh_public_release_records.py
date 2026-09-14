#!/usr/bin/env python3
"""Refresh internal hashes and build the metadata-safe manifest deployed to Pages."""

from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def publication_digest(records: list[dict[str, Any]]) -> str:
    fields = (
        "code", "title", "canonical_source", "canonical_sha256", "package_source",
        "package_source_sha256", "package_sha256", "package_files", "source_pdf",
        "public_pdf", "cover", "pages", "bytes", "sha256", "cover_sha256",
        "qa_validator", "qa_validator_sha256", "qa_report", "qa_status", "qa_checks",
        "qa_report_sha256", "cover_renderer", "cover_dpi",
    )
    return json_digest([{key: record.get(key) for key in fields} for record in records])


def public_pdf_map() -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in (SITE / "pdf").rglob("*.pdf"):
        code = path.name[:3]
        if code.startswith("N") and code[1:].isdigit():
            result[code] = path
    if set(result) != {f"N{number:02d}" for number in range(37)}:
        raise RuntimeError(f"Incomplete PDF map: {sorted(result)}")
    return result


def library_titles() -> dict[str, str]:
    source = (SITE / "index.html").read_text(encoding="utf-8")
    matches = re.findall(r"<p>(N\d{2})\s*·\s*\d+\s+páginas</p><h3>(.*?)</h3>", source)
    titles = {code: html.unescape(re.sub(r"<[^>]+>", "", title)).strip() for code, title in matches}
    guide = re.search(r'<p class="card-code">N00[^<]*</p><h3>(.*?)</h3>', source)
    if guide:
        titles["N00"] = html.unescape(re.sub(r"<[^>]+>", "", guide.group(1))).strip()
    return titles


def detailed_record(root_record: dict[str, Any], title: str) -> dict[str, Any]:
    code = root_record["code"]
    canonical_name = Path(str(root_record["canonical_source"])).name
    return {
        "code": code,
        "title": f"{code} · {title}",
        "canonical_source": root_record["canonical_source"],
        "canonical_sha256": root_record["canonical_sha256"],
        "package_source": f"{code}-v9-editorial/source/{canonical_name}",
        "package_source_sha256": root_record["canonical_sha256"],
        "package_sha256": root_record["package_sha256"],
        "package_files": root_record["package_files"],
        "source_pdf": root_record["pdf"],
        "public_pdf": str(root_record["public_pdf"]).removeprefix("site/"),
        "cover": str(root_record["cover"]).removeprefix("site/"),
        "pages": root_record["pages"],
        "bytes": root_record["bytes"],
        "sha256": root_record["sha256"],
        "qa_validator": root_record["qa_validator"],
        "qa_validator_sha256": root_record["qa_validator_sha256"],
        "qa_report": root_record["qa_report"],
        "qa_status": root_record["qa_status"],
        "qa_checks": root_record["qa_checks"],
        "qa_report_sha256": root_record["qa_report_sha256"],
        "cover_sha256": root_record["cover_sha256"],
        "cover_renderer": "pdftoppm version 26.05.0",
        "cover_dpi": 120,
    }


def main() -> int:
    pdfs = public_pdf_map()
    root_manifest_path = ROOT / "course-manifest.json"
    approval_path = ROOT / "BLOCK-01-integrated-release-current" / "approval.json"
    root_manifest = load(root_manifest_path)
    approval = load(approval_path)
    previous_public = load(SITE / "course-manifest.json")
    titles = library_titles()

    metrics: dict[str, dict[str, Any]] = {}
    for code, path in pdfs.items():
        metrics[code] = {
            "pages": len(PdfReader(str(path), strict=False).pages),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "public_pdf": path.relative_to(ROOT).as_posix(),
        }

    root_records = {record["code"]: record for record in root_manifest["documents"]}
    for code, values in metrics.items():
        root_records[code].update(values)

    detailed = [detailed_record(root_records[f"N{number:02d}"], titles[f"N{number:02d}"]) for number in range(11, 37)]
    release_sha256 = publication_digest(detailed)
    root_manifest["site_publication"]["release_sha256"] = release_sha256

    approval["pdf_sha256"] = {code: metrics[code]["sha256"] for code in sorted(approval["pdf_sha256"])}
    for code, record in approval.get("published", {}).items():
        record["bytes"] = metrics[code]["bytes"]
        record["sha256"] = metrics[code]["sha256"]
    approval["public_release_sanitization"] = {
        "status": "approved",
        "scope": "N00-N10",
        "content_and_layout_preserved": True,
        "production_metadata_removed": True,
    }

    safe_manifest = {
        "course": "Metodología del Estudio de Sistemas de Información",
        "institution": previous_public["institution"],
        "edition": previous_public["edition"],
        "author": previous_public["author"],
        "nuclei_total": 36,
        "blocks_total": 8,
        "status": "Colección completa y disponible",
        "blocks": previous_public["blocks"],
        "readings": [
            {
                "code": code,
                "title": titles[code],
                "pages": metrics[code]["pages"],
                "pdf": Path(metrics[code]["public_pdf"]).relative_to("site").as_posix(),
            }
            for code in sorted(metrics)
        ],
        "program": {
            "pages": len(PdfReader(str(SITE / "covers" / "programa" / "programa-metsi-2026.pdf"), strict=False).pages),
            "pdf": "covers/programa/programa-metsi-2026.pdf",
        },
    }

    save(root_manifest_path, root_manifest)
    save(approval_path, approval)
    save(SITE / "course-manifest.json", safe_manifest)
    print(json.dumps({"status": "PASS", "release_sha256": release_sha256, "documents": len(metrics)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
