#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html as html_lib
import json
import re
import shutil
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

import pdfplumber
from PIL import Image, ImageChops
from pypdf import PdfReader


HERE = Path(__file__).resolve().parent
ROOT = HERE / "N02-v12-final"
BASE_ROOT = HERE / "N02-v11-final"
BASE_SOURCE = BASE_ROOT / "source" / "N02_el_sistema_no_cabe_en_una_aplicacion-v11.md"
BASE_PDF = BASE_ROOT / "output" / "N02-METSI-lectura-previa-v11-final.pdf"
SOURCE = ROOT / "source" / "N02_el_sistema_no_cabe_en_una_aplicacion-v12.md"
PDF = ROOT / "output" / "N02-METSI-lectura-previa-v12-final.pdf"
HTML = ROOT / "index.html"
CSS = ROOT / "magazine.css"
QA = ROOT / "qa-report.json"
REPORT = ROOT / "integrity-report.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(value: str) -> str:
    value = value.replace("ﬁ", "fi").replace("ﬂ", "fl")
    return re.sub(r"[^0-9a-záéíóúüñ]+", "", value.casefold())


def check(name: str, passed: bool, detail: object) -> dict[str, object]:
    return {"check": name, "status": "PASS" if passed else "FAIL", "detail": detail}


def links_by_page(reader: PdfReader) -> list[list[str]]:
    result: list[list[str]] = []
    for page in reader.pages:
        links = []
        for annotation in page.get("/Annots", []):
            action = annotation.get_object().get("/A")
            if action and action.get("/URI"):
                links.append(str(action.get("/URI")))
        result.append(links)
    return result


def structure_alts(reader: PdfReader) -> list[str]:
    root = reader.trailer["/Root"].get("/StructTreeRoot")
    alts: list[str] = []
    seen: set[int] = set()

    def walk(value: object) -> None:
        try:
            item = value.get_object()  # type: ignore[attr-defined]
        except Exception:
            item = value
        identity = id(item)
        if identity in seen:
            return
        seen.add(identity)
        if isinstance(item, dict):
            if item.get("/Alt"):
                alts.append(str(item.get("/Alt")))
            if item.get("/K") is not None:
                walk(item.get("/K"))
        elif isinstance(item, (list, tuple)):
            for child in item:
                walk(child)

    if root:
        walk(root)
    return alts


