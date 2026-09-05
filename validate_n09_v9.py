#!/usr/bin/env python3
"""Validador determinista y de sólo lectura para el cierre METSI N09 v9.

Lee la fuente canónica, el paquete editable, los manifiestos, los activos y los
PDF. Imprime un único informe JSON en stdout, no reescribe ningún artefacto y
usa códigos de salida 0 para PASS, 1 para una guarda incumplida y 2 para un
error de ejecución.
"""

from __future__ import annotations

import argparse
import json
import re
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
    result,
    sha256,
    structure_figures,
)


HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE / "N09-v9-final"
EXPECTED_SOURCE_SHA = "8e81a6462d515a955a1575dd36b91a12df500939f871df616934aa32bb018845"
EXPECTED_N08_PDF_SHA = "c931e032947c56fe4310fbc698c8f5a370f8f884c3180827955f9d0e42b5adbc"
EXPECTED_DIAGRAM_SHA = "719fc5ce84aadc321e240a6dfdf468634a5da7997e47fbe9600cd4311ff8884d"
EXPECTED_BLOCKS = 324
EXPECTED_PAGES = 28
EXPECTED_A4 = (594.96, 841.92)
EXPECTED_SECTIONS = [
    "Pregunta profesional",
    "La puerta automática que sólo era automática para algunos",
    "Tesis",
    "De N08 a N09: del trabajo realizado al recorrido vivido",
    "Movimiento 1 · Seguir el recorrido completo y reconocer barreras sistémicas",
    "Movimiento 2 · Diseñar con diversidad y comprender la adopción",
    "Movimiento 3 · Medir, recuperar y gobernar la experiencia",
    "Errores frecuentes",
    "Consecuencias profesionales",
    "Límites y tensiones",
    "Síntesis",
    "Cinco píldoras para recordar",
    "Glosario esencial",
    "Preguntas de preparación",
]
EXPECTED_ROUTES = (
    ["PROBLEMA"] * 4
    + ["DISTINCIONES", "DECISIONES", "PRUEBA", "TRANSFERENCIA"]
    + ["PREPARACIÓN"] * 6
)
EXPECTED_REFERENTS = [
    ("Sasha Costanza-Chock", "assets/referent-sasha-costanza-chock.jpg"),
    ("Lucy A. Suchman", "assets/referent-lucy-suchman.jpg"),
    ("Reva Schwartz", "assets/referent-reva-schwartz.jpg"),
    ("Elham Tabassi", "assets/referent-elham-tabassi.jpg"),
    ("Kamie Roberts", "assets/referent-kamie-roberts.jpg"),
    ("Martin Stanley", "assets/referent-martin-stanley.jpg"),
]
EXPECTED_GENERATED = {
    "cover.png": ("cover", [1055, 1491]),
    "editorial-01.png": ("work-content-and-archive", [1448, 1086]),
    "editorial-02.png": ("journey-and-support-work", [1448, 1086]),
    "editorial-03.png": ("promise-versus-verified-attribute", [1448, 1086]),
    "editorial-04.png": ("recovery-and-alternative-channel", [1448, 1086]),
    "pause-01.png": ("full-page-pause-friction-threshold", [1055, 1491]),
    "pause-02.png": ("full-page-pause-repair-continuity", [1055, 1491]),
}
EXPECTED_URLS = {
    "https://www.iso.org/standard/63500.html",
    "https://www.iso.org/standard/77520.html",
    "https://www.w3.org/TR/WCAG22/",
    "https://www.iso.org/standard/91029.html",
    "https://www.w3.org/WAI/fundamentals/accessibility-principles/",
    "https://designjustice.mitpress.mit.edu/",
    "https://doi.org/10.1016/C2013-0-13303-2",
    "https://doi.org/10.1017/CBO9780511808418",
    "https://eur-lex.europa.eu/eli/dir/2019/882/oj",
    "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
    "https://doi.org/10.6028/NIST.AI.600-1",
    "https://doi.org/10.54394/HETP0387",
}
EXPECTED_PAUSE_QUOTES = [
    "Una experiencia sin barreras aparentes puede seguir produciendo exclusión en el resultado.",
    "El promedio mejora con facilidad cuando deja fuera a quienes más fricción encuentran.",
]
EXPECTED_PAUSE_ALTS = [
    "Una niña espera frente a una puerta automática de vidrio que aún no responde mientras una adulta observa a distancia.",
    "Dos trabajadoras de hotel sostienen la continuidad del servicio con un registro en papel, una llave física y un teléfono junto a una pantalla inactiva.",
]
EXPECTED_COVER_ALT = (
    "Una mujer argentina cruza de manera autónoma un umbral de vidrio contemporáneo apoyada en su bastón, "
    "con amplio espacio arquitectónico a la izquierda."
)
EXPECTED_CONTENTS_ALT = (
    "Dos profesionales argentinos organizan planos, carpetas, registros y una tableta sobre una mesa de archivo "
    "para contrastar evidencia de trabajo."
)
EXPECTED_INFOGRAPHIC_ALT = (
    "Mapa de recorrido accesible que relaciona transiciones vividas, trabajo interno, evidencia, riesgo, recuperación "
    "y distribución de carga El recorrido conecta lo que la persona puede hacer con el trabajo que sostiene la promesa, "
    "la evidencia crítica y la alternativa de reparación."
)
EXPECTED_CLOSING_ALT = (
    "Diez fósforos dispuestos en secuencia vertical, desde intactos hasta consumidos y convertidos en ceniza."
)
EXPECTED_CLOSING_CAPTION = (
    "La secuencia vuelve visible que toda intervención consume recursos, deja huellas y necesita un criterio de cierre."
)
EXPECTED_COUNTS = {"pills": 5, "glossary": 9, "questions": 6, "references": 14}
EXPECTED_METADATA = {
    "/Title": "N09 · Experiencia, accesibilidad y adopción no son decoración",
    "/Author": "Diego Carralbal",
    "/Subject": "Metodología de Sistemas de Información · FCE · UBA",
}
EXPECTED_HOTEL_VOICES = [
    ("Elena Acosta", "assets/hotel-elena.jpg"),
    ("Lucía Ferreyra", "assets/hotel-lucia.jpg"),
    ("Ricardo Sosa", "assets/hotel-ricardo.jpg"),
    ("Federico Müller", "assets/hotel-federico.jpg"),
]
EXPECTED_RENDERED_VISUALS = {
    *(f"assets/{filename}" for filename in EXPECTED_GENERATED),
    *(relative for _, relative in EXPECTED_REFERENTS),
    *(relative for _, relative in EXPECTED_HOTEL_VOICES),
    "assets/matches-close.png",
    "diagrams/N09-mapa-decision.svg",
}
EXPECTED_SUPPORTING_VISUALS = {
    "infographic-work-layer/n09-accessible-service-blueprint.svg",
    "infographic-work-layer/n09-accessible-service-blueprint.png",
}
EXPECTED_VISUAL_CATEGORIES = {
    "imagegen": 7,
    "referent_portrait": 6,
    "hotel_horizonte_portrait": 4,
    "canonical_closing": 1,
    "rendered_infographic": 1,
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
    "assets/image-manifest.json",
    "image-manifest.json",
    "assets/cover-image-audit.md",
    "image-rights-manifest.json",
    "page-spread-plan.json",
    "provenance/regression-lock.json",
    "provenance/cover-image-premium-bw-v1.md",
    "provenance/editorial-image-provenance.md",
    "provenance/accessibility-image-map.md",
    "provenance/referent-portrait-sources.md",
    "source/N09_experiencia_accesibilidad_y_adopcion-content-final.md",
    "diagrams/N09-mapa-decision.svg",
    "diagrams/N09-mapa-decision.json",
    "infographic-work-layer/n09-accessible-service-blueprint.svg",
    "infographic-work-layer/n09-accessible-service-blueprint.png",
    "infographic-work-layer/content-manifest.json",
    "infographic-work-layer/alt-text.md",
    "infographic-work-layer/qa-report.md",
    "infographic-work-layer/review.html",
    "output/N09-METSI-lectura-previa-v9.pdf",
    "output/N09-METSI-lectura-previa-v9-final.pdf",
    "qa/N09-contact-sheet.jpg",
]


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Se esperaba un objeto JSON en {path}")
    return value


