#!/usr/bin/env python3
"""Render every page to prove public metadata sanitization preserved appearance."""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent
PDFTOPPM = Path("/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm")
REPORT_DIR = ROOT / "qa-reports" / "public-release-sanitization"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(pdf: Path, output: Path, dpi: int) -> list[Path]:
    subprocess.run(
        [str(PDFTOPPM), "-r", str(dpi), "-png", str(pdf), str(output / "page")],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    return sorted(output.glob("page-*.png"))


def text_sha(pdf: Path) -> str:
    digest = hashlib.sha256()
    for page in PdfReader(str(pdf), strict=False).pages:
        digest.update((page.extract_text() or "").encode("utf-8"))
        digest.update(b"\x00PAGE\x00")
    return digest.hexdigest()


def compare(code: str, source: Path, public: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix=f"metsi-{code}-source-") as left_dir, tempfile.TemporaryDirectory(prefix=f"metsi-{code}-public-") as right_dir:
        left = render(source, Path(left_dir), 36)
        right = render(public, Path(right_dir), 36)
        left_hashes = [sha256(path) for path in left]
        right_hashes = [sha256(path) for path in right]
    source_text = text_sha(source)
    public_text = text_sha(public)
    return {
        "code": code,
        "source": source.relative_to(ROOT).as_posix(),
        "public": public.relative_to(ROOT).as_posix(),
        "pages": len(left),
        "render_dpi": 36,
        "all_page_rasters_identical": left_hashes == right_hashes,
        "extracted_text_identical": source_text == public_text,
        "source_text_sha256": source_text,
        "public_text_sha256": public_text,
    }


def program_contact_sheet(pdf: Path) -> dict[str, Any]:
    output = REPORT_DIR / "programa-metsi-2026-review.png"
    with tempfile.TemporaryDirectory(prefix="metsi-program-") as directory:
        pages = render(pdf, Path(directory), 72)
        images = [Image.open(path).convert("RGB") for path in pages]
        thumb_width = 298
        thumbs = []
        for image in images:
            height = round(image.height * thumb_width / image.width)
            thumbs.append(ImageOps.expand(image.resize((thumb_width, height)), border=4, fill="white"))
        columns = 4
        rows = (len(thumbs) + columns - 1) // columns
        cell_width = max(image.width for image in thumbs) + 20
        cell_height = max(image.height for image in thumbs) + 20
        sheet = Image.new("RGB", (columns * cell_width, rows * cell_height), "#d8d8d5")
        for index, image in enumerate(thumbs):
            x = (index % columns) * cell_width + 10
            y = (index // columns) * cell_height + 10
            sheet.paste(image, (x, y))
        sheet.save(output, optimize=True)
    return {
        "pdf": pdf.relative_to(ROOT).as_posix(),
        "pages": len(pages),
        "contact_sheet": output.relative_to(ROOT).as_posix(),
        "rendered_successfully": len(pages) == 7,
    }


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = load(ROOT / "course-manifest.json")
    results = []
    for record in manifest["documents"]:
        code = record["code"]
        results.append(compare(code, ROOT / record["pdf"], ROOT / record["public_pdf"]))
        print(code, "PASS" if results[-1]["all_page_rasters_identical"] and results[-1]["extracted_text_identical"] else "FAIL", flush=True)
    program = program_contact_sheet(ROOT / "site" / "covers" / "programa" / "programa-metsi-2026.pdf")
    status = "PASS" if all(row["all_page_rasters_identical"] and row["extracted_text_identical"] for row in results) and program["rendered_successfully"] else "FAIL"
    report = {"status": status, "documents": results, "program": program}
    (REPORT_DIR / "visual-equivalence.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "documents": len(results), "pages": sum(row["pages"] for row in results)}))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
