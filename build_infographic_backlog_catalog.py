#!/usr/bin/env python3
"""Build a visual review catalog for the METSI N00–N36 infographic assets."""

from __future__ import annotations

import argparse
import html
import json
import math
import os
import re
from pathlib import Path

from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent
VARIANT = os.environ.get("METSI_CATALOG_VARIANT", "v1")
TMP = ROOT / "tmp" / (f"infographic-catalog-{VARIANT}" if VARIANT in {"v2", "v3"} else "infographic-catalog")
ATLAS = TMP / "atlas.png"
HTML = TMP / "atlas.html"
INVENTORY = TMP / "inventory.json"
THUMBS = TMP / "thumbs"
OUTPUT = ROOT / "output" / "pdf" / (
    f"METSI-catalogo-infografias-N00-N36-revision-{VARIANT}.pdf"
    if VARIANT in {"v2", "v3"}
    else "METSI-catalogo-infografias-N00-N36-backlog.pdf"
)
CANDIDATE_V2 = ROOT / "editorial-standard" / "infographic-rebuild-candidates-v2"
CANDIDATE_V3 = ROOT / "editorial-standard" / "infographic-rebuild-candidates-v3"

PACKAGES = {
    0: "N00-v2-candidate",
    1: "N01-v18-final",
    2: "N02-v14-final",
    3: "N03-v9-final",
    4: "N04-v9-final",
    5: "N05-v9-final",
    6: "N06-v9-final",
    7: "N07-v9-final",
    8: "N08-v9-final",
    9: "N09-v9-final",
    10: "N10-v9-final",
    **{n: f"N{n:02d}-v6-editorial" for n in range(11, 37)},
}

VOLT = HexColor("#CFFF00")
INK = HexColor("#171918")
MID = HexColor("#626763")
LIGHT = HexColor("#E5E8E5")
PAPER = HexColor("#F7F6F1")
WHITE = HexColor("#FFFFFF")

CELL_W = 1400
CELL_H = 820
COLS = 3


def svg_title(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"<title[^>]*>(.*?)</title>", raw, re.S | re.I)
    if match:
        return html.unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip()
    meta = path.with_suffix(".json")
    if meta.exists():
        data = json.loads(meta.read_text(encoding="utf-8"))
        if data.get("title"):
            return data["title"]
        if data.get("source_headings"):
            return data["source_headings"][0]
    return path.stem


def build_inventory() -> list[dict]:
    items: list[dict] = []
    for n in range(37):
        package = ROOT / PACKAGES[n]
        diagram_dir = package / "diagrams"
        svg_files = sorted(diagram_dir.glob("*.svg"))
        index_text = (package / "index.html").read_text(encoding="utf-8", errors="ignore")
        candidate_records = {}
        if VARIANT == "v3":
            candidate_manifest = CANDIDATE_V3 / f"N{n:02d}" / "manifest.json"
            if candidate_manifest.exists():
                manifest_data = json.loads(candidate_manifest.read_text(encoding="utf-8"))
                for record in manifest_data.get("pieces", []):
                    original = Path(record["source_spec"]).name.replace("-v2.spec.json", ".svg")
                    candidate_records[original] = (record, "NUEVA V3")
            fallback_manifest = CANDIDATE_V2 / f"N{n:02d}" / "manifest.json"
            if fallback_manifest.exists():
                manifest_data = json.loads(fallback_manifest.read_text(encoding="utf-8"))
                for record in manifest_data.get("pieces", []):
                    candidate_records.setdefault(Path(record["source"]).name, (record, "CONSERVADA V2"))
        elif VARIANT == "v2":
            candidate_manifest = CANDIDATE_V2 / f"N{n:02d}" / "manifest.json"
            if candidate_manifest.exists():
                manifest_data = json.loads(candidate_manifest.read_text(encoding="utf-8"))
                candidate_records = {Path(record["source"]).name: (record, "NUEVA V2") for record in manifest_data.get("pieces", [])}
        for position, svg in enumerate(svg_files, start=1):
            candidate_entry = candidate_records.get(svg.name)
            candidate_record = candidate_entry[0] if candidate_entry else None
            candidate_revision = candidate_entry[1] if candidate_entry else "CONSERVADA"
            display_svg = ROOT / candidate_record["svg"] if candidate_record else svg
            rel = display_svg.relative_to(ROOT).as_posix()
            href = f"diagrams/{svg.name}"
            used = href in index_text
            suffix = "" if len(svg_files) == 1 else chr(64 + position)
            items.append(
                {
                    "n": n,
                    "code": f"N{n:02d}{suffix}",
                    "title": candidate_record["title"] if candidate_record else svg_title(svg),
                    "path": rel,
                    "used": used,
                    "package": package.name,
                    "revision": candidate_revision,
                }
            )
    return items


