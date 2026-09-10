#!/usr/bin/env python3
"""Export METSI Block C HTML packages to tagged A4 PDFs with Chromium."""

from __future__ import annotations

import argparse
import os
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
PACKAGE_VERSION = 6


def export(number: int) -> Path:
    package = ROOT / f"N{number:02d}-v{PACKAGE_VERSION}-editorial"
    source = package / "index.html"
    output = package / "output" / f"N{number:02d}-METSI-lectura-previa-v{PACKAGE_VERSION}.pdf"
    temporary = Path("/private/tmp") / f"N{number:02d}-METSI-v{PACKAGE_VERSION}-{os.getpid()}.pdf"
    with tempfile.TemporaryDirectory(prefix=f"metsi-N{number:02d}-", dir="/private/tmp") as profile:
        command = [
            str(CHROME), "--headless=new", "--no-sandbox", "--disable-gpu",
            "--disable-dev-shm-usage", "--disable-extensions", "--disable-background-networking",
            "--disable-component-update", "--no-pdf-header-footer",
            "--run-all-compositor-stages-before-draw", "--virtual-time-budget=7000",
            f"--user-data-dir={profile}", f"--print-to-pdf={temporary}", source.resolve().as_uri(),
        ]
        if temporary.exists():
            temporary.unlink()
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        deadline = time.monotonic() + 180
        previous = -1
        stable_since = None
        try:
            while time.monotonic() < deadline:
                if temporary.exists() and temporary.stat().st_size > 100_000:
                    size = temporary.stat().st_size
                    if size == previous:
                        stable_since = stable_since or time.monotonic()
                        if time.monotonic() - stable_since >= 2:
                            break
                    else:
                        previous = size
                        stable_since = None
                if process.poll() is not None and temporary.exists():
                    break
                time.sleep(.5)
            else:
                raise TimeoutError(f"Chrome no completó N{number:02d}")
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
        shutil.copy2(temporary, output)
        temporary.unlink()
    if not output.exists() or output.stat().st_size < 100_000:
        raise RuntimeError(f"Exportación incompleta: {output}")
    print(f"EXPORTED N{number:02d} {output.stat().st_size} bytes")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=11)
    parser.add_argument("--end", type=int, default=16)
    args = parser.parse_args()
    for number in range(args.start, args.end + 1):
        export(number)


if __name__ == "__main__":
    main()
