#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import zlib
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf._text_extraction import mult
from pypdf.generic import ArrayObject, ByteStringObject, ContentStream, FloatObject, NameObject, NumberObject, TextStringObject
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader


HERE = Path(__file__).resolve().parent
LINKEDIN = "https://www.linkedin.com/in/carralbal/"


def resolve_font(env_name: str, packaged_name: str, system_path: str) -> Path:
    """Resolve the exact METSI font without depending on a user directory."""
    candidates = []
    configured = os.environ.get(env_name)
    if configured:
        candidates.append(Path(configured).expanduser())
    candidates.extend((HERE / "assets" / "fonts" / packaged_name, Path(system_path)))
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        f"Falta {packaged_name}. Definí {env_name} con la ruta al archivo tipográfico autorizado."
    )


def register_fonts() -> None:
    avenir = resolve_font("METSI_AVENIR_FONT", "Avenir.ttc", "/System/Library/Fonts/Avenir.ttc")
    didot = resolve_font("METSI_DIDOT_FONT", "Didot.ttc", "/System/Library/Fonts/Supplemental/Didot.ttc")
    pdfmetrics.registerFont(TTFont("Avenir", str(avenir), subfontIndex=0))
    pdfmetrics.registerFont(TTFont("Didot", str(didot), subfontIndex=0))


def footer(width: float, height: float, number: int, light: bool) -> bytes:
    stream = BytesIO()
    canvas = Canvas(stream, pagesize=(width, height))
    canvas.setFont("Avenir", 6.7)
    if light:
        canvas.setFillColorRGB(.91, .93, .89)
        canvas.setStrokeColorRGB(.65, .68, .63)
    else:
        canvas.setFillColorRGB(.34, .36, .34)
        canvas.setStrokeColorRGB(.76, .78, .76)
    canvas.setLineWidth(.35)
    canvas.line(44, 40, width - 44, 40)
    canvas.drawString(44, 25, f"{number:02d}")
    label = "Diego Carralbal, 2026  ·  linkedin.com/in/carralbal"
    label_width = pdfmetrics.stringWidth(label, "Avenir", 6.7)
    x = width - 44 - label_width
    canvas.drawString(x, 25, label)
    canvas.linkURL(LINKEDIN, (x, 18, width - 44, 35), relative=0, thickness=0)
    canvas.save()
    return stream.getvalue()


def solid_background(width: float, height: float, red: float, green: float, blue: float) -> bytes:
    stream = BytesIO()
    canvas = Canvas(stream, pagesize=(width, height))
    canvas.setFillColorRGB(red, green, blue)
    canvas.rect(0, 0, width, height, stroke=0, fill=1)
    canvas.save()
    return stream.getvalue()


def solid_bottom_band(width: float, height: float, band_height: float, red: float, green: float, blue: float) -> bytes:
    stream = BytesIO()
    canvas = Canvas(stream, pagesize=(width, height))
    canvas.setFillColorRGB(red, green, blue)
    canvas.rect(0, 0, width, band_height, stroke=0, fill=1)
    canvas.save()
    return stream.getvalue()


def solid_left_band(width: float, height: float, band_width: float, red: float, green: float, blue: float) -> bytes:
    stream = BytesIO()
    canvas = Canvas(stream, pagesize=(width, height))
    canvas.setFillColorRGB(red, green, blue)
    canvas.rect(0, 0, band_width, height, stroke=0, fill=1)
    canvas.save()
    return stream.getvalue()


def set_image_alt(page, value: str) -> int:
    """Attach diagnostic alt metadata to image XObjects.

    This does not replace a tagged ``Figure`` connected through the structure
    tree.  It is retained only as redundant metadata for compatible viewers.
    """
    resources = page.get("/Resources")
    if not resources:
        return 0
    resources = resources.get_object()
    xobjects = resources.get("/XObject")
    if not xobjects:
        return 0
    xobjects = xobjects.get_object()
    count = 0
    for reference in xobjects.values():
        obj = reference.get_object()
        if obj.get("/Subtype") == "/Image":
            obj[NameObject("/Alt")] = TextStringObject(value)
            count += 1
    return count


