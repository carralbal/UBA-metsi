#!/usr/bin/env python3
"""Publish the audited Block 01 integration into the local METSI site tree."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
RELEASES = {
    "N00": ("N00-v3-final/output/N00-METSI-lectura-previa-v3-final.pdf", "N00-METSI-lectura-previa-v3-final.pdf"),
    "N02": ("N02-v15-final/output/N02-METSI-lectura-previa-v15-final.pdf", "N02-METSI-lectura-previa-v15-final.pdf"),
    "N03": ("N03-v10-final/output/N03-METSI-lectura-previa-v10-final.pdf", "N03-METSI-lectura-previa-v10-final.pdf"),
    "N05": ("N05-v10-final/output/N05-METSI-lectura-previa-v10-final.pdf", "N05-METSI-lectura-previa-v10-final.pdf"),
    "N06": ("N06-v10-final/output/N06-METSI-lectura-previa-v10-final.pdf", "N06-METSI-lectura-previa-v10-final.pdf"),
    "N07": ("N07-v10-final/output/N07-METSI-lectura-previa-v10-final.pdf", "N07-METSI-lectura-previa-v10-final.pdf"),
    "N08": ("N08-v10-final/output/N08-METSI-lectura-previa-v10-final.pdf", "N08-METSI-lectura-previa-v10-final.pdf"),
    "N09": ("N09-v10-final/output/N09-METSI-lectura-previa-v10-final.pdf", "N09-METSI-lectura-previa-v10-final.pdf"),
}
OBSOLETE = (
    "N00-METSI-lectura-previa-v2-final.pdf",
    "N02-METSI-lectura-previa-v14-final.pdf",
    "N03-METSI-lectura-previa-v9-final.pdf",
    "N05-METSI-lectura-previa-v9-final.pdf",
    "N06-METSI-lectura-previa-v9-final.pdf",
    "N07-METSI-lectura-previa-v9-final.pdf",
    "N08-METSI-lectura-previa-v9-final.pdf",
    "N09-METSI-lectura-previa-v9-final.pdf",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    target_dir = SITE / "pdf"
    target_dir.mkdir(parents=True, exist_ok=True)
    published: dict[str, dict[str, object]] = {}
    for code, (source_rel, target_name) in RELEASES.items():
        source = ROOT / source_rel
        target = target_dir / target_name
        if not source.is_file():
            raise FileNotFoundError(source)
        shutil.copy2(source, target)
        cover = SITE / "covers" / f"{code}.png"
        if not cover.is_file():
            subprocess.run(
                ["pdftoppm", "-f", "1", "-singlefile", "-png", "-r", "120", str(source), str(cover.with_suffix(""))],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        published[code] = {
            "source": source_rel,
            "public": f"site/pdf/{target_name}",
            "bytes": target.stat().st_size,
            "sha256": sha256(target),
            "cover_sha256": sha256(cover),
        }
    for name in OBSOLETE:
        path = target_dir / name
        if path.exists():
            path.unlink()

    pdf_hashes: dict[str, str] = {}
    for number in range(11):
        code = f"N{number:02d}"
        candidates = sorted(target_dir.glob(f"{code}-METSI-lectura-previa-*-final.pdf"))
        if len(candidates) != 1:
            raise RuntimeError(f"{code}: expected one public PDF, got {len(candidates)}")
        pdf_hashes[code] = sha256(candidates[0])

    approval_dir = ROOT / "BLOCK-01-integrated-release-current"
    approval_dir.mkdir(parents=True, exist_ok=True)
    approval = {
        "schema": "metsi-block01-integrated-release/v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "approved",
        "scope": [f"N{number:02d}" for number in range(11)],
        "changed": sorted(RELEASES),
        "preserved": ["N01", "N04", "N10"],
        "pdf_sha256": pdf_hashes,
        "published": published,
    }
    (approval_dir / "approval.json").write_text(
        json.dumps(approval, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(approval, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
