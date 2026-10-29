"""Reproduce the canonical N30 PDF byte-for-byte from Git history.

The full v28 input is already a normal Git blob. This creates it only inside a
temporary directory, applies the approved p. 3 normalization, verifies SHA,
and removes the temporary files automatically.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
REVISION = "a04f8e2ce7849f4d7647a2f1f01a9a1fed354ced"
GIT_PATH = "site/pdf/publicados/N30-METSI-lectura-previa-v10-final.pdf"
V28_SHA = "a838b7b1f85b77bde2127a9b1fd5d0d219d4f5d6fc8be2b1521564c3f5a0cc22"
FINAL_SHA = "3fd62b76ae56949e28b089c6b728094cef6e24b4eebed00e83b3a2a6fe9685db"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    canonical = ROOT / GIT_PATH
    if digest(canonical) != FINAL_SHA:
        raise AssertionError("Current canonical N30 SHA changed")
    with tempfile.TemporaryDirectory(prefix="metsi-n30-rebuild-", dir="/private/tmp") as directory:
        candidate = Path(directory) / "n30-v28.pdf"
        with candidate.open("wb") as stream:
            subprocess.run(["git", "show", f"{REVISION}:{GIT_PATH}"], cwd=ROOT, stdout=stream, check=True)
        if digest(candidate) != V28_SHA:
            raise AssertionError(f"Historical v28 differs: {digest(candidate)}")
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/normalize_n30_n31_referentes_20261028.py"), "N30", str(candidate)],
            check=True,
        )
        if digest(candidate) != FINAL_SHA:
            raise AssertionError(f"Final PDF differs: {digest(candidate)}")
        print({"v28_sha": V28_SHA, "final_sha": FINAL_SHA,
               "same_as_canonical": digest(candidate) == digest(canonical),
               "temporary_files_removed_on_exit": True})


if __name__ == "__main__":
    main()
