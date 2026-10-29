"""Prove N25 PDF-level provenance without keeping an extra finished PDF.

Inputs: the original PDF from Git LFS history, three small editorial overlays
tracked in this repository, and the p. 3 normalization script. All generated
PDFs live in a temporary directory removed automatically after SHA checks.
"""

from __future__ import annotations

from io import BytesIO
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import Color
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OVERLAYS = ROOT / "N25-pdf-source/overlays"
ORIGINAL_SHA = "5994f0f2465c5f39582723ef4b74cf2531000fe2b25e8b3e87291d974c526518"
V7_SHA = "19cd382b9ea34ef09878dbc0e4ccfa4502740e809e524b9015df360e8adeb241"
FINAL_SHA = "8b3380ea04f9ac019157cbe9e5677343860a87a7b87a9423c107061bd9b1232e"
PAGE_W, PAGE_H = 594.95996, 841.91998


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lfs_media_dir() -> Path:
    output = subprocess.check_output(["git", "lfs", "env"], cwd=ROOT, text=True)
    entry = next(line for line in output.splitlines() if line.startswith("LocalMediaDir="))
    return Path(entry.split("=", 1)[1])


def grayscale_layer(rect, redraw_volt=False):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    c.setBlendMode("Color")
    c.setFillColor(Color(.5, .5, .5))
    c.rect(*rect, fill=1, stroke=0)
    c.setBlendMode("Normal")
    if redraw_volt:
        c.setFillColor(Color(.84, 1, 0))
        shape = c.beginPath()
        shape.moveTo(50, 783.3)
        shape.lineTo(113, 783.3)
        shape.lineTo(120, 791.3)
        shape.lineTo(57, 791.3)
        shape.close()
        c.drawPath(shape, fill=1, stroke=0)
    c.showPage()
    c.save()
    buffer.seek(0)
    return PdfReader(buffer).pages[0]


def main() -> None:
    media = lfs_media_dir()
    source = media / ORIGINAL_SHA[:2] / ORIGINAL_SHA[2:4] / ORIGINAL_SHA
    final = ROOT / "site/pdf/publicados/N25-METSI-lectura-previa-v10-final.pdf"
    if not source.is_file():
        raise FileNotFoundError(f"Historical LFS object not cached: {ORIGINAL_SHA}")
    if digest(source) != ORIGINAL_SHA or digest(final) != FINAL_SHA:
        raise AssertionError("Baseline or final PDF SHA changed")
    for number in (9, 20, 28):
        if not (OVERLAYS / f"overlay-p{number}.pdf").is_file():
            raise FileNotFoundError(number)

    with tempfile.TemporaryDirectory(prefix="metsi-n25-rebuild-", dir="/private/tmp") as directory:
        temporary = Path(directory)
        monochrome = temporary / "n25-monochrome.pdf"
        candidate = temporary / "n25-v7.pdf"
        writer = PdfWriter(clone_from=source)
        if len(writer.pages) != 33:
            raise AssertionError("Original page count changed")
        writer.pages[6].merge_page(grayscale_layer((48, PAGE_H - 406, 491, 159)))
        writer.pages[17].merge_page(grayscale_layer((0, 44, PAGE_W, PAGE_H - 44), redraw_volt=True))
        with monochrome.open("wb") as stream:
            writer.write(stream)

        merged = PdfWriter(clone_from=monochrome)
        original = PdfReader(source)
        for number in (9, 20, 28):
            overlay = PdfReader(OVERLAYS / f"overlay-p{number}.pdf")
            if len(overlay.pages) != 1:
                raise AssertionError(f"Unexpected overlay pagination: {number}")
            merged.pages[number - 1].merge_page(overlay.pages[0])
        with candidate.open("wb") as stream:
            merged.write(stream)
        current = PdfReader(candidate)
        if len(current.pages) != 33:
            raise AssertionError("Candidate page count changed")
        for index in range(33):
            if original.pages[index].extract_text() not in current.pages[index].extract_text():
                raise AssertionError(f"Original text lost: page {index + 1}")
        if digest(candidate) != V7_SHA:
            raise AssertionError(f"V7 candidate differs: {digest(candidate)}")
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/normalize_n22_n23_n25_referentes_20261028.py"), "N25", str(candidate)],
            check=True,
        )
        if digest(candidate) != FINAL_SHA:
            raise AssertionError(f"Current final differs: {digest(candidate)}")
        print({"pages": 33, "original_sha": ORIGINAL_SHA, "v7_sha": V7_SHA,
               "final_sha": FINAL_SHA, "same_as_canonical": digest(candidate) == digest(final),
               "temporary_files_removed_on_exit": True})


if __name__ == "__main__":
    main()
