#!/usr/bin/env python3
"""Build the 37 METSI companion chronicles and their static index.

The N documents remain untouched. Each factual article cites its primary source;
every article has its own licensed photo, shared with its website card.
"""

from __future__ import annotations

import html
import importlib.util
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageOps
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[1]
CHRONICLES = ROOT / "site/covers/cronicas"
RELEASE = "narrativas-20261008"
DATA_PATH = ROOT / "pedagogy/cronicas-20261008/articles.py"
NARRATIVES_PATH = ROOT / "pedagogy/cronicas-20261008/narratives.py"
IMAGE_MANIFEST = ROOT / "pedagogy/cronicas-20261008/image-manifest.json"
OUTPUT = CHRONICLES / "pdf"
LOCAL_COMPILATION = ROOT.parent.parent / "output/pdf/METSI-cronicas-N00-N36.pdf"

spec = importlib.util.spec_from_file_location("metsi_chronicles_data", DATA_PATH)
assert spec and spec.loader
data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data)
ARTICLES = data.ARTICLES
story_spec = importlib.util.spec_from_file_location("metsi_chronicle_narratives", NARRATIVES_PATH)
assert story_spec and story_spec.loader
narratives = importlib.util.module_from_spec(story_spec)
story_spec.loader.exec_module(narratives)
for article in ARTICLES:
    article["story"] = narratives.paragraphs(article["id"])
IMAGE_INFO = {item["section_id"]: item for item in
              json.loads(IMAGE_MANIFEST.read_text(encoding="utf-8"))["images"]}

HOME_HTML = (ROOT / "site/index.html").read_text(encoding="utf-8")
READING_URLS = {}
for match in re.finditer(r'<article><a href="([^"]+)" download><img[^>]+alt="Portada de (N\d\d)"', HOME_HTML):
    READING_URLS[match.group(2)] = "https://carralbal.github.io/UBA-metsi/" + match.group(1)
guide = re.search(r'<a href="([^"]+)" download><img[^>]+alt="Portada de N00', HOME_HTML)
if guide:
    READING_URLS["N00"] = "https://carralbal.github.io/UBA-metsi/" + guide.group(1)
for article in ARTICLES:
    article["reading_url"] = READING_URLS[article["id"]]

INK = colors.HexColor("#171716")
PAPER = colors.HexColor("#F7F6F1")
MUTED = colors.HexColor("#555752")
RULE = colors.HexColor("#B9BBB5")
VOLT = colors.HexColor("#CFFF00")

pdfmetrics.registerFont(TTFont("METSI-Didot", "/System/Library/Fonts/Supplemental/Didot.ttc", subfontIndex=0))
pdfmetrics.registerFont(TTFont("METSI-Baskerville", "/System/Library/Fonts/Supplemental/Baskerville.ttc", subfontIndex=0))
pdfmetrics.registerFont(TTFont("METSI-Baskerville-Italic", "/System/Library/Fonts/Supplemental/Baskerville.ttc", subfontIndex=2))
pdfmetrics.registerFont(TTFont("METSI-Avenir", "/System/Library/Fonts/Avenir.ttc", subfontIndex=11))
pdfmetrics.registerFont(TTFont("METSI-Avenir-Medium", "/System/Library/Fonts/Avenir.ttc", subfontIndex=8))


def story_photo(number: str) -> Path:
    """The same exclusive, licensed photo is used by PDF and web card."""
    path = CHRONICLES / "images/story" / f"{number}.jpg"
    if not path.is_file():
        raise FileNotFoundError(f"Missing crónica photo: {path}")
    return path


def photo_caption(number: str) -> str:
    return (f"Foto ilustrativa: {IMAGE_INFO[number]['creator']} / Unsplash. "
            "No documenta el caso narrado.")


def card_photo(number: str) -> Path:
    return story_photo(number)


def build_card_images(articles: list[dict]) -> None:
    """Make web crops of the exact image embedded in each article PDF."""
    destination = CHRONICLES / "images/cards"
    destination.mkdir(parents=True, exist_ok=True)
    for article in articles:
        number = article["id"]
        with Image.open(card_photo(number)) as source:
            crop = ImageOps.fit(
                source.convert("L"), (840, 525), method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.47),
            )
            crop.save(destination / f"{number}.webp", "WEBP", quality=82, method=6)


