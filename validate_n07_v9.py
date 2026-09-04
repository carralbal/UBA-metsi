#!/usr/bin/env python3
"""Deterministic, read-only release validator for METSI N07 v9.

The validator reads the canonical source, packaged HTML/CSS/manifests, the raw
and finalized PDFs, and the N06 regression lock.  It prints one JSON report to
stdout and never rewrites any release artifact.  Exit codes are 0 for PASS, 1
for a failed release gate, and 2 for an execution error.
"""

from __future__ import annotations

import argparse
import hashlib
import html as html_lib
import json
import math
import re
import statistics
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import pdfplumber
from PIL import Image
from pypdf import PdfReader


HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE / "N07-v9-final"
EXPECTED_SOURCE_SHA = "4e0416a028109761f0a9f498315946a62a147355c759054a733dd82902f639b6"
EXPECTED_N06_PDF_SHA = "7cd9de77fdb634f90f8f47a083a2f9e77cadc042621ae01b7b9f5fae09df7955"
EXPECTED_BLOCKS = 371
EXPECTED_PAGES = 31
EXPECTED_A4 = (594.96, 841.92)
EXPECTED_SECTIONS = [
    "Pregunta profesional",
    "La pregunta que fabricó la respuesta",
    "Tesis",
    "De N06 a N07: de la misión de evidencia a la conversación",
    "Movimiento 1 · Construir preguntas que no fabriquen la respuesta",
    "Movimiento 2 · Diseñar una situación en la que resulte posible decir",
    "Movimiento 3 · Convertir relatos en afirmaciones contrastables",
    "2026: transcribir y resumir automáticamente exige una cadena de evidencia",
    "De N07 a N08: de lo dicho a lo realizado",
    "Síntesis",
    "Cinco píldoras para recordar",
    "Glosario esencial",
    "Preguntas de preparación",
]
EXPECTED_ROUTES = (
    ["PROBLEMA"] * 4
    + ["DISTINCIONES", "DECISIONES", "PRUEBA"]
    + ["TRANSFERENCIA"] * 2
    + ["PREPARACIÓN"] * 4
)
EXPECTED_REFERENTS = [
    ("Svend Brinkmann", "assets/referent-svend-brinkmann.jpg"),
    ("Sasha Costanza-Chock", "assets/referent-sasha-costanza-chock.jpg"),
    ("Lucy Suchman", "assets/referent-lucy-suchman.jpg"),
    ("Reva Schwartz", "assets/referent-reva-schwartz.jpg"),
    ("Elham Tabassi", "assets/referent-elham-tabassi.jpg"),
    ("George Awad", "assets/referent-george-awad.jpg"),
]
EXPECTED_EDITORIAL = [f"assets/editorial-0{number}.png" for number in range(1, 5)]
EXPECTED_PAUSES = ["assets/pause-01.png", "assets/pause-02.png"]
EXPECTED_INTERNAL_IMAGES = [Path(value).name for value in EXPECTED_EDITORIAL + EXPECTED_PAUSES]
EXPECTED_URLS = {
    "https://doi.org/10.1037/h0061470",
    "https://doi.org/10.1177/1049732315617444",
    "https://doi.org/10.6028/NIST.AI.600-1",
    "https://doi.org/10.6028/NIST.AI.100-4",
    "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
}
EXPECTED_QUOTES = {
    5: "Cada pregunta ilumina una parte de la experiencia y deja otras en sombra.",
    13: "Un solo incidente no demuestra prevalencia ni causalidad. Sí puede refutar una afirmación universal.",
}
EXPECTED_COVER_ALT = (
    "Dos profesionales argentinos conversan en un espacio de trabajo contemporáneo, "
    "con amplio espacio negativo y una escala luminosa de grises, en una fotografía "
    "editorial concebida en blanco y negro"
)
EXPECTED_CONTENTS_ALT = (
    "Escena editorial en blanco y negro sobre preguntas, recorridos y decisiones "
    "posibles durante una investigación profesional."
)
EXPECTED_PAUSE_ALTS = {
    5: (
        "Dos sillas vacías frente a una puerta abierta en una sala de entrevistas, "
        "con luz lateral y una amplia escala de grises."
    ),
    13: (
        "Trabajadora de servicio vista a través de capas de vidrio y reflejos en un "
        "corredor, entre lo que el procedimiento declara y el trabajo que efectivamente ocurre."
    ),
}
EXPECTED_INFOGRAPHIC_ALT = (
    "Secuencia entre pregunta decisoria, episodio concreto, rastros y contraste, "
    "afirmación calibrada y decisión revisable La entrevista produce evidencia cuando "
    "conecta episodios y rastros con afirmaciones de alcance explícito y decisiones "
    "que todavía pueden revisarse."
)
EXPECTED_PILLS_ALT = "Cinco ideas para recordar"
EXPECTED_CLOSING_ALT = (
    "Diez fósforos dispuestos en secuencia vertical, desde intactos hasta consumidos "
    "y convertidos en ceniza."
)
EXPECTED_CLOSING_CAPTION = (
    "La secuencia vuelve visible que toda intervención consume recursos, deja huellas "
    "y necesita un criterio de cierre."
)
EXPECTED_COUNTS = {"pills": 5, "glossary": 13, "questions": 6, "references": 11}
EXPECTED_METADATA = {
    "/Title": "N07 · Entrevistar no es pedir requisitos",
    "/Author": "Diego Carralbal",
    "/Subject": "Metodología de Sistemas de Información · FCE · UBA",
}
EXPECTED_DIAGRAM_SHA = "f3e8fedacccaed9cf30ad00dd15485a04cbbd31c4bd840e14ec660c00161d8bc"
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
    "source/N07_entrevistar_no_es_pedir_requisitos-content-final.md",
    "diagrams/N07-mapa-decision.svg",
    "diagrams/N07-mapa-decision.json",
    "infographic-evidence-chain/n07-evidence-chain.svg",
    "infographic-evidence-chain/n07-evidence-chain.png",
    "infographic-evidence-chain/content-manifest.json",
    "infographic-evidence-chain/alt-text.md",
    "infographic-evidence-chain/qa-report.md",
    "infographic-evidence-chain/review.html",
    "output/N07-METSI-lectura-previa-v9.pdf",
    "output/N07-METSI-lectura-previa-v9-final.pdf",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(value: str) -> str:
    value = html_lib.unescape(value).replace("ﬁ", "fi").replace("ﬂ", "fl")
    return re.sub(r"[^0-9a-záéíóúüñ]+", "", value.casefold())


def words(value: str) -> list[str]:
    return re.findall(r"[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñÀ-ÿ]+", value)


def first_fragment(value: str, count: int = 8) -> str:
    tokens = words(value)
    return compact(" ".join(tokens[: min(count, len(tokens))]))


