#!/usr/bin/env python3
"""Export the regionalized packages to PDF using the established Chromium path."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import export_pdfs as first  # noqa: E402
import export_block_c_pdfs as later  # noqa: E402


VERSIONS = {1: 19, 2: 16, 3: 11, 4: 10, 5: 11, 6: 11, 7: 11, 8: 11, 9: 11, 10: 10}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--numbers", nargs="*", type=int, default=list(range(1, 37)))
    args = parser.parse_args()
    selected = set(args.numbers)
    if not selected or min(selected) < 1 or max(selected) > 36:
        raise ValueError("--numbers admite valores entre 1 y 36")
    for number, version in VERSIONS.items():
        if number not in selected:
            continue
        code = f"N{number:02d}"
        os.environ[f"METSI_PACKAGE_ROOT_{code}"] = str(ROOT / f"{code}-v{version}-final")
        os.environ[f"METSI_PDF_VERSION_{code}"] = f"v{version}"
        first.export(number)
    later.PACKAGE_VERSION = 10
    for number in range(11, 37):
        if number not in selected:
            continue
        later.export(number)


if __name__ == "__main__":
    main()
