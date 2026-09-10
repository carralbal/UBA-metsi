#!/usr/bin/env python3
"""Gate determinista, exhaustivo y de solo lectura para N11-N36 editorial.

Emite un objeto JSON por paquete (JSON Lines). No confia en informes QA previos,
no escribe dentro de los paquetes y devuelve 1 si al menos uno falla (2 ante un
error de ejecucion). Requiere Pillow, pdfplumber, pypdf, numpy y Poppler.
"""

from __future__ import annotations

import argparse
import hashlib
import html as html_lib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

import numpy as np
import pdfplumber
from PIL import Image
from pypdf import PdfReader


HERE = Path(__file__).resolve().parent
FIRST_DOCUMENT = 11
LAST_DOCUMENT = 36
PACKAGE_VERSION = 6
A4_POINTS = (594.96, 841.92)
A4_TOLERANCE = 1.0
DENSITY_MINIMUM = 0.55
FOOTER_URL = "https://www.linkedin.com/in/carralbal"
MEDIA_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".tif", ".tiff", ".svg"}
RASTER_SUFFIXES = MEDIA_SUFFIXES - {".svg"}
ROUTES = {"PROBLEMA", "DISTINCIONES", "DECISIONES", "PRUEBA", "TRANSFERENCIA", "PREPARACIÓN"}
INVALID_RIGHTS = re.compile(r"pending|withheld|unverified|not[_ -]?approved|blocked|unknown|generated|synthetic|ai[_ -]?generated", re.I)
PRIVATE_PATH = re.compile(r"(?:/Users/|/home/|/private/tmp/|file://|[A-Za-z]:[\\/]Users[\\/])")
LFS_HEADER = b"version https://git-lfs.github.com/spec/v1"
PLACEHOLDER = re.compile(
    r"(?i)(?:\blorem ipsum\b|\bplaceholder\b|\bfixme\b|\btbd\b|"
    r"(?-i:\bTODO\s*:)|\[\s*(?:insertar|completar|pendiente)\b|"
    r"portrait-unavailable|perfil bibliogr[aá]fico sin retrato|"
    r"editorial-(?:support|contact)-sheet|class=[\"'][^\"']*contact-sheet)"
)
DIRECT_ADDRESS = re.compile(
    r"(?iu)\b(?:usted(?:es)?|vos|tú|contigo|tu|tus|te|podés|debés|tenés|querés|"
    r"pensá|elegí|traé|revisá|imaginá|considerá|nuestro|nuestra|nuestros|nuestras)\b"
)
INCIDENT_DASH = re.compile(r"(?:—|\s–\s)")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_fingerprint(root: Path) -> dict[str, str]:
    """Content snapshot used to reject a report over a concurrently changed tree."""
    return {
        path.relative_to(root).as_posix(): sha256(path)
        for path in sorted(item for item in root.rglob("*") if item.is_file())
    }


def compact(value: str) -> str:
    value = html_lib.unescape(value).replace("ﬁ", "fi").replace("ﬂ", "fl")
    value = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"[^0-9a-záéíóúüñ]+", "", value)


def words(value: str) -> list[str]:
    # Include Spanish ordinal indicators so edition statements such as
    # "2.ª ed." produce the same searchable fragment as the tagged PDF text.
    return re.findall(r"[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñÀ-ÿªº]+", html_lib.unescape(value))


def check(identifier: str, passed: bool, evidence: Any) -> dict[str, Any]:
    return {"check": identifier, "status": "PASS" if passed else "FAIL", "evidence": evidence}


def clean_markdown_cell(value: str) -> str:
    value = value.strip().strip("`")
    match = re.search(r"\[([^]]+)\]\((https?://[^)]+)\)", value)
    if match:
        return match.group(2) if value.lower().find("http") >= 0 else match.group(1)
    return value