def package_relative_report_paths(value: Any, root: Path) -> Any:
    """Vuelve portables sólo las rutas del informe, sin alterar el gate."""
    if isinstance(value, dict):
        return {key: package_relative_report_paths(item, root) for key, item in value.items()}
    if isinstance(value, list):
        return [package_relative_report_paths(item, root) for item in value]
    if isinstance(value, tuple):
        return [package_relative_report_paths(item, root) for item in value]
    if isinstance(value, str):
        candidate = Path(value)
        if candidate.is_absolute():
            try:
                return candidate.relative_to(root).as_posix()
            except ValueError:
                pass
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


def find_pages(page_texts: list[str], value: str) -> list[int]:
    needle = compact(value)
    return [number for number, text in enumerate(page_texts, 1) if needle in compact(text)]


def find_unique_page(page_texts: list[str], value: str) -> int | None:
    pages = find_pages(page_texts, value)
    return pages[0] if len(pages) == 1 else None


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


def difference_hash(path: Path) -> int:
    with Image.open(path) as image:
        sample = image.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
        pixels = list(sample.get_flattened_data())
    value = 0
    bit = 0
    for row in range(8):
        offset = row * 9
        for column in range(8):
            if pixels[offset + column] > pixels[offset + column + 1]:
                value |= 1 << bit
            bit += 1
    return value


def effective_asset_alt(html: str, relative: str) -> str:
    figure_pattern = re.compile(
        rf"<figure\b([^>]*)>(?:(?!</figure>).)*?<img\b[^>]*src=\"{re.escape(relative)}\"[^>]*>(?:(?!</figure>).)*?</figure>",
        re.S,
    )
    figure = figure_pattern.search(html)
    if figure:
        aria = re.search(r'aria-label="([^"]*)"', figure.group(1))
        if aria and aria.group(1).strip():
            return aria.group(1).strip()
    image = re.search(rf'<img\b[^>]*src="{re.escape(relative)}"[^>]*>', html)
    if not image:
        return ""
    alt = re.search(r'alt="([^"]*)"', image.group(0))
    return alt.group(1).strip() if alt else ""


