#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html as html_lib
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

import pdfplumber
from PIL import Image
from pypdf import PdfReader


HERE = Path(__file__).resolve().parent
ROOT = HERE / "N02-v14-final"
CANONICAL = HERE / "N02-content-final" / "source" / "N02_el_sistema_no_cabe_en_una_aplicacion-content-final.md"
SOURCE = ROOT / "source" / "N02_el_sistema_no_cabe_en_una_aplicacion-content-final.md"
PDF = ROOT / "output" / "N02-METSI-lectura-previa-v14-final.pdf"
HTML = ROOT / "index.html"
CSS = ROOT / "magazine.css"
MANIFEST = ROOT / "manifest.json"
IMAGE_MANIFEST = ROOT / "provenance" / "image-manifest.json"
QA = ROOT / "qa-report.json"
INTEGRITY = ROOT / "integrity-report.json"
REPORT = ROOT / "validation-v14.json"

EXPECTED_SOURCE_SHA = "6f6bfde594de374a8873fe212ac3c326b50b1186d61268a540a9303a77b1f138"
EXPECTED_ROUTES = (
    ["PROBLEMA"] * 4
    + ["DISTINCIONES"] * 7
    + ["DECISIONES"] * 6
    + ["PRUEBA"]
    + ["TRANSFERENCIA"]
    + ["PREPARACIÓN"] * 5
)
EXPECTED_URLS = {
    "https://doi.org/10.17705/1CAIS.00906",
    "https://doi.org/10.1016/S0003-6870(00)00009-0",
    "https://doi.org/10.1177/001872675100400101",
    "https://doi.org/10.1016/j.intcom.2010.07.003",
    "https://is2020.hosting2.acm.org/wp-content/uploads/2021/06/is2020.pdf",
    "https://doi.org/10.6028/NIST.AI.100-1",
    "https://dora.dev/research/2025/dora-report/",
    "https://dora.dev/insights/balancing-ai-tensions/",
    "https://doi.org/10.17705/1CAIS.05446",
    "https://doi.org/10.1002/sys.21664",
    "https://www.iso.org/standard/81702.html",
    "https://doi.org/10.6028/NIST.AI.600-1",
    "https://doi.org/10.1007/s12525-024-00734-y",
    "https://doi.org/10.1007/s10796-025-10591-5",
    "https://www.nist.gov/programs-projects/concept-note-ai-rmf-profile-trustworthy-ai-critical-infrastructure",
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


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def cover_tonal_audit(path: Path) -> dict[str, object]:
    with Image.open(path) as source:
        image = source.convert("RGB")
        image.thumbnail((512, 512), Image.Resampling.LANCZOS)
        pixels = list(image.getdata())
    luminance = [.2126 * red + .7152 * green + .0722 * blue for red, green, blue in pixels]
    spreads = [float(max(pixel) - min(pixel)) for pixel in pixels]
    p05 = percentile(luminance, .05)
    p95 = percentile(luminance, .95)
    spread_p95 = percentile(spreads, .95)
    tonal_stddev = statistics.pstdev(luminance)
    dark_fraction = sum(value < 32 for value in luminance) / len(luminance)
    passed = (
        spread_p95 <= 6.0
        and p05 <= 70.0
        and p95 >= 170.0
        and p95 - p05 >= 150.0
        and tonal_stddev >= 45.0
        and dark_fraction <= .35
    )
    return {
        "passed": passed,
        "channel_spread_p95": round(spread_p95, 2),
        "luminance_p05": round(p05, 2),
        "luminance_p95": round(p95, 2),
        "tonal_span": round(p95 - p05, 2),
        "luminance_stddev": round(tonal_stddev, 2),
        "fraction_below_32": round(dark_fraction, 4),
    }


def effective_css_rule(css: str, selector: str) -> str:
    matches = re.findall(re.escape(selector) + r"\{([^}]*)\}", css)
    return re.sub(r"\s+", "", matches[-1]) if matches else ""


def rgba_alphas(rule: str) -> list[float]:
    return [float(value) for value in re.findall(r"rgba\([^)]*,([0-9]*\.?[0-9]+)\)", rule)]


def packaged_asset_audit(records: list[dict[str, object]], html: str, cover_source: str) -> dict[str, object]:
    failures: list[dict[str, object]] = []
    record_files = {str(record.get("file", "")) for record in records}
    referenced = set(re.findall(r'<img[^>]+src="(assets/[^"]+)"', html))
    referenced.discard("assets/cover.png")
    referenced.add(cover_source)
    for record in records:
        relative = str(record.get("file", ""))
        path = ROOT / relative
        expected = str(record.get("sha256", ""))
        actual = sha256(path) if path.is_file() else None
        if actual != expected:
            failures.append({"file": relative, "expected": expected, "actual": actual})
    missing_records = sorted(referenced - record_files)
    unreferenced_records = sorted(record_files - referenced)
    return {
        "passed": not failures and not missing_records and not unreferenced_records,
        "records": len(records),
        "failures": failures,
        "missing_records": missing_records,
        "unreferenced_records": unreferenced_records,
    }


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
                extents[page_number] = {
                    "top": round(top, 2),
                    "bottom": round(bottom, 2),
                    "fill": round((bottom - top) / 744.0, 4),
                }
    return extents


def section_heading_alignment(html: str, page_texts: list[str]) -> dict[str, object]:
    compact_pages = [compact(text) for text in page_texts]
    aligned: dict[str, object] = {}
    pattern = re.compile(
        r'<section class="reading-section[^>]*data-section="(\d{2})"[^>]*>(.*?)(?=<section class="reading-section|</article>)',
        re.S,
    )
    for number, section in pattern.findall(html):
        heading_match = re.search(r"<h2[^>]*>(.*?)</h2>", section, re.S)
        body_match = re.search(r"<(?:p|li)[^>]*>(.*?)</(?:p|li)>", section, re.S)
        if not heading_match or not body_match:
            aligned[number] = {"same_page": False, "reason": "missing heading or body"}
            continue
        heading = strip_markup(heading_match.group(1))
        body_words = re.findall(r"[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", strip_markup(body_match.group(1)))[:8]
        heading_pages = {index + 1 for index, text in enumerate(compact_pages) if compact(heading) in text}
        body_pages = {index + 1 for index, text in enumerate(compact_pages) if compact(" ".join(body_words)) in text}
        shared = sorted(heading_pages & body_pages)
        aligned[number] = {"same_page": bool(shared), "pages": shared}
    return aligned


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    canonical = CANONICAL.read_text(encoding="utf-8")
    html = HTML.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    image_manifest = json.loads(IMAGE_MANIFEST.read_text(encoding="utf-8"))
    qa = json.loads(QA.read_text(encoding="utf-8"))
    integrity = json.loads(INTEGRITY.read_text(encoding="utf-8"))
    source_manifest = json.loads((ROOT / "source-manifest.json").read_text(encoding="utf-8"))
    reader = PdfReader(str(PDF))
    page_texts = [page.extract_text() or "" for page in reader.pages]
    pdf_text = "\n".join(page_texts)
    body, references = source.split("## Referencias base", 1)
    headings = re.findall(r"^## (.+)$", source, flags=re.M)
    section_headings = headings[:-1]
    route_labels = [
        re.search(rf'data-section="{index:02d}".*?<em>([^<]+)</em>', html, re.S).group(1)
        for index in range(1, 25)
    ]
    links = links_by_page(reader)
    all_links = {uri for page in links for uri in page}
    external_links = {uri for uri in all_links if "linkedin.com/in/carralbal" not in uri}
    extents = page_extents(PDF)
    ordinary_pages = list(range(6, 17)) + list(range(18, 29))
    underfilled = {page: extents[page]["fill"] for page in ordinary_pages if extents[page]["fill"] < 0.60}
    alignment = section_heading_alignment(html, page_texts)
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
    anchors = {
        "Alter 2002": "Steven Alter propuso",
        "Checkland y Poulter 2007": "Peter Checkland y John Poulter",
        "Clegg 2000": "Clegg (2000)",
        "Mumford 2003": "Mumford insistió",
        "Trist y Bamforth 1951": "Trist y Bamforth",
        "Baxter y Sommerville 2011": "Baxter y Sommerville (2011)",
        "ACM/AIS 2020": "IS2020 de ACM y AIS",
        "Tabassi 2023": "NIST (Tabassi, 2023)",
        "DORA 2025": "DORA, al estudiar desarrollo asistido por IA en 2025",
        "DORA 2026": "DORA (2026)",
        "Alter 2024": "Alter (2024)",
        "Polojärvi 2023": "Polojärvi (2023)",
        "ISO 15288": "ISO/IEC/IEEE 15288:2023",
        "Autio 2024": "Autio y colaboradores, 2024",
        "Hofmann 2024": "Hofmann y colaboradores (2024)",
        "Nguyen y Elbanna 2025": "Nguyen y Elbanna (2025)",
        "NIST 2026": "NIST (2026)",
    }
    anchor_result = {key: value in body for key, value in anchors.items()}
    all_source_ids = [entry["source_id"] for entry in source_manifest["eligible_blocks"]]
    html_source_ids = re.findall(r'data-source-id="([^"]+)"', html)
    source_urls = {value.rstrip(".,") for value in re.findall(r"https://\S+", references)}
    pills_block = source.split("## Cinco píldoras para recordar", 1)[1].split("## Glosario esencial", 1)[0]
    glossary_block = source.split("## Glosario esencial", 1)[1].split("## Preguntas de preparación", 1)[0]
    questions_block = source.split("## Preguntas de preparación", 1)[1].split("## Referencias base", 1)[0]
    counts = {
        "pills": len(re.findall(r"^\d+\. \*\*", pills_block, re.M)),
        "glossary": len(re.findall(r"^- \*\*", glossary_block, re.M)),
        "questions": len(re.findall(r"^\d+\. ", questions_block, re.M)),
        "references": len(re.findall(r"^- ", references, re.M)),
    }
    cover_contract = manifest.get("cover", {})
    cover_source_relative = str(cover_contract.get("source", ""))
    cover_source = ROOT / cover_source_relative
    cover_alias = ROOT / "assets" / str(cover_contract.get("file", ""))
    cover_tone = cover_tonal_audit(cover_source) if cover_source.is_file() else {"passed": False, "reason": "missing cover source"}
    cover_rule = effective_css_rule(css, ".cover-n02>img")
    shade_rule = effective_css_rule(css, ".cover-n02 .cover-shade")
    shade_alphas = rgba_alphas(shade_rule)
    cover_audit = {
        "passed": (
            cover_source.is_file()
            and cover_alias.is_file()
            and sha256(cover_source) == sha256(cover_alias) == cover_contract.get("sha256")
            and cover_contract.get("photographic_origin") == "native_black_and_white"
            and cover_contract.get("render_treatment") == "no_grayscale_conversion"
            and str(cover_contract.get("alt", "")) in html
            and cover_tone.get("passed") is True
            and "filter:none" in cover_rule
            and bool(shade_alphas)
            and max(shade_alphas) <= .60
            and ".collection-cover.cover-shade{position:absolute;inset:0" in re.sub(r"\s+", "", css)
        ),
        "source": cover_source_relative,
        "sha256": sha256(cover_source) if cover_source.is_file() else None,
        "tone": cover_tone,
        "contract": cover_contract,
        "cover_rule": cover_rule,
        "shade_rule": shade_rule,
    }
    asset_audit = packaged_asset_audit(image_manifest.get("used_assets", []), html, cover_source_relative)
    checks = [
        result("canonical_source_is_byte_identical", SOURCE.read_bytes() == CANONICAL.read_bytes() and sha256(SOURCE) == EXPECTED_SOURCE_SHA, {"sha256": sha256(SOURCE), "expected": EXPECTED_SOURCE_SHA}),
        result("canonical_structure", len(section_headings) == 24 and len(headings) == 25 and headings[-1] == "Referencias base", headings),
        result("canonical_handoffs_present", all(token in source for token in ("De HH-01 a HH-02: del pedido revisable al sistema relevante", "Tercera aplicación de HH-02: una frontera lista para ser revisada", "De HH-02 a N03: un mapa con consecuencias abiertas")), "HH-01 input, third HH-02 application and N03 output are present"),
        result("source_blocks_render_once", integrity.get("status") == "PASS" and Counter(all_source_ids) == Counter(html_source_ids) and len(all_source_ids) == 255, integrity),
        result("pdf_page_count_and_size", len(reader.pages) == 29 and qa.get("pages") == 29 and qa.get("a4_pages") == 29, {"pages": len(reader.pages), "a4": qa.get("a4_pages")}),
        result("all_headings_in_pdf", all(compact(heading) in compact(pdf_text) for heading in headings), {"headings": len(headings)}),
        result("section_titles_have_body_on_same_page", len(alignment) == 24 and all(value["same_page"] for value in alignment.values()), alignment),
        result("route_is_monotonic", route_labels == EXPECTED_ROUTES, {"actual": route_labels, "expected": EXPECTED_ROUTES}),
        result("contents_is_complete_and_ordered", all(re.search(rf"\b{index:02d}\b", page_texts[1]) for index in range(1, 25)) and page_texts[1].count("SIN NUM.") >= 2 and all(compact(section_headings[index]) in compact(page_texts[1]) for index in range(24)), "01 to 24 plus Referentes and Referencias base as SIN NUM."),
        result("all_references_anchored", len(re.findall(r"^- ", references, re.M)) == 17 and all(anchor_result.values()), anchor_result),
        result("all_urls_preserved_and_linked", source_urls == EXPECTED_URLS and external_links == EXPECTED_URLS and qa.get("external_reference_links") == sorted(EXPECTED_URLS), {"source": sorted(source_urls), "annotations": sorted(external_links)}),
        result("hyphenated_urls_intact", all(token in pdf_text for token in ("wp-content", "balancing-ai-tensions", "dora-report", "NIST.AI.100-1", "NIST.AI.600-1", "s12525-024-00734-y", "s10796-025-10591-5", "concept-note-ai-rmf-profile-trustworthy-ai-critical-infrastructure")), "all locked hyphenated URL tokens extract intact"),
        result("checkland_record_intact", "Checkland, P., & Poulter, J. (2007)" in references and "ISBN 978-0-470-02554-3" in references and "wiley.com" not in references.casefold(), "John Poulter, Wiley 2007, ISBN preserved, no Wiley URL"),
        result("ordinary_pages_are_at_least_sixty_percent_full", not underfilled, {"minimum": min(extents[page]["fill"] for page in ordinary_pages), "underfilled": underfilled, "pages": {page: extents[page]["fill"] for page in ordinary_pages}}),
        result("no_automatic_sparse_fills", qa.get("sparse_visual_fill_source_pages") == [] and qa.get("removed_blank_source_pages") == [], {"sparse": qa.get("sparse_visual_fill_source_pages"), "removed": qa.get("removed_blank_source_pages")}),
        result("two_internal_full_bleed_pauses", html.count('class="full-bleed full-bleed-quote"') == 2 and "Pregunta profesional" in page_texts[3] and "Una pantalla puede decir" in page_texts[4] and "Cómo emerge un resultado" in page_texts[15] and "Decir que una propiedad" in page_texts[16], "two pauses, first immediately after page 4, second after emergence"),
        result("cover_accessible_and_complete", all(token in page_texts[0] for token in ("LECTURA PREVIA", "EDICIÓN 2026", "N02", "FCE · UBA", "El sistema deinformación")) and "L E C T U R A" not in page_texts[0], page_texts[0][:250]),
        result("cover_is_native_bw_tonally_open_hash_locked_and_locally_shaded", cover_audit["passed"], cover_audit),
        result("cover_and_pauses_are_full_bleed", all(extents[page]["fill"] >= 1.0 for page in (1, 5, 17, 29)), {page: extents[page]["fill"] for page in (1, 5, 17, 29)}),
        result("referents_and_hotel_voices", html.count('class="contributor"') == 6 and html.count("hotel-voice hotel-voice-") == 4 and len(re.findall(r'hotel-(?:elena|lucia|ricardo|federico)\.jpg', html)) == 4, "six referents and four distinct Hotel Horizonte voices"),
        result("counts_close", counts == {"pills": 5, "glossary": 19, "questions": 6, "references": 17}, counts),
        result("impersonal_register", not direct_forms, direct_forms),
        result("dash_rule", not re.search(r"[—–]", body) and references.count("—") == 1 and "engineering — System life cycle processes" in references, "only the official ISO title retains an em dash"),
        result("no_placeholders_or_isolated_initials", not re.search(r"\b(?:TBD|lorem|XXX)\b|\[[^\]]+\]", source, re.I) and not isolated_initials, {"isolated_initials": isolated_initials}),
        result("tagging_language_and_alt", bool(reader.trailer["/Root"].get("/StructTreeRoot")) and reader.trailer["/Root"].get("/Lang") == "es-AR" and qa.get("marked_pdf") and len(structure_alts(reader)) >= 1, {"language": reader.trailer["/Root"].get("/Lang"), "alts": structure_alts(reader)}),
        result("footer_and_closing", qa.get("linkedin_pages") == 29 and qa.get("closing_folio_present") and qa.get("closing_caption_present") and qa.get("closing_quote_absent") and qa.get("closing_alt_present"), {key: qa.get(key) for key in ("linkedin_pages", "closing_folio_present", "closing_caption_present", "closing_quote_absent", "closing_alt_present")}),
        result("rendered_assets_match_the_packaged_provenance", asset_audit["passed"], asset_audit),
        result("qa_pipeline_passed", qa.get("status") == "PASS" and not qa.get("missing_headings") and not qa.get("forbidden_fonts"), {"status": qa.get("status"), "missing_headings": qa.get("missing_headings"), "forbidden_fonts": qa.get("forbidden_fonts")}),
        result("css_preserves_body_scale", "font-size:10.4pt;line-height:1.36" in css and ".document-n02 section[data-section=\"11\"] .photo-band img{height:34mm}" in css, "canonical typography retained; only image height and column composition were adjusted"),
    ]
    passed = all(item["status"] == "PASS" for item in checks)
    report = {
        "document": "N02",
        "version": "v14-final",
        "status": "PASS" if passed else "FAIL",
        "source_sha256": sha256(SOURCE),
        "pdf_sha256": sha256(PDF),
        "pdf_bytes": PDF.stat().st_size,
        "pages": len(reader.pages),
        "checks": checks,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