def draw_photo(c: canvas.Canvas, src: Path, x: float, y: float, w: float, h: float) -> None:
    with Image.open(src) as image:
        iw, ih = image.size
    # Cover-crop portrait or landscape sources with no exposed paper band.
    scale = max(w / iw, h / ih)
    scaled_w = iw * scale
    scaled_h = ih * scale
    c.saveState()
    path = c.beginPath()
    path.rect(x, y, w, h)
    c.clipPath(path, stroke=0, fill=0)
    c.drawImage(str(src), x - (scaled_w - w) * 0.5, y - (scaled_h - h) * 0.5,
                width=scaled_w, height=scaled_h, mask="auto")
    c.restoreState()


def tracked(c: canvas.Canvas, text: str, x: float, y: float, font: str, size: float,
            charspace: float = 0, color=INK) -> None:
    obj = c.beginText(x, y)
    obj.setFont(font, size)
    obj.setCharSpace(charspace)
    obj.setFillColor(color)
    obj.textOut(text)
    # PDF text-state character spacing persists across BT/ET operators.
    # Reset it or later Platypus paragraphs render wider than they measured.
    obj.setCharSpace(0)
    c.drawText(obj)


def paragraph(raw: str, font_size: float = 10.3, italic: bool = False) -> Paragraph:
    style = ParagraphStyle(
        "quote" if italic else "body",
        fontName="METSI-Baskerville-Italic" if italic else "METSI-Baskerville",
        fontSize=font_size,
        leading=font_size * 1.35,
        textColor=INK,
        leftIndent=8 if italic else 0,
    )
    return Paragraph(html.escape(raw), style)


def draw_p(c: canvas.Canvas, p: Paragraph, x: float, y: float, width: float) -> float:
    _, h = p.wrap(width, 1000)
    p.drawOn(c, x, y - h)
    return y - h


def draw_title(c: canvas.Canvas, title: str, x: float, y: float, max_w: float) -> float:
    size = 38.0
    words = title.split()
    while size >= 29:
        lines: list[str] = []
        current = ""
        for word in words:
            trial = f"{current} {word}".strip()
            if current and pdfmetrics.stringWidth(trial, "METSI-Didot", size) > max_w:
                lines.append(current)
                current = word
            else:
                current = trial
        if current:
            lines.append(current)
        if len(lines) <= 2 and all(pdfmetrics.stringWidth(line, "METSI-Didot", size) <= max_w for line in lines):
            break
        size -= 0.8
    if len(lines) > 2:
        raise ValueError(f"Title is too long for two lines: {title}")
    for line in lines:
        tracked(c, line, x, y, "METSI-Didot", size)
        y -= size * 1.08
    return y


def draw_columns(c: canvas.Canvas, story: list[str], top: float, bottom: float,
                 font_size: float = 11.7) -> list[float]:
    margin, gap = 44, 14
    width = (A4[0] - 2 * margin - 2 * gap) / 3
    parts = [(paragraph(s, font_size, s.startswith("«")), s.startswith("«")) for s in story]
    heights = [p.wrap(width, 1000)[1] + 7.0 for p, _ in parts]
    # Keep narrative beats intact while balancing all possible sequential
    # three-column partitions (the N02 pilot contains seven, not six).
    choices = [(first, second) for first in range(1, len(parts)-1)
               for second in range(first+1, len(parts))]
    cuts = min(choices, key=lambda ij: (
        max(sum(heights[:ij[0]]), sum(heights[ij[0]:ij[1]]),
            sum(heights[ij[1]:])),
        max(sum(heights[:ij[0]]), sum(heights[ij[0]:ij[1]]),
            sum(heights[ij[1]:])) -
        min(sum(heights[:ij[0]]), sum(heights[ij[0]:ij[1]]),
            sum(heights[ij[1]:])),
    ))
    groups = [parts[:cuts[0]], parts[cuts[0]:cuts[1]], parts[cuts[1]:]]
    if max(sum(heights[:cuts[0]]), sum(heights[cuts[0]:cuts[1]]),
           sum(heights[cuts[1]:])) > top - bottom:
        raise ValueError(
            f"Narrative needs {max(sum(heights[:cuts[0]]), sum(heights[cuts[0]:cuts[1]]), sum(heights[cuts[1]:])):.0f}pt "
            f"but has {top-bottom:.0f}pt"
        )
    ends = []
    for i, group in enumerate(groups):
        x = margin + i * (width + gap)
        y = top
        for p, italic in group:
            h = p.wrap(width, 1000)[1]
            if y - h < bottom:
                raise ValueError(f"Text overflows column {i+1}: {y-h:.1f} < {bottom}")
            if italic:
                c.setStrokeColor(INK)
                c.setLineWidth(1)
                c.line(x, y, x, y - h)
            y = draw_p(c, p, x, y, width) - 7.0
        ends.append(y)
    return ends