def set_structure_figure_alt(writer: PdfWriter, page_number: int, alt_text: str) -> int:
    """Set /Alt on Figure structure elements associated with one output page."""
    if not alt_text or not (1 <= page_number <= len(writer.pages)):
        return 0
    root = writer.root_object.get("/StructTreeRoot")
    target_ref = writer.pages[page_number - 1].indirect_reference
    target_id = target_ref.idnum if target_ref is not None else None
    if not root or target_id is None:
        return 0
    seen: set[tuple[str, int, int] | tuple[str, int]] = set()
    adjusted = 0

    def reference_id(value) -> int | None:
        if value is None:
            return None
        if hasattr(value, "idnum"):
            return int(value.idnum)
        ref = getattr(value, "indirect_reference", None)
        return int(ref.idnum) if ref is not None else None

    def walk(node, inherited_page=None) -> None:
        nonlocal adjusted
        if node is None:
            return
        if hasattr(node, "idnum"):
            identity = ("ref", int(node.idnum), int(getattr(node, "generation", 0)))
            if identity in seen:
                return
            seen.add(identity)
        try:
            item = node.get_object()
        except Exception:
            item = node
        if isinstance(item, dict):
            identity = ("obj", id(item))
            if identity in seen:
                return
            seen.add(identity)
            page_ref = item.get("/Pg") or inherited_page
            if str(item.get("/S")) == "/Figure" and reference_id(page_ref) == target_id:
                item[NameObject("/Alt")] = TextStringObject(alt_text)
                adjusted += 1
            if item.get("/K") is not None:
                walk(item.get("/K"), page_ref)
        elif isinstance(item, (list, tuple, ArrayObject)):
            for child in item:
                walk(child, inherited_page)

    walk(root)
    return adjusted


def visible_text_floor(page) -> float:
    """Return the lowest visible baseline in page coordinates."""
    values: list[float] = []

    def visitor(text, cm, tm, font_dict, font_size) -> None:
        if not text.strip():
            return
        y = float(mult(tm, cm)[5])
        if 0 <= y <= float(page.mediabox.height):
            values.append(y)

    page.extract_text(visitor_text=visitor)
    return min(values, default=0.0)


def wrap_quote(value: str, max_width: float, size: float = 13.5) -> list[str]:
    words = value.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join([*current, word])
        if current and pdfmetrics.stringWidth(candidate, "Didot", size) > max_width:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines[:3]


def sparse_visual_overlay(width: float, height: float, image_path: Path, quote: str, text_floor: float) -> bytes:
    """Fill a genuinely unused lower field with a document-local editorial plate."""
    stream = BytesIO()
    canvas = Canvas(stream, pagesize=(width, height))
    x = 44.0
    y = 56.0
    visual_width = width - 88.0
    # The image occupies the whole genuinely unused lower field.  The quote is
    # contained inside the photograph instead of floating above it, where it
    # could collide with the preceding article text.
    visual_height = max(220.0, min(650.0, text_floor - y - 6.0))
    quote_size = 13.1
    quote_lines = wrap_quote(quote, visual_width - 76.0, quote_size)
    quote_panel_height = max(64.0, len(quote_lines) * 16.5 + 30.0)

    with Image.open(image_path) as source:
        source = source.convert("RGB")
        target_width = 1600
        target_height = max(540, round(target_width * visual_height / visual_width))
        source = ImageOps.fit(source, (target_width, target_height), method=Image.Resampling.LANCZOS)
        source = ImageEnhance.Color(source).enhance(.28)
        source = ImageEnhance.Contrast(source).enhance(1.08)
        buffer = BytesIO()
        source.save(buffer, format="JPEG", quality=88, optimize=True)
        buffer.seek(0)
        canvas.drawImage(ImageReader(buffer), x, y, visual_width, visual_height, preserveAspectRatio=False, mask="auto")

    canvas.setFillColorRGB(.055, .06, .055)
    canvas.setFillAlpha(.78)
    canvas.rect(x, y, visual_width, quote_panel_height, stroke=0, fill=1)
    canvas.setFillAlpha(1)
    canvas.setFillColorRGB(.81, 1.0, 0.0)
    mark_x = x + 18.0
    mark_y = y + quote_panel_height - 19.0
    mark = canvas.beginPath()
    mark.moveTo(mark_x, mark_y)
    mark.lineTo(mark_x + 42.0, mark_y)
    mark.lineTo(mark_x + 37.0, mark_y + 5.0)
    mark.lineTo(mark_x - 5.0, mark_y + 5.0)
    mark.close()
    canvas.drawPath(mark, stroke=0, fill=1)
    canvas.setFillColorRGB(.97, .97, .95)
    canvas.setFont("Didot", quote_size)
    line_y = y + quote_panel_height - 25.0
    for line in quote_lines:
        canvas.drawString(x + 72.0, line_y, line)
        line_y -= 16.5
    canvas.save()
    return stream.getvalue()


