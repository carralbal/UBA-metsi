#!/usr/bin/env python3
"""Validate a reference-grade METSI infographic SVG and optional content manifest."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET


SVG_NS = "{http://www.w3.org/2000/svg}"
FORBIDDEN_TEXT = ("\u00ad", "\u2011")
FORBIDDEN_CSS = ("hyphens:auto", "hyphens: auto", "overflow-wrap:anywhere", "overflow-wrap: anywhere")


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def numeric_font_size(value: str | None) -> float | None:
    if not value:
        return None
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", value)
    return float(match.group(1)) if match else None


def validate_svg(path: Path) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []
    raw = path.read_text(encoding="utf-8")
    lowered = raw.lower().replace(" ", "")

    for token in FORBIDDEN_TEXT:
        if token in raw:
            failures.append(f"contains forbidden hyphenation character U+{ord(token):04X}")
    for token in FORBIDDEN_CSS:
        if token.replace(" ", "") in lowered:
            failures.append(f"contains forbidden CSS: {token}")

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        return [f"invalid XML: {exc}"], warnings

    if local_name(root.tag) != "svg":
        failures.append("root element is not <svg>")
    if not root.get("viewBox"):
        failures.append("SVG root has no viewBox")
    if root.get("role") != "img":
        failures.append('SVG root must declare role="img"')
    if not root.get("aria-labelledby"):
        failures.append("SVG root has no aria-labelledby")

    elements = list(root.iter())
    names = Counter(local_name(el.tag) for el in elements)
    if names["foreignObject"]:
        failures.append("foreignObject is forbidden; keep the asset editable and deterministic")
    if names["title"] < 1:
        failures.append("missing <title>")
    if names["desc"] < 1:
        failures.append("missing <desc>")
    if names["g"] < 8:
        failures.append(f"insufficient structural groups: {names['g']} (minimum 8)")
    if names["path"] < 8:
        warnings.append(f"few path elements: {names['path']} (recommended at least 8)")
    if names["circle"] < 4:
        warnings.append(f"few visible ports/nodes: {names['circle']} (recommended at least 4)")

    texts: list[str] = []
    for el in elements:
        if local_name(el.tag) != "text":
            continue
        label = " ".join("".join(el.itertext()).split())
        if not label:
            failures.append("contains an empty <text> element")
            continue
        texts.append(label)
        font_size = numeric_font_size(el.get("font-size"))
        style = el.get("style", "")
        if font_size is None:
            match = re.search(r"font-size\s*:\s*([0-9.]+)", style)
            font_size = float(match.group(1)) if match else None
        if font_size is not None and font_size < 9:
            failures.append(f'text "{label[:50]}" is below 9 px')
        elif font_size is not None and font_size < 14:
            warnings.append(f'text "{label[:50]}" is below the preferred 14 px')

    meaningful = [text for text in texts if len(text) > 1]
    if len(meaningful) < 15:
        failures.append(f"insufficient meaningful labels: {len(meaningful)} (minimum 15)")
    duplicates = {label: count for label, count in Counter(meaningful).items() if count > 2 and len(label) > 4}
    for label, count in sorted(duplicates.items()):
        failures.append(f'duplicated visible label {count} times: "{label}"')

    return failures, warnings


def validate_manifest(path: Path) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid manifest: {exc}"], warnings

    for key in ("claim", "source_sections", "nodes", "edges"):
        if key not in data:
            failures.append(f'manifest missing required field "{key}"')
    if not isinstance(data.get("claim"), str) or not data.get("claim", "").strip():
        failures.append("manifest claim must be a non-empty string")
    if not isinstance(data.get("source_sections"), list) or not data.get("source_sections"):
        failures.append("manifest must contain at least one source section")

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    if not isinstance(nodes, list) or len(nodes) < 4:
        failures.append("manifest must contain at least four nodes")
        nodes = []
    if not isinstance(edges, list) or not edges:
        failures.append("manifest must contain at least one edge")
        edges = []

    ids: list[str] = []
    for node in nodes:
        if not isinstance(node, dict):
            failures.append("every manifest node must be an object")
            continue
        node_id = str(node.get("id", "")).strip()
        label = str(node.get("label", "")).strip()
        if not node_id:
            failures.append("manifest node has no id")
        else:
            ids.append(node_id)
        if not label:
            failures.append(f'manifest node "{node_id or "?"}" has no label')
        if not node.get("source"):
            warnings.append(f'manifest node "{node_id or "?"}" has no source mapping')

    duplicate_ids = [item for item, count in Counter(ids).items() if count > 1]
    if duplicate_ids:
        failures.append(f"duplicate node ids: {', '.join(sorted(duplicate_ids))}")
    valid_ids = set(ids)
    edge_ids: list[str] = []
    for edge in edges:
        if not isinstance(edge, dict):
            failures.append("every manifest edge must be an object")
            continue
        edge_id = str(edge.get("id", "")).strip()
        if edge_id:
            edge_ids.append(edge_id)
        source = str(edge.get("from", "")).strip()
        target = str(edge.get("to", "")).strip()
        if source not in valid_ids or target not in valid_ids:
            failures.append(f'edge "{edge_id or "?"}" references an unknown endpoint')
        if not str(edge.get("relation", "")).strip():
            failures.append(f'edge "{edge_id or "?"}" has no relation')
        if not str(edge.get("meaning", "")).strip():
            warnings.append(f'edge "{edge_id or "?"}" has no explanatory meaning')
    duplicate_edge_ids = [item for item, count in Counter(edge_ids).items() if count > 1]
    if duplicate_edge_ids:
        failures.append(f"duplicate edge ids: {', '.join(sorted(duplicate_edge_ids))}")

    return failures, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path, help="SVG infographic to validate")
    parser.add_argument("--manifest", type=Path, help="Optional content-manifest.json")
    args = parser.parse_args()

    if not args.svg.is_file():
        print(f"FAIL: SVG not found: {args.svg}")
        return 1

    failures, warnings = validate_svg(args.svg)
    if args.manifest:
        mf, mw = validate_manifest(args.manifest)
        failures.extend(mf)
        warnings.extend(mw)

    for warning in warnings:
        print(f"WARN: {warning}")
    for failure in failures:
        print(f"FAIL: {failure}")
    if failures:
        print(f"RESULT: FAIL ({len(failures)} failure(s), {len(warnings)} warning(s))")
        return 1
    print(f"RESULT: PASS ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
