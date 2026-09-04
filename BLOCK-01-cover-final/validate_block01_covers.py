#!/usr/bin/env python3
"""Auditoría consolidada, determinista y de sólo lectura para tapas METSI N00–N10.

El script no escribe dentro de los paquetes. Renderiza en un directorio temporal,
compara todas las páginas posteriores a la tapa contra el baseline bloqueado y
genera dos únicos artefactos de revisión en ``--output-dir``: ``audit.json`` y
``contact-sheet-N00-N10.jpg``.

Código de salida: 0 si todas las guardas pasan, 1 si existe una regresión y 2 si
la auditoría no pudo ejecutarse.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pdfplumber
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader


HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE.parent
DEFAULT_BASELINE_MANIFEST = HERE / "baseline-interior-hashes.json"
EXPECTED_A4 = (594.96, 841.92)
A4_TOLERANCE_PT = 1.0


@dataclass(frozen=True)
class DocumentSpec:
    code: str
    package: str
    pdf: str


DOCUMENTS = (
    DocumentSpec("N00", "N00", "output/N00-METSI-lectura-previa-final.pdf"),
    DocumentSpec("N01", "N01-v18-final", "output/N01-METSI-lectura-previa-v18-final.pdf"),
    DocumentSpec("N02", "N02-v14-final", "output/N02-METSI-lectura-previa-v14-final.pdf"),
    DocumentSpec("N03", "N03-v9-final", "output/N03-METSI-lectura-previa-v9-final.pdf"),
    DocumentSpec("N04", "N04-v9-final", "output/N04-METSI-lectura-previa-v9-final.pdf"),
    DocumentSpec("N05", "N05-v9-final", "output/N05-METSI-lectura-previa-v9-final.pdf"),
    DocumentSpec("N06", "N06-v9-final", "output/N06-METSI-lectura-previa-v9-final.pdf"),
    DocumentSpec("N07", "N07-v9-final", "output/N07-METSI-lectura-previa-v9-final.pdf"),
    DocumentSpec("N08", "N08-v9-final", "output/N08-METSI-lectura-previa-v9-final.pdf"),
    DocumentSpec("N09", "N09-v9-final", "output/N09-METSI-lectura-previa-v9-final.pdf"),
    DocumentSpec("N10", "N10-v9-final", "output/N10-METSI-lectura-previa-v9-final.pdf"),
)


class CoverParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_cover = False
        self.cover_depth = 0
        self.src: str | None = None
        self.alt: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "section" and "collection-cover" in values.get("class", "").split():
            self.in_cover = True
            self.cover_depth = 1
        elif self.in_cover:
            self.cover_depth += 1
        if self.in_cover and tag == "img" and self.src is None:
            self.src = values.get("src") or None
            self.alt = values.get("alt") or None

    def handle_endtag(self, tag: str) -> None:
        del tag
        if self.in_cover:
            self.cover_depth -= 1
            if self.cover_depth <= 0:
                self.in_cover = False


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    return re.sub(r"\s+", " ", value).strip()


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def result(passed: bool, **details: Any) -> dict[str, Any]:
    return {"passed": bool(passed), **details}


def percentile(values: np.ndarray, fraction: float) -> float:
    return float(np.percentile(values, fraction * 100.0))


def image_metrics(path: Path) -> dict[str, Any]:
    with Image.open(path) as source:
        image = source.convert("RGB")
        size = list(image.size)
        image.thumbnail((512, 768), Image.Resampling.LANCZOS)
        pixels = np.asarray(image, dtype=np.float32)
    spread = pixels.max(axis=2) - pixels.min(axis=2)
    luminance = (
        pixels[:, :, 0] * 0.2126
        + pixels[:, :, 1] * 0.7152
        + pixels[:, :, 2] * 0.0722
    )
    flattened = luminance.ravel()
    p05 = percentile(flattened, 0.05)
    p50 = percentile(flattened, 0.50)
    p95 = percentile(flattened, 0.95)
    spread_p95 = percentile(spread.ravel(), 0.95)
    mean = float(flattened.mean())
    stddev = float(flattened.std())
    dark = float((flattened < 32).mean() * 100.0)
    highlights = float((flattened > 224).mean() * 100.0)
    midtones = float(((flattened >= 64) & (flattened <= 192)).mean() * 100.0)
    native_bw = spread_p95 <= 8.0
    raw_tonal_reference = (
        p95 - p05 >= 110.0
        and p95 >= 165.0
        and stddev >= 40.0
        and 60.0 <= mean <= 190.0
        and dark <= 40.0
        and highlights <= 55.0
    )
    return {
        "file": str(path),
        "size_px": size,
        "sha256": sha256(path),
        "luminance": {
            "mean": round(mean, 2),
            "p05": round(p05, 2),
            "p50": round(p50, 2),
            "p95": round(p95, 2),
            "stddev": round(stddev, 2),
            "range_p95_p05": round(p95 - p05, 2),
            "dark_below_32_pct": round(dark, 2),
            "midtones_64_192_pct": round(midtones, 2),
            "highlights_above_224_pct": round(highlights, 2),
        },
        "channel_spread_p95": round(spread_p95, 2),
        "native_bw_passed": native_bw,
        "raw_tonal_reference_passed": raw_tonal_reference,
    }


def parse_cover_html(package: Path) -> tuple[Path, str]:
    html_path = package / "index.html"
    parser = CoverParser()
    parser.feed(html_path.read_text(encoding="utf-8"))
    if not parser.src:
        raise ValueError(f"No se encontró la imagen de tapa en {html_path}")
    asset = (package / parser.src).resolve()
    if not asset.is_file():
        raise FileNotFoundError(asset)
    return asset, parser.alt or ""


def active_css_sources(package: Path) -> list[tuple[str, str]]:
    html = (package / "index.html").read_text(encoding="utf-8")
    hrefs = re.findall(
        r"<link\b[^>]*\brel=[\"'][^\"']*stylesheet[^\"']*[\"'][^>]*\bhref=[\"']([^\"']+)[\"']",
        html,
        re.I,
    )
    if not hrefs:
        hrefs = re.findall(r"<link\b[^>]*\bhref=[\"']([^\"']+\.css)[\"'][^>]*>", html, re.I)
    sources: list[tuple[str, str]] = []
    for href in hrefs:
        path = (package / href).resolve()
        if path.is_file():
            sources.append((href, path.read_text(encoding="utf-8")))
    for number, css in enumerate(re.findall(r"<style\b[^>]*>(.*?)</style>", html, re.I | re.S), 1):
        sources.append((f"index.html#style-{number}", css))
    return sources


def css_cover_coverage(package: Path) -> dict[str, Any]:
    sources = active_css_sources(package)
    css = "\n".join(value for _, value in sources)
    rules = re.findall(r"([^{}]+)\{([^{}]*)\}", css)
    image_declarations = " ".join(
        body for selector, body in rules if ".collection-cover>img" in selector.replace(" ", "")
    )
    shade_declarations = " ".join(
        body for selector, body in rules if "cover-shade" in selector
    )
    compact_image = re.sub(r"\s+", "", image_declarations).lower()
    compact_shade = re.sub(r"\s+", "", shade_declarations).lower()
    image_ok = all(
        marker in compact_image
        for marker in ("position:absolute", "inset:0", "width:100%", "height:100%", "object-fit:cover")
    )
    shade_ok = all(
        marker in compact_shade
        for marker in ("position:absolute", "inset:0", "width:100%", "height:100%")
    )
    return result(
        image_ok and shade_ok,
        stylesheets=[name for name, _ in sources],
        image_full_page=image_ok,
        overlay_full_page=shade_ok,
    )


def effective_cover_filter(package: Path, code: str) -> dict[str, Any]:
    """Resuelve la propiedad filter sobre la imagen de tapa en la cascada usada.

    El CSS histórico conserva reglas genéricas con grayscale. La guarda considera
    sólo la declaración ganadora para el elemento ``section.collection-cover >
    img`` del documento auditado, respetando especificidad y orden.
    """
    sources = active_css_sources(package)

    parent_classes = {"collection-cover", f"cover-{code.lower()}"}
    candidates: list[dict[str, Any]] = []
    order = 0
    for source_name, css in sources:
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        for selectors, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
            match = re.search(r"(?:^|;)\s*filter\s*:\s*([^;}]+)", body, re.I)
            if not match:
                continue
            for selector in selectors.split(","):
                order += 1
                compact_selector = re.sub(r"\s+", "", selector.strip())
                parent = re.fullmatch(r"(?:section)?((?:\.[A-Za-z0-9_-]+)+)>img", compact_selector)
                if not parent:
                    continue
                required_classes = set(re.findall(r"\.([A-Za-z0-9_-]+)", parent.group(1)))
                if not required_classes.issubset(parent_classes):
                    continue
                candidates.append(
                    {
                        "source": source_name,
                        "selector": selector.strip(),
                        "value": normalize_text(match.group(1)),
                        "specificity": [0, len(required_classes), 1],
                        "order": order,
                    }
                )
    winner = max(candidates, key=lambda item: (tuple(item["specificity"]), item["order"])) if candidates else None
    value = str(winner["value"]).lower() if winner else ""
    converts = bool(re.search(r"grayscale\s*\(|saturate\s*\(\s*0(?:\D|$)", value))
    return result(bool(winner) and not converts, effective=winner, candidates=candidates, conversion_filter_detected=converts)


def manifest_cover_contract(package: Path, cover_asset: Path, code: str) -> dict[str, Any]:
    manifest_path = package / "manifest.json"
    if not manifest_path.is_file():
        return result(False, reason="manifest.json ausente")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    cover = data.get("cover") if isinstance(data, dict) else None
    if not isinstance(cover, dict):
        return result(False, reason="manifest.cover ausente")
    deployed_sha = sha256(cover_asset)
    declared_source = str(cover.get("source") or "")
    source_path = (package / declared_source).resolve() if declared_source else None
    source_exists = bool(source_path and source_path.is_file())
    source_sha = sha256(source_path) if source_exists and source_path else None
    declared_sha = str(cover.get("sha256") or "")
    origin_ok = cover.get("photographic_origin") == "native_black_and_white"
    treatment_ok = cover.get("render_treatment") == "no_grayscale_conversion"
    asset_ok = declared_sha == deployed_sha
    source_ok = source_exists and source_sha == deployed_sha
    file_ok = str(cover.get("file") or "") == cover_asset.name
    cascade = effective_cover_filter(package, code)
    return result(
        origin_ok and treatment_ok and asset_ok and source_ok and file_ok and cascade["passed"],
        manifest=manifest_path.name,
        photographic_origin=cover.get("photographic_origin"),
        render_treatment=cover.get("render_treatment"),
        declared_file=cover.get("file"),
        deployed_file=cover_asset.name,
        declared_sha256=declared_sha,
        deployed_sha256=deployed_sha,
        declared_source=declared_source,
        source_exists=source_exists,
        source_sha256=source_sha,
        checks={
            "photographic_origin_native_black_and_white": origin_ok,
            "render_treatment_no_grayscale_conversion": treatment_ok,
            "manifest_sha_matches_deployed": asset_ok,
            "declared_source_exists_and_matches_deployed": source_ok,
            "declared_file_matches_deployed": file_ok,
            "effective_css_has_no_bw_conversion": cascade["passed"],
        },
        effective_css_filter=cascade,
    )


def pdf_urls(reader: PdfReader) -> set[str]:
    values: set[str] = set()
    for page in reader.pages:
        for reference in page.get("/Annots") or []:
            try:
                annotation = reference.get_object()
                action = annotation.get("/A")
                action = action.get_object() if action else None
                uri = action.get("/URI") if action else None
                if uri:
                    values.add(str(uri))
            except Exception:
                continue
    return values


def dereference(value: Any) -> Any:
    try:
        return value.get_object()
    except Exception:
        return value


def indirect_identity(value: Any) -> tuple[int, int] | None:
    if value is None:
        return None
    if hasattr(value, "idnum"):
        return int(value.idnum), int(getattr(value, "generation", 0))
    item = dereference(value)
    reference = getattr(item, "indirect_reference", None)
    if reference is not None and hasattr(reference, "idnum"):
        return int(reference.idnum), int(getattr(reference, "generation", 0))
    return None


def object_label(value: Any) -> str:
    identity = indirect_identity(value)
    return f"{identity[0]} {identity[1]} R" if identity else "direct"


def same_pdf_object(first: Any, second: Any) -> bool:
    first_identity = indirect_identity(first)
    second_identity = indirect_identity(second)
    if first_identity is not None or second_identity is not None:
        return first_identity is not None and first_identity == second_identity
    return dereference(first) is dereference(second)


def parent_tree_entries(structure_root: Any) -> dict[int, Any]:
    root = dereference(structure_root)
    if not isinstance(root, dict) or root.get("/ParentTree") is None:
        return {}
    entries: dict[int, Any] = {}
    seen: set[tuple[int, int] | int] = set()

    def walk_number_tree(value: Any) -> None:
        identity = indirect_identity(value)
        marker: tuple[int, int] | int = identity if identity is not None else id(dereference(value))
        if marker in seen:
            return
        seen.add(marker)
        node = dereference(value)
        if not isinstance(node, dict):
            return
        numbers = dereference(node.get("/Nums")) if node.get("/Nums") is not None else None
        if isinstance(numbers, (list, tuple)):
            for index in range(0, len(numbers) - 1, 2):
                try:
                    entries[int(numbers[index])] = numbers[index + 1]
                except (TypeError, ValueError):
                    continue
        kids = dereference(node.get("/Kids")) if node.get("/Kids") is not None else []
        if isinstance(kids, (list, tuple)):
            for child in kids:
                walk_number_tree(child)

    walk_number_tree(root.get("/ParentTree"))
    return entries


def structure_figures(reader: PdfReader) -> list[dict[str, Any]]:
    """Devuelve figuras con evidencia verificable de su enlace al ParentTree.

    Un ``/Alt`` escrito en un diccionario no alcanza: cada ruta se considera
    válida sólo si el contenido marcado o el objeto referenciado vuelve al
    elemento estructural que lo contiene mediante ``/ParentTree``.
    """
    structure_root = reader.trailer["/Root"].get("/StructTreeRoot")
    if not structure_root:
        return []
    parent_entries = parent_tree_entries(structure_root)
    page_numbers = {
        indirect_identity(page.indirect_reference): number
        for number, page in enumerate(reader.pages, 1)
        if page.indirect_reference is not None
    }
    page_by_number = {number: page for number, page in enumerate(reader.pages, 1)}
    figures: list[dict[str, Any]] = []
    seen: set[tuple[int, int] | int] = set()

    def page_number(value: Any) -> int | None:
        return page_numbers.get(indirect_identity(value))

    def mapped_owner(parent_key: int, mcid: int | None, owner: Any) -> tuple[bool, str | None]:
        mapped = parent_entries.get(parent_key)
        if mapped is None:
            return False, None
        if mcid is not None:
            array = dereference(mapped)
            if not isinstance(array, (list, tuple)) or mcid < 0 or mcid >= len(array):
                return False, None
            mapped = array[mcid]
        return same_pdf_object(mapped, owner), object_label(mapped)

    def validate_content_item(
        kind: str,
        item: Any,
        owner: Any,
        inherited_page: Any,
    ) -> dict[str, Any]:
        item_object = dereference(item)
        effective_page = inherited_page
        if isinstance(item_object, dict):
            effective_page = item_object.get("/Pg") or effective_page

        if kind in {"MCID", "MCR"}:
            try:
                mcid = int(item_object if kind == "MCID" else item_object.get("/MCID"))
            except (TypeError, ValueError, AttributeError):
                mcid = -1
            stream = item_object.get("/Stm") if kind == "MCR" and isinstance(item_object, dict) else None
            holder = dereference(stream) if stream is not None else None
            if stream is None:
                number = page_number(effective_page)
                holder = page_by_number.get(number) if number is not None else None
            struct_parents = holder.get("/StructParents") if isinstance(holder, dict) else None
            try:
                parent_key = int(struct_parents)
            except (TypeError, ValueError):
                parent_key = -1
            owner_match, target = mapped_owner(parent_key, mcid, owner) if parent_key >= 0 and mcid >= 0 else (False, None)
            number = page_number(effective_page)
            return {
                "kind": kind,
                "page": number,
                "mcid": mcid if mcid >= 0 else None,
                "stream": object_label(stream) if stream is not None else None,
                "struct_parents": parent_key if parent_key >= 0 else None,
                "parent_tree_target": target,
                "owner_structure_element": object_label(owner),
                "parent_tree_matches_owner": owner_match,
                "valid": number == 1 and mcid >= 0 and parent_key >= 0 and owner_match,
            }

        object_reference = item_object.get("/Obj") if isinstance(item_object, dict) else None
        referenced_object = dereference(object_reference)
        if isinstance(referenced_object, dict):
            effective_page = item_object.get("/Pg") or referenced_object.get("/P") or inherited_page
            struct_parent = referenced_object.get("/StructParent")
        else:
            struct_parent = None
        try:
            parent_key = int(struct_parent)
        except (TypeError, ValueError):
            parent_key = -1
        owner_match, target = mapped_owner(parent_key, None, owner) if parent_key >= 0 else (False, None)
        number = page_number(effective_page)
        return {
            "kind": "OBJR",
            "page": number,
            "object": object_label(object_reference) if object_reference is not None else None,
            "struct_parent": parent_key if parent_key >= 0 else None,
            "parent_tree_target": target,
            "owner_structure_element": object_label(owner),
            "parent_tree_matches_owner": owner_match,
            "valid": number == 1 and object_reference is not None and parent_key >= 0 and owner_match,
        }

    def content_routes(value: Any, owner: Any, inherited_page: Any) -> list[dict[str, Any]]:
        item = dereference(value)
        if isinstance(item, (list, tuple)):
            routes: list[dict[str, Any]] = []
            for child in item:
                routes.extend(content_routes(child, owner, inherited_page))
            return routes
        if isinstance(item, int) and not isinstance(item, bool):
            return [validate_content_item("MCID", item, owner, inherited_page)]
        if not isinstance(item, dict):
            return []
        item_type = str(item.get("/Type") or "")
        if item_type == "/MCR":
            return [validate_content_item("MCR", item, owner, inherited_page)]
        if item_type == "/OBJR":
            return [validate_content_item("OBJR", item, owner, inherited_page)]
        if item.get("/S") is not None:
            child_page = item.get("/Pg") or inherited_page
            child_owner = value
            return content_routes(item.get("/K"), child_owner, child_page) if item.get("/K") is not None else []
        return []

    def walk(value: Any, inherited_page: Any = None) -> None:
        item = dereference(value)
        if isinstance(item, (dict, list, tuple)):
            identity = indirect_identity(value)
            marker: tuple[int, int] | int = identity if identity is not None else id(item)
            if marker in seen:
                return
            seen.add(marker)
        if isinstance(item, dict):
            page_reference = item.get("/Pg") or inherited_page
            if str(item.get("/S")) == "/Figure":
                routes = content_routes(item.get("/K"), value, page_reference) if item.get("/K") is not None else []
                route_pages = [route.get("page") for route in routes if route.get("page") is not None]
                figure_page = page_number(page_reference)
                figures.append(
                    {
                        "page": figure_page if figure_page is not None else (route_pages[0] if route_pages else None),
                        "alt": str(item.get("/Alt") or ""),
                        "structure_element": object_label(value),
                        "semantic_routes": routes,
                        "valid_page_one_route": any(route.get("valid") for route in routes),
                    }
                )
            if item.get("/K") is not None:
                walk(item.get("/K"), page_reference)
        elif isinstance(item, (list, tuple)):
            for child in item:
                walk(child, inherited_page)

    walk(structure_root)
    return figures


def pdf_fonts(reader: PdfReader) -> dict[str, Any]:
    base_fonts: set[str] = set()
    seen: set[int] = set()

    def walk_resources(value: Any) -> None:
        try:
            resources = value.get_object()
        except Exception:
            resources = value
        if not isinstance(resources, dict):
            return
        identity = id(resources)
        if identity in seen:
            return
        seen.add(identity)
        fonts = resources.get("/Font")
        if fonts:
            try:
                fonts = fonts.get_object()
            except Exception:
                pass
            if isinstance(fonts, dict):
                for reference in fonts.values():
                    try:
                        font = reference.get_object()
                    except Exception:
                        font = reference
                    if isinstance(font, dict) and font.get("/BaseFont"):
                        base_fonts.add(str(font.get("/BaseFont")).lstrip("/"))
        xobjects = resources.get("/XObject")
        if xobjects:
            try:
                xobjects = xobjects.get_object()
            except Exception:
                pass
            if isinstance(xobjects, dict):
                for reference in xobjects.values():
                    try:
                        item = reference.get_object()
                    except Exception:
                        item = reference
                    if isinstance(item, dict) and item.get("/Resources"):
                        walk_resources(item.get("/Resources"))

    for page in reader.pages:
        walk_resources(page.get("/Resources") or {})
    cleaned = sorted(re.sub(r"^[A-Z]{6}\+", "", name) for name in base_fonts)
    families = sorted(
        {
            "Avenir" if "Avenir" in name else
            "Didot" if "Didot" in name else
            "Baskerville" if "Baskerville" in name else
            "AppleSymbols" if "AppleSymbols" in name else name
            for name in cleaned
        }
    )
    allowed = {"Avenir", "Didot", "Baskerville", "AppleSymbols"}
    unexpected = sorted(set(families) - allowed)
    return result(not unexpected and {"Avenir", "Didot", "Baskerville"}.issubset(families), families=families, unexpected=unexpected)


def largest_image_bleed(pdf_path: Path) -> dict[str, Any]:
    with pdfplumber.open(pdf_path) as document:
        page = document.pages[0]
        if not page.images:
            return result(False, reason="La tapa no contiene una imagen PDF identificable")
        image = max(page.images, key=lambda item: float(item["width"]) * float(item["height"]))
        gaps = {
            "left": max(0.0, float(image.get("x0", 0.0))),
            "right": max(0.0, float(page.width) - float(image.get("x1", 0.0))),
            "top": max(0.0, float(image.get("top", 0.0))),
            "bottom": max(0.0, float(page.height) - float(image.get("bottom", 0.0))),
        }
        rounded = {key: round(value, 3) for key, value in gaps.items()}
        return result(
            all(value <= 1.5 for value in gaps.values()),
            tolerance_pt=1.5,
            gaps_pt=rounded,
            bbox={key: round(float(image[key]), 3) for key in ("x0", "x1", "top", "bottom")},
        )


def render_page(pdf_path: Path, output: Path, dpi: int) -> Path:
    command = [
        "pdftoppm", "-f", "1", "-l", "1", "-r", str(dpi),
        "-png", "-singlefile", str(pdf_path), str(output.with_suffix("")),
    ]
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    return output


def edge_halo_metrics(path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        pixels = np.asarray(image.convert("RGB"), dtype=np.float32)
    luminance = (
        pixels[:, :, 0] * 0.2126
        + pixels[:, :, 1] * 0.7152
        + pixels[:, :, 2] * 0.0722
    )

    def depth(side: str) -> int:
        maximum = min(48, luminance.shape[0] // 10, luminance.shape[1] // 10)
        count = 0
        for index in range(maximum):
            if side == "top":
                line = luminance[index, :]
            elif side == "bottom":
                line = luminance[-1 - index, :]
            elif side == "left":
                line = luminance[:, index]
            else:
                line = luminance[:, -1 - index]
            near_paper = float((line >= 245.0).mean()) >= 0.985
            uniform_pale = float(line.mean()) >= 230.0 and float(line.std()) <= 6.0
            if near_paper or uniform_pale:
                count += 1
            else:
                break
        return count

    depths = {side: depth(side) for side in ("top", "right", "bottom", "left")}
    row_means = luminance.mean(axis=1)
    bottom_start = int(len(row_means) * 0.70)
    bottom_derivatives = np.abs(np.diff(row_means[bottom_start:]))
    return result(
        max(depths.values()) <= 1,
        maximum_allowed_px=1,
        pale_uniform_border_depth_px=depths,
        bottom_band_max_row_mean_delta=round(float(bottom_derivatives.max(initial=0.0)), 2),
    )


def render_interiors(pdf_path: Path, target: Path, page_count: int) -> list[Path]:
    target.mkdir(parents=True, exist_ok=True)
    prefix = target / "page"
    subprocess.run(
        [
            "pdftoppm", "-f", "2", "-l", str(page_count), "-r", "72",
            str(pdf_path), str(prefix),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    return sorted(target.glob("page-*.ppm"))


def page_number_from_render(path: Path) -> int:
    match = re.search(r"-(\d+)\.ppm$", path.name)
    if not match:
        raise ValueError(path)
    return int(match.group(1))


def rendered_page_hashes(pdf_path: Path, target: Path, page_count: int) -> dict[str, str]:
    pages = render_interiors(pdf_path, target, page_count)
    return {
        str(page_number_from_render(path)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in pages
    }


def compare_interiors_to_hashes(
    current: Path,
    expected_hashes: dict[str, str],
    page_count: int,
    scratch: Path,
) -> dict[str, Any]:
    current_hashes = rendered_page_hashes(current, scratch / "current", page_count)
    expected_numbers = {str(number) for number in range(2, page_count + 1)}
    missing_current = sorted(expected_numbers - set(current_hashes), key=int)
    missing_expected = sorted(expected_numbers - set(expected_hashes), key=int)
    unexpected_current = sorted(set(current_hashes) - expected_numbers, key=int)
    unexpected_expected = sorted(set(expected_hashes) - expected_numbers, key=int)
    differences = [
        {
            "page": int(number),
            "expected_sha256": expected_hashes[number],
            "current_sha256": current_hashes[number],
        }
        for number in sorted(expected_numbers & set(current_hashes) & set(expected_hashes), key=int)
        if current_hashes[number] != expected_hashes[number]
    ]
    return result(
        not differences
        and not missing_current
        and not missing_expected
        and not unexpected_current
        and not unexpected_expected,
        renderer="pdftoppm 72 dpi RGB PPM",
        pages_compared=max(0, page_count - 1),
        compared_page_range=[2, page_count],
        differences=differences,
        missing_current=missing_current,
        missing_expected=missing_expected,
        unexpected_current=unexpected_current,
        unexpected_expected=unexpected_expected,
        page_pixel_sha256=current_hashes,
    )


def baseline_from_pdf(pdf_path: Path, scratch: Path) -> dict[str, Any]:
    reader = PdfReader(pdf_path)
    page_count = len(reader.pages)
    return {
        "page_count": page_count,
        "interior_page_count": max(0, page_count - 1),
        "interior_page_pixel_sha256": rendered_page_hashes(
            pdf_path, scratch / "baseline", page_count
        ),
        "url_set": sorted(pdf_urls(reader)),
        "source_baseline_pdf_sha256": sha256(pdf_path),
    }


def a4_and_pages(reader: PdfReader, expected_page_count: int) -> dict[str, Any]:
    sizes: list[list[float]] = []
    wrong: list[dict[str, Any]] = []
    for number, page in enumerate(reader.pages, 1):
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        sizes.append([round(width, 2), round(height, 2)])
        if abs(width - EXPECTED_A4[0]) > A4_TOLERANCE_PT or abs(height - EXPECTED_A4[1]) > A4_TOLERANCE_PT:
            wrong.append({"page": number, "size_pt": [round(width, 2), round(height, 2)]})
    page_count = len(reader.pages)
    return result(
        page_count == expected_page_count and not wrong,
        pages=page_count,
        expected_pages=expected_page_count,
        expected_a4_pt=list(EXPECTED_A4),
        tolerance_pt=A4_TOLERANCE_PT,
        unique_page_sizes_pt=sorted({tuple(size) for size in sizes}),
        non_a4_pages=wrong,
    )


def eyebrow_check(reader: PdfReader) -> dict[str, Any]:
    raw = reader.pages[0].extract_text() or ""
    normalized = normalize_text(raw)
    first = normalized.find("LECTURA PREVIA")
    second = normalized.find("EDICIÓN 2026")
    lines = [normalize_text(line) for line in raw.splitlines() if normalize_text(line)]
    return result(
        first >= 0 and second > first,
        expected=["LECTURA PREVIA", "EDICIÓN 2026"],
        found_in_order=first >= 0 and second > first,
        separate_lines=("LECTURA PREVIA" in lines and "EDICIÓN 2026" in lines),
        extracted_prefix=normalized[:280],
    )


def cover_alt_check(reader: PdfReader, html_alt: str) -> dict[str, Any]:
    figures = structure_figures(reader)
    page_one_figures = [item for item in figures if item.get("page") == 1]
    page_one_alts = [str(item["alt"]) for item in page_one_figures if item.get("alt")]
    xobject_alts: list[str] = []
    seen_xobjects: set[tuple[int, int] | int] = set()

    def collect_xobject_alts(resources_value: Any) -> None:
        resources = dereference(resources_value)
        if not isinstance(resources, dict) or resources.get("/XObject") is None:
            return
        xobjects = dereference(resources.get("/XObject"))
        if not isinstance(xobjects, dict):
            return
        for reference in xobjects.values():
            item = dereference(reference)
            identity = indirect_identity(reference)
            marker: tuple[int, int] | int = identity if identity is not None else id(item)
            if marker in seen_xobjects:
                continue
            seen_xobjects.add(marker)
            if isinstance(item, dict) and item.get("/Subtype") == "/Image" and item.get("/Alt"):
                xobject_alts.append(str(item.get("/Alt")))
            if isinstance(item, dict) and item.get("/Resources") is not None:
                collect_xobject_alts(item.get("/Resources"))

    collect_xobject_alts(reader.pages[0].get("/Resources") or {})
    catalog = reader.trailer["/Root"]
    mark_info = catalog.get("/MarkInfo")
    try:
        mark_info = mark_info.get_object() if mark_info else {}
    except Exception:
        mark_info = {}
    marked = bool(mark_info.get("/Marked")) if isinstance(mark_info, dict) else False
    language = str(catalog.get("/Lang") or "")
    exact_figures = [
        item
        for item in page_one_figures
        if html_alt and item.get("alt") == html_alt
    ]
    exact_figure = bool(exact_figures)
    exact_figure_with_valid_route = any(item.get("valid_page_one_route") for item in exact_figures)
    exact_xobject = html_alt in xobject_alts if html_alt else False
    return result(
        len(normalize_text(html_alt)) >= 20
        and exact_figure_with_valid_route
        and marked
        and language.lower().startswith("es"),
        html_alt=html_alt,
        pdf_page_one_figure_alts=page_one_alts,
        pdf_page_one_figures=page_one_figures,
        pdf_page_one_image_xobject_alts=xobject_alts,
        exact_figure_match=exact_figure,
        exact_figure_with_valid_semantic_route=exact_figure_with_valid_route,
        accepted_semantic_routes=[
            route
            for item in exact_figures
            for route in item.get("semantic_routes", [])
            if route.get("valid")
        ],
        image_xobject_exact_match_diagnostic=exact_xobject,
        image_xobject_alt_is_not_acceptance_evidence=True,
        pdf_marked=marked,
        pdf_language=language,
    )


def discover_premium_sources(package: Path) -> list[Path]:
    values = list((package / "assets").glob("cover-source-premium-bw-*"))
    return sorted(path for path in values if path.is_file())


def dhash(path: Path) -> int:
    with Image.open(path) as image:
        gray = image.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
        pixels = np.asarray(gray, dtype=np.int16)
    value = 0
    bit = 0
    for row in range(8):
        for column in range(8):
            if pixels[row, column] > pixels[row, column + 1]:
                value |= 1 << bit
            bit += 1
    return value


def make_contact_sheet(records: list[dict[str, Any]], output: Path) -> None:
    columns = 4
    card_width = 310
    image_width = 270
    image_height = 382
    label_height = 98
    margin = 28
    rows = (len(records) + columns - 1) // columns
    sheet = Image.new("RGB", (margin * 2 + columns * card_width, margin * 2 + rows * (image_height + label_height)), "#ECEDE9")
    draw = ImageDraw.Draw(sheet)
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 25)
        body_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 16)
    except OSError:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
    for index, record in enumerate(records):
        row, column = divmod(index, columns)
        x = margin + column * card_width + (card_width - image_width) // 2
        y = margin + row * (image_height + label_height)
        with Image.open(record["_cover_render"]) as cover:
            cover_rgb = cover.convert("RGB")
            cover_rgb.thumbnail((image_width, image_height), Image.Resampling.LANCZOS)
            canvas = Image.new("RGB", (image_width, image_height), "white")
            offset = ((image_width - cover_rgb.width) // 2, (image_height - cover_rgb.height) // 2)
            canvas.paste(cover_rgb, offset)
        sheet.paste(canvas, (x, y))
        passed = record["passed"]
        color = "#1C6B46" if passed else "#A42828"
        draw.text((x, y + image_height + 10), f"{record['code']}  {'PASS' if passed else 'REVISAR'}", font=title_font, fill=color)
        tone = record["checks"]["composed_cover_tone"]["metrics"]["luminance"]
        spread = record["checks"]["native_cover_image"]["metrics"]["channel_spread_p95"]
        draw.text((x, y + image_height + 44), f"PDF L {tone['mean']:.0f}  p05 {tone['p05']:.0f}  p95 {tone['p95']:.0f}", font=body_font, fill="#282A27")
        draw.text((x, y + image_height + 66), f"ACTIVO RGB p95 {spread:.0f}", font=body_font, fill="#555753")
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, "JPEG", quality=93, optimize=True, progressive=True)


def load_baseline_manifest(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError(f"Manifest de baseline inválido: {path}")
    documents = data.get("documents")
    if not isinstance(documents, dict) or set(documents) != {spec.code for spec in DOCUMENTS}:
        raise ValueError("El manifest de baseline no contiene exactamente N00–N10")
    total = 0
    for spec in DOCUMENTS:
        record = documents[spec.code]
        if not isinstance(record, dict):
            raise ValueError(f"Registro de baseline inválido: {spec.code}")
        page_count = int(record.get("page_count", 0))
        hashes = record.get("interior_page_pixel_sha256")
        urls = record.get("url_set")
        if page_count < 2 or not isinstance(hashes, dict) or not isinstance(urls, list):
            raise ValueError(f"Baseline incompleto: {spec.code}")
        expected_pages = {str(number) for number in range(2, page_count + 1)}
        if set(hashes) != expected_pages or any(not re.fullmatch(r"[0-9a-f]{64}", str(value)) for value in hashes.values()):
            raise ValueError(f"Huellas interiores inválidas: {spec.code}")
        if int(record.get("interior_page_count", -1)) != page_count - 1:
            raise ValueError(f"Recuento interior inválido: {spec.code}")
        total += page_count - 1
    if total != 328 or int(data.get("total_interior_pages", -1)) != 328:
        raise ValueError("El baseline no cierra en 328 páginas interiores")
    return data


def explicit_baseline_records(directory: Path, scratch: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for spec in DOCUMENTS:
        pdf_path = directory / f"{spec.code}.pdf"
        if not pdf_path.is_file():
            raise FileNotFoundError(pdf_path)
        target = scratch / spec.code
        records[spec.code] = baseline_from_pdf(pdf_path, target)
        shutil.rmtree(target, ignore_errors=True)
    return records


def audit_document(
    spec: DocumentSpec,
    root: Path,
    baseline_record: dict[str, Any],
    baseline_label: str,
    scratch_root: Path,
) -> dict[str, Any]:
    package = root / spec.package
    pdf_path = package / spec.pdf
    for path in (package / "index.html", pdf_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    cover_asset, html_alt = parse_cover_html(package)
    reader = PdfReader(pdf_path)
    expected_page_count = int(baseline_record["page_count"])
    pages_check = a4_and_pages(reader, expected_page_count)
    page_count = int(pages_check["pages"])
    render_path = render_page(pdf_path, scratch_root / f"{spec.code}-cover.png", 120)
    native_metrics = image_metrics(cover_asset)
    render_metrics = image_metrics(render_path)
    native_metrics["file"] = rel(cover_asset, root)
    render_metrics["file"] = "generated:cover-page-1@120dpi"
    current_urls = pdf_urls(reader)
    baseline_urls = {str(value) for value in baseline_record["url_set"]}
    url_check = result(
        current_urls == baseline_urls,
        current_count=len(current_urls),
        baseline_count=len(baseline_urls),
        current=sorted(current_urls),
        baseline=sorted(baseline_urls),
        added=sorted(current_urls - baseline_urls),
        removed=sorted(baseline_urls - current_urls),
    )
    premium_sources = discover_premium_sources(package)
    checks = {
        "pages_and_a4": pages_check,
        "cover_alt": cover_alt_check(reader, html_alt),
        "eyebrow_extractable": eyebrow_check(reader),
        "native_cover_image": result(
            native_metrics["native_bw_passed"],
            asset=rel(cover_asset, root),
            premium_sources=[rel(path, root) for path in premium_sources],
            deployed_matches_premium_source=any(sha256(path) == native_metrics["sha256"] for path in premium_sources),
            metrics=native_metrics,
        ),
        "manifest_and_provenance_contract": manifest_cover_contract(package, cover_asset, spec.code),
        "composed_cover_tone": result(
            60.0 <= render_metrics["luminance"]["mean"] <= 190.0
            and render_metrics["luminance"]["p95"] >= 145.0
            and render_metrics["luminance"]["range_p95_p05"] >= 110.0
            and render_metrics["luminance"]["stddev"] >= 35.0
            and render_metrics["luminance"]["dark_below_32_pct"] <= 40.0
            and render_metrics["luminance"]["midtones_64_192_pct"] >= 25.0,
            metrics=render_metrics,
        ),
        "css_full_page_cover": css_cover_coverage(package),
        "pdf_image_bleed": largest_image_bleed(pdf_path),
        "rendered_halo": edge_halo_metrics(render_path),
        "fonts": pdf_fonts(reader),
        "urls_equal_baseline": url_check,
        "interior_pixels_equal_baseline": compare_interiors_to_hashes(
            pdf_path,
            {str(key): str(value) for key, value in baseline_record["interior_page_pixel_sha256"].items()},
            page_count,
            scratch_root / f"{spec.code}-interiors",
        ),
    }
    passed = all(check["passed"] for check in checks.values())
    return {
        "code": spec.code,
        "passed": passed,
        "package": spec.package,
        "pdf": rel(pdf_path, root),
        "pdf_sha256": sha256(pdf_path),
        "baseline": baseline_label,
        "baseline_pdf_sha256": baseline_record.get("source_baseline_pdf_sha256"),
        "checks": checks,
        "_cover_asset": str(cover_asset),
        "_cover_render": str(render_path),
    }


def source_uniqueness(records: list[dict[str, Any]]) -> dict[str, Any]:
    hashes: dict[str, list[str]] = {}
    hash_values: dict[str, int] = {}
    for record in records:
        metrics = record["checks"]["native_cover_image"]["metrics"]
        digest = metrics["sha256"]
        hashes.setdefault(digest, []).append(record["code"])
        hash_values[record["code"]] = dhash(Path(record["_cover_asset"]))
    duplicates = {digest: codes for digest, codes in hashes.items() if len(codes) > 1}
    distances: list[dict[str, Any]] = []
    codes = sorted(hash_values)
    for index, first in enumerate(codes):
        for second in codes[index + 1:]:
            distance = (hash_values[first] ^ hash_values[second]).bit_count()
            distances.append({"pair": [first, second], "distance_64": distance})
    minimum = min((item["distance_64"] for item in distances), default=64)
    nearest = sorted(distances, key=lambda item: item["distance_64"])[:8]
    return result(
        not duplicates and minimum >= 10,
        exact_sha_duplicates=duplicates,
        distinct_exact_sources=len(hashes),
        documents=len(records),
        minimum_dhash_distance_64=minimum,
        nearest_pairs=nearest,
    )


def strip_private_fields(record: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if not key.startswith("_")}


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--baseline-manifest", type=Path, default=DEFAULT_BASELINE_MANIFEST)
    parser.add_argument(
        "--baseline-dir",
        type=Path,
        default=None,
        help="Directorio opcional con N00.pdf a N10.pdf; si se omite se usan las huellas empaquetadas.",
    )
    parser.add_argument("--output-dir", type=Path, default=HERE)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    baseline_manifest_path = args.baseline_manifest.resolve()
    output_dir = args.output_dir.resolve()
    if not shutil.which("pdftoppm"):
        print("ERROR: pdftoppm no está disponible", file=sys.stderr)
        return 2
    try:
        baseline_manifest = load_baseline_manifest(baseline_manifest_path)
        with tempfile.TemporaryDirectory(prefix="metsi-block01-cover-audit-") as temporary:
            scratch = Path(temporary)
            if args.baseline_dir is not None:
                baseline_dir = args.baseline_dir.resolve()
                baseline_documents = explicit_baseline_records(
                    baseline_dir, scratch / "explicit-baseline"
                )
                baseline_label = f"explicit-pdf-directory:{baseline_dir.name}"
                baseline_descriptor = {
                    "mode": "explicit_pdf_directory",
                    "directory_name": baseline_dir.name,
                }
            else:
                baseline_documents = baseline_manifest["documents"]
                baseline_label = f"bundled-manifest:{baseline_manifest_path.name}"
                baseline_descriptor = {
                    "mode": "bundled_manifest",
                    "file": baseline_manifest_path.name,
                    "sha256": sha256(baseline_manifest_path),
                    "baseline_id": baseline_manifest.get("baseline_id"),
                }
            records = [
                audit_document(
                    spec,
                    root,
                    baseline_documents[spec.code],
                    baseline_label,
                    scratch,
                )
                for spec in DOCUMENTS
            ]
            uniqueness = source_uniqueness(records)
            interior_pages_compared = sum(
                int(record["checks"]["interior_pixels_equal_baseline"]["pages_compared"])
                for record in records
            )
            interior_total = result(
                interior_pages_compared == 328,
                expected=328,
                actual=interior_pages_compared,
            )
            failed_checks = {
                record["code"]: [name for name, check in record["checks"].items() if not check["passed"]]
                for record in records
                if not record["passed"]
            }
            overall = (
                all(record["passed"] for record in records)
                and uniqueness["passed"]
                and interior_total["passed"]
            )
            contact_sheet = output_dir / "contact-sheet-N00-N10.jpg"
            make_contact_sheet(records, contact_sheet)
            public_records = [strip_private_fields(record) for record in records]
            report = {
                "schema_version": 2,
                "scope": "METSI Bloque 1, N00–N10; N11 excluido",
                "passed": overall,
                "summary": {
                    "documents_passed": sum(1 for record in records if record["passed"]),
                    "documents_total": len(records),
                    "failed_checks": failed_checks,
                    "interior_pages_compared": interior_pages_compared,
                    "url_sets_equal": sum(1 for record in records if record["checks"]["urls_equal_baseline"]["passed"]),
                },
                "root": ".",
                "baseline": baseline_descriptor,
                "method": {
                    "interior_pixel_comparison": "Páginas 2 a última, raster RGB PPM a 72 dpi con pdftoppm; SHA-256 exacto contra la huella canónica por página.",
                    "native_bw": "Dispersión RGB p95 menor o igual a 8 en el activo desplegado.",
                    "tonal_range": "Sobre la tapa PDF compuesta: media 60–190, p95 >= 145, p95 menos p05 >= 110, desvío >= 35, sombras < 32 <= 40 % y medios tonos 64–192 >= 25 %.",
                    "bleed_and_halo": "Caja de imagen a <= 1,5 pt de cada borde, CSS de imagen y overlay a página completa y borde pálido uniforme <= 1 px.",
                    "cover_alt": "Alt no vacío en HTML y coincidencia exacta con una Figure /Alt de la página 1 que tenga ruta semántica válida mediante MCID o MCR y ParentTree, u OBJR, StructParent y ParentTree; PDF marcado y con idioma español. El /Alt del XObject se informa sólo como diagnóstico.",
                    "eyebrow": "Las cadenas LECTURA PREVIA y EDICIÓN 2026 aparecen completas y en orden en la extracción de la página 1.",
                    "url_set": "Igualdad exacta de los URI de anotaciones PDF contra el baseline.",
                },
                "series_checks": {
                    "cover_source_uniqueness": uniqueness,
                    "interior_pages_compared_total": interior_total,
                },
                "documents": public_records,
                "artifacts": {
                    "audit_json": rel(output_dir / "audit.json", root),
                    "contact_sheet": rel(contact_sheet, root),
                    "baseline_manifest": rel(baseline_manifest_path, root),
                },
            }
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "audit.json").write_text(
                json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        print(json.dumps({"passed": overall, "documents": {record["code"]: record["passed"] for record in records}, "audit": str(output_dir / "audit.json"), "contact_sheet": str(contact_sheet)}, ensure_ascii=False, indent=2))
        return 0 if overall else 1
    except Exception as error:
        print(f"ERROR: {type(error).__name__}: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
