#!/usr/bin/env python3
"""Surgical source correction: a ramp scan does not prove baggage boarded."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "N02-post-cecilia-editorial-20261026/index.html"

REPLACEMENTS = {
    "Las dos están mirando un dato correcto sobre algo que ocurrió antes. Ninguna sabe todavía dónde está la valija ahora.":
        "Ambas ven el mismo estado; ninguna sabe si la valija embarcó ni dónde está ahora.",
    "La escena es ficticia. Vamos a seguirla porque permite entender una diferencia importante sin empezar por una definición. Antes de la salida del avión, alguien había escaneado la etiqueta y puesto la valija en un carro. Después llegó una tormenta. El carro fue movido y el equipaje quedó junto a otra puerta. El escaneo se conservó; el movimiento posterior no quedó registrado. El avión salió. Para la aplicación, la secuencia seguía en orden. Para Martina, el viaje estaba incompleto.":
        "La escena es ficticia. Antes de la salida, alguien escaneó la etiqueta y puso la valija en un carro. La aplicación llamó «embarcado» a ese paso, que no probaba que hubiera subido al avión. Después llegó una tormenta: movieron el carro, pero no registraron ese traslado. El avión salió sin la valija. La pantalla mantuvo un estado falso; para Martina, el viaje estaba incompleto.",
    "Un dato correcto sobre un momento no describe por sí solo el servicio completo.":
        "Un escaneo real puede alimentar un estado equivocado y no describir el servicio completo.",
}


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    for before, after in REPLACEMENTS.items():
        count = source.count(before)
        if count == 0 and after in source:
            continue
        if count != 1:
            raise ValueError(f"Expected exactly one occurrence, got {count}: {before[:70]}")
        source = source.replace(before, after)
    SOURCE.write_text(source, encoding="utf-8")
    print(f"Corrected {len(REPLACEMENTS)} source paragraphs in {SOURCE}")


if __name__ == "__main__":
    main()
