"""Recover the immutable pre-Cecilia N00 publication from Git history."""

from hashlib import sha256
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
BASELINE = Path(__file__).resolve().parent / "baseline-public-v4.pdf"
COMMIT = "1b9a546d5442bb9d674fb8147e2a1174db6a6aec"
REPO_PATH = "site/pdf/publicados/N00-METSI-lectura-previa-v4-recorrido.pdf"
EXPECTED_SHA256 = "266aca386c1da43b1ebb83f3b24eaebd022c55b54b3c95a89b3d2b99ccc787c4"


def ensure_baseline() -> Path:
    if not BASELINE.exists():
        temporary = BASELINE.with_suffix(".tmp")
        with temporary.open("wb") as output:
            subprocess.run(["git", "show", f"{COMMIT}:{REPO_PATH}"],
                           cwd=ROOT, stdout=output, check=True)
        temporary.replace(BASELINE)
    actual = sha256(BASELINE.read_bytes()).hexdigest()
    if actual != EXPECTED_SHA256:
        raise ValueError(f"N00 baseline SHA mismatch: {actual}")
    return BASELINE


if __name__ == "__main__":
    print(ensure_baseline())
