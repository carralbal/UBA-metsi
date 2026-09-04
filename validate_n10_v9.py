#!/usr/bin/env python3
"""Validador determinista y de solo lectura para METSI N10 v9 final.

Lee la fuente canonica y su copia empaquetada, HTML, CSS, manifiestos, activos,
PDF crudo y PDF final. Imprime un unico informe JSON. No modifica artefactos.
Devuelve 0 para PASS, 1 para una guarda incumplida y 2 para error de ejecucion.
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import sys
from collections import Counter
from itertools import combinations
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
    links_by_page,
    local_reference_issues,
    page_extents,
    page_image_alts,
    result,
    sha256,
    structure_figures,
)


HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE / "N10-v9-final"
EXPECTED_SOURCE_SHA = "f272051348f0f2bf459e384cd66d433ae2881ac1d4d1d38200664a4c0e3f29c3"
EXPECTED_COVER_SHA = "347f75bc02c056dfed010f231564c53188c078ce9e032549ae57488c87385744"
EXPECTED_DIAGRAM_SHA = "8eae98d3624777f9b0d631852fb75584504ccf22fd550c1ef41a995f75f1c707"
EXPECTED_BLOCKS = 261
EXPECTED_PAGES = 31
EXPECTED_A4 = (594.96, 841.92)
EXPECTED_SECTIONS = [
    "Pregunta profesional",
    "El puente que resolvia el problema equivocado",
    "Hotel Horizonte: una decision que parece estar tomada",
    "Tesis",
    "De N09 a N10: del recorrido vivido al encuadre provisional",
    "Movimiento 1 · Separar pedido, sintoma, mecanismo y problema",
    "Movimiento 2 · Formular outcomes, protecciones y evidencia de revision",
    "Movimiento 3 · Integrar evidencia y abrir una puerta de decision",
    "Errores frecuentes",
    "Consecuencias profesionales",
    "Cierre del Bloque 1: un encuadre listo para ser refutado",
    "Sintesis",
    "Cinco pildoras para recordar",
    "Glosario esencial",
    "Preguntas de preparacion",
]
# compact() elimina tildes solo cuando no forman parte de la busqueda; por eso
# se mantienen a continuacion las formas canonicas para las comparaciones.
EXPECTED_SECTIONS_CANONICAL = [
    "Pregunta profesional",
    "El puente que resolvía el problema equivocado",
    "Hotel Horizonte: una decisión que parece estar tomada",
    "Tesis",
    "De N09 a N10: del recorrido vivido al encuadre provisional",
    "Movimiento 1 · Separar pedido, síntoma, mecanismo y problema",
    "Movimiento 2 · Formular outcomes, protecciones y evidencia de revisión",
    "Movimiento 3 · Integrar evidencia y abrir una puerta de decisión",
    "Errores frecuentes",
    "Consecuencias profesionales",
    "Cierre del Bloque 1: un encuadre listo para ser refutado",
    "Síntesis",
    "Cinco píldoras para recordar",
    "Glosario esencial",
    "Preguntas de preparación",
]
EXPECTED_ROUTES = (
    ["PROBLEMA"] * 4
    + ["DISTINCIONES"] * 2
    + ["DECISIONES", "PRUEBA"]
    + ["TRANSFERENCIA"] * 3
    + ["PREPARACIÓN"] * 4
)
EXPECTED_REFERENTS = [
    ("Donald A. Schön", "assets/referent-donald-schon.jpg"),
    ("Ray Pawson", "assets/referent-ray-pawson.jpg"),
    ("Reva Schwartz", "assets/referent-reva-schwartz.jpg"),
    ("Elham Tabassi", "assets/referent-elham-tabassi.jpg"),
    ("Kamie Roberts", "assets/referent-kamie-roberts.jpg"),
    ("Martin Stanley", "assets/referent-martin-stanley.jpg"),
]
EXPECTED_IMAGEGEN = [
    "cover.png",
    "editorial-01.png",
    "editorial-02.png",
    "editorial-03.png",
    "editorial-04.png",
    "editorial-05.png",
    "pause-01.png",
    "pause-02.png",
]
EXPECTED_IMAGEGEN_SIZES = {
    "cover.png": [1055, 1491],
    "editorial-01.png": [1448, 1086],
    "editorial-02.png": [1448, 1086],
    "editorial-03.png": [1448, 1086],
    "editorial-04.png": [1448, 1086],
    "editorial-05.png": [1448, 1086],
    "pause-01.png": [1055, 1491],
    "pause-02.png": [1055, 1491],
}
EXPECTED_URLS = {
    "https://doi.org/10.1016/j.destud.2011.07.006",
    "https://doi.org/10.6028/NIST.AI.600-1",
    "https://dora.dev/research/2025/dora-report/",
    "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
    "https://www.computer.org/education/bodies-of-knowledge/software-engineering/v4",
    "https://www.iso.org/standard/72089.html",
    "https://www.iso.org/standard/81702.html",
    "https://www.weforum.org/publications/the-future-of-jobs-report-2025/",
}
EXPECTED_PAUSE_QUOTES = {
    5: "El pedido nombra una respuesta; el encuadre debe explicar qué situación justifica intervenir.",
    20: "Un problema es revisable cuando declara qué evidencia podría volverlo falso.",
}
EXPECTED_PAUSE_ALTS = {
    5: "Un puente nuevo domina el paisaje mientras, debajo, personas esperan un colectivo y un ciclista atraviesa un cruce junto a las vías.",
    20: "Una médica y una enfermera comparan dos fichas en blanco mientras observan el flujo de una sala de espera hospitalaria.",
}
EXPECTED_COVER_ALT = (
    "Una profesional argentina observa desde el acceso peatonal de un puente cómo confluyen "
    "un colectivo, automóviles, ciclistas, peatones y una vía ferroviaria junto al río."
)
EXPECTED_INFOGRAPHIC_ALT = (
    "Instrumento de encuadre en tres bandas que conecta nueve campos de análisis con una "
    "puerta final de cuatro salidas La situación, los afectados, el outcome, los mecanismos "
    "rivales, la evidencia, la frontera, las restricciones, la protección y la reparación "
    "se revisan antes de aprobar, devolver, dividir o reformular."
)
EXPECTED_CLOSING_ALT = (
    "Diez fósforos dispuestos en secuencia vertical, desde intactos hasta consumidos "
    "y convertidos en ceniza."
)
EXPECTED_CLOSING_CAPTION = (
    "La secuencia vuelve visible que toda intervención consume recursos, deja huellas "
    "y necesita un criterio de cierre."
)
EXPECTED_CONTENTS_NOTE = (
    "Nota. SIN NUM. identifica los aparatos de orientación y referencia que no integran "
    "la secuencia argumental."
)
EXPECTED_CONTENTS_IMAGE_ALT = (
    "Manos de profesionales argentinos ordenan fichas en blanco junto a una maqueta "
    "de puente sobre una mesa clara antes de elegir una solución."
)
EXPECTED_CONTENTS_IMAGE_CAPTION = (
    "Una lectura previa para llegar al encuentro con preguntas, no con respuestas memorizadas."
)
EXPECTED_CONTENTS_SECTION_11 = "Cierre del Bloque 1: un encuadre listo para ser refutado"
EXPECTED_HOTEL_CAPTION = (
    "El software puede funcionar y la promesa fallar: el objeto de análisis es el sistema "
    "sociotécnico que produce el servicio."
)
EXPECTED_COUNTS = {"pills": 5, "glossary": 8, "questions": 6, "references": 13}
EXPECTED_HOTEL_VOICES = ["Elena Acosta", "Lucía Ferreyra", "Ricardo Sosa", "Federico Müller"]
EXPECTED_METADATA = {
    "/Title": "N10 · Construir el problema: de síntomas a outcomes verificables",
    "/Author": "Diego Carralbal",
    "/Subject": "Metodología de Sistemas de Información · FCE · UBA",
}
EXCEPTION_PAGES = {1, 2, 3, 4, 5, 20, 31}
REQUIRED_FILES = [
    "HANDOFF.md",
    "CHANGELOG.md",
    "PUBLICATION-READINESS.md",
    "visual-audit.md",
    "index.html",
    "magazine.css",
    "metsi.css",
    "manifest.json",
    "document.json",
    "source-manifest.json",
    "integrity-report.json",
    "qa-report.json",
    "assets/image-manifest.json",
    "assets/cover-image-audit.md",
    "image-manifest.json",
    "image-rights-manifest.json",
    "page-spread-plan.json",
    "provenance/regression-lock.json",
    "provenance/cover-image-premium-bw-v1.md",
    "provenance/editorial-image-provenance.md",
    "provenance/referent-portrait-sources.md",
    "source/N10_construir_el_problema_y_outcomes-content-final.md",
    "diagrams/N10-HH10-encuadre-puerta-decision.svg",
    "diagrams/N10-HH10-encuadre-puerta-decision@2x.png",
    "diagrams/content-manifest.json",
    "diagrams/alt-text.md",
    "diagrams/qa-report.md",
    "diagrams/review.html",
    "infographic-work-layer/N10-HH10-encuadre-puerta-decision.svg",
    "infographic-work-layer/N10-HH10-encuadre-puerta-decision@2x.png",
    "infographic-work-layer/content-manifest.json",
    "infographic-work-layer/alt-text.md",
    "infographic-work-layer/qa-report.md",
    "infographic-work-layer/review.html",
    "output/N10-METSI-lectura-previa-v9.pdf",
    "output/N10-METSI-lectura-previa-v9-final.pdf",
    "qa/N10-contact-sheet.jpg",
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


def heading_body_alignment(entries: list[dict[str, Any]], page_texts: list[str]) -> dict[str, Any]:
    compact_pages = [compact(text) for text in page_texts]
    records: list[dict[str, Any]] = []
    for index, entry in enumerate(entries[:-1]):
        if entry.get("kind") not in {"heading-2", "heading-3"}:
            continue
        following = entries[index + 1]
        heading = compact(str(entry.get("text", "")))
        fragment = first_fragment(str(following.get("text", "")))
        heading_pages = {number for number, text in enumerate(compact_pages, 1) if heading in text}
        body_pages = {number for number, text in enumerate(compact_pages, 1) if fragment in text}
        shared = sorted(heading_pages & body_pages)
        records.append({
            "source_id": entry.get("source_id"),
            "heading": entry.get("text"),
            "following_source_id": following.get("source_id"),
            "same_pages": shared,
        })
    failed = [record for record in records if not record["same_pages"]]
    return {"passed": bool(records) and not failed, "checked": len(records), "failed": failed}


def dhash(path: Path) -> int:
    with Image.open(path) as image:
        sample = image.convert("L").resize((9, 8))
        getter = getattr(sample, "get_flattened_data", None)
        pixels = list(getter() if getter else sample.getdata())
    value = 0
    for row in range(8):
        for column in range(8):
            if pixels[row * 9 + column] > pixels[row * 9 + column + 1]:
                value |= 1 << (row * 8 + column)
    return value


def imagegen_audit(root: Path, data: dict[str, Any], html: str) -> dict[str, Any]:
    records = {str(item.get("file")): item for item in data.get("assets", []) if isinstance(item, dict)}
    details: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    perceptual: dict[str, int] = {}
    for name in EXPECTED_IMAGEGEN:
        record = records.get(name)
        path = root / "assets" / name
        reasons: list[str] = []
        if not record:
            reasons.append("falta registro")
        if not path.is_file():
            reasons.append("falta activo")
        if path.is_file():
            with Image.open(path) as image:
                size = list(image.size)
            tone = cover_tone(path)
            tone_metrics = {key: value for key, value in tone.items() if key != "passed"}
            digest = sha256(path)
            perceptual[name] = dhash(path)
            detail = {"file": name, "size": size, "sha256": digest, "tone_metrics": tone_metrics}
            details.append(detail)
            if size != EXPECTED_IMAGEGEN_SIZES[name]:
                reasons.append(f"dimensiones inesperadas: {size}")
            if record and record.get("sha256") != digest:
                reasons.append("sha256 no coincide")
            if record and record.get("bytes") != path.stat().st_size:
                reasons.append("bytes no coinciden")
            channel_limit = 6.0 if name == "cover.png" else 3.0
            if float(tone.get("channel_spread_p95", 999.0)) > channel_limit:
                reasons.append("dispersion cromatica incompatible con monocromo de origen")
            tonal_span = float(tone.get("luminance_p95", 0.0)) - float(tone.get("luminance_p05", 255.0))
            if tonal_span < 140.0 or float(tone.get("luminance_stddev", 0.0)) < 35.0:
                reasons.append("gama tonal insuficiente")
        if record:
            for field in ("role", "origin", "alt", "prompt"):
                if not record.get(field):
                    reasons.append(f"falta {field}")
            if record.get("postprocessing") != "none":
                reasons.append("posprocesamiento no nulo")
        if html.count(f'src="assets/{name}"') != 1:
            reasons.append(f"referencias HTML: {html.count(f'src=\"assets/{name}\"')}")
        if reasons:
            invalid.append({"file": name, "reasons": reasons})
    distances = [
        ((perceptual[a] ^ perceptual[b]).bit_count(), a, b)
        for a, b in combinations(sorted(perceptual), 2)
    ]
    minimum = min(distances) if distances else None
    hashes = [item["sha256"] for item in details]
    passed = (
        set(records) == set(EXPECTED_IMAGEGEN)
        and len(details) == len(EXPECTED_IMAGEGEN)
        and len(set(hashes)) == len(EXPECTED_IMAGEGEN)
        and minimum is not None
        and minimum[0] >= 16
        and not invalid
        and "OpenAI ImageGen" in str(data.get("generator", ""))
        and data.get("qa", {}).get("status") == "PASS"
        and data.get("qa", {}).get("expected_asset_count") == len(EXPECTED_IMAGEGEN)
        and data.get("qa", {}).get("actual_asset_count") == len(EXPECTED_IMAGEGEN)
        and data.get("qa", {}).get("native_black_and_white_generation") is True
        and data.get("qa", {}).get("visual_duplicates_detected") is False
    )
    return {
        "passed": passed,
        "assets": details,
        "invalid": invalid,
        "minimum_pairwise_dhash_distance": minimum,
    }


def referent_audit(
    root: Path,
    inventory: HtmlInventory,
    manifest: dict[str, Any],
    rights: dict[str, Any],
    pdf_page_3_text: str,
) -> dict[str, Any]:
    actual = [(item.get("name", "").strip(), item.get("src", "")) for item in inventory.contributors]
    main_records = [item for item in manifest.get("portrait_references", []) if isinstance(item, dict)]
    rights_records = [item for item in rights.get("assets", []) if isinstance(item, dict)]
    rights_by_file = {str(item.get("file")): item for item in rights_records}
    main_by_file = {
        "assets/" + str(item.get("file", "")).removeprefix("assets/"): item
        for item in main_records
    }
    invalid: list[dict[str, Any]] = []
    hashes: list[str] = []
    for name, relative in EXPECTED_REFERENTS:
        path = root / relative
        main = main_by_file.get(relative)
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
                reasons.append(f"se esperaba 720 por 720 gris, se obtuvo {size} {mode}")
            if main and main.get("sha256") != digest:
                reasons.append("sha256 principal no coincide")
            if right and right.get("sha256") != digest:
                reasons.append("sha256 de derechos no coincide")
        if not main:
            reasons.append("falta manifiesto principal")
        if not right:
            reasons.append("falta manifiesto de derechos")
        if main and not all(main.get(field) for field in ("source_page", "license_url", "creator", "credit_line")):
            reasons.append("manifiesto principal incompleto")
        if right:
            if not all((right.get("source_page"), right.get("license_url"), right.get("credit_line"))):
                reasons.append("registro de derechos incompleto")
            if right.get("approved") is not True:
                reasons.append("derechos no aprobados")
        if compact(name) not in compact(pdf_page_3_text):
            reasons.append("nombre ausente de Referentes")
        if reasons:
            invalid.append({"name": name, "file": relative, "reasons": reasons})
    passed = (
        actual == EXPECTED_REFERENTS
        and len(main_records) == len(rights_records) == 6
        and len(hashes) == len(set(hashes)) == 6
        and not invalid
        and rights.get("status") == "approved"
        and rights.get("approved_asset_count") == 6
        and rights.get("blocked_asset_count") == 0
    )
    return {"passed": passed, "actual": actual, "rights_status": rights.get("status"), "invalid": invalid}


def reference_layout(page: pdfplumber.page.Page) -> dict[str, Any]:
    tokens = {"Dorst", "Jackson", "Schön", "Toulmin", "Pawson", "Kellogg", "World", "Autio", "Unión", "DORA", "IEEE", "ISO/IEC/IEEE"}
    positions: list[dict[str, Any]] = []
    for word in page.extract_words(use_text_flow=False):
        token = re.sub(r"[,.;:]$", "", str(word.get("text", "")))
        if token in tokens:
            positions.append({"token": token, "x0": round(float(word.get("x0", 0.0)), 2), "top": round(float(word.get("top", 0.0)), 2)})
    left = [item for item in positions if item["x0"] < page.width * 0.47]
    right = [item for item in positions if item["x0"] > page.width * 0.48]
    return {"passed": len(left) >= 7 and len(right) >= 6, "left": left, "right": right}


def contents_bottom_layout(page: pdfplumber.page.Page) -> dict[str, Any]:
    groups: dict[float, list[dict[str, Any]]] = {}
    for char in page.chars:
        if page.height * 0.80 < float(char.get("top", 0.0)) < page.height * 0.90:
            groups.setdefault(round(float(char.get("size", 0.0)), 2), []).append(char)

    def locate(expected: str) -> tuple[float | None, list[dict[str, Any]]]:
        for size, chars in groups.items():
            if compact(expected) in compact("".join(str(char.get("text", "")) for char in chars)):
                return size, chars
        return None, []

    note_size, note_chars = locate(EXPECTED_CONTENTS_NOTE)
    caption_size, caption_chars = locate(EXPECTED_CONTENTS_IMAGE_CAPTION)

    def bbox(chars: list[dict[str, Any]]) -> dict[str, float] | None:
        if not chars:
            return None
        return {
            "x0": min(float(char["x0"]) for char in chars),
            "x1": max(float(char["x1"]) for char in chars),
            "top": min(float(char["top"]) for char in chars),
            "bottom": max(float(char["bottom"]) for char in chars),
        }

    note_box, caption_box = bbox(note_chars), bbox(caption_chars)
    overlap_x = overlap_y = 0.0
    if note_box and caption_box:
        overlap_x = max(0.0, min(note_box["x1"], caption_box["x1"]) - max(note_box["x0"], caption_box["x0"]))
        overlap_y = max(0.0, min(note_box["bottom"], caption_box["bottom"]) - max(note_box["top"], caption_box["top"]))
    return {
        "passed": bool(note_box and caption_box) and not (overlap_x > 0.25 and overlap_y > 0.25),
        "note_font_size": note_size,
        "caption_font_size": caption_size,
        "note_bbox": note_box,
        "caption_bbox": caption_box,
        "overlap_width_pt": round(overlap_x, 3),
        "overlap_height_pt": round(overlap_y, 3),
    }


def portable_image_manifest(root: Path, data: dict[str, Any]) -> dict[str, Any]:
    assets = data.get("assets", [])
    invalid: list[dict[str, Any]] = []
    files: list[str] = []
    package_root = root.resolve()
    for record in assets if isinstance(assets, list) else []:
        if not isinstance(record, dict):
            invalid.append({"file": None, "reasons": ["registro no es objeto"]})
            continue
        relative = str(record.get("file", ""))
        files.append(relative)
        target = (root / relative).resolve()
        reasons: list[str] = []
        if not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
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
    passed = (
        isinstance(assets, list)
        and data.get("document") == "N10"
        and data.get("edition") == "v9-final"
        and data.get("rendered_asset_count") == 20
        and data.get("supporting_source_count") == 2
        and len(assets) == 22
        and len(files) == len(set(files))
        and not invalid
        and not nonportable
    )
    return {"passed": passed, "entries": len(assets), "invalid": invalid, "nonportable_markers": nonportable}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--expected-pages", type=int, default=EXPECTED_PAGES)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    source = root / "source/N10_construir_el_problema_y_outcomes-content-final.md"
    canonical = HERE / "N10-content-final/source/N10_construir_el_problema_y_outcomes-content-final.md"
    content_integrity_path = HERE / "N10-content-final/provenance/integrity-report.json"
    pdf = root / "output/N10-METSI-lectura-previa-v9-final.pdf"
    raw_pdf = root / "output/N10-METSI-lectura-previa-v9.pdf"
    html_path = root / "index.html"
    css_path = root / "magazine.css"
    manifest_path = root / "manifest.json"
    source_manifest_path = root / "source-manifest.json"
    integrity_path = root / "integrity-report.json"
    qa_path = root / "qa-report.json"
    generation_path = root / "assets/image-manifest.json"
    cover_image_audit_path = root / "assets/cover-image-audit.md"
    image_manifest_path = root / "image-manifest.json"
    rights_path = root / "image-rights-manifest.json"
    spread_plan_path = root / "page-spread-plan.json"

    essential = [
        source, canonical, content_integrity_path, pdf, raw_pdf, html_path, css_path,
        manifest_path, source_manifest_path, integrity_path, qa_path, generation_path,
        cover_image_audit_path,
        rights_path, image_manifest_path, spread_plan_path,
    ]
    missing_essential = [str(path) for path in essential if not path.is_file()]
    if missing_essential:
        print(json.dumps({"document": "N10", "version": "v9-final", "status": "ERROR", "missing": missing_essential}, ensure_ascii=False, indent=2))
        return 2

    source_text = source.read_text(encoding="utf-8")
    html = html_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")
    manifest = read_json(manifest_path)
    source_manifest = read_json(source_manifest_path)
    integrity = read_json(integrity_path)
    qa = read_json(qa_path)
    generation = read_json(generation_path)
    cover_image_audit = cover_image_audit_path.read_text(encoding="utf-8")
    image_manifest = read_json(image_manifest_path)
    rights = read_json(rights_path)
    spread_plan = read_json(spread_plan_path)
    content_integrity = read_json(content_integrity_path)
    generation_records = {
        str(item.get("file")): item
        for item in generation.get("assets", [])
        if isinstance(item, dict)
    }
    reader = PdfReader(str(pdf))
    page_texts = [page.extract_text() or "" for page in reader.pages]
    compact_pdf = compact("\n".join(page_texts))

    inventory = HtmlInventory()
    inventory.feed(html)
    local_errors = local_reference_issues(root, inventory, css)
    entries = source_manifest.get("eligible_blocks", [])
    source_ids = [str(entry.get("source_id", "")) for entry in entries]
    html_ids = re.findall(r'data-source-id="([^"]+)"', html)
    missing_fragments = [
        {"source_id": entry.get("source_id"), "text": str(entry.get("text", ""))[:120]}
        for entry in entries
        if not block_is_rendered(str(entry.get("text", "")), compact_pdf)
    ]
    alignment = heading_body_alignment(entries, page_texts)

    heading2 = [str(entry.get("text", "")) for entry in entries if entry.get("kind") == "heading-2"]
    html_section_matches = re.findall(
        r'<section\b[^>]*data-section="(\d+)"[^>]*>.*?'
        r'<span>\1</span><b>METSI · N10 <em>(PROBLEMA|DISTINCIONES|DECISIONES|PRUEBA|TRANSFERENCIA|PREPARACIÓN)</em></b>.*?'
        r'<h2[^>]*>(.*?)</h2>',
        html,
        re.S,
    )
    html_sections = [(int(number), route, compact(re.sub(r"<[^>]+>", "", title))) for number, route, title in html_section_matches]
    html_routes = [route for _, route, _ in sorted(html_sections)]

    route_pattern = re.compile(
        r"(?m)^(\d{2})\s+METSI\s*·\s*N10\s+"
        r"(PROBLEMA|DISTINCIONES|DECISIONES|PRUEBA|TRANSFERENCIA|PREPARACIÓN)"
    )
    pdf_headers: list[tuple[int, int, str]] = []
    for page_number, text in enumerate(page_texts, 1):
        for match in route_pattern.finditer(text):
            pdf_headers.append((int(match.group(1)), page_number, match.group(2)))
    pdf_headers.sort(key=lambda item: item[0])
    pdf_routes = [route for _, _, route in pdf_headers]

    contents = compact(page_texts[1]) if len(page_texts) > 1 else ""
    contents_flow = re.sub(r"\s+", " ", page_texts[1].replace("\u00a0", " ")).strip()
    contents_positions = [contents.find(compact(heading)) for heading in EXPECTED_SECTIONS_CANONICAL]
    counts = source_counts(source_text)

    link_pages = links_by_page(reader)
    external_pages = {
        number: sorted({uri for uri in links if "linkedin.com/in/carralbal" not in uri})
        for number, links in enumerate(link_pages, 1)
        if any("linkedin.com/in/carralbal" not in uri for uri in links)
    }
    external_links = {uri for links in link_pages for uri in links if "linkedin.com/in/carralbal" not in uri}
    linkedin_per_page = [sum("linkedin.com/in/carralbal" in uri for uri in links) for links in link_pages]
    source_urls = set(content_integrity.get("references", {}).get("urls", []))

    figures = structure_figures(reader)
    alts_by_page: dict[int | None, list[str | None]] = {}
    for figure in figures:
        alts_by_page.setdefault(figure["page"], []).append(figure["alt"])

    with pdfplumber.open(pdf) as document:
        extents = page_extents(document)
        cover_bleed = full_bleed_image(document.pages[0])
        contents_bottom = contents_bottom_layout(document.pages[1])
        page4_dark = dark_full_page_background(document.pages[3])
        pause_bleed = {number: full_bleed_image(document.pages[number - 1]) for number in EXPECTED_PAUSE_QUOTES}
        closing_bleed = full_bleed_image(document.pages[-1])
        references_layout = reference_layout(document.pages[-2])
        reference_images = len(document.pages[-2].images)
        rendered_fonts = sorted({str(char.get("fontname", "")) for page in document.pages for char in page.chars})

    media_sizes: list[dict[str, float]] = []
    a4_ok = len(reader.pages) == args.expected_pages == EXPECTED_PAGES
    for number, page in enumerate(reader.pages, 1):
        width, height = float(page.mediabox.width), float(page.mediabox.height)
        media_sizes.append({"page": number, "width": round(width, 3), "height": round(height, 3)})
        if abs(width - EXPECTED_A4[0]) > 0.75 or abs(height - EXPECTED_A4[1]) > 0.75:
            a4_ok = False

    ordinary_pages = [number for number in range(1, len(reader.pages) + 1) if number not in EXCEPTION_PAGES]
    ordinary_fill = {number: extents.get(number, {}).get("fill", 0.0) for number in ordinary_pages}
    underfilled = {number: value for number, value in ordinary_fill.items() if value < 0.55}

    cover_path = root / "assets/cover.png"
    cover_metrics = cover_tone(cover_path)
    cover_rule_match = re.search(r"\.cover-n09>img,\.cover-n10>img\{([^}]*)\}", css)
    cover_rule = cover_rule_match.group(1) if cover_rule_match else ""
    shade_match = re.search(r"\.cover-n09 \.cover-shade,\.cover-n10 \.cover-shade\{([^}]*)\}", css)
    shade_rule = shade_match.group(1) if shade_match else ""
    shade_alphas = [float(value) for value in re.findall(r"rgba\([^,]+,[^,]+,[^,]+,\s*([0-9.]+)\)", shade_rule)]
    cover_ok = (
        sha256(cover_path) == EXPECTED_COVER_SHA == manifest.get("cover", {}).get("sha256")
        and manifest.get("cover", {}).get("photographic_origin") == "native_black_and_white"
        and manifest.get("cover", {}).get("render_treatment") == "no_grayscale_conversion"
        and float(cover_metrics.get("channel_spread_p95", 999.0)) <= 6.0
        and float(cover_metrics.get("luminance_p05", 999.0)) <= 50.0
        and float(cover_metrics.get("luminance_p95", 0.0)) >= 200.0
        and float(cover_metrics.get("luminance_stddev", 0.0)) >= 35.0
        and "filter:none" in cover_rule
        and "grayscale(" not in cover_rule
        and bool(shade_alphas)
        and max(shade_alphas) <= 0.55
        and sum(value == 0.0 for value in shade_alphas) >= 2
    )

    imagegen = imagegen_audit(root, generation, html)
    image_inventory = portable_image_manifest(root, image_manifest)
    referents = referent_audit(root, inventory, manifest, rights, page_texts[2])

    diagram_copy = root / "diagrams/N10-HH10-encuadre-puerta-decision.svg"
    diagram_source = root / "infographic-work-layer/N10-HH10-encuadre-puerta-decision.svg"
    diagram_manifest = read_json(root / "diagrams/content-manifest.json")
    diagram_qa = (root / "diagrams/qa-report.md").read_text(encoding="utf-8")
    diagram_svg = diagram_copy.read_text(encoding="utf-8")
    section8_match = re.search(r'<section\b[^>]*data-section="08"[^>]*>(.*?)</section>', html, re.S)
    diagram_font_sizes = [float(value) for value in re.findall(r"font-size\s*:\s*([0-9.]+)px", diagram_svg)]
    diagram_forbidden = sorted(set(re.findall(r"(?i)\b(?:Arial|Helvetica|Times(?: New Roman)?)\b", diagram_svg)))
    diagram_ok = (
        sha256(diagram_copy) == sha256(diagram_source) == EXPECTED_DIAGRAM_SHA
        and diagram_copy.read_bytes() == diagram_source.read_bytes()
        and diagram_manifest.get("source_sha256") == EXPECTED_SOURCE_SHA
        and diagram_manifest.get("anchor") == "N10-s08-b001"
        and diagram_manifest.get("topology") == "hybrid-three-band-decision-gate-with-review-loop"
        and manifest.get("diagram", {}).get("file") == diagram_copy.name
        and html.count('src="diagrams/N10-HH10-encuadre-puerta-decision.svg"') == 1
        and bool(section8_match and 'src="diagrams/N10-HH10-encuadre-puerta-decision.svg"' in section8_match.group(1))
        and "RESULT: PASS (0 warning(s))" in diagram_qa
        and len(diagram_manifest.get("groups", [])) == 3
        and len(diagram_manifest.get("nodes", [])) == 14
        and len(diagram_manifest.get("edges", [])) == 16
        and diagram_font_sizes and min(diagram_font_sizes) >= 14.0
        and not diagram_forbidden
        and "foreignObject" not in diagram_svg
    )

    hotel_match = re.search(r'<aside class="hotel-voices-compact".*?</aside>', html, re.S)
    hotel_html = hotel_match.group(0) if hotel_match else ""
    hotel_names = re.findall(r"<h3>([^<]+)</h3>", hotel_html)
    hotel_images = re.findall(r'<img[^>]+src="([^"]+)"', hotel_html)
    hotel_hashes = [sha256(root / value) for value in hotel_images if (root / value).is_file()]

    reference_text = compact(page_texts[-2])
    reference_tokens = [
        "Dorst, K.", "Jackson, M.", "Schön, D. A.", "Toulmin, S. E.", "Pawson, R.",
        "W. K. Kellogg Foundation", "ISO/IEC/IEEE 29148:2018", "World Economic Forum",
        "Autio, C.", "Unión Europea", "DORA", "IEEE Computer Society", "ISO/IEC/IEEE (2023)",
    ]
    reference_positions = [reference_text.find(compact(value)) for value in reference_tokens]

    root_object = reader.trailer["/Root"]
    mark_info = root_object.get("/MarkInfo") or {}
    metadata = reader.metadata or {}
    metadata_values = {key: str(metadata.get(key, "")) for key in EXPECTED_METADATA}
    semantic_alts = [figure.get("alt") for figure in figures]
    expected_alts = [
        EXPECTED_COVER_ALT, *EXPECTED_PAUSE_ALTS.values(), EXPECTED_INFOGRAPHIC_ALT,
        EXPECTED_CLOSING_ALT,
    ]

    contents_match = re.search(r'<section class="front-page contents-page">(.*?)</section>', html, re.S)
    contents_html = contents_match.group(1) if contents_match else ""
    section_positions = {
        number: html.find(f'data-section="{number:02d}"')
        for number in range(1, 16)
    }
    editorial_positions = {
        name: html.find(f'src="assets/{name}"')
        for name in (
            "editorial-01.png", "editorial-02.png", "editorial-03.png",
            "editorial-04.png", "editorial-05.png",
        )
    }
    editorial_mapping_ok = (
        editorial_positions["editorial-05.png"] >= 0
        and contents_match is not None
        and 'src="assets/editorial-05.png"' in contents_html
        and section_positions[3] < editorial_positions["editorial-02.png"] < section_positions[4]
        and section_positions[5] < editorial_positions["editorial-01.png"] < section_positions[6]
        and section_positions[7] < editorial_positions["editorial-03.png"] < section_positions[8]
        and section_positions[8] < editorial_positions["editorial-04.png"] < section_positions[9]
    )

    planned_pages = spread_plan.get("pages", [])
    plan_ok = (
        spread_plan.get("document") == "N10"
        and spread_plan.get("version") == "v9-final"
        and spread_plan.get("page_count") == EXPECTED_PAGES
        and isinstance(planned_pages, list)
        and [item.get("page") for item in planned_pages] == list(range(1, EXPECTED_PAGES + 1))
    )
    required_missing = [relative for relative in REQUIRED_FILES if not (root / relative).is_file()]
    aliases_ok = (
        (root / "metsi.css").read_bytes() == css_path.read_bytes()
        and read_json(root / "document.json") == manifest
    )

    checks = [
        result("required_release_files_present", not required_missing, {"missing": required_missing}),
        result("page_and_spread_plan_is_complete", plan_ok, {"pages": len(planned_pages) if isinstance(planned_pages, list) else None}),
        result("package_aliases_match_authoring_files", aliases_ok, "metsi.css == magazine.css; document.json == manifest.json"),
        result("html_and_css_local_references_resolve", not local_errors, local_errors),
        result(
            "all_html_image_sources_are_concrete_files",
            not re.search(r'<img\b[^>]*\bsrc="(?:assets/|)"', html)
            and all((root / item.get("src", "")).is_file() for item in inventory.images),
            [item.get("src", "") for item in inventory.images if not (root / item.get("src", "")).is_file()],
        ),
        result(
            "canonical_source_sha_and_byte_identity",
            source.read_bytes() == canonical.read_bytes() and sha256(source) == EXPECTED_SOURCE_SHA,
            {"actual": sha256(source), "expected": EXPECTED_SOURCE_SHA, "byte_identical": source.read_bytes() == canonical.read_bytes()},
        ),
        result(
            "content_audit_remains_closed",
            content_integrity.get("overall") == "pass"
            and content_integrity.get("sha256") == EXPECTED_SOURCE_SHA
            and content_integrity.get("word_counts", {}).get("total") == 9110
            and content_integrity.get("word_counts", {}).get("substantive_from_thesis_through_synthesis") == 7180
            and content_integrity.get("references", {}).get("entries") == 13
            and all(content_integrity.get("references", {}).get("anchors", {}).values()),
            {"overall": content_integrity.get("overall"), "word_counts": content_integrity.get("word_counts"), "anchors": content_integrity.get("references", {}).get("anchors")},
        ),
        result(
            "source_manifest_has_261_blocks_exactly_once",
            len(source_ids) == EXPECTED_BLOCKS
            and len(set(source_ids)) == EXPECTED_BLOCKS
            and Counter(source_ids) == Counter(html_ids)
            and integrity.get("status") == "PASS"
            and integrity.get("source_block_count") == EXPECTED_BLOCKS
            and integrity.get("rendered_source_id_count") == EXPECTED_BLOCKS,
            {"manifest": len(source_ids), "html": len(html_ids), "integrity": integrity},
        ),
        result("all_source_blocks_have_rendered_fragments", not missing_fragments, {"checked": len(entries), "missing": missing_fragments}),
        result(
            "source_id_reading_order_is_preserved_in_html",
            [html.find(f'data-source-id="{source_id}"') for source_id in source_ids]
            == sorted(html.find(f'data-source-id="{source_id}"') for source_id in source_ids)
            and all(html.find(f'data-source-id="{source_id}"') >= 0 for source_id in source_ids),
            {"ids_checked": len(source_ids)},
        ),
        result("canonical_15_section_structure", heading2 == EXPECTED_SECTIONS_CANONICAL + ["Referencias base"], heading2),
        result("content_counts_close", counts == EXPECTED_COUNTS, {"actual": counts, "expected": EXPECTED_COUNTS}),
        result("all_13_references_are_anchored", all(content_integrity.get("references", {}).get("anchors", {}).values()), content_integrity.get("references", {}).get("anchors")),
        result(
            "pdf_is_distinct_finalized_artifact",
            sha256(pdf) != sha256(raw_pdf),
            {"raw": sha256(raw_pdf), "final": sha256(pdf)},
        ),
        result(
            "pdf_has_31_a4_pages",
            a4_ok and qa.get("pages") == EXPECTED_PAGES and qa.get("a4_pages") == EXPECTED_PAGES,
            {"actual_pages": len(reader.pages), "sizes": media_sizes},
        ),
        result("pdf_metadata_is_complete", all(metadata_values[key] == value for key, value in EXPECTED_METADATA.items()), metadata_values),
        result(
            "contents_and_section_order_are_complete",
            all(position >= 0 for position in contents_positions)
            and contents_positions == sorted(contents_positions)
            and page_texts[1].count("SIN NUM.") >= 2
            and [number for number, _, _ in pdf_headers] == list(range(1, 16))
            and [page for _, page, _ in pdf_headers] == sorted(page for _, page, _ in pdf_headers)
            and [number for number, _, _ in html_sections] == list(range(1, 16)),
            {"contents_positions": dict(zip(EXPECTED_SECTIONS_CANONICAL, contents_positions)), "pdf_headers": pdf_headers},
        ),
        result(
            "contents_note_is_complete_and_extractable",
            EXPECTED_CONTENTS_NOTE in contents_flow
            and EXPECTED_CONTENTS_SECTION_11 in contents_flow
            and contents_bottom["passed"],
            {
                "page": 2,
                "expected_note": EXPECTED_CONTENTS_NOTE,
                "expected_section_11": EXPECTED_CONTENTS_SECTION_11,
                "bottom_layout": contents_bottom,
            },
        ),
        result("route_is_exact_in_html_and_pdf", html_routes == EXPECTED_ROUTES and pdf_routes == EXPECTED_ROUTES, {"html": html_routes, "pdf": pdf_routes, "expected": EXPECTED_ROUTES}),
        result("all_source_headings_keep_following_body_on_same_page", alignment["passed"], alignment),
        result("ordinary_pages_are_at_least_55_percent_full", bool(ordinary_fill) and not underfilled, {"ordinary_pages": ordinary_fill, "minimum": min(ordinary_fill.values()), "underfilled": underfilled, "exceptions": sorted(EXCEPTION_PAGES)}),
        result("page_4_is_intentional_dark_full_page_opening", page4_dark.get("passed") and "Pregunta profesional" in page_texts[3], {"background": page4_dark, "fill": extents.get(4)}),
        result(
            "cover_reaches_all_edges_and_preserves_native_bw_tonal_range",
            cover_bleed.get("passed") and cover_ok,
            {
                "bleed": cover_bleed,
                "tone_metrics": {key: value for key, value in cover_metrics.items() if key != "passed"},
                "n10_tone_thresholds_passed": cover_ok,
                "cover_rule": cover_rule,
                "shade_rule": shade_rule,
            },
        ),
        result(
            "cover_and_pause_alts_match_image_manifest",
            manifest.get("cover", {}).get("alt") == generation_records.get("cover.png", {}).get("alt") == EXPECTED_COVER_ALT
            and all(generation_records.get(f"pause-0{index}.png", {}).get("alt") == EXPECTED_PAUSE_ALTS[page] for index, page in enumerate(sorted(EXPECTED_PAUSE_ALTS), 1))
            and EXPECTED_COVER_ALT in alts_by_page.get(1, [])
            and all(EXPECTED_PAUSE_ALTS[page] in alts_by_page.get(page, []) for page in EXPECTED_PAUSE_ALTS),
            {
                "manifest_cover": generation_records.get("cover.png", {}).get("alt"),
                "pdf_cover": alts_by_page.get(1, []),
                "manifest_pauses": [generation_records.get(f"pause-0{index}.png", {}).get("alt") for index in (1, 2)],
                "pdf_pauses": {page: alts_by_page.get(page, []) for page in EXPECTED_PAUSE_ALTS},
            },
        ),
        result(
            "cover_eyebrow_is_two_accessible_text_runs",
            '<span>LECTURA PREVIA</span><span>EDICIÓN 2026</span>' in html
            and "LECTURA PREVIA" in page_texts[0]
            and "EDICIÓN 2026" in page_texts[0]
            and not re.search(r"L\s+E\s+C\s+T\s+U\s+R\s+A", page_texts[0]),
            page_texts[0][:320],
        ),
        result(
            "exactly_two_full_bleed_internal_pauses",
            html.count('class="full-bleed full-bleed-quote"') == 2
            and all(compact(EXPECTED_PAUSE_QUOTES[page]) in compact(page_texts[page - 1]) for page in EXPECTED_PAUSE_QUOTES)
            and all(pause_bleed[page].get("passed") for page in EXPECTED_PAUSE_QUOTES)
            and all(EXPECTED_PAUSE_ALTS[page] in alts_by_page.get(page, []) for page in EXPECTED_PAUSE_ALTS),
            {"pages": sorted(EXPECTED_PAUSE_QUOTES), "bleed": pause_bleed},
        ),
        result("eight_imagegen_assets_are_hash_locked_unique_native_bw_and_tonally_open", imagegen["passed"], imagegen),
        result(
            "image_audit_prose_matches_eight_asset_series",
            "Ocho fotografías exactas: una tapa, cinco editoriales horizontales y dos pausas verticales." in cover_image_audit
            and "Distancia perceptual mínima entre pares: 23 bits sobre 64." in cover_image_audit
            and "El OCR de los ocho archivos" in cover_image_audit
            and "Las ocho escenas fueron generadas nativamente en blanco y negro." in cover_image_audit,
            {"file": "assets/cover-image-audit.md"},
        ),
        result("portable_hash_locked_image_manifest_is_complete", image_inventory["passed"], image_inventory),
        result(
            "contents_and_four_sections_use_five_unique_editorials_once",
            editorial_mapping_ok
            and all(html.count(f'src="assets/editorial-0{index}.png"') == 1 for index in range(1, 6)),
            {"contents_has_editorial_05": 'src="assets/editorial-05.png"' in contents_html, "positions": editorial_positions, "section_positions": section_positions},
        ),
        result(
            "contents_editorial_alt_matches_image_manifest_and_tagged_pdf",
            generation_records.get("editorial-05.png", {}).get("alt") == EXPECTED_CONTENTS_IMAGE_ALT
            and f'alt="{EXPECTED_CONTENTS_IMAGE_ALT}"' in contents_html
            and EXPECTED_CONTENTS_IMAGE_ALT in alts_by_page.get(2, []),
            {
                "manifest": generation_records.get("editorial-05.png", {}).get("alt"),
                "pdf": alts_by_page.get(2, []),
            },
        ),
        result(
            "hotel_horizonte_photo_caption_is_complete_and_extractable",
            EXPECTED_HOTEL_CAPTION in page_texts[7]
            and f'<figcaption aria-hidden="true">{EXPECTED_HOTEL_CAPTION}</figcaption>' in html,
            {"page": 8, "expected": EXPECTED_HOTEL_CAPTION},
        ),
        result(
            "four_distinct_hotel_horizonte_voices_are_present",
            hotel_names == EXPECTED_HOTEL_VOICES
            and len(hotel_images) == len(hotel_hashes) == len(set(hotel_hashes)) == 4
            and all(compact(name) in compact(page_texts[8]) for name in EXPECTED_HOTEL_VOICES),
            {"names": hotel_names, "images": hotel_images, "hashes": hotel_hashes},
        ),
        result("six_unique_referents_have_approved_rights_and_provenance", referents["passed"], referents),
        result(
            "reference_grade_infographic_is_exact_once_anchored_and_font_clean",
            diagram_ok and EXPECTED_INFOGRAPHIC_ALT in alts_by_page.get(21, []),
            {"sha256": sha256(diagram_copy), "groups": len(diagram_manifest.get("groups", [])), "nodes": len(diagram_manifest.get("nodes", [])), "edges": len(diagram_manifest.get("edges", [])), "minimum_font_px": min(diagram_font_sizes) if diagram_font_sizes else None, "forbidden_fonts": diagram_forbidden},
        ),
        result(
            "references_are_image_free_two_column_penultimate_page",
            reference_images == 0
            and references_layout["passed"]
            and all(position >= 0 for position in reference_positions)
            and reference_positions == sorted(reference_positions),
            {"page": 30, "images": reference_images, "layout": references_layout, "order_positions": reference_positions},
        ),
        result(
            "eight_exact_urls_are_printed_and_annotated_on_references_page",
            source_urls == EXPECTED_URLS
            and external_links == EXPECTED_URLS
            and external_pages == {30: sorted(EXPECTED_URLS)},
            {"source": sorted(source_urls), "annotations": sorted(external_links), "pages": external_pages},
        ),
        result(
            "rendered_typography_has_no_arial_helvetica_or_times",
            not any(any(name in font.casefold() for name in ("arial", "helvetica", "times")) for font in rendered_fonts)
            and not qa.get("forbidden_fonts"),
            {"fonts": rendered_fonts, "qa_forbidden": qa.get("forbidden_fonts")},
        ),
        result(
            "pdf_is_tagged_es_ar_with_semantic_image_alts",
            bool(root_object.get("/StructTreeRoot"))
            and bool(mark_info.get("/Marked"))
            and root_object.get("/Lang") == "es-AR"
            and '<html lang="es-AR">' in html
            and all(expected in semantic_alts for expected in expected_alts),
            {"lang": root_object.get("/Lang"), "marked": bool(mark_info.get("/Marked")), "figures": figures},
        ),
        result(
            "all_pages_have_folio_and_linkedin_footer",
            linkedin_per_page == [1] * EXPECTED_PAGES
            and all(re.search(rf"\b{number:02d}\b", text) for number, text in enumerate(page_texts, 1)),
            {"linkedin_annotations_per_page": linkedin_per_page},
        ),
        result(
            "last_page_is_full_bleed_structured_matches_closing",
            closing_bleed.get("passed")
            and EXPECTED_CLOSING_CAPTION in page_texts[-1]
            and re.search(r"\b31\b", page_texts[-1]) is not None
            and "linkedin.com/in/carralbal" in page_texts[-1]
            and EXPECTED_CLOSING_ALT in alts_by_page.get(31, [])
            and EXPECTED_CLOSING_ALT in page_image_alts(reader, 31)
            and manifest.get("closing", {}).get("policy") == "canonical_structured_closing_without_quote"
            and qa.get("closing_quote_absent") is True,
            {"bleed": closing_bleed, "text": page_texts[-1], "xobject_alts": page_image_alts(reader, 31)},
        ),
    ]

    passed = all(item["status"] == "PASS" for item in checks)
    report = {
        "document": "N10",
        "version": "v9-final",
        "validator": Path(__file__).name,
        "mode": "read-only",
        "status": "PASS" if passed else "FAIL",
        "passed_checks": sum(item["status"] == "PASS" for item in checks),
        "total_checks": len(checks),
        "failed_checks": [item["check"] for item in checks if item["status"] == "FAIL"],
        "source_sha256": sha256(source),
        "raw_pdf_sha256": sha256(raw_pdf),
        "pdf_sha256": sha256(pdf),
        "pdf_bytes": pdf.stat().st_size,
        "pages": len(reader.pages),
        "minimum_ordinary_page_fill": min(ordinary_fill.values()) if ordinary_fill else None,
        "cover_sha256": sha256(cover_path),
        "infographic_sha256": sha256(diagram_copy),
        "checks": checks,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(json.dumps({"document": "N10", "version": "v9-final", "status": "ERROR", "error": f"{type(error).__name__}: {error}"}, ensure_ascii=False, indent=2))
        sys.exit(2)