def generated_asset_audit(root: Path, data: dict[str, Any], html: str) -> dict[str, Any]:
    records = {
        str(record.get("file")): record
        for record in data.get("assets", [])
        if isinstance(record, dict)
    }
    details: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    hashes: list[str] = []
    dhashes: dict[str, int] = {}
    for filename, (role, expected_size) in EXPECTED_GENERATED.items():
        record = records.get(filename)
        path = root / "assets" / filename
        reasons: list[str] = []
        if not record:
            reasons.append("falta registro en assets/image-manifest.json")
        if not path.is_file():
            reasons.append("falta activo")
        if path.is_file():
            scan = image_monochrome(path)
            tone = cover_tone(path)
            digest = sha256(path)
            hashes.append(digest)
            dhashes[filename] = difference_hash(path)
            details.append({**scan, "tone": tone})
            if scan.get("size") != expected_size:
                reasons.append(f"dimensiones distintas de {expected_size}")
            if not scan.get("monochrome"):
                reasons.append("no es monocromo nativo")
            if float(tone.get("channel_spread_p95", 999.0)) > 6.0:
                reasons.append("separación de canales incompatible con blanco y negro nativo")
            if float(tone.get("luminance_p95", 0.0)) < 180.0 or float(tone.get("luminance_stddev", 0.0)) < 40.0:
                reasons.append("gama tonal insuficiente")
            if record and record.get("sha256") != digest:
                reasons.append("sha256 no coincide")
            if record and record.get("bytes") != path.stat().st_size:
                reasons.append("tamaño en bytes no coincide")
        if record:
            if record.get("role") != role:
                reasons.append(f"rol distinto de {role}")
            if [record.get("width"), record.get("height")] != expected_size:
                reasons.append("dimensiones del manifiesto no coinciden")
            if record.get("origin") != "generated_for_metsi_with_openai_imagegen":
                reasons.append("origen no declarado como ImageGen para METSI")
            if not all(record.get(field) for field in ("alt", "prompt")):
                reasons.append("falta texto alternativo o prompt")
        relative = f"assets/{filename}"
        effective_alt = effective_asset_alt(html, relative)
        if filename != "cover.png" and record and compact(str(record.get("alt", ""))) not in compact(effective_alt):
            reasons.append("el texto alternativo efectivo no describe el activo según su manifiesto")
        if html.count(relative) != 1:
            reasons.append(f"el HTML referencia {relative} {html.count(relative)} veces")
        if reasons:
            invalid.append({"file": filename, "effective_alt": effective_alt, "manifest_alt": record.get("alt") if record else None, "reasons": reasons})

    distances = {
        f"{left}|{right}": (dhashes[left] ^ dhashes[right]).bit_count()
        for index, left in enumerate(dhashes)
        for right in list(dhashes)[index + 1 :]
    }
    minimum_distance = min(distances.values()) if distances else None
    qa = data.get("qa", {})
    passed = (
        set(records) == set(EXPECTED_GENERATED)
        and len(hashes) == len(set(hashes)) == 7
        and minimum_distance is not None
        and minimum_distance >= 16
        and not invalid
        and data.get("document") == "N09"
        and data.get("edition") == "v9-final"
        and str(data.get("generator", "")).startswith("OpenAI ImageGen")
        and "originalmente en blanco y negro" in str(data.get("editorial_policy", "")).casefold()
        and qa.get("expected_asset_count") == qa.get("actual_asset_count") == 7
        and qa.get("visual_duplicates_detected") is False
        and qa.get("heavy_scrim_or_vignette_detected") is False
        and qa.get("status") == "PASS"
    )
    return {
        "passed": passed,
        "assets": details,
        "minimum_pairwise_dhash_distance": minimum_distance,
        "manifest_minimum": qa.get("minimum_pairwise_dhash_distance"),
        "invalid": invalid,
    }


