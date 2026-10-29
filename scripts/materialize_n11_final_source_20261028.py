"""Package the exact recovered N11 v76 HTML without duplicating shared assets.

Run once from this repository. This does not produce or alter a PDF.
"""

from __future__ import annotations

import hashlib
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HISTORICAL = ROOT.parent / "UBA-metsi-publication/output/source-recovery-20261020/N11-public-recovery-v1-private-20261022"
TARGET = ROOT / "N11-v76-recovered-final"
SHARED = ROOT / "N11-v13-editorial"
HTML = HISTORICAL / "index-v76-private.html"


def digest(path: Path) -> bytes:
    return hashlib.sha256(path.read_bytes()).digest()


def main() -> None:
    if TARGET.exists():
        raise FileExistsError(TARGET)
    source = HTML.read_text(encoding="utf-8")
    styles = sorted(set(re.findall(r'<link rel="stylesheet" href="([^"]+)"', source)))
    assets = sorted(set(re.findall(r'(?:src|href)="((?:assets|diagrams)/[^"]+)"', source)))
    if len(styles) != 47 or len(assets) != 23:
        raise AssertionError((len(styles), len(assets)))

    # Verify every shared resource is byte-identical before redirecting its URL.
    remap: dict[str, str] = {}
    for relative in assets:
        old = HISTORICAL / relative
        existing = SHARED / relative
        if not old.is_file():
            raise FileNotFoundError(old)
        if existing.is_file():
            if digest(old) != digest(existing):
                raise AssertionError(f"Shared asset differs: {relative}")
            remap[relative] = f"../N11-v13-editorial/{relative}"

    TARGET.mkdir()
    for name in styles + ["public-recovery-n11-v1.css"]:  # Imported by v2.
        shutil.copyfile(HISTORICAL / name, TARGET / name)
    for relative in assets:
        if relative in remap:
            source = source.replace(f'"{relative}"', f'"{remap[relative]}"')
        else:
            destination = TARGET / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HISTORICAL / relative, destination)

    source = source.replace(
        "</head>",
        '<link rel="stylesheet" href="../pedagogy/source-overrides/referentes-legibles-n11-20261028.css"></head>',
        1,
    )
    (TARGET / "index.html").write_text(source, encoding="utf-8")
    if source.count('data-source-id=') != 384:
        raise AssertionError("Source-block count changed")
    print({
        "source_blocks": 384,
        "style_files": len(styles) + 1,
        "resources": len(assets),
        "reused_identical_resources": len(remap),
        "new_small_resources": len(assets) - len(remap),
        "target": str(TARGET),
    })


if __name__ == "__main__":
    main()
