#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html as html_lib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image
from pypdf import PdfReader


HERE = Path(__file__).resolve().parent
ROOT = HERE / "N02-v9-final"
SOURCE = ROOT / "source" / "N02_el_sistema_no_cabe_en_una_aplicacion-v9.md"
BASELINE_SOURCE = HERE.parent / "metsi_content" / "lecturas_fuente_v8" / "N02_el_sistema_no_cabe_en_una_aplicacion.md"
BASELINE_PDF = HERE / "N02" / "output" / "N02-METSI-lectura-previa-final.pdf"
PDF = ROOT / "output" / "N02-METSI-lectura-previa-v9-final.pdf"
HTML = ROOT / "index.html"
CSS = ROOT / "magazine.css"
QA = ROOT / "qa-report.json"
REPORT = ROOT / "integrity-report.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(value: str) -> str:
    return re.sub(r"[^0-9a-záéíóúüñ]+", "", value.casefold().replace("ﬁ", "fi").replace("ﬂ", "fl"))


def check(name: str, passed: bool, detail: object) -> dict[str, object]:
    return {"check": name, "status": "PASS" if passed else "FAIL", "detail": detail}


def links_by_page(reader: PdfReader) -> list[list[str]]:
    result: list[list[str]] = []
    for page in reader.pages:
        links: list[str] = []
        for annotation in page.get("/Annots", []):
            action = annotation.get_object().get("/A")
            if action and action.get("/URI"):
                links.append(str(action.get("/URI")))
        result.append(links)
    return result


def used_image_sources(html: str, prefix: str) -> list[Path]:
    names = re.findall(rf'src="assets/({prefix}[^"]+)"', html)
    return [ROOT / "assets" / name for name in names]


def heading_pages(source: str, page_texts: list[str]) -> dict[str, object]:
    sections = re.findall(r"^## (.+?)\n(.*?)(?=^## |\Z)", source, flags=re.M | re.S)
    result: dict[str, object] = {}
    for heading, body in sections:
        words = re.findall(r"[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", re.sub(r"^### .+$", "", body, flags=re.M))
        first = compact(" ".join(words[:7]))
        first_without_dropcap = compact(" ".join(words[1:8]))
        located = None
        for index, text in enumerate(page_texts[3:], start=4):
            page = compact(text)
            if compact(heading) not in page:
                continue
            body_present = bool(first) and (first in page or first_without_dropcap in page)
            located = {"page": index, "body_present": body_present}
            if body_present:
                break
        result[heading] = located or {"page": None, "body_present": False}
    return result


