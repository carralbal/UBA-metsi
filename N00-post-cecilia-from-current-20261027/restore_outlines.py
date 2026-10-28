#!/usr/bin/env python3
"""Restore the public N00 outline hierarchy against the revised page layout."""

from pathlib import Path
import re

from pypdf import PdfReader, PdfWriter
from baseline import ensure_baseline


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
SOURCE = HERE / "proper-assembly-v4/N00-post-cecilia-full-v2.pdf"
OUTPUT = HERE / "proper-assembly-v4/N00-post-cecilia-full-v3.pdf"

TITLE_FIXES = {
    "METSI: dos formas de empezar aintervenir": "METSI: del pedido o la señal a una intervención defendible",
    "Un encuentro, paso a paso: ejemploUn encuentro, paso a paso: ejemplocon Hotel Horizonte": "Un encuentro, paso a paso: ejemplo con Hotel Horizonte",
    "Bloque E. Pasar de entregar cosas aBloque E. Pasar de entregar cosas agobernar capacidades": "Bloque E. Pasar de entregar cosas a gobernar capacidades",
    "Bloque G. Incorporar IA sin delegar elBloque G. Incorporar IA sin delegar eljuicio": "Bloque G. Incorporar IA sin delegar el juicio",
    "Convenciones del sistema editorialConvenciones del sistema editorial": "Convenciones del sistema editorial",
    "Componentes de una lectura NComponentes de una lectura N": "Componentes de una lectura N",
    "Historia, analogía o metáforaHistoria, analogía o metáfora": "Historia, analogía o metáfora",
    "InfografíasInfografías": "Infografías",
    "Arquetipos del casoArquetipos del caso": "Arquetipos del caso",
    "Cinco píldoras para recordarCinco píldoras para recordar": "Cinco píldoras para recordar",
    "Resolución de MartinaResolución de Martina": "Resolución de Martina",
    "Una tensión real entre reflexión profesional y justicia de diseñoUna tensión real entre reflexión profesional y justicia de diseño": "Una tensión real entre reflexión profesional y justicia de diseño",
}


def compact(text: str) -> str:
    text = text.lower().replace("ﬁ", "fi").replace("ﬂ", "fl")
    return re.sub(r"[^a-z0-9áéíóúüñ]", "", text)


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    source = PdfReader(SOURCE, strict=True)
    public = PdfReader(ensure_baseline(), strict=True)
    if len(source.pages) != len(public.pages) or len(source.pages) != 55:
        raise ValueError("N00 must have exactly 55 candidate and public pages")
    page_text = [compact(page.extract_text() or "") for page in source.pages]
    writer = PdfWriter(clone_from=source)
    records = []

    def add_items(items, parent=None, depth=0):
        last = None
        for entry in items:
            if isinstance(entry, list):
                if last is None:
                    raise ValueError("Outline children without a parent")
                add_items(entry, last, depth + 1)
                continue
            title = TITLE_FIXES.get(entry.title, entry.title)
            query = compact(title)
            public_page = public.get_destination_page_number(entry)
            hits = [index for index, text in enumerate(page_text) if query in text]
            if title == "METSI: ver, comprender, intervenir":
                hits = [0]
            if not hits:
                raise ValueError(f"Outline target not found in revised PDF: {title!r}")
            target = min(hits, key=lambda page: (abs(page - public_page), page))
            last = writer.add_outline_item(title, target, parent=parent)
            records.append((depth, title, public_page + 1, target + 1))

    add_items(public.outline)
    if len(records) != 98:
        raise AssertionError(f"Expected 98 outline items, got {len(records)}")
    writer._info = None
    with OUTPUT.open("wb") as stream:
        writer.write(stream)
    result = PdfReader(OUTPUT, strict=True)
    if len(result.pages) != 55:
        raise AssertionError("Outline restoration changed the page count")
    print(f"Restored {len(records)} outline items to {OUTPUT}")
    for depth, title, old, new in records:
        if old != new:
            print(f"Moved target {old:02d}→{new:02d} {'  ' * depth}{title}")


if __name__ == "__main__":
    main()
