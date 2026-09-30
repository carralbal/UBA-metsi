#!/usr/bin/env python3
"""Install only cover-locked METSI recovery PDFs into the public site tree."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from lock_editorial_recovery_covers import ROOT, approved_pdf


STAGE = Path("/private/tmp/metsi-editorial-recovery.LQBs9R")
RECEIPT = ROOT / "pedagogy/editorial-recovery-20260929/install-receipt.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    approved = json.loads((STAGE / "approved-cover-verification.json").read_text())
    if len(approved) != 36 or not all(row["rendered_cover_pixel_identical"] for row in approved):
        raise ValueError("The complete 36-cover comparison is missing or failed")
    copies: list[dict[str, str]] = []
    for number in range(1, 37):
        code = f"N{number:02d}"
        source = STAGE / code / "candidate.pdf"
        destination = approved_pdf(number)
        lock = json.loads((STAGE / code / "cover-lock.json").read_text())
        if digest(source) != lock["locked_candidate_sha256"]:
            raise ValueError(f"{code}: candidate changed since the cover lock")
        if digest(destination) != lock["approved_pdf_sha256"]:
            raise ValueError(f"{code}: published PDF changed since the backup")
        copies.append({"document": code, "path": str(destination.relative_to(ROOT)),
                       "previous_sha256": digest(destination), "new_sha256": digest(source)})

    for row in copies:
        number = int(row["document"][1:])
        source = STAGE / row["document"] / "candidate.pdf"
        destination = ROOT / row["path"]
        temporary = destination.with_name(destination.name + ".editorial-recovery.tmp")
        shutil.copyfile(source, temporary)
        if digest(temporary) != row["new_sha256"]:
            raise ValueError(f"N{number:02d}: copy verification failed")
        temporary.replace(destination)
    RECEIPT.write_text(json.dumps({"rollback_commit": "7551d2ce0b5c267cff185b8a2441b4975bcd3638",
                                   "rollback_tag": "pre-editorial-recovery-20260929",
                                   "files": copies}, ensure_ascii=False, indent=2) + "\n")
    print(f"Installed {len(copies)} cover-locked PDFs; receipt: {RECEIPT}")


if __name__ == "__main__":
    main()
