#!/usr/bin/env python3
"""Assemble a recovery preview with the exact, already-published cover page.

The staged HTML restores interior magazine layouts but contains obsolete cover
assets. Never expose its raw PDF as a reviewable candidate. This script uses
the current public PDF as the immutable cover source and retains every later
page from the new interior render. It does not write to the published PDFs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from pypdf import PdfReader, PdfWriter


ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def approved_pdf(number: int) -> Path:
    folder = ROOT / "site/pdf" / ("publicados" if number >= 11 else "")
    matches = list(folder.glob(f"N{number:02d}-METSI-lectura-previa-*.pdf"))
    if len(matches) != 1:
        raise ValueError(f"N{number:02d}: expected one published PDF, found {matches}")
    return matches[0]


def lock_one(stage: Path, number: int) -> dict:
    code = f"N{number:02d}"
    approved = approved_pdf(number)
    folder = stage / code
    interior = folder / "interior-stage.pdf"
    # Earlier pilot renders used this name. Accept them only for one-time
    # migration; after that, every render writes interior-stage.pdf.
    if not interior.is_file():
        legacy = folder / "candidate.pdf"
        if not legacy.is_file() or (folder / "cover-lock.json").exists():
            raise FileNotFoundError(interior)
        interior = legacy
    source_pdf = PdfReader(approved)
    stage_pdf = PdfReader(interior)
    if len(source_pdf.pages) < 2 or len(stage_pdf.pages) < 2:
        raise ValueError(f"{code}: source or stage has no interior")
    output = folder / "candidate.pdf"
    temporary = folder / "candidate.cover-locking.pdf"
    writer = PdfWriter()
    writer.add_page(source_pdf.pages[0])
    for page in stage_pdf.pages[1:]:
        writer.add_page(page)
    writer.add_metadata({
        "/Title": f"{code} · METSI · prueba de recuperación editorial",
        "/Subject": "Tapa publicada conservada sin cambios; interior en revisión",
    })
    with temporary.open("wb") as handle:
        writer.write(handle)
    check = PdfReader(temporary)
    if len(check.pages) != len(stage_pdf.pages):
        raise ValueError(f"{code}: page count changed during cover lock")
    if check.pages[0].get_contents().get_data() != source_pdf.pages[0].get_contents().get_data():
        raise ValueError(f"{code}: cover drawing instructions differ")
    if check.pages[0].extract_text() != source_pdf.pages[0].extract_text():
        raise ValueError(f"{code}: cover text differs")
    temporary.replace(output)
    record = {
        "document": code,
        "approved_cover_pdf": str(approved.relative_to(ROOT)),
        "approved_pdf_sha256": digest(approved),
        "interior_stage_pdf": str(interior),
        "locked_candidate_pdf": str(output),
        "locked_candidate_sha256": digest(output),
        "approved_cover_content_identical": True,
        "approved_cover_text_identical": True,
        "status": "cover_locked_interior_not_approved",
    }
    (folder / "cover-lock.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", type=Path)
    parser.add_argument("numbers", nargs="*", type=int)
    args = parser.parse_args()
    for n in args.numbers or range(1, 37):
        if not 1 <= n <= 36:
            parser.error(f"Invalid document N{n}")
        print(json.dumps(lock_one(args.stage, n), ensure_ascii=False))
