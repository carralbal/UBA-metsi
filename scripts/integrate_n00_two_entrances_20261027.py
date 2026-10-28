#!/usr/bin/env python3
"""Apply a small, checked two-entrance edit to the recovered current N00 source."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "N00-post-cecilia-from-current-20261027/N00/index.html"

REPLACEMENTS = [
    (
        "METSI: del pedido a una intervención defendible",
        "METSI: del pedido o la señal a una intervención defendible",
        3,
    ),
    (
        "La materia comienza con una incomodidad deliberada. En la vida profesional, los pedidos suelen llegar redactados como soluciones: «hay que reemplazar el sistema», «necesitamos una app», «incorporemos inteligencia artificial», «automaticemos este proceso». Esas frases pueden contener una oportunidad real, una restricción legítima o una decisión política ya tomada. Pero todavía no explican qué fenómeno debe cambiar, quién vive el problema, qué mecanismo lo produce ni qué consecuencias podría introducir la solución preferida. METSI trabaja precisamente en ese espacio entre el pedido y una intervención defendible.",
        "La materia comienza con una incomodidad deliberada. Hay dos formas frecuentes de entrar en una situación. Una es reactiva: «hay que reemplazar el sistema», «necesitamos una app», «incorporemos inteligencia artificial». Otra es proactiva: nadie encarga una solución, pero al observar demoras, reparaciones o datos contradictorios aparece una señal que merece investigación. Ni el pedido ni la señal definen por sí solos el problema: hay que averiguar qué fenómeno importa, a quién afecta, qué mecanismo lo produce y qué consecuencias introduciría cada intervención. METSI trabaja entre esas entradas y una decisión defendible.",
        1,
    ),
    (
        "La progresión completa puede leerse como una cadena de transformaciones: del pedido al problema;",
        "La progresión completa puede leerse como una cadena de transformaciones: del pedido o la señal al problema;",
        1,
    ),
    (
        "La primera tarea no será aceptarlo ni rechazarlo, sino reconstruir qué promesa de servicio está en juego y qué sistema la sostiene o la contradice.",
        "La primera tarea no será aceptarlo ni rechazarlo, sino reconstruir qué promesa de servicio está en juego y qué sistema la sostiene o la contradice. Esta es la entrada reactiva del caso; en N01 también veremos cómo una señal observada puede abrir el mismo recorrido sin encargo de una herramienta.",
        1,
    ),
]


def main():
    body = FILE.read_text(encoding="utf-8")
    for old, new, expected in REPLACEMENTS:
        if body.count(old) != expected or new in body:
            raise ValueError(f"Unexpected N00 occurrence count: {old[:60]!r}")
        body = body.replace(old, new)
    FILE.write_text(body, encoding="utf-8")
    print("N00 edits", len(REPLACEMENTS), "source IDs unchanged")


if __name__ == "__main__":
    main()
