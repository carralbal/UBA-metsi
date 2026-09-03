#!/usr/bin/env python3
"""Deterministic, read-only release validator for METSI N06 v9.

The validator is intentionally self-contained.  It reads the N06 package and
prints one JSON report to stdout; it never rewrites the PDF, manifests, assets,
or QA reports.  A clean package exits 0, a failed gate exits 1, and an execution
error exits 2.
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
DEFAULT_ROOT = HERE / "N06-v9-final"
EXPECTED_SOURCE_SHA = "837172826ad62ec7d7b841208202f91adbadf73d5286387fdf304c636b10e9fd"
EXPECTED_BLOCKS = 348
EXPECTED_PAGES = 28
EXPECTED_A4 = (594.96, 841.92)
EXPECTED_SECTIONS = [
    "Pregunta profesional",
    "La médica que pidió un estudio menos",
    "Tesis",
    "De N05 a N06: de los actores a una estrategia de aprendizaje",
    "Movimiento 1 · Formular incertidumbres que puedan cambiar una decisión",
    "Movimiento 2 · Diseñar una cartera mínima de evidencia",
    "Movimiento 3 · Decidir con evidencia suficiente y riesgo residual",
    "Caso de transferencia: alertas de abandono universitario",
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
    + ["DISTINCIONES"]
    + ["DECISIONES", "PRUEBA", "TRANSFERENCIA"]
    + ["PREPARACIÓN"] * 7
)
EXPECTED_REFERENTS = [
    ("James G. March", "assets/referent-james-march.jpg"),
    ("Michael Quinn Patton", "assets/referent-michael-quinn-patton.jpg"),
    ("Eric Ries", "assets/referent-eric-ries.jpg"),
    ("Donald A. Schön", "assets/referent-donald-schon.jpg"),
    ("Elham Tabassi", "assets/referent-elham-tabassi.jpg"),
    ("Daniel Kahneman", "assets/referent-daniel-kahneman.jpg"),
]
EXPECTED_URLS = {
    "https://dora.dev/research/2025/dora-report/",
    "https://www.iso.org/standard/77520.html",
    "https://doi.org/10.1287/orsc.2.1.71",
    "https://doi.org/10.6028/NIST.AI.100-1",
    "https://doi.org/10.1126/science.185.4157.1124",
}
EXPECTED_COVER_ALT = (
    "Profesional argentina observa un muro de evidencias y caminos alternativos "
    "en un estudio de Buenos Aires, en una fotografía editorial concebida en "
    "blanco y negro con una escala amplia de grises"
)
EXPECTED_CONTENTS_ALT = "Imagen editorial asociada al contenido de N06"
EXPECTED_DIAGRAM_ALT = "Cinco ideas para recordar"
EXPECTED_CLOSING_ALT = (
    "Diez fósforos dispuestos en secuencia vertical, desde intactos hasta "
    "consumidos y convertidos en ceniza."
)
EXPECTED_CLOSING_CAPTION = (
    "La secuencia vuelve visible que toda intervención consume recursos, deja "
    "huellas y necesita un criterio de cierre."
)
EXPECTED_QUOTES = {
    5: "Investigar no es reunir más respuestas: es comprar la diferencia que una decisión necesita.",
    13: "Cada compromiso compra aprendizaje y, al mismo tiempo, consume opciones.",
}
EXPECTED_METADATA = {
    "/Title": "N06 · Discovery como estrategia de reducción de incertidumbre",
    "/Author": "Diego Carralbal",
    "/Subject": "Metodología de Sistemas de Información · FCE · UBA",
}
EXPECTED_COUNTS = {"pills": 5, "glossary": 9, "questions": 6, "references": 10}
REQUIRED_PACKAGE_FILES = [
    "index.html",
    "magazine.css",
    "metsi.css",
    "manifest.json",
    "document.json",
    "image-manifest.json",
    "source-manifest.json",
    "integrity-report.json",
    "qa-report.json",
    "PUBLICATION-READINESS.md",
    "HANDOFF.md",
    "CHANGELOG.md",
    "page-spread-plan.json",
    "source/N06_discovery_como_reduccion_de_incertidumbre-content-final.md",
    "output/N06-METSI-lectura-previa-v9.pdf",
    "output/N06-METSI-lectura-previa-v9-final.pdf",
    "provenance/regression-lock.json",
    "provenance/cover-image-premium-bw-v1.md",
    "provenance/editorial-image-provenance.md",
    "provenance/referent-portrait-sources.md",
]
PRIVATE_PATH_RE = re.compile(
    r"(?:file://|/(?:Users|home|private|tmp|var/folders)/|[A-Za-z]:\\\\)", re.I
)
DIRECT_ADDRESS_RE = re.compile(
    r"\b(?:dibujá|identificá|explicá|transferí|mirá|pensá|escribí|compará|"
    r"analizá|reconstruí|elegí|tenés|podés|querés|usted)\b",
    re.I,
)
CLEAR_RIGHTS_STATUSES = {
    "original_course_asset",
    "canonical_course_asset",
    "generated_for_metsi",
    "licensed",
    "public_domain",
    "permission_confirmed_by_course_author",
    "unsplash_license",
    "pexels_license",
    "pixabay_license",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(value: str) -> str:
    value = value.replace("ﬁ", "fi").replace("ﬂ", "fl")
    return re.sub(r"[^0-9a-záéíóúüñ]+", "", value.casefold())


def strip_markup(value: str) -> str:
    value = html_lib.unescape(re.sub(r"<[^>]+>", " ", value))
    return re.sub(r"[*_`]", "", value)


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "status": "PASS" if passed else "FAIL", "detail": detail}


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


class HtmlInventory(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.images: list[dict[str, str]] = []
        self.local_refs: list[str] = []
        self.contributors: list[dict[str, str]] = []
        self._contributor: dict[str, str] | None = None
        self._in_contributor_h3 = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
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
        for annotation in page.get("/Annots", []):
            item = annotation.get_object()
            action = item.get("/A")
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
    """Read explicit /Alt values attached to image XObjects on one page."""
    page = reader.pages[page_number - 1]
    resources = page.get("/Resources")
    if not resources:
        return []
    resources = resources.get_object()
    xobjects = resources.get("/XObject")
    if not xobjects:
        return []
    values: list[str] = []
    for reference in xobjects.get_object().values():
        item = reference.get_object()
        if item.get("/Subtype") == "/Image" and item.get("/Alt"):
            values.append(str(item.get("/Alt")))
    return values


def cover_pattern_coverage(page) -> dict[str, Any]:
    resources = page.get("/Resources")
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)
    records: list[dict[str, float]] = []
    if resources:
        patterns = resources.get_object().get("/Pattern")
        if patterns:
            for reference in patterns.get_object().values():
                pattern = reference.get_object()
                bbox = pattern.get("/BBox")
                matrix = pattern.get("/Matrix")
                if not bbox or len(bbox) != 4 or not matrix or len(matrix) != 6:
                    continue
                covered_width = abs(float(matrix[0])) * (float(bbox[2]) - float(bbox[0]))
                covered_height = abs(float(matrix[3])) * (float(bbox[3]) - float(bbox[1]))
                records.append(
                    {
                        "covered_width": round(covered_width, 3),
                        "covered_height": round(covered_height, 3),
                        "required_width": round(width, 3),
                        "required_height": round(height, 3),
                    }
                )
    passed = bool(records) and all(
        item["covered_width"] >= width - 1.0 and item["covered_height"] >= height - 1.0
        for item in records
    )
    return {"passed": passed, "patterns": records, "tolerance_pt": 1.0}


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


def heading_alignment(html: str, page_texts: list[str]) -> dict[str, dict[str, Any]]:
    compact_pages = [compact(text) for text in page_texts]
    aligned: dict[str, dict[str, Any]] = {}
    for level, heading_html in re.findall(r"<(h[234])[^>]*>(.*?)</\1>", html, re.S):
        heading = strip_markup(heading_html).strip()
        if not heading or heading in aligned:
            continue
        position = html.find(heading_html)
        tail = html[position + len(heading_html) :]
        body_match = re.search(r"<(?:p|li)[^>]*>(.*?)</(?:p|li)>", tail, re.S)
        if not body_match:
            continue
        body_words = re.findall(
            r"[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", strip_markup(body_match.group(1))
        )[:7]
        heading_pages = {
            index + 1
            for index, text in enumerate(compact_pages)
            if compact(heading) in text
        }
        body_pages = {
            index + 1
            for index, text in enumerate(compact_pages)
            if compact(" ".join(body_words)) in text
        }
        shared = sorted(heading_pages & body_pages)
        aligned[heading] = {"level": level, "same_page": bool(shared), "pages": shared}
    return aligned


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
    candidates: list[dict[str, Any]] = []
    for rect in page.rects:
        gaps = edge_gaps(page, rect)
        luminance = color_luminance(rect.get("non_stroking_color"))
        if all(value <= tolerance for value in gaps.values()) and luminance is not None:
            candidates.append(
                {
                    "gaps_pt": gaps,
                    "luminance": round(luminance, 4),
                    "color": rect.get("non_stroking_color"),
                }
            )
    dark = [item for item in candidates if item["luminance"] <= maximum_luminance]
    return {
        "passed": bool(dark),
        "tolerance_pt": tolerance,
        "maximum_luminance": maximum_luminance,
        "full_page_rectangles": candidates,
    }


def page2_note_footer_clearance(page: pdfplumber.page.Page) -> dict[str, Any]:
    text_lines = page.extract_text_lines()
    note_lines = [
        line
        for line in text_lines
        if "Nota." in str(line.get("text", "")) and "SIN NUM." in str(line.get("text", ""))
    ]
    rules = [
        line
        for line in page.lines
        if float(line.get("top", 0)) > 740 and float(line.get("width", 0)) > page.width * 0.60
    ]
    footer_lines = [
        line for line in text_lines if "linkedin.com/in/carralbal" in str(line.get("text", ""))
    ]
    if not note_lines or not rules or not footer_lines:
        return {
            "passed": False,
            "reason": "note, footer rule, or footer text not found",
            "note_lines": len(note_lines),
            "rules": len(rules),
            "footer_lines": len(footer_lines),
        }
    note_bottom = max(float(line["bottom"]) for line in note_lines)
    rule_top = min(float(line["top"]) for line in rules)
    footer_top = min(float(line["top"]) for line in footer_lines)
    clearance = min(rule_top, footer_top) - note_bottom
    minimum = 6.0
    return {
        "passed": clearance >= minimum,
        "clearance_pt": round(clearance, 3),
        "minimum_pt": minimum,
        "note_bottom": round(note_bottom, 3),
        "rule_top": round(rule_top, 3),
        "footer_top": round(footer_top, 3),
        "note": note_lines[0].get("text"),
    }


def cover_tone(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"passed": False, "reason": "cover source missing"}
    with Image.open(path) as image:
        sample = image.convert("RGB")
        sample.thumbnail((512, 512))
        get_flattened = getattr(sample, "get_flattened_data", None)
        pixels = list(get_flattened() if get_flattened else sample.getdata())
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
        "sample_pixels": len(pixels),
        "channel_spread_p95": round(p95_spread, 2),
        "luminance_p05": round(p05, 2),
        "luminance_p95": round(p95, 2),
        "luminance_stddev": round(tonal_std, 2),
    }


def package_private_paths(root: Path) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".json", ".md", ".html", ".css"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_number, line in enumerate(text.splitlines(), 1):
            if PRIVATE_PATH_RE.search(line):
                issues.append(
                    {
                        "file": str(path.relative_to(root)),
                        "line": line_number,
                        "excerpt": line.strip()[:240],
                    }
                )
    return issues


def local_reference_issues(root: Path, inventory: HtmlInventory, css: str) -> list[dict[str, str]]:
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


def json_absolute_paths(value: Any, location: str = "$") -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            issues.extend(json_absolute_paths(child, f"{location}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            issues.extend(json_absolute_paths(child, f"{location}[{index}]"))
    elif isinstance(value, str) and PRIVATE_PATH_RE.search(value):
        issues.append({"location": location, "value": value})
    return issues


def rights_manifest_audit(root: Path, required_images: set[str]) -> dict[str, Any]:
    path = root / "image-manifest.json"
    if not path.exists():
        return {
            "passed": False,
            "reason": "image-manifest.json missing",
            "required_images": sorted(required_images),
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"passed": False, "reason": f"invalid image manifest: {exc}"}
    records = data.get("assets", [])
    by_file = {record.get("file"): record for record in records if isinstance(record, dict)}
    missing: list[str] = []
    invalid: list[dict[str, Any]] = []
    for file_name in sorted(required_images):
        record = by_file.get(file_name)
        if not record:
            missing.append(file_name)
            continue
        asset = root / file_name
        status = str(record.get("rights_status", ""))
        allowed = (
            status in CLEAR_RIGHTS_STATUSES
            or status.startswith("wikimedia_commons_cc_")
            or status.startswith("wikimedia_commons_")
            or status.startswith("cc_")
            or status.startswith("licensed_")
            or status.startswith("public_domain_")
        )
        reasons: list[str] = []
        if not asset.exists():
            reasons.append("asset missing")
        if not allowed:
            reasons.append(f"rights_status is not publication-grade: {status!r}")
        if record.get("sha256") and asset.exists() and record["sha256"] != sha256(asset):
            reasons.append("sha256 mismatch")
        if status in {"licensed", "unsplash_license", "pexels_license", "pixabay_license"} or status.startswith(("wikimedia_commons_", "cc_", "licensed_", "public_domain_")):
            if not record.get("source_page"):
                reasons.append("licensed asset lacks source_page")
            if not record.get("license_url"):
                reasons.append("licensed asset lacks license_url")
        if status == "permission_confirmed_by_course_author":
            if not record.get("source_page") or not record.get("rights_basis"):
                reasons.append("permission record lacks source_page or rights_basis")
        if status in {"original_course_asset", "canonical_course_asset", "generated_for_metsi"}:
            if not record.get("sha256"):
                reasons.append("course asset lacks sha256")
        if reasons:
            invalid.append({"file": file_name, "reasons": reasons})
    return {
        "passed": not missing and not invalid and bool(data.get("policy")),
        "records": len(records),
        "required": len(required_images),
        "missing": missing,
        "invalid": invalid,
        "policy_present": bool(data.get("policy")),
    }


def portrait_audit(
    root: Path,
    inventory: HtmlInventory,
    manifest: dict[str, Any],
    pdf_page_3_text: str,
) -> dict[str, Any]:
    actual = [
        (item.get("name", "").strip(), item.get("src", ""))
        for item in inventory.contributors
    ]
    assets: list[dict[str, Any]] = []
    for _, relative in actual:
        path = root / relative
        if not path.exists():
            assets.append({"file": relative, "exists": False})
            continue
        with Image.open(path) as image:
            size = list(image.size)
        assets.append(
            {"file": relative, "exists": True, "size": size, "sha256": sha256(path)}
        )
    manifest_portraits = manifest.get("portrait_references", [])
    manifest_pairs = [
        (str(item.get("name", "")), "assets/" + str(item.get("file", "")).removeprefix("assets/"))
        for item in manifest_portraits
        if isinstance(item, dict)
    ]
    weak_statuses = {
        "official_community_profile",
        "official_author_profile",
        "documentary_institution_photo",
        "existing_course_asset",
        "interview_profile",
        "wikimedia_commons",
    }
    weak = [
        {"name": item.get("name"), "rights_status": item.get("rights_status")}
        for item in manifest_portraits
        if item.get("rights_status") in weak_statuses
    ]
    hashes = [item.get("sha256") for item in assets if item.get("exists")]
    sizes = [tuple(item.get("size", [])) for item in assets if item.get("exists")]
    pdf_names = {
        name: compact(name) in compact(pdf_page_3_text) for name, _ in EXPECTED_REFERENTS
    }
    passed = (
        actual == EXPECTED_REFERENTS
        and manifest_pairs == EXPECTED_REFERENTS
        and len(assets) == 6
        and all(item.get("exists") for item in assets)
        and len(set(hashes)) == 6
        and len(set(sizes)) == 1
        and not weak
        and all(pdf_names.values())
    )
    return {
        "passed": passed,
        "actual": actual,
        "expected": EXPECTED_REFERENTS,
        "manifest": manifest_pairs,
        "assets": assets,
        "weak_rights_records": weak,
        "names_in_pdf_page_3": pdf_names,
    }


def reference_columns(page: pdfplumber.page.Page) -> dict[str, Any]:
    expected_left = {"DORA.", "Hubbard,", "International", "March,"}
    expected_right = {"Patton,", "Ries,", "Schön,", "Tabassi,", "Torres,", "Tversky,"}
    left: dict[str, float] = {}
    right: dict[str, float] = {}
    for word in page.extract_words(use_text_flow=False):
        token = str(word.get("text", ""))
        x0 = float(word.get("x0", 0))
        if token in expected_left and token not in left:
            left[token] = round(x0, 2)
        if token in expected_right and token not in right:
            right[token] = round(x0, 2)
    passed = (
        set(left) == expected_left
        and set(right) == expected_right
        and all(value < page.width * 0.45 for value in left.values())
        and all(value > page.width * 0.45 for value in right.values())
    )
    return {"passed": passed, "left": left, "right": right}


def tall_accent_bars(page: pdfplumber.page.Page) -> list[dict[str, Any]]:
    bars: list[dict[str, Any]] = []
    for rect in page.rects:
        width = float(rect.get("width", 0))
        height = float(rect.get("height", 0))
        luminance = color_luminance(rect.get("non_stroking_color"))
        color = rect.get("non_stroking_color")
        is_volt = (
            isinstance(color, (tuple, list))
            and len(color) >= 3
            and float(color[0]) >= 0.70
            and float(color[1]) >= 0.80
            and float(color[2]) <= 0.25
        )
        if width <= 18 and height >= 150 and (is_volt or (luminance is not None and luminance <= 0.25)):
            bars.append(
                {
                    "x0": round(float(rect.get("x0", 0)), 2),
                    "top": round(float(rect.get("top", 0)), 2),
                    "width": round(width, 2),
                    "height": round(height, 2),
                    "color": color,
                }
            )
    return bars


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="N06-v9-final package directory (default: sibling N06-v9-final)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    source = root / "source/N06_discovery_como_reduccion_de_incertidumbre-content-final.md"
    canonical = HERE / "N06-content-final/source/N06_discovery_como_reduccion_de_incertidumbre-content-final.md"
    pdf = root / "output/N06-METSI-lectura-previa-v9-final.pdf"
    raw_pdf = root / "output/N06-METSI-lectura-previa-v9.pdf"
    html_path = root / "index.html"
    css_path = root / "magazine.css"
    manifest_path = root / "manifest.json"
    source_manifest_path = root / "source-manifest.json"
    integrity_path = root / "integrity-report.json"
    qa_path = root / "qa-report.json"
    content_integrity_path = HERE / "N06-content-final/provenance/integrity-report.json"

    essential = [
        source,
        canonical,
        pdf,
        raw_pdf,
        html_path,
        css_path,
        manifest_path,
        source_manifest_path,
        integrity_path,
        qa_path,
        content_integrity_path,
    ]
    missing_essential = [str(path) for path in essential if not path.exists()]
    if missing_essential:
        print(
            json.dumps(
                {"document": "N06", "version": "v9-final", "status": "ERROR", "missing": missing_essential},
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
    content_integrity = json.loads(content_integrity_path.read_text(encoding="utf-8"))
    reader = PdfReader(str(pdf))
    page_texts = [page.extract_text() or "" for page in reader.pages]
    pdf_text = "\n".join(page_texts)
    compact_pdf = compact(pdf_text)
    body, references = source_text.split("## Referencias base", 1)
    headings = re.findall(r"^## (.+)$", source_text, flags=re.M)
    inventory = HtmlInventory()
    inventory.feed(html)
    link_pages = links_by_page(reader)
    all_links = {uri for links in link_pages for uri in links}
    external_links = {uri for uri in all_links if "linkedin.com/in/carralbal" not in uri}
    source_urls = {value.rstrip(".,") for value in re.findall(r"https://\S+", references)}
    figures = structure_figures(reader)
    cover_scrim = cover_pattern_coverage(reader.pages[0])

    with pdfplumber.open(pdf) as document:
        extents = page_extents(document)
        cover_bleed = full_bleed_image(document.pages[0])
        page2_clearance = page2_note_footer_clearance(document.pages[1])
        page4_dark = dark_full_page_background(document.pages[3])
        pause_bleed = {page: full_bleed_image(document.pages[page - 1]) for page in EXPECTED_QUOTES}
        closing_bleed = full_bleed_image(document.pages[27])
        columns = reference_columns(document.pages[26])
        reference_bars = tall_accent_bars(document.pages[26])
        page27_images = len(document.pages[26].images)

    all_source_ids = [entry["source_id"] for entry in source_manifest.get("eligible_blocks", [])]
    html_source_ids = re.findall(r'data-source-id="([^"]+)"', html)
    missing_rendered_blocks = [
        entry["source_id"]
        for entry in source_manifest.get("eligible_blocks", [])
        if compact(str(entry.get("text", ""))) not in compact_pdf
    ]

    route_tokens = ("PROBLEMA", "DISTINCIONES", "DECISIONES", "PRUEBA", "TRANSFERENCIA", "PREPARACIÓN")
    pdf_section_headers: list[tuple[int, int, str]] = []
    for section_number, (heading, expected_route) in enumerate(zip(EXPECTED_SECTIONS, EXPECTED_ROUTES), 1):
        matching_pages = [
            page_number
            for page_number, text in enumerate(page_texts[3:], 4)
            if re.search(rf"(?m)^{section_number:02d}\s+METSI\s*·\s*N06\s*$", text)
            and compact(heading) in compact(text)
        ]
        if not matching_pages:
            continue
        page_number = matching_pages[0]
        page_compact = compact(page_texts[page_number - 1])
        route = expected_route if compact(expected_route) in page_compact else ""
        if not route:
            route = next((token for token in route_tokens if compact(token) in page_compact), "")
        pdf_section_headers.append((section_number, page_number, route))
    section_pages = {
        EXPECTED_SECTIONS[number - 1]: page
        for number, page, _ in pdf_section_headers
        if 1 <= number <= len(EXPECTED_SECTIONS)
    }
    ordered_section_pages = [section_pages.get(heading) for heading in EXPECTED_SECTIONS]
    pdf_route_labels = [route for _, _, route in pdf_section_headers]

    html_route_labels: list[str] = []
    for number in range(1, 16):
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
        html_route_labels.append(route_match.group(1) if route_match else "")

    contents_text = compact(page_texts[1])
    contents_positions = [contents_text.find(compact(heading)) for heading in EXPECTED_SECTIONS]
    reading_html = html.split('<article class="reading">', 1)[-1]
    alignment = heading_alignment(reading_html, page_texts)
    orphan_headings = {key: value for key, value in alignment.items() if not value["same_page"]}
    isolated_initials = [
        {"page": page_number, "value": line.strip()}
        for page_number, text in enumerate(page_texts, 1)
        for line in text.splitlines()
        if re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", line.strip())
    ]
    ordinary_pages = [page for page in range(6, 27) if page != 13]
    underfilled = {
        page: extents.get(page, {}).get("fill", 0.0)
        for page in ordinary_pages
        if extents.get(page, {}).get("fill", 0.0) < 0.50
    }

    pills_block = source_text.split("## Cinco píldoras para recordar", 1)[1].split("## Glosario esencial", 1)[0]
    glossary_block = source_text.split("## Glosario esencial", 1)[1].split("## Preguntas de preparación", 1)[0]
    questions_block = source_text.split("## Preguntas de preparación", 1)[1].split("## Referencias base", 1)[0]
    counts = {
        "pills": len(re.findall(r"^\d+\. \*\*", pills_block, re.M)),
        "glossary": len(re.findall(r"^- \*\*", glossary_block, re.M)),
        "questions": len(re.findall(r"^\d+\. ", questions_block, re.M)),
        "references": len(re.findall(r"^- ", references, re.M)),
    }
    anchor_patterns = {
        "DORA (2025)": r"\bDORA \(2025\)",
        "Hubbard (2014)": r"\bHubbard \(2014\)",
        "ISO 9241-210:2019": r"\bISO 9241-210:2019\b",
        "March (1991)": r"\bMarch \(1991\)",
        "Patton (2015)": r"\bPatton \(2015\)",
        "Ries (2011)": r"\bRies \(2011\)",
        "Schön (1983)": r"\bSchön \(1983\)",
        "Tabassi (2023)": r"\bTabassi, 2023\b",
        "Torres (2021)": r"\bTorres \(2021\)",
        "Tversky y Kahneman (1974)": r"\bTversky y Kahneman \(1974\)",
    }
    anchors = {key: bool(re.search(pattern, body)) for key, pattern in anchor_patterns.items()}

    required_image_paths = {item.get("src", "") for item in inventory.images if item.get("src")}
    required_image_paths.add("assets/cover-source-premium-bw-v1.png")
    rights = rights_manifest_audit(root, required_image_paths)
    portraits = portrait_audit(root, inventory, manifest, page_texts[2])
    private_paths = package_private_paths(root)
    manifest_absolute = json_absolute_paths(manifest)
    source_manifest_absolute = json_absolute_paths(source_manifest)
    local_reference_errors = local_reference_issues(root, inventory, css)
    symlinks = [str(path.relative_to(root)) for path in root.rglob("*") if path.is_symlink()]

    cover_source = root / "assets/cover-source-premium-bw-v1.png"
    tone = cover_tone(cover_source)
    cover_rule_match = re.search(r"\.cover-n06>img\{([^}]*)\}", css)
    cover_rule = cover_rule_match.group(1) if cover_rule_match else ""
    cover_contract = manifest.get("cover", {})
    no_css_color_conversion = "grayscale(" not in cover_rule and "saturate(0" not in cover_rule
    cover_sha_matches = (
        cover_source.exists()
        and cover_contract.get("sha256") == sha256(cover_source)
        and (root / "assets/cover.png").exists()
        and sha256(root / "assets/cover.png") == sha256(cover_source)
    )

    media_sizes: list[dict[str, float]] = []
    a4_ok = len(reader.pages) == EXPECTED_PAGES
    for number, page in enumerate(reader.pages, 1):
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        media_sizes.append({"page": number, "width": round(width, 3), "height": round(height, 3)})
        if abs(width - EXPECTED_A4[0]) > 0.75 or abs(height - EXPECTED_A4[1]) > 0.75:
            a4_ok = False

    root_object = reader.trailer["/Root"]
    mark_info = root_object.get("/MarkInfo") or {}
    alts_by_page: dict[int | None, list[str | None]] = {}
    for figure in figures:
        alts_by_page.setdefault(figure["page"], []).append(figure["alt"])
    all_html_alts = [item.get("alt", "").strip() for item in inventory.images]
    required_alt_pass = (
        EXPECTED_COVER_ALT in page_image_alts(reader, 1)
        and EXPECTED_CONTENTS_ALT in alts_by_page.get(2, [])
        and EXPECTED_CONTENTS_ALT in page_image_alts(reader, 2)
        and EXPECTED_DIAGRAM_ALT in alts_by_page.get(25, [])
        and EXPECTED_CLOSING_ALT in alts_by_page.get(28, [])
        and all(figure["alt"] for figure in figures)
        and all(all_html_alts)
    )

    reference_page_compact_no_space = re.sub(r"\s+", "", page_texts[26])
    printed_urls = {url: url in reference_page_compact_no_space for url in EXPECTED_URLS}
    reference_order_tokens = ["DORA.", "Hubbard, D. W.", "International Organization", "March, J. G.", "Patton, M. Q.", "Ries, E.", "Schön, D. A.", "Tabassi, E.", "Torres, T.", "Tversky, A."]
    reference_order_positions = [page_texts[26].find(token) for token in reference_order_tokens]

    page_linkedin = [
        sum(1 for uri in links if "linkedin.com/in/carralbal" in uri) for links in link_pages
    ]
    external_pages = {
        number: sorted({uri for uri in links if "linkedin.com/in/carralbal" not in uri})
        for number, links in enumerate(link_pages, 1)
        if any("linkedin.com/in/carralbal" not in uri for uri in links)
    }

    package_missing = [name for name in REQUIRED_PACKAGE_FILES if not (root / name).exists()]
    aliases_ok = (
        (root / "metsi.css").exists()
        and (root / "document.json").exists()
        and (root / "metsi.css").read_bytes() == css_path.read_bytes()
        and json.loads((root / "document.json").read_text(encoding="utf-8")) == manifest
    )

    metadata = reader.metadata or {}
    metadata_values = {key: str(metadata.get(key, "")) for key in EXPECTED_METADATA}
    metadata_ok = all(metadata_values[key] == value for key, value in EXPECTED_METADATA.items())
    keywords = str(metadata.get("/Keywords", ""))
    metadata_ok = metadata_ok and all(token in keywords for token in ("METSI", "UBA", "Investigación"))

    checks = [
        check(
            "package_contract_files_present",
            not package_missing,
            {"missing": package_missing, "required": len(REQUIRED_PACKAGE_FILES)},
        ),
        check("package_aliases_match_authoring_files", aliases_ok, "metsi.css == magazine.css and document.json == manifest.json"),
        check("package_has_no_symlinks", not symlinks, symlinks),
        check("package_has_no_private_absolute_paths", not private_paths, private_paths),
        check("manifest_paths_are_relative", not manifest_absolute and not source_manifest_absolute, {"manifest": manifest_absolute, "source_manifest": source_manifest_absolute}),
        check("html_and_css_local_references_resolve_inside_package", not local_reference_errors, local_reference_errors),
        check("rendered_image_rights_are_complete", rights.get("passed", False), rights),
        check(
            "canonical_source_sha_and_byte_identity",
            source.read_bytes() == canonical.read_bytes() and sha256(source) == EXPECTED_SOURCE_SHA,
            {"actual": sha256(source), "expected": EXPECTED_SOURCE_SHA, "byte_identical": source.read_bytes() == canonical.read_bytes()},
        ),
        check(
            "source_manifest_has_348_blocks_exactly_once",
            len(all_source_ids) == EXPECTED_BLOCKS
            and Counter(all_source_ids) == Counter(html_source_ids)
            and len(set(html_source_ids)) == EXPECTED_BLOCKS
            and integrity.get("status") == "PASS",
            {"manifest": len(all_source_ids), "html": len(html_source_ids), "unique_html": len(set(html_source_ids)), "integrity": integrity},
        ),
        check("all_348_source_blocks_are_in_pdf_text", not missing_rendered_blocks, {"missing": missing_rendered_blocks, "checked": len(all_source_ids)}),
        check(
            "content_audit_remains_closed",
            content_integrity.get("overall") == "pass"
            and content_integrity.get("sha256") == EXPECTED_SOURCE_SHA
            and content_integrity.get("word_counts", {}).get("total") == 8052
            and content_integrity.get("word_counts", {}).get("substantive_from_thesis_through_synthesis") == 7069,
            content_integrity.get("word_counts"),
        ),
        check("canonical_section_structure", headings == EXPECTED_SECTIONS + ["Referencias base"], headings),
        check("three_movements_and_handoffs", all(token in source_text for token in ("Movimiento 1 · Formular", "Movimiento 2 · Diseñar", "Movimiento 3 · Decidir", "De N05 a N06", "HH-06", "N07")), "N05 input, three movements, HH-06 conductor, N07 output"),
        check("content_counts_close", counts == EXPECTED_COUNTS, {"actual": counts, "expected": EXPECTED_COUNTS}),
        check("all_references_are_anchored", all(anchors.values()), anchors),
        check("impersonal_register", not DIRECT_ADDRESS_RE.search(body), sorted(set(DIRECT_ADDRESS_RE.findall(body)))),
        check("no_prose_dashes_or_placeholders", not re.search(r"[—–]", body) and not re.search(r"\b(?:TBD|lorem|XXX)\b|\[(?:TODO|TBD)[^]]*\]", source_text, re.I), "no dashes in body and no placeholders"),
        check("pdf_is_distinct_finalized_artifact", sha256(pdf) != sha256(raw_pdf), {"raw": sha256(raw_pdf), "final": sha256(pdf)}),
        check("pdf_has_28_a4_pages", a4_ok and qa.get("pages") == 28 and qa.get("a4_pages") == 28, {"pages": len(reader.pages), "sizes": media_sizes}),
        check("pdf_metadata_is_complete", metadata_ok, {"metadata": metadata_values, "keywords": keywords}),
        check("contents_is_complete_and_ordered", all(position >= 0 for position in contents_positions) and contents_positions == sorted(contents_positions) and page_texts[1].count("SIN NUM.") >= 2, {"positions": dict(zip(EXPECTED_SECTIONS, contents_positions)), "sin_num": page_texts[1].count("SIN NUM.")}),
        check(
            "section_order_is_monotonic_in_body",
            [number for number, _, _ in pdf_section_headers] == list(range(1, 16))
            and all(page is not None for page in ordered_section_pages)
            and ordered_section_pages == sorted(ordered_section_pages)
            and all(
                compact(EXPECTED_SECTIONS[number - 1]) in compact(page_texts[page - 1])
                for number, page, _ in pdf_section_headers
            ),
            {"headers": pdf_section_headers, "pages": section_pages},
        ),
        check(
            "route_is_monotonic_and_reproducible",
            pdf_route_labels == EXPECTED_ROUTES and html_route_labels == EXPECTED_ROUTES,
            {"pdf": pdf_route_labels, "html": html_route_labels, "expected": EXPECTED_ROUTES},
        ),
        check("page_1_cover_image_reaches_all_edges", cover_bleed["passed"], cover_bleed),
        check("page_1_cover_scrim_reaches_all_edges", cover_scrim["passed"], cover_scrim),
        check("page_1_cover_is_native_bw_with_broad_tones", tone.get("passed", False) and cover_contract.get("photographic_origin") == "native_black_and_white" and cover_contract.get("render_treatment") == "no_grayscale_conversion" and no_css_color_conversion and cover_sha_matches, {"tone": tone, "manifest": cover_contract, "css_rule": cover_rule, "sha_matches": cover_sha_matches}),
        check("page_1_eyebrow_and_cover_text_are_extractable", all(token in page_texts[0] for token in ("LECTURA PREVIA", "EDICIÓN 2026", "N06", "FCE · UBA", "Discovery como")) and not re.search(r"L\s+E\s+C\s+T\s+U\s+R\s+A", page_texts[0]), page_texts[0][:500]),
        check("page_2_note_clears_rule_and_footer", page2_clearance["passed"], page2_clearance),
        check("page_4_is_dark_full_page_opening", page4_dark["passed"] and "Pregunta profesional" in page_texts[3] and "04" in page_texts[3], {"background": page4_dark, "text": page_texts[3][:300]}),
        check("pages_5_and_13_are_exact_full_bleed_pauses", html.count('class="full-bleed full-bleed-quote"') == 2 and all(info["passed"] for info in pause_bleed.values()) and all(compact(quote) in compact(page_texts[page - 1]) for page, quote in EXPECTED_QUOTES.items()), {"html_count": html.count('class="full-bleed full-bleed-quote"'), "pages": pause_bleed}),
        check("page_27_is_minimalist_two_column_references", "Referencias base" in page_texts[26] and counts["references"] == 10 and columns["passed"] and page27_images == 0 and not reference_bars and all(position >= 0 for position in reference_order_positions) and reference_order_positions == sorted(reference_order_positions), {"columns": columns, "images": page27_images, "accent_bars": reference_bars, "order_positions": reference_order_positions}),
        check("page_28_is_full_bleed_structured_matches_closing", closing_bleed["passed"] and EXPECTED_CLOSING_CAPTION in page_texts[27] and "28" in page_texts[27] and "linkedin.com/in/carralbal" in page_texts[27] and "Investigar no es" not in page_texts[27] and (root / "assets/matches-close.png").exists(), {"bleed": closing_bleed, "text": page_texts[27][:500]}),
        check("six_exact_unique_referents", portraits["passed"] and ".contributor-portrait{display:block;width:25mm;height:25mm" in css, portraits),
        check("five_reference_urls_are_printed_complete_and_annotated", source_urls == EXPECTED_URLS and external_links == EXPECTED_URLS and all(printed_urls.values()) and external_pages == {27: sorted(EXPECTED_URLS)}, {"source": sorted(source_urls), "annotations": sorted(external_links), "printed": printed_urls, "external_pages": external_pages}),
        check("all_pages_have_folio_and_linkedin_footer", page_linkedin == [1] * 28 and all(re.search(rf"\b{number:02d}\b", text) for number, text in enumerate(page_texts, 1)), {"linkedin_annotations_per_page": page_linkedin}),
        check("tagging_language_and_required_alt_text", bool(root_object.get("/StructTreeRoot")) and bool(mark_info.get("/Marked")) and root_object.get("/Lang") == "es-AR" and required_alt_pass, {"lang": root_object.get("/Lang"), "marked": bool(mark_info.get("/Marked")), "figures": figures, "empty_html_alts": sum(1 for alt in all_html_alts if not alt)}),
        check("no_orphan_headings", len(alignment) >= 50 and not orphan_headings and not isolated_initials, {"headings_checked": len(alignment), "orphans": orphan_headings, "isolated_initials": isolated_initials}),
        check("ordinary_pages_are_at_least_half_full", not underfilled, {"ordinary_pages": {page: extents.get(page, {}).get("fill") for page in ordinary_pages}, "underfilled": underfilled, "minimum": min(extents.get(page, {}).get("fill", 0.0) for page in ordinary_pages)}),
        check("known_apparatus_pages_are_present", "Contenido" in page_texts[1] and "Referentes" in page_texts[2] and "Pregunta profesional" in page_texts[3] and "Referencias base" in page_texts[26], {"pages": {2: "Contenido", 3: "Referentes", 4: "Pregunta profesional", 27: "Referencias base"}}),
    ]

    passed = all(item["status"] == "PASS" for item in checks)
    failed_checks = [item["check"] for item in checks if item["status"] == "FAIL"]
    report = {
        "document": "N06",
        "version": "v9-final",
        "validator": Path(__file__).name,
        "mode": "read-only",
        "root": str(root),
        "status": "PASS" if passed else "FAIL",
        "failed_checks": failed_checks,
        "source_sha256": sha256(source),
        "pdf_sha256": sha256(pdf),
        "pdf_bytes": pdf.stat().st_size,
        "pages": len(reader.pages),
        "minimum_ordinary_page_fill": min(extents.get(page, {}).get("fill", 0.0) for page in ordinary_pages),
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
                    "document": "N06",
                    "version": "v9-final",
                    "status": "ERROR",
                    "error": f"{type(error).__name__}: {error}",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        sys.exit(2)
