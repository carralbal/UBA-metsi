#!/usr/bin/env python3
"""Run the course publication gate on tracked public files only.

The working tree contains unrelated, untracked experiments; they must never
enter this release or produce false failures in its publication gate.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main(validator: Path) -> int:
    tracked = subprocess.check_output(
        ["git", "ls-files", "site", ".github/workflows", "course-manifest.json"],
        cwd=ROOT, text=True,
    ).splitlines()
    with tempfile.TemporaryDirectory(prefix="metsi-editorial-publication-gate-") as directory:
        destination = Path(directory)
        for name in tracked:
            source = ROOT / name
            if source.is_symlink():
                raise ValueError(f"Tracked public asset is a symlink: {name}")
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            os.link(source, target)
        result = subprocess.run([sys.executable, str(validator), str(destination)], text=True)
        return result.returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("validator", type=Path)
    raise SystemExit(main(parser.parse_args().validator))
