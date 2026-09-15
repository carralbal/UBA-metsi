#!/usr/bin/env python3
"""Restaura desde el último estado aprobado los seis paquetes con tesis v2."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# State immediately after the N00 thesis-standard expansion and before the
# later accessibility pass selected the wrong early authority file.
BASE = "97d2c96"
PACKAGES = {
    2: "N02-v15-final",
    3: "N03-v10-final",
    5: "N05-v10-final",
    6: "N06-v10-final",
    8: "N08-v10-final",
    9: "N09-v10-final",
}


def previous(path: Path) -> bytes:
    relative = path.relative_to(ROOT).as_posix()
    return subprocess.check_output(["git", "show", f"{BASE}:{relative}"], cwd=ROOT)


def main() -> None:
    restored = 0
    for package_name in PACKAGES.values():
        package = ROOT / package_name
        manifest_text = previous(package / "source-manifest.json")
        (package / "source-manifest.json").write_bytes(manifest_text)
        import json
        manifest = json.loads(manifest_text)
        paths = [
            package / manifest["source"],
            package / "index.html",
            package / "manifest.json",
        ]
        for path in paths:
            path.write_bytes(previous(path))
            restored += 1
    print({"status": "RESTORED", "packages": len(PACKAGES), "files": restored + len(PACKAGES)})


if __name__ == "__main__":
    main()
