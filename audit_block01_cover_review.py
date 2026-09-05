#!/usr/bin/env python3
"""Genera una revisión comparativa, de sólo lectura, de las tapas N00 a N10."""

from __future__ import annotations

import hashlib
import json
import math
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "BLOCK-01-cover-review-current"
PDFTOPPM = shutil.which("pdftoppm") or str(
    Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm"
)


@dataclass(frozen=True)
class Document:
    code: str
    pdf: str


DOCUMENTS = (
    Document("N00", "N00-v2-candidate/output/N00-METSI-lectura-previa-v2-candidate-final.pdf"),
    Document("N01", "N01-v18-final/output/N01-METSI-lectura-previa-v18-final.pdf"),
    Document("N02", "N02-v14-final/output/N02-METSI-lectura-previa-v14-final.pdf"),
    Document("N03", "N03-v9-final/output/N03-METSI-lectura-previa-v9-final.pdf"),
    Document("N04", "N04-v9-final/output/N04-METSI-lectura-previa-v9-final.pdf"),
    Document("N05", "N05-v9-final/output/N05-METSI-lectura-previa-v9-final.pdf"),
    Document("N06", "N06-v9-final/output/N06-METSI-lectura-previa-v9-final.pdf"),
    Document("N07", "N07-v9-final/output/N07-METSI-lectura-previa-v9-final.pdf"),
    Document("N08", "N08-v9-final/output/N08-METSI-lectura-previa-v9-final.pdf"),
    Document("N09", "N09-v9-final/output/N09-METSI-lectura-previa-v9-final.pdf"),
    Document("N10", "N10-v9-final/output/N10-METSI-lectura-previa-v9-final.pdf"),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def srgb_channel(value: float) -> float:
    value /= 255.0
    return value / 12.92 if value <= .04045 else ((value + .055) / 1.055) ** 2.4


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    red, green, blue = (srgb_channel(float(value)) for value in rgb)
    return .2126 * red + .7152 * green + .0722 * blue


def contrast(light_rgb: tuple[int, int, int], background_value: float) -> float:
    foreground = relative_luminance(light_rgb)
    background = relative_luminance((int(background_value),) * 3)
    high, low = max(foreground, background), min(foreground, background)
    return (high + .05) / (low + .05)


def metrics(path: Path, code: str) -> dict:
    image = Image.open(path).convert("RGB")
    pixels = np.asarray(image, dtype=np.float32)
    luminance = pixels[:, :, 0] * .2126 + pixels[:, :, 1] * .7152 + pixels[:, :, 2] * .0722
    spread = pixels.max(axis=2) - pixels.min(axis=2)
    gray = luminance[spread < 12]
    height, width = luminance.shape
    x0 = int(width * (.50 if code == "N00" else .58))
    x1 = int(width * .95)
    y0 = int(height * .77)
    y1 = int(height * .92)
    zone_luminance = luminance[y0:y1, x0:x1]
    zone_spread = spread[y0:y1, x0:x1]
    background = zone_luminance[zone_spread < 10]
    background = background[(background > 4) & (background < 246)]
    if not len(background):
        background = zone_luminance.ravel()
    p50 = float(np.percentile(background, 50))
    p75 = float(np.percentile(background, 75))
    current_rgb = (247, 246, 242) if code == "N00" else (207, 255, 0)
    current_contrast = contrast(current_rgb, p75)
    white_contrast = contrast((247, 246, 242), p75)
    ink_contrast = contrast((25, 25, 24), p50)
    if current_contrast >= 4.5:
        recommendation = "conservar"
    elif white_contrast >= 4.5:
        recommendation = "texto_blanco"
    elif ink_contrast >= 4.5:
        recommendation = "texto_tinta"
    else:
        recommendation = "base_tonal_local"
    edge = np.concatenate((luminance[0, :], luminance[-1, :], luminance[:, 0], luminance[:, -1]))
    return {
        "render": str(path.relative_to(ROOT)),
        "sha256": sha256(path),
        "size_px": list(image.size),
        "global": {
            "mean": round(float(luminance.mean()), 2),
            "p05": round(float(np.percentile(luminance, 5)), 2),
            "p50": round(float(np.percentile(luminance, 50)), 2),
            "p95": round(float(np.percentile(luminance, 95)), 2),
            "midtones_64_192_pct": round(float(((luminance >= 64) & (luminance <= 192)).mean() * 100), 2),
            "gray_channel_spread_p95": round(float(np.percentile(spread, 95)), 2),
        },
        "thesis_zone_proxy": {
            "background_p50": round(p50, 2),
            "background_p75": round(p75, 2),
            "current_color": "paper-white" if code == "N00" else "volt",
            "current_contrast_on_p75": round(current_contrast, 2),
            "paper_white_contrast_on_p75": round(white_contrast, 2),
            "ink_contrast_on_p50": round(ink_contrast, 2),
            "recommendation": recommendation,
            "note": "Proxy tonal sobre la zona de tesis. La decisión final exige inspección visual del texto sobre la fotografía.",
        },
        "edge": {
            "mean": round(float(edge.mean()), 2),
            "near_white_pct": round(float((edge > 247).mean() * 100), 2),
            "full_bleed_without_uniform_white_frame": float((edge > 247).mean()) < .85,
        },
        "native_monochrome_render": float(np.percentile(spread, 95)) <= 8,
        "gray_samples": int(gray.size),
    }


def make_contact_sheet(records: list[dict]) -> Path:
    columns = 4
    card_width = 360
    image_width = 320
    image_height = 452
    label_height = 92
    margin = 22
    gap = 20
    rows = math.ceil(len(records) / columns)
    sheet = Image.new(
        "RGB",
        (margin * 2 + columns * card_width + (columns - 1) * gap,
         margin * 2 + rows * (image_height + label_height) + (rows - 1) * gap),
        "#E7E8E4",
    )
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, record in enumerate(records):
        row, column = divmod(index, columns)
        x = margin + column * (card_width + gap)
        y = margin + row * (image_height + label_height + gap)
        cover = Image.open(ROOT / record["metrics"]["render"]).convert("RGB")
        cover.thumbnail((image_width, image_height), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (image_width, image_height), "white")
        canvas.paste(cover, ((image_width - cover.width) // 2, 0))
        sheet.paste(canvas, (x, y))
        global_metrics = record["metrics"]["global"]
        proxy = record["metrics"]["thesis_zone_proxy"]
        lines = [
            f"{record['code']} | media {global_metrics['mean']} | medios {global_metrics['midtones_64_192_pct']}%",
            f"tesis {proxy['current_color']} | contraste proxy {proxy['current_contrast_on_p75']}:1",
            f"sugerencia automatica: {proxy['recommendation']}",
        ]
        for line_number, line in enumerate(lines):
            draw.text((x, y + image_height + 8 + line_number * 22), line, fill="#20211F", font=font)
    output = OUTPUT / "contact-sheet-N00-N10-current.jpg"
    sheet.save(output, quality=93, optimize=True)
    return output


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    records = []
    with tempfile.TemporaryDirectory(prefix="metsi-cover-review-") as temporary:
        temporary_path = Path(temporary)
        for document in DOCUMENTS:
            pdf = ROOT / document.pdf
            reader = PdfReader(str(pdf))
            prefix = temporary_path / document.code
            subprocess.run(
                [PDFTOPPM, "-f", "1", "-l", "1", "-png", "-r", "120", str(pdf), str(prefix)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            rendered = next(temporary_path.glob(f"{document.code}-*.png"))
            destination = OUTPUT / f"cover-{document.code}.png"
            shutil.copy2(rendered, destination)
            text = " ".join((reader.pages[0].extract_text() or "").split())
            records.append({
                "code": document.code,
                "pdf": document.pdf,
                "pdf_sha256": sha256(pdf),
                "pages": len(reader.pages),
                "a4": all(abs(float(page.mediabox.width) - 594.96) <= 1 and abs(float(page.mediabox.height) - 841.92) <= 1 for page in reader.pages),
                "eyebrow_extractable": "LECTURA PREVIA" in text and "EDICIÓN 2026" in text,
                "metrics": metrics(destination, document.code),
            })
    contact = make_contact_sheet(records)
    report = {
        "scope": "Revisión comparativa de tapas vigentes N00 a N10. N00 usa el candidato v2; N01 a N10 usan sus finales cerrados.",
        "read_only": True,
        "documents": records,
        "series": {
            "all_a4": all(record["a4"] for record in records),
            "all_eyebrows_extractable": all(record["eyebrow_extractable"] for record in records),
            "all_full_bleed_without_uniform_white_frame": all(record["metrics"]["edge"]["full_bleed_without_uniform_white_frame"] for record in records),
            "all_native_monochrome_renders": all(record["metrics"]["native_monochrome_render"] for record in records),
            "global_luminance_mean_range": [
                min(record["metrics"]["global"]["mean"] for record in records),
                max(record["metrics"]["global"]["mean"] for record in records),
            ],
            "contact_sheet": str(contact.relative_to(ROOT)),
        },
    }
    (OUTPUT / "audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["series"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
