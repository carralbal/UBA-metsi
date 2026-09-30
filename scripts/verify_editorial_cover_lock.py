#!/usr/bin/env python3
"""Fail if any recovery candidate changes a pixel of its published cover."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from lock_editorial_recovery_covers import approved_pdf


def render_first_page(pdf: Path, prefix: Path) -> bytes:
    subprocess.run(
        [
            "pdftoppm", "-f", "1", "-l", "1", "-r", "96",
            "-singlefile", "-png", str(pdf), str(prefix),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    return prefix.with_suffix(".png").read_bytes()


def verify(stage: Path, number: int, temporary: Path) -> dict:
    code = f"N{number:02d}"
    approved = approved_pdf(number)
    candidate = stage / code / "candidate.pdf"
    lock = stage / code / "cover-lock.json"
    if not candidate.is_file() or not lock.is_file():
        raise FileNotFoundError(f"{code}: locked candidate or receipt missing")
    metadata = json.loads(lock.read_text())
    if metadata["approved_pdf_sha256"] != hashlib.sha256(approved.read_bytes()).hexdigest():
        raise ValueError(f"{code}: published PDF changed since the cover was locked")
    before = render_first_page(approved, temporary / f"{code}-approved")
    after = render_first_page(candidate, temporary / f"{code}-candidate")
    if before != after:
        raise ValueError(f"{code}: rendered cover differs from the published cover")
    return {"document": code, "rendered_cover_pixel_identical": True,
            "png_sha256": hashlib.sha256(before).hexdigest()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", type=Path)
    parser.add_argument("numbers", nargs="*", type=int)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="metsi-cover-verify-") as folder:
        result = [verify(args.stage, n, Path(folder))
                  for n in (args.numbers or range(1, 37))]
    report = args.stage / "approved-cover-verification.json"
    report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(f"Verified {len(result)} covers against their current published PDFs: {report}")