def prepare() -> None:
    TMP.mkdir(parents=True, exist_ok=True)
    THUMBS.mkdir(parents=True, exist_ok=True)
    items = build_inventory()
    INVENTORY.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    rows = math.ceil(len(items) / COLS)
    cards = []
    for idx, item in enumerate(items):
        uri = (ROOT / item["path"]).resolve().as_uri()
        cards.append(
            f'<div class="cell" data-index="{idx}"><img src="{uri}" alt=""></div>'
        )
    doc = f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; width: {COLS * CELL_W}px; height: {rows * CELL_H}px; overflow: hidden; background: #fff; }}
body {{ display: grid; grid-template-columns: repeat({COLS}, {CELL_W}px); grid-auto-rows: {CELL_H}px; }}
.cell {{ width: {CELL_W}px; height: {CELL_H}px; padding: 24px; background: #fff; display: flex; align-items: center; justify-content: center; }}
.cell img {{ display: block; width: 100%; height: 100%; object-fit: contain; }}
</style></head><body>{''.join(cards)}</body></html>"""
    HTML.write_text(doc, encoding="utf-8")
    print(json.dumps({"items": len(items), "cols": COLS, "rows": rows, "width": COLS * CELL_W, "height": rows * CELL_H, "html": str(HTML)}, ensure_ascii=False))


def crop_thumbnails(items: list[dict]) -> None:
    atlas = Image.open(ATLAS).convert("RGB")
    expected_w = COLS * CELL_W
    expected_h = math.ceil(len(items) / COLS) * CELL_H
    if atlas.width != expected_w or atlas.height != expected_h:
        raise RuntimeError(f"Atlas inesperado: {atlas.size}; esperado {(expected_w, expected_h)}")
    for idx, item in enumerate(items):
        col = idx % COLS
        row = idx // COLS
        crop = atlas.crop((col * CELL_W, row * CELL_H, (col + 1) * CELL_W, (row + 1) * CELL_H))
        target = THUMBS / f"{idx:02d}-{item['code']}.png"
        crop.save(target, optimize=True)
        item["thumb"] = str(target)


def wrap(text: str, font: str, size: float, max_width: float, max_lines: int = 3) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if stringWidth(candidate, font, size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
            if len(lines) == max_lines - 1:
                break
    if current and len(lines) < max_lines:
        lines.append(current)
    consumed = " ".join(lines)
    if len(consumed) < len(text) and lines:
        while stringWidth(lines[-1] + "…", font, size) > max_width and len(lines[-1]) > 2:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip(" ,.;:") + "…"
    return lines


def draw_header(c: canvas.Canvas, page_no: int, total: int) -> None:
    width, height = landscape(A4)
    c.setStrokeColor(INK)
    c.setLineWidth(0.8)
    c.line(34, height - 28, width - 34, height - 28)
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(MID)
    c.drawString(34, 17, "METSI · BACKLOG EDITORIAL · INFOGRAFÍAS N00 A N36")
    c.drawRightString(width - 34, 17, f"{page_no:02d} / {total:02d}")


def draw_checkbox(c: canvas.Canvas, x: float, y: float, label: str) -> float:
    c.setStrokeColor(INK)
    c.setLineWidth(0.8)
    c.rect(x, y - 7, 8, 8, fill=0, stroke=1)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 7.2)
    c.drawString(x + 12, y - 5, label)
    return x + 12 + stringWidth(label, "Helvetica-Bold", 7.2) + 17


def draw_card(c: canvas.Canvas, item: dict, x: float, y: float, w: float, h: float) -> None:
    c.setFillColor(WHITE)
    c.setStrokeColor(LIGHT)
    c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, 5, fill=1, stroke=1)
    c.setFillColor(VOLT)
    c.rect(x, y, 5, h, fill=1, stroke=0)

    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(x + 16, y + h - 23, item["code"])
    revision = item.get("revision", "")
    if revision in {"NUEVA V2", "NUEVA V3"}:
        status = f"{revision} · PARA APROBAR"
    elif revision == "CONSERVADA V2":
        status = "CONSERVADA V2"
    elif item["used"]:
        status = "CONSERVADA · EN DOCUMENTO"
    else:
        status = "CONSERVADA · NO EMBEBIDA"
    c.setFont("Helvetica-Bold", 7.2)
    c.setFillColor(MID if item["used"] else INK)
    c.drawRightString(x + w - 14, y + h - 21, status)

    title_x = x + 55
    title_w = w - 195
    c.setFillColor(INK)
    c.setFont("Times-Bold", 10.2)
    for i, line in enumerate(wrap(item["title"], "Times-Bold", 10.2, title_w, 2)):
        c.drawString(title_x, y + h - 20 - i * 11, line)

    image_box = (x + 15, y + 42, w - 30, h - 80)
    img = Image.open(item["thumb"])
    iw, ih = img.size
    bx, by, bw, bh = image_box
    scale = min(bw / iw, bh / ih)
    dw, dh = iw * scale, ih * scale
    c.drawImage(ImageReader(img), bx + (bw - dw) / 2, by + (bh - dh) / 2, dw, dh, mask="auto")

    c.setFillColor(MID)
    c.setFont("Helvetica", 6.6)
    source = item["path"]
    if stringWidth(source, "Helvetica", 6.6) > w - 30:
        source = "…" + source[-80:]
    c.drawString(x + 15, y + 30, source)
    cx = x + 15
    cx = draw_checkbox(c, cx, y + 15, "OK")
    cx = draw_checkbox(c, cx, y + 15, "REHACER")
    draw_checkbox(c, cx, y + 15, "REVISAR INTEGRACIÓN")


def compose() -> None:
    if not ATLAS.exists():
        raise FileNotFoundError(f"Falta {ATLAS}")
    items = json.loads(INVENTORY.read_text(encoding="utf-8"))
    crop_thumbnails(items)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    width, height = landscape(A4)
    cards_per_page = 4
    content_pages = math.ceil(len(items) / cards_per_page)
    total_pages = 1 + content_pages
    c = canvas.Canvas(str(OUTPUT), pagesize=(width, height), pageCompression=1)
    c.setTitle("METSI · Catálogo de infografías N00 a N36")
    c.setAuthor("Diego Carralbal · METSI")
    c.setSubject("Hoja visual para backlog editorial")

    c.setFillColor(PAPER)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setFillColor(VOLT)
    c.rect(42, height - 78, 76, 10, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(42, height - 108, "METSI · N00 A N36")
    c.setFont("Times-Bold", 38)
    c.drawString(42, height - 164, "Hoja de revisión")
    c.drawString(42, height - 205, "de infografías")
    c.setFont("Helvetica", 13)
    c.setFillColor(MID)
    if VARIANT == "v3":
        subtitle = "Revisión visual · una topología específica para cada argumento"
    else:
        subtitle = "Backlog editorial · revisión visual antes de rehacer piezas"
    c.drawString(44, height - 242, subtitle)

    embedded = sum(1 for i in items if i["used"])
    new_label = f"NUEVA {VARIANT.upper()}"
    new_count = sum(1 for i in items if i.get("revision") == new_label)
    c.setFillColor(WHITE)
    c.roundRect(42, 104, width - 84, 145, 6, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(62, 203, f"{len(items)} piezas")
    c.setFont("Helvetica-Bold", 11)
    if VARIANT in {"v2", "v3"}:
        c.drawString(62, 180, f"{new_count} nuevas {VARIANT} · {len(items) - new_count} conservadas · todavía sin modificar los PDF")
    else:
        c.drawString(62, 180, f"37 documentos · {embedded} embebidas · {len(items) - embedded} activos no embebidos")
    c.setFont("Helvetica", 9)
    c.setFillColor(MID)
    c.drawString(62, 153, "Cada tarjeta muestra la pieza gráfica real seleccionada para esta ronda.")
    c.drawString(62, 137, "Marcá OK, REHACER o REVISAR INTEGRACIÓN y devolvé los códigos N correspondientes.")
    c.drawString(62, 121, "Alcance: infografías SVG autónomas. No incluye fotografías, tablas ni composición de página.")
    c.setFillColor(VOLT)
    c.rect(width - 213, 136, 126, 8, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(width - 213, 120, "PALETA: PAPEL · TINTA · GRISES · VOLT")
    draw_header(c, 1, total_pages)
    c.showPage()

    margin_x = 34
    gap_x = 16
    gap_y = 16
    usable_w = width - margin_x * 2
    card_w = (usable_w - gap_x) / 2
    card_h = (height - 92 - gap_y) / 2
    top_y = height - 45
    for page_index in range(content_pages):
        c.setFillColor(PAPER)
        c.rect(0, 0, width, height, fill=1, stroke=0)
        start = page_index * cards_per_page
        page_items = items[start : start + cards_per_page]
        for local_idx, item in enumerate(page_items):
            col = local_idx % 2
            row = local_idx // 2
            x = margin_x + col * (card_w + gap_x)
            y = top_y - (row + 1) * card_h - row * gap_y
            draw_card(c, item, x, y, card_w, card_h)
        draw_header(c, page_index + 2, total_pages)
        c.showPage()
    c.save()
    print(json.dumps({"pdf": str(OUTPUT), "variant": VARIANT, "pages": total_pages, "items": len(items), "new_count": new_count, "embedded": embedded, "not_embedded": len(items)-embedded, "bytes": OUTPUT.stat().st_size}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["prepare", "compose"])
    args = parser.parse_args()
    if args.stage == "prepare":
        prepare()
    else:
        compose()


if __name__ == "__main__":
    main()