def block_is_rendered(value: str, compact_pdf: str) -> bool:
    tokens = words(value)
    if not tokens:
        return False
    count = min(10, len(tokens))
    fragments = {
        compact(" ".join(tokens[:count])),
        compact(" ".join(tokens[-count:])),
    }
    return all(fragment and fragment in compact_pdf for fragment in fragments)


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    return float(ordered[lower] * (upper - position) + ordered[upper] * (position - lower))


def result(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "status": "PASS" if passed else "FAIL", "detail": detail}


class HtmlInventory(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.images: list[dict[str, str]] = []
        self.local_refs: list[str] = []
        self.contributors: list[dict[str, str]] = []
        self.role_img_labels: list[str] = []
        self._contributor: dict[str, str] | None = None
        self._in_contributor_h3 = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if values.get("role") == "img":
            self.role_img_labels.append(values.get("aria-label", "").strip())
        if tag == "article" and "contributor" in values.get("class", "").split():
            self._contributor = {}
        if tag == "img":
            self.images.append(values)
            if self._contributor is not None:
                self._contributor["src"] = values.get("src", "")
                self._contributor["alt"] = values.get("alt", "")
        if tag == "h3" and self._contributor is not None:
            self._in_contributor_h3 = True
        for attribute in ("src", "href"):
            value = values.get(attribute, "")
            if value and not re.match(r"^(?:https?:|data:|mailto:|#)", value, re.I):
                self.local_refs.append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag == "h3":
            self._in_contributor_h3 = False
        if tag == "article" and self._contributor is not None:
            self.contributors.append(self._contributor)
            self._contributor = None

    def handle_data(self, data: str) -> None:
        if self._in_contributor_h3 and self._contributor is not None:
            self._contributor["name"] = self._contributor.get("name", "") + data


def links_by_page(reader: PdfReader) -> list[list[str]]:
    pages: list[list[str]] = []
    for page in reader.pages:
        links: list[str] = []
        for reference in page.get("/Annots", []):
            annotation = reference.get_object()
            action = annotation.get("/A")
            if action and action.get("/URI"):
                links.append(str(action.get("/URI")))
        pages.append(links)
    return pages


def structure_figures(reader: PdfReader) -> list[dict[str, Any]]:
    root = reader.trailer["/Root"].get("/StructTreeRoot")
    page_ids = {
        page.indirect_reference.idnum: number
        for number, page in enumerate(reader.pages, 1)
        if page.indirect_reference is not None
    }
    figures: list[dict[str, Any]] = []
    seen: set[int] = set()

    def walk(value: object, inherited_page: object | None = None) -> None:
        try:
            item = value.get_object()  # type: ignore[attr-defined]
        except Exception:
            item = value
        if isinstance(item, (dict, list, tuple)):
            identity = id(item)
            if identity in seen:
                return
            seen.add(identity)
        if isinstance(item, dict):
            page_ref = item.get("/Pg") or inherited_page
            if str(item.get("/S")) == "/Figure":
                page_number = None
                try:
                    page_number = page_ids.get(page_ref.idnum)  # type: ignore[union-attr]
                except Exception:
                    pass
                figures.append(
                    {
                        "page": page_number,
                        "alt": str(item.get("/Alt")) if item.get("/Alt") else None,
                    }
                )
            if item.get("/K") is not None:
                walk(item.get("/K"), page_ref)
        elif isinstance(item, (list, tuple)):
            for child in item:
                walk(child, inherited_page)

    if root:
        walk(root)
    return figures


def page_image_alts(reader: PdfReader, page_number: int) -> list[str]:
    page = reader.pages[page_number - 1]
    resources = page.get("/Resources")
    if not resources:
        return []
    xobjects = resources.get_object().get("/XObject")
    if not xobjects:
        return []
    values: list[str] = []
    for reference in xobjects.get_object().values():
        item = reference.get_object()
        if item.get("/Subtype") == "/Image" and item.get("/Alt"):
            values.append(str(item.get("/Alt")))
    return values


def edge_gaps(page: pdfplumber.page.Page, item: dict[str, Any]) -> dict[str, float]:
    return {
        "left": round(max(0.0, float(item.get("x0", 0))), 3),
        "right": round(max(0.0, float(page.width) - float(item.get("x1", 0))), 3),
        "top": round(max(0.0, float(item.get("top", 0))), 3),
        "bottom": round(max(0.0, float(page.height) - float(item.get("bottom", 0))), 3),
    }


def full_bleed_image(page: pdfplumber.page.Page, tolerance: float = 1.0) -> dict[str, Any]:
    if not page.images:
        return {"passed": False, "reason": "no image", "gaps_pt": None}
    image = max(page.images, key=lambda item: float(item["width"]) * float(item["height"]))
    gaps = edge_gaps(page, image)
    return {
        "passed": all(value <= tolerance for value in gaps.values()),
        "tolerance_pt": tolerance,
        "gaps_pt": gaps,
        "bbox": {
            key: round(float(image[key]), 3)
            for key in ("x0", "x1", "top", "bottom")
        },
    }


def color_luminance(color: object) -> float | None:
    if isinstance(color, (int, float)):
        return float(color)
    if isinstance(color, (tuple, list)) and color:
        values = [float(value) for value in color[:3]]
        if len(values) == 1:
            return values[0]
        if len(values) >= 3:
            return 0.2126 * values[0] + 0.7152 * values[1] + 0.0722 * values[2]
    return None


def dark_full_page_background(
    page: pdfplumber.page.Page, tolerance: float = 1.0, maximum_luminance: float = 0.20
) -> dict[str, Any]:
    rectangles: list[dict[str, Any]] = []
    for rectangle in page.rects:
        gaps = edge_gaps(page, rectangle)
        luminance = color_luminance(rectangle.get("non_stroking_color"))
        if all(value <= tolerance for value in gaps.values()) and luminance is not None:
            rectangles.append(
                {
                    "gaps_pt": gaps,
                    "luminance": round(luminance, 4),
                    "color": rectangle.get("non_stroking_color"),
                }
            )
    return {
        "passed": any(item["luminance"] <= maximum_luminance for item in rectangles),
        "maximum_luminance": maximum_luminance,
        "full_page_rectangles": rectangles,
    }


def page_extents(document: pdfplumber.PDF) -> dict[int, dict[str, float]]:
    extents: dict[int, dict[str, float]] = {}
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


def cover_tone(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"passed": False, "reason": "cover source missing"}
    with Image.open(path) as image:
        sample = image.convert("RGB")
        sample.thumbnail((512, 512))
        getter = getattr(sample, "get_flattened_data", None)
        pixels = list(getter() if getter else sample.getdata())
    spreads = [max(pixel) - min(pixel) for pixel in pixels]
    luminance = [
        0.2126 * red + 0.7152 * green + 0.0722 * blue
        for red, green, blue in pixels
    ]
    p95_spread = percentile([float(value) for value in spreads], 0.95)
    p05 = percentile(luminance, 0.05)
    p95 = percentile(luminance, 0.95)
    tonal_std = statistics.pstdev(luminance)
    passed = p95_spread <= 3.0 and p05 <= 70.0 and p95 >= 200.0 and tonal_std >= 35.0
    return {
        "passed": passed,
        "channel_spread_p95": round(p95_spread, 2),
        "luminance_p05": round(p05, 2),
        "luminance_p95": round(p95, 2),
        "luminance_stddev": round(tonal_std, 2),
    }


def image_monochrome(path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        size = list(image.size)
        sample = image.convert("RGB")
        sample.thumbnail((256, 256))
        getter = getattr(sample, "get_flattened_data", None)
        pixels = list(getter() if getter else sample.getdata())
    spreads = [float(max(pixel) - min(pixel)) for pixel in pixels]
    return {
        "file": str(path),
        "size": size,
        "sha256": sha256(path),
        "channel_spread_p95": round(percentile(spreads, 0.95), 2),
        "monochrome": percentile(spreads, 0.95) <= 3.0,
    }


def local_reference_issues(
    root: Path, inventory: HtmlInventory, css: str
) -> list[dict[str, str]]:
    references = list(inventory.local_refs)
    for value in re.findall(r"url\(([^)]+)\)", css, re.I):
        value = value.strip().strip("\"'")
        if value and not re.match(r"^(?:https?:|data:|#)", value, re.I):
            references.append(value)
    issues: list[dict[str, str]] = []
    root_resolved = root.resolve()
    for value in sorted(set(references)):
        candidate = (root / value).resolve()
        try:
            inside = candidate.is_relative_to(root_resolved)
        except AttributeError:
            inside = str(candidate).startswith(str(root_resolved) + "/")
        if Path(value).is_absolute() or not inside:
            issues.append({"reference": value, "reason": "not package-relative"})
        elif not candidate.exists():
            issues.append({"reference": value, "reason": "missing target"})
    return issues


def complete_image_manifest_audit(
    root: Path, data: dict[str, Any]
) -> dict[str, Any]:
    """Verify that the consolidated image inventory is portable and hash locked."""
    assets = data.get("assets", [])
    rendered_count = data.get("rendered_asset_count")
    supporting_count = data.get("supporting_source_count")
    issues: list[dict[str, Any]] = []
    files: list[str] = []
    root_resolved = root.resolve()

    for record in assets if isinstance(assets, list) else []:
        if not isinstance(record, dict):
            issues.append({"file": None, "reasons": ["asset record is not an object"]})
            continue
        relative = str(record.get("file", ""))
        files.append(relative)
        reasons: list[str] = []
        path_value = Path(relative)
        candidate = (root / path_value).resolve()
        try:
            inside = candidate.is_relative_to(root_resolved)
        except AttributeError:
            inside = str(candidate).startswith(str(root_resolved) + "/")
        if not relative or path_value.is_absolute() or ".." in path_value.parts or not inside:
            reasons.append("file is not a safe package-relative path")
        elif not candidate.is_file():
            reasons.append("file does not exist")
        elif record.get("sha256") != sha256(candidate):
            reasons.append("sha256 mismatch")
        if not record.get("role") or not record.get("origin") or not record.get("rights_status"):
            reasons.append("role, origin, or rights status missing")
        if reasons:
            issues.append({"file": relative, "reasons": reasons})

    serialized = json.dumps(data, ensure_ascii=False)
    portability_markers = [marker for marker in ("/Users/", "/private/tmp/", "file://") if marker in serialized]
    supporting_roles = {
        "cover-source",
        "editable-infographic-source",
    }
    actual_supporting = sum(
        1 for record in assets if isinstance(record, dict) and record.get("role") in supporting_roles
    ) if isinstance(assets, list) else 0
    actual_rendered = len(assets) - actual_supporting if isinstance(assets, list) else 0
    counts_ok = (
        isinstance(assets, list)
        and rendered_count == 19
        and supporting_count == 2
        and len(assets) == rendered_count + supporting_count == 21
        and actual_rendered == rendered_count
        and actual_supporting == supporting_count
    )
    passed = (
        counts_ok
        and len(files) == len(set(files))
        and not issues
        and not portability_markers
        and data.get("document") == "N07"
        and data.get("edition") == "v9-final"
        and bool(data.get("policy"))
    )
    return {
        "passed": passed,
        "entries": len(assets) if isinstance(assets, list) else None,
        "rendered_assets": actual_rendered,
        "supporting_sources": actual_supporting,
        "unique_files": len(set(files)),
        "issues": issues,
        "nonportable_markers": portability_markers,
    }


def reference_columns(page: pdfplumber.page.Page) -> dict[str, Any]:
    expected_left = {"Brinkmann,", "Klein,", "Flanagan,", "Malterud,", "Costanza-Chock,", "Beyer,"}
    expected_right = {"Braun,", "Suchman,", "Unión"}
    left: dict[str, float] = {}
    right: dict[str, float] = {}
    national: list[float] = []
    for word in page.extract_words(use_text_flow=False):
        token = str(word.get("text", ""))
        x0 = float(word.get("x0", 0))
        if token in expected_left and token not in left:
            left[token] = round(x0, 2)
        if token in expected_right and token not in right:
            right[token] = round(x0, 2)
        if token == "National":
            national.append(round(x0, 2))
    passed = (
        set(left) == expected_left
        and set(right) == expected_right
        and len(national) == 2
        and all(value < page.width * 0.45 for value in left.values())
        and all(value > page.width * 0.45 for value in right.values())
        and all(value > page.width * 0.45 for value in national)
    )
    return {"passed": passed, "left": left, "right": right, "national": national}


def generated_image_audit(root: Path, data: dict[str, Any], html: str) -> dict[str, Any]:
    expected = EXPECTED_EDITORIAL + EXPECTED_PAUSES
    records = {
        str(record.get("file")): record
        for record in data.get("assets", [])
        if isinstance(record, dict)
    }
    assets: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    for relative in expected:
        record = records.get(relative)
        path = root / relative
        reasons: list[str] = []
        if not record:
            reasons.append("missing provenance record")
        if not path.exists():
            reasons.append("missing asset")
        if path.exists() and record:
            if record.get("sha256") != sha256(path):
                reasons.append("sha256 mismatch")
            if not record.get("production_brief") or not record.get("alt"):
                reasons.append("production brief or alt missing")
            if [record.get("width"), record.get("height")] != list(Image.open(path).size):
                reasons.append("dimensions mismatch")
            info = image_monochrome(path)
            assets.append(info)
            if not info["monochrome"]:
                reasons.append("asset is not monochrome")
        if html.count(relative) != 1:
            reasons.append(f"HTML reference count is {html.count(relative)}")
        if reasons:
            invalid.append({"file": relative, "reasons": reasons})
    hashes = [item["sha256"] for item in assets]
    expected_roles = {
        **{value: "editorial-photo" for value in EXPECTED_EDITORIAL[:3]},
        EXPECTED_EDITORIAL[3]: "contents-photo",
        **{value: "full-bleed-pause" for value in EXPECTED_PAUSES},
    }
    roles_ok = all(records.get(value, {}).get("role") == role for value, role in expected_roles.items())
    passed = (
        not invalid
        and len(assets) == 6
        and len(set(hashes)) == 6
        and roles_ok
        and data.get("generator") == "OpenAI ImageGen"
        and "blanco y negro" in str(data.get("editorial_rule", "")).casefold()
    )
    return {
        "passed": passed,
        "assets": assets,
        "invalid": invalid,
        "unique_hashes": len(set(hashes)),
        "roles_ok": roles_ok,
        "generator": data.get("generator"),
        "policy_present": bool(data.get("editorial_rule")),
    }


def portrait_audit(
    root: Path,
    inventory: HtmlInventory,
    manifest: dict[str, Any],
    rights_data: dict[str, Any],
    pdf_page_3_text: str,
) -> dict[str, Any]:
    actual = [
        (item.get("name", "").strip(), item.get("src", ""))
        for item in inventory.contributors
    ]
    manifest_records = manifest.get("portrait_references", [])
    manifest_files = [
        "assets/" + str(item.get("file", "")).removeprefix("assets/")
        for item in manifest_records
        if isinstance(item, dict)
    ]
    rights_records = rights_data.get("assets", [])
    rights_by_file = {
        str(item.get("file")): item for item in rights_records if isinstance(item, dict)
    }
    assets: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    for name, relative in EXPECTED_REFERENTS:
        path = root / relative
        manifest_record = next(
            (item for item in manifest_records if "assets/" + str(item.get("file", "")).removeprefix("assets/") == relative),
            None,
        )
        rights_record = rights_by_file.get(relative)
        reasons: list[str] = []
        if not path.exists():
            reasons.append("missing portrait")
        if not manifest_record:
            reasons.append("missing main-manifest record")
        if not rights_record:
            reasons.append("missing rights record")
        if path.exists():
            with Image.open(path) as image:
                size = list(image.size)
                mode = image.mode
            digest = sha256(path)
            assets.append({"file": relative, "size": size, "mode": mode, "sha256": digest})
            if size != [720, 720] or mode not in {"L", "LA"}:
                reasons.append(f"expected 720x720 grayscale, got {size} {mode}")
            if manifest_record and manifest_record.get("sha256") != digest:
                reasons.append("main-manifest sha256 mismatch")
            if rights_record and rights_record.get("sha256") != digest:
                reasons.append("rights-manifest sha256 mismatch")
        for record_name, record in (("main", manifest_record), ("rights", rights_record)):
            if record and not all(record.get(field) for field in ("source_page", "license_url", "credit_line")):
                reasons.append(f"{record_name} record lacks source, license, or credit")
        if rights_record and rights_record.get("approved") is not True:
            reasons.append("rights record is not approved")
        if compact(name) not in compact(pdf_page_3_text):
            reasons.append("name missing from PDF page 3")
        if reasons:
            invalid.append({"name": name, "file": relative, "reasons": reasons})
    hashes = [item["sha256"] for item in assets]
    alts_ok = all(item.get("alt", "").strip() for item in inventory.contributors)
    passed = (
        actual == EXPECTED_REFERENTS
        and manifest_files == [relative for _, relative in EXPECTED_REFERENTS]
        and len(rights_records) == 6
        and rights_data.get("asset_count") == 6
        and len(set(hashes)) == 6
        and len(assets) == 6
        and not invalid
        and alts_ok
        and bool(rights_data.get("policy"))
        and rights_data.get("identity_and_uniqueness_review", {}).get("status") == "passed"
    )
    return {
        "passed": passed,
        "actual": actual,
        "expected": EXPECTED_REFERENTS,
        "manifest_files": manifest_files,
        "assets": assets,
        "invalid": invalid,
        "html_alts_complete": alts_ok,
        "rights_policy_present": bool(rights_data.get("policy")),
    }


def heading_body_alignment(
    entries: list[dict[str, Any]], page_texts: list[str]
) -> dict[str, Any]:
    compact_pages = [compact(text) for text in page_texts]
    records: list[dict[str, Any]] = []
    for index, entry in enumerate(entries[:-1]):
        if entry.get("kind") not in {"heading-2", "heading-3"}:
            continue
        following = entries[index + 1]
        heading_pages = {
            page_number
            for page_number, text in enumerate(compact_pages, 1)
            if compact(str(entry.get("text", ""))) in text
        }
        fragment = first_fragment(str(following.get("text", "")))
        body_pages = {
            page_number
            for page_number, text in enumerate(compact_pages, 1)
            if fragment and fragment in text
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
    failed = [item for item in records if not item["same_pages"]]
    return {"passed": len(records) == 51 and not failed, "checked": len(records), "failed": failed}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="N07-v9-final package directory (default: sibling N07-v9-final)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    source = root / "source/N07_entrevistar_no_es_pedir_requisitos-content-final.md"
    canonical = HERE / "N07-content-final/source/N07_entrevistar_no_es_pedir_requisitos-content-final.md"
    content_integrity_path = HERE / "N07-content-final/provenance/integrity-report.json"
    pdf = root / "output/N07-METSI-lectura-previa-v9-final.pdf"
    raw_pdf = root / "output/N07-METSI-lectura-previa-v9.pdf"
    html_path = root / "index.html"
    css_path = root / "magazine.css"
    manifest_path = root / "manifest.json"
    source_manifest_path = root / "source-manifest.json"
    integrity_path = root / "integrity-report.json"
    qa_path = root / "qa-report.json"
    generation_manifest_path = root / "image-generation-manifest.json"
    rights_manifest_path = root / "image-rights-manifest.json"
    image_manifest_path = root / "image-manifest.json"
    n06_pdf = HERE / "N06-v9-final/output/N06-METSI-lectura-previa-v9-final.pdf"

    essential = [
        source,
        canonical,
        content_integrity_path,
        pdf,
        raw_pdf,
        html_path,
        css_path,
        manifest_path,
        source_manifest_path,
        integrity_path,
        qa_path,
        generation_manifest_path,
        rights_manifest_path,
        image_manifest_path,
        n06_pdf,
    ]
    missing_essential = [str(path) for path in essential if not path.exists()]
    if missing_essential:
        print(
            json.dumps(
                {
                    "document": "N07",
                    "version": "v9-final",
                    "status": "ERROR",
                    "missing": missing_essential,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    source_text = source.read_text(encoding="utf-8")
    html = html_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    integrity = json.loads(integrity_path.read_text(encoding="utf-8"))
    qa = json.loads(qa_path.read_text(encoding="utf-8"))
    generation_manifest = json.loads(generation_manifest_path.read_text(encoding="utf-8"))
    rights_manifest = json.loads(rights_manifest_path.read_text(encoding="utf-8"))
    image_manifest = json.loads(image_manifest_path.read_text(encoding="utf-8"))
    content_integrity = json.loads(content_integrity_path.read_text(encoding="utf-8"))
    reader = PdfReader(str(pdf))
    page_texts = [page.extract_text() or "" for page in reader.pages]
    pdf_text = "\n".join(page_texts)
    compact_pdf = compact(pdf_text)
    body, references = source_text.split("## Referencias base", 1)
    headings = re.findall(r"^## (.+)$", source_text, flags=re.M)

    inventory = HtmlInventory()
    inventory.feed(html)
    local_errors = local_reference_issues(root, inventory, css)
    link_pages = links_by_page(reader)
    external_pages = {
        number: sorted({uri for uri in links if "linkedin.com/in/carralbal" not in uri})
        for number, links in enumerate(link_pages, 1)
        if any("linkedin.com/in/carralbal" not in uri for uri in links)
    }
    external_links = {
        uri
        for links in link_pages
        for uri in links
        if "linkedin.com/in/carralbal" not in uri
    }
    linkedin_per_page = [
        sum(1 for uri in links if "linkedin.com/in/carralbal" in uri)
        for links in link_pages
    ]
    source_urls = {value.rstrip(".,") for value in re.findall(r"https://\S+", references)}

    figures = structure_figures(reader)
    alts_by_page: dict[int | None, list[str | None]] = {}
    for figure in figures:
        alts_by_page.setdefault(figure["page"], []).append(figure["alt"])

    with pdfplumber.open(pdf) as document:
        extents = page_extents(document)
        cover_bleed = full_bleed_image(document.pages[0])
        cover_words = document.pages[0].extract_words(use_text_flow=False)
        cover_title_end = max(
            word["x1"] for word in cover_words if word["text"] == "pedir"
        )
        cover_quote_start = min(
            word["x0"] for word in cover_words if word["text"] == "episodios,"
        )
        cover_title_quote_gutter = cover_quote_start - cover_title_end
        page4_dark = dark_full_page_background(document.pages[3])
        pause_bleed = {
            page: full_bleed_image(document.pages[page - 1]) for page in EXPECTED_QUOTES
        }
        closing_bleed = full_bleed_image(document.pages[30])
        columns = reference_columns(document.pages[29])
        reference_images = len(document.pages[29].images)
        image_pages = {number: len(page.images) for number, page in enumerate(document.pages, 1)}
        rendered_fonts = sorted({str(char.get("fontname", "")) for page in document.pages for char in page.chars})

    media_sizes: list[dict[str, float]] = []
    a4_ok = len(reader.pages) == EXPECTED_PAGES
    for number, page in enumerate(reader.pages, 1):
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        media_sizes.append({"page": number, "width": round(width, 3), "height": round(height, 3)})
        if abs(width - EXPECTED_A4[0]) > 0.75 or abs(height - EXPECTED_A4[1]) > 0.75:
            a4_ok = False

    entries = source_manifest.get("eligible_blocks", [])
    all_source_ids = [str(entry.get("source_id", "")) for entry in entries]
    html_source_ids = re.findall(r'data-source-id="([^"]+)"', html)
    missing_rendered = [
        entry.get("source_id")
        for entry in entries
        if not block_is_rendered(str(entry.get("text", "")), compact_pdf)
    ]
    alignment = heading_body_alignment(entries, page_texts)

    route_pattern = re.compile(
        r"(?m)^(\d{2})\s+METSI\s*·\s*N07\s+"
        r"(PROBLEMA|DISTINCIONES|DECISIONES|PRUEBA|TRANSFERENCIA|PREPARACIÓN)\s*$"
    )
    pdf_headers: list[tuple[int, int, str]] = []
    for page_number, text in enumerate(page_texts, 1):
        for match in route_pattern.finditer(text):
            pdf_headers.append((int(match.group(1)), page_number, match.group(2)))
    pdf_headers.sort(key=lambda item: item[0])
    pdf_routes = [route for _, _, route in pdf_headers]
    section_pages = [page for _, page, _ in pdf_headers]

    html_routes: list[str] = []
    html_section_positions: list[int] = []
    for number in range(1, 14):
        marker = f'data-section="{number:02d}"'
        position = html.find(marker)
        html_section_positions.append(position)
        section_match = re.search(
            rf'<section\b[^>]*data-section="{number:02d}"[^>]*>(.*?)</section>',
            html,
            re.S,
        )
        route_match = (
            re.search(
                r"<em>(PROBLEMA|DISTINCIONES|DECISIONES|PRUEBA|TRANSFERENCIA|PREPARACIÓN)</em>",
                section_match.group(1),
            )
            if section_match
            else None
        )
        html_routes.append(route_match.group(1) if route_match else "")

    contents_text = compact(page_texts[1])
    contents_positions = [contents_text.find(compact(heading)) for heading in EXPECTED_SECTIONS]
    html_id_positions = [html.find(f'data-source-id="{source_id}"') for source_id in all_source_ids]

    pills_block = source_text.split("## Cinco píldoras para recordar", 1)[1].split("## Glosario esencial", 1)[0]
    glossary_block = source_text.split("## Glosario esencial", 1)[1].split("## Preguntas de preparación", 1)[0]
    questions_block = source_text.split("## Preguntas de preparación", 1)[1].split("## Referencias base", 1)[0]
    counts = {
        "pills": len(re.findall(r"^\d+\. \*\*", pills_block, re.M)),
        "glossary": len(re.findall(r"^- \*\*", glossary_block, re.M)),
        "questions": len(re.findall(r"^\d+\. ", questions_block, re.M)),
        "references": len(re.findall(r"^- ", references, re.M)),
    }

    page28_compact = compact(page_texts[27])
    page28_reading_tokens = [
        "11 METSI · N07 PREPARACIÓN",
        "Cinco píldoras para recordar",
        "1. Toda pregunta propone un marco posible para la respuesta.",
        "2. Un relato sincero puede ser impreciso y seguir siendo valioso.",
        "3. Los episodios enseñan más que las opiniones generales.",
        "4. Contradicción no es ruido: puede señalar fronteras o significados distintos.",
        "5. El resumen automático nunca reemplaza la cadena hacia la fuente.",
    ]
    page28_reading_positions = [
        page28_compact.find(compact(token)) for token in page28_reading_tokens
    ]

    sondas_heading = next(
        entry for entry in entries if entry.get("text") == "Sondas útiles:"
    )
    sondas_first_item = next(
        entry for entry in entries if entry.get("source_id") == "N07-s06-b068"
    )
    sondas_heading_pages = {
        page_number
        for page_number, text in enumerate(page_texts, 1)
        if compact(str(sondas_heading.get("text", ""))) in compact(text)
    }
    sondas_first_item_fragment = first_fragment(str(sondas_first_item.get("text", "")))
    sondas_first_item_pages = {
        page_number
        for page_number, text in enumerate(page_texts, 1)
        if sondas_first_item_fragment in compact(text)
    }
    sondas_shared_pages = sorted(sondas_heading_pages & sondas_first_item_pages)

    protocol_item_pages: dict[int, list[int]] = {}
    for item_number, source_id in ((8, "N07-s08-b017"), (9, "N07-s08-b018"), (10, "N07-s08-b019")):
        entry = next(entry for entry in entries if entry.get("source_id") == source_id)
        fragment = first_fragment(str(entry.get("text", "")))
        protocol_item_pages[item_number] = [
            page_number
            for page_number, text in enumerate(page_texts, 1)
            if fragment in compact(text)
        ]
    item10_pages = set(protocol_item_pages[10])
    protocol_last_item_not_isolated = not (
        27 in item10_pages
        and 27 not in set(protocol_item_pages[8])
        and 27 not in set(protocol_item_pages[9])
    )

    anchor_patterns = {
        "Brinkmann y Kvale (2015)": r"Brinkmann y Kvale \(2015\)",
        "Klein (1998)": r"Klein \(1998\)",
        "Flanagan (1954)": r"Flanagan \(1954\)",
        "Malterud, Siersma y Guassora (2016)": r"Malterud,\s*Siersma y Guassora \(2016\)",
        "Costanza-Chock (2020)": r"Costanza-Chock \(2020\)",
        "Beyer y Holtzblatt (1997)": r"Beyer y Holtzblatt \(1997\)",
        "Braun y Clarke (2021)": r"Braun y Clarke \(2021\)",
        "Suchman (2007)": r"Suchman \(2007\)",
        "NIST AI 600-1 (2024)": r"NIST AI 600-1 \(2024\)",
        "NIST AI 100-4 (2024)": r"NIST AI 100-4 \(2024\)",
        "Reglamento europeo 2024/1689": r"Reglamento europeo 2024/1689",
    }
    anchors = {name: bool(re.search(pattern, body)) for name, pattern in anchor_patterns.items()}

    generated = generated_image_audit(root, generation_manifest, html)
    portraits = portrait_audit(root, inventory, manifest, rights_manifest, page_texts[2])
    complete_images = complete_image_manifest_audit(root, image_manifest)

    cover_source = root / "assets/cover-source-premium-bw-v1.png"
    cover_alias = root / "assets/cover.png"
    cover_contract = manifest.get("cover", {})
    tone = cover_tone(cover_source)
    cover_rule_match = re.search(r"\.cover-n07>img\{([^}]*)\}", css)
    cover_rule = cover_rule_match.group(1) if cover_rule_match else ""
    shade_match = re.search(r"\.cover-n07 \.cover-shade\{([^}]*)\}", css)
    shade_rule = shade_match.group(1) if shade_match else ""
    shade_alphas = [
        float(value)
        for value in re.findall(r"rgba\([^,]+,[^,]+,[^,]+,\s*([0-9.]+)\)", shade_rule)
    ]
    localized_light_shade = (
        bool(shade_rule)
        and "linear-gradient" in shade_rule
        and "inset:0" in shade_rule
        and "width:100%" in shade_rule
        and "height:100%" in shade_rule
        and bool(shade_alphas)
        and max(shade_alphas) <= 0.55
        and sum(1 for value in shade_alphas if value == 0.0) >= 2
    )
    no_css_grayscale = (
        "filter:none" in cover_rule
        and "grayscale(" not in cover_rule
        and "saturate(0" not in cover_rule
    )
    cover_hashes_ok = (
        cover_source.exists()
        and cover_alias.exists()
        and sha256(cover_source) == sha256(cover_alias) == cover_contract.get("sha256")
    )

    diagram_source = root / "infographic-evidence-chain/n07-evidence-chain.svg"
    diagram_copy = root / "diagrams/N07-mapa-decision.svg"
    diagram_contract = manifest.get("diagram", {})
    section7_match = re.search(
        r'<section\b[^>]*data-section="07"[^>]*>(.*?)</section>', html, re.S
    )
    diagram_in_section7 = bool(
        section7_match and 'src="diagrams/N07-mapa-decision.svg"' in section7_match.group(1)
    )
    diagram_ok = (
        sha256(diagram_source) == sha256(diagram_copy) == EXPECTED_DIAGRAM_SHA
        and diagram_contract.get("source_sha256") == EXPECTED_DIAGRAM_SHA
        and diagram_contract.get("topology") == "reference-grade-interview-evidence-decision-chain"
        and diagram_in_section7
    )
    diagram_svg = diagram_source.read_text(encoding="utf-8")
    diagram_font_sizes = [
        float(value)
        for value in re.findall(r"font-size(?:\s*:\s*|=\")([0-9.]+)", diagram_svg)
    ]
    diagram_min_font_px = min(diagram_font_sizes) if diagram_font_sizes else 0.0
    diagram_final_width_mm = 160.0
    diagram_min_font_pt = diagram_min_font_px * diagram_final_width_mm / 1800.0 * 72.0 / 25.4

    ordinary_pages = [page for page in range(2, 31) if page not in {4, 5, 13}]
    ordinary_fill = {page: extents.get(page, {}).get("fill", 0.0) for page in ordinary_pages}
    underfilled = {page: fill for page, fill in ordinary_fill.items() if fill < 0.55}

    reference_pdf_compact = re.sub(r"\s+", "", page_texts[29])
    printed_urls = {url: url in reference_pdf_compact for url in EXPECTED_URLS}
    reference_order_tokens = [
        "Brinkmann, S.",
        "Klein, G.",
        "Flanagan, J. C.",
        "Malterud, K.",
        "Costanza-Chock, S.",
        "Beyer, H.",
        "Braun, V.",
        "Suchman, L. A.",
        "National Institute of Standards and Technology (2024). Artificial Intelligence",
        "National Institute of Standards and Technology (2024). Reducing Risks",
        "Unión Europea (2024).",
    ]
    compact_reference_text = compact(page_texts[29])
    reference_positions = [compact_reference_text.find(compact(token)) for token in reference_order_tokens]

    root_object = reader.trailer["/Root"]
    mark_info = root_object.get("/MarkInfo") or {}
    required_structure_alts = {
        1: EXPECTED_COVER_ALT,
        2: EXPECTED_CONTENTS_ALT,
        5: EXPECTED_PAUSE_ALTS[5],
        13: EXPECTED_PAUSE_ALTS[13],
        18: EXPECTED_INFOGRAPHIC_ALT,
        28: EXPECTED_PILLS_ALT,
        31: EXPECTED_CLOSING_ALT,
    }
    structure_alts_ok = all(
        expected in alts_by_page.get(page, [])
        for page, expected in required_structure_alts.items()
    )
    html_semantic_images_ok = (
        all(inventory.role_img_labels)
        and len(inventory.role_img_labels) >= 4
        and all(
            item.get("alt", "").strip()
            for item in inventory.images
            if item.get("src", "")
            in {
                "assets/cover.png",
                "assets/editorial-04.png",
                *EXPECTED_PAUSES,
                "assets/matches-close.png",
                *[relative for _, relative in EXPECTED_REFERENTS],
            }
        )
    )

    metadata = reader.metadata or {}
    metadata_values = {key: str(metadata.get(key, "")) for key in EXPECTED_METADATA}
    metadata_ok = all(metadata_values[key] == value for key, value in EXPECTED_METADATA.items())
    metadata_ok = metadata_ok and all(
        token in str(metadata.get("/Keywords", "")) for token in ("METSI", "UBA", "Investigación")
    )

    required_missing = [name for name in REQUIRED_FILES if not (root / name).exists()]
    aliases_ok = (
        (root / "metsi.css").read_bytes() == css_path.read_bytes()
        and json.loads((root / "document.json").read_text(encoding="utf-8")) == manifest
    )
    image_usage_pages_ok = (
        image_pages.get(2) == 1
        and image_pages.get(7) == 1
        and image_pages.get(17) == 1
        and image_pages.get(25) == 5
        and image_pages.get(5) == 1
        and image_pages.get(13) == 1
    )
    pause_html_count = html.count('class="full-bleed full-bleed-quote"')

    checks = [
        result("required_release_files_present", not required_missing, {"missing": required_missing}),
        result(
            "consolidated_image_manifest_is_complete_portable_and_hash_locked",
            complete_images["passed"],
            complete_images,
        ),
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
            and content_integrity.get("references", {}).get("entries") == 11
            and all(content_integrity.get("references", {}).get("anchors", {}).values()),
            {"overall": content_integrity.get("overall"), "word_counts": content_integrity.get("word_counts"), "anchors": content_integrity.get("references", {}).get("anchors")},
        ),
        result(
            "source_manifest_has_371_blocks_exactly_once",
            len(all_source_ids) == EXPECTED_BLOCKS
            and len(set(all_source_ids)) == EXPECTED_BLOCKS
            and Counter(all_source_ids) == Counter(html_source_ids)
            and integrity.get("status") == "PASS"
            and integrity.get("source_block_count") == EXPECTED_BLOCKS,
            {"manifest": len(all_source_ids), "unique_manifest": len(set(all_source_ids)), "html": len(html_source_ids), "unique_html": len(set(html_source_ids)), "integrity": integrity},
        ),
        result("all_371_source_blocks_have_rendered_fragments", not missing_rendered, {"checked": len(entries), "missing": missing_rendered}),
        result("source_id_reading_order_is_preserved_in_html", all(position >= 0 for position in html_id_positions) and html_id_positions == sorted(html_id_positions), {"ids_checked": len(html_id_positions)}),
        result("canonical_13_section_structure", headings == EXPECTED_SECTIONS + ["Referencias base"], headings),
        result("content_counts_close", counts == EXPECTED_COUNTS, {"actual": counts, "expected": EXPECTED_COUNTS}),
        result(
            "page_28_section_11_heading_precedes_all_five_pills_in_extracted_order",
            all(position >= 0 for position in page28_reading_positions)
            and page28_reading_positions == sorted(page28_reading_positions),
            {"tokens": page28_reading_tokens, "positions": page28_reading_positions},
        ),
        result(
            "sondas_utiles_label_stays_with_its_first_list_item",
            bool(sondas_shared_pages),
            {
                "heading_source_id": sondas_heading.get("source_id"),
                "first_item_source_id": sondas_first_item.get("source_id"),
                "heading_pages": sorted(sondas_heading_pages),
                "first_item_pages": sorted(sondas_first_item_pages),
                "shared_pages": sondas_shared_pages,
            },
        ),
        result(
            "protocol_item_10_does_not_open_page_27_as_an_isolated_list_item",
            protocol_last_item_not_isolated,
            {"item_pages": protocol_item_pages},
        ),
        result("all_11_references_are_anchored", all(anchors.values()), anchors),
        result(
            "pdf_is_distinct_finalized_artifact",
            sha256(pdf) != sha256(raw_pdf),
            {"raw_sha256": sha256(raw_pdf), "final_sha256": sha256(pdf)},
        ),
        result(
            "pdf_has_31_a4_pages",
            a4_ok and qa.get("pages") == 31 and qa.get("a4_pages") == 31,
            {"pages": len(reader.pages), "sizes": media_sizes},
        ),
        result("pdf_metadata_is_complete", metadata_ok, {"metadata": metadata_values, "keywords": str(metadata.get("/Keywords", ""))}),
        result(
            "contents_and_section_reading_order_are_complete",
            all(position >= 0 for position in contents_positions)
            and contents_positions == sorted(contents_positions)
            and page_texts[1].count("SIN NUM.") >= 2
            and [number for number, _, _ in pdf_headers] == list(range(1, 14))
            and section_pages == sorted(section_pages)
            and all(position >= 0 for position in html_section_positions)
            and html_section_positions == sorted(html_section_positions),
            {"contents_positions": dict(zip(EXPECTED_SECTIONS, contents_positions)), "pdf_headers": pdf_headers, "sin_num": page_texts[1].count("SIN NUM.")},
        ),
        result(
            "route_is_exact_in_html_and_pdf",
            pdf_routes == EXPECTED_ROUTES and html_routes == EXPECTED_ROUTES,
            {"pdf": pdf_routes, "html": html_routes, "expected": EXPECTED_ROUTES, "counts": dict(Counter(pdf_routes))},
        ),
        result("all_source_headings_keep_following_body_on_same_page", alignment["passed"], alignment),
        result("ordinary_pages_are_at_least_55_percent_full", not underfilled, {"ordinary_pages": ordinary_fill, "exception": {4: extents.get(4)}, "underfilled": underfilled, "minimum": min(ordinary_fill.values())}),
        result(
            "page_4_is_intentional_dark_full_page_opening",
            page4_dark["passed"] and "Pregunta profesional" in page_texts[3] and extents.get(4, {}).get("fill", 1.0) < 0.55,
            {"background": page4_dark, "fill": extents.get(4)},
        ),
        result("rendered_pdf_contains_zero_arial", not any("arial" in font.casefold() for font in rendered_fonts) and not qa.get("forbidden_fonts"), {"fonts": rendered_fonts, "qa_forbidden": qa.get("forbidden_fonts")}),
        result("page_1_cover_reaches_all_edges", cover_bleed["passed"], cover_bleed),
        result(
            "cover_title_and_pull_quote_keep_a_safe_gutter",
            cover_title_quote_gutter >= 12.0,
            {
                "title_end_x_pt": round(cover_title_end, 3),
                "quote_start_x_pt": round(cover_quote_start, 3),
                "gutter_pt": round(cover_title_quote_gutter, 3),
                "minimum_pt": 12.0,
            },
        ),
        result(
            "page_1_cover_is_native_bw_without_css_conversion_or_heavy_global_scrim",
            tone.get("passed", False)
            and cover_contract.get("photographic_origin") == "native_black_and_white"
            and cover_contract.get("render_treatment") == "no_grayscale_conversion"
            and no_css_grayscale
            and localized_light_shade
            and cover_hashes_ok,
            {"tone": tone, "contract": cover_contract, "cover_rule": cover_rule, "shade_rule": shade_rule, "shade_alphas": shade_alphas, "hashes_ok": cover_hashes_ok},
        ),
        result(
            "cover_eyebrow_is_two_accessible_text_runs",
            re.search(r'<div class="cover-meta cover-meta-left cover-meta-eyebrow"><span>LECTURA PREVIA</span><span>EDICIÓN 2026</span></div>', html) is not None
            and "LECTURA PREVIA" in page_texts[0]
            and "EDICIÓN 2026" in page_texts[0]
            and not re.search(r"L\s+E\s+C\s+T\s+U\s+R\s+A", page_texts[0]),
            page_texts[0][:300],
        ),
        result(
            "four_editorial_photos_and_two_pause_photos_are_unique_and_provenanced",
            generated["passed"]
            and manifest.get("internal_images") == EXPECTED_INTERNAL_IMAGES
            and manifest.get("sparse_fill_images") == []
            and image_usage_pages_ok,
            {"audit": generated, "internal_images": manifest.get("internal_images"), "image_pages": image_pages},
        ),
        result(
            "contents_photo_is_unique_and_not_reused_in_body",
            html.count('src="assets/editorial-04.png"') == 1
            and re.search(r'<section class="front-page contents-page">.*?src="assets/editorial-04.png"', html, re.S) is not None
            and all(f'assets/editorial-0{number}.png' not in html.split('<article class="reading">', 1)[0] for number in range(1, 4)),
            {"contents_reference_count": html.count('src="assets/editorial-04.png"')},
        ),
        result(
            "pages_5_and_13_are_the_only_full_bleed_pauses",
            pause_html_count == 2
            and all(info["passed"] for info in pause_bleed.values())
            and all(compact(quote) in compact(page_texts[page - 1]) for page, quote in EXPECTED_QUOTES.items())
            and all(expected in alts_by_page.get(page, []) for page, expected in EXPECTED_PAUSE_ALTS.items()),
            {"html_count": pause_html_count, "pages": pause_bleed},
        ),
        result(
            "reference_grade_infographic_is_anchored_to_movement_3",
            diagram_ok and EXPECTED_INFOGRAPHIC_ALT in alts_by_page.get(18, []),
            {"source_sha256": sha256(diagram_source), "copy_sha256": sha256(diagram_copy), "in_section_07": diagram_in_section7, "manifest": diagram_contract},
        ),
        result(
            "infographic_labels_are_readable_at_final_a4_size",
            diagram_min_font_px >= 29.0 and diagram_min_font_pt >= 7.0,
            {
                "minimum_svg_font_px": diagram_min_font_px,
                "final_width_mm": diagram_final_width_mm,
                "minimum_equivalent_pt": round(diagram_min_font_pt, 2),
            },
        ),
        result(
            "page_30_is_image_free_two_column_references",
            "Referencias base" in page_texts[29]
            and reference_images == 0
            and columns["passed"]
            and all(position >= 0 for position in reference_positions)
            and reference_positions == sorted(reference_positions),
            {"columns": columns, "images": reference_images, "order_positions": reference_positions},
        ),
        result(
            "five_exact_urls_are_printed_and_annotated_only_on_page_30",
            source_urls == EXPECTED_URLS
            and external_links == EXPECTED_URLS
            and external_pages == {30: sorted(EXPECTED_URLS)}
            and all(printed_urls.values()),
            {"source": sorted(source_urls), "annotations": sorted(external_links), "pages": external_pages, "printed": printed_urls},
        ),
        result(
            "page_31_is_full_bleed_structured_matches_closing",
            closing_bleed["passed"]
            and EXPECTED_CLOSING_CAPTION in page_texts[30]
            and re.search(r"\b31\b", page_texts[30]) is not None
            and "linkedin.com/in/carralbal" in page_texts[30]
            and EXPECTED_CLOSING_ALT in alts_by_page.get(31, [])
            and EXPECTED_CLOSING_ALT in page_image_alts(reader, 31)
            and manifest.get("closing", {}).get("policy") == "canonical_structured_closing_without_quote"
            and qa.get("closing_quote_absent") is True,
            {"bleed": closing_bleed, "text": page_texts[30], "xobject_alts": page_image_alts(reader, 31)},
        ),
        result("six_unique_referents_have_complete_rights_and_provenance", portraits["passed"], portraits),
        result(
            "tagging_language_and_alt_structure_are_complete",
            bool(root_object.get("/StructTreeRoot"))
            and bool(mark_info.get("/Marked"))
            and root_object.get("/Lang") == "es-AR"
            and '<html lang="es-AR">' in html
            and structure_alts_ok
            and html_semantic_images_ok,
            {"lang": root_object.get("/Lang"), "marked": bool(mark_info.get("/Marked")), "figures": figures, "required_alts": required_structure_alts, "role_img_labels": inventory.role_img_labels},
        ),
        result(
            "all_pages_have_folio_and_linkedin_footer",
            linkedin_per_page == [1] * EXPECTED_PAGES
            and all(re.search(rf"\b{number:02d}\b", text) for number, text in enumerate(page_texts, 1)),
            {"linkedin_annotations_per_page": linkedin_per_page},
        ),
        result(
            "n06_final_pdf_regression_sha_is_unchanged",
            sha256(n06_pdf) == EXPECTED_N06_PDF_SHA,
            {"actual": sha256(n06_pdf), "expected": EXPECTED_N06_PDF_SHA},
        ),
    ]

    passed = all(item["status"] == "PASS" for item in checks)
    failed_checks = [item["check"] for item in checks if item["status"] == "FAIL"]
    report = {
        "document": "N07",
        "version": "v9-final",
        "validator": Path(__file__).name,
        "mode": "read-only",
        "status": "PASS" if passed else "FAIL",
        "failed_checks": failed_checks,
        "source_sha256": sha256(source),
        "pdf_sha256": sha256(pdf),
        "pdf_bytes": pdf.stat().st_size,
        "pages": len(reader.pages),
        "minimum_ordinary_page_fill": min(ordinary_fill.values()),
        "checks": checks,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(
            json.dumps(
                {
                    "document": "N07",
                    "version": "v9-final",
                    "status": "ERROR",
                    "error": f"{type(error).__name__}: {error}",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        sys.exit(2)
