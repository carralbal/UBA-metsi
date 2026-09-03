#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html as html_lib
import json
import re
import sys
from collections import Counter
from pathlib import Path

import pdfplumber
from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
ROOT = HERE / "N03-v8-final"
CANONICAL = HERE / "N03-content-final/source/N03_fronteras_retroalimentacion_y_efectos-content-final.md"
SOURCE = ROOT / "source/N03_fronteras_retroalimentacion_y_efectos-content-final.md"
PDF = ROOT / "output/N03-METSI-lectura-previa-v8-final.pdf"
RAW_PDF = ROOT / "output/N03-METSI-lectura-previa-v8.pdf"
HTML = ROOT / "index.html"
CSS = ROOT / "magazine.css"
QA = ROOT / "qa-report.json"
INTEGRITY = ROOT / "integrity-report.json"
REPORT = ROOT / "validation-v8.json"
EXPECTED_SOURCE_SHA = "6930c5a6cf7c98ad2f60ebf662334a7f491827260e460c939c51b7c9acef6854"
EXPECTED_ROUTES = ["PROBLEMA"] * 4 + ["DISTINCIONES", "DECISIONES", "PRUEBA", "TRANSFERENCIA"] + ["PREPARACIÓN"] * 3
EXPECTED_URLS = {
    "https://doi.org/10.1007/978-1-4615-4201-8",
    "https://doi.org/10.7551/mitpress/8179.001.0001",
    "https://doi.org/10.6028/NIST.AI.600-1",
    "https://doi.org/10.6028/NIST.AI.700-2",
    "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
    "https://doi.org/10.1002/sys.21664",
    "https://www.iso.org/standard/81702.html",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(value: str) -> str:
    value = value.replace("ﬁ", "fi").replace("ﬂ", "fl")
    return re.sub(r"[^0-9a-záéíóúüñ]+", "", value.casefold())


def strip_markup(value: str) -> str:
    value = html_lib.unescape(re.sub(r"<[^>]+>", " ", value))
    return re.sub(r"[*_`]", "", value)


def result(name: str, passed: bool, detail: object) -> dict[str, object]:
    return {"check": name, "status": "PASS" if passed else "FAIL", "detail": detail}


def links_by_page(reader: PdfReader) -> list[list[str]]:
    pages: list[list[str]] = []
    for page in reader.pages:
        links: list[str] = []
        for annotation in page.get("/Annots", []):
            action = annotation.get_object().get("/A")
            if action and action.get("/URI"):
                links.append(str(action.get("/URI")))
        pages.append(links)
    return pages


def structure_alts(reader: PdfReader) -> list[str]:
    root = reader.trailer["/Root"].get("/StructTreeRoot")
    values: list[str] = []
    seen: set[int] = set()

    def walk(value: object) -> None:
        try:
            item = value.get_object()  # type: ignore[attr-defined]
        except Exception:
            item = value
        if id(item) in seen:
            return
        seen.add(id(item))
        if isinstance(item, dict):
            if item.get("/Alt"):
                values.append(str(item.get("/Alt")))
            if item.get("/K") is not None:
                walk(item.get("/K"))
        elif isinstance(item, (list, tuple)):
            for child in item:
                walk(child)

    if root:
        walk(root)
    return values


def page_extents(pdf: Path) -> dict[int, dict[str, float]]:
    extents: dict[int, dict[str, float]] = {}
    with pdfplumber.open(pdf) as document:
        for page_number, page in enumerate(document.pages, 1):
            objects: list[tuple[float, float]] = []
            for line in page.extract_text_lines():
                top = float(line["top"])
                if 40 <= top < 790:
                    objects.append((top, float(line["bottom"])))
            for image in page.images:
                top = max(40.0, float(image.get("top", 0)))
                bottom = min(790.0, float(image.get("bottom", 0)))
                if bottom > top:
                    objects.append((top, bottom))
            if objects:
                top = min(item[0] for item in objects)
                bottom = max(item[1] for item in objects)
                extents[page_number] = {"top": round(top, 2), "bottom": round(bottom, 2), "fill": round((bottom - top) / 744.0, 4)}
    return extents


def heading_alignment(html: str, page_texts: list[str]) -> dict[str, object]:
    compact_pages = [compact(text) for text in page_texts]
    aligned: dict[str, object] = {}
    for level, heading_html in re.findall(r"<(h[234])[^>]*>(.*?)</\1>", html, re.S):
        heading = strip_markup(heading_html).strip()
        if not heading or heading in aligned:
            continue
        position = html.find(heading_html)
        tail = html[position + len(heading_html):]
        body_match = re.search(r"<(?:p|li)[^>]*>(.*?)</(?:p|li)>", tail, re.S)
        if not body_match:
            continue
        body_words = re.findall(r"[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", strip_markup(body_match.group(1)))[:7]
        heading_pages = {index + 1 for index, text in enumerate(compact_pages) if compact(heading) in text}
        body_pages = {index + 1 for index, text in enumerate(compact_pages) if compact(" ".join(body_words)) in text}
        shared = sorted(heading_pages & body_pages)
        aligned[heading] = {"level": level, "same_page": bool(shared), "pages": shared}
    return aligned


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    canonical = CANONICAL.read_bytes()
    html = HTML.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")
    qa = json.loads(QA.read_text(encoding="utf-8"))
    integrity = json.loads(INTEGRITY.read_text(encoding="utf-8"))
    source_manifest = json.loads((ROOT / "source-manifest.json").read_text(encoding="utf-8"))
    content_integrity = json.loads((HERE / "N03-content-final/provenance/integrity-report.json").read_text(encoding="utf-8"))
    reader = PdfReader(str(PDF))
    page_texts = [page.extract_text() or "" for page in reader.pages]
    pdf_text = "\n".join(page_texts)
    body, references = source.split("## Referencias base", 1)
    headings = re.findall(r"^## (.+)$", source, flags=re.M)
    section_headings = headings[:-1]
    route_labels = [re.search(rf'data-section="{index:02d}".*?<em>([^<]+)</em>', html, re.S).group(1) for index in range(1, 12)]
    all_links = {uri for page in links_by_page(reader) for uri in page}
    external_links = {uri for uri in all_links if "linkedin.com/in/carralbal" not in uri}
    source_urls = {value.rstrip(".,") for value in re.findall(r"https://\S+", references)}
    extents = page_extents(PDF)
    ordinary_pages = [page for page in range(6, 30) if page != 19]
    underfilled = {page: extents[page]["fill"] for page in ordinary_pages if extents[page]["fill"] < 0.50}
    alignment = heading_alignment(html, page_texts)
    isolated_initials = [{"page": page_number, "value": line.strip()} for page_number, text in enumerate(page_texts, 1) for line in text.splitlines() if re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", line.strip())]
    direct_forms = sorted(set(re.findall(r"\b(?:dibujá|identificá|explicá|transferí|mirá|pensá|escribí|compará|analizá|reconstruí|elegí|tenés|podés|querés|usted)\b", body, re.I)))
    anchor_tokens = {
        "Churchman (1968)": "C. West Churchman formuló",
        "Midgley (2000)": "Gerald Midgley profundizó",
        "Meadows (2008)": "Donella Meadows ofrece",
        "Senge (2006)": "Peter Senge utiliza",
        "Sterman (2000)": "John Sterman propone",
        "Leveson (2012)": "Nancy Leveson muestra",
        "NIST AI 600-1 (2024)": "NIST AI 600-1 propone",
        "NIST AI 700-2 (2025)": "informe piloto ARIA de NIST",
        "Reglamento UE 2024/1689": "Reglamento europeo 2024/1689",
        "Polojärvi (2023)": "Polojärvi (2023)",
        "ISO/IEC/IEEE 15288:2023": "ISO/IEC/IEEE 15288:2023 distingue",
    }
    anchors = {key: token in body for key, token in anchor_tokens.items()}
    all_source_ids = [entry["source_id"] for entry in source_manifest["eligible_blocks"]]
    html_source_ids = re.findall(r'data-source-id="([^"]+)"', html)
    pills_block = source.split("## Cinco píldoras para recordar", 1)[1].split("## Glosario esencial", 1)[0]
    glossary_block = source.split("## Glosario esencial", 1)[1].split("## Preguntas de preparación", 1)[0]
    questions_block = source.split("## Preguntas de preparación", 1)[1].split("## Referencias base", 1)[0]
    counts = {
        "pills": len(re.findall(r"^\d+\. \*\*", pills_block, re.M)),
        "glossary": len(re.findall(r"^- \*\*", glossary_block, re.M)),
        "questions": len(re.findall(r"^\d+\. ", questions_block, re.M)),
        "references": len(re.findall(r"^- ", references, re.M)),
    }
    alts = structure_alts(reader)
    checks = [
        result("canonical_source_is_byte_identical", SOURCE.read_bytes() == canonical and sha256(SOURCE) == EXPECTED_SOURCE_SHA, {"sha256": sha256(SOURCE), "expected": EXPECTED_SOURCE_SHA}),
        result("canonical_structure", len(section_headings) == 11 and len(headings) == 12 and headings[-1] == "Referencias base", headings),
        result("three_movement_architecture", all(token in source for token in ("Movimiento 1 · Delimitar", "Movimiento 2 · Observar", "Movimiento 3 · Decidir")), "three movements present"),
        result("canonical_handoffs_present", all(token in source for token in ("De N02 a N03: del mapa a sus consecuencias", "HH-03", "N04")), "N02 input, HH-03 conductor and N04 output are present"),
        result("source_blocks_render_once", integrity.get("status") == "PASS" and Counter(all_source_ids) == Counter(html_source_ids) and len(all_source_ids) == 320, integrity),
        result("content_audit_remains_closed", content_integrity.get("overall") == "pass" and content_integrity.get("word_counts", {}).get("substantive_from_thesis_through_synthesis") == 7631, content_integrity.get("word_counts")),
        result("pdf_is_new_finalized_artifact", PDF.exists() and RAW_PDF.exists() and sha256(PDF) != sha256(RAW_PDF), {"raw_sha256": sha256(RAW_PDF), "final_sha256": sha256(PDF)}),
        result("pdf_page_count_and_size", len(reader.pages) == 30 and qa.get("pages") == 30 and qa.get("a4_pages") == 30, {"pages": len(reader.pages), "a4": qa.get("a4_pages")}),
        result("all_headings_in_pdf", all(compact(heading) in compact(pdf_text) for heading in headings), {"headings": len(headings)}),
        result("no_orphan_headings", len(alignment) >= 50 and all(value["same_page"] for value in alignment.values()), {"count": len(alignment), "failures": {key: value for key, value in alignment.items() if not value["same_page"]}}),
        result("route_is_monotonic", route_labels == EXPECTED_ROUTES, {"actual": route_labels, "expected": EXPECTED_ROUTES}),
        result("contents_is_complete_and_ordered", all(re.search(rf"\b{index:02d}\b", page_texts[1]) for index in range(1, 12)) and page_texts[1].count("SIN NUM.") >= 2 and all(compact(section_headings[index]) in compact(page_texts[1]) for index in range(11)), "01 to 11 plus Referentes and Referencias base as SIN NUM."),
        result("all_references_anchored", counts["references"] == 11 and all(anchors.values()), anchors),
        result("all_urls_preserved_and_linked", source_urls == EXPECTED_URLS and external_links == EXPECTED_URLS and qa.get("external_reference_links") == sorted(EXPECTED_URLS), {"source": sorted(source_urls), "annotations": sorted(external_links)}),
        result("hyphenated_urls_intact", all(token in pdf_text for token in ("NIST.AI.600-1", "NIST.AI.700-2", "eur-lex")), "locked hyphenated URL tokens extract intact"),
        result("ordinary_pages_are_at_least_half_full", not underfilled, {"minimum": min(extents[page]["fill"] for page in ordinary_pages), "underfilled": underfilled, "pages": {page: extents[page]["fill"] for page in ordinary_pages}}),
        result("no_automatic_sparse_fills", qa.get("sparse_visual_fill_source_pages") == [] and qa.get("removed_blank_source_pages") == [], {"sparse": qa.get("sparse_visual_fill_source_pages"), "removed": qa.get("removed_blank_source_pages")}),
        result("two_internal_full_bleed_pauses", html.count('class="full-bleed full-bleed-quote"') == 2 and "Pregunta profesional" in page_texts[3] and "El efecto de la intervención" in page_texts[4] and "Una estabilidad observada" in page_texts[18], "question page 4, first pause page 5, second pause page 19"),
        result("cover_accessible_and_complete", all(token in page_texts[0] for token in ("LECTURA PREVIA", "EDICIÓN 2026", "N03", "FCE · UBA", "Fronteras,")) and "L E C T U R A" not in page_texts[0], page_texts[0][:320]),
        result("premium_cover_contract", "cover-source-premium-v2.png" in (ROOT / "manifest.json").read_text(encoding="utf-8") and "Trabajadora hotelera argentina en un lobby nocturno" in html, "cinematic magazine photograph, Argentine representation, dedicated alt text and stable source asset"),
        result("cover_pauses_and_closing_are_full_bleed", all(extents[page]["fill"] >= 1.0 for page in (1, 5, 19, 30)), {page: extents[page]["fill"] for page in (1, 5, 19, 30)}),
        result("referents_and_hotel_voices", html.count('class="contributor"') == 6 and html.count("hotel-voice hotel-voice-") == 4 and len(re.findall(r'hotel-(?:elena|lucia|ricardo|federico)\.jpg', html)) == 4, "six referents and four distinct equal Hotel Horizonte portraits"),
        result("counts_close", counts == {"pills": 5, "glossary": 13, "questions": 6, "references": 11}, counts),
        result("impersonal_register", not direct_forms, direct_forms),
        result("dash_rule", not re.search(r"[—–]", body) and references.count("—") == 1 and "engineering — System life cycle processes" in references, "only the official ISO title retains an em dash"),
        result("no_placeholders_or_stray_initials", not re.search(r"\b(?:TBD|lorem|XXX)\b|\[[^\]]+\]", source, re.I) and isolated_initials == [{"page": 12, "value": "R"}], {"isolated_initials": isolated_initials, "note": "R is the visible reinforcing-loop marker in the diagram"}),
        result("tagging_language_and_alt", bool(reader.trailer["/Root"].get("/StructTreeRoot")) and reader.trailer["/Root"].get("/Lang") == "es-AR" and qa.get("marked_pdf") and len(alts) >= 3 and qa.get("closing_alt_present"), {"language": reader.trailer["/Root"].get("/Lang"), "alt_count": len(alts), "closing_alt": qa.get("closing_alt_present")}),
        result("footer_and_structured_closing", qa.get("linkedin_pages") == 30 and qa.get("closing_folio_present") and qa.get("closing_caption_present") and qa.get("closing_quote_absent") and qa.get("closing_alt_present"), {key: qa.get(key) for key in ("linkedin_pages", "closing_folio_present", "closing_caption_present", "closing_quote_absent", "closing_alt_present")}),
        result("qa_pipeline_passed", qa.get("status") == "PASS" and not qa.get("missing_headings") and not qa.get("forbidden_fonts"), {"status": qa.get("status"), "missing_headings": qa.get("missing_headings"), "forbidden_fonts": qa.get("forbidden_fonts")}),
        result("n03_layout_contract", ".premium-magazine.document-n03" in css and ".cover-n03 .cover-meta-eyebrow" in css and ".premium-magazine.document-n03 .references" in css, "N03 cover, reading, question and reference rules are explicit"),
    ]
    passed = all(item["status"] == "PASS" for item in checks)
    report = {
        "document": "N03",
        "version": "v8-final",
        "status": "PASS" if passed else "FAIL",
        "source_sha256": sha256(SOURCE),
        "pdf_sha256": sha256(PDF),
        "pdf_bytes": PDF.stat().st_size,
        "pdf_modified": PDF.stat().st_mtime,
        "pages": len(reader.pages),
        "checks": checks,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
