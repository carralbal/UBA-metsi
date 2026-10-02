#!/usr/bin/env python3
"""Compare approved editorial imagery with the readable staged N collection.

This is an inventory, not an automatic design approval. Missing repetitions are
reported separately because some repeated case apparatus is intentional.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from lxml import html


ROOT = Path(__file__).resolve().parents[1]
EARLY_VERSIONS = {1: 19, 2: 16, 3: 11, 4: 10, 5: 11, 6: 11, 7: 11, 8: 11, 9: 11, 10: 10}


def approved_html(number: int) -> Path:
    if number <= 10:
        version = EARLY_VERSIONS[number]
        name = f"N{number:02d}-v{version}-final"
    else:
        name = f"N{number:02d}-v10-editorial"
    return ROOT / name / "index.html"


def inventory(path: Path) -> dict:
    doc = html.parse(str(path))
    images = Counter(node.get("src", "") for node in doc.xpath("//img"))
    figures = Counter(
        " ".join(node.get("class", "").split())
        for node in doc.xpath("//figure")
    )
    sections = [node for node in doc.xpath("//section[@data-section]")]
    return {
        "images": images,
        "figures": figures,
        "sections": len(sections),
        "section_classes": Counter(
            cls for node in sections for cls in node.get("class", "").split()
        ),
    }


def compare(number: int, stage: Path) -> dict:
    approved = inventory(approved_html(number))
    candidate = inventory(stage / f"N{number:02d}" / "index.html")
    missing = approved["images"] - candidate["images"]
    added = candidate["images"] - approved["images"]
    return {
        "document": f"N{number:02d}",
        "approved_images": sum(approved["images"].values()),
        "candidate_images": sum(candidate["images"].values()),
        "missing_image_occurrences": dict(sorted(missing.items())),
        "new_image_occurrences": dict(sorted(added.items())),
        "approved_figures": dict(sorted(approved["figures"].items())),
        "candidate_figures": dict(sorted(candidate["figures"].items())),
        "approved_sections": approved["sections"],
        "candidate_sections": candidate["sections"],
        "candidate_section_classes": dict(sorted(candidate["section_classes"].items())),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    results = [compare(number, args.stage) for number in range(1, 37)]
    report = {"documents": results}
    if args.output:
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    for row in results:
        missing = ", ".join(f"{src} ({count})" for src, count in row["missing_image_occurrences"].items())
        print(f"{row['document']}: {row['approved_images']} → {row['candidate_images']} images; missing {missing or 'none'}")


if __name__ == "__main__":
    main()
