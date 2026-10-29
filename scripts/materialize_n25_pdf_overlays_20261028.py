"""Preserve the three tiny N25 editorial overlays, not another full PDF."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HISTORICAL = ROOT.parent / "UBA-metsi-publication/output/source-recovery-20261020/N25-recovered-from-v14-20261024/N25/pauses-v1-private"
TARGET = ROOT / "N25-pdf-source/overlays"
EXPECTED = {
    9: "2652ff935ccf6490af89c6360f92cf482d0759f1e756c2b59d0000036b1c0a66",
    20: "3e69b5d6337ef7e8369b7286209a80a5cb7afff1450ca738cab06cd79490ce66",
    28: "cd0806a756e1d37134cac27a304b06a8b5a53c729d4903949bf74f24b6584cf8",
}


def main() -> None:
    if TARGET.exists():
        raise FileExistsError(TARGET)
    for number, expected in EXPECTED.items():
        source = HISTORICAL / f"overlay-p{number}.pdf"
        if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
            raise AssertionError(f"Overlay changed: {number}")
    TARGET.mkdir(parents=True)
    for number in EXPECTED:
        shutil.copyfile(HISTORICAL / f"overlay-p{number}.pdf", TARGET / f"overlay-p{number}.pdf")
    print({"overlays": len(EXPECTED), "bytes": sum(p.stat().st_size for p in TARGET.iterdir())})


if __name__ == "__main__":
    main()
