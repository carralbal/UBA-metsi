#!/usr/bin/env python3
"""Validate structural magazine invariants before rendering."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


LAYOUTS = {
    "cover-editorial",
    "section-opener",
    "article-2col",
    "article-3col",
    "article-rail",
    "editorial-frame",
    "mosaic-essay",
    "portrait-profile",
    "panorama-bottom",
    "hero-page",
    "accent-column",
    "diagram-feature",
    "case-dark",
    "closing-fullbleed",
}


def walk_blocks(blocks: list[dict]):
    for block in blocks:
        yield block
        if block.get("kind") == "columns":
            for group in block.get("items", []):
                yield from walk_blocks(group.get("blocks", []))
        if block.get("kind") == "note":
            yield from walk_blocks(block.get("blocks", []))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    args = parser.parse_args()
    spec = json.loads(args.document.read_text(encoding="utf-8"))
    cards = spec.get("cards", [])
    errors: list[str] = []
    warnings: list[str] = []

    if spec.get("meta", {}).get("mode") != "magazine-print":
        errors.append("meta.mode must be magazine-print")
    if not cards:
        errors.append("document has no pages")
    layouts = [card.get("layout") for card in cards]
    unknown = sorted({layout for layout in layouts if layout not in LAYOUTS})
    if unknown:
        errors.append(f"unknown layout families: {unknown}")
    if len(cards) >= 16 and len(set(layouts)) < 5:
        errors.append("full N-document needs at least five layout families")
    for i in range(len(layouts) - 2):
        if layouts[i] and layouts[i] == layouts[i + 1] == layouts[i + 2]:
            errors.append(f"layout repeats three times at pages {i + 1}-{i + 3}: {layouts[i]}")

    if cards and layouts[0] != "cover-editorial":
        errors.append("first page must use cover-editorial")
    if cards and layouts[-1] != "closing-fullbleed":
        errors.append("last page must use closing-fullbleed")
    if cards and not cards[0].get("image"):
        errors.append("editorial cover requires a background image")

    image_roles = Counter()
    infographic_count = 0
    for page_number, card in enumerate(cards, 1):
        if page_number > 1 and page_number < len(cards) and not card.get("spread_id"):
            warnings.append(f"page {page_number} has no spread_id")
        for block in walk_blocks(card.get("blocks", [])):
            kind = block.get("kind")
            if kind == "image":
                image_roles[block.get("role", "ordinary")] += 1
                span = int(block.get("span", 6))
                if not 1 <= span <= 6:
                    errors.append(f"page {page_number}: image span outside 1-6")
            elif kind == "infographic":
                infographic_count += 1

    pause_count = sum(layout in {"hero-page", "closing-fullbleed"} for layout in layouts)
    if len(cards) >= 16 and pause_count < 3:
        errors.append("full N-document needs at least three deliberate visual-pause pages including the close")
    if len(cards) >= 16 and len(image_roles) < 3:
        errors.append("photography needs at least three distinct editorial roles")
    if infographic_count and all(layout != "diagram-feature" for layout in layouts):
        warnings.append("infographics exist but no diagram-feature page is declared")

    report = {
        "document": str(args.document),
        "pages": len(cards),
        "layout_families": Counter(layouts),
        "image_roles": image_roles,
        "infographics": infographic_count,
        "visual_pauses": pause_count,
        "errors": errors,
        "warnings": warnings,
        "pass": not errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, default=dict))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
