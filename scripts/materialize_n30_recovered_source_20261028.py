"""Preserve N30 v27 editable interior source while reusing identical Git assets.

This package is a source witness, not a claimed byte-exact generator of the
current public PDF: the final cover, tagging and p. 3 were assembled PDF-level.
"""

from __future__ import annotations

import hashlib
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HISTORICAL = ROOT.parent / "UBA-metsi-publication/output/source-recovery-20261020/N30-example-breathing-v27-source-private-20261023"
SHARED = ROOT / "N30-v14-editorial"
TARGET = ROOT / "N30-v27-recovered-source"


def same(a: Path, b: Path) -> bool:
    return a.is_file() and b.is_file() and hashlib.sha256(a.read_bytes()).digest() == hashlib.sha256(b.read_bytes()).digest()


def main() -> None:
    if TARGET.exists():
        raise FileExistsError(TARGET)
    source = (HISTORICAL / "N30/index.html").read_text(encoding="utf-8")
    resources = sorted(set(re.findall(r'(?:src|href)="((?:assets|diagrams)/[^"]+)"', source)))
    if len(resources) != 23 or source.count('data-source-id=') != 324:
        raise AssertionError((len(resources), source.count('data-source-id=')))

    # The public cover is the current stable canonical cover. It is referenced,
    # not copied. The PDF-level assembly step is deliberately documented below.
    source = source.replace(
        "../protected-covers/N30.pdf",
        "../../site/pdf/publicados/N30-METSI-lectura-previa-v10-final.pdf",
    )
    source = source.replace('href="magazine.css"', 'href="../../N30-v14-editorial/magazine.css"')

    local = TARGET / "N30"
    local.mkdir(parents=True)
    reused = 0
    copied = 0
    for relative in resources:
        old = HISTORICAL / "N30" / relative
        existing = SHARED / relative
        if not old.is_file():
            raise FileNotFoundError(old)
        if same(old, existing):
            source = source.replace(f'"{relative}"', f'"../../N30-v14-editorial/{relative}"')
            reused += 1
        else:
            destination = local / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(old, destination)
            copied += 1

    for name in ("recovery.css", "revision-local.css"):
        shutil.copyfile(HISTORICAL / "N30" / name, local / name)
    for name in ("corrections.css", "standard-v7.css"):
        shutil.copyfile(HISTORICAL / name, TARGET / name)
    # One additional SVG is referenced from revision-local.css rather than HTML.
    css_diagram = "diagrams/n30-incident-stages-v14.svg"
    css_dest = local / css_diagram
    css_dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(HISTORICAL / "N30" / css_diagram, css_dest)
    (local / "index.html").write_text(source, encoding="utf-8")
    print({"source_blocks": 324, "resources_in_html": len(resources),
           "reused_identical": reused, "copied_changed_or_missing": copied,
           "css_diagram_copied": css_diagram, "target": str(TARGET)})


if __name__ == "__main__":
    main()