def page_occupancies(pdf: Path) -> list[float]:
    bundled = Path("/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/bin/pdftoppm")
    command = shutil.which("pdftoppm") or str(bundled)
    with tempfile.TemporaryDirectory(prefix="n02-v12-occupancy-") as folder:
        prefix = Path(folder) / "page"
        subprocess.run([command, "-png", "-r", "45", str(pdf), str(prefix)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        result: list[float] = []
        for path in sorted(Path(folder).glob("page-*.png")):
            image = Image.open(path).convert("RGB")
            width, height = image.size
            active_rows: list[int] = []
            for y in range(int(height * .035), int(height * .93)):
                active = 0
                for x in range(int(width * .045), int(width * .955)):
                    red, green, blue = image.getpixel((x, y))
                    if min(red, green, blue) < 220 or max(red, green, blue) - min(red, green, blue) > 25:
                        active += 1
                if active >= max(2, int(width * .004)):
                    active_rows.append(y)
            result.append(round((max(active_rows) - min(active_rows) + 1) / height, 3) if active_rows else 0.0)
        return result


def changed_visual_pages(reference: Path, candidate: Path) -> list[int]:
    bundled = Path("/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/bin/pdftoppm")
    command = shutil.which("pdftoppm") or str(bundled)
    with tempfile.TemporaryDirectory(prefix="n02-v12-regression-") as folder:
        root = Path(folder)
        for label, pdf in (("baseline", reference), ("candidate", candidate)):
            subprocess.run([command, "-png", "-r", "45", str(pdf), str(root / label)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        changed: list[int] = []
        for number in range(1, 28):
            old = Image.open(root / f"baseline-{number:02d}.png").convert("RGB")
            new = Image.open(root / f"candidate-{number:02d}.png").convert("RGB")
            if ImageChops.difference(old, new).getbbox():
                changed.append(number)
        return changed


def source_paragraph_spans(html: str, pdf: Path) -> dict[str, object]:
    pages = [page.extract_text() or "" for page in PdfReader(str(pdf)).pages]
    compact_pages = [compact(page.replace("ﬁ", "fi").replace("ﬂ", "fl")) for page in pages]
    spans: list[dict[str, object]] = []
    missing: list[str] = []
    for source_id, raw in re.findall(r'<p[^>]*data-source-id="([^"]+)"[^>]*>(.*?)</p>', html, flags=re.S):
        text = html_lib.unescape(re.sub(r"<[^>]+>", " ", raw))
        words = re.findall(r"[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", text)
        if len(words) < 10:
            continue
        first = compact(" ".join(words[:10]))
        last = compact(" ".join(words[-10:]))
        starts = [index + 1 for index, page in enumerate(compact_pages) if first in page]
        ends = [index + 1 for index, page in enumerate(compact_pages) if last in page]
        if not starts or not ends:
            missing.append(source_id)
        else:
            end_page = ends[-1]
            start_page = max((page for page in starts if page <= end_page), default=starts[0])
            if start_page != end_page:
                spans.append({"source_id": source_id, "start_page": start_page, "end_page": end_page})
    return {"spans": spans, "missing": missing}


def glossary_bold_counts(pdf: Path) -> dict[int, int]:
    result: dict[int, int] = {}
    with pdfplumber.open(pdf) as document:
        for page_number in (24, 25):
            result[page_number] = sum(
                1 for char in document.pages[page_number - 1].chars
                if "SemiBold" in char["fontname"] and abs(float(char["size"]) - 8.8) <= .2
            )
    return result


def question_vertical_gaps(pdf: Path) -> list[float]:
    gaps: list[float] = []
    with pdfplumber.open(pdf) as document:
        words = document.pages[24].extract_words(x_tolerance=1, y_tolerance=2)
        for x0, x1, numbers in ((80, 290, (1, 2, 3)), (305, 520, (4, 5, 6))):
            starts = {
                int(word["text"][:-1]): float(word["top"])
                for word in words
                if word["text"] in {f"{number}." for number in numbers} and x0 <= float(word["x0"]) < x1
            }
            for current, following in zip(numbers, numbers[1:]):
                bottoms = [
                    float(word["bottom"])
                    for word in words
                    if x0 <= float(word["x0"]) < x1 and starts[current] <= float(word["top"]) < starts[following]
                ]
                gaps.append(round(starts[following] - max(bottoms), 2))
    return gaps


def section_heading_body_alignment(html: str, page_texts: list[str]) -> dict[str, object]:
    compact_pages = [compact(text.replace("ﬁ", "fi").replace("ﬂ", "fl")) for text in page_texts]
    result: dict[str, object] = {}
    pattern = re.compile(r'<section class="reading-section[^>]*data-section="(\d{2})"[^>]*>(.*?)(?=<section class="reading-section|</article>)', re.S)
    for number, section in pattern.findall(html):
        heading_match = re.search(r'<h2[^>]*>(.*?)</h2>', section, flags=re.S)
        body_match = re.search(r'<(?:p|li)[^>]*>(.*?)</(?:p|li)>', section, flags=re.S)
        if not heading_match or not body_match:
            result[number] = {"same_page": False, "reason": "missing heading or body block"}
            continue
        heading = html_lib.unescape(re.sub(r"<[^>]+>", " ", heading_match.group(1)))
        body = html_lib.unescape(re.sub(r"<[^>]+>", " ", body_match.group(1)))
        body_words = re.findall(r"[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", body)[:8]
        heading_pages = {index + 1 for index, text in enumerate(compact_pages) if compact(heading) in text}
        body_pages = {index + 1 for index, text in enumerate(compact_pages) if compact(" ".join(body_words)) in text}
        shared = sorted(heading_pages & body_pages)
        result[number] = {"same_page": bool(shared), "pages": shared}
    return result


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    base_source = BASE_SOURCE.read_text(encoding="utf-8")
    body, references = source.split("## Referencias base", 1)
    html = HTML.read_text(encoding="utf-8")
    base_html = (BASE_ROOT / "index.html").read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")
    qa = json.loads(QA.read_text(encoding="utf-8"))
    reader = PdfReader(str(PDF))
    catalog = reader.trailer["/Root"]
    page_texts = [page.extract_text() or "" for page in reader.pages]
    links = links_by_page(reader)
    all_links = {uri for page_links in links for uri in page_links}
    urls = re.findall(r"https://\S+", references)
    headings = re.findall(r"^## (.+)$", source, flags=re.M)
    image_descriptions = re.findall(r'<img[^>]+alt="([^"]+)"', html) + re.findall(r'role="img" aria-label="([^"]+)"', html)

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
    anchor_result = {name: token in body for name, token in anchors.items()}

    p1 = page_texts[0]
    p10 = page_texts[9]
    p17 = page_texts[16]
    p19 = page_texts[18]
    p20 = page_texts[19]
    p24 = page_texts[23]
    order_result = {
        "p19_heading_before_caption": p19.find("Una autopsia") < p19.find("El software puede funcionar"),
        "p20_table_before_voices": p20.find("Promesa comercial") < p20.find("Cuatro voces dentro del sistema"),
        "p24_pills_heading_before_first_item": p24.find("Cinco píldoras para recordar") < p24.find("La pantalla muestra un estado"),
    }
    dropcap_result = {
        "p10": p10.find("07 METSI · N02") < p10.find("El error de buscar") < p10.find("Cuando una organización"),
        "p17": p17.find("13 METSI · N02") < p17.find("2026: cuando la aplicación") < p17.find("En 2026 la frontera"),
        "p23": page_texts[22].find("19 METSI · N02") < page_texts[22].find("Síntesis") < page_texts[22].find("El sistema de información"),
    }
    isolated_initials = [
        {"page": page_index, "value": line.strip()}
        for page_index, text in enumerate(page_texts, 1)
        for line in text.splitlines()
        if re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", line.strip())
    ]
    direct_forms = sorted(set(re.findall(
        r"\b(?:dibujá|identificá|explicá|transferí|mirá|pensá|escribí|compará|analizá|reconstruí|elegí|conozcas|tenés|podés|querés|usted)\b",
        body,
        flags=re.I,
    )))
    transfer_start = base_source.index("## Caso de transferencia: medicación hospitalaria")
    test_start = base_source.index("## Comprobación: ¿el mapa permite decidir algo distinto?")
    synthesis_start = base_source.index("## Síntesis")
    transfer_block = base_source[transfer_start:test_start].rstrip()
    test_block = base_source[test_start:synthesis_start].rstrip()
    reconstructed = base_source[:transfer_start] + test_block + "\n\n" + transfer_block + "\n\n" + base_source[synthesis_start:]
    text_diff_exact = reconstructed == source
    p7_lines = [line.strip() for line in page_texts[6].splitlines() if line.strip()]
    continuation_result = {
        "p6_to_p7": p7_lines[:8][-1].endswith("devuelta.") if len(p7_lines) >= 8 else False,
        "p21_to_p22_closed": page_texts[21].startswith("La amplitud debe ser proporcional"),
        "p23_to_p24_no_longer_splits": page_texts[23].startswith("20 METSI · N02"),
    }
    ordinary_pages = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
    page_words = {page: len(page_texts[page - 1].split()) for page in ordinary_pages}
    catalog_marked = catalog.get("/MarkInfo")
    marked = bool(catalog_marked and catalog_marked.get_object().get("/Marked"))
    alts = structure_alts(reader)
    route_labels = [
        re.search(rf'data-section="{index:02d}".*?<em>([^<]+)</em>', html, flags=re.S).group(1)
        for index in range(1, 23)
    ]
    expected_route = ["PROBLEMA"] * 4 + ["DISTINCIONES"] * 6 + ["DECISIONES"] * 5 + ["PRUEBA"] * 2 + ["TRANSFERENCIA"] + ["PREPARACIÓN"] * 4
    glossary_counts = glossary_bold_counts(PDF)
    question_gaps = question_vertical_gaps(PDF)
    paragraph_spans = source_paragraph_spans(html, PDF)
    occupancies = page_occupancies(PDF)
    baseline_occupancies = page_occupancies(BASE_PDF)
    visual_changes = changed_visual_pages(BASE_PDF, PDF)
    source_tokens = re.findall(r"[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", source.casefold())
    base_tokens = re.findall(r"[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", base_source.casefold())
    pdf_text_compact = re.sub(r"\s+", "", "\n".join(page_texts))
    section_alignment = section_heading_body_alignment(html, page_texts)
    assets = sorted((ROOT / "assets").glob("*"))
    base_assets = {path.name: sha256(path) for path in (BASE_ROOT / "assets").glob("*")}
    candidate_assets = {path.name: sha256(path) for path in assets}

    checks = [
        check("source_sections_and_order", len(headings) == 23 and headings[16:19] == ["Comprobación: ¿el mapa permite decidir algo distinto?", "Caso de transferencia: medicación hospitalaria", "Síntesis"] and headings[-1] == "Referencias base", headings),
        check("human_referents_only", "Elham Tabassi" in html and "referent-nist.jpg" not in html and "Jim Poulter" not in source + html, "Elham Tabassi replaces the institutional card"),
        check("checkland_record_correct", "Checkland, P., & Poulter, J. (2007)" in references and "ISBN 978-0-470-02554-3" in references, "John Poulter, Wiley 2007, ISBN preserved"),
        check("all_seventeen_references_anchored", len(re.findall(r"^- ", references, flags=re.M)) == 17 and all(anchor_result.values()), anchor_result),
        check("fifteen_distinct_reference_urls_linked", len(urls) == 15 and len(set(urls)) == 15 and all_links.issuperset(urls), {"source": len(urls), "linked": len(set(urls) & all_links)}),
        check("body_has_no_em_or_en_dash_punctuation", not re.search(r"[—–]", body), "technical hyphens and bibliographic punctuation excluded"),
        check("impersonal_register", not direct_forms, direct_forms),
        check("questions_and_delivery_instruction", all(token in body for token in ("dos de las seis preguntas", "¿Qué decisiones habilita", "¿Qué optimización local razonable", "Al transferir el criterio")), "six questions plus delivery instruction"),
        check("accessible_dropcaps_removed", all(dropcap_result.values()) and not isolated_initials, {"order": dropcap_result, "isolated_initials": isolated_initials}),
        check("cover_eyebrow_two_clean_lines", "LECTURA PREVIA" in p1 and "EDICIÓN 2026" in p1 and "EDICIÓN 2026N02" not in p1, p1[:180]),
        check("route_is_monotonic_and_matches_contents", route_labels == expected_route, {"labels": route_labels, "expected": expected_route}),
        check("contents_has_complete_renumbered_order", all(re.search(rf"\b{number:02d}\b", page_texts[1]) for number in range(1, 23)) and page_texts[1].count("SIN NUM.") >= 2 and compact(page_texts[1]).find(compact("17 Comprobación: ¿el mapa permite decidir algo distinto?")) < compact(page_texts[1]).find(compact("18 Caso de transferencia: medicación hospitalaria")), "01 to 22 plus both SIN NUM. entries"),
        check("v11_text_delta_is_exact_reorder_only", text_diff_exact and Counter(source_tokens) == Counter(base_tokens), {"exact_reconstruction": text_diff_exact, "v11_words": len(base_tokens), "v12_words": len(source_tokens)}),
        check("page_break_paragraph_control", all(continuation_result.values()), {"minimum_continuation_lines": 4, "results": continuation_result}),
        check("paragraph_spans_controlled", not paragraph_spans["missing"] and paragraph_spans["spans"] == [{"source_id": "N02-s02-b008", "start_page": 6, "end_page": 7}], paragraph_spans),
        check("list_structure_preserved", html.count("<li") == base_html.count("<li"), {"v11": base_html.count("<li"), "v12": html.count("<li"), "locked_visible_bullets": 53}),
        check("glossary_complete_on_page_24", glossary_counts == {24: 387, 25: 0} and "Stakeholder o parte" in page_texts[23] and "Stakeholder o parte" not in page_texts[24], glossary_counts),
        check("list_blocks_do_not_split", all(token in css for token in (".pill-summary .section-body ol{break-inside:avoid-page", ".questions .section-body ol{display:block", ".glossary-two-column .section-body ul{columns:3")) and css.count("page-break-inside:avoid") >= 3, "pills, glossary and questions protected"),
        check("question_spacing_is_content_driven", "grid-template-rows" not in re.search(r'\.premium-magazine\.document-n02 \.questions \.section-body ol\{([^}]*)\}', css).group(1) and "columns:2" in css and question_gaps and max(question_gaps) <= 30.0, {"gaps_points": question_gaps, "maximum": max(question_gaps, default=0)}),
        check("three_column_legible_glossary", "columns:3" in css and "font-size:9.7pt" in css and glossary_counts[24] == 387, "three columns; rendered glossary body and strong terms remain at the approved sizes"),
        check("reading_order_regressions_closed", all(order_result.values()), order_result),
        check("all_section_titles_share_page_with_body", len(section_alignment) == 22 and all(item["same_page"] for item in section_alignment.values()), section_alignment),
        check("no_sparse_ordinary_page", min(page_words.values()) >= 120 and len(occupancies) == 27 and min(occupancies) >= .5, {"word_counts": page_words, "occupancies": occupancies, "minimum": min(occupancies)}),
        check("expected_visual_change_scope", visual_changes == [2, 22, 23, 24, 25], {"changed_pages": visual_changes, "cover_unchanged": 1 not in visual_changes}),
        check("all_approved_assets_preserved", candidate_assets == base_assets, {"assets": len(candidate_assets), "identical": candidate_assets == base_assets}),
        check("a4_27_pages", len(reader.pages) == 27 and all(abs(float(page.mediabox.width) - 595.276) < 2 and abs(float(page.mediabox.height) - 841.89) < 2 for page in reader.pages), len(reader.pages)),
        check("tagged_pdf_in_argentine_spanish", bool(catalog.get("/StructTreeRoot")) and marked and str(catalog.get("/Lang")) == "es-AR", {"struct_tree": bool(catalog.get("/StructTreeRoot")), "marked": marked, "lang": str(catalog.get("/Lang"))}),
        check("specific_image_descriptions", len(image_descriptions) >= 14 and all(value.strip() for value in image_descriptions), {"count": len(image_descriptions)}),
        check("closing_alt_is_structural", any("Diez fósforos" in value for value in alts), alts),
        check("two_internal_pauses_and_canonical_closing", html.count('class="full-bleed full-bleed-quote"') == 2 and 'class="full-bleed closing-image"' in html, "2 pauses plus matches closing"),
        check("folio_and_footer_link_every_page", all(re.search(rf"\b{index:02d}\b", text) and any("linkedin.com/in/carralbal" in uri for uri in links[index - 1]) for index, text in enumerate(page_texts, 1)), "27/27"),
        check("url_copy_layer_preserves_all_hyphens", all(re.sub(r"\s+", "", url) in pdf_text_compact for url in urls) and all(token in pdf_text_compact for token in ("wp-content", "balancing-ai-tensions", "dora-report", "NIST.AI.100-1", "NIST.AI.600-1", "S0003-6870(00)00009-0", "s12525-024-00734-y", "s10796-025-10591-5", "concept-note-ai-rmf-profile-trustworthy-ai-critical-infrastructure")), {"urls": len(urls)}),
        check("only_official_iso_dash_remains", source.count("—") == 1 and "Systems and software engineering — System life cycle processes" in references and "—" not in body, "one bibliographic dash, zero body dashes"),
        check("generator_qa_pass", qa.get("status") == "PASS" and qa.get("struct_tree_present") and qa.get("marked_pdf") and qa.get("document_language") == "es-AR", qa.get("status")),
        check("no_placeholders", not re.search(r"\b(?:TODO|TBD|LOREM IPSUM|PLACEHOLDER|XXX)\b", source + html), "none"),
    ]
    result = {
        "document": "N02",
        "version": "v12 review candidate",
        "candidate": str(PDF),
        "pdf_sha256": sha256(PDF),
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "checks": checks,
    }
    REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