def strip_empty_helvetica(page, reader: PdfReader) -> None:
    resources = page.get("/Resources")
    if not resources:
        return
    resources = resources.get_object()
    fonts = resources.get("/Font")
    if not fonts:
        return
    fonts = fonts.get_object()
    helvetica = {
        str(key)
        for key, value in fonts.items()
        if re.search(r"Arial|Helvetica", str(value.get_object().get("/BaseFont", "")), re.I)
    }
    if not helvetica:
        return
    content = ContentStream(page.get_contents(), reader)
    cleaned = []
    index = 0
    while index < len(content.operations):
        operands, operator = content.operations[index]
        if operator == b"BT":
            end = index + 1
            while end < len(content.operations) and content.operations[end][1] != b"ET":
                end += 1
            if end < len(content.operations):
                block = content.operations[index : end + 1]
                uses = any(op == b"Tf" and str(args[0]) in helvetica for args, op in block)
                draws = any(op in {b"Tj", b"TJ", b"'", b'"'} for _, op in block)
                if uses and not draws:
                    index = end + 1
                    continue
        cleaned.append((operands, operator))
        index += 1
    content.operations = cleaned
    page.replace_contents(content)
    used = {str(args[0]) for args, op in cleaned if op == b"Tf"}
    for key in list(fonts.keys()):
        if str(key) in helvetica and str(key) not in used:
            del fonts[key]


def normalize(value: str) -> str:
    value = value.casefold().replace("ﬁ", "fi").replace("ﬂ", "fl")
    return re.sub(r"[^a-z0-9áéíóúüñ]+", "", value)


def collect_fonts(reader: PdfReader) -> set[str]:
    result: set[str] = set()
    seen: set[int] = set()

    def walk(resources) -> None:
        if not resources:
            return
        resources = resources.get_object()
        marker = id(resources)
        if marker in seen:
            return
        seen.add(marker)
        fonts = resources.get("/Font")
        if fonts:
            for ref in fonts.get_object().values():
                base = ref.get_object().get("/BaseFont")
                if base:
                    result.add(str(base))
        xobjects = resources.get("/XObject")
        if xobjects:
            for ref in xobjects.get_object().values():
                walk(ref.get_object().get("/Resources"))

    for page in reader.pages:
        walk(page.get("/Resources"))
    return result


def scale_cover_pattern_matrices(page, scale: float) -> int:
    """Extend Chromium's N01 cover gradient horizontally to the trim box."""
    resources = page.get("/Resources")
    if not resources:
        return 0
    patterns = resources.get_object().get("/Pattern")
    if not patterns:
        return 0
    adjusted = 0
    for reference in patterns.get_object().values():
        pattern = reference.get_object()
        bbox = pattern.get("/BBox")
        matrix = pattern.get("/Matrix")
        if not bbox or not matrix or len(matrix) != 6:
            continue
        width = float(bbox[2]) - float(bbox[0])
        height = float(bbox[3]) - float(bbox[1])
        if not (538 <= width <= 542 and 762 <= height <= 766):
            continue
        values = [FloatObject(float(value)) for value in matrix]
        values[0] = FloatObject(float(values[0]) * scale)
        pattern[NameObject("/Matrix")] = ArrayObject(values)
        adjusted += 1
    return adjusted


def extend_n01_cover_pattern_to_trim(page) -> int:
    """Extend N01's localized cover scrim to the bottom trim without tiling.

    The final tonal treatment deliberately uses one localized gradient rather
    than the earlier pair of overlapping scrims.  Chromium may rasterize that
    gradient as one or more full-page patterns; every matching pattern must
    reach the trim box.
    """
    resources = page.get("/Resources")
    if not resources:
        return 0
    patterns = resources.get_object().get("/Pattern")
    if not patterns:
        return 0
    target_height = int(round(float(page.mediabox.height)))
    adjusted = 0
    for reference in patterns.get_object().values():
        pattern = reference.get_object()
        bbox = pattern.get("/BBox")
        if not bbox or len(bbox) != 4:
            continue
        old_height = int(round(float(bbox[3]) - float(bbox[1])))
        width = int(round(float(bbox[2]) - float(bbox[0])))
        if not (538 <= width <= 542 and 762 <= old_height <= 766 and target_height > old_height):
            continue
        xobjects = pattern.get("/Resources").get_object().get("/XObject").get_object()
        vertical_images = []
        for name, image_reference in xobjects.items():
            image = image_reference.get_object()
            image_width = int(image.get("/Width", 0))
            image_height = int(image.get("/Height", 0))
            if (
                image.get("/Subtype") == "/Image"
                and image.get("/ColorSpace") == "/DeviceRGB"
                and image_height == old_height
                and image_width in {1, width}
            ):
                vertical_images.append((name, image))
        if len(vertical_images) != 2:
            raise RuntimeError(
                f"Se esperaban dos imágenes verticales en el patrón de tapa N01 y se hallaron {len(vertical_images)}"
            )
        for name, image in vertical_images:
            image_width = int(image.get("/Width"))
            image_height = int(image.get("/Height"))
            row_stride = image_width * 3
            image_data = image.get_data()
            if len(image_data) != row_stride * image_height:
                raise RuntimeError(f"Datos RGB inesperados en {name} del patrón de tapa N01")
            image._data = zlib.compress(
                image_data + image_data[-row_stride:] * (target_height - image_height)
            )
            image[NameObject("/Height")] = NumberObject(target_height)
            soft_mask = image.get("/SMask")
            if soft_mask is None:
                raise RuntimeError(f"Falta máscara alfa en {name} del patrón de tapa N01")
            soft_mask = soft_mask.get_object()
            mask_data = soft_mask.get_data()
            if len(mask_data) != image_width * image_height:
                raise RuntimeError(f"Máscara alfa inesperada en {name} del patrón de tapa N01")
            soft_mask._data = zlib.compress(
                mask_data + mask_data[-image_width:] * (target_height - image_height)
            )
            soft_mask[NameObject("/Height")] = NumberObject(target_height)
        pattern[NameObject("/BBox")] = ArrayObject([
            FloatObject(0), FloatObject(0), FloatObject(float(bbox[2])), FloatObject(target_height + .00012)
        ])
        pattern[NameObject("/YStep")] = FloatObject(target_height + 2.00012)
        stream = pattern.get_data().decode("ascii")
        pattern._data = re.sub(
            rf"(?<![0-9]){old_height}(?=\b|\.)",
            str(target_height),
            stream,
        ).encode("ascii")
        pattern.pop(NameObject("/Filter"), None)
        adjusted += 1
    if adjusted < 1:
        raise RuntimeError("No se encontró el patrón localizado de tapa N01 para extender al corte")
    return adjusted


