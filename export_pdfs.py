#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import signal
import shutil
import subprocess
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


def export(number: int) -> None:
    code = f"N{number:02d}"
    document_root = ROOT / ("N01-v18-final" if number == 1 else "N02-v14-final" if number == 2 else "N03-v9-final" if number == 3 else "N04-v9-final" if number == 4 else "N05-v9-final" if number == 5 else "N06-v9-final" if number == 6 else "N07-v9-final" if number == 7 else "N08-v9-final" if number == 8 else code)
    source = (document_root / "index.html").resolve()
    output_name = "N01-METSI-lectura-previa-v18.pdf" if number == 1 else "N02-METSI-lectura-previa-v14.pdf" if number == 2 else "N03-METSI-lectura-previa-v9.pdf" if number == 3 else "N04-METSI-lectura-previa-v9.pdf" if number == 4 else "N05-METSI-lectura-previa-v9.pdf" if number == 5 else "N06-METSI-lectura-previa-v9.pdf" if number == 6 else "N07-METSI-lectura-previa-v9.pdf" if number == 7 else "N08-METSI-lectura-previa-v9.pdf" if number == 8 else f"{code}-METSI-lectura-previa.pdf"
    output = (document_root / "output" / output_name).resolve()
    with tempfile.TemporaryDirectory(prefix=f"metsi-{code}-chrome-", dir="/private/tmp") as profile:
        # Usar un nombre por proceso evita que una instancia anterior de Chrome,
        # ya terminada o en cierre, siga tocando el mismo archivo temporal.
        temporary_output = Path("/private/tmp") / (
            f"{code}-METSI-{'v18' if number == 1 else 'v14' if number == 2 else 'v9' if number in {3, 4, 5, 6, 7, 8} else 'export'}"
            f"-export-{os.getpid()}.pdf"
        )
        command = [
            str(CHROME),
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--disable-extensions",
            "--disable-background-networking",
            "--disable-component-update",
            "--no-pdf-header-footer",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=5000",
            f"--user-data-dir={profile}",
            f"--print-to-pdf={temporary_output}",
            source.as_uri(),
        ]
        if temporary_output.exists():
            temporary_output.unlink()
        process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        # Las ediciones largas, con fotografía a sangre y retratos de alta
        # resolución, pueden tardar más de un minuto en quedar materializadas.
        # Esperar no altera el documento: evita conservar silenciosamente el
        # PDF anterior cuando Chrome todavía está componiendo las páginas.
        deadline = time.monotonic() + 180
        previous = -1
        stable_since = None
        try:
            while time.monotonic() < deadline:
                if temporary_output.exists() and temporary_output.stat().st_size > 100_000:
                    size = temporary_output.stat().st_size
                    if size == previous:
                        stable_since = stable_since or time.monotonic()
                        if time.monotonic() - stable_since >= 2:
                            break
                    else:
                        previous = size
                        stable_since = None
                if process.poll() is not None and temporary_output.exists():
                    break
                time.sleep(.5)
            else:
                raise TimeoutError(f"Chrome no completó {code}")
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
        if output.exists():
            output.unlink()
        shutil.copy2(temporary_output, output)
        temporary_output.unlink()
    if not output.exists() or output.stat().st_size < 100_000:
        raise RuntimeError(f"Exportación incompleta: {output}")
    print(f"EXPORTED {code} {output.stat().st_size}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("start", type=int)
    parser.add_argument("end", type=int, nargs="?")
    args = parser.parse_args()
    for number in range(args.start, (args.end or args.start) + 1):
        export(number)


if __name__ == "__main__":
    main()
