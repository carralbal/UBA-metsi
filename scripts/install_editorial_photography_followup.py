#!/usr/bin/env python3
"""Install the six visually audited photographic follow-ups, preserving covers."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

from lock_editorial_recovery_covers import ROOT, approved_pdf


EXPECTED = {1, 2, 31, 32, 33, 34}
REVISION = "editorial-fotografia-20261001"
EDITION = ROOT / "pedagogy/editorial-recovery-20260929"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main(stage: Path) -> None:
    covers = json.loads((stage / "approved-cover-verification.json").read_text())
    if len(covers) != 36 or not all(row["rendered_cover_pixel_identical"] for row in covers):
        raise ValueError("All 36 published covers must be pixel-identical")
    geometry = json.loads((stage / "geometry-audit.json").read_text())
    if any(row["out_of_bounds"] or row["overlap_candidates"] for rows in geometry.values() for row in rows):
        raise ValueError("Clipped or overlapping text found")

    rows = []
    source_blocks = 0
    for number in range(1, 37):
        code = f"N{number:02d}"
        folder = stage / code
        audit = json.loads((folder / "text-audit.json").read_text())
        if audit["missing_start"] or audit["missing_end"] or audit["changed_source_ids"]:
            raise ValueError(f"{code}: source text differs or is missing")
        source_blocks += audit["source_blocks"]
        lock = json.loads((folder / "cover-lock.json").read_text())
        approved = approved_pdf(number)
        candidate = folder / "candidate.pdf"
        old_hash, new_hash = digest(approved), digest(candidate)
        if old_hash != lock["approved_pdf_sha256"] or new_hash != lock["locked_candidate_sha256"]:
            raise ValueError(f"{code}: source or candidate changed after cover lock")
        if old_hash != new_hash:
            rows.append({
                "document": code,
                "path": str(approved.relative_to(ROOT)),
                "previous_sha256": old_hash,
                "new_sha256": new_hash,
                "pages": audit["pages"],
                "bytes": candidate.stat().st_size,
            })
    if {int(row["document"][1:]) for row in rows} != EXPECTED:
        raise ValueError(f"Unexpected changes: {[row['document'] for row in rows]}")

    manifest_path = ROOT / "course-manifest.json"
    public_path = ROOT / "site/course-manifest.json"
    html_path = ROOT / "site/index.html"
    manifest = json.loads(manifest_path.read_text())
    public = json.loads(public_path.read_text())
    html = html_path.read_text()
    by_code = {row["document"]: row for row in rows}
    for entry in manifest["documents"]:
        row = by_code.get(entry["code"])
        if row:
            entry.update({
                "pages": row["pages"], "bytes": row["bytes"],
                "sha256": row["new_sha256"], "tag": REVISION,
                "source_version": REVISION, "editorial_revision": REVISION,
                "qa_report": "pedagogy/editorial-recovery-20260929/followup-qa-20261001.json",
                "qa_status": "PASS",
            })
    if sum(entry["code"] in by_code for entry in manifest["documents"]) != 6:
        raise ValueError("Main manifest is incomplete")
    for reading in public["readings"]:
        row = by_code.get(reading["code"])
        if row:
            reading["pages"] = row["pages"]
            reading["pdf"] = re.sub(r"\?v=[^#]+", f"?v={REVISION}", reading["pdf"])
            reading["revision"] = REVISION
    if sum(reading["code"] in by_code for reading in public["readings"]) != 6:
        raise ValueError("Public manifest is incomplete")
    counts = {}
    for code in by_code:
        html, counts[code] = re.subn(
            rf"((?:pdf/(?:publicados/)?{code}-METSI-lectura-previa-[^\"?]+\.pdf)\?v=)[^\"#&]+",
            rf"\g<1>{REVISION}", html,
        )
    if any(count == 0 for count in counts.values()):
        raise ValueError(f"Public links missing for {[code for code, count in counts.items() if not count]}")

    rollback_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    for row in rows:
        source = stage / row["document"] / "candidate.pdf"
        destination = ROOT / row["path"]
        temporary = destination.with_name(destination.name + ".photography-followup.tmp")
        shutil.copyfile(source, temporary)
        if digest(temporary) != row["new_sha256"]:
            raise ValueError(f"{row['document']}: temporary copy failed")
        temporary.replace(destination)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    public_path.write_text(json.dumps(public, ensure_ascii=False, indent=2) + "\n")
    html_path.write_text(html)
    qa = {
        "revision": REVISION,
        "documents_reviewed": 36,
        "documents_changed": [row["document"] for row in rows],
        "documents_unchanged": 30,
        "source_blocks_compared": source_blocks,
        "covers_pixel_identical": 36,
        "source_blocks_changed": 0,
        "source_blocks_missing_from_pdf": 0,
        "out_of_bounds_text": 0,
        "text_overlap_candidates": 0,
        "rollback_commit": rollback_commit,
        "files": rows,
    }
    (EDITION / "followup-qa-20261001.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n")
    print(f"Installed {len(rows)} PDFs; 30 remained byte-identical. Rollback commit: {rollback_commit}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", type=Path)
    main(parser.parse_args().stage)
