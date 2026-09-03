#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image
from pypdf import PdfReader


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "N01" / "source" / "N01_metodologia_sin_recetas-v12.md"
CURATION = HERE / "N01" / "image-curation" / "image-manifest.json"
ROOT = HERE / "N01-v12-final"
HTML = ROOT / "index.html"
CSS = ROOT / "magazine.css"
DIAGRAM = ROOT / "diagrams" / "N01-mapa-decision.svg"
PDF = ROOT / "output" / "N01-METSI-lectura-previa-v12-final.pdf"
BASELINE_PDF = HERE / "N01-v11-final" / "output" / "N01-METSI-lectura-previa-v11-final.pdf"
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


def page_occupancies(pdf: Path) -> list[float]:
    bundled = Path("/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/bin/pdftoppm")
    command = shutil.which("pdftoppm") or str(bundled)
    with tempfile.TemporaryDirectory(prefix="n01-v12-occupancy-") as folder:
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
            span = (max(active_rows) - min(active_rows) + 1) / height if active_rows else 0.0
            result.append(round(span, 3))
        return result


def changed_visual_pages(baseline: Path, candidate: Path) -> list[int]:
    bundled = Path("/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/bin/pdftoppm")
    command = shutil.which("pdftoppm") or str(bundled)
    with tempfile.TemporaryDirectory(prefix="n01-v12-visual-regression-") as folder:
        root = Path(folder)
        for label, pdf in (("baseline", baseline), ("candidate", candidate)):
            subprocess.run(
                [command, "-png", "-r", "45", str(pdf), str(root / label)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        changed: list[int] = []
        for page_number in range(1, 30):
            old = Image.open(root / f"baseline-{page_number:02d}.png").convert("RGB")
            new = Image.open(root / f"candidate-{page_number:02d}.png").convert("RGB")
            from PIL import ImageChops
            if ImageChops.difference(old, new).getbbox():
                changed.append(page_number)
        return changed


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    source_unchanged = source == (HERE / "N01" / "source" / "N01_metodologia_sin_recetas-v11.md").read_text(encoding="utf-8")
    body, references = source.split("## Referencias base", 1)
    html = HTML.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")
    diagram = DIAGRAM.read_text(encoding="utf-8")
    qa = json.loads(QA.read_text(encoding="utf-8"))
    curation = json.loads(CURATION.read_text(encoding="utf-8"))
    reader = PdfReader(str(PDF))
    raw_page_texts = [page.extract_text() or "" for page in reader.pages]
    page_texts = [normalized(text) for text in raw_page_texts]
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
        "https://doi.org/10.1287/orsc.2.1.71",
        "https://doi.org/10.1017/CBO9780511625510",
        "https://www.iso.org/standard/84709.html",
        "https://www.pmi.org/standards/pmbok",
        "https://doi.org/10.6028/NIST.AI.100-1",
        "https://doi.org/10.6028/NIST.AI.600-1",
        "https://www.computer.org/education/bodies-of-knowledge/software-engineering",
        "https://www.iso.org/standard/81702.html",
        "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
        "https://dora.dev/research/2025/dora-report/",
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

    frozen_paths = [
        "N01-v8-final",
        "N01/source/N01_metodologia_sin_recetas-v8.md",
        "N01-v9-final",
        "N01/source/N01_metodologia_sin_recetas-v9.md",
        "N01-v10-final",
        "N01/source/N01_metodologia_sin_recetas-v10.md",
        "N01-v11-final",
        "N01/source/N01_metodologia_sin_recetas-v11.md",
    ]
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
    page_27 = page_texts[26]
    page_10 = page_texts[9]
    page_11 = page_texts[10]
    page_12 = page_texts[11]
    page_12_lines = [normalized(line) for line in raw_page_texts[11].splitlines() if normalized(line)]
    cover_lines = [normalized(line) for line in (reader.pages[0].extract_text() or "").splitlines() if normalized(line)]
    occupancies = page_occupancies(PDF)
    visual_changes = changed_visual_pages(BASELINE_PDF, PDF)
    pills_title_at = compact(page_27).find(compact("Cinco píldoras para recordar"))
    pills_first_item_at = compact(page_27).find(compact("Una metodología rigurosa vuelve visible el juicio"))

    checks = [
        check("v8_through_v11_baselines_frozen", baseline_frozen, frozen_paths),
        check("source_text_byte_identical_to_v11", source_unchanged, sha256(SOURCE)),
        check("source_depth_stable", 7500 <= len(source.split()) <= 8000, {"words": len(source.split())}),
        check("section_count_and_order", len(headings) == 29 and headings[:5] == expected_opening, {"sections": len(headings), "opening": headings[:5]}),
        check("route_visible_all_sections", len(route_labels) == 28 and route_labels[:4] == ["PROBLEMA"] * 4 and route_labels[4:8] == ["DISTINCIONES"] * 4 and route_labels[8:17] == ["DECISIONES"] * 9 and route_labels[17:20] == ["PRUEBA"] * 3 and route_labels[20:24] == ["TRANSFERENCIA"] * 4 and route_labels[24:] == ["PREPARACIÓN"] * 4, {"count": len(route_labels), "labels": route_labels}),
        check("no_orphan_section_headings", all(item["first_body_words_present"] for item in orphan_result.values()), orphan_result),
        check("statement_pages_preserved", html.count('full-bleed full-bleed-quote') == 2 and 'data-section="01"' in html, {"black_quote_pages": html.count('full-bleed full-bleed-quote'), "opening_statement": 'data-section="01"' in html}),
        check("cover_exact_three_lines", "Metodología sin recetas:<br>intervenir cuando el problema<br>todavía no está claro" in html and ".cover-n01 .cover-title{width:160mm}" in css, "three explicit lines"),
        check("page24_caption_and_reading_order", 0 <= p24_title < p24_caption < p24_body, {"title": p24_title, "caption": p24_caption, "body": p24_body}),
        check("method_diagram_readable_and_complete", "font-size=\"24\"" in diagram and all(compact(word) in compact(diagram) for word in ("Amplifica", "capacidad", "sustituir", "juicio")) and "…" not in diagram, {"width_rule": ".n01-method-architecture{width:100%" in css}),
        check("pill_ornament_removed", "pill-summary-icon" not in html and "Cinco píldoras para recordar" in html, "no decorative 01–05 icon"),
        check("references_complete_and_anchored", len(re.findall(r"^- ", references, flags=re.M)) == 15 and all(anchor_result.values()), {"entries": len(re.findall(r"^- ", references, flags=re.M)), "anchors": anchor_result}),
        check("all_eleven_reference_links", all_links.issuperset(expected_fixed_links) and len(expected_fixed_links) == 11, sorted(expected_fixed_links & all_links)),
        check("url_copy_layer_preserves_hyphens", all(re.sub(r"\s+", "", url) in re.sub(r"\s+", "", pdf_text) for url in expected_fixed_links) and all(token not in re.sub(r"\s+", "", pdf_text) for token in ("eurlex.europa.eu", "/wpcontent/", "bodiesofknowledge")), {"checked": len(expected_fixed_links)}),
        check("cover_meta_two_ordered_text_runs", "LECTURA PREVIA" in cover_lines and "EDICIÓN 2026" in cover_lines and cover_lines.index("LECTURA PREVIA") < cover_lines.index("EDICIÓN 2026"), cover_lines[:8]),
        check("page12_widow_removed_without_rewriting", compact("Supongamos que una gerenta afirma") not in compact(page_11) and page_12_lines[:2] and compact("Un ejemplo completo: de una frase vaga a una decisión comprobable") in compact(page_12_lines[0]) and compact("Supongamos que una gerenta afirma") in compact(page_12_lines[1]), page_12_lines[:6]),
        check("page27_pills_reading_order", 0 <= pills_title_at < pills_first_item_at, {"title": pills_title_at, "first_item": pills_first_item_at}),
        check("page10_ghost_label_removed", "se apoya en" not in page_10.casefold() and "se apoya en" not in diagram.casefold(), "residual connector label absent from SVG and PDF text layer"),
        check("visual_changes_limited_to_reflow_pages", visual_changes == [11, 12], {"changed_pages": visual_changes, "unchanged_pages": 27}),
        check("checkland_isbn_no_wiley_url", "ISBN 978-0-470-02554-3" in source and "wiley.com" not in source.casefold(), "ISBN 978-0-470-02554-3"),
        check("referents_match_references", all(referents_match.values()), referents_match),
        check("pmbok8_precision", all(token in body for token in ("doce principios de la séptima en seis", "dominios de desempeño de ocho a siete", "Áreas de Foco", "cuarenta procesos no prescriptivos")), "6 principles, 7 domains, Focus Areas, 40 processes"),
        check("revisability_named_and_reused", source.casefold().count("criterio de revisabilidad") >= 5 and "criterio de revisabilidad** es la exigencia de declarar qué evidencia adversa podría cambiar una explicación, un alcance o una decisión" in source, {"count": source.casefold().count("criterio de revisabilidad")}),
        check("voice_caption_updated", "Seis relatos verdaderos que ninguno explica por sí solo." in html and "Seis relatos verdaderos que ninguno explica solo." not in html, "caption with por sí"),
        check("sections_23_25_two_columns", all(f'section[data-section="{idx}"] .section-body{{columns:2;column-count:2' in css for idx in (23, 24, 25)), "sections 23, 24 and 25"),
        check("six_conflicting_hotel_voices", all(token in html for token in ("directorio espera una fecha hoy", "campaña tiene que salir esta semana", "once habitaciones", "dos grupos juntos", "Los estados viajaron sin error", "ocho habitaciones")), {"voices": 6}),
        check("six_distinct_hotel_portraits", len(hotel_portraits) == 6 and len({sha256(path) for path in hotel_portraits}) == 6, [path.name for path in hotel_portraits]),
        check("six_distinct_referent_portraits", len(referent_portraits) == 6 and len({sha256(path) for path in referent_portraits}) == 6, [path.name for path in referent_portraits]),
        check("questions_and_delivery", "¿Qué permite distinguir una adaptación rigurosa de una improvisación conveniente?" in source and "¿Qué outcome haría que el sistema de turnos mejore el acceso en lugar de reforzar una barrera previa?" in source and "traer respondidas por escrito dos de las siete preguntas" in source, "Q3 impersonal, Q7 health case, written delivery"),
        check("impersonal_register", not re.search(r"\busted(?:es)?\b|\bdistinguiría\b", source, flags=re.I), "no usted or distinguiría"),
        check("synthesis_last_paragraph_complete_on_page_27", compact("N01 deja entonces una capacidad inicial y una pregunta abierta") in compact(page_27) and compact("hacen posible, o imposible, la promesa completa") in compact(page_27), "last paragraph moved as a complete unit"),
        check("glossary_three_columns_complete_and_legible", "column-count:3" in css and "font-size:9.7pt" in css and all(compact(term) in compact(glossary_page) for term in glossary_terms) and compact("Preguntas de preparación") not in compact(glossary_page), {"physical_page": glossary_page_index + 1, "terms": len(glossary_terms)}),
        check("assets_preserved", len(assets) == 8 and assets_valid, {"assets": len(assets), "hashes_valid": assets_valid}),
        check("pdf_a4_exactly_29_pages", len(reader.pages) == 29 and all(abs(float(page.mediabox.width) - 595.276) < 2 and abs(float(page.mediabox.height) - 841.89) < 2 for page in reader.pages), {"pages": len(reader.pages)}),
        check("no_page_less_than_half_filled", len(occupancies) == 29 and min(occupancies, default=0) >= .5, {"minimum": min(occupancies, default=0), "page": occupancies.index(min(occupancies)) + 1 if occupancies else None, "occupancies": occupancies}),
        check("pdf_qa_pass", qa.get("status") == "PASS", qa.get("status")),
        check("folios_and_footer_links", all(any("linkedin.com/in/carralbal" in uri for uri in links) for links in links_per_page), {"pages": len(reader.pages)}),
        check("closing_page_unchanged_structure", qa.get("closing_caption_present") and qa.get("closing_folio_present") and qa.get("closing_alt_present") and qa.get("closing_quote_absent"), {key: qa.get(key) for key in ("closing_caption_present", "closing_folio_present", "closing_alt_present", "closing_quote_absent")}),
    ]

    result = {
        "document": "N01",
        "version": "v12",
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
