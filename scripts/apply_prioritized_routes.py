#!/usr/bin/env python3
"""Apply the canonical METSI prioritized-reading contract to N01–N36.

This migration is intentionally limited to the Contents page and package
metadata. It does not rewrite the academic source, images, diagrams, or any
other editorial component.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOTS = {
    1: "N01-v18-final",
    2: "N02-v15-final",
    3: "N03-v10-final",
    4: "N04-v9-final",
    5: "N05-v10-final",
    6: "N06-v10-final",
    7: "N07-v10-final",
    8: "N08-v10-final",
    9: "N09-v10-final",
    10: "N10-v9-final",
    **{number: f"N{number:02d}-v9-editorial" for number in range(11, 37)},
}

ROUTE_NOTE = (
    '<p class="contents-route"><b>Ruta priorizada: 1 h 20 min a 1 h 40 min.</b> '
    'Núcleo de lectura: 60 a 75 min; preparación: 20 a 25 min. '
    'Las extensiones agregan 30 a 45 min y profundizan el recorrido.</p>'
)

CSS_MARKER = "/* METSI prioritized reading route: canonical v1 */"
ROUTE_CSS = r"""
/* METSI prioritized reading route: canonical v1 */
.premium-magazine:not(.document-n00) .contents-page .contents-route{
  max-width:170mm;margin:2mm 0 0;padding-left:3mm;border-left:1.4mm solid #CFFF00;
  font:7.7pt/1.24 Avenir,sans-serif;color:#30322f
}
.premium-magazine:not(.document-n00) .contents-layout li.contents-item{padding-left:1.2mm}
.premium-magazine:not(.document-n00) .contents-layout li.contents-core{border-left:1mm solid #CFFF00}
.premium-magazine:not(.document-n00) .contents-layout li.contents-extension{border-left:1mm solid transparent}
.premium-magazine:not(.document-n00) .contents-layout li small{
  display:inline-block;margin-left:1mm;font-size:6pt;line-height:1;letter-spacing:.06em;color:#666
}
""".strip()


def plain_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", value))).strip()


CORE_OVERRIDES = {
    1: {1, 2, 3, 4, 8, 9, 13, 14, 16, 18, 21, 25, 28},
    2: {1, 2, 3, 4, 7, 9, 10, 12, 15, 16, 18, 21, 24},
}


def is_core(document: int, index: int, title: str) -> bool:
    if document in CORE_OVERRIDES:
        return index in CORE_OVERRIDES[document]
    normalized = plain_text(title).casefold()
    return (
        index <= 4
        or "hotel horizonte" in normalized
        or normalized.startswith("movimiento ")
        or normalized == "síntesis"
        or normalized == "preguntas de preparación"
    )


def classify_item(document: int, match: re.Match[str]) -> str:
    item = match.group(0)
    number_match = re.search(r"<b>(\d{2})</b>", item)
    if not number_match:
        return item
    index = int(number_match.group(1))
    span_start = item.find("<span")
    span_end = item.rfind("</span>")
    title_markup = item[span_start:span_end] if span_start >= 0 and span_end > span_start else item
    title_markup = re.sub(r"<small>(?:NÚCLEO|EXT\.)</small>", "", title_markup)
    route = "core" if is_core(document, index, title_markup) else "extension"
    label = "NÚCLEO" if route == "core" else "EXT."
    item = re.sub(r"<li(?: class=\"[^\"]*\")?>", f'<li class="contents-item contents-{route}">', item, count=1)
    item = re.sub(r"\s*<small>(?:NÚCLEO|EXT\.)</small>", "", item)
    span_end = item.rfind("</span>")
    item = item[:span_end] + f" <small>{label}</small>" + item[span_end:]
    return item


def update_html(document: int, path: Path) -> tuple[int, int]:
    source = path.read_text(encoding="utf-8")
    section_match = re.search(
        r'(<section class="[^"]*contents-page[^"]*"[^>]*>)(.*?)(</section>)',
        source,
        flags=re.DOTALL,
    )
    if not section_match:
        raise RuntimeError(f"No se encontró la página Contenido en {path}")
    body = section_match.group(2)
    body, route_count = re.subn(
        r'<p class="contents-route">.*?</p>',
        ROUTE_NOTE,
        body,
        count=1,
        flags=re.DOTALL,
    )
    if route_count != 1:
        raise RuntimeError(f"No se encontró una única ruta de lectura en {path}")
    body = re.sub(
        r'<li(?: class="[^"]*")?>.*?</li>',
        lambda match: classify_item(document, match),
        body,
        flags=re.DOTALL,
    )
    core_count = len(re.findall(r'contents-core', body))
    extension_count = len(re.findall(r'contents-extension', body))
    if core_count < 6 or extension_count < 1:
        raise RuntimeError(f"Clasificación incompleta en {path}: núcleo={core_count}, extensión={extension_count}")
    updated = source[: section_match.start(2)] + body + source[section_match.end(2) :]
    path.write_text(updated, encoding="utf-8")
    return core_count, extension_count


def update_css(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    if CSS_MARKER not in source:
        path.write_text(source.rstrip() + "\n\n" + ROUTE_CSS + "\n", encoding="utf-8")


def update_metadata(path: Path, core_count: int, extension_count: int) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    data["prioritized_reading_route"] = {
        "contract": "metsi-prioritized-reading/v1",
        "total": "80–100 min",
        "core_reading": "60–75 min",
        "preparation": "20–25 min",
        "optional_extensions": "30–45 min adicionales",
        "core_section_count": core_count,
        "extension_section_count": extension_count,
        "visual_signal": "volt-left-rule",
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    results: list[dict[str, object]] = []
    for number, relative in PACKAGE_ROOTS.items():
        package = ROOT / relative
        core_count, extension_count = update_html(number, package / "index.html")
        update_css(package / "magazine.css")
        metsi_css = package / "metsi.css"
        if metsi_css.is_file():
            update_css(metsi_css)
        for name in ("manifest.json", "document.json"):
            path = package / name
            if path.is_file():
                update_metadata(path, core_count, extension_count)
        results.append({"document": f"N{number:02d}", "core": core_count, "extension": extension_count})
    print(json.dumps({"status": "PASS", "documents": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