def normalize_name(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return re.sub(r"[^a-z0-9]+", "", "".join(ch for ch in decomposed if not unicodedata.combining(ch)))


def safe_local_path(root: Path, relative: str) -> tuple[Path | None, str | None]:
    candidate_value = relative.split("#", 1)[0].split("?", 1)[0]
    if not candidate_value:
        return None, "empty path"
    candidate = (root / candidate_value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None, "path escapes package"
    return candidate, None


class InventoryParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.images: list[dict[str, str]] = []
        self.local_refs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "img":
            self.images.append(values)
        for attribute in ("src", "href"):
            value = values.get(attribute, "").strip()
            if value and not re.match(r"^(?:https?:|mailto:|data:|#)", value, re.I):
                self.local_refs.append(value)


def extract_urls(value: str) -> set[str]:
    return {
        match.rstrip(".,;:)]}")
        for match in re.findall(r"https?://[^\s<>\"']+", value)
    }


def annotation_urls(reader: PdfReader) -> dict[int, list[str]]:
    result: dict[int, list[str]] = {}
    for number, page in enumerate(reader.pages, 1):
        urls: list[str] = []
        for reference in page.get("/Annots", []):
            item = reference.get_object()
            action = item.get("/A")
            if action and action.get("/URI"):
                urls.append(str(action.get("/URI")))
        result[number] = urls
    return result


def structure_figure_alts(reader: PdfReader) -> list[dict[str, Any]]:
    structure = reader.trailer["/Root"].get("/StructTreeRoot")
    page_ids = {
        page.indirect_reference.idnum: number
        for number, page in enumerate(reader.pages, 1)
        if page.indirect_reference is not None
    }
    found: list[dict[str, Any]] = []
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
                found.append({"page": page_number, "alt": str(item.get("/Alt", ""))})
            if item.get("/K") is not None:
                walk(item.get("/K"), page_ref)
        elif isinstance(item, (list, tuple)):
            for child in item:
                walk(child, inherited_page)

    if structure:
        walk(structure)
    return found


def full_bleed_geometry(page: pdfplumber.page.Page, kind: str = "image") -> dict[str, Any]:
    candidates = page.images if kind == "image" else page.rects
    records: list[dict[str, Any]] = []
    for item in candidates:
        gaps = {
            "left": max(0.0, float(item.get("x0", 0))),
            "right": max(0.0, float(page.width) - float(item.get("x1", 0))),
            "top": max(0.0, float(item.get("top", 0))),
            "bottom": max(0.0, float(page.height) - float(item.get("bottom", 0))),
        }
        if all(value <= A4_TOLERANCE for value in gaps.values()):
            record: dict[str, Any] = {"gaps_pt": {key: round(value, 3) for key, value in gaps.items()}}
            if kind == "rect":
                record["color"] = item.get("non_stroking_color")
            records.append(record)
    return {"passed": bool(records), "candidates": records}


def luminance(color: object) -> float | None:
    if isinstance(color, (int, float)):
        return float(color)
    if isinstance(color, (list, tuple)) and color:
        values = [float(item) for item in color[:3]]
        if len(values) == 1:
            return values[0]
        if len(values) == 3:
            return .2126 * values[0] + .7152 * values[1] + .0722 * values[2]
    return None


def render_pdf(pdf: Path) -> list[dict[str, Any]]:
    command = shutil.which("pdftoppm")
    if not command:
        raise RuntimeError("pdftoppm (Poppler) is required for raster QA")
    records: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix=f"metsi-n11-n36-v{PACKAGE_VERSION}-") as folder:
        prefix = Path(folder) / "page"
        subprocess.run(
            [command, "-gray", "-r", "72", str(pdf), str(prefix)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        paths = sorted(Path(folder).glob("page-*.pgm"), key=lambda item: int(re.search(r"(\d+)$", item.stem).group(1)))
        for number, path in enumerate(paths, 1):
            with Image.open(path) as image:
                gray = np.asarray(image.convert("L"), dtype=np.uint8)
            height, width = gray.shape
            x0, x1 = int(width * .045), int(width * .955)
            y0, y1 = int(height * .035), int(height * .93)
            crop = gray[y0:y1, x0:x1]
            active_rows = (crop < 220).mean(axis=1) >= .004
            rows = np.flatnonzero(active_rows)
            density = 0.0 if not rows.size else float((rows[-1] - rows[0] + 1) / height)
            band = max(2, int(min(width, height) * .015))
            inner = max(band + 1, int(min(width, height) * .04))
            edges = {
                "top": gray[:band, :], "bottom": gray[-band:, :],
                "left": gray[:, :band], "right": gray[:, -band:],
            }
            adjacent = {
                "top": gray[band:inner, :], "bottom": gray[-inner:-band, :],
                "left": gray[:, band:inner], "right": gray[:, -inner:-band],
            }
            edge_nonwhite = {key: float((value < 248).mean()) for key, value in edges.items()}
            white_gutters = [
                key for key in edges
                if edge_nonwhite[key] < .005 and float((adjacent[key] < 245).mean()) > .03
            ]
            edge_mean = float(np.concatenate([value.reshape(-1) for value in edges.values()]).mean())
            records.append({
                "page": number,
                "width_px": width,
                "height_px": height,
                "vertical_density": round(density, 4),
                "nonwhite_fraction": round(float((gray < 248).mean()), 6),
                "edge_nonwhite": {key: round(value, 5) for key, value in edge_nonwhite.items()},
                "edge_mean": round(edge_mean, 2),
                "white_gutters": white_gutters,
                "pixel_sha256": hashlib.sha256(gray.tobytes()).hexdigest(),
            })
    return records


def decode_media(path: Path) -> tuple[bool, dict[str, Any]]:
    try:
        if path.suffix.casefold() == ".svg":
            root = ET.parse(path).getroot()
            return root.tag.endswith("svg"), {"kind": "svg", "root": root.tag}
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            image.load()
            return True, {"kind": "raster", "format": image.format, "mode": image.mode, "size": list(image.size)}
    except Exception as error:
        return False, {"error": f"{type(error).__name__}: {error}"}


def svg_audit(path: Path, expected_labels: Iterable[str]) -> dict[str, Any]:
    problems: list[str] = []
    collisions: list[dict[str, Any]] = []
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        viewbox = [float(value) for value in re.split(r"[ ,]+", root.attrib.get("viewBox", "").strip())]
        if len(viewbox) != 4 or viewbox[2] <= 0 or viewbox[3] <= 0:
            problems.append("invalid viewBox")
            viewbox = [0.0, 0.0, 0.0, 0.0]
        xml = path.read_text(encoding="utf-8")
        if "…" in xml or re.search(r"(?<!\.)\.\.\.(?!\.)", xml):
            problems.append("ellipsis/truncation marker")
        if "foreignObject" in xml:
            problems.append("foreignObject is not portable")
        all_text = " ".join("".join(node.itertext()).strip() for node in root.iter() if node.tag.endswith("text"))
        svg_tokens = set(words(all_text.casefold()))
        stopwords = {
            "a", "al", "como", "con", "de", "del", "el", "en", "es", "esta", "la", "las",
            "lo", "los", "no", "o", "para", "por", "que", "se", "sin", "su", "una", "un", "y",
        }
        label_coverage: dict[str, float] = {}
        missing_labels = []
        for label in expected_labels:
            required = {
                token.casefold() for token in words(label)
                if len(token) >= 3 and token.casefold() not in stopwords
            }
            coverage = 1.0 if not required else len(required & svg_tokens) / len(required)
            label_coverage[label] = round(coverage, 3)
            if coverage < .5:
                missing_labels.append(label)
        if missing_labels:
            problems.append("manifest labels missing from SVG")
        positions: dict[tuple[float, float], list[str]] = defaultdict(list)
        shape_geometry: dict[tuple[Any, ...], int] = Counter()
        for node in root.iter():
            tag = node.tag.rsplit("}", 1)[-1]
            if tag == "text" and "x" in node.attrib and "y" in node.attrib:
                value = " ".join("".join(node.itertext()).split())
                positions[(round(float(node.attrib["x"]), 2), round(float(node.attrib["y"]), 2))].append(value)
                if viewbox[2] and not (viewbox[0] <= float(node.attrib["x"]) <= viewbox[0] + viewbox[2] and viewbox[1] <= float(node.attrib["y"]) <= viewbox[1] + viewbox[3]):
                    problems.append(f"text outside viewBox: {value[:60]}")
            elif tag == "circle":
                key = (tag, round(float(node.attrib.get("cx", 0)), 2), round(float(node.attrib.get("cy", 0)), 2), round(float(node.attrib.get("r", 0)), 2))
                if key[3] >= min(viewbox[2:]) * .03:
                    shape_geometry[key] += 1
            elif tag == "rect":
                key = (tag, round(float(node.attrib.get("x", 0)), 2), round(float(node.attrib.get("y", 0)), 2), round(float(node.attrib.get("width", 0)), 2), round(float(node.attrib.get("height", 0)), 2))
                if key[3] * key[4] < viewbox[2] * viewbox[3] * .8:
                    shape_geometry[key] += 1
        for position, labels in sorted(positions.items()):
            distinct = sorted({label for label in labels if label})
            if len(distinct) > 1:
                collisions.append({"position": list(position), "texts": distinct})
        duplicate_shapes = [list(key) + [count] for key, count in shape_geometry.items() if count > 1]
        if collisions:
            problems.append("text labels share exact coordinates")
        if duplicate_shapes:
            problems.append("semantic shapes share exact geometry")
        return {
            "passed": not problems,
            "problems": sorted(set(problems)),
            "text_collisions": collisions,
            "duplicate_shapes": duplicate_shapes,
            "missing_labels": missing_labels,
            "label_token_coverage": label_coverage,
            "viewBox": viewbox,
        }
    except Exception as error:
        return {"passed": False, "problems": [f"{type(error).__name__}: {error}"]}


def markdown_portrait_evidence(root: Path) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    candidates = sorted(set(root.glob("portrait-sources*.md")) | set(root.glob("assets/**/portrait-sources*.md")))
    for path in candidates:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for index, line in enumerate(lines[:-1]):
            if "|" not in line or "canonical_name" not in line.casefold():
                continue
            headers = [item.strip().casefold() for item in line.strip().strip("|").split("|")]
            for row in lines[index + 2:]:
                if not row.lstrip().startswith("|"):
                    break
                values = [clean_markdown_cell(item) for item in row.strip().strip("|").split("|")]
                if len(values) == len(headers):
                    record = dict(zip(headers, values))
                    record["_source"] = path.relative_to(root).as_posix()
                    records.append(record)
            break
    return records


def portrait_evidence(root: Path, package: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    registry = root / "portrait-registry.json"
    if registry.is_file():
        data = json.loads(registry.read_text(encoding="utf-8"))
        for key, record in (data.get("entries", {}) if isinstance(data, dict) else {}).items():
            if isinstance(record, dict):
                result.append({"key": key, "_source": registry.name, **record})
    result.extend(markdown_portrait_evidence(root))
    rights_file = package / "image-rights-manifest.json"
    if rights_file.is_file():
        data = json.loads(rights_file.read_text(encoding="utf-8"))
        for record in data.get("assets", []):
            if isinstance(record, dict):
                result.append({"_source": rights_file.name, **record})
    return result


def collect_manifest_media(manifest: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    records: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def add(record: dict[str, Any], fallback_dir: str = "assets") -> None:
        value = str(record.get("file") or record.get("source") or "").strip()
        if not value:
            return
        if "/" not in value and fallback_dir:
            value = f"{fallback_dir}/{value}"
        records[value].append(record)

    if isinstance(manifest.get("cover"), dict):
        cover = dict(manifest["cover"])
        cover["file"] = cover.get("source") or cover.get("file")
        add(cover)
    for record in manifest.get("image_manifest", []):
        if isinstance(record, dict):
            add(record)
    for record in manifest.get("portrait_references", []):
        if isinstance(record, dict):
            add(record)
    for record in manifest.get("diagrams", []):
        if isinstance(record, dict):
            add(record, "diagrams")
    if isinstance(manifest.get("closing"), dict):
        add(manifest["closing"])
    return records


def source_block_present(text: str, pdf_compact: str) -> bool:
    tokens = words(text)
    if not tokens:
        return False
    count = min(9, len(tokens))
    fragments = {compact(" ".join(tokens[:count])), compact(" ".join(tokens[-count:]))}
    return all(fragment and fragment in pdf_compact for fragment in fragments)


def page_for_fragment(page_texts: list[str], value: str) -> list[int]:
    token_list = words(value)
    fragment = compact(" ".join(token_list[: min(9, len(token_list))]))
    return [number for number, text in enumerate(page_texts, 1) if fragment and fragment in compact(text)]


def heading_body_audit(entries: list[dict[str, Any]], page_texts: list[str]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    for index, entry in enumerate(entries):
        if entry.get("kind") not in {"heading-2", "heading-3", "heading-4"}:
            continue
        following = next((item for item in entries[index + 1:] if not str(item.get("kind", "")).startswith("heading")), None)
        if not following:
            failures.append({"source_id": entry.get("source_id"), "reason": "no following body"})
            continue
        heading_pages = set(page_for_fragment(page_texts, str(entry.get("text", ""))))
        body_pages = set(page_for_fragment(page_texts, str(following.get("text", ""))))
        if not heading_pages & body_pages:
            failures.append({
                "source_id": entry.get("source_id"),
                "heading": str(entry.get("text", ""))[:100],
                "body_source_id": following.get("source_id"),
                "heading_pages": sorted(heading_pages),
                "body_pages": sorted(body_pages),
            })
    return {"passed": not failures, "failures": failures}


def parse_density_exceptions(manifest: dict[str, Any], page_count: int) -> tuple[set[int], list[dict[str, Any]]]:
    accepted: set[int] = set()
    invalid: list[dict[str, Any]] = []
    raw = manifest.get("density_exceptions", manifest.get("qa_density_exceptions", []))
    if raw is None:
        raw = []
    if not isinstance(raw, list):
        return accepted, [{"reason": "density exceptions must be a list"}]
    for item in raw:
        if not isinstance(item, dict):
            invalid.append({"value": item, "reason": "not an object"})
            continue
        page, role, reason = item.get("page"), str(item.get("role", "")), str(item.get("reason", ""))
        valid = isinstance(page, int) and 1 <= page <= page_count and role in {
            "orientation_apparatus", "reference_apparatus", "assessment_apparatus", "accessibility_apparatus"
        } and len(reason.strip()) >= 24 and not PLACEHOLDER.search(reason)
        if valid:
            accepted.add(page)
        else:
            invalid.append({"value": item, "reason": "invalid page, role, or substantive justification"})
    return accepted, invalid


def audit(number: int) -> dict[str, Any]:
    document = f"N{number:02d}"
    package = HERE / f"{document}-v{PACKAGE_VERSION}-editorial"
    checks: list[dict[str, Any]] = []
    if not package.is_dir():
        checks.append(check("package_exists", False, {"expected": package.name}))
        return finalize_report(document, package.name, checks, {})

    core = {
        "html": package / "index.html", "css": package / "magazine.css",
        "manifest": package / "manifest.json", "document": package / "document.json",
        "source_manifest": package / "source-manifest.json", "integrity": package / "integrity-report.json",
        "pdf": package / "output" / f"{document}-METSI-lectura-previa-v{PACKAGE_VERSION}-final.pdf",
        "raw_pdf": package / "output" / f"{document}-METSI-lectura-previa-v{PACKAGE_VERSION}.pdf",
    }
    missing_core = sorted(key for key, path in core.items() if not path.is_file())
    checks.append(check("required_package_files_exist", not missing_core, {"missing": missing_core}))
    if missing_core:
        return finalize_report(document, package.name, checks, {})
    initial_fingerprint = package_fingerprint(package)

    html = core["html"].read_text(encoding="utf-8")
    css = core["css"].read_text(encoding="utf-8")
    manifest = json.loads(core["manifest"].read_text(encoding="utf-8"))
    document_json = json.loads(core["document"].read_text(encoding="utf-8"))
    source_manifest = json.loads(core["source_manifest"].read_text(encoding="utf-8"))
    integrity = json.loads(core["integrity"].read_text(encoding="utf-8"))
    source_relative = str(manifest.get("source", ""))
    source_path, source_path_error = safe_local_path(package, source_relative)
    source_exists = source_path is not None and source_path.is_file()
    source = source_path.read_text(encoding="utf-8") if source_exists else ""

    inventory = InventoryParser()
    inventory.feed(html)
    css_refs = [value.strip(" \"'") for value in re.findall(r"url\(([^)]+)\)", css)]
    local_refs = inventory.local_refs + [value for value in css_refs if value and not re.match(r"^(?:https?:|data:|#)", value, re.I)]
    broken_refs: list[dict[str, str]] = []
    for value in sorted(set(local_refs)):
        path, error = safe_local_path(package, value)
        if error or not path or not path.is_file():
            broken_refs.append({"reference": value, "reason": error or "missing file"})
    checks.append(check("html_css_paths_are_local_safe_and_resolve", not broken_refs, broken_refs))

    entries = source_manifest.get("eligible_blocks", [])
    entries = entries if isinstance(entries, list) else []
    source_ids = [str(item.get("source_id", "")) for item in entries if isinstance(item, dict)]
    html_ids = re.findall(r'data-source-id=["\']([^"\']+)', html)
    source_hash = sha256(source_path) if source_exists and source_path else None
    source_contract = (
        source_exists and not source_path_error and manifest.get("number") == number
        and source_manifest.get("document") == document
        and source_manifest.get("source") == source_relative
        and manifest.get("source_sha256") == source_hash
        and document_json == manifest
    )
    checks.append(check("source_manifest_and_package_identity_are_hash_locked", source_contract, {
        "source": source_relative, "source_exists": source_exists, "source_path_error": source_path_error,
        "declared_sha256": manifest.get("source_sha256"), "actual_sha256": source_hash,
        "document_json_matches": document_json == manifest,
    }))
    exact_ids = (
        bool(source_ids) and all(source_ids) and len(source_ids) == len(set(source_ids))
        and html_ids == source_ids
        and integrity.get("status") == "PASS"
        and integrity.get("source_block_count") == len(source_ids)
        and integrity.get("rendered_source_id_count") == len(source_ids)
        and integrity.get("missing_source_ids") == [] and integrity.get("unexpected_source_ids") == []
    )
    checks.append(check("source_ids_have_exact_one_to_one_ordered_coverage", exact_ids, {
        "manifest_count": len(source_ids), "manifest_unique": len(set(source_ids)), "html_count": len(html_ids),
        "html_unique": len(set(html_ids)), "first_sequence_difference": next((index for index, pair in enumerate(zip(source_ids, html_ids)) if pair[0] != pair[1]), None),
        "integrity": integrity,
    }))

    repeated_blocks: list[list[str]] = []
    block_groups: dict[str, list[str]] = defaultdict(list)
    for entry in entries:
        normalized = " ".join(words(str(entry.get("text", "")))).casefold()
        if len(normalized.split()) >= 12:
            block_groups[normalized].append(str(entry.get("source_id", "")))
    repeated_blocks = sorted(ids for ids in block_groups.values() if len(ids) > 1)
    checks.append(check("no_exact_repeated_source_blocks", not repeated_blocks, repeated_blocks))

    forbidden_files: list[str] = []
    private_hits: list[dict[str, Any]] = []
    placeholder_hits: list[dict[str, Any]] = []
    for path in sorted(item for item in package.rglob("*") if item.is_file()):
        relative = path.relative_to(package).as_posix()
        head = path.read_bytes()[:200]
        if head.startswith(LFS_HEADER):
            forbidden_files.append(relative)
        if path.suffix.casefold() in {".html", ".css", ".json", ".md", ".svg", ".txt", ".xml"}:
            value = path.read_text(encoding="utf-8", errors="replace")
            if PRIVATE_PATH.search(value):
                private_hits.append({"file": relative, "matches": sorted(set(PRIVATE_PATH.findall(value)))})
            match = None if path.suffix.casefold() == ".css" else PLACEHOLDER.search(value)
            if match:
                placeholder_hits.append({"file": relative, "match": match.group(0)[:100]})
    checks.append(check("no_lfs_pointers_private_paths_or_placeholders", not forbidden_files and not private_hits and not placeholder_hits, {
        "lfs_pointers": forbidden_files, "private_paths": private_hits, "placeholders": placeholder_hits,
    }))

    # The no-dash rule governs METSI prose. Bibliographic titles and page
    # ranges preserve their authoritative punctuation and are audited by the
    # reference checks below rather than rewritten as course prose.
    prose_source = re.split(r"(?m)^## Referencias base\s*$", source, maxsplit=1)[0]
    personal = sorted(set(match.group(0) for match in DIRECT_ADDRESS.finditer(prose_source)))
    dashes = [{"offset": match.start(), "value": match.group(0)} for match in INCIDENT_DASH.finditer(prose_source)]
    checks.append(check("source_register_is_impersonal_and_has_no_incident_dashes", not personal and not dashes, {
        "direct_address": personal, "incident_dashes": dashes[:20],
    }))

    # PDF parsing is deliberately independent from any stored qa-report.
    pdf_bytes = core["pdf"].read_bytes()
    reader = PdfReader(core["pdf"], strict=True)
    raw_reader = PdfReader(core["raw_pdf"], strict=True)
    if reader.is_encrypted:
        raise ValueError("final PDF is encrypted")
    with pdfplumber.open(core["pdf"]) as pdf_document:
        page_texts = [page.extract_text() or "" for page in pdf_document.pages]
        plumber_texts = list(page_texts)
        full_images = {index: full_bleed_geometry(page, "image") for index, page in enumerate(pdf_document.pages, 1)}
        page4_rects = full_bleed_geometry(pdf_document.pages[3], "rect") if len(pdf_document.pages) >= 4 else {"passed": False, "candidates": []}
        page4_dark = any((luminance(item.get("color")) is not None and luminance(item.get("color")) <= .20) for item in page4_rects.get("candidates", []))
        clipped_text: list[dict[str, Any]] = []
        blank_vector_pages: list[int] = []
        for index, page in enumerate(pdf_document.pages, 1):
            if not page.extract_words() and not page.images and not page.rects and not page.curves:
                blank_vector_pages.append(index)
            for word in page.extract_words():
                if float(word["x0"]) < -0.5 or float(word["x1"]) > float(page.width) + .5 or float(word["top"]) < -.5 or float(word["bottom"]) > float(page.height) + .5:
                    clipped_text.append({"page": index, "text": word.get("text"), "bbox": [word.get(key) for key in ("x0", "top", "x1", "bottom")]})
    pypdf_texts = [page.extract_text() or "" for page in reader.pages]
    pdf_text = "\n".join(pypdf_texts)
    pdf_compact = compact(pdf_text)
    # pypdf conserva mejor que pdfplumber el orden de lectura de columnas. La
    # geometria sigue proviniendo de pdfplumber; las pruebas textuales usan esta capa.
    page_texts = pypdf_texts
    page_count = len(reader.pages)
    sizes = [[round(float(page.mediabox.width), 2), round(float(page.mediabox.height), 2)] for page in reader.pages]
    a4 = all(abs(width - A4_POINTS[0]) <= A4_TOLERANCE and abs(height - A4_POINTS[1]) <= A4_TOLERANCE for width, height in sizes)
    valid_pdf = (
        pdf_bytes.startswith(b"%PDF-") and b"%%EOF" in pdf_bytes[-2048:]
        and page_count > 0 and len(raw_reader.pages) > 0 and a4
        and sha256(core["pdf"]) != sha256(core["raw_pdf"])
    )
    checks.append(check("final_pdf_is_parseable_new_distinct_and_all_pages_are_a4", valid_pdf, {
        "pages": page_count, "unique_sizes": sorted({tuple(item) for item in sizes}),
        "bytes": len(pdf_bytes), "final_sha256": sha256(core["pdf"]), "raw_sha256": sha256(core["raw_pdf"]),
    }))

    missing_pdf_blocks = [str(entry.get("source_id")) for entry in entries if not source_block_present(str(entry.get("text", "")), pdf_compact)]
    checks.append(check("every_source_block_has_verifiable_pdf_text", not missing_pdf_blocks, {
        "checked": len(entries), "missing_source_ids": missing_pdf_blocks,
    }))

    headings = [str(item.get("text", "")) for item in entries if item.get("kind") == "heading-2"]
    sections = [(int(number), route, html_lib.unescape(re.sub(r"<[^>]+>", "", title)).strip()) for number, route, title in re.findall(
        rf'<section\b[^>]*data-section=["\'](\d+)["\'][^>]*>.*?<div class=["\']section-marker["\']>.*?<em>({"|".join(ROUTES)})</em>.*?<h2[^>]*>(.*?)</h2>',
        html, re.S,
    )]
    section_numbers = [item[0] for item in sections]
    html_routes = [item[1] for item in sections]
    pdf_header_matches = re.findall(rf'\b(\d{{2}})\s+METSI\s*·\s*{document}\s+({"|".join(ROUTES)})\b', "\n".join(plumber_texts))
    pdf_routes = [route for _, route in pdf_header_matches]
    contents_text = compact(pypdf_texts[1] if page_count >= 2 else "")
    # Anchor each title to its numbered contents entry.  Searching a bare title
    # produced a false failure whenever a short heading such as "Tesis" also
    # appeared in the introductory copy above the list.
    contents_positions = [
        contents_text.find(
            compact("Referencias base SIN NUM.")
            if heading == "Referencias base"
            else compact(f"{index:02d} {heading}")
        )
        for index, heading in enumerate(headings, 1)
    ]
    navigation_ok = (
        headings and section_numbers == list(range(1, len(headings) + 1))
        and [compact(title) for _, _, title in sections] == [compact(title) for title in headings]
        and html_routes == pdf_routes and len(html_routes) == len(headings)
        and set(html_routes) == ROUTES
        and all(position >= 0 for position in contents_positions)
        and contents_positions == sorted(contents_positions)
        and "contenido" in (page_texts[1].casefold() if page_count >= 2 else "")
        and "ruta de lectura" in (page_texts[1].casefold() if page_count >= 2 else "")
    )
    checks.append(check("contents_index_titles_sections_and_routes_are_complete", navigation_ok, {
        "heading_count": len(headings), "section_numbers": section_numbers,
        "html_routes": html_routes, "pdf_routes": pdf_routes,
        "missing_from_contents": [heading for heading, position in zip(headings, contents_positions) if position < 0],
    }))

    pills_match = re.search(
        r'<section\b[^>]*class=["\'][^"\']*pill-summary[^"\']*["\'][^>]*>.*?'
        r'<h2[^>]*>(.*?)</h2>.*?<li[^>]*>(.*?)</li>',
        html,
        re.S,
    )
    pills_evidence: dict[str, Any] = {"found_in_html": bool(pills_match)}
    pills_order_ok = False
    if pills_match:
        pills_title = html_lib.unescape(re.sub(r"<[^>]+>", "", pills_match.group(1))).strip()
        first_pill = html_lib.unescape(re.sub(r"<[^>]+>", "", pills_match.group(2))).strip()
        title_fragment = compact(pills_title)
        item_fragment = compact(first_pill)
        candidates = []
        for page_number, text in enumerate(page_texts, 1):
            normalized = compact(text)
            title_position = normalized.find(title_fragment)
            item_position = normalized.find(item_fragment)
            if title_position >= 0 and item_position >= 0:
                candidates.append({
                    "page": page_number,
                    "title_position": title_position,
                    "first_item_position": item_position,
                })
        pills_order_ok = len(candidates) == 1 and candidates[0]["title_position"] < candidates[0]["first_item_position"]
        pills_evidence.update({"title": pills_title, "first_item": first_pill, "candidate_pages": candidates})
    checks.append(check(
        "pill_summary_heading_precedes_items_in_pdf_reading_order",
        pills_order_ok,
        pills_evidence,
    ))

    heading_body = heading_body_audit(entries, page_texts)
    checks.append(check("all_source_titles_keep_body_on_the_same_page", heading_body["passed"], heading_body["failures"]))

    expected_hh = f"HH-{number:02d}"
    hotel_ok = all("hotelhorizonte" in compact(value) and compact(expected_hh) in compact(value) for value in (source, html, pdf_text))
    checks.append(check("hotel_horizonte_and_document_hh_artifact_are_present", hotel_ok, {"expected_artifact": expected_hh}))

    pause_html = re.findall(r'<section\b[^>]*class=["\'][^"\']*full-bleed[^"\']*full-bleed-quote[^"\']*["\'][^>]*>(.*?)</section>', html, re.S)
    pause_pages = sorted(page for page in range(2, page_count) if full_images.get(page, {}).get("passed"))
    pause_ok = len(pause_html) == 2 and len(pause_pages) == 2 and pause_pages[0] == 5
    checks.append(check("exactly_two_internal_pauses_with_first_on_page_5", pause_ok, {"html_count": len(pause_html), "pdf_pages": pause_pages}))

    raster = render_pdf(core["pdf"])
    raster_by_page = {item["page"]: item for item in raster}
    bleed_pages = [1, *pause_pages, page_count]
    bleed_evidence = {
        page: {"pdf_geometry": full_images.get(page, {}), "raster": raster_by_page.get(page)}
        for page in bleed_pages
    }
    bleed_ok = (
        page_count >= 5 and full_images.get(1, {}).get("passed")
        and page4_rects.get("passed") and page4_dark and raster_by_page.get(4, {}).get("edge_mean", 255) <= 80
        and all(full_images.get(page, {}).get("passed") for page in pause_pages)
        and full_images.get(page_count, {}).get("passed")
        and all(not raster_by_page.get(page, {}).get("white_gutters") for page in [1, 4, *pause_pages, page_count])
    )
    checks.append(check("cover_page4_pauses_and_closing_are_true_pdf_and_raster_bleeds", bleed_ok, {
        "page4": {"dark_geometry": page4_dark, "geometry": page4_rects, "raster": raster_by_page.get(4)},
        "image_pages": bleed_evidence,
    }))

    closing = manifest.get("closing", {}) if isinstance(manifest.get("closing"), dict) else {}
    closing_src = str(closing.get("file", ""))
    if "/" not in closing_src:
        closing_src = f"assets/{closing_src}"
    closing_html = re.search(r'<(?:figure|section)\b[^>]*class=["\'][^"\']*closing-image[^"\']*["\'][^>]*>(.*?)</(?:figure|section)>', html, re.S)
    closing_block = closing_html.group(1) if closing_html else ""
    closing_ok = (
        bool(re.search(r"match|f[oó]sfor", closing_src, re.I))
        and closing_src in closing_block and "fósfor" in str(closing.get("alt", "")).casefold()
        and bool(str(closing.get("caption", "")).strip())
        and compact(str(closing.get("caption", ""))) in compact(page_texts[-1])
        and closing.get("folio") is True and closing.get("footer") is True
    )
    checks.append(check("last_page_is_the_structured_matches_closing", closing_ok, {"file": closing_src, "manifest": closing}))

    manifest_media = collect_manifest_media(manifest)
    media_results: list[dict[str, Any]] = []
    for relative, records in sorted(manifest_media.items()):
        path, error = safe_local_path(package, relative)
        exists = path is not None and path.is_file()
        decoded, decode_detail = decode_media(path) if exists and path else (False, {"error": error or "missing"})
        digest = sha256(path) if exists and path else None
        declared_hashes = sorted({str(record.get("sha256", "")) for record in records if record.get("sha256")})
        media_results.append({
            "file": relative, "exists": exists, "decoded": decoded, "decode": decode_detail,
            "sha256": digest, "declared_sha256": declared_hashes,
            "hash_ok": len(declared_hashes) == 1 and declared_hashes[0] == digest,
        })
    html_image_paths = [item.get("src", "") for item in inventory.images]
    unmanifested = sorted(set(html_image_paths) - set(manifest_media))
    missing_alts = sorted(set(
        item.get("src", "")
        for item in inventory.images
        if not item.get("alt", "").strip()
        and not (
            item.get("aria-hidden", "").casefold() == "true"
            and "hotel-character-portrait" in item.get("class", "").split()
        )
    ))
    alt_mismatches: list[str] = []
    for image in inventory.images:
        records = manifest_media.get(image.get("src", ""), [])
        allowed = {str(record.get("alt", "")) for record in records if record.get("alt")}
        if allowed and image.get("alt", "") not in allowed:
            alt_mismatches.append(image.get("src", ""))
    media_ok = (
        bool(media_results) and not unmanifested and not missing_alts and not alt_mismatches
        and all(item["exists"] and item["decoded"] and item["hash_ok"] for item in media_results)
    )
    checks.append(check("all_visible_media_are_decodable_alt_texted_manifested_and_hash_locked", media_ok, {
        "media": media_results, "unmanifested_html_images": unmanifested,
        "missing_html_alts": missing_alts, "html_manifest_alt_mismatches": sorted(set(alt_mismatches)),
    }))

    visible_counts = Counter(html_image_paths)
    repeated_sources = {path: count for path, count in sorted(visible_counts.items()) if count > 1}
    visible_hashes: dict[str, list[str]] = defaultdict(list)
    for relative in sorted(set(html_image_paths)):
        path, _ = safe_local_path(package, relative)
        if path and path.is_file():
            visible_hashes[sha256(path)].append(relative)
    duplicate_hashes = {digest: paths for digest, paths in visible_hashes.items() if len(paths) > 1}
    page_hashes: dict[str, list[int]] = defaultdict(list)
    for item in raster:
        page_hashes[item["pixel_sha256"]].append(item["page"])
    duplicate_pages = sorted(pages for pages in page_hashes.values() if len(pages) > 1)
    template_tokens = sorted(set(re.findall(r"(?i)(?:editorial-(?:support|contact)-sheet|portrait-unavailable)", html)))
    checks.append(check("no_exact_visual_reuse_contact_sheets_visible_templates_or_duplicate_pages", not repeated_sources and not duplicate_hashes and not duplicate_pages and not template_tokens, {
        "repeated_image_sources": repeated_sources, "duplicate_media_hashes": duplicate_hashes,
        "duplicate_rendered_pages": duplicate_pages, "template_artifacts": template_tokens,
    }))

    portraits = [item for item in manifest.get("portrait_references", []) if isinstance(item, dict)]
    contributors = []
    for block in re.findall(r'<article\b[^>]*class=["\'][^"\']*contributor[^"\']*["\'][^>]*>(.*?)</article>', html, re.S):
        name_match = re.search(r"<h3[^>]*>(.*?)</h3>", block, re.S)
        image_match = re.search(r'<img\b[^>]*src=["\']([^"\']+)["\'][^>]*>', block, re.S)
        contributors.append({
            "name": html_lib.unescape(re.sub(r"<[^>]+>", "", name_match.group(1))).strip() if name_match else "",
            "file": image_match.group(1) if image_match else "",
            "fallback": bool(re.search(r"portrait-unavailable|role=[\"']img[\"']", block, re.I)),
        })
    evidence = portrait_evidence(HERE, package)
    portrait_failures: list[dict[str, Any]] = []
    portrait_hashes: list[str] = []
    for record in portraits:
        name = str(record.get("name", "")).strip()
        relative = str(record.get("file", "")).strip()
        path, error = safe_local_path(package, relative) if relative else (None, "missing file")
        reasons: list[str] = []
        digest = None
        decoded = False
        if not relative or not path or not path.is_file():
            reasons.append(error or "portrait missing")
        elif path.suffix.casefold() not in RASTER_SUFFIXES:
            reasons.append("portrait is not raster")
        else:
            decoded, _ = decode_media(path)
            digest = sha256(path)
            portrait_hashes.append(digest)
            if not decoded:
                reasons.append("portrait does not decode")
            if record.get("sha256") != digest:
                reasons.append("portrait hash mismatch")
        candidates = [item for item in evidence if normalize_name(str(item.get("canonical_name") or item.get("name") or "")) == normalize_name(name)]
        if digest:
            matching_hash = [item for item in candidates if not item.get("sha256") or str(item.get("sha256")) == digest]
            candidates = matching_hash or candidates
        proof = next((item for item in candidates if item.get("source_page") and (item.get("credit_line") or item.get("creator")) and item.get("license_name") and item.get("license_url")), candidates[0] if candidates else {})
        source_page = str(record.get("source_page") or proof.get("source_page") or "")
        credit = str(record.get("credit_line") or record.get("creator") or proof.get("credit_line") or proof.get("creator") or "")
        license_name = str(record.get("license_name") or proof.get("license_name") or "")
        license_url = str(record.get("license_url") or proof.get("license_url") or "")
        manifest_rights = str(record.get("rights_status") or "")
        evidence_rights = str(proof.get("rights_status") or "")
        rights_status = evidence_rights or manifest_rights
        any_invalid_rights = any(
            INVALID_RIGHTS.search(value) for value in (manifest_rights, evidence_rights) if value
        )
        approved = record.get("approved") is True or proof.get("approved") is True or (
            bool(license_name and license_url and rights_status) and not any_invalid_rights
        )
        if not source_page.startswith("https://"):
            reasons.append("missing HTTPS identity/source page")
        if not credit:
            reasons.append("missing creator/credit line")
        if not license_name or not license_url.startswith("https://"):
            reasons.append("missing explicit license name/URL")
        if not rights_status or any_invalid_rights or not approved:
            reasons.append("rights are absent, pending, generated, or not approved")
        if len(words(name)) < 2:
            reasons.append("name is not a concrete person name")
        if reasons:
            portrait_failures.append({"name": name, "file": relative, "reasons": sorted(set(reasons)), "evidence_source": proof.get("_source")})
    portrait_ok = (
        len(portraits) == len(contributors) == 6
        and len({normalize_name(str(item.get("name", ""))) for item in portraits}) == 6
        and len(portrait_hashes) == len(set(portrait_hashes)) == 6
        and not any(item["fallback"] or not item["file"] for item in contributors)
        and [normalize_name(str(item.get("name", ""))) for item in portraits] == [normalize_name(item["name"]) for item in contributors]
        and not portrait_failures
    )
    checks.append(check("six_real_people_have_six_unique_decodable_raster_portraits_credits_and_approved_rights", portrait_ok, {
        "manifest_count": len(portraits), "html_contributors": contributors,
        "unique_portrait_hashes": len(set(portrait_hashes)), "failures": portrait_failures,
    }))

    diagrams = [item for item in manifest.get("diagrams", []) if isinstance(item, dict)]
    diagram_audits: list[dict[str, Any]] = []
    for record in diagrams:
        relative = str(record.get("file", ""))
        if "/" not in relative:
            relative = f"diagrams/{relative}"
        path, error = safe_local_path(package, relative)
        audit = svg_audit(path, record.get("labels", [])) if path and path.is_file() else {"passed": False, "problems": [error or "missing SVG"]}
        diagram_audits.append({"file": relative, **audit})
    diagram_ok = (
        1 <= len(diagrams) <= 2
        and len({str(item.get("family", "")) for item in diagrams}) == len(diagrams)
        and len({str(item.get("sha256", "")) for item in diagrams}) == len(diagrams)
        and all(item.get("family") and item.get("sha256") for item in diagrams)
        and all(item["passed"] for item in diagram_audits)
        and all(html_image_paths.count((str(item.get("file")) if "/" in str(item.get("file")) else f"diagrams/{item.get('file')}")) == 1 for item in diagrams)
    )
    checks.append(check("one_or_two_semantically_selected_infographics_are_unique_and_layout_safe", diagram_ok, {
        "families": [item.get("family") for item in diagrams], "hashes": [item.get("sha256") for item in diagrams], "audits": diagram_audits,
    }))

    root_object = reader.trailer["/Root"]
    mark_info = root_object.get("/MarkInfo") or {}
    figure_alts = structure_figure_alts(reader)
    # N07-N10 exigen figuras semanticas para tapa, editoriales, pausas,
    # infografias y cierre. Los retratos de la ficha se verifican aparte.
    html_alts = sorted(set(
        item.get("alt", "") for item in inventory.images
        if item.get("alt") and "referent-" not in item.get("src", "")
    ))
    semantic_alts = {item.get("alt", "") for item in figure_alts}
    access_ok = (
        root_object.get("/Lang") == "es-AR" and bool(root_object.get("/StructTreeRoot"))
        and bool(mark_info.get("/Marked")) and '<html lang="es-AR">' in html
        and all(alt in semantic_alts for alt in html_alts)
    )
    checks.append(check("pdf_is_tagged_es_ar_and_visible_images_have_semantic_alts", access_ok, {
        "lang": root_object.get("/Lang"), "marked": bool(mark_info.get("/Marked")),
        "struct_tree": bool(root_object.get("/StructTreeRoot")),
        "missing_semantic_alts": sorted(set(html_alts) - semantic_alts),
    }))

    links = annotation_urls(reader)
    footer_counts = [sum(url == FOOTER_URL for url in links[page]) for page in range(1, page_count + 1)]
    folio_missing = [page for page, text in enumerate(page_texts, 1) if not re.search(rf"(?m)(?:^|\s){page:02d}\s+Diego Carralbal,\s*2026\s*·\s*linkedin\.com/in/carralbal\s*$", text)]
    checks.append(check("every_page_has_exact_folio_footer_and_link_annotation", footer_counts == [1] * page_count and not folio_missing, {
        "footer_annotation_counts": footer_counts, "missing_folio_footer_pages": folio_missing,
    }))

    expected_urls = extract_urls(source)
    actual_external = {url for page in links.values() for url in page if url != FOOTER_URL}
    normalized_pdf_text = re.sub(r"\s+", "", pdf_text)
    missing_printed = sorted(url for url in expected_urls if re.sub(r"\s+", "", url) not in normalized_pdf_text)
    reference_pages = [page for page, text in enumerate(page_texts, 1) if page > 3 and "referencias base" in text.casefold()]
    external_link_pages = sorted(page for page, urls in links.items() if any(url != FOOTER_URL for url in urls))
    urls_ok = expected_urls == actual_external and not missing_printed and external_link_pages == reference_pages
    checks.append(check("all_source_urls_are_complete_printed_exactly_annotated_and_confined_to_references", urls_ok, {
        "expected": sorted(expected_urls), "annotated": sorted(actual_external), "missing_printed": missing_printed,
        "reference_pages": reference_pages, "external_link_pages": external_link_pages,
    }))

    declared_exceptions, invalid_exceptions = parse_density_exceptions(manifest, page_count)
    # References are a stable scholarly apparatus whose occupied height is
    # determined by the source list, not an ordinary prose page to be padded.
    structural_exceptions = {1, 2, 3, 4, page_count, *pause_pages, *reference_pages}
    ordinary_pages = [page for page in range(1, page_count + 1) if page not in structural_exceptions | declared_exceptions]
    underfilled = {str(page): raster_by_page[page]["vertical_density"] for page in ordinary_pages if raster_by_page[page]["vertical_density"] < DENSITY_MINIMUM}
    blank_raster = [item["page"] for item in raster if item["nonwhite_fraction"] < .0002]
    density_ok = bool(ordinary_pages) and not invalid_exceptions and not underfilled
    checks.append(check("ordinary_raster_pages_reach_55_percent_vertical_density", density_ok, {
        "minimum": min((raster_by_page[page]["vertical_density"] for page in ordinary_pages), default=None),
        "underfilled": underfilled, "structural_exceptions": sorted(structural_exceptions),
        "declared_exceptions": sorted(declared_exceptions), "invalid_exception_declarations": invalid_exceptions,
    }))
    checks.append(check("no_blank_pages_or_clipped_text_objects", not blank_vector_pages and not blank_raster and not clipped_text, {
        "blank_vector_pages": blank_vector_pages, "blank_raster_pages": blank_raster, "clipped_text": clipped_text[:50],
    }))

    final_fingerprint = package_fingerprint(package)
    changed_during_audit = sorted(
        relative for relative in set(initial_fingerprint) | set(final_fingerprint)
        if initial_fingerprint.get(relative) != final_fingerprint.get(relative)
    )
    checks.append(check("package_bytes_remained_stable_during_audit", not changed_during_audit, {
        "changed_files": changed_during_audit,
    }))

    metrics = {
        "pages": page_count, "source_blocks": len(entries), "pdf_bytes": len(pdf_bytes),
        "pdf_sha256": sha256(core["pdf"]), "pause_pages": pause_pages,
        "minimum_ordinary_vertical_density": min((raster_by_page[page]["vertical_density"] for page in ordinary_pages), default=None),
    }
    return finalize_report(document, package.name, checks, metrics)


def finalize_report(document: str, package: str, checks: list[dict[str, Any]], metrics: dict[str, Any]) -> dict[str, Any]:
    failed = [item["check"] for item in checks if item["status"] == "FAIL"]
    return {
        "document": document, "package": package, "version": f"v{PACKAGE_VERSION}-editorial",
        "validator": Path(__file__).name, "mode": "read-only",
        "status": "FAIL" if failed else "PASS", "passed_checks": len(checks) - len(failed),
        "total_checks": len(checks), "failed_checks": failed, "metrics": metrics, "checks": checks,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, default=FIRST_DOCUMENT, help="Primer N a validar (11-36).")
    parser.add_argument("--end", type=int, default=LAST_DOCUMENT, help="Ultimo N a validar, inclusive (11-36).")
    parser.add_argument("--version", type=int, default=PACKAGE_VERSION, help="Versión editorial a validar.")
    args = parser.parse_args()
    if not (FIRST_DOCUMENT <= args.start <= args.end <= LAST_DOCUMENT):
        parser.error("se requiere 11 <= --start <= --end <= 36")
    return args


def main() -> int:
    global PACKAGE_VERSION
    args = parse_args()
    PACKAGE_VERSION = args.version
    any_fail = False
    any_error = False
    for number in range(args.start, args.end + 1):
        try:
            report = audit(number)
            any_fail = any_fail or report["status"] != "PASS"
        except Exception as error:
            report = {
                "document": f"N{number:02d}", "package": f"N{number:02d}-v{PACKAGE_VERSION}-editorial",
                "version": f"v{PACKAGE_VERSION}-editorial", "validator": Path(__file__).name, "mode": "read-only",
                "status": "ERROR", "error": f"{type(error).__name__}: {error}",
            }
            any_error = True
        print(json.dumps(report, ensure_ascii=False, sort_keys=True, default=str))
    return 2 if any_error else (1 if any_fail else 0)


if __name__ == "__main__":
    sys.exit(main())
