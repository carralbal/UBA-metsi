#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

from pypdf import PdfReader


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "N01" / "source" / "N01_metodologia_sin_recetas-v8.md"
CURATION = HERE / "N01" / "image-curation" / "image-manifest.json"
ROOT = HERE / "N01-v8-final"
HTML = ROOT / "index.html"
PDF = ROOT / "output" / "N01-METSI-lectura-previa-v8-final.pdf"
QA = ROOT / "qa-report.json"
REPORT = ROOT / "integrity-report.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(name: str, passed: bool, detail: object) -> dict:
    return {"check": name, "status": "PASS" if passed else "FAIL", "detail": detail}


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    body, references = source.split("## Referencias base", 1)
    html = HTML.read_text(encoding="utf-8")
    curation = json.loads(CURATION.read_text(encoding="utf-8"))
    qa = json.loads(QA.read_text(encoding="utf-8"))
    reader = PdfReader(str(PDF))

    anchors = {
        "Checkland y Poulter": "Checkland y Poulter",
        "Schön": "Schön describió",
        "Argyris y Schön": "Argyris y Schön distinguen",
        "March": "March formuló",
        "Suchman": "Lucy Suchman mostró",
        "Senge": "Senge agrega",
        "ISO 24748": "ISO/IEC/IEEE 24748-1:2024",
        "PMBOK 8": "PMBOK Guide, octava edición",
        "NIST AI RMF": "AI Risk Management Framework 1.0 de NIST",
        "NIST GenAI": "perfil de NIST para inteligencia artificial generativa",
        "SWEBOK V4.0a": "SWEBOK Guide V4.0a",
        "ISO 15288": "ISO/IEC/IEEE 15288:2023",
        "EU AI Act": "Reglamento de Inteligencia Artificial de la Unión Europea",
        "DORA 2025": "informe DORA 2025",
        "IS2020": "modelo curricular IS2020 de ACM y AIS",
    }
    anchor_result = {name: token in body for name, token in anchors.items()}

    assets = curation["assets"]
    asset_hashes = [entry["sha256"] for entry in assets]
    selected_paths = [HERE / "N01" / "image-curation" / entry["file"] for entry in assets]
    source_ids = [entry["source_id"] for entry in assets]
    image_files_valid = all(path.exists() and sha256(path) == entry["sha256"] for path, entry in zip(selected_paths, assets))
    other_image_hashes: set[str] = set()
    for code in ["N00", "N01", "N02", "N03", "N04", "N05", "N06", "N07", "N08", "N09", "N10"]:
        for path in (HERE / code).rglob("*"):
            if not path.is_file() or path.suffix.casefold() not in {".jpg", ".jpeg", ".png"}:
                continue
            if path in selected_paths:
                continue
            other_image_hashes.add(sha256(path))
    cross_document_duplicates = sorted(set(asset_hashes) & other_image_hashes)

    hotel_files = sorted((ROOT / "assets").glob("hotel-*"))
    hotel_portraits = [path for path in hotel_files if path.name != "hotel-horizonte.png"]
    referent_portraits = sorted((ROOT / "assets").glob("referent-*"))

    page_texts = [(page.extract_text() or "") for page in reader.pages]
    pdf_text = "\n".join(page_texts)
    links_per_page = []
    for page in reader.pages:
        links = []
        for annotation in page.get("/Annots", []):
            action = annotation.get_object().get("/A")
            if action and action.get("/URI"):
                links.append(str(action.get("/URI")))
        links_per_page.append(links)

    old_pdf_clean = subprocess.run(
        ["git", "diff", "--quiet", "--", "N01/output/N01-METSI-lectura-previa-final.pdf"],
        cwd=HERE,
        check=False,
    ).returncode == 0

    checks = [
        check("source_minimum_depth", len(source.split()) >= 7500, {"words": len(source.split()), "minimum": 7500}),
        check("source_sections", len(re.findall(r"^## ", source, flags=re.M)) == 29, {"sections": len(re.findall(r"^## ", source, flags=re.M))}),
        check("references_complete", len(re.findall(r"^- ", references, flags=re.M)) == 15, {"entries": len(re.findall(r"^- ", references, flags=re.M))}),
        check("references_anchored", all(anchor_result.values()), anchor_result),
        check("no_em_dash", "—" not in source, {"count": source.count("—")}),
        check("two_full_page_quotes", html.count('full-bleed full-bleed-quote') == 2, {"count": html.count('full-bleed full-bleed-quote')}),
        check("six_hotel_voices", len(re.findall(r'hotel-voice hotel-voice-\d+', html)) == 6, {"count": len(re.findall(r'hotel-voice hotel-voice-\d+', html))}),
        check("six_distinct_hotel_portraits", len(hotel_portraits) == 6 and len({sha256(path) for path in hotel_portraits}) == 6, {"files": [path.name for path in hotel_portraits]}),
        check("six_distinct_referents", len(referent_portraits) == 6 and len({sha256(path) for path in referent_portraits}) == 6, {"files": [path.name for path in referent_portraits]}),
        check("minimal_references_layout", "references-image-full" not in html and 'data-section="apparatus-reference"' in html, {"image_plate": "references-image-full" in html, "apparatus": 'data-section="apparatus-reference"' in html}),
        check("contents_complete", len(re.findall(r'<li><b>\d{2}</b>', html)) == 28 and html.count("SIN NUM.") >= 2, {"numbered": len(re.findall(r'<li><b>\d{2}</b>', html)), "sin_num_mentions": html.count("SIN NUM.")}),
        check("image_manifest", len(assets) == 8 and len(asset_hashes) == len(set(asset_hashes)) and len(source_ids) == len(set(source_ids)) and image_files_valid, {"assets": len(assets), "hashes_unique": len(asset_hashes) == len(set(asset_hashes)), "source_ids_unique": len(source_ids) == len(set(source_ids)), "files_valid": image_files_valid}),
        check("images_unique_across_n00_n10", not cross_document_duplicates, {"duplicate_hashes": cross_document_duplicates}),
        check("pdf_a4", len(reader.pages) == 30 and all(abs(float(page.mediabox.width) - 595.276) < 2 and abs(float(page.mediabox.height) - 841.89) < 2 for page in reader.pages), {"pages": len(reader.pages)}),
        check("pdf_qa", qa.get("status") == "PASS", qa.get("status")),
        check("folios_and_footer_links", all(any("linkedin.com/in/carralbal" in uri for uri in links) for links in links_per_page), {"pages_with_footer_link": sum(any("linkedin.com/in/carralbal" in uri for uri in links) for links in links_per_page), "pages": len(reader.pages)}),
        check("closing_structure", qa.get("closing_caption_present") and qa.get("closing_folio_present") and qa.get("closing_alt_present") and qa.get("closing_quote_absent"), {key: qa.get(key) for key in ("closing_caption_present", "closing_folio_present", "closing_alt_present", "closing_quote_absent")}),
        check("pdf_text_complete", all(title in pdf_text for title in ("Pregunta profesional", "Aplicación a Hotel Horizonte", "Preguntas de preparación", "Referencias base")), {"required_titles": 4}),
        check("approved_baseline_preserved", old_pdf_clean, {"path": "N01/output/N01-METSI-lectura-previa-final.pdf"}),
    ]

    result = {
        "document": "N01",
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