def consolidated_image_manifest_audit(
    root: Path,
    html: str,
    consolidated: dict[str, Any],
    generation: dict[str, Any],
    rights: dict[str, Any],
    diagram_content: dict[str, Any],
    upstream_path: Path,
    upstream: dict[str, Any],
) -> dict[str, Any]:
    """Comprueba que el inventario portable representa cada visual y su linaje."""
    records = [item for item in consolidated.get("assets", []) if isinstance(item, dict)]
    files = [str(item.get("file", "")) for item in records]
    by_file = {str(item.get("file", "")): item for item in records}
    rendered = [item for item in records if item.get("rendered") is True]
    supporting = [item for item in records if item.get("rendered") is False]
    html_images = re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', html)
    generation_by_file = {
        f"assets/{item.get('file')}": item
        for item in generation.get("assets", [])
        if isinstance(item, dict)
    }
    rights_by_file = {
        str(item.get("file", "")): item
        for item in rights.get("assets", [])
        if isinstance(item, dict)
    }
    upstream_by_file = {
        str(item.get("file", "")): item
        for item in upstream.get("assets", [])
        if isinstance(item, dict)
    }
    diagram_assets = diagram_content.get("assets", {})
    infographic_expected = {
        "diagrams/N09-mapa-decision.svg": diagram_assets.get("integration_copy", {}).get("sha256"),
        "infographic-work-layer/n09-accessible-service-blueprint.svg": diagram_assets.get("editable_svg", {}).get("sha256"),
        "infographic-work-layer/n09-accessible-service-blueprint.png": diagram_assets.get("preview_2x", {}).get("sha256"),
    }
    upstream_digest = sha256(upstream_path)
    invalid: list[dict[str, Any]] = []
    actual_hashes: list[str] = []

    for relative, record in by_file.items():
        reasons: list[str] = []
        path = root / relative
        if not relative or relative.startswith("/") or ".." in Path(relative).parts:
            reasons.append("ruta no portable")
        if not path.is_file():
            reasons.append("archivo ausente")
        else:
            digest = sha256(path)
            actual_hashes.append(digest)
            if record.get("sha256") != digest:
                reasons.append("sha256 no coincide")
            if record.get("bytes") != path.stat().st_size:
                reasons.append("tamaño en bytes no coincide")
            if path.suffix.casefold() == ".svg":
                svg = path.read_text(encoding="utf-8")
                width_match = re.search(r'<svg\b[^>]*\bwidth="([0-9.]+)"', svg)
                height_match = re.search(r'<svg\b[^>]*\bheight="([0-9.]+)"', svg)
                size = [
                    int(float(width_match.group(1))) if width_match else None,
                    int(float(height_match.group(1))) if height_match else None,
                ]
            else:
                with Image.open(path) as image:
                    size = list(image.size)
            if [record.get("width"), record.get("height")] != size:
                reasons.append(f"dimensiones declaradas distintas de {size}")

        if not record.get("origin") or not record.get("rights_status"):
            reasons.append("falta origen o estado de derechos")
        if record.get("rendered") is True and html.count(f'src="{relative}"') != 1:
            reasons.append("el activo renderizado no aparece exactamente una vez en HTML")
        if record.get("rendered") is False and html.count(f'src="{relative}"') != 0:
            reasons.append("una fuente de apoyo aparece renderizada en HTML")

        provenance_file = record.get("provenance_file")
        if provenance_file and not (root / str(provenance_file)).is_file():
            reasons.append("archivo de procedencia ausente")

        category = record.get("category")
        if category == "imagegen":
            source = generation_by_file.get(relative)
            if not source:
                reasons.append("sin registro espejo en assets/image-manifest.json")
            else:
                if source.get("sha256") != record.get("sha256"):
                    reasons.append("huella distinta del manifiesto ImageGen")
                if [source.get("width"), source.get("height")] != [record.get("width"), record.get("height")]:
                    reasons.append("dimensiones distintas del manifiesto ImageGen")
                if source.get("origin") != record.get("origin"):
                    reasons.append("origen distinto del manifiesto ImageGen")
            if record.get("rights_status") != "generated_for_metsi":
                reasons.append("estado de derechos ImageGen inválido")
        elif category == "referent_portrait":
            source = rights_by_file.get(relative)
            if not source:
                reasons.append("sin registro espejo en image-rights-manifest.json")
            else:
                mirrors = {
                    "sha256": source.get("sha256"),
                    "width": source.get("width"),
                    "height": source.get("height"),
                    "name": source.get("name"),
                    "source_page": source.get("source_page"),
                    "credit_line": source.get("credit_line"),
                    "license": source.get("license_short"),
                    "license_url": source.get("license_url"),
                }
                for field, expected in mirrors.items():
                    if record.get(field) != expected:
                        reasons.append(f"{field} difiere del manifiesto de derechos")
                if source.get("approved") is not True or record.get("rights_status") != "approved":
                    reasons.append("aprobación de derechos inválida")
        elif category in {"hotel_horizonte_portrait", "canonical_closing"}:
            inheritance = record.get("inheritance", {})
            upstream_record = upstream_by_file.get(relative)
            expected_manifest = str(upstream_path.relative_to(root.parent))
            if not upstream_record:
                reasons.append("activo heredado ausente del manifiesto anterior")
            if inheritance.get("upstream_document") != "N08-v9-final":
                reasons.append("documento de herencia inválido")
            if inheritance.get("upstream_manifest") != f"../{expected_manifest}":
                reasons.append("ruta de manifiesto heredado inválida")
            if inheritance.get("upstream_manifest_sha256") != upstream_digest:
                reasons.append("huella del manifiesto heredado no coincide")
            if inheritance.get("upstream_asset_sha256") != record.get("sha256"):
                reasons.append("huella de activo heredado no coincide")
            if upstream_record and upstream_record.get("sha256") != record.get("sha256"):
                reasons.append("activo distinto de su antecedente canónico")
            if record.get("rights_status") != "canonical_course_asset":
                reasons.append("estado canónico inválido")
        elif category in {"rendered_infographic", "infographic_support"}:
            if infographic_expected.get(relative) != record.get("sha256"):
                reasons.append("huella distinta del manifiesto de infografía")
            if record.get("rights_status") != "original_course_asset":
                reasons.append("estado de obra original inválido")
        else:
            reasons.append("categoría desconocida")

        if reasons:
            invalid.append({"file": relative, "reasons": reasons})

    category_counts = Counter(str(item.get("category", "")) for item in rendered)
    expected_supporting = EXPECTED_SUPPORTING_VISUALS
    declared_categories = consolidated.get("category_counts", {})
    passed = (
        consolidated.get("document") == "N09"
        and consolidated.get("edition") == "v9-final"
        and consolidated.get("status") == "PASS"
        and consolidated.get("rendered_asset_count") == len(rendered) == 19
        and consolidated.get("supporting_asset_count") == len(supporting) == 2
        and set(item.get("file") for item in rendered) == EXPECTED_RENDERED_VISUALS
        and set(item.get("file") for item in supporting) == expected_supporting
        and Counter(html_images) == Counter(EXPECTED_RENDERED_VISUALS)
        and category_counts == Counter(EXPECTED_VISUAL_CATEGORIES)
        and declared_categories == EXPECTED_VISUAL_CATEGORIES
        and len(files) == len(set(files)) == 21
        and len(actual_hashes) == 21
        and len({item.get("sha256") for item in rendered}) == 19
        and not invalid
    )
    return {
        "passed": passed,
        "rendered_declared": consolidated.get("rendered_asset_count"),
        "rendered_actual": len(rendered),
        "supporting_declared": consolidated.get("supporting_asset_count"),
        "supporting_actual": len(supporting),
        "category_counts": dict(category_counts),
        "html_images": html_images,
        "upstream_manifest_sha256": upstream_digest,
        "invalid": invalid,
    }


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
                size = list(image.size)
            digest = sha256(path)
            hashes.append(digest)
            if size != [720, 720]:
                reasons.append(f"se esperaba 720 × 720, se obtuvo {size}")
            if not image_monochrome(path).get("monochrome"):
                reasons.append("el derivado no es monocromo")
            if main and main.get("sha256") != digest:
                reasons.append("sha256 del manifiesto principal no coincide")
            if right and right.get("sha256") != digest:
                reasons.append("sha256 del manifiesto de derechos no coincide")
        if not main:
            reasons.append("falta registro en manifest.json")
        if not right:
            reasons.append("falta registro en image-rights-manifest.json")
        if main and not all(main.get(field) for field in ("source_page", "license_url", "credit_line")):
            reasons.append("registro principal sin fuente, licencia o crédito")
        if right and not all(right.get(field) for field in ("source_page", "license_url", "credit_line", "reference_basis")):
            reasons.append("registro de derechos incompleto")
        if right and right.get("approved") is not True:
            reasons.append("derechos no aprobados")
        if compact(name) not in compact(pdf_page_3_text):
            reasons.append("nombre ausente de la página Referentes")
        if reasons:
            invalid.append({"name": name, "file": relative, "reasons": reasons})
    main_files = ["assets/" + str(item.get("file", "")).removeprefix("assets/") for item in main_records]
    passed = (
        actual == EXPECTED_REFERENTS
        and main_files == [relative for _, relative in EXPECTED_REFERENTS]
        and [str(item.get("file")) for item in rights_records] == [relative for _, relative in EXPECTED_REFERENTS]
        and rights.get("document") == "N09"
        and rights.get("edition") == "v9-final"
        and rights.get("status") == "approved"
        and rights.get("expected_referent_count") == rights.get("approved_asset_count") == 6
        and rights.get("blocked_asset_count") == 0
        and len(hashes) == len(set(hashes)) == 6
        and not invalid
    )
    return {"passed": passed, "actual": actual, "invalid": invalid, "rights_status": rights.get("status")}


