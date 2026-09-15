#!/usr/bin/env python3
"""Build the public METSI 2026 program PDF from its canonical Markdown."""

from __future__ import annotations

import re
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "programa" / "programa-metsi-2026.md"
OUTPUT = ROOT / "site" / "programa" / "programa-metsi-2026.pdf"
VOLT = colors.HexColor("#CFFF00")
INK = colors.HexColor("#171817")
MUTED = colors.HexColor("#62655F")
PAPER = colors.HexColor("#F1F0EA")
LINE = colors.HexColor("#B9BCB4")


def clean_inline(text: str) -> str:
    text = text.replace("–", "-").replace("—", "-").replace("‑", "-")
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
    text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)
    return text


class ProgramDoc(BaseDocTemplate):
    def __init__(self, filename: str) -> None:
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=22 * mm,
            rightMargin=22 * mm,
            topMargin=25 * mm,
            bottomMargin=20 * mm,
            title="Programa académico 2026 - METSI",
            author="Diego Carralbal",
            subject="Metodología de los Sistemas de Información, FCE UBA",
        )
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="body")
        self.addPageTemplates(PageTemplate(id="program", frames=[frame], onPage=self.decorate))

    def decorate(self, canvas, doc) -> None:
        canvas.saveState()
        width, height = A4
        if doc.page == 1:
            canvas.setFillColor(INK)
            canvas.rect(0, 0, width, height, stroke=0, fill=1)
            canvas.setFillColor(VOLT)
            canvas.rect(22 * mm, height - 28 * mm, 28 * mm, 3 * mm, stroke=0, fill=1)
        else:
            canvas.setStrokeColor(LINE)
            canvas.setLineWidth(.5)
            canvas.line(22 * mm, height - 15 * mm, width - 22 * mm, height - 15 * mm)
            canvas.setFont("Helvetica", 7)
            canvas.setFillColor(MUTED)
            canvas.drawString(22 * mm, height - 12 * mm, "METSI · PROGRAMA ACADÉMICO 2026")
        canvas.setStrokeColor(LINE if doc.page != 1 else colors.HexColor("#767A72"))
        canvas.line(22 * mm, 14 * mm, width - 22 * mm, 14 * mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#D7D8D2") if doc.page == 1 else MUTED)
        canvas.drawString(22 * mm, 9.5 * mm, f"{doc.page:02d}")
        canvas.drawRightString(width - 22 * mm, 9.5 * mm, "Diego Carralbal, 2026 · FCE UBA")
        canvas.restoreState()


def styles():
    base = getSampleStyleSheet()
    return {
        "cover_kicker": ParagraphStyle("cover_kicker", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=VOLT, spaceAfter=16, tracking=1.8),
        "cover_title": ParagraphStyle("cover_title", parent=base["Title"], fontName="Times-Roman", fontSize=40, leading=39, textColor=colors.HexColor("#FBFAF5"), spaceAfter=15, alignment=TA_LEFT),
        "cover_deck": ParagraphStyle("cover_deck", parent=base["Normal"], fontName="Helvetica", fontSize=12, leading=18, textColor=colors.HexColor("#D7D8D2"), spaceAfter=18),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontName="Times-Roman", fontSize=25, leading=27, textColor=INK, spaceBefore=5, spaceAfter=11),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName="Times-Roman", fontSize=18, leading=20, textColor=INK, spaceBefore=13, spaceAfter=6),
        "h3": ParagraphStyle("h3", parent=base["Heading3"], fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=INK, spaceBefore=11, spaceAfter=5),
        "body": ParagraphStyle("body", parent=base["BodyText"], fontName="Times-Roman", fontSize=9.6, leading=13.4, textColor=INK, spaceAfter=5.5),
        "bullet": ParagraphStyle("bullet", parent=base["BodyText"], fontName="Times-Roman", fontSize=9.3, leading=12.8, textColor=INK, leftIndent=12, firstLineIndent=-8, spaceAfter=4),
        "small": ParagraphStyle("small", parent=base["BodyText"], fontName="Helvetica", fontSize=8, leading=11, textColor=MUTED, spaceAfter=5),
    }


def cover_story(s):
    metadata = [
        ["ASIGNATURA", "Metodología de los Sistemas de Información"],
        ["CÓDIGO", "658"],
        ["CARRERA", "Licenciatura en Sistemas de Información de las Organizaciones"],
        ["CICLO", "Formación Profesional"],
        ["CARGA", "108 horas · 6 horas semanales"],
        ["CORRELATIVA", "Ingeniería de Software"],
    ]
    table = Table(metadata, colWidths=[31 * mm, 102 * mm], hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), INK),
        ("TEXTCOLOR", (0, 0), (0, -1), VOLT),
        ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#FBFAF5")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Times-Roman"),
        ("FONTSIZE", (0, 0), (0, -1), 7),
        ("FONTSIZE", (1, 0), (1, -1), 10),
        ("LEADING", (0, 0), (-1, -1), 13),
        ("LINEBELOW", (0, 0), (-1, -1), .35, colors.HexColor("#62655F")),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return [
        Spacer(1, 38 * mm),
        Paragraph("FCE · UBA · LICENCIATURA EN SISTEMAS", s["cover_kicker"]),
        Paragraph("Programa académico<br/>2026", s["cover_title"]),
        Paragraph("Metodología de los Sistemas de Información", s["cover_deck"]),
        Spacer(1, 8 * mm),
        table,
        Spacer(1, 16 * mm),
        Paragraph("Versión propuesta para revisión de cátedra y evaluación institucional.", s["cover_deck"]),
    ]


def markdown_story(text: str, s):
    story = []
    in_list = False
    for raw in text.splitlines()[1:]:
        line = raw.strip()
        if not line:
            if in_list:
                story.append(Spacer(1, 2 * mm))
                in_list = False
            continue
        if line.startswith("### "):
            story.append(Paragraph(clean_inline(line[4:]), s["h3"]))
        elif line.startswith("## "):
            story.append(Paragraph(clean_inline(line[3:]), s["h1"]))
        elif re.match(r"^\d+\.\s", line):
            number, item = line.split(". ", 1)
            story.append(Paragraph(f"<b>{number}.</b> {clean_inline(item)}", s["bullet"]))
            in_list = True
        elif line.startswith("- "):
            story.append(Paragraph(f"• {clean_inline(line[2:])}", s["bullet"]))
            in_list = True
        else:
            style = s["small"] if line.startswith("Estas condiciones fueron") else s["body"]
            story.append(Paragraph(clean_inline(line), style))
    return story


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    s = styles()
    text = SOURCE.read_text(encoding="utf-8")
    story = cover_story(s)
    story.append(PageBreak())
    story.extend(markdown_story(text, s))
    ProgramDoc(str(OUTPUT)).build(story)
    reader = PdfReader(str(OUTPUT), strict=False)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    writer._info = None
    writer._ID = None
    writer.root_object.pop(NameObject("/Metadata"), None)
    sanitized = OUTPUT.with_suffix(".sanitized.pdf")
    with sanitized.open("wb") as stream:
        writer.write(stream)
    sanitized.replace(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
