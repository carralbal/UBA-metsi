#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

from pypdf import PdfReader


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "N01" / "source" / "N01_metodologia_sin_recetas-v9.md"
CURATION = HERE / "N01" / "image-curation" / "image-manifest.json"
ROOT = HERE / "N01-v9-final"
HTML = ROOT / "index.html"
CSS = ROOT / "magazine.css"
DIAGRAM = ROOT / "diagrams" / "N01-mapa-decision.svg"
PDF = ROOT / "output" / "N01-METSI-lectura-previa-v9-final.pdf"
QA = ROOT / "qa-report.json"
REPORT = ROOT / "integrity-report.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def compact(value: str) -> str:
    return re.sub(r"[^0-9a-záéíóúüñ]+", "", value.casefold())


def check(name: str, passed: bool, detail: object) -> dict:
    return {"check": name, "status": "PASS" if passed else "FAIL", "detail": detail}


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    body, references = source.split("## Referencias base", 1)
    html = HTML.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")
    diagram = DIAGRAM.read_text(encoding="utf-8")
    qa = json.loads(QA.read_text(encoding="utf-8"))
    curation = json.loads(CURATION.read_text(encoding="utf-8"))
    reader = PdfReader(str(PDF))
    page_texts = [normalized(page.extract_text() or "") for page in reader.pages]
    pdf_text = "\n".join(page_texts)
    headings = re.findall(r"^## (.+)$", source, flags=re.M)
    numbered_headings = headings[:-1]

    expected_opening = [
        "Pregunta profesional",
        "El mapa perfecto de la montaña equivocada",
        "Tesis",
        "Cómo leer este mapa: N01 abre el recorrido N02 a N10",
        "La tranquilidad de empezar por una solución",
    ]
    route_labels = re.findall(r"<em>(PROBLEMA|DISTINCIONES|DECISIONES|PRUEBA|TRANSFERENCIA|PREPARACIÓN)</em>", html)

    anchors = {
        "Checkland y Poulter": "Checkland y Poulter",
        "Schön": "Schön describió",
        "Argyris y Schön": "Argyris y Schön distinguen",
        "March": "March formuló",
        "Suchman": "Lucy Suchman mostró",
        "Senge": "Senge agrega",
        "ISO 24748": "ISO/IEC/IEEE 24748-1:2024",
        "PMBOK 8": "PMBOK Guide",
        "NIST AI RMF": "AI Risk Management Framework 1.0 de NIST",
        "NIST GenAI": "perfil de NIST para inteligencia artificial generativa",
        "SWEBOK V4.0a": "SWEBOK Guide V4.0a",
        "ISO 15288": "ISO/IEC/IEEE 15288:2023",
        "EU AI Act": "Reglamento de Inteligencia Artificial de la Unión Europea",
        "DORA 2025": "informe DORA 2025",
        "IS2020": "modelo curricular IS2020 de ACM y AIS",
    }
    anchor_result = {name: token in body for name, token in anchors.items()}

    section_blocks = re.findall(r"^## (.+?)\n(.*?)(?=^## |\Z)", source, flags=re.M | re.S)
    orphan_result: dict[str, object] = {}
    for heading, section_body in section_blocks[:-1]:
        heading_needle = compact(heading)
        body_words = re.findall(r"[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", re.sub(r"^### .+$", "", section_body, flags=re.M))
        body_needle = compact(" ".join(body_words[:6]))
        body_needle_without_drop_cap = compact(" ".join(body_words[1:7]))
        candidate = None
        for physical_page, text in enumerate(page_texts[3:], start=4):
            compact_page = compact(text)
            if heading_needle not in compact_page:
                continue
            body_present = bool(body_needle) and (
                body_needle in compact_page or body_needle_without_drop_cap in compact_page
            )
            candidate = {"physical_page": physical_page, "first_body_words_present": body_present}
            if body_present:
                break
        orphan_result[heading] = candidate or {"physical_page": None, "first_body_words_present": False}

    links_per_page: list[list[str]] = []
    for page in reader.pages:
        links: list[str] = []
        for annotation in page.get("/Annots", []):
            action = annotation.get_object().get("/A")
            if action and action.get("/URI"):
                links.append(str(action.get("/URI")))
        links_per_page.append(links)
    all_links = {uri for page in links_per_page for uri in page}
    expected_fixed_links = {
        "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
        "https://is2020.hosting2.acm.org/wp-content/uploads/2021/06/is2020.pdf",
    }

    p24 = page_texts[23]
    p24_compact = compact(p24)
    p24_title = p24_compact.find(compact("Aplicación a Hotel Horizonte"))
    p24_caption = p24_compact.find(compact("El software puede funcionar y la promesa fallar: el objeto de análisis es el sistema sociotécnico que produce el servicio."))
    p24_body = p24_compact.find(compact("El pedido inicial puede transformarse en un brief de intervención provisional."))

    assets = curation["assets"]
    selected_paths = [HERE / "N01" / "image-curation" / entry["file"] for entry in assets]
    assets_valid = all(path.exists() and sha256(path) == entry["sha256"] for path, entry in zip(selected_paths, assets))
    hotel_portraits = [path for path in sorted((ROOT / "assets").glob("hotel-*")) if path.name != "hotel-horizonte.png"]
    referent_portraits = sorted((ROOT / "assets").glob("referent-*"))

    frozen_paths = ["N01-v8-final", "N01/source/N01_metodologia_sin_recetas-v8.md"]
    baseline_frozen = subprocess.run(
        ["git", "diff", "--quiet", "--", *frozen_paths], cwd=HERE, check=False
    ).returncode == 0

    referent_pairs = [
        ("Learning for Action", "Wiley, 2007 · con Jim Poulter"),
        ("The Reflective Practitioner", "Basic Books, 1983"),
        ("Organizational Learning II", "Addison-Wesley, 1996 · con Donald A. Schön"),
        ("Exploration and Exploitation in Organizational Learning", "Organization Science, 1991"),
        ("Human-Machine Reconfigurations: Plans and Situated Actions", "Cambridge University Press, 2007"),
        ("The Fifth Discipline", "Currency · edición revisada, 2006"),
    ]
    referents_match = {work: work in html and edition in html for work, edition in referent_pairs}

    glossary_terms = [
        "Frontera", "Situación problemática", "Evidencia suficiente",
        "Incertidumbre epistemológica", "Incertidumbre de acción",
        "Incertidumbre de coordinación", "Incertidumbre normativa",
        "Criterio de revisabilidad", "Tailoring", "Outcome", "Hito de decisión",
        "Trazabilidad", "Reversibilidad", "Agente de inteligencia artificial",
    ]
    glossary_page_index = next(
        index for index, text in enumerate(page_texts[3:], start=3)
        if compact("Glosario esencial") in compact(text)
    )
    glossary_page = page_texts[glossary_page_index]

    checks = [
        check("v8_baseline_frozen", baseline_frozen, frozen_paths),
        check("source_depth_stable", 7500 <= len(source.split()) <= 8000, {"words": len(source.split())}),
        check("section_count_and_order", len(headings) == 29 and headings[:5] == expected_opening, {"sections": len(headings), "opening": headings[:5]}),
        check("route_visible_all_sections", len(route_labels) == 28 and set(route_labels) == {"PROBLEMA", "DISTINCIONES", "DECISIONES", "PRUEBA", "TRANSFERENCIA", "PREPARACIÓN"}, {"count": len(route_labels), "labels": sorted(set(route_labels))}),
        check("no_orphan_section_headings", all(item["first_body_words_present"] for item in orphan_result.values()), orphan_result),
        check("statement_pages_preserved", html.count('full-bleed full-bleed-quote') == 2 and 'data-section="01"' in html, {"black_quote_pages": html.count('full-bleed full-bleed-quote'), "opening_statement": 'data-section="01"' in html}),
        check("cover_exact_three_lines", "Metodología sin recetas:<br>intervenir cuando el problema<br>todavía no está claro" in html and ".cover-n01 .cover-title{width:160mm}" in css, "three explicit lines"),
        check("page24_caption_and_reading_order", 0 <= p24_title < p24_caption < p24_body, {"title": p24_title, "caption": p24_caption, "body": p24_body}),
        check("method_diagram_readable_and_complete", "font-size=\"24\"" in diagram and all(compact(word) in compact(diagram) for word in ("Amplifica", "capacidad", "sustituir", "juicio")) and "…" not in diagram, {"width_rule": ".n01-method-architecture{width:100%" in css}),
        check("pill_ornament_removed", "pill-summary-icon" not in html and "Cinco píldoras para recordar" in html, "no decorative 01–05 icon"),
        check("references_complete_and_anchored", len(re.findall(r"^- ", references, flags=re.M)) == 15 and all(anchor_result.values()), {"entries": len(re.findall(r"^- ", references, flags=re.M)), "anchors": anchor_result}),
        check("fixed_reference_links", expected_fixed_links.issubset(all_links) and "wpcontent" not in pdf_text and "eurlex" not in pdf_text, sorted(expected_fixed_links & all_links)),
        check("checkland_isbn_no_wiley_url", "ISBN 978-0-470-02554-3" in source and "wiley.com" not in source.casefold(), "ISBN 978-0-470-02554-3"),
        check("referents_match_references", all(referents_match.values()), referents_match),
        check("pmbok8_precision", all(token in body for token in ("doce principios de la séptima en seis", "dominios de desempeño de ocho a siete", "Áreas de Foco", "cuarenta procesos no prescriptivos")), "6 principles, 7 domains, Focus Areas, 40 processes"),
        check("revisability_named_and_reused", source.casefold().count("criterio de revisabilidad") >= 5, {"count": source.casefold().count("criterio de revisabilidad")}),
        check("six_conflicting_hotel_voices", all(token in html for token in ("directorio espera una fecha hoy", "campaña tiene que salir esta semana", "once habitaciones", "dos grupos juntos", "Los estados viajaron sin error", "ocho habitaciones")), {"voices": 6}),
        check("six_distinct_hotel_portraits", len(hotel_portraits) == 6 and len({sha256(path) for path in hotel_portraits}) == 6, [path.name for path in hotel_portraits]),
        check("six_distinct_referent_portraits", len(referent_portraits) == 6 and len({sha256(path) for path in referent_portraits}) == 6, [path.name for path in referent_portraits]),
        check("questions_and_delivery", "¿Qué permite distinguir una adaptación rigurosa de una improvisación conveniente?" in source and "¿Qué outcome haría que el sistema de turnos mejore el acceso en lugar de reforzar una barrera previa?" in source and "traer respondidas por escrito dos de las siete preguntas" in source, "Q3 impersonal, Q7 health case, written delivery"),
        check("impersonal_register", not re.search(r"\busted(?:es)?\b|\bdistinguiría\b", source, flags=re.I), "no usted or distinguiría"),
        check("glossary_four_columns_complete_one_page", "column-count:4" in css and all(compact(term) in compact(glossary_page) for term in glossary_terms) and compact("Cinco píldoras para recordar") not in compact(glossary_page) and compact("Preguntas de preparación") not in compact(glossary_page), {"physical_page": glossary_page_index + 1, "terms": len(glossary_terms), "exclusive": True}),
        check("assets_preserved", len(assets) == 8 and assets_valid, {"assets": len(assets), "hashes_valid": assets_valid}),
        check("pdf_a4_30_pages", len(reader.pages) == 30 and all(abs(float(page.mediabox.width) - 595.276) < 2 and abs(float(page.mediabox.height) - 841.89) < 2 for page in reader.pages), {"pages": len(reader.pages)}),
        check("pdf_qa_pass", qa.get("status") == "PASS", qa.get("status")),
        check("folios_and_footer_links", all(any("linkedin.com/in/carralbal" in uri for uri in links) for links in links_per_page), {"pages": len(reader.pages)}),
        check("closing_page_30_unchanged_structure", qa.get("closing_caption_present") and qa.get("closing_folio_present") and qa.get("closing_alt_present") and qa.get("closing_quote_absent"), {key: qa.get(key) for key in ("closing_caption_present", "closing_folio_present", "closing_alt_present", "closing_quote_absent")}),
    ]

    result = {
        "document": "N01",
        "version": "v9",
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
