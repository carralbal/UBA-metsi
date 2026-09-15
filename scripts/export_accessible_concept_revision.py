#!/usr/bin/env python3
"""Reexporta sólo los N modificados por la revisión de capas accesibles."""

from __future__ import annotations

import os
import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import export_pdfs
import finalize_and_qa
import finalize_block_c_pdfs

TOUCHED = tuple(range(37))
PACKAGES = {
    0: ("N00-v3-final", "v3"), 1: ("N01-v18-final", "v18"),
    2: ("N02-v15-final", "v15"), 3: ("N03-v10-final", "v10"),
    4: ("N04-v9-final", "v9"), 5: ("N05-v10-final", "v10"),
    6: ("N06-v10-final", "v10"), 7: ("N07-v10-final", "v10"),
    8: ("N08-v10-final", "v10"), 9: ("N09-v10-final", "v10"),
    10: ("N10-v9-final", "v9"),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("documents", nargs="*", help="Números N a reexportar; por defecto, todos los modificados")
    args = parser.parse_args()
    selected = tuple(int(item.removeprefix("N").removeprefix("n")) for item in args.documents) or TOUCHED
    unknown = sorted(set(selected) - set(TOUCHED))
    if unknown:
        raise SystemExit(f"Fuera del conjunto revisado: {unknown}")
    finalize_and_qa.register_fonts()
    for number in selected:
        code = f"N{number:02d}"
        if number <= 10:
            package, version = PACKAGES[number]
            os.environ[f"METSI_PACKAGE_ROOT_{code}"] = str(ROOT / package)
            os.environ[f"METSI_PDF_VERSION_{code}"] = version
            if number == 0:
                os.environ["METSI_N00_ROOT"] = str(ROOT / package)
        export_pdfs.export(number)
        if number <= 10:
            finalize_and_qa.finalize(number)
        else:
            finalize_block_c_pdfs.finalize(number)


if __name__ == "__main__":
    main()