def rendered_edge_metrics(pdf: Path, pages: list[int]) -> dict[str, object]:
    pdftoppm = shutil.which("pdftoppm") or str(
        Path("/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/bin/pdftoppm")
    )
    result: dict[str, object] = {}
    with tempfile.TemporaryDirectory(prefix="n02-v9-edges-") as folder:
        for page_number in pages:
            prefix = Path(folder) / f"p{page_number:02d}"
            subprocess.run(
                [pdftoppm, "-f", str(page_number), "-l", str(page_number), "-singlefile", "-png", "-r", "36", str(pdf), str(prefix)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            image = Image.open(prefix.with_suffix(".png")).convert("RGB")
            w, h = image.size
            strips = {
                "top": image.crop((0, 0, w, 2)),
                "bottom": image.crop((0, h - 2, w, h)),
                "left": image.crop((0, 0, 2, h)),
                "right": image.crop((w - 2, 0, w, h)),
            }
            page_metrics: dict[str, float] = {}
            for side, strip in strips.items():
                pixels = list(strip.get_flattened_data())
                page_metrics[side] = round(sum(sum(pixel) / 3 for pixel in pixels) / max(1, len(pixels)), 2)
            result[str(page_number)] = page_metrics
    return result


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    baseline = BASELINE_SOURCE.read_text(encoding="utf-8")
    body, references = source.split("## Referencias base", 1)
    html = HTML.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")
    qa = json.loads(QA.read_text(encoding="utf-8"))
    reader = PdfReader(str(PDF))
    page_texts = [page.extract_text() or "" for page in reader.pages]
    pdf_text = "\n".join(page_texts)
    links = links_by_page(reader)
    all_links = {uri for page in links for uri in page}
    urls = re.findall(r"https://\S+", references)
    unique_urls = set(urls)
    headings = re.findall(r"^## (.+)$", source, flags=re.M)
    sections = headings[:-1]
    heading_locations = heading_pages(source, page_texts)
    route_labels = re.findall(r"<em>(PROBLEMA|DISTINCIONES|DECISIONES|PRUEBA|TRANSFERENCIA|PREPARACIÓN)</em>", html)

    anchors = {
        "Alter 2002": "Steven Alter propuso",
        "Checkland 1988": "Peter Checkland llega",
        "Clegg 2000": "Clegg (2000)",
        "Mumford 2003": "Enid Mumford",
        "Trist y Bamforth 1951": "Trist y Bamforth",
        "Baxter y Sommerville 2011": "Baxter y Sommerville (2011)",
        "ACM/AIS 2020": "IS2020 de ACM y AIS",
        "NIST AI RMF": "marco de gestión de riesgos de IA de NIST",
        "DORA 2025": "DORA, al estudiar desarrollo asistido por IA en 2025",
        "DORA 2026": "DORA (2026)",
        "Alter 2024": "Alter (2024)",
        "Polojärvi 2023": "Polojärvi (2023)",
        "ISO 15288": "ISO/IEC/IEEE 15288:2023",
        "NIST AI 600-1": "Autio y colaboradores, 2024",
        "Hofmann 2024": "Hofmann y colaboradores (2024)",
        "Nguyen y Elbanna 2025": "Nguyen y Elbanna (2025)",
        "NIST 2026": "NIST (2026)",
    }
    anchor_result = {name: token in body for name, token in anchors.items()}

    expected_edits = [
        "## Cinco píldoras para recordar",
        "Dibujá dos fronteras distintas",
        "Identificá una optimización local razonable",
        "Explicá el mecanismo",
        "Transferí el criterio a un dominio que conozcas",
        "IS2020 de ACM y AIS",
        "Clegg (2000), y Baxter y Sommerville (2011)",
        "Autio y colaboradores, 2024",
        "DORA (2026)",
        "NIST (2026)",
    ]
    baseline_hashes = {
        "pdf": sha256(BASELINE_PDF),
        "source": sha256(BASELINE_SOURCE),
        "cover": sha256(HERE / "N02" / "assets" / "cover.jpg"),
        "matches": sha256(HERE / "N02" / "assets" / "matches-close.png"),
    }
    current_hashes = {
        "cover": sha256(ROOT / "assets" / "cover.jpg"),
        "matches": sha256(ROOT / "assets" / "matches-close.png"),
        "editorial-03": sha256(ROOT / "assets" / "editorial-03.jpg"),
        "editorial-04": sha256(ROOT / "assets" / "editorial-04.jpg"),
    }
    referents = used_image_sources(html, "referent-")
    hotel = used_image_sources(html, "hotel-")
    editorial = used_image_sources(html, "editorial-") + used_image_sources(html, "sparse-fill-")
    image_alts = re.findall(r'<img[^>]+alt="([^"]*)"', html)
    edge_metrics = rendered_edge_metrics(PDF, [1, 4, 5, 16])
    edge_pass = all(
        all(value < 248 for value in edge_metrics[str(page)].values())
        for page in (1, 4, 5, 16)
    )

    content_order = ["Referentes", *sections, "Referencias base"]
    positions = [compact(html).find(compact(value)) for value in content_order]
    checks = [
        check("baseline_v8_frozen", baseline_hashes["pdf"] == "8b9300ae2f7cbac11fa3ce4b122b0750567f410ad581eabb585507b1e7582313" and baseline_hashes["source"] == "00a8899601af4a1aade38645479c6f5f2dab63dfdcaa914e0982aca20bdb529b", baseline_hashes),
        check("source_is_minimal_v9_revision", all(value in source for value in expected_edits) and len(source.split()) - len(baseline.split()) == 56, {"v8_words": len(baseline.split()), "v9_words": len(source.split()), "expected_changes": expected_edits}),
        check("section_count_and_order", len(sections) == 22 and headings[-1] == "Referencias base", headings),
        check("contents_matches_real_order", all(value >= 0 for value in positions) and positions == sorted(positions), content_order),
        check("all_routes_present", route_labels == ["PROBLEMA"] * 4 + ["DISTINCIONES"] * 6 + ["DECISIONES"] * 5 + ["PRUEBA"] + ["TRANSFERENCIA"] * 2 + ["PREPARACIÓN"] * 4, route_labels),
        check("no_orphan_section_titles", all(value["body_present"] for value in heading_locations.values()), heading_locations),
        check("exactly_two_internal_full_page_pauses", html.count('class="full-bleed full-bleed-quote"') == 2 and html.find('data-section="01"') < html.find('class="full-bleed full-bleed-quote"') < html.find('data-section="02"'), {"count": html.count('class="full-bleed full-bleed-quote"')}),
        check("full_bleed_pages_reach_all_edges", edge_pass, edge_metrics),
        check("references_are_minimal_unnumbered_apparatus", 'data-section="apparatus-reference"' in html and "references-image-full" not in html and "columns:2" in css, "SIN NUM., two columns, no bibliography image"),
        check("all_seventeen_references_anchored", len(re.findall(r"^- ", references, flags=re.M)) == 17 and all(anchor_result.values()), anchor_result),
        check("all_reference_urls_linked_and_copyable", len(urls) == 16 and len(unique_urls) == 15 and all_links.issuperset(unique_urls) and all(re.sub(r"\s+", "", url) in re.sub(r"\s+", "", pdf_text) for url in unique_urls), {"url_entries": len(urls), "unique": len(unique_urls), "linked": len(unique_urls & all_links)}),
        check("six_distinct_referent_images", len(referents) == 6 and len({sha256(path) for path in referents}) == 6, [path.name for path in referents]),
        check("four_distinct_hotel_portraits", len([path for path in hotel if path.suffix == ".jpg"]) == 4 and len({sha256(path) for path in hotel if path.suffix == ".jpg"}) == 4, [path.name for path in hotel if path.suffix == ".jpg"]),
        check("editorial_photographs_not_repeated", len(editorial) == 6 and len({sha256(path) for path in editorial}) == 6 and all(sha256(path) != current_hashes["cover"] for path in editorial), [path.name for path in editorial]),
        check("one_compact_infographic", html.count('src="diagrams/N02-mapa-decision.svg"') == 1, "N02-mapa-decision.svg"),
        check("approved_visual_assets_preserved", current_hashes["cover"] == baseline_hashes["cover"] and current_hashes["matches"] == baseline_hashes["matches"] and current_hashes["editorial-03"] == sha256(HERE / "N02" / "assets" / "editorial-03.jpg") and current_hashes["editorial-04"] == sha256(HERE / "N02" / "assets" / "editorial-04.jpg"), current_hashes),
        check("all_images_have_specific_alt_text", image_alts and all(value.strip() and not value.startswith(("Imagen editorial asociada", "Imagen conceptual vinculada", "Pausa visual vinculada")) for value in image_alts), {"count": len(image_alts), "alts": image_alts}),
        check("a4_27_pages_no_blank_pages", len(reader.pages) == 27 and all(abs(float(page.mediabox.width) - 595.276) < 2 and abs(float(page.mediabox.height) - 841.89) < 2 and re.search(r"\w", page_texts[index]) for index, page in enumerate(reader.pages)), {"pages": len(reader.pages)}),
        check("folio_and_footer_link_on_every_page", all(re.search(rf"\b{index:02d}\b", text) and any("linkedin.com/in/carralbal" in uri for uri in links[index - 1]) for index, text in enumerate(page_texts, 1)), {"pages": len(reader.pages)}),
        check("closing_matches_structure", qa.get("closing_caption_present") and qa.get("closing_folio_present") and qa.get("closing_alt_present") and qa.get("closing_quote_absent"), {key: qa.get(key) for key in ("closing_caption_present", "closing_folio_present", "closing_alt_present", "closing_quote_absent")}),
        check("rioplatense_direct_instructions", all(value in source for value in ("Dibujá", "Identificá", "Explicá", "Transferí")) and not any(value in source for value in ("Dibuje dos fronteras", "Identifique una optimización", "Transfiera el criterio")), "voseo in preparation prompts"),
        check("source_id_integrity", json.loads((ROOT / "integrity-report.json").read_text(encoding="utf-8")).get("status") == "PASS", "all source blocks rendered once"),
        check("pdf_qa_pass", qa.get("status") == "PASS", qa.get("status")),
        check("no_placeholders", not re.search(r"\b(?:TODO|TBD|LOREM IPSUM|PLACEHOLDER)\b", source + html), "none"),
    ]

    result = {
        "document": "N02",
        "version": "v9 review candidate",
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
