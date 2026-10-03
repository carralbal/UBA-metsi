#!/usr/bin/env python3
"""Embed the approved N00–N36 route in the home without duplicating its source."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "site" / "index.html"
ROUTE = ROOT / "site" / "covers" / "recorrido" / "index.html"
BEGIN = "      <!-- BEGIN approved N00–N36 learning route -->"
END = "      <!-- END approved N00–N36 learning route -->"


def main() -> None:
    route = ROUTE.read_text(encoding="utf-8")
    component_start = route.index('<div id="metsi-viaje-vertical"')
    component_end = route.index("\n</div>\n</body>", component_start) + len("\n</div>")
    component = route[component_start:component_end]
    component = component.replace('src="mapa.svg"', 'src="covers/recorrido/mapa.svg"')

    replacement = (
        f'{BEGIN}\n'
        '      <div class="learning-map-section" id="mapa-recorrido">\n'
        f'{component}\n'
        '        <p class="learning-map-open"><a href="covers/recorrido/">Abrir el recorrido en una página independiente ↗</a></p>\n'
        '      </div>\n'
        f'{END}'
    )

    home = HOME.read_text(encoding="utf-8")
    if BEGIN in home:
        start = home.index(BEGIN)
        end = home.index(END, start) + len(END)
    else:
        start = home.index('      <div class="block-map section-pad">')
        end = home.index('\n    </section>\n\n    <section class="case-study', start)
    home = home[:start] + replacement + home[end:]
    home = home.replace('class="journey-learning-link" href="covers/recorrido/"', 'class="journey-learning-link" href="#mapa-recorrido"')
    home = home.replace('class="guide-route-link" href="covers/recorrido/"', 'class="guide-route-link" href="#mapa-recorrido"')
    HOME.write_text(home, encoding="utf-8")


if __name__ == "__main__":
    main()
