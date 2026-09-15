#!/usr/bin/env python3
"""Build the regionalized N01-N36 HTML packages without touching prior editions."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import build_collection as first  # noqa: E402
import build_block_c_editorial as later  # noqa: E402


VERSIONS = {1: 19, 2: 16, 3: 11, 4: 10, 5: 11, 6: 11, 7: 11, 8: 11, 9: 11, 10: 10}
BASES = {1: 18, 2: 15, 3: 10, 4: 9, 5: 10, 6: 10, 7: 10, 8: 10, 9: 10, 10: 9}


def seed_first_packages() -> None:
    manifest = json.loads((ROOT / "academic-content-regionalization-manifest-n01-n36.json").read_text())
    paths = {int(item["code"][1:]): ROOT / item["source"] for item in manifest["documents"]}
    for number in range(1, 11):
        source_root = ROOT / f"N{number:02d}-v{BASES[number]}-final"
        target_root = ROOT / f"N{number:02d}-v{VERSIONS[number]}-final"
        if not target_root.exists():
            shutil.copytree(source_root, target_root)
        first.SOURCE_PATH_OVERRIDES[number] = paths[number]
        first.OUTPUT_ROOT_OVERRIDES[number] = target_root
        first.PACKAGE_VERSION_LABELS[number] = f"v{VERSIONS[number]}-final"
        result = first.build_document(number)
        print(f"BUILT N{number:02d} {result['source_words']} words")


def build_later_packages() -> None:
    manifest = json.loads((ROOT / "academic-content-regionalization-manifest-n01-n36.json").read_text())
    later.SOURCES = {
        int(item["code"][1:]): ROOT / item["source"]
        for item in manifest["documents"]
        if int(item["code"][1:]) >= 11
    }
    later.PACKAGE_VERSION = 10
    later.BASELINE_VERSION = 9
    for number in range(11, 37):
        result = later.build(number)
        print(f"BUILT N{number:02d} {result['source_words']} words")


def main() -> None:
    seed_first_packages()
    build_later_packages()


if __name__ == "__main__":
    main()
