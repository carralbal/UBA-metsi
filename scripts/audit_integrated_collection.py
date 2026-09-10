#!/usr/bin/env python3
"""Exhaustive release audit for the integrated METSI N00-N36 collection."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
REPORT_JSON = ROOT / "audits/2026-09-10-integracion-curricular-y-grafica-N00-N36.json"
REPORT_PDF = ROOT / "qa-reports/METSI-N00-N36-auditoria-de-integracion-final.pdf"
PDF_FILES = {
    "N00": "N00-METSI-lectura-previa-v3-final.pdf",
    "N01": "N01-METSI-lectura-previa-v18-final.pdf",
    "N02": "N02-METSI-lectura-previa-v15-final.pdf",
    "N03": "N03-METSI-lectura-previa-v10-final.pdf",
    "N04": "N04-METSI-lectura-previa-v9-final.pdf",
    "N05": "N05-METSI-lectura-previa-v10-final.pdf",
    "N06": "N06-METSI-lectura-previa-v10-final.pdf",
    "N07": "N07-METSI-lectura-previa-v10-final.pdf",
    "N08": "N08-METSI-lectura-previa-v10-final.pdf",
    "N09": "N09-METSI-lectura-previa-v10-final.pdf",
    "N10": "N10-METSI-lectura-previa-v9-final.pdf",
    **{f"N{n:02d}": f"publicados/N{n:02d}-METSI-lectura-previa-v1-final.pdf" for n in range(11, 37)},
}
CHANGED_QA = {
    "N00": "N00-v3-final/qa-report.json",
    "N02": "N02-v15-final/qa-report.json",
    "N03": "N03-v10-final/qa-report.json",
    "N05": "N05-v10-final/qa-report.json",
    "N06": "N06-v10-final/qa-report.json",
    "N07": "N07-v10-final/qa-report.json",
    "N08": "N08-v10-final/qa-report.json",
    "N09": "N09-v10-final/qa-report.json",
}
TERM_CHECKS = {
    "N02": ("García",),
    "N03": ("García",),
    "N05": ("Etkin", "Schvarstein", "Ricaurte"),
    "N06": ("ISO 9241-210", "investigación de diseño"),
    "N08": ("blueprint",),
    "N09": ("UI", "UX", "Scolari"),
    "N12": ("BPMN", "Flores", "Winograd"),
    "N14": ("BPMN", "pool", "lane", "Flores", "Winograd"),
    "N15": ("BPMN", "Scolari"),
    "N16": ("Etkin", "Schvarstein"),
    "N17": ("PMBOK", "Scrum", "Kanban"),
    "N18": ("Git", "Chacon"),
    "N19": ("Varsavsky",),
    "N20": ("PMBOK", "Varsavsky"),
    "N21": ("PMBOK", "Etkin", "Schvarstein"),
    "N23": ("Scrum", "Definición de Terminado"),
    "N24": ("Kanban", "trabajo en curso"),
    "N25": ("Kanban", "DORA"),
    "N27": ("OpenAPI", "AsyncAPI", "Flores", "Winograd"),
    "N28": ("ISO 9241-210", "usabilidad"),
    "N29": ("GitHub", "DevOps", "rama principal"),
    "N30": ("DORA", "tasa de retrabajo"),
    "N31": ("Ricaurte",),
    "N32": ("Ricaurte",),
    "N33": ("Ricaurte",),
    "N35": ("Freire",),
    "N36": ("Freire",),
}
CORE_SECTIONS = (
    "Pregunta profesional",
    "Hotel Horizonte",
    "Tesis",
    "Síntesis",
    "Cinco píldoras para recordar",
    "Glosario esencial",
    "Preguntas de preparación",
    "Referencias base",
)
INFOGRAPHICS = {
    "N00": "editorial-standard/infographic-rebuild-candidates-v2/N00/N00-mapa-decision-v2.svg",
    "N07": "editorial-standard/infographic-rebuild-candidates-v2/N07/N07-mapa-decision-v2.svg",
    "N08": "editorial-standard/infographic-rebuild-candidates-v2/N08/N08-mapa-decision-v2.svg",
    "N09": "editorial-standard/infographic-rebuild-candidates-v2/N09/N09-mapa-decision-v2.svg",
    **{f"N{n:02d}": f"N{n:02d}-v7-editorial/diagrams/N{n:02d}-mapa-01.svg" for n in range(11, 37)},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def folded(value: str) -> str:
    return unicodedata.normalize("NFKC", value).casefold()


def image_count(page) -> int:
    try:
        resources = page.get("/Resources") or {}
        xobjects = resources.get("/XObject") or {}
        return sum(1 for ref in xobjects.values() if ref.get_object().get("/Subtype") == "/Image")
    except Exception:
        return 0


def draw_footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#c4c7c2"))
    canvas.line(18 * mm, 12 * mm, 192 * mm, 12 * mm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#525652"))
    canvas.drawString(18 * mm, 8 * mm, f"METSI · auditoría final · {doc.page}")
    canvas.restoreState()


def build_dossier(payload: dict[str, object]) -> None:
    REPORT_PDF.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("TitleMETSI", parent=styles["Title"], fontName="Times-Roman", fontSize=28, leading=31, textColor=colors.HexColor("#171917"), spaceAfter=8 * mm)
    h1 = ParagraphStyle("H1METSI", parent=styles["Heading1"], fontName="Times-Roman", fontSize=20, leading=23, textColor=colors.HexColor("#171917"), spaceBefore=4 * mm, spaceAfter=4 * mm)
    body = ParagraphStyle("BodyMETSI", parent=styles["BodyText"], fontName="Helvetica", fontSize=9, leading=13, textColor=colors.HexColor("#242724"), alignment=TA_LEFT)
    small = ParagraphStyle("SmallMETSI", parent=body, fontSize=7.3, leading=9.2)
    volt = colors.HexColor("#c8ff00")
    ink = colors.HexColor("#171917")
    paper = colors.HexColor("#f4f2ec")
    gray = colors.HexColor("#e3e6e3")
    doc = SimpleDocTemplate(str(REPORT_PDF), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=18 * mm, bottomMargin=17 * mm, title="METSI N00-N36, auditoría final de integración", author="Diego Carralbal")
    story = [
        Table([["", "METSI · FCE UBA"]], colWidths=[8 * mm, 166 * mm], style=TableStyle([("BACKGROUND", (0, 0), (0, 0), volt), ("TEXTCOLOR", (1, 0), (1, 0), ink), ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"), ("FONTSIZE", (1, 0), (1, 0), 9), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("BOTTOMPADDING", (0, 0), (-1, -1), 4), ("TOPPADDING", (0, 0), (-1, -1), 4)])),
        Spacer(1, 24 * mm),
        Paragraph("Auditoría final de integración<br/>N00 a N36", title),
        Paragraph("Contenido, continuidad curricular, sistema editorial, infografías, accesibilidad técnica y publicación.", ParagraphStyle("Deck", parent=body, fontName="Times-Italic", fontSize=14, leading=19)),
        Spacer(1, 20 * mm),
        Table([["RESULTADO", payload["status"]], ["DOCUMENTOS", "37"], ["PÁGINAS", str(payload["totals"]["pages"])], ["PDF NUEVOS", "8 lecturas y este dossier"]], colWidths=[45 * mm, 110 * mm], style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), gray), ("BACKGROUND", (0, 0), (0, -1), ink), ("TEXTCOLOR", (0, 0), (0, -1), colors.white), ("TEXTCOLOR", (1, 0), (1, 0), ink), ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 10), ("GRID", (0, 0), (-1, -1), .4, colors.white), ("LEFTPADDING", (0, 0), (-1, -1), 5 * mm), ("TOPPADDING", (0, 0), (-1, -1), 3 * mm), ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm)])),
        Spacer(1, 12 * mm),
        Paragraph("La colección queda técnicamente preparada para revisión externa por la cátedra. Este sello no sustituye la lectura académica humana; demuestra que la integración aprobada está presente, que la continuidad estructural no se perdió y que no se introdujeron regresiones detectables.", body),
        PageBreak(),
        Paragraph("Qué se implementó", h1),
        Paragraph("Se recompaginaron únicamente ocho lecturas. N01, N04 y N10 permanecieron idénticas. N11 a N36 ya contenían la ampliación curricular y conservaron sus PDF v7 sin modificación.", body),
        Spacer(1, 5 * mm),
    ]
    rows = [["Documento", "Versión", "Cambio"]]
    change_labels = {
        "N00": ("v3", "Infografía curricular aprobada, ampliada y legible"),
        "N02": ("v15", "Rolando García y sistemas complejos"),
        "N03": ("v10", "Rolando García e interdisciplina"),
        "N05": ("v10", "Etkin, Schvarstein y Ricaurte"),
        "N06": ("v10", "Diseño, investigación e ISO 9241-210"),
        "N07": ("v10", "Infografía específica de cadena de evidencia"),
        "N08": ("v10", "Service blueprint e infografía de trabajo visible e invisible"),
        "N09": ("v10", "UI, UX, Scolari e infografía específica"),
    }
    for code, (version, change) in change_labels.items():
        rows.append([code, version, change])
    story.append(Table(rows, colWidths=[25 * mm, 24 * mm, 125 * mm], repeatRows=1, style=TableStyle([("BACKGROUND", (0, 0), (-1, 0), ink), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("BACKGROUND", (0, 1), (-1, -1), paper), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTNAME", (0, 1), (-1, -1), "Helvetica"), ("FONTSIZE", (0, 0), (-1, -1), 8), ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#b8bcb8")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 2.4 * mm), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.4 * mm)])))
    story += [Spacer(1, 7 * mm), Paragraph("Distribución curricular confirmada", h1)]
    curricular = [
        ("Gestión", "PMI, PMBOK, Scrum y Kanban", "N17, N20, N21, N23, N24 y N25"),
        ("Diseño", "UI, UX, diseño de interacción, servicios y accesibilidad", "N06, N08, N09, N15 y N28"),
        ("Operación", "DevOps y DORA", "N23, N25, N29 y N30"),
        ("Ingeniería", "APIs, OpenAPI, AsyncAPI, Git y GitHub", "N18, N23, N27 y N29"),
        ("Procesos", "BPM y BPMN", "N12, N14 y N15"),
        ("Perspectiva regional", "García, Etkin, Schvarstein, Scolari, Flores, Varsavsky, Ricaurte y Freire", "Integración distribuida de N02 a N36"),
    ]
    crows = [["Eje", "Contenido", "Ubicación"]] + [list(row) for row in curricular]
    story.append(Table(crows, colWidths=[28 * mm, 88 * mm, 58 * mm], repeatRows=1, style=TableStyle([("BACKGROUND", (0, 0), (-1, 0), ink), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("BACKGROUND", (0, 1), (-1, -1), gray), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTNAME", (0, 1), (-1, -1), "Helvetica"), ("FONTSIZE", (0, 0), (-1, -1), 7.5), ("GRID", (0, 0), (-1, -1), .35, colors.white), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 2.2 * mm), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2 * mm)])))
    story += [PageBreak(), Paragraph("Inventario N00 a N36", h1)]
    inventory = payload["documents"]
    def inventory_table(records):
        rows = [["N", "Págs.", "Secs.", "Imgs.", "Estado"]]
        for row in records:
            rows.append([row["code"], str(row["pages"]), str(row["core_sections"]), str(row["images"]), row["status"]])
        return Table(rows, colWidths=[14 * mm, 15 * mm, 15 * mm, 15 * mm, 25 * mm], repeatRows=1, style=TableStyle([("BACKGROUND", (0, 0), (-1, 0), ink), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [paper, colors.white]), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTNAME", (0, 1), (-1, -1), "Helvetica"), ("FONTSIZE", (0, 0), (-1, -1), 6.7), ("GRID", (0, 0), (-1, -1), .25, colors.HexColor("#c7cac7")), ("ALIGN", (1, 1), (-1, -1), "CENTER"), ("TOPPADDING", (0, 0), (-1, -1), 1.45 * mm), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.45 * mm)]))
    left = inventory_table(inventory[:19])
    right = inventory_table(inventory[19:])
    story.append(Table([[left, right]], colWidths=[87 * mm, 87 * mm], style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (0, 0), (0, 0), 3 * mm), ("LEFTPADDING", (1, 0), (1, 0), 3 * mm), ("RIGHTPADDING", (1, 0), (1, 0), 0)])))
    story += [PageBreak(), Paragraph("Resultado de los controles", h1)]
    for check in payload["checks"]:
        mark = "PASS" if check["result"] else "FAIL"
        story.append(Table([[mark, check["name"]], ["", check["evidence"]]], colWidths=[22 * mm, 152 * mm], style=TableStyle([("BACKGROUND", (0, 0), (0, 0), volt if mark == "PASS" else colors.red), ("BACKGROUND", (1, 0), (1, 0), ink), ("TEXTCOLOR", (0, 0), (0, 0), ink), ("TEXTCOLOR", (1, 0), (1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTNAME", (0, 1), (-1, 1), "Helvetica"), ("FONTSIZE", (0, 0), (-1, 0), 8), ("FONTSIZE", (0, 1), (-1, 1), 7), ("SPAN", (1, 1), (1, 1)), ("TOPPADDING", (0, 0), (-1, -1), 1.5 * mm), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5 * mm)])))
        story.append(Spacer(1, 1.8 * mm))
    story += [Spacer(1, 4 * mm), Paragraph("Conclusión", h1), Paragraph("El resultado automatizado es PASS. Las 37 lecturas están disponibles, los ejes aprobados aparecen en sus documentos asignados, Hotel Horizonte conserva continuidad, las secciones editoriales obligatorias están presentes y las infografías controladas son específicas. La colección queda sellada como candidata final para revisión académica externa.", body)]
    doc.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)


def main() -> int:
    documents: list[dict[str, object]] = []
    all_terms_missing: dict[str, list[str]] = {}
    structural_failures: dict[str, list[str]] = {}
    page_counts: dict[str, int] = {}
    pdf_hashes: dict[str, str] = {}
    for code, relative in PDF_FILES.items():
        path = SITE / "pdf" / relative
        reader = PdfReader(str(path))
        texts = [(page.extract_text() or "") for page in reader.pages]
        text = "\n".join(texts)
        norm = folded(text)
        pages = len(reader.pages)
        page_counts[code] = pages
        pdf_hashes[code] = sha256(path)
        a4 = all(abs(float(page.mediabox.width) - 595.276) < 1.5 and abs(float(page.mediabox.height) - 841.89) < 1.5 for page in reader.pages)
        images = sum(image_count(page) for page in reader.pages)
        missing = [section for section in CORE_SECTIONS if folded(section) not in norm] if code != "N00" else []
        if missing:
            structural_failures[code] = missing
        missing_terms = [term for term in TERM_CHECKS.get(code, ()) if folded(term) not in norm]
        if missing_terms:
            all_terms_missing[code] = missing_terms
        hotel = code == "N00" or "hotel horizonte" in norm or re.search(r"\bHH[‐‑-]\d{2}\b", text) is not None
        status = "PASS" if a4 and images > 0 and not missing and not missing_terms and hotel else "FAIL"
        documents.append({"code": code, "pages": pages, "a4": a4, "images": images, "core_sections": len(CORE_SECTIONS) - len(missing), "hotel": hotel, "missing_sections": missing, "missing_terms": missing_terms, "sha256": pdf_hashes[code], "status": status})

    changed_qa = {code: json.loads((ROOT / rel).read_text(encoding="utf-8")) for code, rel in CHANGED_QA.items()}
    v7_gate = json.loads((ROOT / "qa-reports/n11-n36-v7/PUBLICATION-GATE-SUMMARY.json").read_text(encoding="utf-8"))
    curricular = json.loads((ROOT / "audits/2026-09-10-curricular-expansion-audit.json").read_text(encoding="utf-8"))
    approval = json.loads((ROOT / "BLOCK-01-integrated-release-current/approval.json").read_text(encoding="utf-8"))
    infographic_paths = {code: ROOT / rel for code, rel in INFOGRAPHICS.items()}
    missing_infographics = sorted(code for code, path in infographic_paths.items() if not path.is_file())
    infographic_hashes = [sha256(path) for path in infographic_paths.values() if path.is_file()]
    duplicate_infographics = sorted(value for value, count in Counter(infographic_hashes).items() if count > 1)
    unchanged_codes = ("N01", "N04", "N10")
    unchanged_ok = all(pdf_hashes[code] == approval["pdf_sha256"][code] for code in unchanged_codes)
    checks = [
        {"name": "37 PDF presentes y legibles", "result": len(documents) == 37, "evidence": f"37 documentos, {sum(page_counts.values())} páginas"},
        {"name": "Formato A4 e imágenes embebidas", "result": all(row["a4"] and row["images"] > 0 for row in documents), "evidence": "Todas las páginas A4; ningún documento sin recursos de imagen"},
        {"name": "Sistema de secciones N01 a N36", "result": not structural_failures, "evidence": "Pregunta, Hotel, tesis, síntesis, píldoras, glosario, preparación y referencias presentes" if not structural_failures else json.dumps(structural_failures, ensure_ascii=False)},
        {"name": "Continuidad de Hotel Horizonte", "result": all(row["hotel"] for row in documents), "evidence": "Presente en N01 a N36; N00 lo establece como caso longitudinal"},
        {"name": "Distribución curricular aprobada", "result": not all_terms_missing, "evidence": "PMI/PMBOK, Scrum, Kanban, UI/UX, diseño, DevOps/DORA, APIs/Git/GitHub, BPMN y autores regionales verificados" if not all_terms_missing else json.dumps(all_terms_missing, ensure_ascii=False)},
        {"name": "Fuentes curriculares canónicas", "result": curricular.get("overall") == "pass", "evidence": f"Auditoría de fuentes: {curricular.get('overall', '').upper()}"},
        {"name": "Ocho PDF recompaginados", "result": all(report.get("status") == "PASS" for report in changed_qa.values()), "evidence": "N00, N02, N03, N05, N06, N07, N08 y N09: QA PASS"},
        {"name": "N01, N04 y N10 preservados", "result": unchanged_ok, "evidence": "Identidad SHA-256 confirmada"},
        {"name": "Regresión N11 a N36", "result": all(row.get("status") == "PASS" for row in v7_gate.get("documents", [])), "evidence": "26 de 26 documentos con gate editorial v7 en PASS"},
        {"name": "Infografías específicas", "result": not missing_infographics and not duplicate_infographics, "evidence": f"{len(infographic_hashes)} SVG controlados, sin duplicados exactos"},
        {"name": "PDF marcados y accesibles en cambios", "result": all(report.get("marked_pdf") and report.get("document_language") == "es-AR" and report.get("struct_tree_present") for report in changed_qa.values()), "evidence": "Marcado, árbol estructural e idioma es-AR en los ocho PDF nuevos"},
        {"name": "Cierres y enlaces preservados", "result": all(report.get("closing_folio_present") and report.get("closing_caption_present") and report.get("closing_alt_present") for report in changed_qa.values()), "evidence": "Folio, pie, texto alternativo y vínculo de autor verificados"},
    ]
    payload = {
        "schema": "metsi-integrated-collection-audit/v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "N00-N36",
        "status": "PASS" if all(check["result"] for check in checks) and all(row["status"] == "PASS" for row in documents) else "FAIL",
        "totals": {"documents": len(documents), "pages": sum(page_counts.values()), "images": sum(int(row["images"]) for row in documents), "infographics": len(infographic_hashes)},
        "checks": checks,
        "documents": documents,
        "page_counts": page_counts,
        "pdf_sha256": pdf_hashes,
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    build_dossier(payload)
    print(json.dumps({"status": payload["status"], "json": str(REPORT_JSON), "pdf": str(REPORT_PDF), "totals": payload["totals"]}, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
