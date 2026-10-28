"""Restore the approved public N00 method paragraph lost by source recovery."""

from pathlib import Path

FILE = Path(__file__).resolve().parents[1] / "N00-post-cecilia-from-current-20261027/N00/index.html"
OLD = (
    "Esto no significa que la materia desconfíe de la tecnología ni que postergue indefinidamente la acción. "
    "Significa que actuar profesionalmente exige decidir cuánto comprender antes de comprometer recursos, "
    "qué incertidumbre puede aceptarse, qué evidencia sería suficiente y qué paso reversible permite aprender "
    "sin trasladar un daño. A veces la decisión correcta será construir software. Otras veces será configurar, "
    "integrar, comprar, cambiar una regla, redistribuir autoridad, mejorar una práctica manual o no automatizar "
    "todavía. La metodología no elige de antemano una familia de soluciones: organiza el aprendizaje necesario "
    "para elegir."
)
NEW = (
    "Esto no significa desconfiar de la tecnología ni postergar indefinidamente la acción. Significa comprobar "
    "qué sabemos, qué falta averiguar y si un cambio es viable en lo técnico, lo económico y el trabajo cotidiano. "
    "Después habrá que describir requisitos, comparar alternativas, planificar la intervención y ver qué pasa "
    "cuando el servicio se usa. Construir, configurar, integrar, comprar, cambiar una regla o conservar una "
    "tarea manual son opciones que deben justificarse, no respuestas elegidas de antemano."
)

body = FILE.read_text(encoding="utf-8")
if body.count(OLD) != 1 or NEW in body:
    raise SystemExit("N00 public paragraph mismatch; no edit made")
FILE.write_text(body.replace(OLD, NEW), encoding="utf-8")
print("Restored N00-s05-b003 from the 55-page public PDF")
