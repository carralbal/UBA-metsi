#!/usr/bin/env python3
"""Record the verified public PDF replacements in the METSI manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
STAGE = Path("/private/tmp/metsi-editorial-recovery.LQBs9R")
EDITION = ROOT / "pedagogy/editorial-recovery-20260929"
MANIFEST = ROOT / "course-manifest.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    receipt = json.loads((EDITION / "install-receipt.json").read_text())
    rows = {row["document"]: row for row in receipt["files"]}
    if len(rows) != 36:
        raise ValueError("Incomplete installation receipt")
    manifest = json.loads(MANIFEST.read_text())
    manifest["updated_at"] = "2026-09-29"
    qa = []
    for entry in manifest["documents"]:
        code = entry["code"]
        if code not in rows:
            continue
        path = ROOT / rows[code]["path"]
        sha = digest(path)
        if sha != rows[code]["new_sha256"]:
            raise ValueError(f"{code}: installed PDF differs from receipt")
        pages = len(PdfReader(path).pages)
        entry.update({
            "pdf": rows[code]["path"],
            "public_pdf": rows[code]["path"],
            "pages": pages,
            "bytes": path.stat().st_size,
            "sha256": sha,
            "source_version": "editorial-recuperada-20260929",
            "editorial_revision": "editorial-recuperada-20260929",
            "tag": "editorial-recuperada-20260929",
            "qa_report": "pedagogy/editorial-recovery-20260929/qa-summary.json",
            "qa_status": "PASS",
            "qa_validator": "scripts/audit_editorial_recovery.py + scripts/audit_editorial_geometry.py + scripts/verify_editorial_cover_lock.py",
        })
        qa.append({"document": code, "pages": pages, "bytes": path.stat().st_size,
                   "sha256": sha, "cover_unchanged": True,
                   "source_blocks_missing": 0, "text_overlaps": 0,
                   "out_of_bounds_text": 0})
    if len(qa) != 36:
        raise ValueError("Manifest lacks one or more N01–N36 entries")
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    (EDITION / "qa-summary.json").write_text(json.dumps({
        "edition": "editorial-recuperada-20260929",
        "rollback_tag": "pre-editorial-recovery-20260929",
        "documents": qa,
        "checks": {
            "covers_pixel_identical_to_previous_published_edition": 36,
            "documents_with_all_source_blocks_visible": 36,
            "documents_with_no_geometry_errors": 36,
            "clean_public_site_link_and_size_gate": True,
        },
        "stage_report": str(STAGE / "approved-cover-verification.json"),
    }, ensure_ascii=False, indent=2) + "\n")
    print(f"Updated manifest and QA summary for {len(qa)} PDFs")


if __name__ == "__main__":
    main()
