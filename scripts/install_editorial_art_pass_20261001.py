#!/usr/bin/env python3
"""Install the visually audited editorial interiors, preserving public covers.

All 36 candidates are checked. Only byte-different PDFs are replaced. The
previous Git commit is the recoverable backup; never install from a stale
stage or quietly touch unrelated site assets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import unicodedata
from pathlib import Path

from pypdf import PdfReader

from lock_editorial_recovery_covers import ROOT, approved_pdf


REVISION = "editorial-arte-20261001"
EXPECTED_CHANGED = {1, 3, 4, 6, 8, 10, 16, 17, 18, 23, 27, 30, 32}
RECEIPT = ROOT / "pedagogy/editorial-recovery-20260929/art-pass-20261001.json"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def normalized(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in value if not unicodedata.combining(c)).lower())


def heading_page(pdf: Path, heading: str) -> int:
    key = normalized(heading)
    matches = [index for index, page in enumerate(PdfReader(pdf).pages, start=1)
               if index > 5 and key in normalized(page.extract_text() or "")]
    if len(matches) != 1:
        raise ValueError(f"{pdf.name}: {heading!r} occurs on pages {matches}")
    return matches[0]


def check(stage: Path) -> list[dict]:
    covers = json.loads((stage / "approved-cover-verification.json").read_text())
    if len(covers) != 36 or not all(row["rendered_cover_pixel_identical"] for row in covers):
        raise ValueError("All 36 covers need a pixel-identical comparison")
    geometry = json.loads((stage / "geometry-audit.json").read_text())
    if len(geometry) != 36 or any(row["out_of_bounds"] or row["overlap_candidates"]
                                  for rows in geometry.values() for row in rows):
        raise ValueError("Clipped or overlapping text in the staged PDFs")
    rows = []
    for number in range(1, 37):
        code = f"N{number:02d}"
        folder = stage / code
        candidate = folder / "candidate.pdf"
        published = approved_pdf(number)
        audit = json.loads((folder / "text-audit.json").read_text())
        lock = json.loads((folder / "cover-lock.json").read_text())
        if audit["missing_start"] or audit["missing_end"] or audit["changed_source_ids"]:
            raise ValueError(f"{code}: source paragraphs changed or disappeared")
        before, after = digest(published), digest(candidate)
        if before != lock["approved_pdf_sha256"] or after != lock["locked_candidate_sha256"]:
            raise ValueError(f"{code}: published or staged PDF changed after cover lock")
        rows.append({
            "document": code,
            "path": str(published.relative_to(ROOT)),
            "previous_sha256": before,
            "new_sha256": after,
            "changed": before != after,
            "pages": audit["pages"],
            "bytes": candidate.stat().st_size,
            "source_blocks": audit["source_blocks"],
            "references_page": heading_page(candidate, "Referencias base"),
        })
    changed = {int(row["document"][1:]) for row in rows if row["changed"]}
    if changed != EXPECTED_CHANGED:
        raise ValueError(f"Unexpected PDF changes: {sorted(changed)}")
    return rows


def update_html(source: str, rows: list[dict]) -> str:
    by_code = {row["document"]: row for row in rows if row["changed"]}
    for code, row in by_code.items():
        source, count = re.subn(
            rf'(pdf/(?:publicados/)?{code}-METSI-lectura-previa-[^"?]+\.pdf\?v=)[^"#&]+',
            lambda match: match[1] + REVISION, source,
        )
        if count == 0:
            raise ValueError(f"{code}: no public HTML link found")
        source = re.sub(
            rf'({code}-METSI-lectura-previa-[^"#]+#page=)\d+',
            lambda match: match[1] + str(row["references_page"]), source,
        )
        source = re.sub(
            rf'(Bibliografía de {code}, página )\d+',
            lambda match: match[1] + str(row["references_page"]), source,
        )
        source = re.sub(
            rf'(<li><a href="[^"]*{code}-METSI-lectura-previa-[^"]*"[^>]*>[^<]*</a><small>Referencias base · pág\. )\d+',
            lambda match: match[1] + str(row["references_page"]), source,
        )
        source, count = re.subn(
            rf'(<p>{code} · )\d+( páginas</p>)',
            lambda match: match[1] + str(row["pages"]) + match[2], source,
        )
        if count != 1:
            raise ValueError(f"{code}: expected exactly one collection page count, found {count}")
    return source


def update_atlas(source: str, stage: Path, rows: list[dict]) -> str:
    prefix = "window.METSI_ATLAS = "
    if not source.startswith(prefix):
        raise ValueError("Unexpected atlas data format")
    atlas = json.loads(source[len(prefix):].rstrip().removesuffix(";"))
    changed = {row["document"] for row in rows if row["changed"]}
    for item in atlas["items"]:
        for reference in item["refs"]:
            code = reference["code"]
            if code not in changed:
                continue
            candidate = stage / code / "candidate.pdf"
            page = heading_page(candidate, reference["section"])
            reference["page"] = page
            reference["href"] = re.sub(
                r"\?v=[^#]+#page=\d+", f"?v={REVISION}#page={page}", reference["href"]
            )
    return prefix + json.dumps(atlas, ensure_ascii=False, indent=2) + ";\n"


def main(stage: Path, install: bool) -> None:
    rows = check(stage)
    manifest_path = ROOT / "course-manifest.json"
    public_path = ROOT / "site/course-manifest.json"
    home_path = ROOT / "site/index.html"
    atlas_path = ROOT / "site/covers/atlas-data.js"
    manifest = json.loads(manifest_path.read_text())
    public = json.loads(public_path.read_text())
    by_code = {row["document"]: row for row in rows if row["changed"]}
    for entry in manifest["documents"]:
        if entry["code"] in by_code:
            row = by_code[entry["code"]]
            entry.update({"pages": row["pages"], "bytes": row["bytes"],
                          "sha256": row["new_sha256"], "tag": REVISION,
                          "source_version": REVISION, "editorial_revision": REVISION,
                          "qa_report": str(RECEIPT.relative_to(ROOT)), "qa_status": "PASS"})
    for reading in public["readings"]:
        if reading["code"] in by_code:
            row = by_code[reading["code"]]
            reading["pages"] = row["pages"]
            reading["pdf"] = re.sub(r"\?v=[^#]+", f"?v={REVISION}", reading["pdf"])
            reading["revision"] = REVISION
    home = update_html(home_path.read_text(), rows)
    atlas = update_atlas(atlas_path.read_text(), stage, rows)
    print(f"Checked 36 PDFs; replacements: {', '.join(by_code)}")
    print(f"Source blocks verified: {sum(row['source_blocks'] for row in rows)}")
    if not install:
        print("Dry run only: no public file changed")
        return
    rollback_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    temporary = []
    for row in by_code.values():
        source = stage / row["document"] / "candidate.pdf"
        target = ROOT / row["path"]
        staged = target.with_name(target.name + ".art-pass.tmp")
        shutil.copyfile(source, staged)
        if digest(staged) != row["new_sha256"]:
            raise ValueError(f"{row['document']}: temporary copy differs")
        temporary.append((staged, target))
    for staged, target in temporary:
        staged.replace(target)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    public_path.write_text(json.dumps(public, ensure_ascii=False, indent=2) + "\n")
    home_path.write_text(home)
    atlas_path.write_text(atlas)
    RECEIPT.write_text(json.dumps({
        "revision": REVISION, "rollback_commit": rollback_commit,
        "documents_checked": 36, "covers_pixel_identical": 36,
        "source_blocks_verified": sum(row["source_blocks"] for row in rows),
        "text_out_of_bounds": 0, "text_overlap_candidates": 0,
        "files": rows,
    }, ensure_ascii=False, indent=2) + "\n")
    print(f"Installed {len(by_code)} updated PDFs, preserved {36-len(by_code)} byte-identical PDFs")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", type=Path)
    parser.add_argument("--install", action="store_true")
    args = parser.parse_args()
    main(args.stage, args.install)
