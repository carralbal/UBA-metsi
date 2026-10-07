#!/usr/bin/env python3
"""Install QA-passed N01–N36 PDFs locally, retaining an exact rollback copy."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVISION = "fullbleed-editorial-20261007"
FOLDER = ROOT / "output/pdf/METSI-N00-N36-fullbleed-editorial-2026-10-07"
BACKUP = ROOT / "output/pdf/METSI-N01-N36-rollback-before-fullbleed-2026-10-07"
ROOT_MANIFEST = ROOT / "course-manifest.json"
SITE_MANIFEST = ROOT / "site/course-manifest.json"
LINK_FILES = [ROOT / "site/index.html", ROOT / "site/covers/atlas-data.js"]
PDF_URL = re.compile(r"(pdf/(?:publicados/)?N(?!00)\d{2}-[^?\"'\s<>]+\.pdf)\?v=[^#\"'\s<>]+")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    receipts = json.loads((FOLDER / "manifest.json").read_text())
    qa = json.loads((FOLDER / "qa.json").read_text())
    assert len(receipts) == 37 and qa["status"] == "PASS" and qa["documents"] == 37
    manifest = json.loads(ROOT_MANIFEST.read_text())
    rows = {row["code"]: row for row in manifest["documents"]}
    assert set(rows) == {f"N{number:02d}" for number in range(37)}
    receipt_map = {entry["document"]: entry for entry in receipts}
    BACKUP.mkdir(parents=True, exist_ok=True)
    rollback = []
    for number in range(1, 37):
        code = f"N{number:02d}"
        row = rows[code]
        receipt = receipt_map[code]
        source = ROOT / receipt["output"]
        public = ROOT / row["public_pdf"]
        if not public.is_file() or digest(source) != receipt["sha256"]:
            raise ValueError(f"{code}: missing public PDF or changed finished proof")
        current_hash = digest(public)
        backup = BACKUP / public.name
        old_hash = digest(backup) if backup.exists() else current_hash
        if current_hash not in (old_hash, receipt["sha256"]):
            raise ValueError(f"{code}: existing rollback copy does not match published PDF")
        if not backup.exists():
            shutil.copy2(public, backup)
        rollback.append({"document": code, "path": str(public.relative_to(ROOT)),
                         "backup": str(backup.relative_to(ROOT)), "sha256": old_hash,
                         "bytes": backup.stat().st_size})
        if current_hash != receipt["sha256"]:
            shutil.copy2(source, public)
        row["bytes"] = public.stat().st_size
        row["sha256"] = receipt["sha256"]
        row["publication_revision"] = REVISION
        row["fullbleed_correction"] = {
            "revision": REVISION, "changed_pages": receipt["changed_pages"],
            "previous_sha256": old_hash,
            "paper_panel_restyled": receipt["paper_panel_restyled"],
            "approved_cover_and_prose_preserved": True,
            "proof_manifest": str((FOLDER / "manifest.json").relative_to(ROOT)),
            "rollback_copy": str(backup.relative_to(ROOT)),
        }
    manifest["updated_at"] = "2026-10-07"
    ROOT_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

    site_manifest = json.loads(SITE_MANIFEST.read_text())
    for row in site_manifest["readings"]:
        if row["code"] != "N00":
            row["pdf"] = PDF_URL.sub(lambda match: match.group(1) + "?v=" + REVISION, row["pdf"])
            row["revision"] = REVISION
    site_manifest["editorial_revision"] = REVISION
    SITE_MANIFEST.write_text(json.dumps(site_manifest, ensure_ascii=False, indent=2) + "\n")
    rewritten = {}
    for path in LINK_FILES:
        text = path.read_text()
        revised, count = PDF_URL.subn(lambda match: match.group(1) + "?v=" + REVISION, text)
        if count < 1:
            raise ValueError(f"No versioned N PDF links in {path}")
        path.write_text(revised)
        rewritten[str(path.relative_to(ROOT))] = count
    report = {"status": "LOCAL_INSTALL_READY_FOR_PUBLICATION", "revision": REVISION,
              "updated_pdfs": len(rollback), "rollback": rollback, "links_rewritten": rewritten}
    (BACKUP / "rollback-manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: report[key] for key in ("status", "updated_pdfs", "links_rewritten")},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
