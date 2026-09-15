#!/usr/bin/env python3
"""Publish the audited regionalized N01-N36 PDFs into the stable site tree."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audits" / "regionalization-final-pdf-audit-n01-n36-2026-09-15.json"
SITE_MANIFEST = ROOT / "site" / "course-manifest.json"
ROOT_MANIFEST = ROOT / "course-manifest.json"
VERSIONS = {1: 19, 2: 16, 3: 11, 4: 10, 5: 11, 6: 11, 7: 11, 8: 11, 9: 11, 10: 10}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def public_relative(number: int) -> str:
    code = f"N{number:02d}"
    version = VERSIONS.get(number, 10)
    prefix = "pdf/" if number <= 10 else "pdf/publicados/"
    return f"{prefix}{code}-METSI-lectura-previa-v{version}-final.pdf"


def main() -> None:
    audit = json.loads(AUDIT.read_text())
    if audit["summary"]["passed"] != 36 or audit["summary"]["failed"]:
        raise RuntimeError("La auditoría regionalizada no está cerrada en 36/36")
    audit_rows = {row["document"]: row for row in audit["documents"]}
    source_manifest = json.loads(
        (ROOT / "academic-content-regionalization-manifest-n01-n36.json").read_text()
    )
    source_rows = {item["code"]: item for item in source_manifest["documents"]}
    site_manifest = json.loads(SITE_MANIFEST.read_text())
    root_manifest = json.loads(ROOT_MANIFEST.read_text())
    html_path = ROOT / "site" / "index.html"
    html = html_path.read_text()
    publication_rows = []
    current_public_targets = {ROOT / "site" / public_relative(number) for number in range(1, 37)}
    for number in range(1, 37):
        code = f"N{number:02d}"
        row = audit_rows[code]
        source = ROOT / row["pdf"]
        public = public_relative(number)
        target = ROOT / "site" / public
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if sha(target) != row["sha256"]:
            raise RuntimeError(f"{code}: SHA diferente después de copiar al sitio")
        html = re.sub(
            rf'pdf/(?:publicados/)?{code}-METSI-lectura-previa-v\d+-final\.pdf',
            public,
            html,
        )
        html = re.sub(rf'{code} · \d+ páginas', f'{code} · {row["pages"]} páginas', html)
        site_item = next(item for item in site_manifest["readings"] if item["code"] == code)
        site_item["pages"] = row["pages"]
        site_item["pdf"] = public
        root_item = next(item for item in root_manifest["documents"] if item["code"] == code)
        version = VERSIONS.get(number, 10)
        package = f"{code}-v{version}-final" if number <= 10 else f"{code}-v10-editorial"
        canonical_source = source_rows[code]["source"]
        canonical_path = ROOT / canonical_source
        for stale_key in ("package_sha256", "qa_report_sha256", "qa_validator_sha256"):
            root_item.pop(stale_key, None)
        root_item.update({
            "status": "closed",
            "pdf": row["pdf"],
            "public_pdf": f"site/{public}",
            "pages": row["pages"],
            "bytes": row["bytes"],
            "sha256": row["sha256"],
            "tag": f"{code.casefold()}-v{version}-regional-final",
            "source_version": "regional-v1",
            "canonical_source": canonical_source,
            "canonical_sha256": sha(canonical_path),
            "package_files": sum(path.is_file() for path in (ROOT / package).rglob("*")),
            "qa_report": AUDIT.relative_to(ROOT).as_posix(),
            "qa_status": "PASS",
            "qa_checks": len(row["checks"]),
            "qa_validator": "scripts/finalize_audit_regionalized_release.py",
        })
        publication_rows.append({
            "document": code,
            "package": package,
            "source": row["pdf"],
            "public": f"site/{public}",
            "pages": row["pages"],
            "sha256": row["sha256"],
            "regional_percentage": row["regional_percentage"],
        })
        print(f"SYNCED {code} -> {public}")
    for candidate in (ROOT / "site" / "pdf").glob("N??-METSI-lectura-previa-v*-final.pdf"):
        if candidate.name.startswith("N00-") or candidate in current_public_targets:
            continue
        candidate.unlink()
        print(f"RETIRED {candidate.relative_to(ROOT)}")
    for candidate in (ROOT / "site" / "pdf" / "publicados").glob("N??-METSI-lectura-previa-v*-final.pdf"):
        if candidate in current_public_targets:
            continue
        candidate.unlink()
        print(f"RETIRED {candidate.relative_to(ROOT)}")
    root_manifest["updated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    html_path.write_text(html)
    SITE_MANIFEST.write_text(json.dumps(site_manifest, ensure_ascii=False, indent=2) + "\n")
    ROOT_MANIFEST.write_text(json.dumps(root_manifest, ensure_ascii=False, indent=2) + "\n")
    report = {
        "date": "2026-09-15",
        "documents": 36,
        "status": "READY",
        "regional_percentage_min": audit["summary"]["min_regional_percentage"],
        "regional_percentage_max": audit["summary"]["max_regional_percentage"],
        "rows": publication_rows,
    }
    target_report = ROOT / "audits" / "regionalization-publication-manifest-n01-n36-2026-09-15.json"
    target_report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
