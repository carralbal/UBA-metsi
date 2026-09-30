#!/usr/bin/env python3
"""Install only the three verified final-art PDF changes, never the full set."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from lock_editorial_recovery_covers import ROOT, approved_pdf


EXPECTED_CHANGED = {3, 4, 28}
RECEIPT = ROOT / "pedagogy/editorial-recovery-20260929/final-art-install-20260930.json"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main(stage: Path) -> None:
    cover_results = json.loads((stage / "approved-cover-verification.json").read_text())
    if len(cover_results) != 36 or not all(row["rendered_cover_pixel_identical"] for row in cover_results):
        raise ValueError("The pixel-level verification of all 36 approved covers is required")

    geometry = json.loads((stage / "geometry-audit.json").read_text())
    if any(row["out_of_bounds"] or row["overlap_candidates"] for rows in geometry.values() for row in rows):
        raise ValueError("Geometry audit reports clipping or overlapping text")

    changes: list[dict[str, str]] = []
    source_blocks_verified = 0
    for number in range(1, 37):
        code = f"N{number:02d}"
        folder = stage / code
        audit = json.loads((folder / "text-audit.json").read_text())
        if audit["missing_start"] or audit["missing_end"]:
            raise ValueError(f"{code}: missing source text")
        source_blocks_verified += audit["source_blocks"]
        source = folder / "candidate.pdf"
        destination = approved_pdf(number)
        lock = json.loads((folder / "cover-lock.json").read_text())
        old_hash, new_hash = digest(destination), digest(source)
        if old_hash != lock["approved_pdf_sha256"] or new_hash != lock["locked_candidate_sha256"]:
            raise ValueError(f"{code}: a PDF changed after approval")
        if old_hash != new_hash:
            changes.append({
                "document": code,
                "path": str(destination.relative_to(ROOT)),
                "previous_sha256": old_hash,
                "new_sha256": new_hash,
            })

    changed_numbers = {int(row["document"][1:]) for row in changes}
    if changed_numbers != EXPECTED_CHANGED:
        raise ValueError(f"Expected only N03, N04 and N28 to change; found {sorted(changed_numbers)}")

    rollback_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    temporary_files: list[tuple[Path, Path]] = []
    for row in changes:
        source = stage / row["document"] / "candidate.pdf"
        destination = ROOT / row["path"]
        temporary = destination.with_name(destination.name + ".final-art.tmp")
        shutil.copyfile(source, temporary)
        if digest(temporary) != row["new_sha256"]:
            raise ValueError(f"{row['document']}: temporary copy failed verification")
        temporary_files.append((temporary, destination))
    for temporary, destination in temporary_files:
        temporary.replace(destination)

    RECEIPT.write_text(json.dumps({
        "rollback_commit": rollback_commit,
        "covers_pixel_identical": 36,
        "source_blocks_verified": source_blocks_verified,
        "files": changes,
    }, ensure_ascii=False, indent=2) + "\n")
    print(f"Installed {len(changes)} verified PDFs; untouched: 33; receipt: {RECEIPT}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", type=Path)
    arguments = parser.parse_args()
    main(arguments.stage)