def render_article_legacy(article: dict) -> Path:
    number = article["id"]
    path = OUTPUT / f"{number}.pdf"
    W, H = A4
    M = 44
    c = canvas.Canvas(str(path), pagesize=A4, pageCompression=1)
    c.setTitle(f"METSI | Crónicas {number} | {article['title']}")
    c.setAuthor("METSI - Diego Carralbal")
    c.setSubject(f"Artículo periodístico complementario a la lectura {number}")
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setStrokeColor(RULE)
    c.setLineWidth(.6)
    c.line(M, H-33, W-M, H-33)
    tracked(c, "METSI", M, H-66, "METSI-Didot", 23.5)
    tracked(c, "CRÓNICAS / SISTEMAS DE INFORMACIÓN", M+112, H-60, "METSI-Avenir-Medium", 8.1, 1.05)
    tracked(c, number, W-M-26, H-60, "METSI-Avenir-Medium", 8.1, .9)
    c.setFillColor(VOLT)
    c.rect(M, H-83, 31, 4, fill=1, stroke=0)
    tracked(c, article["kicker"].upper(), M, H-105, "METSI-Avenir-Medium", 7.4, 1.08, MUTED)
    title_bottom = draw_title(c, article["title"], M, H-151, W-2*M)
    deck = Paragraph(html.escape(article["deck"]), ParagraphStyle(
        "deck", fontName="METSI-Baskerville", fontSize=12, leading=15.2, textColor=MUTED))
    deck_bottom = draw_p(c, deck, M, title_bottom+12, W-2*M-22)
    photo_h = 96
    photo_y = deck_bottom - 18 - photo_h
    draw_photo(c, story_photo(number), M, photo_y, W-2*M, photo_h)
    tracked(c, photo_caption(number),
            M, photo_y-13, "METSI-Avenir", 6.75, 0, MUTED)
    c.linkURL(IMAGE_INFO[number]["source_page"],
              (M, photo_y-16, W-M, photo_y-6), relative=0)
    font_size = 11.2
    while True:
        try:
            ends = draw_columns(c, article["story"], photo_y-30, 92, font_size)
            break
        except ValueError:
            # Avoid drawing a partial failed layout by recreating the page.
            c = canvas.Canvas(str(path), pagesize=A4, pageCompression=1)
            c.setTitle(f"METSI | Crónicas {number} | {article['title']}")
            c.setAuthor("METSI - Diego Carralbal")
            c.setFillColor(PAPER)
            c.rect(0, 0, W, H, fill=1, stroke=0)
            c.setStrokeColor(RULE)
            c.line(M, H-33, W-M, H-33)
            tracked(c, "METSI", M, H-66, "METSI-Didot", 23.5)
            tracked(c, "CRÓNICAS / SISTEMAS DE INFORMACIÓN", M+112, H-60, "METSI-Avenir-Medium", 8.1, 1.05)
            tracked(c, number, W-M-26, H-60, "METSI-Avenir-Medium", 8.1, .9)
            c.setFillColor(VOLT)
            c.rect(M, H-83, 31, 4, fill=1, stroke=0)
            tracked(c, article["kicker"].upper(), M, H-105, "METSI-Avenir-Medium", 7.4, 1.08, MUTED)
            title_bottom = draw_title(c, article["title"], M, H-151, W-2*M)
            deck_bottom = draw_p(c, deck, M, title_bottom+12, W-2*M-22)
            photo_y = deck_bottom-18-photo_h
            draw_photo(c, story_photo(number), M, photo_y, W-2*M, photo_h)
            tracked(c, photo_caption(number),
                    M, photo_y-13, "METSI-Avenir", 6.75, 0, MUTED)
            c.linkURL(IMAGE_INFO[number]["source_page"],
                      (M, photo_y-16, W-M, photo_y-6), relative=0)
            font_size -= .2
            if font_size < 10.1:
                raise ValueError(f"{number} requires copy edit to fit one page")
    c.setStrokeColor(RULE)
    c.line(M, 81, W-M, 81)
    tracked(c, "FUENTES", M, 65, "METSI-Avenir-Medium", 6.6, 1.05)
    links = [(article["source_label"], article["source_url"]),
             *article.get("extra_sources", []),
             (f"Lectura {number}", article["reading_url"])]
    sx = M + 47
    for i, (label, url) in enumerate(links):
        label_width = pdfmetrics.stringWidth(label, "METSI-Avenir", 6.5)
        tracked(c, label, sx, 65, "METSI-Avenir", 6.5, 0, MUTED)
        c.linkURL(url, (sx, 62, sx+label_width, 74), relative=0)
        sx += label_width + 8
        if i < len(links)-1:
            tracked(c, "·", sx-6, 65, "METSI-Avenir", 6.5, 0, MUTED)
    tracked(c, article.get("quote_note", "Cita de la fuente indicada; fotografía conceptual."),
            M, 50, "METSI-Avenir", 6.3, 0, MUTED)
    right = "DIEGO CARRALBAL · METSI · FCE UBA"
    tracked(c, right, W-M-pdfmetrics.stringWidth(right, "METSI-Avenir-Medium", 6),
            50, "METSI-Avenir-Medium", 6, .25, MUTED)
    c.showPage()
    c.save()
    return path


