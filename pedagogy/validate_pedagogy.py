#!/usr/bin/env python3
"""Valida la estructura mínima de los paquetes pedagógicos METSI."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REQUIRED = {
    "PREPARACION-ASINCRONICA.md": (
        "## Propósito",
        "## Producción requerida",
        "## Criterios de entrada",
    ),
    "TALLER-SINCRONICO.md": (
        "## Resultado del encuentro",
        "## Duración base",
        "## Preparación docente",
        "## Secuencia",
        "## Evidencias para el portfolio",
    ),
    "GUION-DOCENTE.md": ("Qué se ve", "Nota de orador"),
    "RUBRICA-Y-EVIDENCIAS.md": (
        "## Escala",
        "## Rúbrica",
        "## Evidencia de aprendizaje",
        "## Conexión acumulativa",
    ),
}


def main() -> int:
    problems: list[str] = []
    plan = (ROOT / "PLAN-MAESTRO.md").read_text(encoding="utf-8")
    planned = sorted(set(re.findall(r"\bN(?:0[1-9]|[12][0-9]|3[0-6])\b", plan)))
    expected = [f"N{number:02d}" for number in range(1, 37)]
    if planned != expected:
        problems.append("El plan maestro no contiene exactamente N01 a N36.")

    directories = sorted(path for path in ROOT.glob("N[0-9][0-9]") if path.is_dir())
    package_names = [path.name for path in directories]
    if package_names != expected:
        missing = sorted(set(expected) - set(package_names))
        extra = sorted(set(package_names) - set(expected))
        problems.append(
            "Los directorios de paquetes no coinciden con N01 a N36. "
            f"Faltan: {missing or 'ninguno'}. Sobran: {extra or 'ninguno'}."
        )

    packages: dict[str, dict[str, object]] = {}
    workshop_sequences: dict[tuple[str, ...], str] = {}
    for directory in directories:
        package_problems: list[str] = []
        package_texts: dict[str, str] = {}
        for filename, markers in REQUIRED.items():
            path = directory / filename
            if not path.is_file():
                package_problems.append(f"Falta {filename}.")
                continue
            text = path.read_text(encoding="utf-8")
            package_texts[filename] = text
            for marker in markers:
                if marker not in text:
                    package_problems.append(f"{filename} no contiene {marker}.")
            if re.search(r"\b(?:TODO|TBD|XXX)\b|lorem ipsum", text):
                package_problems.append(f"{filename} contiene un marcador pendiente.")
            if re.search(r"&(?:[a-zA-Z]+|#[0-9]+|#x[0-9a-fA-F]+);", text):
                package_problems.append(f"{filename} contiene una entidad HTML residual.")

        workshop = package_texts.get("TALLER-SINCRONICO.md", "")
        activities = re.findall(
            r"^### \d+\. (.*?), (\d+) minutos$", workshop, flags=re.MULTILINE
        )
        if len(activities) != 8:
            package_problems.append(
                f"TALLER-SINCRONICO.md contiene {len(activities)} actividades; se esperan 8."
            )
        total_minutes = sum(int(minutes) for _, minutes in activities)
        if total_minutes != 120:
            package_problems.append(
                f"TALLER-SINCRONICO.md suma {total_minutes} minutos; se esperan 120."
            )
        sequence = tuple(title.casefold() for title, _ in activities)
        if sequence and sequence in workshop_sequences:
            package_problems.append(
                "TALLER-SINCRONICO.md repite íntegramente la secuencia de "
                f"{workshop_sequences[sequence]}."
            )
        elif sequence:
            workshop_sequences[sequence] = directory.name

        guide = package_texts.get("GUION-DOCENTE.md", "")
        screens = re.findall(r"^\|\s*\d+\s*\|", guide, flags=re.MULTILINE)
        if len(screens) != 10:
            package_problems.append(
                f"GUION-DOCENTE.md contiene {len(screens)} pantallas; se esperan 10."
            )

        rubric = package_texts.get("RUBRICA-Y-EVIDENCIAS.md", "")
        criteria = re.findall(r"^\|\s*[^|]+\s*\|\s*¿", rubric, flags=re.MULTILINE)
        if len(criteria) < 8:
            package_problems.append(
                f"RUBRICA-Y-EVIDENCIAS.md contiene {len(criteria)} criterios; se esperan al menos 8."
            )

        combined = "\n".join(package_texts.values())
        if not re.search(rf"\b(?:HH-{directory.name[1:]}|Hotel Horizonte)\b", combined):
            package_problems.append("El paquete no integra el caso Hotel Horizonte correspondiente.")
        packages[directory.name] = {
            "status": "PASS" if not package_problems else "FAIL",
            "activities": len(activities),
            "minutes": total_minutes,
            "screens": len(screens),
            "rubric_criteria": len(criteria),
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
