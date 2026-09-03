#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html as html_lib
import json
import re
import sys
from collections import Counter
from pathlib import Path

from pypdf import PdfReader

from validate_n03_v9 import (
    compact,
    heading_alignment,
    links_by_page,
    page_extents,
    result,
    structure_alts,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE / "N04-v9-final"
CANONICAL = HERE / "N04-content-final/source/N04_hechos_sintomas_relatos_hipotesis_y_decisiones-content-final.md"
SOURCE = ROOT / "source/N04_hechos_sintomas_relatos_hipotesis_y_decisiones-content-final.md"
PDF = ROOT / "output/N04-METSI-lectura-previa-v9-final.pdf"
RAW_PDF = ROOT / "output/N04-METSI-lectura-previa-v9.pdf"
HTML = ROOT / "index.html"
CSS = ROOT / "magazine.css"
QA = ROOT / "qa-report.json"
INTEGRITY = ROOT / "integrity-report.json"
REPORT = ROOT / "validation-v9.json"
EXPECTED_SOURCE_SHA = "4e86351bcd6865c81bbdb8a5e72352e55042b5d9e16f71949737c610e6d13320"
EXPECTED_ROUTES = ["PROBLEMA"] * 4 + ["DISTINCIONES", "DECISIONES", "PRUEBA", "TRANSFERENCIA"] + ["PREPARACIÓN"] * 3
EXPECTED_URLS = {
    "https://doi.org/10.1017/CBO9780511840005",
    "https://iupress.org/9780253211903/the-essential-peirce-volume-2/",
    "https://www.iso.org/standard/35736.html",
    "https://doi.org/10.1080/07421222.1996.11518099",
    "https://doi.org/10.6028/NIST.AI.100-1",
    "https://doi.org/10.6028/NIST.AI.600-1",
    "https://doi.org/10.6028/NIST.AI.100-4",
    "https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strip_markup(value: str) -> str:
    value = html_lib.unescape(re.sub(r"<[^>]+>", " ", value))
    return re.sub(r"[*_`]", "", value)


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    body, references = source.split("## Referencias base", 1)
    html = HTML.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")
    qa = json.loads(QA.read_text(encoding="utf-8"))
    integrity = json.loads(INTEGRITY.read_text(encoding="utf-8"))
    content_integrity = json.loads((HERE / "N04-content-final/provenance/integrity-report.json").read_text(encoding="utf-8"))
    source_manifest = json.loads((ROOT / "source-manifest.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    cover_regression = json.loads((ROOT / "provenance/cover-regression-v8-v9.json").read_text(encoding="utf-8"))
    reader = PdfReader(str(PDF))
    page_texts = [page.extract_text() or "" for page in reader.pages]
    pdf_text = "\n".join(page_texts)
    headings = re.findall(r"^## (.+)$", source, flags=re.M)
    section_headings = headings[:-1]
    route_labels = [
        re.search(rf'data-section="{index:02d}".*?<em>([^<]+)</em>', html, re.S).group(1)
        for index in range(1, 12)
    ]
    all_links = {uri for page in links_by_page(reader) for uri in page}
    external_links = {uri for uri in all_links if "linkedin.com/in/carralbal" not in uri}
    source_urls = {value.rstrip(".,") for value in re.findall(r"https://\S+", references)}
    extents = page_extents(PDF)
    ordinary_pages = [page for page in range(6, 32) if page != 22]
    underfilled = {page: extents[page]["fill"] for page in ordinary_pages if extents[page]["fill"] < 0.50}
    alignment = heading_alignment(html, page_texts)
    isolated_initials = [
        {"page": page_number, "value": line.strip()}
        for page_number, text in enumerate(page_texts, 1)
        for line in text.splitlines()
        if re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", line.strip())
    ]
    direct_forms = sorted(set(re.findall(
        r"\b(?:dibujá|identificá|explicá|transferí|mirá|pensá|escribí|compará|analizá|reconstruí|elegí|tenés|podés|querés|usted)\b",
        body,
        re.I,
    )))
    anchor_tokens = {
        "Toulmin (2003)": "Stephen Toulmin",
        "Peirce (1998)": "Charles S. Peirce",
        "Pearl y Mackenzie (2018)": "Judea Pearl",
        "ISO/IEC 25012:2008": "ISO/IEC 25012 organiza",
        "Wang y Strong (1996)": "Wang y Strong muestran",
        "Schön (1983)": "Donald Schön",
        "NIST AI 100-1 (2023)": "AI Risk Management Framework 1.0 de NIST",
        "NIST AI 600-1 (2024)": "NIST AI 600-1 advierte",
        "NIST AI 100-4 (2024)": "NIST AI 100-4 y C2PA",
        "C2PA 2.4 (2026)": "NIST AI 100-4 y C2PA",
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
        result("canonical_source_is_byte_identical", SOURCE.read_bytes() == CANONICAL.read_bytes() and sha256(SOURCE) == EXPECTED_SOURCE_SHA, sha256(SOURCE)),
        result("canonical_structure", len(section_headings) == 11 and len(headings) == 12 and headings[-1] == "Referencias base", headings),
        result("three_movement_architecture", all(token in source for token in ("Movimiento 1 · Desarmar", "Movimiento 2 · Contrastar", "Movimiento 3 · Decidir")), "three movements present"),
        result("canonical_handoffs_present", all(token in source for token in ("De N03 a N04: del mapa a la justificación", "HH-04", "N05")), "N03 input, HH-04 conductor and N05 output are present"),
        result("source_blocks_render_once", integrity.get("status") == "PASS" and Counter(all_source_ids) == Counter(html_source_ids) and len(all_source_ids) == 437, integrity),
        result("content_audit_remains_closed", content_integrity.get("overall") == "pass" and content_integrity.get("word_counts", {}).get("total") == 10108 and content_integrity.get("word_counts", {}).get("substantive_from_thesis_through_synthesis") == 8695, content_integrity.get("word_counts")),
        result("pdf_is_new_finalized_artifact", PDF.exists() and RAW_PDF.exists() and sha256(PDF) != sha256(RAW_PDF), {"raw": sha256(RAW_PDF), "final": sha256(PDF)}),
        result("pdf_page_count_and_size", len(reader.pages) == 32 and qa.get("pages") == 32 and qa.get("a4_pages") == 32, {"pages": len(reader.pages), "a4": qa.get("a4_pages")}),
        result("all_headings_in_pdf", all(compact(heading) in compact(pdf_text) for heading in headings), len(headings)),
        result("no_orphan_headings", len(alignment) >= 45 and all(value["same_page"] for value in alignment.values()), {"count": len(alignment), "failures": {key: value for key, value in alignment.items() if not value["same_page"]}}),
        result("route_is_monotonic", route_labels == EXPECTED_ROUTES, {"actual": route_labels, "expected": EXPECTED_ROUTES}),
        result("contents_is_complete_and_ordered", all(re.search(rf"\b{index:02d}\b", page_texts[1]) for index in range(1, 12)) and page_texts[1].count("SIN NUM.") >= 2 and all(compact(section_headings[index]) in compact(page_texts[1]) for index in range(11)) and "secuencia argumental" in page_texts[1], "01 to 11, two SIN NUM. entries and complete note"),
        result("all_references_anchored", counts["references"] == 10 and all(anchors.values()), anchors),
        result("all_urls_preserved_and_linked", source_urls == EXPECTED_URLS and external_links == EXPECTED_URLS and qa.get("external_reference_links") == sorted(EXPECTED_URLS), {"source": sorted(source_urls), "annotations": sorted(external_links)}),
        result("hyphenated_urls_intact", all(token in pdf_text for token in ("essential-peirce-volume-2", "NIST.AI.100-1", "NIST.AI.600-1", "NIST.AI.100-4")), "locked hyphenated URL tokens extract intact"),
        result("ordinary_pages_are_at_least_half_full", not underfilled, {"minimum": min(extents[page]["fill"] for page in ordinary_pages), "underfilled": underfilled}),
        result("no_automatic_sparse_fills", qa.get("sparse_visual_fill_source_pages") == [] and qa.get("removed_blank_source_pages") == [], {"sparse": qa.get("sparse_visual_fill_source_pages"), "removed": qa.get("removed_blank_source_pages")}),
        result("two_internal_full_bleed_pauses", html.count('class="full-bleed full-bleed-quote"') == 2 and "Pregunta profesional" in page_texts[3] and "Una cifra no habla sola" in page_texts[4] and "La evidencia más valiosa" in page_texts[21], "question page 4, first pause page 5, second pause page 22"),
        result("cover_accessible_and_complete", all(token in page_texts[0] for token in ("LECTURA PREVIA", "EDICIÓN 2026", "N04", "FCE · UBA", "Hechos, síntomas")) and "L E C T U R A" not in page_texts[0], page_texts[0][:320]),
        result("premium_cover_contract", "cover-source-premium-bw-v2.png" in json.dumps(manifest) and "Analista de sistemas argentina en un hotel de Buenos Aires" in html and "grayscale(1)" not in re.search(r"\.cover-n04>img\{([^}]*)\}", css).group(1), "native black-and-white cinematic photography, Argentine representation, no desaturation filter and dedicated alt text"),
        result("only_cover_changed_against_v8", cover_regression.get("status") == "PASS" and cover_regression.get("page_1_mean_absolute_pixel_difference", 0) > 0 and cover_regression.get("pages_2_to_32_maximum_mean_absolute_pixel_difference") == 0 and cover_regression.get("pages_2_to_32_changed") == [], cover_regression),
        result("cover_pauses_and_closing_are_full_bleed", all(extents[page]["fill"] >= 1.0 for page in (1, 5, 22, 32)), {page: extents[page]["fill"] for page in (1, 5, 22, 32)}),
        result("referents_and_hotel_voices", html.count('class="contributor"') == 6 and html.count("hotel-voice hotel-voice-") == 4 and len(re.findall(r'hotel-(?:elena|lucia|ricardo|federico)\.jpg', html)) == 4 and "ISO / IEC" in page_texts[2], "six referents and four distinct equal Hotel Horizonte portraits"),
        result("counts_close", counts == {"pills": 5, "glossary": 16, "questions": 6, "references": 10}, counts),
        result("impersonal_register", not direct_forms, direct_forms),
        result("dash_rule", not re.search(r"[—–]", body), "dashes occur only inside official reference titles"),
        result("no_placeholders_or_stray_initials", not re.search(r"\b(?:TBD|lorem|XXX)\b|\[[^\]]+\]", source, re.I) and not isolated_initials, isolated_initials),
        result("tagging_language_and_alt", bool(reader.trailer["/Root"].get("/StructTreeRoot")) and reader.trailer["/Root"].get("/Lang") == "es-AR" and qa.get("marked_pdf") and len(alts) >= 3 and qa.get("closing_alt_present"), {"language": reader.trailer["/Root"].get("/Lang"), "alt_count": len(alts)}),
        result("footer_and_structured_closing", qa.get("linkedin_pages") == 32 and qa.get("closing_folio_present") and qa.get("closing_caption_present") and qa.get("closing_quote_absent") and qa.get("closing_alt_present"), {key: qa.get(key) for key in ("linkedin_pages", "closing_folio_present", "closing_caption_present", "closing_quote_absent", "closing_alt_present")}),
        result("qa_pipeline_passed", qa.get("status") == "PASS" and not qa.get("missing_headings") and not qa.get("forbidden_fonts"), qa.get("status")),
        result("n04_layout_contract", ".premium-magazine.document-n04" in css and ".cover-n04 .cover-meta-eyebrow" in css and ".premium-magazine.document-n04 .references" in css, "N04 cover, reading, glossary, question and reference rules are explicit"),
    ]
    passed = all(item["status"] == "PASS" for item in checks)
    report = {
        "document": "N04",
        "version": "v9-final",
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