def draw_second_page_columns(c: canvas.Canvas, story: list[str], top: float,
                             bottom: float) -> list[float]:
    """Balance intact middle paragraphs in two readable editorial columns."""
    margin, gap = 44, 25
    width = (A4[0] - 2 * margin - gap) / 2
    parts = [paragraph(text, 12.6) for text in story]
    heights = [p.wrap(width, 1000)[1] + 13 for p in parts]
    cuts = range(1, len(parts))
    cut = min(cuts, key=lambda k: max(sum(heights[:k]), sum(heights[k:])))
    if max(sum(heights[:cut]), sum(heights[cut:])) > top - bottom:
        raise ValueError(
            f"Second-page text needs {max(sum(heights[:cut]), sum(heights[cut:])):.0f}pt "
            f"but has {top-bottom:.0f}pt"
        )
    ends = []
    for col, group in enumerate((parts[:cut], parts[cut:])):
        x = margin + col * (width + gap)
        y = top
        for p in group:
            y = draw_p(c, p, x, y, width) - 13
        ends.append(y)
    return ends


def render_article(article: dict) -> Path:
    """Two-page magazine article; story and photo are not reduced to a telegram."""
    number = article["id"]
    story = article["story"]
    if len(story) < 5:
        raise ValueError(f"{number}: at least five narrative beats required")
    path = OUTPUT / f"{number}.pdf"
    W, H = A4
    M = 44
    c = canvas.Canvas(str(path), pagesize=A4, pageCompression=1)
    c.setTitle(f"METSI | Crónicas {number} | {article['title']}")
    c.setAuthor("METSI - Diego Carralbal")
    c.setSubject(f"Artículo periodístico complementario a la lectura {number}")

    # Page 1 keeps the approved typographic/photo grammar, now with breathing
    # room for the full journalistic opening rather than compressed columns.
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setStrokeColor(RULE)
    c.setLineWidth(.6)
    c.line(M, H-33, W-M, H-33)
    tracked(c, "METSI", M, H-66, "METSI-Didot", 23.5)
    tracked(c, "CRÓNICAS / SISTEMAS DE INFORMACIÓN", M+112, H-60,
            "METSI-Avenir-Medium", 8.1, 1.05)
    tracked(c, number, W-M-26, H-60, "METSI-Avenir-Medium", 8.1, .9)
    c.setFillColor(VOLT)
    c.rect(M, H-83, 31, 4, fill=1, stroke=0)
    tracked(c, article["kicker"].upper(), M, H-105,
            "METSI-Avenir-Medium", 7.4, 1.08, MUTED)
    title_bottom = draw_title(c, article["title"], M, H-151, W-2*M)
    deck = Paragraph(html.escape(article["deck"]), ParagraphStyle(
        "deck", fontName="METSI-Baskerville", fontSize=12, leading=15.2,
        textColor=MUTED))
    deck_bottom = draw_p(c, deck, M, title_bottom+12, W-2*M-22)
    photo_h = 120
    photo_y = deck_bottom - 17 - photo_h
    draw_photo(c, story_photo(number), M, photo_y, W-2*M, photo_h)
    tracked(c, photo_caption(number), M, photo_y-13,
            "METSI-Avenir", 6.75, 0, MUTED)
    c.linkURL(IMAGE_INFO[number]["source_page"],
              (M, photo_y-16, W-M, photo_y-6), relative=0)
    draw_columns(c, story[:3], photo_y-31, 98, 11.0)
    c.setStrokeColor(RULE)
    c.line(M, 81, W-M, 81)
    tracked(c, "METSI · CRÓNICAS · " + number, M, 57,
            "METSI-Avenir-Medium", 7, .4, MUTED)
    tracked(c, "SIGUE EN 02", W-M-72, 57,
            "METSI-Avenir-Medium", 7, .4, MUTED)
    c.showPage()

    # Page 2 carries the analysis and reserves the ending for a generous,
    # un-repeated final beat. The source rail remains linked and legible.
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setStrokeColor(RULE)
    c.line(M, H-33, W-M, H-33)
    tracked(c, "METSI", M, H-66, "METSI-Didot", 23.5)
    tracked(c, f"{number} / CONTINUACIÓN", W-M-122, H-60,
            "METSI-Avenir-Medium", 8.1, 1, MUTED)
    c.setFillColor(VOLT)
    c.rect(M, H-84, 31, 4, fill=1, stroke=0)
    tracked(c, article["kicker"].upper(), M, H-109,
            "METSI-Avenir-Medium", 7.4, 1.08, MUTED)
    ends = draw_second_page_columns(c, story[3:-1], H-130, 295)
    callout_top = min(385, min(ends)-28)
    c.setStrokeColor(RULE)
    c.line(M, callout_top+12, W-M, callout_top+12)
    c.setFillColor(VOLT)
    c.rect(M, callout_top-1, 5, 36, fill=1, stroke=0)
    ending_size = 20
    while ending_size >= 15:
        ending = Paragraph(html.escape(story[-1]), ParagraphStyle(
            "closing", fontName="METSI-Baskerville-Italic",
            fontSize=ending_size, leading=ending_size*1.23,
            textColor=INK, leftIndent=18))
        _, ending_h = ending.wrap(W-2*M-8, 1000)
        if callout_top-ending_h >= 116:
            break
        ending_size -= .5
    if ending_size < 15:
        raise ValueError(f"{number}: final beat needs editorial copy edit")
    ending.drawOn(c, M+8, callout_top-ending_h)

    c.setStrokeColor(RULE)
    c.line(M, 94, W-M, 94)
    tracked(c, "FUENTES", M, 77, "METSI-Avenir-Medium", 6.6, 1.05)
    links = [(article["source_label"], article["source_url"]),
             *article.get("extra_sources", []),
             (f"Lectura {number}", article["reading_url"])]
    sx = M + 47
    for i, (label, url) in enumerate(links):
        label_width = pdfmetrics.stringWidth(label, "METSI-Avenir", 6.5)
        tracked(c, label, sx, 77, "METSI-Avenir", 6.5, 0, MUTED)
        c.linkURL(url, (sx, 74, sx+label_width, 86), relative=0)
        sx += label_width + 8
        if i < len(links)-1:
            tracked(c, "·", sx-6, 77, "METSI-Avenir", 6.5, 0, MUTED)
    if sx > W-M+2:
        raise ValueError(f"{number}: source rail exceeds page width")
    tracked(c, "Fotografía conceptual; no documenta a las personas del caso.",
            M, 56, "METSI-Avenir", 6.3, 0, MUTED)
    right = "DIEGO CARRALBAL · METSI · FCE UBA"
    tracked(c, right, W-M-pdfmetrics.stringWidth(right, "METSI-Avenir-Medium", 6),
            56, "METSI-Avenir-Medium", 6, .25, MUTED)
    c.showPage()
    c.save()
    return path


