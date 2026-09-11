#!/usr/bin/env python3
"""Valida la estructura mínima de los paquetes pedagógicos METSI."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REQUIRED = {
    "PREPARACION-ASINCRONICA.md": ("## Propósito", "## Producción requerida"),
    "TALLER-SINCRONICO.md": ("## Resultado del encuentro", "## Secuencia"),
    "GUION-DOCENTE.md": ("Qué se ve", "Nota de orador"),
    "RUBRICA-Y-EVIDENCIAS.md": ("## Rúbrica", "Evidencia"),
}


def main() -> int:
    problems: list[str] = []
    plan = (ROOT / "PLAN-MAESTRO.md").read_text(encoding="utf-8")
    planned = sorted(set(re.findall(r"\bN(?:0[1-9]|[12][0-9]|3[0-6])\b", plan)))
    expected = [f"N{number:02d}" for number in range(1, 37)]
    if planned != expected:
        problems.append("El plan maestro no contiene exactamente N01 a N36.")

    packages: dict[str, dict[str, object]] = {}
    for directory in sorted(path for path in ROOT.glob("N[0-9][0-9]") if path.is_dir()):
        package_problems: list[str] = []
        for filename, markers in REQUIRED.items():
            path = directory / filename
            if not path.is_file():
                package_problems.append(f"Falta {filename}.")
                continue
            text = path.read_text(encoding="utf-8")
            for marker in markers:
                if marker not in text:
                    package_problems.append(f"{filename} no contiene {marker}.")
            if re.search(r"\b(?:TODO|TBD|XXX)\b|lorem ipsum", text):
                package_problems.append(f"{filename} contiene un marcador pendiente.")
        packages[directory.name] = {
            "status": "PASS" if not package_problems else "FAIL",
            "problems": package_problems,
        }
        problems.extend(f"{directory.name}: {problem}" for problem in package_problems)

    result = {
        "scope": "METSI pedagogical production",
        "status": "PASS" if not problems else "FAIL",
        "planned_nuclei": len(planned),
        "packages_built": len(packages),
        "packages": packages,
        "problems": problems,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