def extend_n06_cover_pattern_to_trim(page, scale: float) -> int:
    """Extend N06's rasterized cover scrim to the four trim edges.

    Chromium emits the full-height gradient as a 548 × 775 image inside a
    tiling pattern. Scaling the page content enlarges the photograph but the
    pattern matrix remains in device coordinates, leaving a visible horizontal
    seam near the bottom. Scale the pattern horizontally and extend its final
    gradient row vertically so the tonal treatment reaches the trim box.
    """
    resources = page.get("/Resources")
    if not resources:
        return 0
    patterns = resources.get_object().get("/Pattern")
    if not patterns:
        return 0
    target_height = int(round(float(page.mediabox.height)))
    adjusted = 0
    for reference in patterns.get_object().values():
        pattern = reference.get_object()
        bbox = pattern.get("/BBox")
        matrix = pattern.get("/Matrix")
        if not bbox or len(bbox) != 4 or not matrix or len(matrix) != 6:
            continue
        old_height = int(round(float(bbox[3]) - float(bbox[1])))
        width = int(round(float(bbox[2]) - float(bbox[0])))
        if not (546 <= width <= 550 and 773 <= old_height <= 777 and target_height > old_height):
            continue
        values = [FloatObject(float(value)) for value in matrix]
        values[0] = FloatObject(float(values[0]) * scale)
        pattern[NameObject("/Matrix")] = ArrayObject(values)
        xobjects = pattern.get("/Resources").get_object().get("/XObject").get_object()
        full_height_images = []
        for name, image_reference in xobjects.items():
            image = image_reference.get_object()
            if (
                image.get("/Subtype") == "/Image"
                and image.get("/ColorSpace") == "/DeviceRGB"
                and int(image.get("/Width", 0)) == width
                and int(image.get("/Height", 0)) == old_height
            ):
                full_height_images.append((name, image))
        if len(full_height_images) != 1:
            raise RuntimeError(
                f"Se esperaba una imagen de gradiente completa en la tapa N06 y se hallaron {len(full_height_images)}"
            )
        name, image = full_height_images[0]
        row_stride = width * 3
        image_data = image.get_data()
        if len(image_data) != row_stride * old_height:
            raise RuntimeError(f"Datos RGB inesperados en {name} del patrón de tapa N06")
        image._data = zlib.compress(
            image_data + image_data[-row_stride:] * (target_height - old_height)
        )
        image[NameObject("/Height")] = NumberObject(target_height)
        soft_mask = image.get("/SMask")
        if soft_mask is None:
            raise RuntimeError(f"Falta máscara alfa en {name} del patrón de tapa N06")
        soft_mask = soft_mask.get_object()
        mask_data = soft_mask.get_data()
        if len(mask_data) != width * old_height:
            raise RuntimeError(f"Máscara alfa inesperada en {name} del patrón de tapa N06")
        soft_mask._data = zlib.compress(
            mask_data + mask_data[-width:] * (target_height - old_height)
        )
        soft_mask[NameObject("/Height")] = NumberObject(target_height)
        pattern[NameObject("/BBox")] = ArrayObject([
            FloatObject(0), FloatObject(0), FloatObject(float(bbox[2])), FloatObject(target_height + .00012)
        ])
        pattern[NameObject("/YStep")] = FloatObject(target_height + 2.00012)
        stream = pattern.get_data().decode("ascii")
        pattern._data = re.sub(
            rf"(?<![0-9]){old_height}(?=\b|\.)",
            str(target_height),
            stream,
        ).encode("ascii")
        pattern.pop(NameObject("/Filter"), None)
        adjusted += 1
    if adjusted != 1:
        raise RuntimeError(f"Se esperaba extender un patrón de tapa N06 y se extendieron {adjusted}")
    return adjusted