def static_index(articles: list[dict]) -> None:
    build_card_images(articles)
    cards = []
    groups = [
        ("Antes de empezar", range(0, 1)),
        ("A · Comprender", range(1, 5)),
        ("B · Investigar", range(5, 11)),
        ("C · Representar", range(11, 17)),
        ("D · Cambiar", range(17, 22)),
        ("E · Probar y entregar", range(22, 26)),
        ("F · Sostener", range(26, 31)),
        ("G · Decidir sobre IA", range(31, 34)),
        ("H · Integrar y aprender", range(34, 37)),
    ]
    by_id = {a["id"]: a for a in articles}
    for label, numbers in groups:
        cards.append(f'<section class="group"><h2>{html.escape(label)}</h2><div class="grid">')
        for n in numbers:
            a = by_id[f"N{n:02d}"]
            number = a["id"]
            featured = " feature" if number == "N00" else ""
            loading = "eager" if number == "N00" else "lazy"
            cards.append(
                f'<article class="card{featured}">'
                f'<a class="card-media" href="pdf/{number}.pdf?v={RELEASE}" target="_blank" rel="noopener" '
                f'aria-label="Abrir crónica {number}: {html.escape(a["title"], quote=True)}">'
                f'<img src="images/cards/{number}.webp?v={RELEASE}" alt="Imagen editorial ilustrativa de la crónica {number}" '
                f'width="840" height="525" loading="{loading}" decoding="async"></a>'
                f'<div class="card-copy"><span>{number} · {html.escape(a["region"])}</span>'
                f'<h3>{html.escape(a["title"])}</h3><p>{html.escape(a["deck"])}</p>'
                f'<div class="actions"><a href="pdf/{number}.pdf?v={RELEASE}" target="_blank" rel="noopener">Leer la crónica ↗</a>'
                f'<a href="{html.escape(a["reading_url"], quote=True)}" target="_blank" rel="noopener">Lectura {number} ↗</a></div></div></article>'
            )
        cards.append("</div></section>")
    page = '''<!doctype html><html lang="es-AR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Crónicas METSI · 37 historias para pensar los sistemas</title><meta name="description" content="37 crónicas periodísticas: casos reales, preguntas incómodas y lecturas METSI para entender mejor los sistemas de información.">
<link rel="stylesheet" href="style.css?v=cards-20261008"></head><body><header class="top"><a class="brand" href="../../">METSI</a><a href="../../#biblioteca">Volver a la colección ↗</a></header>
<main><div class="hero"><p class="eyebrow"><i></i> UNA SERIE EDITORIAL COMPLEMENTARIA</p><h1>Los sistemas también<br>son historias de personas.</h1>
<p class="lead">Una crónica por cada lectura N00–N36. Casos reales, preguntas incómodas y una idea central para seguir pensando. Son una puerta de entrada: no reemplazan las lecturas.</p>
<p class="method">Las imágenes son ilustrativas y están en blanco y negro. Los hechos y las citas remiten a fuentes enlazadas en cada PDF. La mayoría de los casos procede de Argentina y América Latina.</p></div>
''' + "\n".join(cards) + '''</main><footer>METSI · Diego Carralbal · FCE UBA <a href="../../">Volver al sitio</a></footer></body></html>'''
    (CHRONICLES / "index.html").write_text(page, encoding="utf-8")


