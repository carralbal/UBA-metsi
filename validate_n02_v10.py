#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from pypdf import PdfReader


HERE = Path(__file__).resolve().parent
ROOT = HERE / "N02-v10-final"
SOURCE = ROOT / "source" / "N02_el_sistema_no_cabe_en_una_aplicacion-v10.md"
PDF = ROOT / "output" / "N02-METSI-lectura-previa-v10-final.pdf"
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


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    body, references = source.split("## Referencias base", 1)
    html = HTML.read_text(encoding="utf-8")
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

    p19 = page_texts[18]
    p20 = page_texts[19]
    p24 = page_texts[23]
    order_result = {
        "p19_heading_before_caption": p19.find("Una autopsia") < p19.find("El software puede funcionar"),
        "p20_table_before_voices": p20.find("Promesa comercial") < p20.find("Cuatro voces dentro del sistema"),
        "p24_pills_heading_before_first_item": p24.find("Cinco píldoras para recordar") < p24.find("La pantalla muestra un estado"),
    }
    ordinary_pages = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
    page_words = {page: len(page_texts[page - 1].split()) for page in ordinary_pages}
    catalog_marked = catalog.get("/MarkInfo")
    marked = bool(catalog_marked and catalog_marked.get_object().get("/Marked"))
    alts = structure_alts(reader)

    checks = [
        check("source_sections_and_order", len(headings) == 23 and headings[-1] == "Referencias base", headings),
        check("human_referents_only", "Elham Tabassi" in html and "referent-nist.jpg" not in html and "Jim Poulter" not in source + html, "Elham Tabassi replaces the institutional card"),
        check("checkland_record_correct", "Checkland, P., & Poulter, J. (2007)" in references and "ISBN 978-0-470-02554-3" in references, "John Poulter, Wiley 2007, ISBN preserved"),
        check("all_seventeen_references_anchored", len(re.findall(r"^- ", references, flags=re.M)) == 17 and all(anchor_result.values()), anchor_result),
        check("fifteen_distinct_reference_urls_linked", len(urls) == 15 and len(set(urls)) == 15 and all_links.issuperset(urls), {"source": len(urls), "linked": len(set(urls) & all_links)}),
        check("body_has_no_em_or_en_dash_punctuation", not re.search(r"[—–]", body), "technical hyphens and bibliographic punctuation excluded"),
        check("rioplatense_instructions", all(word in body for word in ("Dibujá", "Identificá", "Explicá", "Transferí")), "voseo preserved"),
        check("three_column_legible_glossary", "columns:3" in css and "font-size:9.7pt" in css, "three columns at 9.7 pt"),
        check("reading_order_regressions_closed", all(order_result.values()), order_result),
        check("no_sparse_ordinary_page", min(page_words.values()) >= 120, page_words),
        check("a4_27_pages", len(reader.pages) == 27 and all(abs(float(page.mediabox.width) - 595.276) < 2 and abs(float(page.mediabox.height) - 841.89) < 2 for page in reader.pages), len(reader.pages)),
        check("tagged_pdf_in_argentine_spanish", bool(catalog.get("/StructTreeRoot")) and marked and str(catalog.get("/Lang")) == "es-AR", {"struct_tree": bool(catalog.get("/StructTreeRoot")), "marked": marked, "lang": str(catalog.get("/Lang"))}),
        check("specific_image_descriptions", len(image_descriptions) >= 14 and all(value.strip() for value in image_descriptions), {"count": len(image_descriptions)}),
        check("closing_alt_is_structural", any("Diez fósforos" in value for value in alts), alts),
        check("two_internal_pauses_and_canonical_closing", html.count('class="full-bleed full-bleed-quote"') == 2 and 'class="full-bleed closing-image"' in html, "2 pauses plus matches closing"),
        check("folio_and_footer_link_every_page", all(re.search(rf"\b{index:02d}\b", text) and any("linkedin.com/in/carralbal" in uri for uri in links[index - 1]) for index, text in enumerate(page_texts, 1)), "27/27"),
        check("generator_qa_pass", qa.get("status") == "PASS" and qa.get("struct_tree_present") and qa.get("marked_pdf") and qa.get("document_language") == "es-AR", qa.get("status")),
        check("no_placeholders", not re.search(r"\b(?:TODO|TBD|LOREM IPSUM|PLACEHOLDER)\b", source + html), "none"),
    ]
    result = {
        "document": "N02",
        "version": "v10 review candidate",
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
