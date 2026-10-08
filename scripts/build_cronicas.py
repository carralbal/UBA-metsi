#!/usr/bin/env python3
"""Build the 37 one-page METSI companion chronicles and their static index.

The N documents remain untouched. Each factual article cites its primary source;
the cover-source photographs are illustrative, never evidence of the reported case.
"""

from __future__ import annotations

import html
import importlib.util
import json
import re
import shutil
from pathlib import Path

from PIL import Image
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
DATA_PATH = ROOT / "pedagogy/cronicas-20261008/articles.py"
OUTPUT = CHRONICLES / "pdf"
LOCAL_COMPILATION = ROOT.parent.parent / "output/pdf/METSI-cronicas-N00-N36.pdf"

spec = importlib.util.spec_from_file_location("metsi_chronicles_data", DATA_PATH)
assert spec and spec.loader
data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data)
ARTICLES = data.ARTICLES

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


def cover_photo(number: str) -> Path:
    """Use the approved original monochrome image, without the cover's text."""
    if number == "N00":
        return CHRONICLES / "images/N00-bw.png"
    if number in {"N09", "N10"}:
        version = "N09-v12-final" if number == "N09" else "N10-v10-final"
        return ROOT / version / "assets/editorial-02.png"
    matches = sorted(ROOT.glob(f"{number}-v*-*/assets/cover-source-premium-bw-v*.png"))
    if not matches:
        raise FileNotFoundError(f"No approved source photograph for {number}")
    # Version numbers are chronological, unlike lexicographic ordering.
    return max(matches, key=lambda p: (int(re.search(r"-v(\d+)-", p.parts[-3]).group(1)),
                                       int(re.search(r"-v(\d+)\.png$", p.name).group(1))))


def draw_photo(c: canvas.Canvas, src: Path, x: float, y: float, w: float, h: float) -> None:
    with Image.open(src) as image:
        iw, ih = image.size
    # The source artwork is portrait. A wide, short editorial crop avoids resizing
    # and never imposes a coloured effect over the image.
    scale = w / iw
    scaled_h = ih * scale
    c.saveState()
    path = c.beginPath()
    path.rect(x, y, w, h)
    c.clipPath(path, stroke=0, fill=0)
    c.drawImage(str(src), x, y - (scaled_h - h) * 0.53, width=w, height=scaled_h, mask="auto")
    c.restoreState()


def tracked(c: canvas.Canvas, text: str, x: float, y: float, font: str, size: float,
            charspace: float = 0, color=INK) -> None:
    obj = c.beginText(x, y)
    obj.setFont(font, size)
    obj.setCharSpace(charspace)
    obj.setFillColor(color)
    obj.textOut(text)
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
    # Each paragraph is an editorial beat. Six beats read cleanly as two per
    # column; the shorter five-beat piece is split at its least uneven break.
    if len(parts) == 6:
        cuts = (2, 4)
    else:
        choices = ((1, 3), (2, 3), (2, 4))
        cuts = min(choices, key=lambda ij: max(sum(heights[:ij[0]]),
                      sum(heights[ij[0]:ij[1]]), sum(heights[ij[1]:])))
    groups = [parts[:cuts[0]], parts[cuts[0]:cuts[1]], parts[cuts[1]:]]
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


def render_article(article: dict) -> Path:
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
    photo_h = 140
    photo_y = deck_bottom - 18 - photo_h
    draw_photo(c, cover_photo(number), M, photo_y, W-2*M, photo_h)
    tracked(c, "Imagen editorial ilustrativa · Colección METSI. No documenta el caso narrado.",
            M, photo_y-13, "METSI-Avenir", 6.75, 0, MUTED)
    font_size = 11.7
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
            draw_photo(c, cover_photo(number), M, photo_y, W-2*M, photo_h)
            tracked(c, "Imagen editorial ilustrativa · Colección METSI. No documenta el caso narrado.",
                    M, photo_y-13, "METSI-Avenir", 6.75, 0, MUTED)
            font_size -= .2
            if font_size < 9.1:
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


def static_index(articles: list[dict]) -> None:
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
            cards.append(
                f'<article class="card"><span>{a["id"]} · {html.escape(a["region"])}</span>'
                f'<h3>{html.escape(a["title"])}</h3><p>{html.escape(a["deck"])}</p>'
                f'<div class="actions"><a href="pdf/{a["id"]}.pdf" target="_blank" rel="noopener">Leer la crónica ↗</a>'
                f'<a href="{html.escape(a["reading_url"], quote=True)}" target="_blank" rel="noopener">Lectura {a["id"]} ↗</a></div></article>'
            )
        cards.append("</div></section>")
    page = '''<!doctype html><html lang="es-AR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Crónicas METSI · 37 historias para pensar los sistemas</title><meta name="description" content="37 artículos de una página: casos reales, preguntas incómodas y lecturas METSI para entender mejor los sistemas de información.">
<link rel="stylesheet" href="style.css"></head><body><header class="top"><a class="brand" href="../../">METSI</a><a href="../../#biblioteca">Volver a la colección ↗</a></header>
<main><div class="hero"><p class="eyebrow"><i></i> UNA SERIE EDITORIAL COMPLEMENTARIA</p><h1>Los sistemas también<br>son historias de personas.</h1>
<p class="lead">Una crónica por cada lectura N00–N36. Casos reales, preguntas incómodas y una idea central para seguir pensando. Son una puerta de entrada: no reemplazan las lecturas.</p>
<p class="method">Las imágenes son ilustrativas y están en blanco y negro. Los hechos y las citas remiten a fuentes enlazadas en cada PDF. La mayoría de los casos procede de Argentina y América Latina.</p></div>
''' + "\n".join(cards) + '''</main><footer>METSI · Diego Carralbal · FCE UBA <a href="../../">Volver al sitio</a></footer></body></html>'''
    (CHRONICLES / "index.html").write_text(page, encoding="utf-8")


def main() -> None:
    assert len(ARTICLES) == 37, f"Expected 37 articles, got {len(ARTICLES)}"
    assert [a["id"] for a in ARTICLES] == [f"N{i:02d}" for i in range(37)]
    assert sum(a["region"] in {"Argentina", "América Latina"} for a in ARTICLES) >= 26
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for a in ARTICLES:
        if "pilot_pdf" in a:
            source = ROOT.parent.parent / a["pilot_pdf"]
            target = OUTPUT / f"{a['id']}.pdf"
            if source.exists():
                shutil.copy2(source, target)
            elif not target.exists():
                raise FileNotFoundError(f"Pilot PDF missing: {a['id']}")
        else:
            render_article(a)
    combined = PdfWriter()
    for i in range(37):
        pdf = OUTPUT / f"N{i:02d}.pdf"
        reader = PdfReader(str(pdf))
        assert len(reader.pages) == 1, (pdf, len(reader.pages))
        combined.append(reader)
    LOCAL_COMPILATION.parent.mkdir(parents=True, exist_ok=True)
    with LOCAL_COMPILATION.open("wb") as f:
        combined.write(f)
    static_index(ARTICLES)
    (CHRONICLES / "articles.json").write_text(
        json.dumps([{k: v for k, v in a.items() if k != "story"} for a in ARTICLES],
                   ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Built {len(ARTICLES)} one-page PDFs + collection + static index")


if __name__ == "__main__":
    main()