def hotel_voice_audit(root: Path, html: str, pdf_text: str) -> dict[str, Any]:
    invalid: list[dict[str, Any]] = []
    hashes: list[str] = []
    for name, relative in EXPECTED_HOTEL_VOICES:
        path = root / relative
        reasons: list[str] = []
        if not path.is_file():
            reasons.append("falta retrato")
        else:
            hashes.append(sha256(path))
            if not image_monochrome(path).get("monochrome"):
                reasons.append("retrato no monocromo")
        if html.count(f'src="{relative}"') != 1:
            reasons.append("referencia HTML ausente o duplicada")
        if compact(name) not in compact(pdf_text):
            reasons.append("nombre ausente del PDF")
        if reasons:
            invalid.append({"name": name, "file": relative, "reasons": reasons})
    names = [name for name, _ in EXPECTED_HOTEL_VOICES]
    return {
        "passed": not invalid and len(set(names)) == len(set(hashes)) == 4 and len(re.findall(r'class="hotel-voice(?:\s+[^"]*)?"', html)) == 4,
        "names": names,
        "unique_hashes": len(set(hashes)),
        "invalid": invalid,
    }


def references_two_columns(page: pdfplumber.page.Page) -> dict[str, Any]:
    anchors: list[dict[str, float | str]] = []
    for word in page.extract_words(use_text_flow=False):
        text = str(word.get("text", ""))
        if text in {"ISO", "W3C", "Costanza-Chock,", "Lazar,", "Norman,", "Rogers,", "Suchman,", "Parlamento", "Autio,", "Gmyrek,"}:
            anchors.append({"text": text, "x0": round(float(word.get("x0", 0.0)), 2), "top": round(float(word.get("top", 0.0)), 2)})
    left = [item for item in anchors if float(item["x0"]) < page.width * 0.47]
    right = [item for item in anchors if float(item["x0"]) > page.width * 0.48]
    left_starts = {round(float(item["x0"]), 1) for item in left}
    right_starts = {round(float(item["x0"]), 1) for item in right}
    return {
        "passed": len(left) >= 7 and len(right) >= 7 and any(abs(value - 68.1) < 1 for value in left_starts) and any(abs(value - 306.5) < 1 for value in right_starts),
        "left_markers": len(left),
        "right_markers": len(right),
        "left_x": sorted(left_starts),
        "right_x": sorted(right_starts),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--expected-pages", type=int, default=EXPECTED_PAGES)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    source = root / "source/N09_experiencia_accesibilidad_y_adopcion-content-final.md"
    canonical = HERE / "N09-content-final/source/N09_experiencia_accesibilidad_y_adopcion-content-final.md"
    content_integrity_path = HERE / "N09-content-final/provenance/integrity-report.json"
    pdf = root / "output/N09-METSI-lectura-previa-v9-final.pdf"
    raw_pdf = root / "output/N09-METSI-lectura-previa-v9.pdf"
    html_path = root / "index.html"
    css_path = root / "magazine.css"
    manifest_path = root / "manifest.json"
    source_manifest_path = root / "source-manifest.json"
    integrity_path = root / "integrity-report.json"
    qa_path = root / "qa-report.json"
    generation_path = root / "assets/image-manifest.json"
    consolidated_images_path = root / "image-manifest.json"
    rights_path = root / "image-rights-manifest.json"
    spread_plan_path = root / "page-spread-plan.json"
    diagram_integration_path = root / "diagrams/N09-mapa-decision.json"
    diagram_content_path = root / "infographic-work-layer/content-manifest.json"
    n08_pdf = HERE / "N08-v9-final/output/N08-METSI-lectura-previa-v9-final.pdf"
    n08_image_manifest_path = HERE / "N08-v9-final/image-manifest.json"

    essential = [
        source, canonical, content_integrity_path, pdf, raw_pdf, html_path, css_path,
        manifest_path, source_manifest_path, integrity_path, qa_path, generation_path,
        consolidated_images_path, rights_path, spread_plan_path, diagram_integration_path,
        diagram_content_path, n08_pdf, n08_image_manifest_path,
    ]
    missing = [str(path) for path in essential if not path.is_file()]
    if missing:
        error_report = {"document": "N09", "version": "v9-final", "status": "ERROR", "missing": missing}
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
    consolidated_images = read_json(consolidated_images_path)
    rights = read_json(rights_path)
    spread_plan = read_json(spread_plan_path)
    diagram_integration = read_json(diagram_integration_path)
    diagram_content = read_json(diagram_content_path)
    n08_image_manifest = read_json(n08_image_manifest_path)
    content_integrity = read_json(content_integrity_path)
    reader = PdfReader(str(pdf))
    page_texts = [page.extract_text() or "" for page in reader.pages]
    compact_pdf = compact("\n".join(page_texts))
    headings = re.findall(r"^## (.+)$", source_text, flags=re.M)
    _, reference_source = source_text.split("## Referencias base", 1)
    source_urls = {value.rstrip(".,") for value in re.findall(r"https://\S+", reference_source)}
    counts = source_counts(source_text)

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
        r"(?m)^(\d{2})\s+METSI\s*·\s*N09\s+"
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
    structure_alts = [figure.get("alt") for figure in figures]
    alts_by_page: dict[int | None, list[str | None]] = {}
    for figure in figures:
        alts_by_page.setdefault(figure.get("page"), []).append(figure.get("alt"))
    pause_matches = [find_pages(page_texts, quote) for quote in EXPECTED_PAUSE_QUOTES]
    pause_pages = [matches[0] if matches else None for matches in pause_matches]
    reference_matches = find_pages(page_texts, "Referencias base")
    reference_page = reference_matches[-1] if reference_matches else None
    diagram_page = find_unique_page(page_texts, "N09 · INSTRUMENTO DE DECISIÓN")

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
        rendered_fonts = sorted({str(char.get("fontname", "")) for page in document.pages for char in page.chars})

    expected_pages = args.expected_pages
    planned_pages = len(spread_plan.get("pages", [])) if isinstance(spread_plan.get("pages"), list) else 0
    media_sizes: list[dict[str, float]] = []
    a4_ok = len(reader.pages) == expected_pages == EXPECTED_PAGES
    for number, page in enumerate(reader.pages, 1):
        width, height = float(page.mediabox.width), float(page.mediabox.height)
        media_sizes.append({"page": number, "width": round(width, 3), "height": round(height, 3)})
        if abs(width - EXPECTED_A4[0]) > 0.75 or abs(height - EXPECTED_A4[1]) > 0.75:
            a4_ok = False

    exceptional_pages = {1, 2, 3, 4, len(reader.pages), *[page for page in pause_pages if page]}
    ordinary_pages = [number for number in range(1, len(reader.pages) + 1) if number not in exceptional_pages]
    ordinary_fill = {number: extents.get(number, {}).get("fill", 0.0) for number in ordinary_pages}
    underfilled = {number: value for number, value in ordinary_fill.items() if value < 0.55}

    cover = root / "assets/cover.png"
    cover_contract = manifest.get("cover", {})
    cover_scan = image_monochrome(cover)
    cover_tones = cover_tone(cover)
    cover_rule_match = re.search(r"\.cover-n09>img,[^{]*\{([^}]*)\}", css)
    cover_rule = cover_rule_match.group(1) if cover_rule_match else ""
    shade_match = re.search(r"\.cover-n09 \.cover-shade,[^{]*\{([^}]*)\}", css)
    shade_rule = shade_match.group(1) if shade_match else ""
    shade_alphas = [float(value) for value in re.findall(r"rgba\([^,]+,[^,]+,[^,]+,\s*([0-9.]+)\)", shade_rule)]
    cover_ok = (
        cover_scan.get("monochrome") is True
        and float(cover_tones.get("channel_spread_p95", 999.0)) <= 6.0
        and float(cover_tones.get("luminance_p05", 999.0)) <= 70.0
        and float(cover_tones.get("luminance_p95", 0.0)) >= 195.0
        and float(cover_tones.get("luminance_stddev", 0.0)) >= 45.0
        and cover_contract.get("sha256") == sha256(cover)
        and cover_contract.get("photographic_origin") == "native_black_and_white"
        and cover_contract.get("render_treatment") == "no_grayscale_conversion"
        and "filter:none" in cover_rule
        and "grayscale(" not in cover_rule
        and bool(shade_alphas)
        and max(shade_alphas) <= 0.55
        and sum(value == 0.0 for value in shade_alphas) >= 2
    )

    diagram_source = root / "infographic-work-layer/n09-accessible-service-blueprint.svg"
    diagram_copy = root / "diagrams/N09-mapa-decision.svg"
    diagram_svg = diagram_source.read_text(encoding="utf-8")
    diagram_font_sizes = [float(value) for value in re.findall(r"font-size\s*:\s*([0-9.]+)px", diagram_svg)]
    diagram_min_px = min(diagram_font_sizes) if diagram_font_sizes else 0.0
    diagram_min_pt = diagram_min_px * 160.0 / 1800.0 * 72.0 / 25.4
    section7 = re.search(r'<section\b[^>]*data-section="07"[^>]*>(.*?)</section>', html, re.S)
    diagram_ok = (
        sha256(diagram_source) == sha256(diagram_copy) == EXPECTED_DIAGRAM_SHA
        and diagram_integration.get("source_sha256") == EXPECTED_DIAGRAM_SHA
        and diagram_integration.get("integration_sha256") == EXPECTED_DIAGRAM_SHA
        and diagram_integration.get("anchor_source_id") == "N09-s07-b035"
        and diagram_integration.get("topology") == "service-blueprint-evidence-atlas"
        and diagram_integration.get("canonical_field_count") == 8
        and diagram_content.get("canonical_field_count") == 8
        and diagram_content.get("anchor", {}).get("source_id") == "N09-s07-b035"
        and bool(section7 and section7.group(1).count('src="diagrams/N09-mapa-decision.svg"') == 1)
        and html.count('src="diagrams/N09-mapa-decision.svg"') == 1
        and diagram_min_px >= 28.0
        and diagram_min_pt >= 7.0
        and re.search(r"\.premium-magazine\.document-n09 \.infographic-boundaries[^\{]*\{[^}]*width:160mm", css) is not None
    )

    generated = generated_asset_audit(root, generation, html)
    consolidated_visuals = consolidated_image_manifest_audit(
        root,
        html,
        consolidated_images,
        generation,
        rights,
        diagram_content,
        n08_image_manifest_path,
        n08_image_manifest,
    )
    referents = referent_rights_audit(root, inventory, manifest, rights, page_texts[2])
    hotel_voices = hotel_voice_audit(root, html, "\n".join(page_texts))
    required_missing = [relative for relative in REQUIRED_FILES if not (root / relative).is_file()]
    aliases_ok = (
        (root / "metsi.css").read_bytes() == css_path.read_bytes()
        and read_json(root / "document.json") == manifest
    )

    root_object = reader.trailer["/Root"]
    mark_info = root_object.get("/MarkInfo") or {}
    metadata = reader.metadata or {}
    metadata_values = {key: str(metadata.get(key, "")) for key in EXPECTED_METADATA}
    metadata_ok = all(metadata_values[key] == value for key, value in EXPECTED_METADATA.items())
    semantic_alts_ok = all(
        expected in structure_alts
        for expected in (
            EXPECTED_COVER_ALT,
            EXPECTED_CONTENTS_ALT,
            EXPECTED_INFOGRAPHIC_ALT,
            *EXPECTED_PAUSE_ALTS,
            EXPECTED_CLOSING_ALT,
        )
    )
    pause_alts_ok = all(
        page and expected in alts_by_page.get(page, [])
        for page, expected in zip(pause_pages, EXPECTED_PAUSE_ALTS)
    )
    pause_html_count = html.count('class="full-bleed full-bleed-quote"')
    first_pause_html = html.find(EXPECTED_PAUSE_QUOTES[0])
    second_pause_html = html.find(EXPECTED_PAUSE_QUOTES[1])
    section1 = html.find('data-section="01"')
    section2 = html.find('data-section="02"')
    section6 = html.find('data-section="06"')
    section7_start = html.find('data-section="07"')
    pauses_in_order = (
        -1 not in (section1, first_pause_html, section2, section6, second_pause_html, section7_start)
        and section1 < first_pause_html < section2
        and section6 < second_pause_html < section7_start
    )
    forbidden = [font for font in rendered_fonts if any(token in font.casefold() for token in ("arial", "helvetica", "times"))]

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
            and content_integrity.get("word_counts", {}).get("substantive_from_thesis_through_synthesis") == 6637
            and content_integrity.get("references", {}).get("entries") == 14
            and all(content_integrity.get("references", {}).get("anchors", {}).values()),
            {"overall": content_integrity.get("overall"), "word_counts": content_integrity.get("word_counts"), "anchors": content_integrity.get("references", {}).get("anchors")},
        ),
        result(
            "source_manifest_has_324_blocks_exactly_once",
            len(source_ids) == EXPECTED_BLOCKS
            and len(set(source_ids)) == EXPECTED_BLOCKS
            and Counter(source_ids) == Counter(html_ids)
            and source_manifest.get("eligible_block_count") == EXPECTED_BLOCKS
            and integrity.get("status") == "PASS"
            and integrity.get("source_block_count") == integrity.get("rendered_source_id_count") == EXPECTED_BLOCKS,
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
        result("all_14_references_are_anchored", all(content_integrity.get("references", {}).get("anchors", {}).values()), content_integrity.get("references", {}).get("anchors")),
        result("pdf_is_distinct_finalized_artifact", sha256(pdf) != sha256(raw_pdf), {"raw": sha256(raw_pdf), "final": sha256(pdf)}),
        result(
            "pdf_has_28_a4_pages_and_plan_matches",
            a4_ok and planned_pages == EXPECTED_PAGES and qa.get("pages") == qa.get("a4_pages") == EXPECTED_PAGES,
            {"expected": EXPECTED_PAGES, "planned": planned_pages, "actual": len(reader.pages), "sizes": media_sizes},
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
        result("typography_uses_no_arial_helvetica_or_times", not forbidden and not qa.get("forbidden_fonts"), {"fonts": rendered_fonts, "forbidden": forbidden, "qa_forbidden": qa.get("forbidden_fonts")}),
        result("page_1_cover_reaches_all_edges", cover_bleed.get("passed") is True, cover_bleed),
        result("cover_is_native_bw_with_tonal_range_and_localized_shade", cover_ok, {"scan": cover_scan, "tone": cover_tones, "contract": cover_contract, "cover_rule": cover_rule, "shade_rule": shade_rule}),
        result(
            "cover_eyebrow_is_two_accessible_text_runs",
            '<span>LECTURA PREVIA</span><span>EDICIÓN 2026</span>' in html
            and "LECTURA PREVIA" in page_texts[0]
            and "EDICIÓN 2026" in page_texts[0]
            and not re.search(r"L\s+E\s+C\s+T\s+U\s+R\s+A", page_texts[0]),
            page_texts[0][:350],
        ),
        result("seven_imagegen_assets_are_unique_native_bw_tonal_and_hash_locked", generated["passed"], generated),
        result(
            "portable_image_manifest_covers_every_rendered_visual_and_its_provenance",
            consolidated_visuals["passed"],
            consolidated_visuals,
        ),
        result(
            "exactly_two_full_bleed_pauses_in_expected_positions",
            pause_html_count == 2
            and pauses_in_order
            and pause_pages == [5, 15]
            and all(value.get("passed") for value in pause_bleed.values())
            and pause_alts_ok,
            {"html_count": pause_html_count, "pages": pause_pages, "bleed": pause_bleed, "html_order": pauses_in_order},
        ),
        result(
            "reference_grade_infographic_is_exact_and_inserted_once",
            diagram_ok and diagram_page == 18 and EXPECTED_INFOGRAPHIC_ALT in alts_by_page.get(18, []),
            {"page": diagram_page, "sha256": sha256(diagram_source), "min_svg_px": diagram_min_px, "min_final_pt": round(diagram_min_pt, 2), "integration": diagram_integration},
        ),
        result("six_unique_referents_have_approved_rights_and_provenance", referents["passed"], referents),
        result("four_unique_hotel_horizonte_voices_are_present", hotel_voices["passed"], hotel_voices),
        result(
            "references_are_image_free_two_column_penultimate_page",
            reference_page == 27 == len(reader.pages) - 1 and reference_images == 0 and references_layout.get("passed"),
            {"page": reference_page, "images": reference_images, "columns": references_layout},
        ),
        result(
            "twelve_exact_urls_are_printed_and_annotated_only_on_references_page",
            source_urls == EXPECTED_URLS
            and external_links == EXPECTED_URLS
            and external_pages == {27: sorted(EXPECTED_URLS)},
            {"source": sorted(source_urls), "annotations": sorted(external_links), "pages": external_pages},
        ),
        result(
            "last_page_is_full_bleed_structured_matches_closing",
            closing_bleed.get("passed")
            and EXPECTED_CLOSING_CAPTION in page_texts[-1]
            and re.search(r"\b28\b", page_texts[-1]) is not None
            and "linkedin.com/in/carralbal" in page_texts[-1]
            and EXPECTED_CLOSING_ALT in alts_by_page.get(28, [])
            and EXPECTED_CLOSING_ALT in page_image_alts(reader, 28)
            and manifest.get("closing", {}).get("policy") == "canonical_structured_closing_without_quote"
            and qa.get("closing_quote_absent") is True,
            {"bleed": closing_bleed, "text": page_texts[-1], "xobject_alts": page_image_alts(reader, 28)},
        ),
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
        result("n08_final_pdf_regression_sha_is_unchanged", sha256(n08_pdf) == EXPECTED_N08_PDF_SHA, {"actual": sha256(n08_pdf), "expected": EXPECTED_N08_PDF_SHA}),
    ]

    passed = all(item["status"] == "PASS" for item in checks)
    report = {
        "document": "N09",
        "version": "v9-final",
        "validator": Path(__file__).name,
        "mode": "read-only",
        "status": "PASS" if passed else "FAIL",
        "failed_checks": [item["check"] for item in checks if item["status"] == "FAIL"],
        "source_sha256": sha256(source),
        "html_sha256": sha256(html_path),
        "css_sha256": sha256(css_path),
        "raw_pdf_sha256": sha256(raw_pdf),
        "pdf_sha256": sha256(pdf),
        "pdf_bytes": pdf.stat().st_size,
        "pages": len(reader.pages),
        "minimum_ordinary_page_fill": min(ordinary_fill.values()) if ordinary_fill else None,
        "checks": checks,
    }
    print(json.dumps(package_relative_report_paths(report, root), ensure_ascii=False, indent=2, default=str))
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(json.dumps({"document": "N09", "version": "v9-final", "status": "ERROR", "error": f"{type(error).__name__}: {error}"}, ensure_ascii=False, indent=2))
        sys.exit(2)