def main() -> None:
    assert len(ARTICLES) == 37, f"Expected 37 articles, got {len(ARTICLES)}"
    assert [a["id"] for a in ARTICLES] == [f"N{i:02d}" for i in range(37)]
    assert sum(a["region"] in {"Argentina", "América Latina"} for a in ARTICLES) >= 26
    if sys.argv[1:] == ["--index-only"]:
        static_index(ARTICLES)
        print(f"Built {len(ARTICLES)} indexed cards and image previews; PDFs unchanged")
        return
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for a in ARTICLES:
        render_article(a)
    combined = PdfWriter()
    for i in range(37):
        pdf = OUTPUT / f"N{i:02d}.pdf"
        reader = PdfReader(str(pdf))
        assert 1 <= len(reader.pages) <= 2, (pdf, len(reader.pages))
        combined.append(reader)
    LOCAL_COMPILATION.parent.mkdir(parents=True, exist_ok=True)
    with LOCAL_COMPILATION.open("wb") as f:
        combined.write(f)
    static_index(ARTICLES)
    (CHRONICLES / "articles.json").write_text(
        json.dumps([{k: v for k, v in a.items() if k != "story"} for a in ARTICLES],
                   ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Built {len(ARTICLES)} PDFs + collection + static index")


if __name__ == "__main__":
    main()
