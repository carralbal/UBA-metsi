#!/usr/bin/env python3
"""Install the second, collection-wide editorial recovery release.

The previous installer performs the same 36-document integrity, cover and
geometry checks.  This release has its own revision and rollback receipt;
the earlier 13-document publication is kept as history.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import install_editorial_art_pass_20261001 as release
from prepare_editorial_recovery import EDITORIAL_FIELD_NOTES


release.REVISION = "editorial-completo-20261002"
release.EXPECTED_CHANGED = set(EDITORIAL_FIELD_NOTES)
release.RECEIPT = (
    release.ROOT
    / "pedagogy/editorial-recovery-20260929/completion-20261002.json"
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", type=Path)
    parser.add_argument("--install", action="store_true")
    args = parser.parse_args()
    release.main(args.stage, args.install)
