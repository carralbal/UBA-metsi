#!/usr/bin/env python3
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parent

REQUIRED = [
    "README.md",
    "CASO-BASE.md",
    "DOSSIER-MAESTRO.md",
    "CUADERNO-DE-EQUIPO.md",
    "BITACORA-INDIVIDUAL.md",
    "MATRIZ-N01-N36.md",
    "PROTOCOLO-DE-REVISION-ENTRE-PARES.md",
    "RUBRICA-ACUMULATIVA.md",
    "GUIA-DOCENTE.md",
]

ERRORS = []

for name in REQUIRED:
    path = ROOT / name
    if not path.is_file() or path.stat().st_size < 200:
        ERRORS.append(f"archivo ausente o insuficiente: {name}")

hitos = sorted((ROOT / "hitos").glob("HITO-*.md"))
if len(hitos) != 8:
    ERRORS.append(f"se esperaban 8 hitos y se encontraron {len(hitos)}")

matrix_path = ROOT / "MATRIZ-N01-N36.md"
if matrix_path.is_file():
    matrix = matrix_path.read_text(encoding="utf-8")
    found = set(re.findall(r"\bN(?:0[1-9]|[12][0-9]|3[0-6])\b", matrix))
    expected = {f"N{i:02d}" for i in range(1, 37)}
    missing = sorted(expected - found)
    if missing:
        ERRORS.append("N sin trazabilidad: " + ", ".join(missing))

readme_path = ROOT / "README.md"
if readme_path.is_file():
    readme = readme_path.read_text(encoding="utf-8")
    for phrase in (
        "Equipos estables de tres o cuatro integrantes",
        "ocho hitos formales",
        "Bitácora individual",
        "Revisión por otro equipo",
    ):
        if phrase not in readme:
            ERRORS.append(f"decisión pedagógica ausente: {phrase}")

for path in hitos:
    text = path.read_text(encoding="utf-8")
    for heading in ("## Producto", "## Componentes obligatorios", "## Prueba de salida"):
        if heading not in text:
            ERRORS.append(f"{path.name}: falta {heading}")

if ERRORS:
    print("FAIL")
    for error in ERRORS:
        print(f"- {error}")
    sys.exit(1)

print("PASS")
print(f"- {len(REQUIRED)} documentos troncales")
print(f"- {len(hitos)} hitos formales")
print("- N01 a N36 con trazabilidad")
print("- agrupamiento, bitácora y revisión entre pares declarados")
