#!/usr/bin/env python3
"""Replace N14's redundant first assignment; keep one product and all IDs."""

from pathlib import Path
import re

from lxml import html


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "N14-v11-post-cecilia/index.html"
OLD = (
    "Para el encuentro, elegí un servicio que conozcas. Contá qué espera recibir la "
    "persona y definí un inicio y un cierre. Reconstruí un caso habitual y otro con "
    "una dificultad. Separá trabajo de espera, identificá traspasos y proponé un "
    "cambio pequeño. Agregá qué consecuencia no deseada observarías antes de darlo "
    "por bueno."
)
NEW = (
    "Un proceso sólo puede compararse antes y después si seguimos la misma unidad, "
    "desde el mismo inicio hasta el mismo cierre. Un caso habitual muestra el flujo; "
    "uno con aviso fallido prueba si el mapa también sirve cuando la promesa se rompe."
)


def main() -> None:
    raw = SOURCE.read_text(encoding="utf-8")
    if raw.count(OLD) != 1:
        raise ValueError("The original preparation paragraph is not unique")
    before = html.fromstring(raw)
    old_ids = before.xpath('//*[@data-source-id]/@data-source-id')
    old_assignment = before.xpath('//*[@data-source-id="N14-s26-b007"]')
    new_assignment = before.xpath('//*[@data-source-id="N14-add-asis-tobe-prep"]')
    if len(old_ids) != 314 or len(set(old_ids)) != 314:
        raise ValueError("Unexpected source ID count")
    if len(old_assignment) != 1 or " ".join(old_assignment[0].itertext()).strip() != OLD:
        raise ValueError("Unexpected original paragraph")
    if len(new_assignment) != 1 or not " ".join(new_assignment[0].itertext()).strip().startswith("Para el encuentro, usá"):
        raise ValueError("The sole AS-IS/TO-BE assignment is missing")
    revised = raw.replace(OLD, NEW, 1)
    after = html.fromstring(revised)
    if after.xpath('//*[@data-source-id]/@data-source-id') != old_ids:
        raise ValueError("Source IDs changed")
    preparation = after.xpath('//*[@data-source-id="N14-s26-b007" or @data-source-id="N14-add-asis-tobe-prep"]')
    if len(preparation) != 2:
        raise ValueError("Preparation structure changed")
    if revised.count("Para el encuentro,") != 1:
        raise ValueError("N14 still has duplicate assignment wording")
    SOURCE.write_text(revised, encoding="utf-8")
    print("N14 canonical source: one assignment, 314 source IDs preserved")


if __name__ == "__main__":
    main()