def cid_width(font, cid: int) -> float:
    descendant = font.get("/DescendantFonts")[0].get_object()
    default = float(descendant.get("/DW", 1000))
    widths = descendant.get("/W", [])
    index = 0
    while index < len(widths):
        start = int(widths[index])
        second = widths[index + 1]
        if isinstance(second, ArrayObject):
            offset = cid - start
            if 0 <= offset < len(second):
                return float(second[offset])
            index += 2
            continue
        end = int(second)
        width = float(widths[index + 2])
        if start <= cid <= end:
            return width
        index += 3
    return default


def consolidate_n01_cover_eyebrow(page, reader: PdfReader) -> int:
    """Turn each eyebrow line into one PDF text run with native char spacing."""
    content = ContentStream(page.get_contents(), reader)
    operations = content.operations
    rewritten = []
    adjusted = 0
    position = 0
    while position < len(operations):
        operands, operator = operations[position]
        if operator != b"BT":
            rewritten.append((operands, operator))
            position += 1
            continue
        end = position + 1
        while end < len(operations) and operations[end][1] != b"ET":
            end += 1
        if end >= len(operations):
            rewritten.extend(operations[position:])
            break
        block = operations[position:end + 1]
        target_tm = None
        font_name = None
        font_size = None
        for block_operands, block_operator in block:
            if block_operator == b"Tf":
                font_name = block_operands[0]
                font_size = float(block_operands[1])
            elif block_operator == b"Tm" and len(block_operands) == 6:
                x = float(block_operands[4])
                y = float(block_operands[5])
                if abs(x - 68.03125) < .02 and (abs(y - 76) < .02 or abs(y - 87) < .02):
                    target_tm = block_operator
        if target_tm is None or font_name is None or font_size is None:
            rewritten.extend(block)
            position = end + 1
            continue
        text_indices = [idx for idx, item in enumerate(block) if item[1] == b"Tj"]
        move_indices = [idx for idx, item in enumerate(block) if item[1] == b"Td"]
        if len(text_indices) < 2 or len(move_indices) != len(text_indices) - 1:
            raise RuntimeError("Estructura inesperada del eyebrow N01")
        glyphs = [block[idx][0][0] for idx in text_indices]
        raw_glyphs = []
        for value in glyphs:
            raw = getattr(value, "original_bytes", None)
            if raw is None:
                raise RuntimeError("Glifo del eyebrow sin codificación PDF original")
            raw_glyphs.append(raw)
        font = page["/Resources"]["/Font"][font_name].get_object()
        spacings = []
        for glyph, move_index in zip(raw_glyphs[:-1], move_indices):
            cid = int.from_bytes(glyph, "big")
            move = float(block[move_index][0][0])
            natural = cid_width(font, cid) * font_size / 1000
            spacings.append(move - natural)
        tracking = sum(spacings) / len(spacings)
        if max(abs(value - tracking) for value in spacings) > .002:
            raise RuntimeError(f"Tracking irregular en eyebrow N01: {spacings}")
        first_text = text_indices[0]
        last_move_or_text = max(text_indices + move_indices)
        new_block = list(block[:first_text])
        new_block.append(([FloatObject(tracking)], b"Tc"))
        new_block.append(([ByteStringObject(b"".join(raw_glyphs))], b"Tj"))
        new_block.append(([FloatObject(0)], b"Tc"))
        new_block.extend(block[last_move_or_text + 1:])
        rewritten.extend(new_block)
        adjusted += 1
        position = end + 1
    if adjusted != 2:
        raise RuntimeError(f"Se esperaban dos líneas de eyebrow y se consolidaron {adjusted}")
    content.operations = rewritten
    page.replace_contents(content)
    return adjusted


