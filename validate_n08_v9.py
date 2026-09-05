#!/usr/bin/env python3
"""Validador determinista y de sólo lectura para el cierre METSI N08 v9.

Lee la fuente canónica, el paquete editable, los manifiestos, el PDF crudo y el
PDF final. Imprime un único informe JSON. No modifica ningún artefacto. Devuelve
0 para PASS, 1 para una guarda incumplida y 2 para un error de ejecución.

El número de páginas se toma del plan de compaginación del paquete, de modo que
la primera compaginación pueda fijarlo sin adivinarlo. También puede pasarse con
``--expected-pages``; una vez cerrada la edición ambas cifras deben coincidir.
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import pdfplumber
from PIL import Image
from pypdf import PdfReader

from validate_n07_v9 import (
    HtmlInventory,
    block_is_rendered,
    compact,
    cover_tone,
    dark_full_page_background,
    first_fragment,
    full_bleed_image,
    image_monochrome,
    links_by_page,
    local_reference_issues,
    page_extents,
    page_image_alts,
    package_relative_report_paths,
    percentile,
    result,
    sha256,
    structure_figures,
)


HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE / "N08-v9-final"
EXPECTED_SOURCE_SHA = "328d2858fbe170bee35f17ada425fdb78b0e34a395bc4992ed33fb5b2910b8b9"
EXPECTED_N07_PDF_SHA = "b174fe88d67bfa717d93139d1039db373a44f39f9f0c92fd4ee06e281baedcd6"
EXPECTED_DIAGRAM_SHA = "ec883deab6147e6f1fa85048e631be14650799177c008f71f9e030cabd4029e6"
EXPECTED_BLOCKS = 256
EXPECTED_A4 = (594.96, 841.92)
EXPECTED_SECTIONS = [
    "Pregunta profesional",
    "El puente que se sostenía gracias a gestos que nadie había diseñado",
    "Tesis",
    "De N07 a N08: de lo dicho a lo realizado",
    "Movimiento 1 · Ver la diferencia entre procedimiento y trabajo realizado",
    "Movimiento 2 · Observar episodios sin confundir descripción e interpretación",
    "Movimiento 3 · Transformar lo observado sin destruir su función",
    "De N08 a N09: del trabajo realizado al recorrido vivido",
    "Errores frecuentes y consecuencias profesionales",
    "Límites y tensiones",
    "Síntesis",
    "Cinco píldoras para recordar",
    "Glosario esencial",
    "Preguntas de preparación",
]
EXPECTED_ROUTES = (
    ["PROBLEMA"] * 4
    + ["DISTINCIONES", "DECISIONES", "PRUEBA"]
    + ["TRANSFERENCIA"] * 2
    + ["PREPARACIÓN"] * 5
)
EXPECTED_REFERENTS = [
    ("Lucy A. Suchman", "assets/referent-lucy-suchman.jpg"),
    ("Edwin Hutchins", "assets/referent-edwin-hutchins.jpg"),
    ("Reva Schwartz", "assets/referent-reva-schwartz.jpg"),
    ("Elham Tabassi", "assets/referent-elham-tabassi.jpg"),
    ("Kamie Roberts", "assets/referent-kamie-roberts.jpg"),
    ("Martin Stanley", "assets/referent-martin-stanley.jpg"),
]
EXPECTED_EDITORIAL = [f"assets/editorial-0{number}.png" for number in range(1, 5)]
EXPECTED_PAUSES = ["assets/pause-01.png", "assets/pause-02.png"]
EXPECTED_INTERNAL_IMAGES = [Path(value).name for value in EXPECTED_EDITORIAL + EXPECTED_PAUSES]
EXPECTED_URLS = {
    "https://doi.org/10.1111/j.1533-8525.1988.tb01249.x",
    "https://doi.org/10.1023/A:1008651105359",
    "https://doi.org/10.1177/001872675100400101",
    "https://doi.org/10.6028/NIST.AI.600-1",
    "https://doi.org/10.54394/HETP0387",
    "https://doi.org/10.1787/287c13c4-en",
}
EXPECTED_PAUSE_QUOTES = [
    "Si sólo se modela lo prescripto, se automatiza una ficción.",
    "Supervisión humana sin tiempo, información, autoridad y alternativa es una ficción.",
]
EXPECTED_PAUSE_ALTS = [
    "Un operador observa desde una cabina un puente con tránsito, un ciclista y una barcaza en el río.",
    "Una recepcionista sostiene una tarjeta en blanco y pausa la confirmación mientras una trabajadora de Housekeeping prepara el servicio al fondo.",
]
EXPECTED_COVER_ALT = (
    "Dos trabajadoras argentinas coordinan tareas en el umbral de una habitación de hotel, "
    "mientras una pared y un corredor dejan amplio espacio visual a la izquierda."
)
EXPECTED_CONTENTS_ALT = (
    "Varias manos organizan una libreta, una radio, una llave, una tarjeta y un plano "
    "sobre una mesa de trabajo."
)
EXPECTED_INFOGRAPHIC_ALT = (
    "Registro en siete capas que relaciona contexto, evento, interpretación, incertidumbre, "
    "función, consecuencia y decisión La cadena conserva la diferencia entre lo observado "
    "y lo inferido, y muestra qué evidencia permite convertir un episodio en una decisión revisable."
)
EXPECTED_CLOSING_ALT = (
    "Diez fósforos dispuestos en secuencia vertical, desde intactos hasta consumidos "
    "y convertidos en ceniza."
)
EXPECTED_CLOSING_CAPTION = (
    "La secuencia vuelve visible que toda intervención consume recursos, deja huellas "
    "y necesita un criterio de cierre."
)
EXPECTED_COUNTS = {"pills": 5, "glossary": 16, "questions": 6, "references": 12}
EXPECTED_METADATA = {
    "/Title": "N08 · Observar el trabajo invisible",
    "/Author": "Diego Carralbal",
    "/Subject": "Metodología de Sistemas de Información · FCE · UBA",
}
REQUIRED_FILES = [
    "HANDOFF.md",
    "CHANGELOG.md",
    "PUBLICATION-READINESS.md",
    "visual-audit.md",
    "validation-v9.json",
    "index.html",
    "magazine.css",
    "metsi.css",
    "manifest.json",
    "document.json",
    "source-manifest.json",
    "integrity-report.json",
    "qa-report.json",
    "image-generation-manifest.json",
    "image-rights-manifest.json",
    "image-manifest.json",
    "page-spread-plan.json",
    "provenance/regression-lock.json",
    "provenance/cover-image-premium-bw-v1.md",
    "provenance/editorial-image-provenance.md",
    "provenance/referent-portrait-sources.md",
    "source/N08_observar_el_trabajo_invisible-content-final.md",
    "diagrams/N08-mapa-decision.svg",
    "diagrams/N08-mapa-decision.json",
    "infographic-work-layer/n08-work-layers.svg",
    "infographic-work-layer/n08-work-layers.png",
    "infographic-work-layer/content-manifest.json",
    "infographic-work-layer/alt-text.md",
    "infographic-work-layer/qa-report.md",
    "infographic-work-layer/review.html",
    "output/N08-METSI-lectura-previa-v9.pdf",
    "output/N08-METSI-lectura-previa-v9-final.pdf",
]


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Se esperaba un objeto JSON en {path}")
    return value


def source_counts(source_text: str) -> dict[str, int]:
    _, after_pills = source_text.split("## Cinco píldoras para recordar", 1)
    pills, after_glossary = after_pills.split("## Glosario esencial", 1)
    glossary, after_questions = after_glossary.split("## Preguntas de preparación", 1)
    questions, references = after_questions.split("## Referencias base", 1)
    return {
        "pills": len(re.findall(r"^\d+\. \*\*", pills, re.M)),
        "glossary": len(re.findall(r"^- \*\*", glossary, re.M)),
        "questions": len(re.findall(r"^\d+\. ", questions, re.M)),
        "references": len(re.findall(r"^- ", references, re.M)),
    }


def find_unique_page(page_texts: list[str], value: str) -> int | None:
    needle = compact(value)
    pages = [number for number, text in enumerate(page_texts, 1) if needle in compact(text)]
    return pages[0] if len(pages) == 1 else None


def find_pages(page_texts: list[str], value: str) -> list[int]:
    needle = compact(value)
    return [number for number, text in enumerate(page_texts, 1) if needle in compact(text)]


def heading_body_alignment(entries: list[dict[str, Any]], page_texts: list[str]) -> dict[str, Any]:
    compact_pages = [compact(text) for text in page_texts]
    records: list[dict[str, Any]] = []
    for index, entry in enumerate(entries[:-1]):
        if entry.get("kind") not in {"heading-2", "heading-3"}:
            continue
        following = entries[index + 1]
        heading = compact(str(entry.get("text", "")))
        fragment = first_fragment(str(following.get("text", "")))
        heading_pages = {
            number for number, text in enumerate(compact_pages, 1) if heading and heading in text
        }
        body_pages = {
            number for number, text in enumerate(compact_pages, 1) if fragment and fragment in text
        }
        shared = sorted(heading_pages & body_pages)
        records.append(
            {
                "source_id": entry.get("source_id"),
                "heading": entry.get("text"),
                "following_source_id": following.get("source_id"),
                "same_pages": shared,
            }
        )
    failed = [record for record in records if not record["same_pages"]]
    return {"passed": bool(records) and not failed, "checked": len(records), "failed": failed}


def references_two_columns(page: pdfplumber.page.Page) -> dict[str, Any]:
    expected = {
        "Suchman", "Beyer", "Hollnagel", "Dekker", "Weick", "Hutchins",
        "Strauss", "Star", "Trist", "Autio", "Gmyrek", "Milanez",
    }
    positions: dict[str, float] = {}
    for word in page.extract_words(use_text_flow=False):
        token = re.sub(r"[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", "", str(word.get("text", "")))
        if token in expected and token not in positions:
            positions[token] = round(float(word.get("x0", 0.0)), 2)
    # La caja de referencias ocupa dos columnas de 238 pt separadas por un
    # medianil estrecho. El segundo eje comienza en x=306,47 pt, levemente antes
    # del 53 % geométrico de la página porque la caja completa está centrada.
    left = {key: value for key, value in positions.items() if value < page.width * 0.47}
    right = {key: value for key, value in positions.items() if value > page.width * 0.48}
    return {
        "passed": set(positions) == expected and len(left) >= 5 and len(right) >= 5,
        "positions": positions,
        "left": left,
        "right": right,
    }


def generated_asset_audit(root: Path, data: dict[str, Any], html: str) -> dict[str, Any]:
    expected = EXPECTED_EDITORIAL + EXPECTED_PAUSES
    records = {
        str(record.get("file")): record
        for record in data.get("assets", [])
        if isinstance(record, dict)
    }
    details: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    for relative in expected:
        record = records.get(relative)
        path = root / relative
        reasons: list[str] = []
        if not record:
            reasons.append("falta registro de procedencia")
        if not path.is_file():
            reasons.append("falta el activo")
        if path.is_file():
            info = image_monochrome(path)
            details.append(info)
            if not info["monochrome"]:
                reasons.append("el activo no es monocromo nativo")
            if record and record.get("sha256") != info["sha256"]:
                reasons.append("sha256 no coincide")
            if record and [record.get("width"), record.get("height")] != info["size"]:
                reasons.append("dimensiones no coinciden")
        if record and not record.get("production_brief"):
            reasons.append("falta brief de producción")
        if record and not record.get("alt"):
            reasons.append("falta texto alternativo")
        if html.count(relative) != 1:
            reasons.append(f"el HTML lo referencia {html.count(relative)} veces")
        if reasons:
            invalid.append({"file": relative, "reasons": reasons})
    hashes = [item["sha256"] for item in details]
    expected_roles = {
        **{value: "editorial-photo" for value in EXPECTED_EDITORIAL[:3]},
        EXPECTED_EDITORIAL[3]: "contents-photo",
        **{value: "full-bleed-pause" for value in EXPECTED_PAUSES},
    }
    roles_ok = all(records.get(path, {}).get("role") == role for path, role in expected_roles.items())
    passed = (
        not invalid
        and len(details) == 6
        and len(set(hashes)) == 6
        and roles_ok
        and data.get("generator") == "OpenAI ImageGen"
        and "blanco y negro" in str(data.get("editorial_rule", "")).casefold()
    )
    return {"passed": passed, "assets": details, "invalid": invalid, "roles_ok": roles_ok}


def referent_rights_audit(
    root: Path,
    inventory: HtmlInventory,
    manifest: dict[str, Any],
    rights: dict[str, Any],
    pdf_page_3_text: str,
) -> dict[str, Any]:
    actual = [(item.get("name", "").strip(), item.get("src", "")) for item in inventory.contributors]
    main_records = [item for item in manifest.get("portrait_references", []) if isinstance(item, dict)]
    rights_records = [item for item in rights.get("assets", []) if isinstance(item, dict)]
    rights_by_file = {str(item.get("file", "")): item for item in rights_records}
    invalid: list[dict[str, Any]] = []
    hashes: list[str] = []
    for name, relative in EXPECTED_REFERENTS:
        path = root / relative
        main = next(
            (
                item for item in main_records
                if "assets/" + str(item.get("file", "")).removeprefix("assets/") == relative
            ),
            None,
        )
        right = rights_by_file.get(relative)
        reasons: list[str] = []
        if not path.is_file():
            reasons.append("falta retrato")
        else:
            with Image.open(path) as image:
                size, mode = list(image.size), image.mode
            digest = sha256(path)
            hashes.append(digest)
            if size != [720, 720] or mode not in {"L", "LA"}:
                reasons.append(f"se esperaba 720 × 720 gris, se obtuvo {size} {mode}")
            if main and main.get("sha256") != digest:
                reasons.append("sha256 del manifiesto principal no coincide")
            if right and right.get("sha256") != digest:
                reasons.append("sha256 del manifiesto de derechos no coincide")
        if not main:
            reasons.append("falta registro en manifest.json")
        if not right:
            reasons.append("falta registro en image-rights-manifest.json")
        for label, record in (("principal", main), ("derechos", right)):
            if record and not all(record.get(field) for field in ("source_page", "license_url", "credit_line")):
                reasons.append(f"registro {label} sin fuente, licencia o crédito")
        if right and right.get("approved") is not True:
            reasons.append("derechos no aprobados")
        if compact(name) not in compact(pdf_page_3_text):
            reasons.append("nombre ausente de la página Referentes")
        if reasons:
            invalid.append({"name": name, "file": relative, "reasons": reasons})
    blocked = rights.get("blocked_candidates", [])
    passed = (
        actual == EXPECTED_REFERENTS
        and ["assets/" + str(item.get("file", "")).removeprefix("assets/") for item in main_records]
        == [relative for _, relative in EXPECTED_REFERENTS]
        and len(rights_records) == 6
        and not blocked
        and len(hashes) == len(set(hashes)) == 6
        and not invalid
        and rights.get("status") in {"approved", "pass", "ready"}
    )
    return {
        "passed": passed,
        "actual": actual,
        "expected": EXPECTED_REFERENTS,
        "rights_status": rights.get("status"),
        "blocked_candidates": len(blocked) if isinstance(blocked, list) else None,
        "invalid": invalid,
    }


def portable_image_manifest(root: Path, data: dict[str, Any]) -> dict[str, Any]:
    assets = data.get("assets", [])
    invalid: list[dict[str, Any]] = []
    files: list[str] = []
    package_root = root.resolve()
    for record in assets if isinstance(assets, list) else []:
        if not isinstance(record, dict):
            invalid.append({"file": None, "reason": "registro no es objeto"})
            continue
        relative = str(record.get("file", ""))
        path_value = Path(relative)
        target = (root / path_value).resolve()
        files.append(relative)
        reasons: list[str] = []
        if not relative or path_value.is_absolute() or ".." in path_value.parts:
            reasons.append("ruta no portable")
        elif not target.is_relative_to(package_root) or not target.is_file():
            reasons.append("archivo ausente o fuera del paquete")
        elif record.get("sha256") != sha256(target):
            reasons.append("sha256 no coincide")
        if not all(record.get(field) for field in ("role", "origin", "rights_status")):
            reasons.append("falta rol, origen o estado de derechos")
        if reasons:
            invalid.append({"file": relative, "reasons": reasons})
    serialized = json.dumps(data, ensure_ascii=False)
    nonportable = [marker for marker in ("/Users/", "/private/tmp/", "file://") if marker in serialized]
    rendered = data.get("rendered_asset_count")
    supporting = data.get("supporting_source_count")
    passed = (
        isinstance(assets, list)
        and rendered == 19
        and supporting == 2
        and len(assets) == 21
        and len(files) == len(set(files))
        and not invalid
        and not nonportable
        and data.get("document") == "N08"
        and data.get("edition") == "v9-final"
    )
    return {
        "passed": passed,
        "entries": len(assets) if isinstance(assets, list) else None,
        "rendered": rendered,
        "supporting": supporting,
        "invalid": invalid,
        "nonportable_markers": nonportable,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--expected-pages", type=int, default=0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    source = root / "source/N08_observar_el_trabajo_invisible-content-final.md"
    canonical = HERE / "N08-content-final/source/N08_observar_el_trabajo_invisible-content-final.md"
    content_integrity_path = HERE / "N08-content-final/provenance/integrity-report.json"
    pdf = root / "output/N08-METSI-lectura-previa-v9-final.pdf"
    raw_pdf = root / "output/N08-METSI-lectura-previa-v9.pdf"
    html_path = root / "index.html"
    css_path = root / "magazine.css"
    manifest_path = root / "manifest.json"
    source_manifest_path = root / "source-manifest.json"
    integrity_path = root / "integrity-report.json"
    qa_path = root / "qa-report.json"
    generation_path = root / "image-generation-manifest.json"
    rights_path = root / "image-rights-manifest.json"
    image_manifest_path = root / "image-manifest.json"
    spread_plan_path = root / "page-spread-plan.json"
    n07_pdf = HERE / "N07-v9-final/output/N07-METSI-lectura-previa-v9-final.pdf"

    essential = [
        source, canonical, content_integrity_path, pdf, raw_pdf, html_path, css_path,
        manifest_path, source_manifest_path, integrity_path, qa_path, generation_path,
        rights_path, image_manifest_path, spread_plan_path, n07_pdf,
    ]
    missing = [str(path) for path in essential if not path.is_file()]
    if missing:
        error_report = {"document": "N08", "version": "v9-final", "status": "ERROR", "missing": missing}
        print(json.dumps(package_relative_report_paths(error_report, root), ensure_ascii=False, indent=2))
        return 2

    source_text = source.read_text(encoding="utf-8")
    html = html_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")
    manifest = read_json(manifest_path)
    source_manifest = read_json(source_manifest_path)
    integrity = read_json(integrity_path)
    qa = read_json(qa_path)
    generation = read_json(generation_path)
    rights = read_json(rights_path)
    image_manifest = read_json(image_manifest_path)
    spread_plan = read_json(spread_plan_path)
    content_integrity = read_json(content_integrity_path)
    reader = PdfReader(str(pdf))
    page_texts = [page.extract_text() or "" for page in reader.pages]
    compact_pdf = compact("\n".join(page_texts))
    headings = re.findall(r"^## (.+)$", source_text, flags=re.M)
    _, references = source_text.split("## Referencias base", 1)
    source_urls = {value.rstrip(".,") for value in re.findall(r"https://\S+", references)}

    inventory = HtmlInventory()
    inventory.feed(html)
    local_errors = local_reference_issues(root, inventory, css)
    entries = source_manifest.get("eligible_blocks", [])
    source_ids = [str(entry.get("source_id", "")) for entry in entries]
    html_ids = re.findall(r'data-source-id="([^"]+)"', html)
    missing_fragments = [
        entry.get("source_id")
        for entry in entries
        if not block_is_rendered(str(entry.get("text", "")), compact_pdf)
    ]
    alignment = heading_body_alignment(entries, page_texts)

    html_sections: list[int] = []
    html_routes: list[str] = []
    for number in range(1, 15):
        match = re.search(rf'<section\b[^>]*data-section="{number:02d}"[^>]*>(.*?)</section>', html, re.S)
        html_sections.append(match.start() if match else -1)
        route = re.search(r"<em>(PROBLEMA|DISTINCIONES|DECISIONES|PRUEBA|TRANSFERENCIA|PREPARACIÓN)</em>", match.group(1) if match else "")
        html_routes.append(route.group(1) if route else "")

    route_pattern = re.compile(
        r"(?m)^(\d{2})\s+METSI\s*·\s*N08\s+"
        r"(PROBLEMA|DISTINCIONES|DECISIONES|PRUEBA|TRANSFERENCIA|PREPARACIÓN)\s*$"
    )
    pdf_headers: list[tuple[int, int, str]] = []
    for page_number, text in enumerate(page_texts, 1):
        for match in route_pattern.finditer(text):
            pdf_headers.append((int(match.group(1)), page_number, match.group(2)))
    pdf_headers.sort(key=lambda item: item[0])
    pdf_routes = [route for _, _, route in pdf_headers]

    contents = compact(page_texts[1]) if len(page_texts) > 1 else ""
    contents_positions = [contents.find(compact(heading)) for heading in EXPECTED_SECTIONS]
    counts = source_counts(source_text)

    link_pages = links_by_page(reader)
    external_pages = {
        number: sorted({uri for uri in links if "linkedin.com/in/carralbal" not in uri})
        for number, links in enumerate(link_pages, 1)
        if any("linkedin.com/in/carralbal" not in uri for uri in links)
    }
    external_links = {
        uri for links in link_pages for uri in links if "linkedin.com/in/carralbal" not in uri
    }
    linkedin_per_page = [sum("linkedin.com/in/carralbal" in uri for uri in links) for links in link_pages]

    figures = structure_figures(reader)
    alts_by_page: dict[int | None, list[str | None]] = {}
    for figure in figures:
        alts_by_page.setdefault(figure["page"], []).append(figure["alt"])
    # Las frases de pausa reaparecen como tesis o síntesis, y "Referencias base"
    # también figura en Contenido. La primera aparición de cada frase corresponde
    # a la pausa editorial; la última aparición de Referencias base, al aparato.
    pause_matches = [find_pages(page_texts, quote) for quote in EXPECTED_PAUSE_QUOTES]
    pause_pages = [matches[0] if matches else None for matches in pause_matches]
    reference_matches = find_pages(page_texts, "Referencias base")
    reference_page = reference_matches[-1] if reference_matches else None
    diagram_page = find_unique_page(page_texts, "La cadena conserva la diferencia entre lo observado y lo inferido")

    with pdfplumber.open(pdf) as document:
        extents = page_extents(document)
        cover_bleed = full_bleed_image(document.pages[0])
        page4_dark = dark_full_page_background(document.pages[3]) if len(document.pages) >= 4 else {"passed": False}
        pause_bleed = {
            page: full_bleed_image(document.pages[page - 1])
            for page in pause_pages if isinstance(page, int)
        }
        closing_bleed = full_bleed_image(document.pages[-1])
        references_layout = references_two_columns(document.pages[reference_page - 1]) if reference_page else {"passed": False}
        reference_images = len(document.pages[reference_page - 1].images) if reference_page else None
        image_pages = {number: len(page.images) for number, page in enumerate(document.pages, 1)}
        rendered_fonts = sorted({str(char.get("fontname", "")) for page in document.pages for char in page.chars})

    planned_pages = len(spread_plan.get("pages", [])) if isinstance(spread_plan.get("pages"), list) else 0
    expected_pages = args.expected_pages or planned_pages
    media_sizes: list[dict[str, float]] = []
    a4_ok = expected_pages > 0 and len(reader.pages) == expected_pages
    for number, page in enumerate(reader.pages, 1):
        width, height = float(page.mediabox.width), float(page.mediabox.height)
        media_sizes.append({"page": number, "width": round(width, 3), "height": round(height, 3)})
        if abs(width - EXPECTED_A4[0]) > 0.75 or abs(height - EXPECTED_A4[1]) > 0.75:
            a4_ok = False

    exceptional_pages = {1, 2, 3, 4, len(reader.pages), *[page for page in pause_pages if page]}
    ordinary_pages = [number for number in range(5, len(reader.pages)) if number not in exceptional_pages]
    ordinary_fill = {number: extents.get(number, {}).get("fill", 0.0) for number in ordinary_pages}
    underfilled = {number: value for number, value in ordinary_fill.items() if value < 0.55}

    cover_source = root / "assets/cover-source-premium-bw-v1.png"
    cover_alias = root / "assets/cover.png"
    tone = cover_tone(cover_source)
    cover_contract = manifest.get("cover", {})
    cover_rule_match = re.search(r"\.cover-n08>img\{([^}]*)\}", css)
    cover_rule = cover_rule_match.group(1) if cover_rule_match else ""
    shade_match = re.search(r"\.cover-n08 \.cover-shade\{([^}]*)\}", css)
    shade_rule = shade_match.group(1) if shade_match else ""
    shade_alphas = [float(value) for value in re.findall(r"rgba\([^,]+,[^,]+,[^,]+,\s*([0-9.]+)\)", shade_rule)]
    cover_ok = (
        # ImageGen produjo un original concebido en blanco y negro con un tinte
        # neutro residual de hasta 5 niveles RGB. Sigue siendo fotografía nativa
        # monocromática y conserva una amplitud tonal superior al gate editorial.
        float(tone.get("channel_spread_p95", 999.0)) <= 6.0
        and float(tone.get("luminance_p05", 999.0)) <= 70.0
        and float(tone.get("luminance_p95", 0.0)) >= 200.0
        and float(tone.get("luminance_stddev", 0.0)) >= 35.0
        and cover_source.is_file()
        and cover_alias.is_file()
        and sha256(cover_source) == sha256(cover_alias) == cover_contract.get("sha256")
        and cover_contract.get("photographic_origin") == "native_black_and_white"
        and cover_contract.get("render_treatment") == "no_grayscale_conversion"
        and "filter:none" in cover_rule
        and "grayscale(" not in cover_rule
        and bool(shade_alphas)
        and max(shade_alphas) <= 0.55
        and sum(value == 0.0 for value in shade_alphas) >= 2
    )

    diagram_source = root / "infographic-work-layer/n08-work-layers.svg"
    diagram_copy = root / "diagrams/N08-mapa-decision.svg"
    diagram_manifest = manifest.get("diagram", {})
    section6 = re.search(r'<section\b[^>]*data-section="06"[^>]*>(.*?)</section>', html, re.S)
    diagram_svg = diagram_source.read_text(encoding="utf-8")
    diagram_font_sizes = [float(value) for value in re.findall(r"font-size\s*:\s*([0-9.]+)px", diagram_svg)]
    diagram_min_px = min(diagram_font_sizes) if diagram_font_sizes else 0.0
    diagram_min_pt = diagram_min_px * 160.0 / 1800.0 * 72.0 / 25.4
    diagram_ok = (
        sha256(diagram_source) == sha256(diagram_copy) == EXPECTED_DIAGRAM_SHA
        and diagram_manifest.get("source_sha256") == EXPECTED_DIAGRAM_SHA
        and diagram_manifest.get("topology") == "reference-grade-observation-work-layer"
        and bool(section6 and 'src="diagrams/N08-mapa-decision.svg"' in section6.group(1))
        and diagram_min_pt >= 7.0
        and re.search(r"\.document-n08 \.infographic-boundaries\{[^}]*width:160mm", css) is not None
    )

    generated = generated_asset_audit(root, generation, html)
    referents = referent_rights_audit(root, inventory, manifest, rights, page_texts[2])
    image_inventory = portable_image_manifest(root, image_manifest)
    required_missing = [relative for relative in REQUIRED_FILES if not (root / relative).is_file()]
    aliases_ok = (
        (root / "metsi.css").read_bytes() == css_path.read_bytes()
        and read_json(root / "document.json") == manifest
    )

    reference_order_tokens = [
        "Suchman, L. A.", "Beyer, H.", "Hollnagel, E.", "Dekker, S.", "Weick, K. E.",
        "Hutchins, E.", "Strauss, A.", "Star, S. L.", "Trist, E. L.", "Autio, C.",
        "Gmyrek, P.", "Milanez, A.",
    ]
    reference_text = compact(page_texts[reference_page - 1]) if reference_page else ""
    reference_positions = [reference_text.find(compact(token)) for token in reference_order_tokens]
    root_object = reader.trailer["/Root"]
    mark_info = root_object.get("/MarkInfo") or {}
    metadata = reader.metadata or {}
    metadata_values = {key: str(metadata.get(key, "")) for key in EXPECTED_METADATA}
    metadata_ok = all(metadata_values[key] == value for key, value in EXPECTED_METADATA.items())
    pause_alts_ok = all(
        page and expected in alts_by_page.get(page, [])
        for page, expected in zip(pause_pages, EXPECTED_PAUSE_ALTS)
    )
    structure_alts = [figure.get("alt") for figure in figures]
    semantic_alts_ok = all(
        expected in structure_alts
        for expected in (EXPECTED_COVER_ALT, EXPECTED_CONTENTS_ALT, EXPECTED_INFOGRAPHIC_ALT, *EXPECTED_PAUSE_ALTS, EXPECTED_CLOSING_ALT)
    )

    pause_html_count = html.count('class="full-bleed full-bleed-quote"')
    first_pause_html = html.find(EXPECTED_PAUSE_QUOTES[0])
    second_pause_html = html.find(EXPECTED_PAUSE_QUOTES[1])
    section1_end = html.find('data-section="01"')
    section2_start = html.find('data-section="02"')
    section6_end = html.find('data-section="06"')
    section7_start = html.find('data-section="07"')
    pauses_in_expected_html_order = (
        -1 not in (section1_end, first_pause_html, section2_start, section6_end, second_pause_html, section7_start)
        and section1_end < first_pause_html < section2_start
        and section6_end < second_pause_html < section7_start
    )

    checks = [
        result("required_release_files_present", not required_missing, {"missing": required_missing}),
        result("package_aliases_match_authoring_files", aliases_ok, "metsi.css == magazine.css; document.json == manifest.json"),
        result("html_and_css_local_references_resolve", not local_errors, local_errors),
        result(
            "canonical_source_sha_and_byte_identity",
            source.read_bytes() == canonical.read_bytes() and sha256(source) == EXPECTED_SOURCE_SHA,
            {"actual": sha256(source), "expected": EXPECTED_SOURCE_SHA, "byte_identical": source.read_bytes() == canonical.read_bytes()},
        ),
        result(
            "content_audit_remains_closed",
            content_integrity.get("overall") == "pass"
            and content_integrity.get("sha256") == EXPECTED_SOURCE_SHA
            and content_integrity.get("references", {}).get("entries") == 12
            and all(content_integrity.get("references", {}).get("anchors", {}).values()),
            {"overall": content_integrity.get("overall"), "word_counts": content_integrity.get("word_counts"), "anchors": content_integrity.get("references", {}).get("anchors")},
        ),
        result(
            "source_manifest_has_256_blocks_exactly_once",
            len(source_ids) == EXPECTED_BLOCKS
            and len(set(source_ids)) == EXPECTED_BLOCKS
            and Counter(source_ids) == Counter(html_ids)
            and integrity.get("status") == "PASS"
            and integrity.get("source_block_count") == EXPECTED_BLOCKS,
            {"manifest": len(source_ids), "html": len(html_ids), "integrity": integrity},
        ),
        result("all_source_blocks_have_rendered_fragments", not missing_fragments, {"checked": len(entries), "missing": missing_fragments}),
        result(
            "source_id_reading_order_is_preserved_in_html",
            all((position := html.find(f'data-source-id="{source_id}"')) >= 0 for source_id in source_ids)
            and [html.find(f'data-source-id="{source_id}"') for source_id in source_ids]
            == sorted(html.find(f'data-source-id="{source_id}"') for source_id in source_ids),
            {"ids_checked": len(source_ids)},
        ),
        result("canonical_14_section_structure", headings == EXPECTED_SECTIONS + ["Referencias base"], headings),
        result("content_counts_close", counts == EXPECTED_COUNTS, {"actual": counts, "expected": EXPECTED_COUNTS}),
        result("all_12_references_are_anchored", all(content_integrity.get("references", {}).get("anchors", {}).values()), content_integrity.get("references", {}).get("anchors")),
        result("pdf_is_distinct_finalized_artifact", sha256(pdf) != sha256(raw_pdf), {"raw": sha256(raw_pdf), "final": sha256(pdf)}),
        result(
            "pdf_page_count_is_locked_and_all_pages_are_a4",
            a4_ok and qa.get("pages") == expected_pages and qa.get("a4_pages") == expected_pages,
            {"expected_pages": expected_pages, "planned_pages": planned_pages, "actual_pages": len(reader.pages), "sizes": media_sizes},
        ),
        result("pdf_metadata_is_complete", metadata_ok, {"metadata": metadata_values, "keywords": str(metadata.get("/Keywords", ""))}),
        result(
            "contents_and_section_order_are_complete",
            all(position >= 0 for position in contents_positions)
            and contents_positions == sorted(contents_positions)
            and page_texts[1].count("SIN NUM.") >= 2
            and [number for number, _, _ in pdf_headers] == list(range(1, 15))
            and [page for _, page, _ in pdf_headers] == sorted(page for _, page, _ in pdf_headers)
            and all(position >= 0 for position in html_sections)
            and html_sections == sorted(html_sections),
            {"contents_positions": dict(zip(EXPECTED_SECTIONS, contents_positions)), "pdf_headers": pdf_headers},
        ),
        result("route_is_exact_in_html_and_pdf", html_routes == EXPECTED_ROUTES and pdf_routes == EXPECTED_ROUTES, {"html": html_routes, "pdf": pdf_routes, "expected": EXPECTED_ROUTES}),
        result("all_source_headings_keep_following_body_on_same_page", alignment["passed"], alignment),
        result("ordinary_pages_are_at_least_55_percent_full", bool(ordinary_fill) and not underfilled, {"ordinary_pages": ordinary_fill, "underfilled": underfilled}),
        result("page_4_is_intentional_dark_full_page_opening", page4_dark.get("passed") and "Pregunta profesional" in page_texts[3], {"background": page4_dark, "fill": extents.get(4)}),
        result("rendered_pdf_contains_zero_arial", not any("arial" in font.casefold() for font in rendered_fonts) and not qa.get("forbidden_fonts"), {"fonts": rendered_fonts, "qa_forbidden": qa.get("forbidden_fonts")}),
        result("page_1_cover_reaches_all_edges", cover_bleed["passed"], cover_bleed),
        result("cover_is_native_bw_without_css_conversion_or_heavy_global_scrim", cover_ok, {"tone": tone, "contract": cover_contract, "cover_rule": cover_rule, "shade_rule": shade_rule}),
        result(
            "cover_eyebrow_is_two_accessible_text_runs",
            '<span>LECTURA PREVIA</span><span>EDICIÓN 2026</span>' in html
            and "LECTURA PREVIA" in page_texts[0]
            and "EDICIÓN 2026" in page_texts[0]
            and not re.search(r"L\s+E\s+C\s+T\s+U\s+R\s+A", page_texts[0]),
            page_texts[0][:350],
        ),
        result(
            "generated_editorial_and_pause_photos_are_unique_native_bw_and_provenanced",
            generated["passed"]
            and manifest.get("internal_images") == EXPECTED_INTERNAL_IMAGES
            and manifest.get("sparse_fill_images") == [],
            {"audit": generated, "internal_images": manifest.get("internal_images")},
        ),
        result(
            "contents_photo_is_unique_and_not_reused",
            html.count('src="assets/editorial-04.png"') == 1
            and re.search(r'<section class="front-page contents-page">.*?src="assets/editorial-04.png"', html, re.S) is not None,
            {"html_references": html.count('src="assets/editorial-04.png"')},
        ),
        result(
            "exactly_two_full_bleed_pauses_with_first_on_page_5",
            pause_html_count == 2
            and pauses_in_expected_html_order
            and pause_pages[0] == 5
            and all(isinstance(page, int) for page in pause_pages)
            and all(value["passed"] for value in pause_bleed.values())
            and pause_alts_ok,
            {"html_count": pause_html_count, "pages": pause_pages, "bleed": pause_bleed, "html_order": pauses_in_expected_html_order},
        ),
        result(
            "reference_grade_infographic_is_anchored_to_section_06_at_160mm",
            diagram_ok and diagram_page is not None and EXPECTED_INFOGRAPHIC_ALT in alts_by_page.get(diagram_page, []),
            {"page": diagram_page, "min_svg_px": diagram_min_px, "min_final_pt": round(diagram_min_pt, 2), "manifest": diagram_manifest},
        ),
        result(
            "references_are_image_free_two_column_penultimate_page",
            reference_page == len(reader.pages) - 1
            and reference_images == 0
            and references_layout["passed"]
            and all(position >= 0 for position in reference_positions)
            and reference_positions == sorted(reference_positions),
            {"page": reference_page, "images": reference_images, "columns": references_layout, "order_positions": reference_positions},
        ),
        result(
            "six_exact_urls_are_printed_and_annotated_only_on_references_page",
            source_urls == EXPECTED_URLS
            and external_links == EXPECTED_URLS
            and external_pages == ({reference_page: sorted(EXPECTED_URLS)} if reference_page else {}),
            {"source": sorted(source_urls), "annotations": sorted(external_links), "pages": external_pages},
        ),
        result(
            "last_page_is_full_bleed_structured_matches_closing",
            closing_bleed["passed"]
            and EXPECTED_CLOSING_CAPTION in page_texts[-1]
            and re.search(rf"\b{len(reader.pages):02d}\b", page_texts[-1]) is not None
            and "linkedin.com/in/carralbal" in page_texts[-1]
            and EXPECTED_CLOSING_ALT in alts_by_page.get(len(reader.pages), [])
            and EXPECTED_CLOSING_ALT in page_image_alts(reader, len(reader.pages))
            and manifest.get("closing", {}).get("policy") == "canonical_structured_closing_without_quote"
            and qa.get("closing_quote_absent") is True,
            {"bleed": closing_bleed, "text": page_texts[-1], "xobject_alts": page_image_alts(reader, len(reader.pages))},
        ),
        result("six_unique_referents_have_approved_rights_and_provenance", referents["passed"], referents),
        result("portable_hash_locked_image_manifest_is_complete", image_inventory["passed"], image_inventory),
        result(
            "tagging_language_and_alt_structure_are_complete",
            bool(root_object.get("/StructTreeRoot"))
            and bool(mark_info.get("/Marked"))
            and root_object.get("/Lang") == "es-AR"
            and '<html lang="es-AR">' in html
            and semantic_alts_ok,
            {"lang": root_object.get("/Lang"), "marked": bool(mark_info.get("/Marked")), "figures": figures},
        ),
        result(
            "all_pages_have_folio_and_linkedin_footer",
            linkedin_per_page == [1] * len(reader.pages)
            and all(re.search(rf"\b{number:02d}\b", text) for number, text in enumerate(page_texts, 1)),
            {"linkedin_annotations_per_page": linkedin_per_page},
        ),
        result("n07_final_pdf_regression_sha_is_unchanged", sha256(n07_pdf) == EXPECTED_N07_PDF_SHA, {"actual": sha256(n07_pdf), "expected": EXPECTED_N07_PDF_SHA}),
    ]

    passed = all(item["status"] == "PASS" for item in checks)
    report = {
        "document": "N08",
        "version": "v9-final",
        "validator": Path(__file__).name,
        "mode": "read-only",
        "status": "PASS" if passed else "FAIL",
        "failed_checks": [item["check"] for item in checks if item["status"] == "FAIL"],
        "source_sha256": sha256(source),
        "pdf_sha256": sha256(pdf),
        "pdf_bytes": pdf.stat().st_size,
        "pages": len(reader.pages),
        "expected_pages": expected_pages,
        "minimum_ordinary_page_fill": min(ordinary_fill.values()) if ordinary_fill else None,
        "checks": checks,
    }
    print(json.dumps(package_relative_report_paths(report, root), ensure_ascii=False, indent=2, default=str))
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(json.dumps({"document": "N08", "version": "v9-final", "status": "ERROR", "error": f"{type(error).__name__}: {error}"}, ensure_ascii=False, indent=2))
        sys.exit(2)