def finalize(number: int) -> dict:
    code = f"N{number:02d}"
    root = HERE / ("N01-v18-final" if number == 1 else "N02-v14-final" if number == 2 else "N03-v9-final" if number == 3 else "N04-v9-final" if number == 4 else "N05-v9-final" if number == 5 else "N06-v9-final" if number == 6 else "N07-v9-final" if number == 7 else "N08-v9-final" if number == 8 else "N09-v9-final" if number == 9 else "N10-v9-final" if number == 10 else code)
    raw_name = "N01-METSI-lectura-previa-v18.pdf" if number == 1 else "N02-METSI-lectura-previa-v14.pdf" if number == 2 else "N03-METSI-lectura-previa-v9.pdf" if number == 3 else "N04-METSI-lectura-previa-v9.pdf" if number == 4 else "N05-METSI-lectura-previa-v9.pdf" if number == 5 else "N06-METSI-lectura-previa-v9.pdf" if number == 6 else "N07-METSI-lectura-previa-v9.pdf" if number == 7 else "N08-METSI-lectura-previa-v9.pdf" if number == 8 else "N09-METSI-lectura-previa-v9.pdf" if number == 9 else "N10-METSI-lectura-previa-v9.pdf" if number == 10 else f"{code}-METSI-lectura-previa.pdf"
    final_name = "N01-METSI-lectura-previa-v18-final.pdf" if number == 1 else "N02-METSI-lectura-previa-v14-final.pdf" if number == 2 else "N03-METSI-lectura-previa-v9-final.pdf" if number == 3 else "N04-METSI-lectura-previa-v9-final.pdf" if number == 4 else "N05-METSI-lectura-previa-v9-final.pdf" if number == 5 else "N06-METSI-lectura-previa-v9-final.pdf" if number == 6 else "N07-METSI-lectura-previa-v9-final.pdf" if number == 7 else "N08-METSI-lectura-previa-v9-final.pdf" if number == 8 else "N09-METSI-lectura-previa-v9-final.pdf" if number == 9 else "N10-METSI-lectura-previa-v9-final.pdf" if number == 10 else f"{code}-METSI-lectura-previa-final.pdf"
    raw = root / "output" / raw_name
    final = root / "output" / final_name
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    reader = PdfReader(str(raw))
    writer = PdfWriter()
    preserve_tagged_structure = number in {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
    if preserve_tagged_structure:
        # Chromium ya produce un PDF etiquetado a partir del HTML semántico.
        # Clonar el documento completo conserva StructTreeRoot, Lang y MarkInfo;
        # agregar páginas una por una los descartaba silenciosamente.
        writer.clone_document_from_reader(reader)
    quotes = [normalize(value) for value in manifest.get("quotes", [])]
    display_quotes = manifest.get("quotes", [])
    internal_images = [root / "assets" / value for value in manifest.get("internal_images", [])]
    sparse_fill_images = [root / "assets" / value for value in manifest.get("sparse_fill_images", [])] or internal_images
    kept_page_number = 0
    removed_blank_pages: list[int] = []
    sparse_visual_fills: list[int] = []
    if number == 0 and preserve_tagged_structure:
        blank_indexes: list[int] = []
        for index, page in enumerate(writer.pages):
            page_text = page.extract_text() or ""
            try:
                image_count = len(page.images)
            except Exception:
                image_count = 0
            if not re.search(r"\w", page_text, flags=re.UNICODE) and image_count == 0:
                blank_indexes.append(index)
        for index in reversed(blank_indexes):
            writer.remove_page(index)
        removed_blank_pages.extend(index + 1 for index in blank_indexes)
        writer.root_object[NameObject("/Lang")] = TextStringObject("es-AR")
    source_pages = writer.pages if preserve_tagged_structure else reader.pages
    for source_page_number, page in enumerate(source_pages, 1):
        page_text = page.extract_text() or ""
        # Chromium can emit an empty intermediary sheet when it moves between
        # named paged-media contexts.  It has no pedagogical or visual content,
        # so remove it before adding folios and links.  Image-only editorial
        # pauses and the closing page are preserved because they contain images.
        try:
            image_count = len(page.images)
        except Exception:
            image_count = 0
        if not preserve_tagged_structure and not re.search(r"\w", page_text, flags=re.UNICODE) and image_count == 0:
            removed_blank_pages.append(source_page_number)
            continue
        source_word_count = len(re.findall(r"\b[\wÁÉÍÓÚÜÑáéíóúüñ'-]+\b", page_text, flags=re.UNICODE))
        text_floor = visible_text_floor(page)
        if (
            number not in {0, 1, 3, 4, 5, 6, 7, 8, 9, 10}
            and
            4 <= source_page_number < len(reader.pages)
            and image_count == 0
            and internal_images
            and display_quotes
            and source_word_count < 180
            and text_floor > 400
        ):
            # Offset the editorial asset so a fill immediately before the
            # first full-bleed pause never repeats that pause's photograph.
            image_path = sparse_fill_images[len(sparse_visual_fills) % len(sparse_fill_images)]
            # Use the fill sequence—not the page number—so two sparse pages do
            # not accidentally repeat the same pull quote. In N03 also avoid
            # echoing the quote of an immediately following full-bleed pause.
            quote_candidates = display_quotes
            if number == 3 and source_page_number < len(reader.pages):
                next_text = normalize(reader.pages[source_page_number].extract_text() or "")
                distinct = [value for value in display_quotes if normalize(value) not in next_text]
                if distinct:
                    quote_candidates = distinct
            quote = quote_candidates[len(sparse_visual_fills) % len(quote_candidates)]
            visual = PdfReader(BytesIO(sparse_visual_overlay(
                float(page.mediabox.width),
                float(page.mediabox.height),
                image_path,
                quote,
                text_floor,
            ))).pages[0]
            page.merge_page(visual)
            sparse_visual_fills.append(source_page_number)
        kept_page_number += 1
        is_n00_part_divider = number == 0 and bool(re.search(r"\bPARTE\s+(?:I|II|III)\b", page_text))
        normalized = normalize(page_text)
        is_opening_question_page = number in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10} and "preguntaprofesional" in normalized and source_word_count < 80
        if is_opening_question_page:
            background = PdfReader(BytesIO(solid_background(
                float(page.mediabox.width),
                float(page.mediabox.height),
                .098,
                .098,
                .098,
            ))).pages[0]
            if preserve_tagged_structure:
                page.merge_page(background, over=False)
            else:
                background.merge_page(page)
                page = background
            bottom_band = PdfReader(BytesIO(solid_bottom_band(
                float(page.mediabox.width),
                float(page.mediabox.height),
                86.0,
                .098,
                .098,
                .098,
            ))).pages[0]
            page.merge_page(bottom_band)
            left_band = PdfReader(BytesIO(solid_left_band(
                float(page.mediabox.width),
                float(page.mediabox.height),
                78.0,
                .098,
                .098,
                .098,
            ))).pages[0]
            page.merge_page(left_band)
        if (number in {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10} and source_page_number == 1) or is_n00_part_divider:
            # Chromium reduce todo el lienzo cuando detecta otras páginas a
            # sangre con desborde editorial. Compensar la portada y todas las
            # portadillas oscuras de N00 devuelve cada fondo a los cuatro
            # bordes del A4 sin alterar la retícula de las páginas de lectura.
            scale = 1.1055
            height = float(page.mediabox.height)
            if number == 1 and source_page_number == 1:
                consolidate_n01_cover_eyebrow(page, reader)
            page.add_transformation(
                Transformation().scale(scale, scale).translate(0, height * (1 - scale))
            )
            if number == 1 and source_page_number == 1:
                scale_cover_pattern_matrices(page, scale)
                extend_n01_cover_pattern_to_trim(page)
            if number == 6 and source_page_number == 1:
                extend_n06_cover_pattern_to_trim(page, scale)
        is_closing_page = source_page_number == len(source_pages)
        light = source_page_number == 1 or is_n00_part_divider or is_opening_question_page or any(q and q in normalized for q in quotes)
        overlay = PdfReader(BytesIO(footer(float(page.mediabox.width), float(page.mediabox.height), kept_page_number, light))).pages[0]
        page.merge_page(overlay)
        if preserve_tagged_structure:
            target_page = page
        else:
            writer.add_page(page)
            target_page = writer.pages[-1]
        # Clean the page only after it belongs to the writer.  pypdf 7 removes
        # support for replacing content on detached reader pages.
        strip_empty_helvetica(target_page, reader)
        if number in {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10} and source_page_number == 1:
            set_image_alt(target_page, manifest.get("cover", {}).get("alt", ""))
        if number == 6 and source_page_number == 2:
            set_image_alt(target_page, "Imagen editorial asociada al contenido de N06")
        if is_closing_page:
            set_image_alt(target_page, manifest.get("closing", {}).get("alt", ""))
    cover_structure_alts = set_structure_figure_alt(
        writer,
        1,
        manifest.get("cover", {}).get("alt", ""),
    )
    if cover_structure_alts < 1:
        raise RuntimeError(
            f"La tapa de {code} no conserva una Figure semántica asociada a la página 1"
        )
    if number == 6:
        set_structure_figure_alt(writer, 2, "Imagen editorial asociada al contenido de N06")
    writer.add_metadata({
        "/Title": manifest["title"],
        "/Author": "Diego Carralbal",
        "/Subject": "Metodología de Sistemas de Información · FCE · UBA",
        "/Keywords": f"METSI, UBA, lectura previa, {manifest['module']}",
    })
    with final.open("wb") as stream:
        writer.write(stream)

    check = PdfReader(str(final))
    texts = [page.extract_text() or "" for page in check.pages]
    all_text = "\n".join(texts)
    declared_source = Path(manifest["source"])
    source_path = declared_source if declared_source.is_absolute() else root / declared_source
    source = source_path.read_text(encoding="utf-8")
    headings = [line.lstrip("#").strip() for line in source.splitlines() if line.startswith("## ")]
    normalized_pdf = normalize(all_text)
    missing = [heading for heading in headings if normalize(heading) not in normalized_pdf]
    fonts = collect_fonts(check)
    forbidden = sorted(font for font in fonts if re.search(r"Arial|Helvetica|Times(?:NewRoman)?", font, re.I))
    a4 = sum(
        abs(float(page.mediabox.width) - 595.276) < 2 and abs(float(page.mediabox.height) - 841.89) < 2
        for page in check.pages
    )
    links = []
    for index, page in enumerate(check.pages, 1):
        for annotation in page.get("/Annots", []):
            obj = annotation.get_object()
            action = obj.get("/A")
            if action and action.get("/URI"):
                links.append((index, str(action.get("/URI"))))
    linkedin_page_set = {page for page, uri in links if "linkedin.com/in/carralbal" in uri}
    external_reference_links = sorted({
        uri for _page, uri in links if "linkedin.com/in/carralbal" not in uri
    })
    closing_page_uris = sorted({uri for page, uri in links if page == len(check.pages)})
    expected_linkedin_pages = len(check.pages)
    closing_manifest = manifest.get("closing", {})
    expected_closing_caption = str(closing_manifest.get("caption", ""))
    expected_closing_alt = str(closing_manifest.get("alt", ""))
    closing_normalized = normalize(texts[-1]) if texts else ""
    closing_caption_present = bool(expected_closing_caption) and normalize(expected_closing_caption) in closing_normalized
    closing_folio_present = bool(texts) and f"{len(check.pages):02d}" in texts[-1].split()
    closing_quote_absent = not any(q and q in closing_normalized for q in quotes)
    closing_image_alts: list[str] = []
    if check.pages:
        resources = check.pages[-1].get("/Resources")
        if resources:
            xobjects = resources.get_object().get("/XObject")
            if xobjects:
                for reference in xobjects.get_object().values():
                    obj = reference.get_object()
                    if obj.get("/Subtype") == "/Image" and obj.get("/Alt"):
                        closing_image_alts.append(str(obj.get("/Alt")))
    closing_alt_present = expected_closing_alt in closing_image_alts
    catalog = check.trailer["/Root"]
    struct_tree_present = bool(catalog.get("/StructTreeRoot"))
    mark_info = catalog.get("/MarkInfo")
    marked_pdf = bool(mark_info and mark_info.get_object().get("/Marked"))
    document_language = str(catalog.get("/Lang", ""))
    result = {
        "number": number,
        "pdf": f"output/{final.name}",
        "pages": len(check.pages),
        "a4_pages": a4,
        "source_words": len(source.split()),
        "pdf_words": len(all_text.split()),
        "missing_headings": missing,
        "forbidden_fonts": forbidden,
        "linkedin_pages": len(linkedin_page_set),
        "expected_linkedin_pages": expected_linkedin_pages,
        "external_reference_links": external_reference_links,
        "closing_page_uris": closing_page_uris,
        "closing_page_text_words": len(texts[-1].split()) if texts else 0,
        "closing_caption_present": closing_caption_present,
        "closing_folio_present": closing_folio_present,
        "closing_quote_absent": closing_quote_absent,
        "closing_image_alts": closing_image_alts,
        "closing_alt_present": closing_alt_present,
        "struct_tree_present": struct_tree_present,
        "marked_pdf": marked_pdf,
        "document_language": document_language,
        "font_inventory": sorted(fonts),
        "removed_blank_source_pages": removed_blank_pages,
        "sparse_visual_fill_source_pages": sparse_visual_fills,
    }
    links_ok = len(external_reference_links) >= 4 if number == 0 else True
    closing_links_ok = closing_page_uris == [LINKEDIN]
    result["status"] = "PASS" if (
        a4 == len(check.pages)
        and not missing
        and not forbidden
        and result["linkedin_pages"] == expected_linkedin_pages
        and closing_links_ok
        and closing_caption_present
        and closing_folio_present
        and closing_quote_absent
        and closing_alt_present
        and struct_tree_present
        and marked_pdf
        and document_language == "es-AR"
        and links_ok
    ) else "FAIL"
    (root / "qa-report.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("start", type=int)
    parser.add_argument("end", type=int, nargs="?")
    args = parser.parse_args()
    register_fonts()
    end = args.end or args.start
    results = [finalize(number) for number in range(args.start, end + 1)]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    if any(result["status"] != "PASS" for result in results):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
